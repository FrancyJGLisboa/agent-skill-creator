"""staleness_check --record: stale/degraded runs leave raw evidence in EVOLUTION.md."""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from staleness_check import record_stale, staleness_check  # noqa: E402


class RecordStaleTest(unittest.TestCase):
    def test_overdue_skill_records_raw_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "old-skill"
            skill.mkdir()
            (skill / "SKILL.md").write_text(
                "---\nname: old-skill\ndescription: x\nmetadata:\n"
                "  last_reviewed: 2020-01-01\n  review_interval_days: 30\n---\n# x\n",
                encoding="utf-8",
            )
            result = staleness_check(str(skill))
            self.assertEqual(result["review_status"], "overdue")

            record_stale(skill, result)
            text = (skill / "EVOLUTION.md").read_text(encoding="utf-8")
            self.assertIn("OVERDUE", text)
            self.assertIn("```json", text)  # raw findings embedded


if __name__ == "__main__":
    unittest.main()
