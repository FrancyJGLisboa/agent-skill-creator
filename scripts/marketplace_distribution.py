#!/usr/bin/env python3
"""Provider-neutral governed install planning and compatibility certification."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from platforms import (
    PLATFORMS, get_platform, list_supported_platforms, normalize_platform_name,
)

ADAPTER_VERSION = "1.0.0"
_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_SEMVER = re.compile(r"^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?(?:\+[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?$")
_TAG = re.compile(r"^v((?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?(?:\+[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?)$")
_SHA = re.compile(r"^[0-9a-fA-F]{40}(?:[0-9a-fA-F]{24})?$")

# Adapter behavior is derived only after canonical platform lookup; this maps the
# few platforms whose installers emit an additional native rule artifact.
_ADAPTED = {
    "cursor": ("cursor-mdc", "{name}.mdc"),
    "windsurf": ("windsurf-rule", "{name}.md"),
    "cline": ("plain-rule", "{name}.md"),
    "roo-code": ("plain-rule", "{name}.md"),
    "kilo-code": ("plain-rule", "{name}.md"),
    "trae": ("plain-rule", "{name}.md"),
    "junie": ("junie-guideline", "guidelines.md"),
}


class DistributionError(ValueError):
    """A distribution plan or certification violates governance policy."""


def adapter_for(platform: str) -> dict[str, str]:
    """Resolve adapter metadata after validating against canonical platforms.py."""
    platform = normalize_platform_name(platform)
    if get_platform(platform) is None:
        raise DistributionError(f"unknown platform: {platform}")
    name = _ADAPTED.get(platform, ("native-skill", "SKILL.md"))[0]
    return {
        "platform": platform,
        "name": name,
        "version": ADAPTER_VERSION,
        "tier": "native" if name == "native-skill" else "adapted",
    }


def _contained(root: Path, destination: Path) -> Path:
    root = root.resolve()
    destination = destination.resolve()
    if destination == root or not destination.is_relative_to(root):
        raise DistributionError("resolved destination escapes its installation root")
    return destination


def resolve_destination(platform: str, scope: str, skill_name: str, *, home: Path, project_root: Path) -> Path:
    """Resolve a canonical platform destination without creating it."""
    platform = normalize_platform_name(platform)
    target = get_platform(platform)
    if target is None:
        raise DistributionError(f"unknown platform: {platform}")
    if scope not in {"user", "project"}:
        raise DistributionError("scope must be user or project")
    if not _SLUG.fullmatch(skill_name):
        raise DistributionError("skill name must be a safe lowercase slug")
    if scope == "user":
        if not target.user_path.startswith("~/"):
            raise DistributionError(f"canonical user path is unsafe for platform {platform}")
        root = home.resolve()
        base = root / target.user_path[2:]
    else:
        canonical = Path(target.project_path)
        if canonical.is_absolute() or ".." in canonical.parts:
            raise DistributionError(f"canonical project path is unsafe for platform {platform}")
        root = project_root.resolve()
        base = root / canonical
    return _contained(root, base / skill_name)


def _immutable_release(reference: object, version: str) -> str:
    if not isinstance(reference, str):
        raise DistributionError("remote install requires an exact immutable release reference")
    tag = _TAG.fullmatch(reference)
    if not tag and not _SHA.fullmatch(reference):
        raise DistributionError("remote install requires an immutable vSEMVER tag or full commit SHA")
    if tag and tag.group(1) != version:
        raise DistributionError("release tag version does not match the skill version")
    return reference


def build_install_plan(
    *, skill_name: str, skill_version: str, platforms: Sequence[str], scope: str,
    source: str, release_ref: str | None, remote: bool, home: Path, project_root: Path,
) -> dict[str, Any]:
    """Build a deterministic no-mutation plan; it never downloads or installs."""
    if not _SLUG.fullmatch(skill_name):
        raise DistributionError("skill name must be a safe lowercase slug")
    if not _SEMVER.fullmatch(skill_version):
        raise DistributionError("skill version must use semantic versioning")
    if not isinstance(source, str) or not source.strip() or "\x00" in source:
        raise DistributionError("distribution source is required")
    exact_ref = _immutable_release(release_ref, skill_version) if remote else None
    requested = {normalize_platform_name(platform) for platform in platforms}
    unknown = requested - set(list_supported_platforms())
    if unknown:
        raise DistributionError("unknown platform(s): " + ", ".join(sorted(unknown)))
    targets: list[dict[str, Any]] = []
    for canonical in PLATFORMS:
        if canonical.name not in requested:
            continue
        adapter = adapter_for(canonical.name)
        artifacts = ["SKILL.md"]
        if canonical.name in _ADAPTED:
            artifacts.append(_ADAPTED[canonical.name][1].format(name=skill_name))
        targets.append({
            "platform": canonical.name,
            "scope": scope,
            "destination": str(resolve_destination(canonical.name, scope, skill_name, home=home, project_root=project_root)),
            "tier": adapter["tier"],
            "adapter": adapter["name"],
            "adapter_version": adapter["version"],
            "artifacts": artifacts,
        })
    return {
        "schema_version": 1,
        "skill": skill_name,
        "skill_version": skill_version,
        "source": source.strip(),
        "remote": remote,
        "release_ref": exact_ref,
        "mutates": False,
        "targets": targets,
    }


def _timestamp(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise DistributionError("certification timestamp must include a timezone")
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def certify_compatibility(
    *, platform: str, skill_version: str, declared_platforms: Sequence[str],
    evidence: Mapping[str, Any], timestamp: datetime,
) -> dict[str, Any]:
    """Validate explicit checks and emit a version-bound certification record."""
    platform = normalize_platform_name(platform)
    adapter = adapter_for(platform)
    if not _SEMVER.fullmatch(skill_version):
        raise DistributionError("skill version must use semantic versioning")
    canonical = set(list_supported_platforms())
    claims = {normalize_platform_name(claim) for claim in declared_platforms}
    unknown = claims - canonical
    if unknown:
        raise DistributionError("unsupported platform claim(s): " + ", ".join(sorted(unknown)))
    if platform not in claims:
        raise DistributionError("platform must be declared before certification")
    if normalize_platform_name(str(evidence.get("platform", ""))) != platform:
        raise DistributionError("certification evidence platform mismatch")
    if evidence.get("skill_version") != skill_version:
        raise DistributionError("certification evidence version mismatch")
    if evidence.get("adapter") != adapter["name"] or evidence.get("adapter_version") != ADAPTER_VERSION:
        raise DistributionError("certification evidence adapter or adapter version mismatch")
    checks = evidence.get("checks")
    if not isinstance(checks, list) or not checks:
        raise DistributionError("certification requires at least one explicit check")
    names: list[str] = []
    for check in checks:
        if not isinstance(check, Mapping) or not isinstance(check.get("name"), str) or not check["name"].strip():
            raise DistributionError("certification check evidence is malformed")
        if check.get("passed") is not True:
            raise DistributionError(f"certification check failed: {check['name']}")
        names.append(check["name"].strip())
    if len(names) != len(set(names)):
        raise DistributionError("certification check names must be unique")
    return {
        "platform": platform,
        "skill_version": skill_version,
        "passed": True,
        "certified_at": _timestamp(timestamp),
        "adapter": adapter["name"],
        "adapter_version": ADAPTER_VERSION,
        "checks": sorted(names),
    }
