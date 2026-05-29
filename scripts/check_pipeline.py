#!/usr/bin/env python3
"""
Pipeline orchestration verifier for generated skills.

A skill is prose an agent interprets, so relying on the agent to run several
scripts in the right order is unreliable. The fix is to move sequencing into
code: a single `scripts/run_pipeline.py` entry-point that calls the steps in
order. This verifier enforces the mechanical half of that contract:

1. compile  - every Python file under scripts/ and shared/ compiles (no
              SyntaxError). A broken script is the top reason an agent flails.
2. deps     - if any third-party module is imported, requirements.txt must be
              present and non-empty (so dependencies are declared, not implicit).
              This checks declaration, not per-package coverage, to avoid the
              import-name vs distribution-name false-positive trap.
3. entry    - (warning) when 2+ step scripts exist, a single run_pipeline.py
              orchestrator should exist so the agent runs ONE command instead
              of sequencing steps itself.

Usage:
    python3 scripts/check_pipeline.py <skill-dir>
    python3 scripts/check_pipeline.py <skill-dir> --json

Exit codes:
    0 - no errors (warnings allowed)
    1 - a script failed to compile, or third-party imports are undeclared
    2 - skill directory not found
"""

from __future__ import annotations

import argparse
import ast
import json
import py_compile
import sys
from pathlib import Path

_ENTRY = "run_pipeline.py"
_TOOLING = {"run_pipeline.py", "run_evals.py"}
_SKIP_DIR_PARTS = {"__pycache__", "tests"}


def python_files(skill_dir: Path) -> list[Path]:
    """All .py files under the skill's scripts/ and shared/ trees."""
    out: list[Path] = []
    for sub in ("scripts", "shared"):
        root = skill_dir / sub
        if root.is_dir():
            out += [
                p for p in root.rglob("*.py")
                if not (_SKIP_DIR_PARTS & set(p.parts))
            ]
    return sorted(out)


def compile_failures(files: list[Path]) -> list[str]:
    """Return 'path: message' for every file that fails to compile."""
    failures: list[str] = []
    for f in files:
        try:
            py_compile.compile(str(f), doraise=True)
        except py_compile.PyCompileError as exc:
            failures.append(f"{f}: {exc.msg}")
    return failures


def _local_module_names(skill_dir: Path, files: list[Path]) -> set[str]:
    names = {p.stem for p in files}
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.is_dir():
        for child in scripts_dir.iterdir():
            if child.is_dir() and child.name not in _SKIP_DIR_PARTS:
                names.add(child.name)
    return names


def _top_level_imports(file: Path) -> set[str]:
    try:
        tree = ast.parse(file.read_text(encoding="utf-8"))
    except SyntaxError:
        return set()  # compile_failures reports this separately
    mods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mods.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            mods.add(node.module.split(".")[0])
    return mods


def third_party_imports(skill_dir: Path, files: list[Path]) -> list[str]:
    """Top-level imported modules that are neither stdlib nor local to the skill."""
    local = _local_module_names(skill_dir, files)
    stdlib = sys.stdlib_module_names
    third: set[str] = set()
    for f in files:
        for mod in _top_level_imports(f):
            if mod and mod not in local and mod not in stdlib:
                third.add(mod)
    return sorted(third)


def requirements_declared(skill_dir: Path) -> bool:
    """True if requirements.txt exists with at least one non-comment entry."""
    req = skill_dir / "requirements.txt"
    if not req.exists():
        return False
    for line in req.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return True
    return False


def step_scripts(skill_dir: Path, files: list[Path]) -> list[Path]:
    """Scripts that look like runnable pipeline steps (have a __main__ guard),
    excluding the orchestrator, the eval runner, and utility/test modules."""
    steps: list[Path] = []
    for f in files:
        if f.name in _TOOLING or "utils" in f.parts:
            continue
        text = f.read_text(encoding="utf-8")
        if "if __name__" in text and "__main__" in text:
            steps.append(f)
    return steps


def has_orchestrator(skill_dir: Path) -> bool:
    return (skill_dir / "scripts" / _ENTRY).exists()


def check(skill_dir: Path) -> dict:
    """Run all checks. Returns {errors: [...], warnings: [...]}."""
    files = python_files(skill_dir)
    errors: list[str] = []
    warnings: list[str] = []

    errors += [f"does not compile -> {fail}" for fail in compile_failures(files)]

    third = third_party_imports(skill_dir, files)
    if third and not requirements_declared(skill_dir):
        errors.append(
            "third-party imports are not declared: add a requirements.txt listing "
            f"the package(s) behind {', '.join(third)}"
        )

    steps = step_scripts(skill_dir, files)
    if len(steps) >= 2 and not has_orchestrator(skill_dir):
        warnings.append(
            f"{len(steps)} runnable step scripts but no scripts/{_ENTRY} — the agent "
            "will have to sequence them from prose. Add a single orchestrator entry-point."
        )

    return {"errors": errors, "warnings": warnings}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify a generated skill's pipeline wiring.")
    parser.add_argument("skill_dir", help="Path to the skill directory.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)

    skill_dir = Path(args.skill_dir).resolve()
    if not skill_dir.is_dir():
        msg = f"not a directory: {skill_dir}"
        print(json.dumps({"error": msg}) if args.json else f"ERROR: {msg}", file=sys.stderr)
        return 2

    result = check(skill_dir)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for err in result["errors"]:
            print(f"  [ERROR] {err}")
        for warn in result["warnings"]:
            print(f"  [WARN]  {warn}")
        if not result["errors"] and not result["warnings"]:
            print("pipeline OK")
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
