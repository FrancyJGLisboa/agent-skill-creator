"""End-to-end test of the shipped evolve loop (scripts/evolve.py in each skill)."""

import json
import os
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


def _ledger_env(skill: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["ASC_SUCCESS_LEDGER"] = str(skill / "success-events.jsonl")
    return env


class EvolveLoopTest(unittest.TestCase):
    def test_healthy_skill_evolves_green(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = _hermetic_copy(Path(tmp))
            proc = subprocess.run(
                [sys.executable, "scripts/evolve.py"],
                cwd=skill, capture_output=True, text=True, timeout=300,
                env=_ledger_env(skill),
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
                env=_ledger_env(skill),
            )
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            evolution = skill / "EVOLUTION.md"
            self.assertTrue(evolution.exists(), "no evidence recorded")
            self.assertIn("```json", evolution.read_text(encoding="utf-8"))


class CorrectionCaptureTest(unittest.TestCase):
    """`--correct` is the only path by which knowledge no check can derive gets in."""

    CORRECTION = "the West region files late, so Friday exports are short"

    def _skill(self, tmp: Path, body: str) -> Path:
        skill = tmp / "demo"
        (skill / "scripts").mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            f"---\nname: demo\ndescription: Demo.\n---\n# /demo\n\n{body}\n",
            encoding="utf-8",
        )
        shutil.copy(ROOT / "scripts" / "evolve_template.py", skill / "scripts" / "evolve.py")
        shutil.copy(ROOT / "scripts" / "success_ledger.py", skill / "scripts" / "success_ledger.py")
        return skill

    def _run(self, skill: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "scripts/evolve.py", *args],
            cwd=skill, capture_output=True, text=True, timeout=60,
            env=_ledger_env(skill),
        )

    def _gotchas(self, skill: Path) -> str:
        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        return text[text.index("## Gotchas"):]

    def test_replaces_none_known_placeholder(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self._skill(Path(tmp), "## Gotchas\n\nNone known.\n\n## Keywords\n\nfoo")
            proc = self._run(skill, "--correct", self.CORRECTION)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(
                self._gotchas(skill),
                f"## Gotchas\n\n- {self.CORRECTION}\n\n## Keywords\n\nfoo\n",
            )

    def test_appends_below_existing_gotchas(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self._skill(Path(tmp), "## Gotchas\n\n- Already known.\n\n## Keywords\n\nfoo")
            self._run(skill, "--correct", self.CORRECTION)
            self.assertEqual(
                self._gotchas(skill),
                f"## Gotchas\n\n- Already known.\n- {self.CORRECTION}\n\n## Keywords\n\nfoo\n",
            )

    def test_creates_the_section_when_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self._skill(Path(tmp), "Body.\n\n## Keywords\n\nfoo")
            self._run(skill, "--correct", self.CORRECTION)
            self.assertEqual(
                self._gotchas(skill),
                f"## Gotchas\n\n- {self.CORRECTION}\n\n## Keywords\n\nfoo\n",
            )

    def test_creates_the_section_with_no_anchor_to_precede(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self._skill(Path(tmp), "Body only.")
            self._run(skill, "--correct", self.CORRECTION)
            self.assertEqual(self._gotchas(skill), f"## Gotchas\n\n- {self.CORRECTION}\n\n")

    def test_records_verbatim_evidence_in_evolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self._skill(Path(tmp), "## Gotchas\n\nNone known.")
            self._run(skill, "--correct", self.CORRECTION)
            log = (skill / "EVOLUTION.md").read_text(encoding="utf-8")
            self.assertIn("correction from use", log)
            self.assertIn(f"> {self.CORRECTION}", log)
            event = json.loads((skill / "success-events.jsonl").read_text(encoding="utf-8"))
            self.assertEqual(event["event"], "correction_recorded")

    def test_creates_a_versioned_edit_and_executable_regression(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self._skill(Path(tmp), "## Gotchas\n\nNone known.")
            self._run(skill, "--correct", self.CORRECTION)
            log = (skill / "EVOLUTION.md").read_text(encoding="utf-8")
            records = list((skill / "evals" / "corrections").glob("*.json"))
            self.assertEqual(len(records), 1)
            record = json.loads(records[0].read_text(encoding="utf-8"))
            self.assertEqual(record["correction"], self.CORRECTION)
            self.assertEqual(record["proposed_skill_edit"]["section"], "Gotchas")
            self.assertEqual(record["regression_test"]["must_contain"], self.CORRECTION)
            self.assertEqual(record["version"]["recommended_bump"], "patch")
            self.assertIn(f"Change ID: `{record['id']}`", log)
            self.assertIn("Version recommendation: patch", log)

    def test_repeated_corrections_all_survive(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self._skill(Path(tmp), "## Gotchas\n\nNone known.\n\n## Keywords\n\nfoo")
            self._run(skill, "--correct", "first thing")
            self._run(skill, "--correct", "second thing")
            gotchas = self._gotchas(skill)
            self.assertIn("- first thing", gotchas)
            self.assertIn("- second thing", gotchas)
            self.assertEqual((skill / "EVOLUTION.md").read_text().count("correction from use"), 2)

    def test_blank_correction_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self._skill(Path(tmp), "## Gotchas\n\nNone known.")
            proc = self._run(skill, "--correct", "   ")
            self.assertEqual(proc.returncode, 2)
            self.assertNotIn("- ", self._gotchas(skill))
            self.assertFalse((skill / "EVOLUTION.md").exists())

    def test_does_not_run_the_verification_steps(self):
        """--correct is a capture command; it must not trigger evals or staleness."""
        with tempfile.TemporaryDirectory() as tmp:
            skill = self._skill(Path(tmp), "## Gotchas\n\nNone known.")
            proc = self._run(skill, "--correct", self.CORRECTION)
            self.assertNotIn("== evolve:", proc.stdout)


if __name__ == "__main__":
    unittest.main()
