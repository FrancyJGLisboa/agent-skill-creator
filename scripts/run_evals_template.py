#!/usr/bin/env python3
"""
Eval runner shipped inside every generated skill as scripts/run_evals.py.

A generated skill carries its own loss function in evals/<skill>.eval.md: a set
of binary checks (each graded by a shell command or flagged for an LLM judge)
plus a handful of golden cases. This runner turns that spec into a deterministic
regression gate and a shape validator. It executes only the `command` checks; it
does NOT run the skill itself (no rollout harness) and does NOT grade `llm-judge`
checks — those are printed as a checklist for an agent or autoresearch-universal.

Modes:
    python3 scripts/run_evals.py                 # run command checks against the
                                                 # golden baseline; non-zero exit
                                                 # if any fail
    python3 scripts/run_evals.py --validate      # check the spec is well-formed
    python3 scripts/run_evals.py --output OUT [--case ID]
                                                 # score a real produced output
    python3 scripts/run_evals.py --json          # machine-readable result

Exit codes:
    0 - all run command checks passed (or --validate found no errors)
    1 - a command check failed, or the spec is malformed
    2 - no eval spec found
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

VALID_TYPES = ("command", "llm-judge")
MIN_GOLDEN_CASES = 3
OUTPUT_PLACEHOLDER = "{output}"

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

    output = Path(args.output).resolve() if args.output else None
    result = run_command_checks(spec, skill_dir, output=output, only_case=args.case)
    judges = llm_judge_criteria(spec)

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
