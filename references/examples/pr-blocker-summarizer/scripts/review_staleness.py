#!/usr/bin/env python3
"""
Review staleness check for a skill.

Compares `metadata.last_reviewed` against `metadata.review_interval_days`. Falls
back to the git commit date for SKILL.md when explicit review dates are absent.
No network. Pure date math + a single git subprocess call.
"""

from __future__ import annotations

import re
import subprocess
from datetime import date, timedelta
from pathlib import Path

from skill_document import SkillDoc

DEFAULT_REVIEW_INTERVAL_DAYS = 90
STALENESS_WARNING_THRESHOLD_DAYS = 60

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _parse_date(value: str) -> date | None:
    """Parse a YYYY-MM-DD string into a date object, or None on failure."""
    if not value or not _DATE_RE.match(value.strip()):
        return None
    try:
        y, m, d = value.strip().split("-")
        return date(int(y), int(m), int(d))
    except (ValueError, IndexError):
        return None


def get_git_last_modified(skill_path: str) -> date | None:
    """Return the date of the last git commit touching SKILL.md, or None if
    git is unavailable, the file is untracked, or the call times out."""
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
        return _parse_date(result.stdout.strip()[:10])  # ISO "YYYY-MM-DDTHH:..." -> "YYYY-MM-DD"
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def check_review_staleness(
    doc: SkillDoc,
    git_last_modified: date | None,
    today: date | None = None,
) -> tuple[list[dict], str, int | None, str]:
    """
    Decide whether the skill is overdue for review.

    `today` is injectable for tests. Returns (issues, review_status,
    days_since_review, date_source). review_status is one of "fresh",
    "due_soon", "overdue", or "unknown".
    """
    if today is None:
        today = date.today()
    issues: list[dict] = []

    created_str = doc.subfield("metadata", "created")
    last_reviewed_str = doc.subfield("metadata", "last_reviewed")
    interval_str = doc.subfield("metadata", "review_interval_days")

    # Validate formats (warnings only)
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

    interval_days = DEFAULT_REVIEW_INTERVAL_DAYS
    if interval_str:
        try:
            interval_days = int(interval_str)
        except ValueError:
            pass

    reference_date: date | None = None
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

    days_since: int | None = None
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

    has_any_temporal = bool(created_str or last_reviewed_str or interval_str)
    if not has_any_temporal:
        issues.append({
            "level": "info",
            "message": "No temporal metadata found",
            "detail": "Consider adding metadata.created, metadata.last_reviewed, "
                      "and metadata.review_interval_days to frontmatter.",
        })

    return issues, review_status, days_since, date_source
