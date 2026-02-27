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
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# --- Import sibling scripts ---

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from validate import validate_skill, _parse_frontmatter, _parse_yaml_field, _parse_subfield_value
from security_scan import security_scan
from staleness_check import DEFAULT_REVIEW_INTERVAL_DAYS


# --- Constants ---

ALL_PLATFORMS = ["claude-code", "copilot", "cursor", "windsurf", "cline", "codex", "gemini"]

PLATFORM_PATHS_USER = {
    "claude-code": "~/.claude/skills",
    "copilot":     "~/.copilot/skills",
    "cursor":      "~/.cursor/rules",
    "windsurf":    "~/.windsurf/skills",
    "cline":       "~/.cline/rules",
    "codex":       "~/.codex/skills",
    "gemini":      "~/.gemini/skills",
}

PLATFORM_PATHS_PROJECT = {
    "claude-code": ".claude/skills",
    "copilot":     ".github/skills",
    "cursor":      ".cursor/rules",
    "windsurf":    ".windsurf/skills",
    "cline":       ".clinerules",
    "codex":       ".codex/skills",
    "gemini":      ".gemini/skills",
}

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
    frontmatter, _ = _parse_frontmatter(content)
    if frontmatter is None:
        return {"name": "", "description": "", "version": "", "author": "", "license": ""}

    name = _parse_yaml_field(frontmatter, "name") or ""
    description = _parse_yaml_field(frontmatter, "description") or ""
    license_val = _parse_yaml_field(frontmatter, "license") or ""

    # Version: try metadata.version first, then top-level version
    version = _parse_subfield_value(frontmatter, "metadata", "version")
    if not version:
        version = _parse_yaml_field(frontmatter, "version") or ""

    # Author: try metadata.author first
    author = _parse_subfield_value(frontmatter, "metadata", "author") or ""

    # Temporal metadata for staleness tracking
    created = _parse_subfield_value(frontmatter, "metadata", "created") or ""
    last_reviewed = _parse_subfield_value(frontmatter, "metadata", "last_reviewed") or ""
    interval = _parse_subfield_value(frontmatter, "metadata", "review_interval_days") or ""

    return {
        "name": name.strip(),
        "description": description.strip(),
        "version": version.strip(),
        "author": author.strip(),
        "license": license_val.strip(),
        "created": created.strip(),
        "last_reviewed": last_reviewed.strip(),
        "review_interval_days": interval.strip(),
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
    checks = [
        ("claude-code", "~/.claude"),
        ("copilot",     "~/.copilot"),
        ("cursor",      "~/.cursor"),
        ("windsurf",    "~/.windsurf"),
        ("cline",       "~/.cline"),
        ("codex",       "~/.codex"),
        ("gemini",      "~/.gemini"),
    ]
    for platform, path in checks:
        if Path(path).expanduser().exists():
            return platform
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

    # Step 5: Check duplicates
    data = load_registry(registry_path)
    for existing in data["skills"]:
        if existing["name"] == name and existing["version"] == version:
            if not args.force:
                print(
                    f"Error: skill '{name}' version '{version}' already exists in registry.",
                    file=sys.stderr,
                )
                print("Use --force to overwrite.", file=sys.stderr)
                sys.exit(1)
            # Remove old entry if forcing
            data["skills"] = [s for s in data["skills"] if not (s["name"] == name and s["version"] == version)]

    # Step 6: Copy skill to registry
    dest = registry_path / "skills" / name
    if dest.exists():
        shutil.rmtree(dest)
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
        "author": metadata["author"],
        "license": metadata["license"],
        "tags": tags,
        "platforms": list(ALL_PLATFORMS),
        "published": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "path": f"skills/{name}",
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

    # Find skill
    skill_entry = None
    for skill in data["skills"]:
        if skill["name"] == args.skill_name:
            skill_entry = skill
            break

    if skill_entry is None:
        print(f"Error: skill '{args.skill_name}' not found in registry.", file=sys.stderr)
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

    skill_entry = None
    for skill in data["skills"]:
        if skill["name"] == args.skill_name:
            skill_entry = skill
            break

    if skill_entry is None:
        print(f"Error: skill '{args.skill_name}' not found in registry.", file=sys.stderr)
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

    # Find skill
    skill_entry = None
    for skill in data["skills"]:
        if skill["name"] == args.skill_name:
            skill_entry = skill
            break

    if skill_entry is None:
        print(f"Error: skill '{args.skill_name}' not found in registry.", file=sys.stderr)
        sys.exit(1)

    if not args.force:
        print(f"Remove '{args.skill_name}' from registry? Use --force to confirm.", file=sys.stderr)
        sys.exit(1)

    # Remove files
    skill_dir = registry_path / skill_entry["path"]
    if skill_dir.exists():
        shutil.rmtree(skill_dir)

    # Remove entry
    data["skills"] = [s for s in data["skills"] if s["name"] != args.skill_name]
    save_registry(registry_path, data)

    print(f"Removed '{args.skill_name}' from registry.")


def cmd_stale(args: argparse.Namespace) -> None:
    """Report skills that are overdue for review."""
    from datetime import date, timedelta

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

        lr = staleness.get("last_reviewed", "")
        cr = staleness.get("created", "")

        if lr:
            try:
                parts = lr.split("-")
                ref_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
                date_source = "last_reviewed"
            except (ValueError, IndexError):
                pass

        if ref_date is None and cr:
            try:
                parts = cr.split("-")
                ref_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
                date_source = "created"
            except (ValueError, IndexError):
                pass

        if ref_date is None and published:
            try:
                parts = published[:10].split("-")
                ref_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
                date_source = "published"
            except (ValueError, IndexError):
                pass

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
    p_install.add_argument("--platform", choices=ALL_PLATFORMS, help="Target platform (auto-detected if omitted)")
    p_install.add_argument("--project", action="store_true", help="Install at project level instead of user level")
    p_install.add_argument("--force", action="store_true", help="Overwrite existing installation")
    p_install.add_argument("--json", action="store_true", help="Output as JSON")

    # info
    p_info = subparsers.add_parser("info", help="Show detailed info about a skill")
    p_info.add_argument("skill_name", help="Name of the skill")
    _add_registry_arg(p_info)
    p_info.add_argument("--json", action="store_true", help="Output as JSON")

    # remove
    p_remove = subparsers.add_parser("remove", help="Remove a skill from the registry")
    p_remove.add_argument("skill_name", help="Name of the skill to remove")
    _add_registry_arg(p_remove)
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
