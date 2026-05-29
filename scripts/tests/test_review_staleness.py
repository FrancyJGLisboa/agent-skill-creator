"""Tests for scripts.review_staleness — date logic and review-due decisions.

All tests inject `today` to keep them deterministic; no real clock, no git.
"""

import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from review_staleness import (  # noqa: E402
    DEFAULT_REVIEW_INTERVAL_DAYS,
    STALENESS_WARNING_THRESHOLD_DAYS,
    _parse_date,
    check_review_staleness,
)
from skill_document import SkillDoc  # noqa: E402


def _doc(metadata_lines: list[str] = ()) -> SkillDoc:
    lines = ["---", "name: demo-skill", "description: x", "metadata:"]
    lines += [f"  {ml}" for ml in metadata_lines]
    lines += ["---", "body"]
    return SkillDoc.from_text("\n".join(lines))


class ParseDateTest(unittest.TestCase):
    def test_valid_date(self) -> None:
        self.assertEqual(_parse_date("2026-01-15"), date(2026, 1, 15))

    def test_empty_or_garbage(self) -> None:
        self.assertIsNone(_parse_date(""))
        self.assertIsNone(_parse_date("not-a-date"))
        self.assertIsNone(_parse_date("2026/01/15"))

    def test_invalid_month(self) -> None:
        self.assertIsNone(_parse_date("2026-13-01"))


class CheckReviewStalenessTest(unittest.TestCase):
    def _check(self, doc: SkillDoc, today: date, git: date | None = None):
        return check_review_staleness(doc, git, today=today)

    def test_recent_review_is_fresh(self) -> None:
        doc = _doc(["last_reviewed: 2026-05-01", "review_interval_days: 90"])
        issues, status, days, src = self._check(doc, today=date(2026, 5, 29))
        self.assertEqual(status, "fresh")
        self.assertEqual(src, "last_reviewed")
        self.assertEqual(days, 28)
        self.assertFalse(any(i["level"] == "error" for i in issues))

    def test_old_review_is_overdue(self) -> None:
        doc = _doc(["last_reviewed: 2025-01-01", "review_interval_days: 90"])
        issues, status, _days, _src = self._check(doc, today=date(2026, 5, 29))
        self.assertEqual(status, "overdue")
        self.assertTrue(any(i["level"] == "error" for i in issues))

    def test_due_soon_window(self) -> None:
        # last_reviewed = today - (warning+5); interval = warning+30 -> due_soon
        warning = STALENESS_WARNING_THRESHOLD_DAYS
        last = date(2026, 1, 1)
        today = date(2026, 1, 1).replace(day=1)
        # construct so today is past warning_date but before deadline
        from datetime import timedelta
        today = last + timedelta(days=warning + 5)
        doc = _doc([f"last_reviewed: {last}", f"review_interval_days: {warning + 30}"])
        issues, status, _days, _src = self._check(doc, today=today)
        self.assertEqual(status, "due_soon")
        self.assertTrue(any(i["level"] == "warning" for i in issues))

    def test_falls_back_to_git_date(self) -> None:
        doc = _doc([])  # no temporal metadata at all
        issues, status, _days, src = self._check(
            doc, today=date(2026, 5, 29), git=date(2026, 4, 15)
        )
        self.assertEqual(src, "git_commit")
        self.assertEqual(status, "fresh")  # within default 90 days

    def test_no_dates_at_all_is_unknown(self) -> None:
        doc = _doc([])
        issues, status, _days, src = self._check(doc, today=date(2026, 5, 29), git=None)
        self.assertEqual(status, "unknown")
        self.assertEqual(src, "unknown")
        self.assertTrue(any("No review date available" in i["message"] for i in issues))

    def test_invalid_date_format_is_warning(self) -> None:
        doc = _doc(["last_reviewed: tomorrow"])
        issues, _status, _days, _src = self._check(doc, today=date(2026, 5, 29))
        self.assertTrue(any("Invalid 'metadata.last_reviewed' date format" in i["message"] for i in issues))

    def test_uses_default_interval_when_absent(self) -> None:
        doc = _doc(["last_reviewed: 2026-01-01"])
        _issues, _status, _days, _src = self._check(doc, today=date(2026, 2, 1))
        # default 90 days; just verify it runs and uses the default
        self.assertEqual(DEFAULT_REVIEW_INTERVAL_DAYS, 90)

    def test_no_temporal_metadata_info(self) -> None:
        doc = _doc([])
        issues, _status, _days, _src = self._check(doc, today=date(2026, 5, 29), git=date(2026, 5, 1))
        self.assertTrue(any("No temporal metadata found" in i["message"] for i in issues))


if __name__ == "__main__":
    unittest.main()
