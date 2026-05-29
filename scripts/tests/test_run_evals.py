"""Unit tests for scripts.run_evals_template (shipped as run_evals.py).

Covers the two modes the runner exposes: --validate (shape checking) and the
default run (deterministic command checks against the golden baseline).
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from run_evals_template import (  # noqa: E402
    find_spec,
    llm_judge_criteria,
    main,
    parse_spec,
    run_command_checks,
    validate_spec,
)

# Portable command checks (no jq dependency). {output} binds to the expected
# baseline file in default run mode.
PASS_CMD = "test -s {output}"          # expected file exists and is non-empty
FAIL_CMD = "grep -q __NO_SUCH_TOKEN__ {output}"  # token never present -> exit 1

WELL_FORMED_CRITERIA = [
    {"id": "non-empty", "text": "Output is non-empty", "type": "command", "cmd": PASS_CMD},
    {"id": "has-totals", "text": "Each region has a total", "type": "llm-judge"},
]


def _make_skill(tmp: Path, criteria: list[dict], golden: list[dict]) -> Path:
    """Create a minimal skill dir with an eval spec + golden files; return it."""
    skill = tmp / "demo-skill"
    (skill / "scripts").mkdir(parents=True)
    evals = skill / "evals"
    evals.mkdir()
    for case in golden:
        case_dir = evals / "golden" / case["id"]
        case_dir.mkdir(parents=True)
        if case.get("input"):
            (evals / case["input"]).write_text("col\n1\n", encoding="utf-8")
        if case.get("expected"):
            (evals / case["expected"]).write_text('{"ok": true}\n', encoding="utf-8")
    spec = {"skill": "demo-skill", "criteria": criteria, "golden": golden}
    body = "# Eval Spec: demo-skill\n\nprose\n\n```json\n" + json.dumps(spec, indent=2) + "\n```\n"
    (evals / "demo-skill.eval.md").write_text(body, encoding="utf-8")
    return skill


def _three_golden(with_expected: bool = True) -> list[dict]:
    cases = []
    for i in (1, 2, 3):
        case = {"id": f"case-{i}", "input": f"golden/case-{i}/input.csv", "split": "val"}
        if with_expected:
            case["expected"] = f"golden/case-{i}/expected.json"
        else:
            case["expected"] = None
            case["expected_status"] = "pending-first-green"
        cases.append(case)
    return cases


class ValidateSpecTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_well_formed_spec_has_no_errors(self) -> None:
        skill = _make_skill(self.tmp, WELL_FORMED_CRITERIA, _three_golden())
        spec = parse_spec(find_spec(skill))
        self.assertEqual(validate_spec(spec, skill), [])

    def test_non_binary_grader_type_is_rejected(self) -> None:
        criteria = [{"id": "x", "text": "rate it", "type": "scale-1-5"}]
        skill = _make_skill(self.tmp, criteria, _three_golden())
        spec = parse_spec(find_spec(skill))
        self.assertTrue(any("type" in e for e in validate_spec(spec, skill)))

    def test_command_criterion_without_cmd_is_rejected(self) -> None:
        criteria = [{"id": "x", "text": "valid json", "type": "command"}]
        skill = _make_skill(self.tmp, criteria, _three_golden())
        spec = parse_spec(find_spec(skill))
        self.assertTrue(any("cmd" in e for e in validate_spec(spec, skill)))

    def test_fewer_than_three_golden_cases_is_rejected(self) -> None:
        skill = _make_skill(self.tmp, WELL_FORMED_CRITERIA, _three_golden()[:2])
        spec = parse_spec(find_spec(skill))
        self.assertTrue(any("golden cases" in e for e in validate_spec(spec, skill)))

    def test_null_expected_without_pending_flag_is_rejected(self) -> None:
        golden = _three_golden(with_expected=False)
        del golden[0]["expected_status"]  # null expected, not flagged
        skill = _make_skill(self.tmp, WELL_FORMED_CRITERIA, golden)
        spec = parse_spec(find_spec(skill))
        self.assertTrue(any("pending-first-green" in e for e in validate_spec(spec, skill)))

    def test_pending_first_green_is_valid(self) -> None:
        skill = _make_skill(self.tmp, WELL_FORMED_CRITERIA, _three_golden(with_expected=False))
        spec = parse_spec(find_spec(skill))
        self.assertEqual(validate_spec(spec, skill), [])


class RunCommandChecksTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_passing_command_check_zero_failures(self) -> None:
        skill = _make_skill(self.tmp, WELL_FORMED_CRITERIA, _three_golden())
        spec = parse_spec(find_spec(skill))
        result = run_command_checks(spec, skill)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["passed"], 3)  # one command criterion x 3 cases

    def test_failing_command_check_is_counted(self) -> None:
        criteria = [{"id": "miss", "text": "has token", "type": "command", "cmd": FAIL_CMD}]
        skill = _make_skill(self.tmp, criteria, _three_golden())
        spec = parse_spec(find_spec(skill))
        result = run_command_checks(spec, skill)
        self.assertEqual(result["failed"], 3)

    def test_llm_judge_not_run_as_command(self) -> None:
        criteria = [{"id": "j", "text": "tone is right", "type": "llm-judge"}]
        skill = _make_skill(self.tmp, criteria, _three_golden())
        spec = parse_spec(find_spec(skill))
        result = run_command_checks(spec, skill)
        self.assertEqual(result["passed"], 0)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(len(llm_judge_criteria(spec)), 1)

    def test_pending_first_green_case_is_skipped_not_failed(self) -> None:
        criteria = [{"id": "non-empty", "text": "non-empty", "type": "command", "cmd": PASS_CMD}]
        skill = _make_skill(self.tmp, criteria, _three_golden(with_expected=False))
        spec = parse_spec(find_spec(skill))
        result = run_command_checks(spec, skill)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["skipped"], 3)


class MainExitCodeTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_validate_well_formed_exits_zero(self) -> None:
        skill = _make_skill(self.tmp, WELL_FORMED_CRITERIA, _three_golden())
        self.assertEqual(main([str(skill), "--validate"]), 0)

    def test_validate_malformed_exits_one(self) -> None:
        criteria = [{"id": "x", "text": "valid json", "type": "command"}]  # no cmd
        skill = _make_skill(self.tmp, criteria, _three_golden())
        self.assertEqual(main([str(skill), "--validate"]), 1)

    def test_run_all_pass_exits_zero(self) -> None:
        skill = _make_skill(self.tmp, WELL_FORMED_CRITERIA, _three_golden())
        self.assertEqual(main([str(skill)]), 0)

    def test_run_with_failure_exits_one(self) -> None:
        criteria = [{"id": "miss", "text": "has token", "type": "command", "cmd": FAIL_CMD}]
        skill = _make_skill(self.tmp, criteria, _three_golden())
        self.assertEqual(main([str(skill)]), 1)

    def test_missing_spec_exits_two(self) -> None:
        empty = self.tmp / "no-evals-skill"
        empty.mkdir()
        self.assertEqual(main([str(empty)]), 2)


if __name__ == "__main__":
    unittest.main()
