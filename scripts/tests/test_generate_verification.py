import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from generate_verification import ensure_readme_link, render_report, verification_errors  # noqa: E402


class VerificationReportTest(unittest.TestCase):
    def test_report_shows_real_counts_and_limits_its_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "demo-skill"
            skill.mkdir()
            (skill / "SKILL.md").write_text("---\nname: demo-skill\nmetadata:\n  version: 1.0.0\n---\n", encoding="utf-8")
            report = render_report(
                skill,
                {"specification": True, "security": True, "skill graph": True},
                {"passed": 6, "failed": 0, "errors": 0, "regressions": 0, "clean": True},
                "live",
                ["codex"],
            )
        self.assertIn("Run type: live", report)
        self.assertIn("Recorded execution environments: codex", report)
        self.assertIn("6 passed, 0 failed, 0 errored, 0 regressed", report)
        self.assertIn("Cross-environment compatibility: not established by this report", report)
        self.assertIn("does not prove", report)

    def test_readme_gains_one_verification_link(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "demo-skill"
            skill.mkdir()
            readme = skill / "README.md"
            readme.write_text("# Demo\n", encoding="utf-8")
            self.assertTrue(ensure_readme_link(skill))
            self.assertFalse(ensure_readme_link(skill))
            self.assertEqual(readme.read_text(encoding="utf-8").count("[VERIFICATION.md](VERIFICATION.md)"), 1)

    def test_verification_becomes_stale_when_a_script_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "demo-skill"
            (skill / "scripts").mkdir(parents=True)
            (skill / "SKILL.md").write_text("---\nname: demo-skill\nmetadata:\n  version: 1.0.0\n---\n", encoding="utf-8")
            script = skill / "scripts" / "run.py"
            script.write_text("print('one')\n", encoding="utf-8")
            report = render_report(skill, {"specification": True}, {"passed": 1, "failed": 0, "errors": 0, "regressions": 0, "clean": True}, "representative", [])
            (skill / "VERIFICATION.md").write_text(report, encoding="utf-8")
            self.assertEqual(verification_errors(skill), [])
            script.write_text("print('two')\n", encoding="utf-8")
            self.assertIn("verification is stale: SKILL.md, scripts, or evals changed", verification_errors(skill))
