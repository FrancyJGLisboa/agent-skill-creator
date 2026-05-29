#!/usr/bin/env python3
"""
Staleness CLI for an agent skill.

Thin orchestrator: reads SKILL.md, runs the three peer modules
(review_staleness, dependency_health, schema_drift), aggregates issues, and
prints / exits. Each concern lives in its own module so it is testable in
isolation and reusable elsewhere.

Usage:
    python3 scripts/staleness_check.py <skill-path> [--json] [--check-deps] [--check-drift]

Exit codes:
    0 - Fresh (no staleness issues)
    1 - Stale (overdue for review)
    2 - Degraded (dependency failures or schema drift)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from skill_document import SkillDoc  # noqa: E402
from review_staleness import (  # noqa: E402
    DEFAULT_REVIEW_INTERVAL_DAYS,
    check_review_staleness,
    get_git_last_modified,
)
from dependency_health import check_dependency_health  # noqa: E402
from schema_drift import check_schema_drift, parse_schema_expectations  # noqa: E402

# Re-exported for back-compat (skill_registry historically imported from here).
__all__ = ["DEFAULT_REVIEW_INTERVAL_DAYS", "staleness_check", "main"]


def staleness_check(
    skill_path: str,
    check_deps: bool = False,
    check_drift: bool = False,
) -> dict:
    """Run the staleness checks against the skill at `skill_path`.

    Returns a result dict with keys: fresh (bool), review_status (str),
    days_since_review (int|None), date_source (str), issues (list[dict]).
    """
    all_issues: list[dict] = []
    skill_dir = Path(skill_path).resolve()

    if not skill_dir.exists():
        return _err(f"Path does not exist: {skill_dir}")
    if not skill_dir.is_dir():
        return _err(f"Path is not a directory: {skill_dir}")

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return _err("SKILL.md not found")

    try:
        content = skill_md.read_text(encoding="utf-8")
    except Exception as exc:
        return _err(f"Could not read SKILL.md: {exc}")

    doc = SkillDoc.from_text(content)
    if doc.frontmatter is None:
        return _err("No valid frontmatter found")

    # Phase 1: review staleness
    git_date = get_git_last_modified(skill_path)
    review_issues, review_status, days_since, date_source = check_review_staleness(doc, git_date)
    all_issues.extend(review_issues)

    # Phase 2: dependency health
    if check_deps:
        deps = doc.list_of_objects("metadata", "dependencies")
        if deps:
            all_issues.extend(check_dependency_health(deps))
        else:
            all_issues.append({
                "level": "info",
                "message": "No dependencies declared",
                "detail": "Add metadata.dependencies to enable health checks.",
            })

    # Phase 3: schema drift
    if check_drift:
        expectations = parse_schema_expectations(doc)
        if expectations:
            all_issues.extend(check_schema_drift(expectations))
        else:
            all_issues.append({
                "level": "info",
                "message": "No schema expectations declared",
                "detail": "Add metadata.schema_expectations to enable drift detection.",
            })

    has_errors = any(i["level"] == "error" for i in all_issues)
    return {
        "fresh": not has_errors,
        "review_status": review_status,
        "days_since_review": days_since,
        "date_source": date_source,
        "issues": all_issues,
    }


def _err(message: str) -> dict:
    return {
        "fresh": False,
        "review_status": "unknown",
        "days_since_review": None,
        "date_source": "none",
        "issues": [{"level": "error", "message": message, "detail": ""}],
    }


def _print_human_readable(result: dict, skill_path: str) -> None:
    print(f"Staleness check: {skill_path}")
    print(f"{'=' * 60}")

    status_label = result["review_status"].upper().replace("_", " ")
    print(f"Review status: {status_label}")
    if result["days_since_review"] is not None:
        print(f"Days since review: {result['days_since_review']} (source: {result['date_source']})")
    print("Overall: FRESH" if result["fresh"] else "Overall: STALE / DEGRADED")

    if result["issues"]:
        for level, label in (("error", "[ERROR]"), ("warning", "[WARN] "), ("info", "[INFO] ")):
            bucket = [i for i in result["issues"] if i["level"] == level]
            if bucket:
                print(f"\n{level.capitalize()} ({len(bucket)}):")
                for issue in bucket:
                    print(f"  {label} {issue['message']}")
                    if issue["detail"]:
                        print(f"          {issue['detail']}")

    print(f"{'=' * 60}")


def main() -> None:
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
