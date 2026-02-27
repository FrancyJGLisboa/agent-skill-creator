#!/usr/bin/env python3
"""
Staleness Detection for Agent Skills.

Checks whether a skill is overdue for review, validates dependency health,
and detects schema drift in declared API endpoints. Designed to surface
skills that may have gone stale as APIs change, compliance rules update,
and data sources move.

Usage:
    python3 scripts/staleness_check.py <skill-path> [--json] [--check-deps] [--check-drift]

Exit codes:
    0 - Fresh (no staleness issues)
    1 - Stale (overdue for review)
    2 - Degraded (dependency failures or schema drift)
"""

import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

# --- Import sibling scripts ---

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from validate import _parse_frontmatter, _parse_subfield_value  # noqa: E402


# --- Constants ---

DEFAULT_REVIEW_INTERVAL_DAYS = 90
STALENESS_WARNING_THRESHOLD_DAYS = 60
HTTP_TIMEOUT_SECONDS = 10
DATE_PATTERN_RE = None  # Lazy-compiled below


def _date_pattern():
    """Return compiled regex for YYYY-MM-DD date format."""
    global DATE_PATTERN_RE
    if DATE_PATTERN_RE is None:
        import re
        DATE_PATTERN_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    return DATE_PATTERN_RE


def _parse_date(value: str) -> Optional[date]:
    """
    Parse a YYYY-MM-DD string into a date object.

    Args:
        value: Date string in YYYY-MM-DD format.

    Returns:
        A date object, or None if parsing fails.
    """
    if not value or not _date_pattern().match(value.strip()):
        return None
    try:
        parts = value.strip().split("-")
        return date(int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, IndexError):
        return None


def _get_git_last_modified(skill_path: str) -> Optional[date]:
    """
    Get the last git commit date for a skill directory.

    Runs ``git log -1 --format=%aI`` on the SKILL.md file as a fallback
    for skills without explicit review dates.

    Args:
        skill_path: Path to the skill directory.

    Returns:
        The date of the last git commit touching SKILL.md, or None
        if git is unavailable or the file is untracked.
    """
    skill_md = Path(skill_path).resolve() / "SKILL.md"
    if not skill_md.exists():
        return None
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--", str(skill_md)],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(Path(skill_path).resolve()),
        )
        if result.returncode != 0 or not result.stdout.strip():
            return None
        # ISO format: 2025-01-15T10:30:00+00:00 -- take the date part
        iso_str = result.stdout.strip()
        return _parse_date(iso_str[:10])
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def _check_review_staleness(frontmatter: str, git_last_modified: Optional[date]) -> list[dict]:
    """
    Check whether a skill is overdue for review.

    Compares ``metadata.last_reviewed`` against ``metadata.review_interval_days``.
    Falls back to the git commit date when explicit review dates are absent.

    Args:
        frontmatter: The frontmatter text (without delimiters).
        git_last_modified: Fallback date from git log.

    Returns:
        List of issue dicts with keys: level, message, detail.
    """
    issues: list[dict] = []
    today = date.today()

    # Extract temporal fields
    created_str = _parse_subfield_value(frontmatter, "metadata", "created")
    last_reviewed_str = _parse_subfield_value(frontmatter, "metadata", "last_reviewed")
    interval_str = _parse_subfield_value(frontmatter, "metadata", "review_interval_days")

    # Validate formats if present
    if created_str and not _parse_date(created_str):
        issues.append({
            "level": "warning",
            "message": "Invalid 'metadata.created' date format",
            "detail": f"Expected YYYY-MM-DD, got: '{created_str}'",
        })

    if last_reviewed_str and not _parse_date(last_reviewed_str):
        issues.append({
            "level": "warning",
            "message": "Invalid 'metadata.last_reviewed' date format",
            "detail": f"Expected YYYY-MM-DD, got: '{last_reviewed_str}'",
        })

    if interval_str:
        try:
            int(interval_str)
        except ValueError:
            issues.append({
                "level": "warning",
                "message": "Invalid 'metadata.review_interval_days' value",
                "detail": f"Expected integer, got: '{interval_str}'",
            })

    # Determine review interval
    interval_days = DEFAULT_REVIEW_INTERVAL_DAYS
    if interval_str:
        try:
            interval_days = int(interval_str)
        except ValueError:
            pass

    # Determine the reference date (last_reviewed > git date > None)
    reference_date = None
    date_source = "unknown"

    last_reviewed = _parse_date(last_reviewed_str) if last_reviewed_str else None
    if last_reviewed:
        reference_date = last_reviewed
        date_source = "last_reviewed"
    elif git_last_modified:
        reference_date = git_last_modified
        date_source = "git_commit"
    else:
        issues.append({
            "level": "info",
            "message": "No review date available",
            "detail": "No 'metadata.last_reviewed' and no git history found. "
                      "Consider adding temporal metadata.",
        })

    # Check staleness
    days_since = None
    review_status = "unknown"

    if reference_date:
        days_since = (today - reference_date).days
        deadline = reference_date + timedelta(days=interval_days)
        warning_date = reference_date + timedelta(days=STALENESS_WARNING_THRESHOLD_DAYS)

        if today > deadline:
            review_status = "overdue"
            issues.append({
                "level": "error",
                "message": f"Skill is overdue for review ({days_since} days since last review)",
                "detail": f"Review interval is {interval_days} days. "
                          f"Last review: {reference_date} (source: {date_source}). "
                          f"Deadline was: {deadline}.",
            })
        elif today > warning_date:
            review_status = "due_soon"
            days_remaining = (deadline - today).days
            issues.append({
                "level": "warning",
                "message": f"Review due in {days_remaining} days",
                "detail": f"Last review: {reference_date} (source: {date_source}). "
                          f"Deadline: {deadline}.",
            })
        else:
            review_status = "fresh"

    # Missing temporal metadata suggestion
    has_any_temporal = bool(created_str or last_reviewed_str or interval_str)
    if not has_any_temporal:
        issues.append({
            "level": "info",
            "message": "No temporal metadata found",
            "detail": "Consider adding metadata.created, metadata.last_reviewed, "
                      "and metadata.review_interval_days to frontmatter.",
        })

    return issues, review_status, days_since, date_source


