#!/usr/bin/env python3
"""
Git-Based Shared Skill Registry.

Manages a git-friendly skill registry for publishing, discovering, and installing
cross-platform agent skills. The registry is a directory with a registry.json
manifest and a skills/ folder — no servers, no databases, no new dependencies.

Usage:
    python3 scripts/skill_registry.py init     [--name NAME] [--registry PATH]
    python3 scripts/skill_registry.py publish  <skill-path> [--registry PATH] [--tags T1,T2] [--force] [--json]
    python3 scripts/skill_registry.py list     [--registry PATH] [--json]
    python3 scripts/skill_registry.py search   <query> [--registry PATH] [--json]
    python3 scripts/skill_registry.py install  <skill-name> [--registry PATH] [--platform PLATFORM] [--project] [--force] [--json]
    python3 scripts/skill_registry.py info     <skill-name> [--registry PATH] [--json]
    python3 scripts/skill_registry.py remove   <skill-name> [--registry PATH] [--force]

Exit codes:
    0 - Success
    1 - Error
"""

import argparse
import json
import re
import shutil
import sys
from datetime import date, datetime, timezone
from pathlib import Path

# --- Import sibling scripts ---

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from validate import validate_skill  # noqa: E402
from skill_document import SkillDoc  # noqa: E402
from security_scan import security_scan  # noqa: E402
from staleness_check import DEFAULT_REVIEW_INTERVAL_DAYS  # noqa: E402
from platforms import PLATFORMS, list_supported_platforms, project_paths, user_paths  # noqa: E402


# --- Constants ---

# Platform tables derive from the canonical scripts/platforms.py registry
# (single source of truth, covers all 17 supported platforms with correct paths).
ALL_PLATFORMS = list_supported_platforms()
PLATFORM_PATHS_USER = user_paths()
PLATFORM_PATHS_PROJECT = project_paths()

# Directories/files to exclude when copying skills
COPY_IGNORE_PATTERNS = shutil.ignore_patterns(
    ".git", "__pycache__", "node_modules", ".venv", "venv", "env",
    ".pytest_cache", ".mypy_cache", "dist", "build", "*.pyc", "*.pyo",
)

# Stop words for auto-tagging
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "is", "are", "was", "were", "be",
    "been", "being", "in", "on", "at", "to", "for", "of", "with", "by",
    "from", "as", "into", "through", "during", "before", "after", "above",
    "below", "between", "out", "off", "over", "under", "again", "further",
    "then", "once", "here", "there", "when", "where", "why", "how", "all",
    "each", "every", "both", "few", "more", "most", "other", "some", "such",
    "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very",
    "can", "will", "just", "should", "now", "it", "its", "this", "that",
    "these", "those", "he", "she", "we", "they", "what", "which", "who",
    "whom", "do", "does", "did", "has", "have", "had", "having", "using",
}

MIN_TAG_LENGTH = 3


# --- Namespacing & date parsing helpers ---

def _slug(value: str) -> str:
    """Return a filesystem-safe slug for an author/namespace path segment."""
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip().lower()).strip("-")
    return slug or "unknown"


def skill_storage_path(name: str, author: str) -> str:
    """
    Relative registry path for a skill's files, namespaced by author.

    A skill with an author is stored under ``skills/<author-slug>/<name>`` so
    two authors can publish the same skill name without clobbering each other's
    files. Authorless skills keep the legacy flat ``skills/<name>`` layout for
    backward compatibility with registries created before namespacing.
    """
    if author:
        return f"skills/{_slug(author)}/{name}"
    return f"skills/{name}"


def resolve_skill_entry(
    data: dict, name: str, author: str | None = None
) -> tuple[dict | None, str | None]:
    """
    Find a single skill entry by name, disambiguating by author when needed.

    Returns ``(entry, None)`` on a unique match, or ``(None, error_message)``
    when the skill is missing or the name is shared by multiple authors and no
    ``author`` filter was supplied.
    """
    matches = [s for s in data["skills"] if s.get("name") == name]
    if author is not None:
        matches = [s for s in matches if s.get("author", "") == author]

    if not matches:
        return None, f"skill '{name}' not found in registry."

    authors = sorted({s.get("author", "") for s in matches})
    if len(authors) > 1:
        listed = ", ".join(a or "(no author)" for a in authors)
        return None, (
            f"skill '{name}' is published by multiple authors ({listed}); "
            f"use --author to disambiguate."
        )

    # Unique (name, author); preserve first-published selection across versions.
    return matches[0], None


