"""Tests for scripts.validate.

Focused on the `## Gotchas` body check: a generated skill must carry the
environment-specific facts that defy reasonable assumptions, but a missing
section is a warning rather than an error -- it should not block delivery of an
otherwise-working skill.
"""

import sys
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from validate import validate_skill  # noqa: E402
from structured_interview import CORE_FIELDS, confirm, new_interview, save  # noqa: E402

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
    (skill / "discovery.json").write_text(json.dumps({
        "question": "What result requires action?",
        "trigger": ["Representative input becomes available"],
        "decision": ["Accept or correct the result"],
        "evidence": ["The supplied input and produced output"],
        "success_measure": "The result passes the skill's evaluation criteria.",
        "environment": {
            "documentation_sources": ["Test fixture documentation"],
            "data_sources": ["Test fixture input"],
            "required_capabilities": ["Read fixture input"],
            "readiness_checks": ["Fixture input exists"],
        },
        "risk": {"tier": "low", "permissions": ["Read fixture input"],
                 "mutation_boundary": "read-only", "approval_required": []},
        "software_mutation": {"applies": False},
        "data_interfaces": {"applies": False},
        "semantic_contract": {"applies": False},
        "routing_tests": {
            "should_trigger": ["Run fixture one", "Run fixture two", "Run fixture three"],
            "should_not_trigger": ["Ignore fixture one", "Ignore fixture two", "Ignore fixture three"],
        },
    }), encoding="utf-8")
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

    def test_missing_decision_contract_is_invalid(self):
        skill = write_skill(self.base, "missing-question-skill", "## Gotchas\n\nNone known.")
        (skill / "discovery.json").unlink()
        result = validate_skill(str(skill))
        self.assertFalse(result["valid"])
        self.assertTrue(any("discovery.json" in error for error in result["errors"]))

    def test_legacy_missing_semantic_contract_is_valid_with_migration_warning(self):
        skill = write_skill(self.base, "legacy-contract-skill", "## Gotchas\n\nNone known.")
        path = skill / "discovery.json"
        discovery = json.loads(path.read_text(encoding="utf-8"))
        discovery.pop("semantic_contract")
        path.write_text(json.dumps(discovery), encoding="utf-8")

        result = validate_skill(str(skill))

        self.assertTrue(result["valid"])
        self.assertTrue(any("legacy discovery.json" in warning for warning in result["warnings"]))

    def test_present_interview_state_blocks_an_unresolved_generated_skill(self):
        skill = write_skill(self.base, "unresolved-interview-skill", "## Gotchas\n\nNone known.")
        save(skill / "interview.json", new_interview("Build report", created_by="owner"))

        result = validate_skill(str(skill))

        self.assertFalse(result["valid"])
        self.assertTrue(any("interview.json is not ready" in error for error in result["errors"]))

    def test_confirmed_nonsemantic_interview_state_passes_validation(self):
        skill = write_skill(self.base, "ready-interview-skill", "## Gotchas\n\nNone known.")
        state = new_interview("Build report", created_by="owner")
        for field in CORE_FIELDS:
            value = False if field == "semantic_contract_applies" else f"approved {field}"
            confirm(
                state, field, value=value, actor="owner", evidence=["owner-review"],
                authorized_human=True,
            )
        save(skill / "interview.json", state)

        result = validate_skill(str(skill))

        self.assertTrue(result["valid"], result["errors"])


LABEL_HINT = "do not say what to do with the file"


def label_warnings(result: dict) -> list[str]:
    return [w for w in result["warnings"] if LABEL_HINT in w]


class TestRunVsReadLabeling(unittest.TestCase):
    """A bare path leaves the agent guessing whether to execute or read a file."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.n = 0

    def tearDown(self):
        self._tmp.cleanup()

    def check(self, body: str) -> list[str]:
        self.n += 1
        skill = write_skill(self.base, f"label{self.n}-skill", "## Gotchas\n\nNone known.\n\n" + body)
        return label_warnings(validate_skill(str(skill)))

    def test_bare_script_path_warns(self):
        found = self.check("`scripts/fetch.py` handles authentication.")
        self.assertEqual(len(found), 1)
        self.assertIn("scripts/fetch.py", found[0])

    def test_run_verb_clears_it(self):
        self.assertEqual(self.check("Run `python3 scripts/fetch.py` to fetch the data."), [])

    def test_verb_on_previous_line_counts(self):
        self.assertEqual(self.check("Run the fetch step:\n\n`scripts/fetch.py --input x`"), [])

    def test_shell_fence_needs_no_verb(self):
        body = "Fetch the data:\n\n```bash\npython3 scripts/fetch.py --input x\n```"
        self.assertEqual(self.check(body), [])

    def test_bare_reference_path_warns(self):
        found = self.check("`references/api-guide.md` has the endpoint list.")
        self.assertEqual(len(found), 1)
        self.assertIn("references/api-guide.md", found[0])

    def test_read_verb_clears_it(self):
        self.assertEqual(self.check("Read `references/api-guide.md` for the endpoints."), [])

    def test_table_rows_are_exempt(self):
        """Reference tables carry the read intent in the column header."""
        body = "| File | Contents |\n|---|---|\n| `references/api-guide.md` | Endpoints |"
        self.assertEqual(self.check(body), [])

    def test_multiple_mentions_collapse_into_one_warning(self):
        body = "`scripts/a.py` does A.\n\n`scripts/b.py` does B.\n\n`scripts/c.py` does C."
        found = self.check(body)
        self.assertEqual(len(found), 1)
        self.assertIn("3 script mention(s)", found[0])

    def test_warning_only_never_invalid(self):
        self.n += 1
        skill = write_skill(self.base, "labelvalid-skill", "`scripts/x.py` exists.")
        result = validate_skill(str(skill))
        self.assertTrue(result["valid"])
        self.assertEqual(result["errors"], [])


if __name__ == "__main__":
    unittest.main()