def _parse_yaml_list(frontmatter: str, parent: str, child: str) -> list[dict]:
    """
    Parse a YAML list-of-objects under a parent.child path in frontmatter.

    Handles the pattern::

        metadata:
          dependencies:
            - url: https://example.com
              name: Example
              type: api

    Args:
        frontmatter: The frontmatter text.
        parent: Top-level field (e.g. ``metadata``).
        child: Second-level field (e.g. ``dependencies``).

    Returns:
        List of dicts, each representing one list item.
    """
    lines = frontmatter.split("\n")
    items: list[dict] = []

    # Find the parent block
    in_parent = False
    in_child = False
    current_item: Optional[dict] = None
    child_indent = -1

    for line in lines:
        stripped = line.strip()

        if not in_parent:
            if stripped.startswith(f"{parent}:"):
                in_parent = True
            continue

        # Inside parent -- check if we've left it
        if line and line[0] != " " and line[0] != "\t" and stripped:
            break

        if not in_child:
            if stripped.startswith(f"{child}:"):
                in_child = True
            continue

        # Inside child list
        if not stripped:
            continue

        # Detect indent level of list items
        raw_indent = len(line) - len(line.lstrip())

        if child_indent == -1 and stripped.startswith("- "):
            child_indent = raw_indent

        # Check if we've left the child block
        if raw_indent <= child_indent and not stripped.startswith("- "):
            # Check if this is a sibling of child (another metadata key)
            if ":" in stripped:
                break

        if stripped.startswith("- "):
            # New list item
            if current_item is not None:
                items.append(current_item)
            current_item = {}
            # Parse "- key: value" on the same line
            rest = stripped[2:].strip()
            if ":" in rest:
                key, _, val = rest.partition(":")
                current_item[key.strip()] = val.strip()
        elif current_item is not None and ":" in stripped:
            # Continuation key-value in the same list item
            key, _, val = stripped.partition(":")
            current_item[key.strip()] = val.strip()

    if current_item is not None:
        items.append(current_item)

    return items


