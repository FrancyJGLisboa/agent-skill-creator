#!/usr/bin/env python3
"""
Eval runner shipped inside every generated skill as scripts/run_evals.py.

A generated skill carries its own loss function in evals/<skill>.eval.md: a set
of binary checks (each graded by a shell command or flagged for an LLM judge)
plus a handful of golden cases. This runner turns that spec into a deterministic
regression gate, a shape validator, and — when the spec declares a `run` command —
an end-to-end rollout harness that executes the skill on each golden input and
scores the real output. It still does NOT grade `llm-judge` checks — those are
printed as a checklist for an agent or autoresearch-universal.

Modes:
    python3 scripts/run_evals.py                 # run command checks against the
                                                 # golden baseline; non-zero exit
                                                 # if any fail
    python3 scripts/run_evals.py --validate      # check the spec is well-formed
    python3 scripts/run_evals.py --output OUT [--case ID]
                                                 # score a real produced output
    python3 scripts/run_evals.py --rollout [--promote] [--timeout N] [--case ID]
                                                 # run the skill (spec's `run`
                                                 # command) on each golden input,
                                                 # then score the produced output;
                                                 # --promote captures the first
                                                 # passing output as the baseline
                                                 # for pending-first-green cases
    python3 scripts/run_evals.py --json          # machine-readable result

The spec's optional `run` field is a command template binding {input} (the golden
case input path) and {output} (a produced-output path). Example:
    "run": "python3 scripts/run_pipeline.py --input {input} --output {output}"

Exit codes:
    0 - all checks passed (or --validate found no errors, or --rollout had nothing
        to run because the spec declares no `run` command)
    1 - a check failed, a rollout case errored, or the spec is malformed
    2 - no eval spec found
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

VALID_TYPES = ("command", "llm-judge")
MIN_GOLDEN_CASES = 3
OUTPUT_PLACEHOLDER = "{output}"
INPUT_PLACEHOLDER = "{input}"
DEFAULT_ROLLOUT_TIMEOUT = 120

_JSON_BLOCK = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)


def find_spec(skill_dir: Path) -> Path | None:
    """Return the first evals/*.eval.md under skill_dir, or None if absent."""
    evals_dir = skill_dir / "evals"
    if not evals_dir.is_dir():
        return None
    specs = sorted(evals_dir.glob("*.eval.md"))
    return specs[0] if specs else None


def parse_spec(spec_path: Path) -> dict:
    """Extract and parse the first fenced ```json block from an eval spec.

    Raises:
        ValueError: if no JSON block is present or it does not parse.
    """
    text = spec_path.read_text(encoding="utf-8")
    match = _JSON_BLOCK.search(text)
    if not match:
        raise ValueError(f"{spec_path}: no ```json block found")
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{spec_path}: malformed JSON block: {exc}") from exc


def validate_spec(spec: dict, skill_dir: Path) -> list[str]:
    """Return a list of shape errors for the spec (empty list means valid)."""
    errors: list[str] = []

    if not spec.get("skill"):
        errors.append("missing 'skill' name")

    # Optional `run` command (enables --rollout). Absent is fine; if present it
    # must be a non-empty string that knows where to write the produced output.
    if "run" in spec:
        run_cmd = spec.get("run")
        if not isinstance(run_cmd, str) or not run_cmd.strip():
            errors.append("'run' must be a non-empty string when present")
        elif OUTPUT_PLACEHOLDER not in run_cmd:
            errors.append(f"'run' must contain the {OUTPUT_PLACEHOLDER} placeholder")

    criteria = spec.get("criteria")
    if not isinstance(criteria, list) or not criteria:
        errors.append("'criteria' must be a non-empty list")
        criteria = []
    for i, crit in enumerate(criteria):
        where = f"criteria[{i}]"
        if not crit.get("id"):
            errors.append(f"{where}: missing 'id'")
        if not crit.get("text"):
            errors.append(f"{where}: missing 'text'")
        ctype = crit.get("type")
        if ctype not in VALID_TYPES:
            errors.append(f"{where}: 'type' must be one of {VALID_TYPES}, got {ctype!r}")
        if ctype == "command" and not crit.get("cmd"):
            errors.append(f"{where}: command criterion needs a non-empty 'cmd'")

    golden = spec.get("golden")
    if not isinstance(golden, list):
        errors.append("'golden' must be a list")
        golden = []
    if len(golden) < MIN_GOLDEN_CASES:
        errors.append(f"need at least {MIN_GOLDEN_CASES} golden cases, found {len(golden)}")
    for i, case in enumerate(golden):
        where = f"golden[{i}]"
        if not case.get("id"):
            errors.append(f"{where}: missing 'id'")
        inp = case.get("input")
        if not inp:
            errors.append(f"{where}: missing 'input'")
        elif not (skill_dir / "evals" / inp).exists():
            errors.append(f"{where}: input file not found: evals/{inp}")
        expected = case.get("expected")
        if expected is not None and not (skill_dir / "evals" / expected).exists():
            errors.append(f"{where}: expected file not found: evals/{expected}")
        if expected is None and case.get("expected_status") != "pending-first-green":
            errors.append(
                f"{where}: null 'expected' must be marked expected_status='pending-first-green'"
            )

    return errors


def _run_one(cmd: str, output_path: Path | None) -> bool:
    """Run a single command check once. {output} is bound to output_path.

    Returns True on exit code 0. Retries once on failure (matches autoresearch
    command-eval semantics).
    """
    if OUTPUT_PLACEHOLDER in cmd:
        if output_path is None:
            return False
        bound = cmd.replace(OUTPUT_PLACEHOLDER, shlex.quote(str(output_path)))
    else:
        bound = cmd
    for _ in range(2):
        proc = subprocess.run(bound, shell=True, capture_output=True)  # noqa: S602
        if proc.returncode == 0:
            return True
    return False


def run_command_checks(
    spec: dict,
    skill_dir: Path,
    output: Path | None = None,
    only_case: str | None = None,
) -> dict:
    """Run every command criterion against each applicable golden case.

    By default {output} binds to each case's `expected` baseline file. When
    `output` is given it binds to that path instead (scoring a real run); use
    `only_case` to restrict scoring to one case.

    Returns a result dict with passed/failed counts and per-check detail.
    """
    evals_dir = skill_dir / "evals"
    command_criteria = [c for c in spec.get("criteria", []) if c.get("type") == "command"]
    results: list[dict] = []
    passed = failed = skipped = 0

    for case in spec.get("golden", []):
        case_id = case.get("id", "?")
        if only_case and case_id != only_case:
            continue
        if output is not None:
            bound_output: Path | None = output
        elif case.get("expected"):
            bound_output = evals_dir / case["expected"]
        else:
            bound_output = None  # pending-first-green: no baseline yet

        for crit in command_criteria:
            needs_output = OUTPUT_PLACEHOLDER in crit["cmd"]
            if needs_output and bound_output is None:
                skipped += 1
                results.append({"case": case_id, "criterion": crit["id"], "status": "skipped"})
                continue
            ok = _run_one(crit["cmd"], bound_output)
            passed += ok
            failed += not ok
            results.append(
                {"case": case_id, "criterion": crit["id"], "status": "pass" if ok else "fail"}
            )

    return {"passed": passed, "failed": failed, "skipped": skipped, "checks": results}


def _expected_baseline_path(evals_dir: Path, case: dict) -> Path:
    """Where a promoted baseline is written for a case.

    Uses the case's declared `expected` path when present; otherwise the
    conventional golden/<case-id>/expected.json.
    """
    expected = case.get("expected")
    if expected:
        return evals_dir / expected
    return evals_dir / "golden" / case.get("id", "case") / "expected.json"


def _run_skill(run_cmd: str, input_path: Path | None, output_path: Path, skill_dir: Path, timeout: int) -> bool:
    """Execute the skill's `run` command for one case.

    Binds {input}/{output} placeholders and runs from the skill root. Returns
    True only on exit code 0 within the timeout. Mirrors _run_one's shell form
    and the timeout= convention used elsewhere (review_staleness, export_utils).
    """
    bound = run_cmd.replace(OUTPUT_PLACEHOLDER, shlex.quote(str(output_path)))
    if INPUT_PLACEHOLDER in bound:
        if input_path is None:
            return False
        bound = bound.replace(INPUT_PLACEHOLDER, shlex.quote(str(input_path)))
    try:
        proc = subprocess.run(  # noqa: S602
            bound, shell=True, cwd=str(skill_dir), capture_output=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return False
    return proc.returncode == 0


def run_rollout(
    spec: dict,
    skill_dir: Path,
    *,
    promote: bool = False,
    only_case: str | None = None,
    timeout: int = DEFAULT_ROLLOUT_TIMEOUT,
) -> dict:
    """Run the skill end-to-end on each golden input, then score the real output.

    For each golden case the spec's `run` command produces an output into a temp
    file; that output is then scored through the same command criteria used by
    run_command_checks. When `promote` is set, a pending-first-green case whose
    run and checks all pass has its produced output captured as the `expected`
    baseline.

    Returns {passed, failed, errors, promoted, checks}. `errors` counts cases
    whose `run` command itself failed or timed out (their checks are not scored).
    """
    evals_dir = skill_dir / "evals"
    run_cmd = spec.get("run")
    passed = failed = errors = 0
    promoted: list[str] = []
    checks: list[dict] = []

    for case in spec.get("golden", []):
        case_id = case.get("id", "?")
        if only_case and case_id != only_case:
            continue

        inp = case.get("input")
        input_path = (evals_dir / inp) if inp else None

        with tempfile.TemporaryDirectory() as td:
            produced = Path(td) / "output"
            ok = _run_skill(run_cmd, input_path, produced, skill_dir, timeout)
            if not ok or not produced.exists():
                errors += 1
                checks.append({"case": case_id, "criterion": "<run>", "status": "error"})
                continue

            scored = run_command_checks(spec, skill_dir, output=produced, only_case=case_id)
            passed += scored["passed"]
            failed += scored["failed"]
            checks.extend(scored["checks"])

            is_pending = case.get("expected") is None and (
                case.get("expected_status") == "pending-first-green"
            )
            if promote and is_pending and scored["failed"] == 0 and scored["passed"] > 0:
                dest = _expected_baseline_path(evals_dir, case)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(produced, dest)
                promoted.append(case_id)

    return {
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "promoted": promoted,
        "checks": checks,
    }


def llm_judge_criteria(spec: dict) -> list[dict]:
    """Return the criteria that require an LLM judge (not run by this script)."""
    return [c for c in spec.get("criteria", []) if c.get("type") == "llm-judge"]


def _default_skill_dir() -> Path:
    """The skill root is the parent of the scripts/ directory holding this file."""
    return Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a skill's bundled eval spec.")
    parser.add_argument(
        "skill_dir",
        nargs="?",
        default=None,
        help="Skill root (default: parent of this script's directory).",
    )
    parser.add_argument("--validate", action="store_true", help="Only check the spec is well-formed.")
    parser.add_argument("--output", default=None, help="Produced output to score against (binds {output}).")
    parser.add_argument("--case", default=None, help="Restrict scoring to this golden case id.")
    parser.add_argument(
        "--rollout",
        action="store_true",
        help="Run the skill (spec's 'run' command) on each golden input, then score the output.",
    )
    parser.add_argument(
        "--promote",
        action="store_true",
        help="With --rollout: capture the first passing output as the baseline for pending-first-green cases.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_ROLLOUT_TIMEOUT,
        help=f"With --rollout: per-case run timeout in seconds (default {DEFAULT_ROLLOUT_TIMEOUT}).",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)

    skill_dir = Path(args.skill_dir).resolve() if args.skill_dir else _default_skill_dir()

    spec_path = find_spec(skill_dir)
    if spec_path is None:
        msg = f"no evals/*.eval.md found under {skill_dir}"
        print(json.dumps({"error": msg}) if args.json else f"ERROR: {msg}", file=sys.stderr)
        return 2

    try:
        spec = parse_spec(spec_path)
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}) if args.json else f"ERROR: {exc}", file=sys.stderr)
        return 1

    errors = validate_spec(spec, skill_dir)
    if args.validate:
        if args.json:
            print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
        elif errors:
            print(f"INVALID {spec_path.name}:")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"VALID {spec_path.name}")
        return 1 if errors else 0

    if errors:
        # A malformed spec cannot be run honestly.
        head = f"ERROR: {spec_path.name} is malformed; run --validate"
        print(json.dumps({"error": head, "errors": errors}) if args.json else head, file=sys.stderr)
        return 1

    judges = llm_judge_criteria(spec)

    if args.rollout:
        if not spec.get("run"):
            msg = "rollout unavailable: spec has no 'run' command"
            print(json.dumps({"rollout": "unavailable", "reason": msg}) if args.json else msg)
            return 0
        result = run_rollout(
            spec, skill_dir, promote=args.promote, only_case=args.case, timeout=args.timeout
        )
        if args.json:
            print(json.dumps({**result, "llm_judge": [c["id"] for c in judges]}, indent=2))
        else:
            for check in result["checks"]:
                print(f"  [{check['status']:>7}] {check['case']} :: {check['criterion']}")
            print(
                f"\nrollout: {result['passed']} passed, {result['failed']} failed, "
                f"{result['errors']} errored"
            )
            if result["promoted"]:
                print(f"promoted baselines: {', '.join(result['promoted'])}")
            if judges:
                print("\nllm-judge checks (evaluate manually or via /autoresearch-universal):")
                for crit in judges:
                    print(f"  - {crit['id']}: {crit['text']}")
        return 1 if (result["failed"] or result["errors"]) else 0

    output = Path(args.output).resolve() if args.output else None
    result = run_command_checks(spec, skill_dir, output=output, only_case=args.case)

    if args.json:
        print(json.dumps({**result, "llm_judge": [c["id"] for c in judges]}, indent=2))
    else:
        for check in result["checks"]:
            print(f"  [{check['status']:>7}] {check['case']} :: {check['criterion']}")
        print(
            f"\ncommand checks: {result['passed']} passed, "
            f"{result['failed']} failed, {result['skipped']} skipped"
        )
        if judges:
            print("\nllm-judge checks (evaluate manually or via /autoresearch-universal):")
            for crit in judges:
                print(f"  - {crit['id']}: {crit['text']}")

    return 1 if result["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
