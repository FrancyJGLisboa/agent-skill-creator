"""Tests for scripts.validate.

Focused on the `## Gotchas` body check: a generated skill must carry the
environment-specific facts that defy reasonable assumptions, but a missing
section is a warning rather than an error -- it should not block delivery of an
otherwise-working skill.
"""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from validate import validate_skill  # noqa: E402

GOTCHAS_HINT = "'## Gotchas' section"


def write_skill(base: Path, name: str, body: str) -> Path:
    """Create a minimal spec-valid skill whose body is exactly ``body``."""
    skill = base / name
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        f"""---
name: {name}
description: >-
  Demo skill {name} used by validate tests. Activates when a test needs a
  spec-valid skill directory on disk.
license: MIT
metadata:
  author: tester
  version: 1.0.0
---
# /{name}

{body}
""",
        encoding="utf-8",
    )
    return skill


def gotchas_warnings(result: dict) -> list[str]:
    return [w for w in result["warnings"] if GOTCHAS_HINT in w]


class TestGotchasCheck(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_missing_gotchas_warns_once_and_stays_valid(self):
        skill = write_skill(self.base, "no-gotchas-skill", "Body with no gotchas.")
        result = validate_skill(str(skill))

        self.assertEqual(len(gotchas_warnings(result)), 1)
        # Warning only: a missing section must not fail the skill.
        self.assertTrue(result["valid"])
        self.assertEqual(result["errors"], [])

    def test_gotchas_section_clears_the_warning(self):
        skill = write_skill(
            self.base,
            "has-gotchas-skill",
            "## Gotchas\n\n- The `/summary` endpoint returns 200 with an empty body.",
        )
        result = validate_skill(str(skill))

        self.assertEqual(gotchas_warnings(result), [])
        self.assertTrue(result["valid"])

    def test_none_known_is_accepted(self):
        """`None known` is an honest answer; inventing gotchas is the failure mode."""
        skill = write_skill(self.base, "none-known-skill", "## Gotchas\n\nNone known.")
        result = validate_skill(str(skill))

        self.assertEqual(gotchas_warnings(result), [])

    def test_heading_match_is_case_and_level_insensitive(self):
        for heading in ("# GOTCHAS", "### Gotchas", "## gotchas and quirks"):
            with self.subTest(heading=heading):
                name = "h" + str(abs(hash(heading)))[:8] + "-skill"
                skill = write_skill(self.base, name, f"{heading}\n\n- Something real.")
                self.assertEqual(gotchas_warnings(validate_skill(str(skill))), [])

    def test_word_gotchas_in_prose_does_not_count(self):
        """Only a heading satisfies the check -- a passing mention is not a section."""
        skill = write_skill(
            self.base,
            "prose-only-skill",
            "This skill has some gotchas you should know about.",
        )
        self.assertEqual(len(gotchas_warnings(validate_skill(str(skill)))), 1)


if __name__ == "__main__":
    unittest.main()
