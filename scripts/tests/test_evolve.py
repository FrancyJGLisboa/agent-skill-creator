"""End-to-end test of the shipped evolve loop (scripts/evolve.py in each skill)."""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
EXAMPLE = ROOT / "references" / "examples" / "weekly-crm-report"


class EvolveLoopTest(unittest.TestCase):
    def test_healthy_skill_evolves_green(self):
        proc = subprocess.run(
            [sys.executable, "scripts/evolve.py"],
            cwd=EXAMPLE, capture_output=True, text=True, timeout=300,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("fresh and green", proc.stdout)

    def test_broken_skill_fails_and_records_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "weekly-crm-report"
            shutil.copytree(EXAMPLE, skill)
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
