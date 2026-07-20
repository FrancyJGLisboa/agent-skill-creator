#!/usr/bin/env python3
"""
Evolve loop shipped inside every generated skill as scripts/evolve.py.

One command that closes the maintenance loop from the skill's own root:

    python3 scripts/evolve.py            # detect -> record -> re-verify
    python3 scripts/evolve.py --judge    # also grade llm-judge criteria (needs ANTHROPIC_API_KEY)

Steps:
  1. staleness_check --check-deps --check-drift --record
     (review-interval, dependency health, schema drift; failures append raw
     evidence to EVOLUTION.md)
  2. run_evals --rollout [--judge]
     (runs the skill on its golden inputs; command checks + baseline regression
     gate + optional pinned judge; failures append raw evidence to EVOLUTION.md)

Exit codes:
    0 - fresh and green
    1 - one or more steps failed; EVOLUTION.md holds the evidence
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    root = Path(__file__).resolve().parent.parent
    judge = ["--judge"] if "--judge" in args else []

    steps = [
        ("staleness", [
            sys.executable, "scripts/staleness_check.py", str(root),
            "--check-deps", "--check-drift", "--record",
        ]),
        ("evals", [
            sys.executable, "scripts/run_evals.py", str(root), "--rollout", *judge,
        ]),
    ]

    failures: list[tuple[str, int]] = []
    for name, cmd in steps:
        print(f"== evolve: {name} ==")
        proc = subprocess.run(cmd, cwd=root)  # noqa: S603
        if proc.returncode != 0:
            failures.append((name, proc.returncode))

    if failures:
        print("\nevolve: FAILED — raw evidence recorded in EVOLUTION.md")
        for name, rc in failures:
            print(f"  - {name} (exit {rc})")
        print(
            "next: fix the findings (or hand EVOLUTION.md back to "
            "/agent-skill-creator to regenerate), then re-run scripts/evolve.py "
            "until clean"
        )
        return 1

    print("\nevolve: all checks fresh and green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
