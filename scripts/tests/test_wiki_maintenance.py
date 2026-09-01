"""Behavioral tests for the persistent non-runtime knowledge layer."""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parent.parent.parent
TEMPLATE = ROOT / "scripts" / "wiki_maintenance_template.py"


class WikiMaintenanceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.skill = Path(self.tmp.name) / "demo-skill"
        (self.skill / "scripts").mkdir(parents=True)
        (self.skill / "SKILL.md").write_text("---\nname: demo-skill\ndescription: Demo.\n---\n", encoding="utf-8")
        shutil.copy(TEMPLATE, self.skill / "scripts" / "wiki_maintenance.py")
        self.evidence = Path(self.tmp.name) / "failure.json"
        self.evidence.write_text('{"result":"failed"}\n', encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def run_tool(self, *args):
        return subprocess.run(
            [sys.executable, "scripts/wiki_maintenance.py", *args], cwd=self.skill,
            capture_output=True, text=True, timeout=30,
        )

    def test_evidence_pattern_and_rejected_decision_are_linked_and_valid(self):
        init = self.run_tool("init")
        self.assertEqual(init.returncode, 0, init.stderr)
        captured = self.run_tool("capture", "--source", str(self.evidence), "--classification", "internal")
        self.assertEqual(captured.returncode, 0, captured.stderr)
        raw = captured.stdout.strip().removeprefix("wiki: captured ")
        pattern = self.run_tool(
            "add-pattern", "--id", "missing-header", "--title", "Missing request header",
            "--finding", "Requests fail when the account header is omitted.", "--evidence", raw,
        )
        self.assertEqual(pattern.returncode, 0, pattern.stderr)
        impact = self.run_tool(
            "record-impact", "--proposal-id", "add-account-header", "--target", "SKILL.md",
            "--validation-score", "0.4", "--decision", "rejected",
            "--evidence", "wiki/patterns/missing-header.md",
        )
        self.assertEqual(impact.returncode, 0, impact.stderr)
        valid = self.run_tool("validate")
        self.assertEqual(valid.returncode, 0, valid.stderr)
        self.assertIn("rejected", (self.skill / "wiki" / "skill-impact.md").read_text(encoding="utf-8"))
        self.assertNotIn("Missing request header", (self.skill / "SKILL.md").read_text(encoding="utf-8"))

    def test_pattern_rejects_evidence_outside_raw_layer(self):
        self.run_tool("init")
        proc = self.run_tool(
            "add-pattern", "--id", "bad-proof", "--title", "Bad proof", "--finding", "No.",
            "--evidence", "SKILL.md",
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("raw/", proc.stderr)
