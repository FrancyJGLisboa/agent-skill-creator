#!/usr/bin/env python3
"""Build and operate a governed, provider-neutral team skill marketplace.

The marketplace targets GitHub Copilot Agent Mode with GitHub and GitLab
repository backends. Governance remains repository-native:
department paths, CODEOWNERS, pull-request checks, immutable version pins, and
machine-readable quality evidence in ``registry.json``.
"""

from __future__ import annotations

import argparse
import json
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
from abc import ABC, abstractmethod
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from check_pipeline import check as check_pipeline  # noqa: E402
from security_scan import security_scan  # noqa: E402
from skill_document import SkillDoc  # noqa: E402
from validate import validate_skill  # noqa: E402
from marketplace_trust import (  # noqa: E402
    TrustError, create_attestation, transition_lifecycle, validate_attestation,
)
from marketplace_health import build_health_report, report_json, report_markdown  # noqa: E402
from marketplace_discovery import (  # noqa: E402
    DiscoveryError, normalize_discovery, render_skill_page, search_skills,
)
from marketplace_metrics import (  # noqa: E402
    CONSENT_SCHEMA, EVENT_TYPES, MetricsError, aggregate_events, create_event,
    record_event, validate_consent,
)
from marketplace_distribution import (  # noqa: E402
    DistributionError, build_install_plan, certify_compatibility,
)

SCHEMA_VERSION = 2
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_TAG_RE = re.compile(r"^v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?$")
SEMVER_RE = re.compile(r"^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?$")
APPROVED = "approved"
BLOCKED_TOOLS = {"shell", "bash"}
COPY_IGNORE_PATTERNS = shutil.ignore_patterns(
    ".git", "__pycache__", "node_modules", ".venv", "venv", ".pytest_cache",
    ".mypy_cache", "dist", "build", "*.pyc", "*.pyo",
)
SCAFFOLD_SCRIPTS = (
    "team_marketplace.py", "check_pipeline.py", "security_scan.py",
    "skill_document.py", "validate.py", "marketplace_trust.py", "marketplace_health.py",
    "marketplace_discovery.py",
    "marketplace_metrics.py",
    "marketplace_distribution.py", "platforms.py",
)
ATTESTATION_FILE = "marketplace-attestation.json"


class MarketplaceError(RuntimeError):
    """A user-correctable marketplace or governance failure."""


class MarketplaceProvider(ABC):
    """Repository-host-specific transport and generated governance files."""

    name: str
    default_host: str

    @abstractmethod
    def generate_files(self, root: Path) -> None:
        """Generate provider-specific CI and governance files."""

    @abstractmethod
    def install(
        self, root: Path, data: dict[str, Any], paths: list[str], scope: str,
        pin: str | None, force: bool, from_local: bool,
    ) -> list[list[str]]:
        """Install a bundle and return executed transport commands."""

    @abstractmethod
    def release(self, root: Path, tag: str) -> None:
        """Publish a checked marketplace release."""


class GitHubProvider(MarketplaceProvider):
    name = "github"
    default_host = "github.com"

    def generate_files(self, root: Path) -> None:
        workflows = root / ".github/workflows"
        workflows.mkdir(parents=True, exist_ok=True)
        (workflows / "marketplace-check.yml").write_text(_CHECK_WORKFLOW, encoding="utf-8")
        (workflows / "marketplace-release.yml").write_text(_RELEASE_WORKFLOW, encoding="utf-8")
        (workflows / "marketplace-health.yml").write_text(_HEALTH_WORKFLOW, encoding="utf-8")

    def install(
        self, root: Path, data: dict[str, Any], paths: list[str], scope: str,
        pin: str | None, force: bool, from_local: bool,
    ) -> list[list[str]]:
        source = str(root.resolve()) if from_local else data["marketplace"]["repository"]
        commands: list[list[str]] = []
        for path in paths:
            selector = Path(path).name if from_local else path
            command = ["gh", "skill", "install", source, selector]
            if from_local:
                command.append("--from-local")
            command += ["--agent", "github-copilot", "--scope", scope]
            if pin:
                command += ["--pin", pin]
            if force:
                command.append("--force")
            result = subprocess.run(command, cwd=root, text=True, check=False)
            if result.returncode:
                raise MarketplaceError(f"gh skill install failed for {path}")
            commands.append(command)
        return commands

    def release(self, root: Path, tag: str) -> None:
        command = ["gh", "skill", "publish", str(root.resolve()), "--tag", tag]
        result = subprocess.run(command, cwd=root, text=True, check=False)
        if result.returncode:
            raise MarketplaceError("gh skill publish failed")


class GitLabProvider(MarketplaceProvider):
    name = "gitlab"
    default_host = "gitlab.com"

    def generate_files(self, root: Path) -> None:
        (root / ".gitlab-ci.yml").write_text(_GITLAB_CI, encoding="utf-8")

    def install(
        self, root: Path, data: dict[str, Any], paths: list[str], scope: str,
        pin: str | None, force: bool, from_local: bool,
    ) -> list[list[str]]:
        source_root = root
        commands: list[list[str]] = []
        temporary: tempfile.TemporaryDirectory[str] | None = None
        try:
            if not from_local:
                marketplace = data["marketplace"]
                clone_url = f"https://{marketplace['host']}/{marketplace['repository']}.git"
                temporary = tempfile.TemporaryDirectory(prefix="acme-marketplace-")
                source_root = Path(temporary.name) / "repository"
                command = [
                    "git", "clone", "--depth", "1", "--branch", str(pin),
                    clone_url, str(source_root),
                ]
                result = subprocess.run(command, text=True, check=False)
                if result.returncode:
                    raise MarketplaceError(f"git clone failed for {clone_url} at {pin}")
                commands.append(command)
            destination_root = (
                Path.home() / ".copilot/skills" if scope == "user"
                else Path.cwd() / ".github/skills"
            )
            destination_root.mkdir(parents=True, exist_ok=True)
            for path in paths:
                source = _contained(source_root, path)
                if not source.is_dir():
                    raise MarketplaceError(f"pinned release is missing bundle skill: {path}")
                destination = destination_root / Path(path).name
                if destination.exists():
                    if not force:
                        raise MarketplaceError(
                            f"skill already installed: {destination}; use --force to replace it"
                        )
                    shutil.rmtree(destination)
                shutil.copytree(source, destination, ignore=COPY_IGNORE_PATTERNS)
            return commands
        finally:
            if temporary is not None:
                temporary.cleanup()

    def release(self, root: Path, tag: str) -> None:
        command = [
            "glab", "release", "create", tag, "--ref", "HEAD",
            "--notes", f"Governed marketplace release {tag}",
        ]
        result = subprocess.run(command, cwd=root, text=True, check=False)
        if result.returncode:
            raise MarketplaceError("glab release create failed")


