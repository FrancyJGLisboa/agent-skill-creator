#!/usr/bin/env python3
"""Fail CI when changed skill packages lack current verification evidence."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from generate_verification import verification_errors


def changed_skill_dirs(base: str, head: str = "HEAD") -> list[Path]:
    """Return unique skill roots affected between two Git revisions."""
    result = subprocess.run(["git", "diff", "--name-only", f"{base}..{head}"], text=True, capture_output=True, check=False)
    if result.returncode:
        raise ValueError(f"cannot diff {base}..{head}")
    roots: set[Path] = set()
    for raw in result.stdout.splitlines():
        path = Path(raw)
        for parent in (path.parent, *path.parents):
            if parent == Path("."):
                break
            if (parent / "SKILL.md").is_file():
                roots.add(parent)
                break
    return sorted(roots)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check verification evidence for changed skills.")
    parser.add_argument("--base", required=True, help="Base Git revision to compare with HEAD.")
    args = parser.parse_args(argv)
    try:
        skills = changed_skill_dirs(args.base)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    failures: list[str] = []
    for skill in skills:
        errors = verification_errors(skill)
        if errors:
            failures.extend(f"{skill}: {error}" for error in errors)
        else:
            print(f"PASS {skill}: verification evidence is current")
    if failures:
        print("Verification gate failed:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print(f"Verification gate passed for {len(skills)} changed skill(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