def parse_iso_date(value: str) -> date | None:
    """
    Parse an ISO date or timestamp string into a ``date``.

    Accepts both plain dates ("2026-06-13") and full ISO timestamps
    ("2026-06-13T12:00:00+00:00"). Returns None for empty or unparseable input.
    """
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None


# --- Registry I/O ---

def load_registry(registry_path: Path) -> dict:
    """Read and parse registry.json from the registry directory."""
    manifest = registry_path / "registry.json"
    if not manifest.exists():
        print(f"Error: registry.json not found in {registry_path}", file=sys.stderr)
        print("Run 'skill_registry.py init' first.", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(manifest.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Error reading registry.json: {exc}", file=sys.stderr)
        sys.exit(1)


def save_registry(registry_path: Path, data: dict) -> None:
    """Atomic write: write to .tmp then rename."""
    manifest = registry_path / "registry.json"
    tmp = registry_path / "registry.json.tmp"
    try:
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(manifest)
    except OSError as exc:
        # Clean up tmp on failure
        if tmp.exists():
            tmp.unlink()
        print(f"Error writing registry.json: {exc}", file=sys.stderr)
        sys.exit(1)


# --- Metadata Extraction ---

def extract_skill_metadata(skill_path: Path) -> dict:
    """
    Parse SKILL.md frontmatter into a metadata dict.

    Returns dict with keys: name, description, version, author, license.
    Missing fields default to empty string.
    """
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return {"name": "", "description": "", "version": "", "author": "", "license": ""}

    content = skill_md.read_text(encoding="utf-8")
    doc = SkillDoc.from_text(content)
    if doc.frontmatter is None:
        return {"name": "", "description": "", "version": "", "author": "", "license": ""}

    meta = doc.metadata
    # Version: try metadata.version first, then top-level version
    version = meta.get("version") or doc.field("version") or ""

    return {
        "name": (doc.name or "").strip(),
        "description": (doc.description or "").strip(),
        "version": version.strip(),
        "author": meta.get("author", "").strip(),
        "license": (doc.license or "").strip(),
        "created": meta.get("created", "").strip(),
        "last_reviewed": meta.get("last_reviewed", "").strip(),
        "review_interval_days": meta.get("review_interval_days", "").strip(),
    }


def auto_extract_tags(description: str) -> list[str]:
    """
    Extract keyword tags from a description string.

    Splits on non-alphanumeric characters, filters stop words and short words,
    returns up to 10 unique lowercase tags.
    """
    if not description:
        return []
    words = re.split(r"[^a-zA-Z0-9-]+", description.lower())
    seen: set[str] = set()
    tags: list[str] = []
    for word in words:
        word = word.strip("-")
        if len(word) < MIN_TAG_LENGTH:
            continue
        if word in STOP_WORDS:
            continue
        if word not in seen:
            seen.add(word)
            tags.append(word)
        if len(tags) >= 10:
            break
    return tags


# --- Platform Detection ---

def detect_platform() -> str:
    """
    Auto-detect the installed agent platform by checking known directories.

    Returns the platform name or "claude-code" as default.
    """
    checks = [(p.name, p.detect_dir) for p in PLATFORMS if p.detect_dir]
    for platform, path in checks:
        if Path(path).expanduser().exists():
            return platform
    print(
        "Note: no agent platform detected; defaulting to claude-code "
        "(use --platform to override)",
        file=sys.stderr,
    )
    return "claude-code"


def resolve_install_path(name: str, platform: str, project: bool) -> Path:
    """
    Map platform + scope to the filesystem install path for a skill.

    Args:
        name: Skill name (used as subdirectory).
        platform: Platform identifier.
        project: If True, use project-level path; otherwise user-level.

    Returns:
        Absolute path where the skill should be installed.
    """
    if project:
        base = PLATFORM_PATHS_PROJECT.get(platform)
    else:
        base = PLATFORM_PATHS_USER.get(platform)

    if base is None:
        print(f"Error: unknown platform '{platform}'", file=sys.stderr)
        print(f"Supported: {', '.join(ALL_PLATFORMS)}", file=sys.stderr)
        sys.exit(1)

    return Path(base).expanduser().resolve() / name


# --- Table Formatting ---

def _format_table(entries: list[dict]) -> str:
    """Format skill entries as an aligned text table."""
    if not entries:
        return "No skills found."

    headers = ["NAME", "VERSION", "AUTHOR", "TAGS"]
    rows = []
    for entry in entries:
        tags = ", ".join(entry.get("tags", []))
        rows.append([
            entry.get("name", ""),
            entry.get("version", ""),
            entry.get("author", ""),
            tags,
        ])

    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    # Build output
    lines = []
    header_line = "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    lines.append(header_line)
    for row in rows:
        lines.append("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)))
    return "\n".join(lines)


# --- Subcommands ---

def cmd_init(args: argparse.Namespace) -> None:
    """Initialize a new skill registry."""
    registry_path = Path(args.registry).resolve()
    manifest = registry_path / "registry.json"

    if manifest.exists():
        print(f"Error: registry already exists at {registry_path}", file=sys.stderr)
        sys.exit(1)

    registry_path.mkdir(parents=True, exist_ok=True)
    (registry_path / "skills").mkdir(exist_ok=True)

    name = args.name or "Shared Skills"
    data = {
        "registry": {
            "name": name,
            "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "schema_version": "1",
        },
        "skills": [],
    }
    save_registry(registry_path, data)
    print(f"Registry initialized: {registry_path}")
    print(f"  Name: {name}")
    print(f"  Manifest: {manifest}")
    print(f"  Skills dir: {registry_path / 'skills'}")


def cmd_publish(args: argparse.Namespace) -> None:
    """Publish a skill to the registry."""
    registry_path = Path(args.registry).resolve()
    skill_path = Path(args.skill_path).resolve()

    if not skill_path.is_dir():
        print(f"Error: skill path is not a directory: {skill_path}", file=sys.stderr)
        sys.exit(1)

    # Step 1: Validate
    validation = validate_skill(str(skill_path))
    if not validation["valid"]:
        print("Validation failed:", file=sys.stderr)
        for err in validation["errors"]:
            print(f"  [ERROR] {err}", file=sys.stderr)
        sys.exit(1)

    # Step 2: Security scan
    scan = security_scan(str(skill_path))
    high_issues = [i for i in scan["issues"] if i["severity"] == "high"]
    other_issues = [i for i in scan["issues"] if i["severity"] != "high"]

    if other_issues:
        for issue in other_issues:
            location = issue["file"]
            if issue["line"] > 0:
                location += f":{issue['line']}"
            print(f"  [WARN] {location}: {issue['description']}")

    if high_issues and not args.force:
        print("Security scan found high-severity issues:", file=sys.stderr)
        for issue in high_issues:
            location = issue["file"]
            if issue["line"] > 0:
                location += f":{issue['line']}"
            print(f"  [HIGH] {location}: {issue['description']}", file=sys.stderr)
        print("Use --force to publish anyway.", file=sys.stderr)
        sys.exit(1)

    # Step 3: Extract metadata
    metadata = extract_skill_metadata(skill_path)
    name = metadata["name"]
    version = metadata["version"] or "0.0.0"

    if not name:
        print("Error: could not extract skill name from SKILL.md frontmatter", file=sys.stderr)
        sys.exit(1)

    # Step 4: Tags
    tags = []
    if args.tags:
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    if not tags:
        tags = auto_extract_tags(metadata["description"])

    author = metadata["author"]

    # Step 5: Check duplicates. Identity is (name, author, version) so two
    # authors can publish the same skill name without colliding.
    data = load_registry(registry_path)

    def _same_skill(s: dict) -> bool:
        return (
            s["name"] == name
            and s.get("author", "") == author
            and s["version"] == version
        )

    for existing in data["skills"]:
        if _same_skill(existing):
            if not args.force:
                who = f" by '{author}'" if author else ""
                print(
                    f"Error: skill '{name}' version '{version}'{who} already exists in registry.",
                    file=sys.stderr,
                )
                print("Use --force to overwrite.", file=sys.stderr)
                sys.exit(1)
            # Remove old entry if forcing
            data["skills"] = [s for s in data["skills"] if not _same_skill(s)]

    # Step 6: Copy skill to registry (author-namespaced path)
    rel_path = skill_storage_path(name, author)
    dest = registry_path / rel_path
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(skill_path, dest, ignore=COPY_IGNORE_PATTERNS)

    # Step 7: Add entry (including staleness metadata)
    staleness_data = {}
    if metadata.get("created"):
        staleness_data["created"] = metadata["created"]
    if metadata.get("last_reviewed"):
        staleness_data["last_reviewed"] = metadata["last_reviewed"]
    if metadata.get("review_interval_days"):
        try:
            staleness_data["review_interval_days"] = int(metadata["review_interval_days"])
        except ValueError:
            pass

    entry = {
        "name": name,
        "description": metadata["description"],
        "version": version,
        "author": author,
        "license": metadata["license"],
        "tags": tags,
        "platforms": list(ALL_PLATFORMS),
        "published": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "path": rel_path,
        "validation": {
            "valid": validation["valid"],
            "errors": len(validation["errors"]),
            "warnings": len(validation["warnings"]),
        },
        "security": {
            "clean": scan["clean"],
            "issues": len(scan["issues"]),
        },
        "staleness": staleness_data,
    }
    data["skills"].append(entry)
    save_registry(registry_path, data)

    if getattr(args, "json", False):
        print(json.dumps(entry, indent=2))
    else:
        print(f"Published '{name}' v{version} to registry.")
        print(f"  Path: {dest}")
        print(f"  Tags: {', '.join(tags)}")


def cmd_list(args: argparse.Namespace) -> None:
    """List all skills in the registry."""
    registry_path = Path(args.registry).resolve()
    data = load_registry(registry_path)

    if getattr(args, "json", False):
        print(json.dumps(data["skills"], indent=2))
        return

    print(_format_table(data["skills"]))


def cmd_search(args: argparse.Namespace) -> None:
    """Search for skills matching a query."""
    registry_path = Path(args.registry).resolve()
    data = load_registry(registry_path)
    query = args.query.lower()

    matches = []
    for skill in data["skills"]:
        searchable = " ".join([
            skill.get("name", ""),
            skill.get("description", ""),
            skill.get("author", ""),
            " ".join(skill.get("tags", [])),
        ]).lower()
        if query in searchable:
            matches.append(skill)

    if getattr(args, "json", False):
        print(json.dumps(matches, indent=2))
        return

    if not matches:
        print(f"No skills matching '{args.query}'.")
        return

    print(f"Skills matching '{args.query}':\n")
    print(_format_table(matches))


def cmd_install(args: argparse.Namespace) -> None:
    """Install a skill from the registry."""
    registry_path = Path(args.registry).resolve()
    data = load_registry(registry_path)

    # Find skill (disambiguating by author when the name is shared)
    skill_entry, error = resolve_skill_entry(data, args.skill_name, getattr(args, "author", None))
    if skill_entry is None:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    # Resolve platform
    platform = args.platform or detect_platform()
    if platform not in ALL_PLATFORMS:
        print(f"Error: unknown platform '{platform}'", file=sys.stderr)
        print(f"Supported: {', '.join(ALL_PLATFORMS)}", file=sys.stderr)
        sys.exit(1)

    # Resolve target path
    project = getattr(args, "project", False)
    target = resolve_install_path(args.skill_name, platform, project)

    # Check if already installed
    if target.exists() and not args.force:
        print(f"Error: skill already installed at {target}", file=sys.stderr)
        print("Use --force to overwrite.", file=sys.stderr)
        sys.exit(1)

    # Copy
    source = registry_path / skill_entry["path"]
    if not source.exists():
        print(f"Error: skill files not found at {source}", file=sys.stderr)
        sys.exit(1)

    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, ignore=COPY_IGNORE_PATTERNS)

    if getattr(args, "json", False):
        print(json.dumps({
            "installed": True,
            "skill": args.skill_name,
            "platform": platform,
            "path": str(target),
        }, indent=2))
        return

    scope = "project" if project else "user"
    print(f"Installed '{args.skill_name}' for {platform} ({scope}-level).")
    print(f"  Path: {target}")

    # Platform-specific activation tips
    tips = {
        "claude-code": "Skill is auto-loaded. Start a new conversation to activate.",
        "copilot":     "Skill is auto-loaded by Copilot Chat.",
        "cursor":      "Skill is loaded alongside .mdc rules.",
        "windsurf":    "Skill is auto-loaded by Windsurf.",
        "cline":       "Skill is loaded from .clinerules.",
        "codex":       "Skill is auto-loaded by Codex CLI.",
        "gemini":      "Skill is auto-loaded by Gemini CLI.",
    }
    tip = tips.get(platform)
    if tip:
        print(f"  Tip: {tip}")


def cmd_info(args: argparse.Namespace) -> None:
    """Show detailed info about a skill."""
    registry_path = Path(args.registry).resolve()
    data = load_registry(registry_path)

    skill_entry, error = resolve_skill_entry(data, args.skill_name, getattr(args, "author", None))
    if skill_entry is None:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    if getattr(args, "json", False):
        print(json.dumps(skill_entry, indent=2))
        return

    print(f"Skill: {skill_entry['name']}")
    print(f"{'=' * 50}")
    print(f"  Version:     {skill_entry.get('version', 'N/A')}")
    print(f"  Author:      {skill_entry.get('author', 'N/A')}")
    print(f"  License:     {skill_entry.get('license', 'N/A')}")
    print(f"  Description: {skill_entry.get('description', 'N/A')}")
    print(f"  Tags:        {', '.join(skill_entry.get('tags', []))}")
    print(f"  Platforms:   {', '.join(skill_entry.get('platforms', []))}")
    print(f"  Published:   {skill_entry.get('published', 'N/A')}")
    print(f"  Path:        {skill_entry.get('path', 'N/A')}")

    validation = skill_entry.get("validation", {})
    if validation:
        status = "valid" if validation.get("valid") else "invalid"
        print(f"  Validation:  {status} ({validation.get('errors', 0)} errors, {validation.get('warnings', 0)} warnings)")

    security = skill_entry.get("security", {})
    if security:
        status = "clean" if security.get("clean") else f"{security.get('issues', 0)} issues"
        print(f"  Security:    {status}")

    print(f"{'=' * 50}")


def cmd_remove(args: argparse.Namespace) -> None:
    """Remove a skill from the registry."""
    registry_path = Path(args.registry).resolve()
    data = load_registry(registry_path)

    # Find skill (disambiguating by author when the name is shared)
    skill_entry, error = resolve_skill_entry(data, args.skill_name, getattr(args, "author", None))
    if skill_entry is None:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    if not args.force:
        print(f"Remove '{args.skill_name}' from registry? Use --force to confirm.", file=sys.stderr)
        sys.exit(1)

    # Remove files
    skill_dir = registry_path / skill_entry["path"]
    if skill_dir.exists():
        shutil.rmtree(skill_dir)

    # Remove only the resolved author's entries for this name (all versions).
    target_author = skill_entry.get("author", "")
    data["skills"] = [
        s for s in data["skills"]
        if not (s["name"] == args.skill_name and s.get("author", "") == target_author)
    ]
    save_registry(registry_path, data)

    print(f"Removed '{args.skill_name}' from registry.")


def cmd_stale(args: argparse.Namespace) -> None:
    """Report skills that are overdue for review."""
    from datetime import timedelta

    registry_path = Path(args.registry).resolve()
    data = load_registry(registry_path)
    today = date.today()

    results: list[dict] = []
    for skill in data["skills"]:
        staleness = skill.get("staleness", {})
        published = skill.get("published", "")

        # Determine reference date: last_reviewed > created > published
        ref_date = None
        date_source = "none"

        for value, source in (
            (staleness.get("last_reviewed", ""), "last_reviewed"),
            (staleness.get("created", ""), "created"),
            (published, "published"),
        ):
            ref_date = parse_iso_date(value)
            if ref_date is not None:
                date_source = source
                break

        interval = staleness.get("review_interval_days", DEFAULT_REVIEW_INTERVAL_DAYS)
        if not isinstance(interval, int):
            try:
                interval = int(interval)
            except (ValueError, TypeError):
                interval = DEFAULT_REVIEW_INTERVAL_DAYS

        days_since = None
        status = "unknown"
        if ref_date:
            days_since = (today - ref_date).days
            deadline = ref_date + timedelta(days=interval)
            if today > deadline:
                status = "overdue"
            elif (deadline - today).days <= 30:
                status = "due_soon"
            else:
                status = "fresh"

        results.append({
            "name": skill.get("name", ""),
            "version": skill.get("version", ""),
            "status": status,
            "days_since_review": days_since,
            "date_source": date_source,
            "review_interval_days": interval,
        })

    if getattr(args, "json", False):
        print(json.dumps(results, indent=2))
        return

    # Text table output
    if not results:
        print("No skills in registry.")
        return

    headers = ["NAME", "VERSION", "STATUS", "DAYS SINCE", "SOURCE", "INTERVAL"]
    rows = []
    for r in results:
        rows.append([
            r["name"],
            r["version"],
            r["status"].upper(),
            str(r["days_since_review"]) if r["days_since_review"] is not None else "N/A",
            r["date_source"],
            str(r["review_interval_days"]),
        ])

    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    header_line = "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print(header_line)
    for row in rows:
        print("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)))

    # Summary
    overdue = sum(1 for r in results if r["status"] == "overdue")
    due_soon = sum(1 for r in results if r["status"] == "due_soon")
    if overdue or due_soon:
        print(f"\nSummary: {overdue} overdue, {due_soon} due soon, {len(results)} total")


# --- CLI ---

def _add_registry_arg(parser: argparse.ArgumentParser) -> None:
    """Add the --registry argument to a subparser."""
    parser.add_argument(
        "--registry", default="./registry",
        help="Path to the registry directory (default: ./registry)",
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="skill_registry",
        description="Git-based shared skill registry for cross-platform agent skills.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init
    p_init = subparsers.add_parser("init", help="Initialize a new skill registry")
    _add_registry_arg(p_init)
    p_init.add_argument("--name", help="Registry name (default: 'Shared Skills')")

    # publish
    p_publish = subparsers.add_parser("publish", help="Publish a skill to the registry")
    p_publish.add_argument("skill_path", help="Path to the skill directory")
    _add_registry_arg(p_publish)
    p_publish.add_argument("--tags", help="Comma-separated tags (auto-extracted if omitted)")
    p_publish.add_argument("--force", action="store_true", help="Overwrite existing or ignore high-severity issues")
    p_publish.add_argument("--json", action="store_true", help="Output as JSON")

    # list
    p_list = subparsers.add_parser("list", help="List all skills in the registry")
    _add_registry_arg(p_list)
    p_list.add_argument("--json", action="store_true", help="Output as JSON")

    # search
    p_search = subparsers.add_parser("search", help="Search for skills")
    p_search.add_argument("query", help="Search query (matches name, description, author, tags)")
    _add_registry_arg(p_search)
    p_search.add_argument("--json", action="store_true", help="Output as JSON")

    # install
    p_install = subparsers.add_parser("install", help="Install a skill from the registry")
    p_install.add_argument("skill_name", help="Name of the skill to install")
    _add_registry_arg(p_install)
    p_install.add_argument("--author", help="Disambiguate when the name is shared by multiple authors")
    p_install.add_argument("--platform", choices=ALL_PLATFORMS, help="Target platform (auto-detected if omitted)")
    p_install.add_argument("--project", action="store_true", help="Install at project level instead of user level")
    p_install.add_argument("--force", action="store_true", help="Overwrite existing installation")
    p_install.add_argument("--json", action="store_true", help="Output as JSON")

    # info
    p_info = subparsers.add_parser("info", help="Show detailed info about a skill")
    p_info.add_argument("skill_name", help="Name of the skill")
    _add_registry_arg(p_info)
    p_info.add_argument("--author", help="Disambiguate when the name is shared by multiple authors")
    p_info.add_argument("--json", action="store_true", help="Output as JSON")

    # remove
    p_remove = subparsers.add_parser("remove", help="Remove a skill from the registry")
    p_remove.add_argument("skill_name", help="Name of the skill to remove")
    _add_registry_arg(p_remove)
    p_remove.add_argument("--author", help="Disambiguate when the name is shared by multiple authors")
    p_remove.add_argument("--force", action="store_true", help="Confirm removal")

    # stale
    p_stale = subparsers.add_parser("stale", help="Report skills overdue for review")
    _add_registry_arg(p_stale)
    p_stale.add_argument("--json", action="store_true", help="Output as JSON")

    return parser


def main() -> None:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    commands = {
        "init":    cmd_init,
        "publish": cmd_publish,
        "list":    cmd_list,
        "search":  cmd_search,
        "install": cmd_install,
        "info":    cmd_info,
        "remove":  cmd_remove,
        "stale":   cmd_stale,
    }

    cmd_func = commands.get(args.command)
    if cmd_func is None:
        parser.print_help()
        sys.exit(1)

    cmd_func(args)


if __name__ == "__main__":
    main()
