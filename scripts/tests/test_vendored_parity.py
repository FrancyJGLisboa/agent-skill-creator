"""Vendored maintenance scripts in bundled examples must match their templates.

Every generated skill ships copies of the shared maintenance scripts. The
bundled examples vendor the same copies; nothing else keeps them in sync with
scripts/ when a template changes. This test is that guard: a template edit
that skips the vendored copies fails here instead of shipping drift.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
SCRIPTS = ROOT / "scripts"
EXAMPLES = ROOT / "references" / "examples"

# template filename in scripts/ -> vendored filename in each example's scripts/
VENDORED = {
    "skill_document.py": "skill_document.py",
    "review_staleness.py": "review_staleness.py",
    "dependency_health.py": "dependency_health.py",
    "schema_drift.py": "schema_drift.py",
    "staleness_check.py": "staleness_check.py",
    "run_evals_template.py": "run_evals.py",
    "evolve_template.py": "evolve.py",
}


class VendoredParityTest(unittest.TestCase):
    def test_examples_match_templates(self) -> None:
        examples = sorted(p for p in EXAMPLES.iterdir() if (p / "SKILL.md").exists())
        self.assertTrue(examples, "no bundled examples found")
        for example in examples:
            for template_name, vendored_name in VENDORED.items():
                vendored = example / "scripts" / vendored_name
                if not vendored.exists():
                    continue  # not every example vendors every script
                with self.subTest(example=example.name, script=vendored_name):
                    template = (SCRIPTS / template_name).read_bytes()
                    self.assertEqual(
                        template,
                        vendored.read_bytes(),
                        f"{vendored.relative_to(ROOT)} drifted from "
                        f"scripts/{template_name}; re-copy the template",
                    )


if __name__ == "__main__":
    sys.exit(unittest.main())