def _check_dependency_health(dependencies: list[dict]) -> list[dict]:
    """
    HTTP HEAD each declared dependency URL and report health status.

    Args:
        dependencies: List of dependency dicts with at least a ``url`` key.

    Returns:
        List of issue dicts reporting the health of each dependency.
    """
    issues: list[dict] = []

    for dep in dependencies:
        url = dep.get("url", "").strip()
        name = dep.get("name", url)

        if not url:
            issues.append({
                "level": "warning",
                "message": f"Dependency '{name}' has no URL",
                "detail": "Cannot check health without a URL.",
            })
            continue

        if not url.startswith(("http://", "https://")):
            issues.append({
                "level": "warning",
                "message": f"Dependency '{name}' has non-HTTP URL",
                "detail": f"Skipping health check for: {url}",
            })
            continue

        try:
            req = Request(url, method="HEAD")
            req.add_header("User-Agent", "agent-skill-staleness-check/1.0")
            with urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
                status = resp.status
                if 200 <= status < 400:
                    issues.append({
                        "level": "info",
                        "message": f"Dependency '{name}' is healthy",
                        "detail": f"HTTP {status} from {url}",
                    })
                elif 400 <= status < 500:
                    issues.append({
                        "level": "warning",
                        "message": f"Dependency '{name}' returned client error",
                        "detail": f"HTTP {status} from {url}. "
                                  "The endpoint may have moved or require authentication.",
                    })
                else:
                    issues.append({
                        "level": "error",
                        "message": f"Dependency '{name}' returned server error",
                        "detail": f"HTTP {status} from {url}",
                    })
        except URLError as exc:
            issues.append({
                "level": "error",
                "message": f"Dependency '{name}' is unreachable",
                "detail": f"Failed to connect to {url}: {exc.reason}",
            })
        except Exception as exc:
            issues.append({
                "level": "error",
                "message": f"Dependency '{name}' check failed",
                "detail": f"Error checking {url}: {exc}",
            })

    return issues


def _parse_schema_expectations(frontmatter: str) -> list[dict]:
    """
    Extract ``metadata.schema_expectations`` list from frontmatter.

    Each expectation has: url, method (default GET), expected_keys (list).

    Args:
        frontmatter: The frontmatter text.

    Returns:
        List of schema expectation dicts.
    """
    raw_items = _parse_yaml_list(frontmatter, "metadata", "schema_expectations")
    expectations: list[dict] = []

    for item in raw_items:
        url = item.get("url", "").strip()
        method = item.get("method", "GET").strip().upper()
        # expected_keys are parsed as a sub-list, but our simple parser
        # puts them inline. We need to re-parse from frontmatter directly.
        expectations.append({
            "url": url,
            "method": method,
            "expected_keys": [],  # Will be filled by deeper parse
        })

    # Deeper parse for expected_keys (list items under each schema_expectations entry)
    expectations = _parse_schema_expectations_deep(frontmatter)
    return expectations