PROVIDERS: dict[str, MarketplaceProvider] = {
    "github": GitHubProvider(),
    "gitlab": GitLabProvider(),
}


def _provider(data: dict[str, Any]) -> MarketplaceProvider:
    name = str(data.get("marketplace", {}).get("provider", "github")).lower()
    try:
        return PROVIDERS[name]
    except KeyError as exc:
        raise MarketplaceError(f"unsupported marketplace provider: {name}") from exc


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _require_slug(value: str, label: str) -> str:
    if not SLUG_RE.fullmatch(value):
        raise MarketplaceError(
            f"invalid {label} '{value}'; use lowercase letters, numbers, and single hyphens"
        )
    return value


def _contained(root: Path, relative: str) -> Path:
    target = (root / relative).resolve()
    resolved_root = root.resolve()
    if target == resolved_root or not target.is_relative_to(resolved_root):
        raise MarketplaceError(f"path escapes marketplace root: {relative}")
    return target


def load_manifest(root: Path) -> dict[str, Any]:
    """Load a schema-v2 marketplace manifest."""
    path = root / "registry.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise MarketplaceError(f"registry.json not found in {root}") from exc
    except json.JSONDecodeError as exc:
        raise MarketplaceError(f"invalid registry.json: {exc}") from exc
    if data.get("schema_version") != SCHEMA_VERSION:
        raise MarketplaceError("marketplace requires schema_version 2; migrate schema-v1 explicitly")
    marketplace = data.setdefault("marketplace", {})
    marketplace.setdefault("provider", "github")
    provider = _provider(data)
    marketplace.setdefault("host", provider.default_host)
    return data


