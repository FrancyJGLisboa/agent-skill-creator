"""v4 regression suite.

Confirms that v4 skill files still parse cleanly under the v6 validator
and that the v6 artifact detector does not crash when given v4-era
workflow descriptions.

This is not a behavioral regression test (no LLM invocation). It is a
structural regression test that catches accidental schema breaks or
detector crashes against the 180+ community forks already running v4
skills.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from artifact_detector import detect_artifact  # noqa: E402
from validate import validate_skill  # noqa: E402

FIXTURES_PATH = ROOT / "scripts" / "tests" / "fixtures" / "v4_skills_regression.json"

# Templates the detector is allowed to return. None means "no artifact" —
# expected for v4 workflow-style skills with no visual output.
ALLOWED_TEMPLATES = {"line-chart", "bar-chart", "kpi-cards", "data-table", None}


class V4RegressionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skills = json.loads(FIXTURES_PATH.read_text())

    def test_validator_accepts_existing_v4_skills(self) -> None:
        """validate_skill must return valid=True for every real v4 skill.

        The validator returns a dict ``{valid: bool, errors: list, warnings: list}``.
        Warnings (missing -skill suffix, missing license, missing AGENTS.md, etc.)
        do NOT break v4 skills — only ``errors`` would.
        """
        failures: list[str] = []
        real_skills_tested = 0

        for skill in self.skills:
            if skill.get("synthetic"):
                continue
            path = skill.get("path")
            if not path:
                continue

            skill_dir = ROOT / Path(path).parent
            if not skill_dir.exists():
                failures.append(f"{skill['id']}: missing path {skill_dir}")
                continue

            real_skills_tested += 1
            try:
                result = validate_skill(str(skill_dir))
            except Exception as exc:  # noqa: BLE001
                failures.append(f"{skill['id']}: validator raised: {exc!r}")
                continue

            if not isinstance(result, dict):
                failures.append(
                    f"{skill['id']}: validator returned non-dict ({type(result).__name__})"
                )
                continue

            if not result.get("valid", False):
                failures.append(
                    f"{skill['id']}: validate_skill returned valid=False; "
                    f"errors={result.get('errors')}"
                )

        self.assertEqual(
            failures, [],
            "Existing v4 skills must still validate under the v6 validator:\n"
            + "\n".join(failures),
        )
        self.assertGreater(
            real_skills_tested, 0,
            "Regression suite must exercise at least one real v4 skill on disk",
        )

    def test_detector_does_not_crash_on_v4_descriptions(self) -> None:
        """detect_artifact must handle every v4 workflow description without crashing.

        It is acceptable for the detector to return None (no artifact) — most
        v4 skills are workflow-style with no visual output. What is NOT
        acceptable is an exception, which would break the v6 Phase 2 pipeline
        for users upgrading existing v4 forks.
        """
        for skill in self.skills:
            description = skill["description"]
            try:
                result = detect_artifact(description)
            except Exception as exc:  # noqa: BLE001
                self.fail(f"detector crashed on {skill['id']!r}: {exc!r}")

            self.assertIn(
                result, ALLOWED_TEMPLATES,
                f"{skill['id']}: detector returned unexpected value {result!r}",
            )


if __name__ == "__main__":
    unittest.main()