def _parse_schema_expectations_deep(frontmatter: str) -> list[dict]:
    """
    Deep-parse schema_expectations including expected_keys sub-lists.

    Args:
        frontmatter: The frontmatter text.

    Returns:
        List of expectation dicts with url, method, expected_keys.
    """
    lines = frontmatter.split("\n")
    expectations: list[dict] = []
    current: Optional[dict] = None
    in_metadata = False
    in_schema = False
    in_expected_keys = False

    for line in lines:
        stripped = line.strip()

        if not in_metadata:
            if stripped.startswith("metadata:"):
                in_metadata = True
            continue

        # Left metadata block?
        if line and line[0] != " " and line[0] != "\t" and stripped:
            break

        if not in_schema:
            if stripped.startswith("schema_expectations:"):
                in_schema = True
            continue

        # Detect new list item
        if stripped.startswith("- url:") or stripped.startswith("- method:"):
            if current is not None:
                expectations.append(current)
            in_expected_keys = False
            current = {"url": "", "method": "GET", "expected_keys": []}
            if stripped.startswith("- url:"):
                current["url"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("- method:"):
                current["method"] = stripped.split(":", 1)[1].strip().upper()
        elif current is not None:
            if stripped.startswith("url:"):
                current["url"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("method:"):
                current["method"] = stripped.split(":", 1)[1].strip().upper()
            elif stripped.startswith("expected_keys:"):
                in_expected_keys = True
            elif in_expected_keys and stripped.startswith("- "):
                current["expected_keys"].append(stripped[2:].strip())
            elif not stripped.startswith("-") and ":" in stripped:
                # Another key at the same level -- might be leaving schema block
                key = stripped.split(":")[0].strip()
                if key not in ("url", "method", "expected_keys"):
                    in_expected_keys = False

    if current is not None:
        expectations.append(current)

    return expectations


def _check_schema_drift(expectations: list[dict]) -> list[dict]:
    """
    GET each declared endpoint and compare top-level JSON keys against expected.

    Args:
        expectations: List of expectation dicts with url, method, expected_keys.

    Returns:
        List of issue dicts reporting drift status.
    """
    issues: list[dict] = []

    for exp in expectations:
        url = exp.get("url", "").strip()
        method = exp.get("method", "GET").upper()
        expected_keys = exp.get("expected_keys", [])

        if not url:
            continue

        if not url.startswith(("http://", "https://")):
            issues.append({
                "level": "warning",
                "message": f"Schema check skipped for non-HTTP URL: {url}",
                "detail": "Only HTTP/HTTPS URLs are supported.",
            })
            continue

        if not expected_keys:
            issues.append({
                "level": "info",
                "message": f"No expected_keys declared for {url}",
                "detail": "Skipping drift check.",
            })
            continue

        try:
            req = Request(url, method=method)
            req.add_header("User-Agent", "agent-skill-staleness-check/1.0")
            req.add_header("Accept", "application/json")
            with urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                data = json.loads(body)

                if not isinstance(data, dict):
                    issues.append({
                        "level": "warning",
                        "message": f"Response from {url} is not a JSON object",
                        "detail": f"Got {type(data).__name__}, expected dict. "
                                  "Cannot compare keys.",
                    })
                    continue

                actual_keys = set(data.keys())
                expected_set = set(expected_keys)

                missing = expected_set - actual_keys
                new_keys = actual_keys - expected_set

                if missing:
                    issues.append({
                        "level": "error",
                        "message": f"Schema drift: missing keys from {url}",
                        "detail": f"Expected keys not found: {sorted(missing)}. "
                                  "The API response structure may have changed.",
                    })

                if new_keys:
                    issues.append({
                        "level": "info",
                        "message": f"Schema drift: new keys in {url}",
                        "detail": f"Unexpected keys found: {sorted(new_keys)}. "
                                  "The API may have added new fields.",
                    })

                if not missing and not new_keys:
                    issues.append({
                        "level": "info",
                        "message": f"Schema matches for {url}",
                        "detail": f"All {len(expected_keys)} expected keys present, "
                                  "no unexpected keys.",
                    })

        except json.JSONDecodeError:
            issues.append({
                "level": "error",
                "message": f"Response from {url} is not valid JSON",
                "detail": "Cannot perform schema drift check.",
            })
        except URLError as exc:
            issues.append({
                "level": "error",
                "message": f"Cannot reach {url} for schema check",
                "detail": f"Error: {exc.reason}",
            })
        except Exception as exc:
            issues.append({
                "level": "error",
                "message": f"Schema check failed for {url}",
                "detail": f"Error: {exc}",
            })

    return issues


def staleness_check(
    skill_path: str,
    check_deps: bool = False,
    check_drift: bool = False,
) -> dict:
    """
    Main entry point for staleness detection.

    Args:
        skill_path: Path to the skill directory.
        check_deps: If True, HTTP-check declared dependencies.
        check_drift: If True, check for schema drift in declared endpoints.

    Returns:
        Dict with keys:
            - fresh (bool): True if no errors found.
            - review_status (str): "fresh", "due_soon", "overdue", or "unknown".
            - days_since_review (int or None): Days since last review.
            - date_source (str): Where the reference date came from.
            - issues (list[dict]): All issues found.
    """
    all_issues: list[dict] = []

    skill_dir = Path(skill_path).resolve()

    # --- Check: directory exists ---
    if not skill_dir.exists():
        return {
            "fresh": False,
            "review_status": "unknown",
            "days_since_review": None,
            "date_source": "none",
            "issues": [{"level": "error", "message": f"Path does not exist: {skill_dir}", "detail": ""}],
        }

    if not skill_dir.is_dir():
        return {
            "fresh": False,
            "review_status": "unknown",
            "days_since_review": None,
            "date_source": "none",
            "issues": [{"level": "error", "message": f"Path is not a directory: {skill_dir}", "detail": ""}],
        }

    # --- Read SKILL.md ---
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return {
            "fresh": False,
            "review_status": "unknown",
            "days_since_review": None,
            "date_source": "none",
            "issues": [{"level": "error", "message": "SKILL.md not found", "detail": ""}],
        }

    try:
        content = skill_md.read_text(encoding="utf-8")
    except Exception as exc:
        return {
            "fresh": False,
            "review_status": "unknown",
            "days_since_review": None,
            "date_source": "none",
            "issues": [{"level": "error", "message": f"Could not read SKILL.md: {exc}", "detail": ""}],
        }

    frontmatter, _ = _parse_frontmatter(content)
    if frontmatter is None:
        return {
            "fresh": False,
            "review_status": "unknown",
            "days_since_review": None,
            "date_source": "none",
            "issues": [{"level": "error", "message": "No valid frontmatter found", "detail": ""}],
        }

    # --- Phase 1: Review staleness ---
    git_date = _get_git_last_modified(skill_path)
    review_issues, review_status, days_since, date_source = _check_review_staleness(
        frontmatter, git_date
    )
    all_issues.extend(review_issues)

    # --- Phase 2: Dependency health ---
    if check_deps:
        deps = _parse_yaml_list(frontmatter, "metadata", "dependencies")
        if deps:
            dep_issues = _check_dependency_health(deps)
            all_issues.extend(dep_issues)
        else:
            all_issues.append({
                "level": "info",
                "message": "No dependencies declared",
                "detail": "Add metadata.dependencies to enable health checks.",
            })

    # --- Phase 3: Schema drift ---
    if check_drift:
        expectations = _parse_schema_expectations(frontmatter)
        if expectations:
            drift_issues = _check_schema_drift(expectations)
            all_issues.extend(drift_issues)
        else:
            all_issues.append({
                "level": "info",
                "message": "No schema expectations declared",
                "detail": "Add metadata.schema_expectations to enable drift detection.",
            })

    # Determine overall freshness
    has_errors = any(i["level"] == "error" for i in all_issues)
    fresh = not has_errors

    return {
        "fresh": fresh,
        "review_status": review_status,
        "days_since_review": days_since,
        "date_source": date_source,
        "issues": all_issues,
    }


def _print_human_readable(result: dict, skill_path: str) -> None:
    """Print staleness check results in a human-readable format."""
    print(f"Staleness check: {skill_path}")
    print(f"{'=' * 60}")

    status_label = result["review_status"].upper().replace("_", " ")
    print(f"Review status: {status_label}")

    if result["days_since_review"] is not None:
        print(f"Days since review: {result['days_since_review']} (source: {result['date_source']})")

    if result["fresh"]:
        print("Overall: FRESH")
    else:
        print("Overall: STALE / DEGRADED")

    if result["issues"]:
        errors = [i for i in result["issues"] if i["level"] == "error"]
        warnings = [i for i in result["issues"] if i["level"] == "warning"]
        infos = [i for i in result["issues"] if i["level"] == "info"]

        if errors:
            print(f"\nErrors ({len(errors)}):")
            for issue in errors:
                print(f"  [ERROR] {issue['message']}")
                if issue["detail"]:
                    print(f"          {issue['detail']}")

        if warnings:
            print(f"\nWarnings ({len(warnings)}):")
            for issue in warnings:
                print(f"  [WARN]  {issue['message']}")
                if issue["detail"]:
                    print(f"          {issue['detail']}")

        if infos:
            print(f"\nInfo ({len(infos)}):")
            for issue in infos:
                print(f"  [INFO]  {issue['message']}")
                if issue["detail"]:
                    print(f"          {issue['detail']}")

    print(f"{'=' * 60}")


def main() -> None:
    """CLI entry point for the staleness checker."""
    if len(sys.argv) < 2:
        print(
            "Usage: python3 scripts/staleness_check.py <skill-path> [--json] [--check-deps] [--check-drift]\n"
            "\n"
            "Arguments:\n"
            "  skill-path      Path to the skill directory to check\n"
            "\n"
            "Options:\n"
            "  --json           Output results as JSON to stdout\n"
            "  --check-deps     HTTP-check declared dependency URLs\n"
            "  --check-drift    Detect schema drift in declared API endpoints\n"
            "\n"
            "Exit codes:\n"
            "  0  Fresh (no staleness issues)\n"
            "  1  Stale (overdue for review)\n"
            "  2  Degraded (dependency failures or schema drift)\n",
            file=sys.stderr,
        )
        sys.exit(1)

    skill_path = sys.argv[1]
    use_json = "--json" in sys.argv
    check_deps = "--check-deps" in sys.argv
    check_drift = "--check-drift" in sys.argv

    result = staleness_check(skill_path, check_deps=check_deps, check_drift=check_drift)

    if use_json:
        print(json.dumps(result, indent=2))
    else:
        _print_human_readable(result, skill_path)

    # Exit codes: 0=fresh, 1=stale, 2=degraded
    if result["review_status"] == "overdue":
        sys.exit(1)

    has_dep_or_drift_errors = any(
        i["level"] == "error" and "review" not in i["message"].lower()
        for i in result["issues"]
    )
    if has_dep_or_drift_errors:
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