def save_manifest(root: Path, data: dict[str, Any]) -> None:
    """Atomically save the marketplace manifest."""
    path = root / "registry.json"
    temporary = root / "registry.json.tmp"
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def migrate_v1_registry(
    source: Path, repository: str, provider: str = "github", host: str | None = None,
) -> dict[str, Any]:
    """Convert a legacy skill_registry.py manifest without silently approving it."""
    try:
        old = json.loads((source / "registry.json").read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise MarketplaceError(f"cannot read schema-v1 registry at {source}: {exc}") from exc
    registry = old.get("registry", {})
    if str(registry.get("schema_version", "1")) != "1":
        raise MarketplaceError("--from-registry accepts only schema-v1 registries")
    skills: list[dict[str, Any]] = []
    for item in old.get("skills", []):
        department = _legacy_department(item)
        author = str(item.get("author", "")).strip()
        legacy_path = item.get("path", f"skills/{item.get('name', '')}")
        governed_path = f"skills/{department}/{item.get('name', '')}"
        skills.append({
            "name": item.get("name", ""),
            "department": department,
            "author": author,
            "owners": [author or department],
            "approval_status": "draft",
            "version": item.get("version", "0.0.0"),
            "description": item.get("description", ""),
            "license": item.get("license", ""),
            "path": governed_path,
            "repository": repository,
            "provenance": {
                "migrated_from_schema": 1, "legacy_path": legacy_path,
                "legacy_published": item.get("published"),
            },
            "quality": {
                "validation": item.get("validation", {"valid": False}),
                "security": {
                    "passed": bool(item.get("security", {}).get("clean", False)),
                    "legacy": item.get("security", {}),
                },
                "pipeline": {"passed": False, "reason": "not run during migration"},
                "evals": {"passed": False, "reason": "not run during migration"},
            },
        })
    return {
        "schema_version": SCHEMA_VERSION,
        "marketplace": {
            "name": registry.get("name", "ACME Skills"),
            "repository": repository,
            "provider": provider,
            "host": host or PROVIDERS[provider].default_host,
            "created": registry.get("created", _now()),
            "migrated_at": _now(),
        },
        "skills": skills,
        "bundles": {},
    }


def _legacy_department(item: dict[str, Any]) -> str:
    author = str(item.get("author", "")).strip().lower()
    candidate = re.sub(r"[^a-z0-9]+", "-", author).strip("-") or "unassigned"
    return candidate if SLUG_RE.fullmatch(candidate) else "unassigned"


def init_marketplace(
    root: Path, name: str, repository: str, from_registry: Path | None = None,
    *, provider: str = "github", host: str | None = None,
) -> dict[str, Any]:
    """Create the repository scaffold, optionally importing schema-v1 files."""
    if not re.fullmatch(r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+", repository):
        raise MarketplaceError("repository must use OWNER/REPO or GROUP/SUBGROUP/REPO format")
    provider = provider.lower()
    if provider not in PROVIDERS:
        raise MarketplaceError(f"unsupported marketplace provider: {provider}")
    resolved_host = (host or PROVIDERS[provider].default_host).strip().lower()
    if not re.fullmatch(r"[a-z0-9.-]+(?::\d+)?", resolved_host):
        raise MarketplaceError("host must be a hostname, optionally followed by a port")
    if (root / "registry.json").exists():
        raise MarketplaceError(f"marketplace already exists at {root}")
    root.mkdir(parents=True, exist_ok=True)
    (root / "skills").mkdir(exist_ok=True)
    (root / "bundles").mkdir(exist_ok=True)
    if from_registry:
        data = migrate_v1_registry(from_registry, repository, provider, resolved_host)
        data["marketplace"]["name"] = name
        for entry in data["skills"]:
            source = _contained(from_registry, entry["provenance"]["legacy_path"])
            destination = _contained(root, entry["path"])
            if source.is_dir():
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(source, destination, ignore=COPY_IGNORE_PATTERNS)
    else:
        data = {
            "schema_version": SCHEMA_VERSION,
            "marketplace": {
                "name": name, "repository": repository, "provider": provider,
                "host": resolved_host, "created": _now(), "active_owners": [],
            },
            "skills": [],
            "bundles": {},
        }
    save_manifest(root, data)
    (root / ".gitignore").write_text(".marketplace-state/\n", encoding="utf-8")
    generate_repository_files(root, data)
    scaffold_scripts = root / "scripts"
    scaffold_scripts.mkdir(exist_ok=True)
    for filename in SCAFFOLD_SCRIPTS:
        source_script = _SCRIPTS_DIR / filename
        destination_script = scaffold_scripts / filename
        if source_script.resolve() != destination_script.resolve():
            shutil.copy2(source_script, destination_script)
    return data


def _metadata(skill: Path) -> dict[str, Any]:
    skill_md = skill / "SKILL.md"
    if not skill_md.exists():
        raise MarketplaceError(f"SKILL.md not found in {skill}")
    doc = SkillDoc.from_text(skill_md.read_text(encoding="utf-8"))
    metadata = doc.metadata
    owners = metadata.get("owners", [])
    if isinstance(owners, str):
        owners = [part.strip() for part in owners.strip("[]").split(",") if part.strip()]
    discovery: dict[str, Any] = {}
    discovery_path = skill / "discovery.json"
    if discovery_path.exists():
        try:
            loaded = json.loads(discovery_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise MarketplaceError(f"invalid discovery.json: {exc}") from exc
        if not isinstance(loaded, dict):
            raise MarketplaceError("discovery.json must contain a JSON object")
        discovery = loaded
    elif metadata.get("discovery"):
        try:
            loaded = json.loads(metadata["discovery"])
        except (json.JSONDecodeError, TypeError) as exc:
            raise MarketplaceError("metadata.discovery must be inline JSON or use discovery.json") from exc
        if isinstance(loaded, dict):
            discovery = loaded
    return {
        "name": (doc.name or "").strip(),
        "description": (doc.description or "").strip(),
        "license": (doc.license or "").strip(),
        "author": str(metadata.get("author", "")).strip(),
        "owners": [str(owner).strip().lstrip("@") for owner in owners],
        "approval_status": str(metadata.get("approval_status", "draft")).strip().lower(),
        "lifecycle": str(metadata.get("lifecycle") or metadata.get("approval_status", "draft")).strip().lower(),
        "version": str(metadata.get("version") or doc.field("version") or "0.0.0").strip(),
        "allowed_tools": doc.field("allowed-tools") or "",
        "discovery": discovery,
    }


def _gate_skill(skill: Path) -> dict[str, Any]:
    validation = validate_skill(str(skill))
    scan = security_scan(str(skill))
    high = [issue for issue in scan["issues"] if issue.get("severity") == "high"]
    pipeline = check_pipeline(skill)
    eval_runner = skill / "scripts/run_evals.py"
    if eval_runner.exists():
        validation_result = subprocess.run(
            [sys.executable, str(eval_runner), "--validate"], cwd=skill,
            capture_output=True, text=True, check=False,
        )
        gate_result = None
        if validation_result.returncode == 0:
            gate_result = subprocess.run(
                [sys.executable, str(eval_runner)], cwd=skill,
                capture_output=True, text=True, check=False,
            )
        evals = {
            "passed": validation_result.returncode == 0 and gate_result is not None and gate_result.returncode == 0,
            "validation_output": ((validation_result.stdout or "") + (validation_result.stderr or "")).strip(),
            "gate_output": (
                ((gate_result.stdout or "") + (gate_result.stderr or "")).strip()
                if gate_result is not None else "not run"
            ),
        }
    else:
        evals = {"passed": False, "status": "required"}
    return {
        "validation": {
            "valid": validation["valid"], "errors": validation["errors"],
            "warnings": validation["warnings"],
        },
        "security": {
            "passed": scan["clean"], "high_findings": high, "issues": scan["issues"],
        },
        "pipeline": {"passed": not pipeline["errors"], **pipeline},
        "evals": evals,
        "checked_at": _now(),
    }


def _source_commit(skill: Path) -> str:
    """Resolve the exact clean Git commit containing a submitted skill."""
    result = subprocess.run(
        ["git", "-C", str(skill), "rev-parse", "HEAD"], capture_output=True,
        text=True, check=False,
    )
    commit = result.stdout.strip()
    if result.returncode or not commit:
        raise MarketplaceError("skill submission must belong to a Git commit")
    dirty = subprocess.run(
        ["git", "-C", str(skill), "status", "--porcelain", "--untracked-files=all", "--", "."],
        capture_output=True, text=True, check=False,
    )
    lines = [
        line for line in dirty.stdout.splitlines()
        if ATTESTATION_FILE not in line and "__pycache__/" not in line
        and not line.rstrip().endswith((".pyc", ".pyo"))
    ]
    if dirty.returncode or lines:
        raise MarketplaceError("skill submission has uncommitted files; attest the exact committed contents")
    return commit


def _load_attestation(skill: Path, meta: dict[str, Any], commit: str) -> dict[str, Any]:
    path = skill / ATTESTATION_FILE
    try:
        artifact = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise MarketplaceError(f"representative-run attestation is required: {path}") from exc
    except json.JSONDecodeError as exc:
        raise MarketplaceError(f"invalid representative-run attestation: {exc}") from exc
    errors = validate_attestation(
        artifact, expected_skill=meta["name"], expected_version=meta["version"],
        expected_commit=commit,
    )
    if errors:
        raise MarketplaceError("attestation gate failed: " + "; ".join(errors))
    return artifact


def attest_skill(skill: Path, run_id: str, completed_at: str) -> Path:
    """Run mandatory eval gates and write commit-bound representative evidence."""
    meta = _metadata(skill)
    commit = _source_commit(skill)
    quality = _gate_skill(skill)
    failures = _quality_errors(meta["name"], quality)
    if failures:
        raise MarketplaceError("; ".join(failures))
    artifact = create_attestation(
        skill_name=meta["name"], skill_version=meta["version"], commit_sha=commit,
        eval_evidence={
            "runner": "scripts/run_evals.py", "executable": True,
            "validation_passed": True, "run_passed": True,
            "checked_at": quality["checked_at"],
        },
        representative_run={
            "passed": True, "run_id": run_id, "completed_at": completed_at,
            "safe_mode": "operator-confirmed",
        },
    )
    path = skill / ATTESTATION_FILE
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _blocked_allowed_tools(value: Any) -> set[str]:
    if isinstance(value, list):
        tokens = {str(item).lower() for item in value}
    else:
        tokens = set(re.findall(r"[a-zA-Z0-9_-]+", str(value).lower()))
    return tokens & BLOCKED_TOOLS


def add_skill(root: Path, skill: Path, department: str, bundle: str) -> dict[str, Any]:
    """Gate and copy one approved skill into its department namespace."""
    department = _require_slug(department, "department")
    bundle = _require_slug(bundle, "bundle")
    if not skill.is_dir():
        raise MarketplaceError(f"skill path is not a directory: {skill}")
    meta = _metadata(skill)
    if not meta["name"]:
        raise MarketplaceError("skill name is missing")
    if _blocked_allowed_tools(meta["allowed_tools"]):
        raise MarketplaceError("pre-approved shell or bash access is forbidden; runtime permission is required")
    if not meta["owners"]:
        raise MarketplaceError("skill metadata must declare at least one owner")
    if not SEMVER_RE.fullmatch(meta["version"]):
        raise MarketplaceError("skill metadata.version must be semantic versioning, such as 1.2.0")
    if meta["lifecycle"] != APPROVED:
        raise MarketplaceError("skill lifecycle must be approved before marketplace intake")
    try:
        normalized_discovery = normalize_discovery({
            "name": meta["name"], "version": meta["version"], "discovery": meta["discovery"],
        })
    except DiscoveryError as exc:
        raise MarketplaceError(f"invalid discovery metadata: {exc}") from exc
    commit = _source_commit(skill)
    attestation = _load_attestation(skill, meta, commit)
    quality = _gate_skill(skill)
    failures = _quality_errors(meta["name"], quality)
    if failures:
        raise MarketplaceError("; ".join(failures))
    data = load_manifest(root)
    identity = (department, meta["name"])
    if any((item.get("department"), item.get("name")) == identity for item in data["skills"]):
        raise MarketplaceError(f"duplicate skill identity: {department}/{meta['name']}")
    relative = f"skills/{department}/{meta['name']}"
    destination = _contained(root, relative)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(skill, destination, ignore=COPY_IGNORE_PATTERNS)
    entry = {
        "name": meta["name"], "department": department, "author": meta["author"],
        "owners": meta["owners"], "approval_status": meta["approval_status"],
        "lifecycle": meta["lifecycle"],
        "version": meta["version"], "description": meta["description"],
        "license": meta["license"], "path": relative,
        "repository": data["marketplace"]["repository"],
        "provenance": {"source": str(skill.resolve()), "commit_sha": commit, "added_at": _now()},
        "attestation": attestation,
        "discovery": meta["discovery"] if isinstance(meta["discovery"], dict) else {},
        "compatibility": normalized_discovery["compatibility"],
        "quality": quality,
    }
    data["skills"].append(entry)
    active_owners = data["marketplace"].setdefault("active_owners", [])
    for owner in meta["owners"]:
        if owner not in active_owners:
            active_owners.append(owner)
    active_owners.sort()
    paths = data.setdefault("bundles", {}).setdefault(bundle, [])
    if relative not in paths:
        paths.append(relative)
        paths.sort()
    save_manifest(root, data)
    generate_repository_files(root, data)
    return entry


def _quality_errors(name: str, quality: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not quality.get("validation", {}).get("valid", False):
        errors.append(f"{name}: validation gate failed")
    for gate in ("security", "pipeline", "evals"):
        if not quality.get(gate, {}).get("passed", False):
            errors.append(f"{name}: {gate} gate failed")
    return errors


def check_marketplace(
    root: Path, *, refresh: bool = True, require_published: bool = False,
) -> list[str]:
    """Return every release-blocking inconsistency; an empty list is releasable."""
    data = load_manifest(root)
    errors: list[str] = []
    try:
        _provider(data)
    except MarketplaceError as exc:
        errors.append(str(exc))
    identities: set[tuple[str, str]] = set()
    known_paths: set[str] = set()
    for entry in data["skills"]:
        identity = (entry.get("department", ""), entry.get("name", ""))
        if identity in identities:
            errors.append(f"duplicate skill identity: {identity[0]}/{identity[1]}")
        identities.add(identity)
        path = str(entry.get("path", ""))
        if path in known_paths:
            errors.append(f"duplicate skill path: {path}")
        known_paths.add(path)
        if entry.get("lifecycle", entry.get("approval_status")) not in {APPROVED, "published"}:
            state = entry.get("lifecycle", entry.get("approval_status", "draft"))
            errors.append(f"{identity[1]}: lifecycle {state} does not permit release")
        if require_published and entry.get("lifecycle", entry.get("approval_status")) != "published":
            errors.append(f"{identity[1]}: release requires committed published lifecycle")
        if not entry.get("owners"):
            errors.append(f"{identity[1]}: owners are required")
        quality = entry.get("quality", {})
        if not refresh:
            errors.extend(_quality_errors(identity[1], quality))
        expected = f"skills/{identity[0]}/{identity[1]}"
        if path != expected:
            errors.append(f"{identity[1]}: manifest path must be {expected}")
        try:
            skill = _contained(root, path)
        except MarketplaceError as exc:
            errors.append(str(exc))
            continue
        if not skill.is_dir():
            errors.append(f"{identity[1]}: skill directory is missing")
            continue
        meta = _metadata(skill)
        if meta["name"] != identity[1]:
            errors.append(f"{identity[1]}: SKILL.md name is inconsistent")
        for field in ("author", "owners", "approval_status", "version"):
            if meta[field] != entry.get(field):
                errors.append(f"{identity[1]}: SKILL.md {field} is inconsistent with registry.json")
        try:
            normalized_discovery = normalize_discovery({
                "name": meta["name"], "version": meta["version"], "discovery": meta["discovery"],
            })
        except DiscoveryError as exc:
            errors.append(f"{identity[1]}: invalid discovery metadata: {exc}")
        else:
            existing = entry.get("compatibility", {})
            certified = existing.get("certified", []) if isinstance(existing, dict) else []
            entry["compatibility"] = {
                "declared": normalized_discovery["compatibility"]["declared"],
                "certified": certified,
            }
        commit = entry.get("provenance", {}).get("commit_sha", "")
        errors.extend(
            f"{identity[1]}: {error}" for error in validate_attestation(
                entry.get("attestation"), expected_skill=identity[1],
                expected_version=entry.get("version", ""), expected_commit=commit,
            )
        )
        if _blocked_allowed_tools(meta["allowed_tools"]):
            errors.append(f"{identity[1]}: pre-approved shell access is forbidden")
        quality = _gate_skill(skill) if refresh else quality
        if refresh:
            entry["quality"] = quality
            errors.extend(_quality_errors(identity[1], quality))
    for bundle, paths in data.get("bundles", {}).items():
        if not SLUG_RE.fullmatch(bundle):
            errors.append(f"invalid bundle name: {bundle}")
        for path in paths:
            if path not in known_paths:
                errors.append(f"bundle {bundle} references unknown skill: {path}")
        bundle_file = root / "bundles" / f"{bundle}.json"
        expected_bundle = {"name": bundle, "skills": sorted(paths)}
        try:
            actual_bundle = json.loads(bundle_file.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            errors.append(f"bundle manifest is missing or invalid: bundles/{bundle}.json")
        else:
            if actual_bundle != expected_bundle:
                errors.append(f"bundle manifest is inconsistent: bundles/{bundle}.json")
    if refresh:
        save_manifest(root, data)
        generate_repository_files(root, data)
    return errors


def generate_repository_files(root: Path, data: dict[str, Any]) -> None:
    """Regenerate catalog, bundles, CODEOWNERS, and provider CI files."""
    (root / "bundles").mkdir(exist_ok=True)
    for name, paths in sorted(data.get("bundles", {}).items()):
        payload = {"name": name, "skills": sorted(paths)}
        (root / "bundles" / f"{name}.json").write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )
    lines = [f"# {data['marketplace']['name']}", "", "Generated from `registry.json`. Do not edit by hand.", ""]
    departments: dict[str, list[dict[str, Any]]] = {}
    for item in data["skills"]:
        departments.setdefault(item["department"], []).append(item)
    for department, skills in sorted(departments.items()):
        lines += [f"## {department.replace('-', ' ').title()}", "", "| Skill | Version | Status | Owners |", "|---|---:|---|---|"]
        for item in sorted(skills, key=lambda value: value["name"]):
            owners = ", ".join(f"@{owner.lstrip('@')}" for owner in item.get("owners", []))
            lines.append(f"| [{item['name']}]({item['path']}) | {item['version']} | {item['approval_status']} | {owners} |")
        lines.append("")
    (root / "CATALOG.md").write_text("\n".join(lines), encoding="utf-8")
    pages = root / "skill-pages"
    pages.mkdir(exist_ok=True)
    expected_pages: set[str] = set()
    for item in data["skills"]:
        filename = f"{item['department']}--{item['name']}.md"
        expected_pages.add(filename)
        (pages / filename).write_text(render_skill_page(item), encoding="utf-8")
    for existing in pages.glob("*.md"):
        if existing.name not in expected_pages:
            existing.unlink()
    provider = _provider(data)
    governance_path = "/.github/" if provider.name == "github" else "/.gitlab-ci.yml"
    owner_lines = ["# Generated from registry.json; repository admins own governance files.", "/registry.json @acme-platform @acme-security", "/bundles/ @acme-platform @acme-security", f"{governance_path} @acme-platform @acme-security"]
    for item in sorted(data["skills"], key=lambda value: value["path"]):
        owners = " ".join(f"@{owner.lstrip('@')}" for owner in item.get("owners", []))
        owner_lines.append(f"/{item['path']}/ {owners} @acme-platform @acme-security")
    (root / "CODEOWNERS").write_text("\n".join(owner_lines) + "\n", encoding="utf-8")
    governance = _GITHUB_GOVERNANCE if provider.name == "github" else _GITLAB_GOVERNANCE
    (root / "GOVERNANCE.md").write_text(governance, encoding="utf-8")
    provider.generate_files(root)


_CHECK_WORKFLOW = """name: Marketplace checks
on:
  pull_request:
jobs:
  governed-marketplace:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: python3 scripts/team_marketplace.py check --marketplace .
      - run: gh skill publish --dry-run
"""

_HEALTH_WORKFLOW = """name: Marketplace health
on:
  schedule:
    - cron: '17 8 * * 1'
  workflow_dispatch:
jobs:
  marketplace-health:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: python3 scripts/team_marketplace.py health --marketplace . --output MARKETPLACE_HEALTH.md --json-output marketplace-health.json
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: marketplace-health
          path: |
            MARKETPLACE_HEALTH.md
            marketplace-health.json
"""

_RELEASE_WORKFLOW = """name: Marketplace release
on:
  push:
    tags: ['v*.*.*']
jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: python3 scripts/team_marketplace.py check --marketplace . --release
      - run: gh skill publish --dry-run
      - run: gh release create "${GITHUB_REF_NAME}" --generate-notes --verify-tag
        env:
          GH_TOKEN: ${{ github.token }}
"""

_GITHUB_GOVERNANCE = """# ACME marketplace governance

Configure the default branch ruleset to require pull requests, CODEOWNER review,
the `governed-marketplace` status check, and approval from both department owners
and the ACME platform/security teams. Disable force pushes and branch deletion.

Configure a tag ruleset for `v*.*.*` that restricts tag creation, updates, and
deletion to release administrators. Releases install by immutable semantic-version
tag; advancing or rolling back a team uses a new managed `install --pin` command.

Skills remain unapproved after schema-v1 migration. Review their scripts, update
`approval_status` to `approved`, run `scripts/evolve.py` when corrections are
needed, and merge changes through a pull request. Do not edit installed copies.
"""

_GITLAB_CI = """stages:
  - check
  - release

workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_TAG
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

marketplace-check:
  stage: check
  image: python:3.12
  script:
    - python3 scripts/team_marketplace.py check --marketplace .

marketplace-release:
  stage: release
  image: registry.gitlab.com/gitlab-org/cli:latest
  rules:
    - if: $CI_COMMIT_TAG =~ /^v[0-9]+\\.[0-9]+\\.[0-9]+/
  script:
    - python3 scripts/team_marketplace.py check --marketplace . --release
    - echo "Creating governed marketplace release $CI_COMMIT_TAG"
  release:
    tag_name: $CI_COMMIT_TAG
    name: "Release $CI_COMMIT_TAG"
    description: "Governed ACME skill marketplace release $CI_COMMIT_TAG"

marketplace-health:
  stage: check
  image: python:3.12
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
  script:
    - python3 scripts/team_marketplace.py health --marketplace . --output MARKETPLACE_HEALTH.md --json-output marketplace-health.json
  artifacts:
    when: always
    paths: [MARKETPLACE_HEALTH.md, marketplace-health.json]
"""

_GITLAB_GOVERNANCE = """# ACME marketplace governance

Protect the default branch and require merge requests, CODEOWNER approval, a
successful `marketplace-check` pipeline, and approval from both department owners
and the ACME platform/security teams. Disable force pushes.

Protect `v*.*.*` tags so only release administrators can create them. Releases
install by immutable semantic-version tag; advancing or rolling back a team uses
a new managed `install --pin` command.

Skills remain unapproved after schema-v1 migration. Review their scripts, update
`approval_status` to `approved`, run `scripts/evolve.py` when corrections are
needed, and merge changes through a merge request. Do not edit installed copies.
"""


def install_bundle(
    root: Path, bundle: str, scope: str, pin: str | None, *, force: bool = False,
    from_local: bool = False,
) -> list[list[str]]:
    """Install every exact skill path through the configured provider."""
    data = load_manifest(root)
    paths = data.get("bundles", {}).get(bundle)
    if paths is None:
        raise MarketplaceError(f"bundle not found: {bundle}")
    if not from_local and not pin:
        raise MarketplaceError("managed remote installs require --pin vX.Y.Z")
    if scope not in {"user", "project"}:
        raise MarketplaceError("scope must be user or project")
    blocked = [
        item["name"] for item in data["skills"]
        if item.get("path") in paths
        and item.get("lifecycle", item.get("approval_status")) not in {APPROVED, "published"}
    ]
    if blocked:
        raise MarketplaceError("bundle contains non-installable skills: " + ", ".join(blocked))
    commands = _provider(data).install(root, data, paths, scope, pin, force, from_local)
    platform = "github-copilot" if _provider(data).name == "github" else "vscode-copilot"
    for path in paths:
        record_marketplace_event(root, "install", Path(path).name, True, platform=platform)
    return commands


def health_marketplace(
    root: Path, *, as_of: date | None = None, active_owners: set[str] | None = None,
) -> dict[str, Any]:
    """Build the marketplace health report using its configured owner directory."""
    data = load_manifest(root)
    configured = data.get("marketplace", {}).get("active_owners", [])
    owners = active_owners if active_owners is not None else {
        str(owner).lstrip("@").strip() for owner in configured if str(owner).strip()
    }
    return build_health_report(data, root, as_of or date.today(), owners)


def search_marketplace(
    root: Path, query: str, *, platform: str | None = None, support_tier: str | None = None,
) -> list[dict[str, Any]]:
    """Search published skills by outcome with optional trust filters."""
    return search_skills(
        load_manifest(root).get("skills", []), query, platform=platform,
        support_tier=support_tier,
    )


def _metrics_paths(root: Path) -> tuple[Path, Path, Path]:
    state = root / ".marketplace-state"
    return root / "metrics-consent.json", state / "metrics-salt", state / "metrics.jsonl"


def configure_metrics_consent(root: Path, expires_at: str, *, approved_at: datetime | None = None) -> Path:
    """Write the explicit, reviewable organizational consent artifact."""
    now = approved_at or datetime.now(timezone.utc)
    artifact = {
        "schema": CONSENT_SCHEMA, "schema_version": 1, "enabled": True,
        "approved_at": now.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "expires_at": expires_at, "allowed_events": sorted(EVENT_TYPES),
    }
    errors = validate_consent(artifact, now=now)
    if errors:
        raise MarketplaceError("invalid metrics consent: " + "; ".join(errors))
    path, _, _ = _metrics_paths(root)
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def record_marketplace_event(
    root: Path, event_name: str, skill_name: str, success: bool, *,
    duration_ms: int | None = None, platform: str | None = None,
) -> bool:
    """Best-effort local recording; absent/invalid consent is a strict no-op."""
    consent_path, salt_path, ledger_path = _metrics_paths(root)
    try:
        consent = json.loads(consent_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return False
    now = datetime.now(timezone.utc)
    if validate_consent(consent, now=now):
        return False
    salt_path.parent.mkdir(parents=True, exist_ok=True)
    if not salt_path.exists():
        salt_path.write_bytes(secrets.token_bytes(32))
        try:
            salt_path.chmod(0o600)
        except OSError:
            pass
    try:
        event = create_event(
            event_name, skill_name=skill_name, salt=salt_path.read_bytes(),
            timestamp=now, success=success, duration_ms=duration_ms, platform=platform,
        )
        return record_event(ledger_path, event, consent, now=now)
    except (MetricsError, OSError):
        return False


def summarize_marketplace_metrics(root: Path) -> dict[str, Any]:
    """Return deterministic aggregate metrics without exposing skill identities."""
    _, _, ledger = _metrics_paths(root)
    try:
        lines = ledger.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        lines = []
    return aggregate_events(lines)


def _find_skill(data: dict[str, Any], department: str, name: str) -> dict[str, Any]:
    entry = next(
        (item for item in data.get("skills", []) if item.get("department") == department and item.get("name") == name),
        None,
    )
    if entry is None:
        raise MarketplaceError(f"skill not found: {department}/{name}")
    return entry


def plan_distribution(
    root: Path, department: str, name: str, platforms: list[str], scope: str,
    release_ref: str | None, *, remote: bool, home: Path, project_root: Path,
) -> dict[str, Any]:
    """Return a non-mutating governed distribution plan for one skill."""
    data = load_manifest(root)
    entry = _find_skill(data, department, name)
    if entry.get("lifecycle", entry.get("approval_status")) != "published" and remote:
        raise MarketplaceError("remote distribution requires a published skill")
    try:
        return build_install_plan(
            skill_name=name, skill_version=entry["version"], platforms=platforms,
            scope=scope, source=data["marketplace"]["repository"] if remote else str((root / entry["path"]).resolve()),
            release_ref=release_ref, remote=remote, home=home, project_root=project_root,
        )
    except DistributionError as exc:
        raise MarketplaceError(str(exc)) from exc


def certify_skill(
    root: Path, department: str, name: str, platform: str, evidence: dict[str, Any],
    *, timestamp: datetime | None = None,
) -> dict[str, Any]:
    """Validate and persist current-version compatibility evidence."""
    data = load_manifest(root)
    entry = _find_skill(data, department, name)
    discovery = entry.setdefault("discovery", {})
    compatibility = discovery.setdefault("compatibility", {})
    declared = compatibility.get("declared", [])
    try:
        record = certify_compatibility(
            platform=platform, skill_version=entry["version"], declared_platforms=declared,
            evidence=evidence, timestamp=timestamp or datetime.now(timezone.utc),
        )
    except DistributionError as exc:
        raise MarketplaceError(str(exc)) from exc
    stored = {**record, "version": record["skill_version"]}
    certifications = compatibility.setdefault("certified", [])
    certifications[:] = [item for item in certifications if item.get("platform") != platform]
    certifications.append(stored)
    certifications.sort(key=lambda item: item["platform"])
    entry["compatibility"] = {
        "declared": sorted(set(declared)), "certified": certifications,
    }
    save_manifest(root, data)
    generate_repository_files(root, data)
    return stored


def transition_skill(root: Path, department: str, name: str, target: str) -> str:
    """Apply one policy-authorized lifecycle transition and regenerate the catalog."""
    data = load_manifest(root)
    entry = next(
        (item for item in data["skills"] if item.get("department") == department and item.get("name") == name),
        None,
    )
    if entry is None:
        raise MarketplaceError(f"skill not found: {department}/{name}")
    source = entry.get("lifecycle", entry.get("approval_status", "draft"))
    try:
        entry["lifecycle"] = transition_lifecycle(source, target)
    except TrustError as exc:
        raise MarketplaceError(str(exc)) from exc
    save_manifest(root, data)
    generate_repository_files(root, data)
    return target


def release_marketplace(root: Path, tag: str) -> None:
    """Run governance gates and publish a provider-native semantic release."""
    if not SEMVER_TAG_RE.fullmatch(tag):
        raise MarketplaceError("release tag must be a protected semantic version such as v1.2.0")
    errors = check_marketplace(root, require_published=True)
    if errors:
        raise MarketplaceError("release refused:\n- " + "\n- ".join(errors))
    data = load_manifest(root)
    unpublished = [
        f"{item['department']}/{item['name']}"
        for item in data["skills"]
        if item.get("lifecycle", item.get("approval_status")) != "published"
    ]
    if unpublished:
        raise MarketplaceError(
            "release requires the published lifecycle transition to be reviewed and committed: "
            + ", ".join(unpublished)
        )
    _provider(data).release(root, tag)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Governed Git-backed Copilot team skill marketplace")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--name", required=True)
    init.add_argument("--repository", required=True)
    init.add_argument("--provider", choices=tuple(PROVIDERS), default="github")
    init.add_argument("--host", help="provider hostname; defaults to github.com or gitlab.com")
    init.add_argument("--from-registry")
    init.add_argument("--marketplace", default=".")
    add = sub.add_parser("add")
    add.add_argument("skill_path")
    add.add_argument("--department", required=True)
    add.add_argument("--bundle", required=True)
    add.add_argument("--marketplace", default=".")
    attest = sub.add_parser("attest")
    attest.add_argument("skill_path")
    attest.add_argument("--run-id", required=True)
    attest.add_argument("--completed-at", required=True)
    check = sub.add_parser("check")
    check.add_argument("--marketplace", default=".")
    check.add_argument("--release", action="store_true", help="require committed published lifecycle")
    release = sub.add_parser("release")
    release.add_argument("--tag", required=True)
    release.add_argument("--marketplace", default=".")
    install = sub.add_parser("install")
    install.add_argument("--bundle", required=True)
    install.add_argument("--scope", choices=("user", "project"), required=True)
    install.add_argument("--pin")
    install.add_argument("--force", action="store_true")
    install.add_argument("--from-local", action="store_true", help=argparse.SUPPRESS)
    install.add_argument("--marketplace", default=".")
    lifecycle = sub.add_parser("lifecycle")
    lifecycle.add_argument("skill_name")
    lifecycle.add_argument("--department", required=True)
    lifecycle.add_argument("--to", required=True)
    lifecycle.add_argument("--marketplace", default=".")
    health = sub.add_parser("health")
    health.add_argument("--marketplace", default=".")
    health.add_argument("--as-of", help="YYYY-MM-DD; defaults to today")
    health.add_argument("--active-owners", help="comma-separated override")
    health.add_argument("--output", help="write Markdown report")
    health.add_argument("--json-output", help="write JSON report")
    search = sub.add_parser("search")
    search.add_argument("query")
    search.add_argument("--platform")
    search.add_argument("--support-tier")
    search.add_argument("--json", action="store_true")
    search.add_argument("--marketplace", default=".")
    consent = sub.add_parser("metrics-consent")
    consent.add_argument("--expires-at", required=True, help="UTC RFC3339 expiry")
    consent.add_argument("--marketplace", default=".")
    metric = sub.add_parser("metrics-record")
    metric.add_argument("event", choices=sorted(EVENT_TYPES))
    metric.add_argument("--skill", required=True)
    metric.add_argument("--success", choices=("true", "false"), default="true")
    metric.add_argument("--duration-ms", type=int)
    metric.add_argument("--platform")
    metric.add_argument("--marketplace", default=".")
    summary = sub.add_parser("metrics-summary")
    summary.add_argument("--marketplace", default=".")
    plan_install = sub.add_parser("plan-install")
    plan_install.add_argument("skill_name")
    plan_install.add_argument("--department", required=True)
    plan_install.add_argument("--platforms", required=True, help="comma-separated canonical platforms")
    plan_install.add_argument("--scope", choices=("user", "project"), required=True)
    plan_install.add_argument("--release-ref")
    plan_install.add_argument("--local", action="store_true")
    plan_install.add_argument("--home", default=str(Path.home()))
    plan_install.add_argument("--project-root", default=str(Path.cwd()))
    plan_install.add_argument("--marketplace", default=".")
    certify = sub.add_parser("certify")
    certify.add_argument("skill_name")
    certify.add_argument("--department", required=True)
    certify.add_argument("--platform", required=True)
    certify.add_argument("--evidence", required=True)
    certify.add_argument("--marketplace", default=".")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.marketplace).resolve()
    try:
        if args.command == "init":
            init_marketplace(
                root, args.name, args.repository,
                Path(args.from_registry).resolve() if args.from_registry else None,
                provider=args.provider, host=args.host,
            )
            print(f"Marketplace initialized at {root}")
        elif args.command == "attest":
            path = attest_skill(Path(args.skill_path).resolve(), args.run_id, args.completed_at)
            print(f"Wrote trust attestation to {path}")
        elif args.command == "add":
            entry = add_skill(root, Path(args.skill_path).resolve(), args.department, args.bundle)
            print(f"Added {entry['department']}/{entry['name']} to bundle {args.bundle}")
        elif args.command == "check":
            errors = check_marketplace(root, require_published=args.release)
            if errors:
                print("Marketplace checks failed:\n- " + "\n- ".join(errors), file=sys.stderr)
                return 1
            print("Marketplace checks passed")
        elif args.command == "release":
            release_marketplace(root, args.tag)
            print(f"Released {args.tag}")
        elif args.command == "install":
            commands = install_bundle(root, args.bundle, args.scope, args.pin, force=args.force, from_local=args.from_local)
            print(f"Installed {len(commands)} skill(s) from bundle {args.bundle}")
        elif args.command == "lifecycle":
            state = transition_skill(root, args.department, args.skill_name, args.to)
            print(f"Transitioned {args.department}/{args.skill_name} to {state}")
        elif args.command == "health":
            try:
                as_of = date.fromisoformat(args.as_of) if args.as_of else None
            except ValueError as exc:
                raise MarketplaceError("--as-of must use YYYY-MM-DD") from exc
            owners = None
            if args.active_owners is not None:
                owners = {value.strip().lstrip("@") for value in args.active_owners.split(",") if value.strip()}
            report = health_marketplace(root, as_of=as_of, active_owners=owners)
            markdown = report_markdown(report)
            if args.output:
                Path(args.output).write_text(markdown, encoding="utf-8")
            if args.json_output:
                Path(args.json_output).write_text(report_json(report), encoding="utf-8")
            if not args.output:
                print(markdown, end="")
            if report["summary"]["status"] == "critical":
                return 1
        elif args.command == "search":
            results = search_marketplace(
                root, args.query, platform=args.platform, support_tier=args.support_tier,
            )
            if args.json:
                print(json.dumps(results, indent=2, ensure_ascii=False))
            elif not results:
                print("No matching published skills.")
            else:
                for item in results:
                    platforms = ",".join(item["certified_platforms"]) or "uncertified"
                    print(f"{item['department']}/{item['name']} v{item['version']} [{item['support_tier']}; {platforms}] — {item['outcome']}")
        elif args.command == "metrics-consent":
            path = configure_metrics_consent(root, args.expires_at)
            print(f"Metrics consent enabled until {args.expires_at}: {path}")
        elif args.command == "metrics-record":
            recorded = record_marketplace_event(
                root, args.event, args.skill, args.success == "true",
                duration_ms=args.duration_ms, platform=args.platform,
            )
            print("Metric recorded." if recorded else "Metric not recorded: valid organizational consent is absent.")
        elif args.command == "metrics-summary":
            print(json.dumps(summarize_marketplace_metrics(root), indent=2, sort_keys=True))
        elif args.command == "plan-install":
            plan = plan_distribution(
                root, args.department, args.skill_name,
                [item.strip() for item in args.platforms.split(",") if item.strip()],
                args.scope, args.release_ref, remote=not args.local,
                home=Path(args.home), project_root=Path(args.project_root),
            )
            print(json.dumps(plan, indent=2, sort_keys=True))
        elif args.command == "certify":
            try:
                evidence = json.loads(Path(args.evidence).read_text(encoding="utf-8"))
            except (FileNotFoundError, json.JSONDecodeError, OSError) as exc:
                raise MarketplaceError(f"cannot read certification evidence: {exc}") from exc
            record = certify_skill(root, args.department, args.skill_name, args.platform, evidence)
            print(json.dumps(record, indent=2, sort_keys=True))
    except MarketplaceError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
