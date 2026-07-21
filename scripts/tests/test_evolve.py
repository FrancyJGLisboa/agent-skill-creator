"""End-to-end test of the shipped evolve loop (scripts/evolve.py in each skill)."""

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
EXAMPLE = ROOT / "references" / "examples" / "weekly-crm-report"


def _hermetic_copy(tmp: Path) -> Path:
    """Copy the example to tmp and pin last_reviewed to today.

    Keeps the test deterministic (the in-repo date would eventually cross the
    review interval and turn this green path red on a fixed calendar day) and
    keeps evolve's --record step from writing EVOLUTION.md into the repo tree.
    """
    skill = tmp / "weekly-crm-report"
    shutil.copytree(EXAMPLE, skill)
    skill_md = skill / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    text, n = re.subn(
        r"^(  last_reviewed: )\S+$",
        rf"\g<1>{date.today().isoformat()}",
        text,
        flags=re.MULTILINE,
    )
    assert n == 1, "expected exactly one last_reviewed line in example SKILL.md"
    skill_md.write_text(text, encoding="utf-8")
    return skill


class EvolveLoopTest(unittest.TestCase):
    def test_healthy_skill_evolves_green(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = _hermetic_copy(Path(tmp))
            proc = subprocess.run(
                [sys.executable, "scripts/evolve.py"],
                cwd=skill, capture_output=True, text=True, timeout=300,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("fresh and green", proc.stdout)

    def test_broken_skill_fails_and_records_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Hermetic copy so the recorded failure is the eval gate below, not
            # a calendar-dependent staleness finding.
            skill = _hermetic_copy(Path(tmp))
            # Break the pipeline: output passes shape checks but diverges from
            # the promoted baseline (the failure mode only the gate can see).
            pipeline = skill / "scripts" / "run_pipeline.py"
            pipeline.write_text(
                "import argparse, pathlib\n"
                "ap = argparse.ArgumentParser()\n"
                "ap.add_argument('--input'); ap.add_argument('--output', required=True)\n"
                "a, _ = ap.parse_known_args()\n"
                "pathlib.Path(a.output).write_text('{\"regions\": [], \"grand_total\": 0}')\n",
                encoding="utf-8",
            )
            proc = subprocess.run(
                [sys.executable, "scripts/evolve.py"],
                cwd=skill, capture_output=True, text=True, timeout=300,
            )
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            evolution = skill / "EVOLUTION.md"
            self.assertTrue(evolution.exists(), "no evidence recorded")
            self.assertIn("```json", evolution.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
