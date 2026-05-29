# Phase 5 — Pipeline Orchestration

This step runs inside Phase 5 (Implementation) for any skill whose work is **two
or more scripts that must run in a fixed order**. It exists to fix a real failure
mode: a skill is prose an agent interprets, so if correct execution depends on the
agent re-deriving the step order and hand-carrying data between scripts every run,
it will eventually run the wrong script, skip a step, or pass the wrong input.

The fix is to **move sequencing out of prose and into code.**

## The rule

When a skill has 2+ scripts that form a pipeline:

1. **Emit one orchestrator entry-point** — `scripts/run_pipeline.py` — that imports
   each step's function and calls them in order, wiring each step's output into the
   next step's input **in code**. The step scripts keep their own `main()` for
   isolated testing, but the orchestrator is the real run path.
2. **Give the agent exactly one happy-path command** in the SKILL.md. Not "run
   fetch, then parse, then analyze" — instead: "run `python scripts/run_pipeline.py`".
   The agent's job collapses from *sequence N steps correctly* to *run one command*.
3. **Wire data in code, never via the agent.** Step B reads step A's return value /
   output file because `run_pipeline.py` passes it — not because the SKILL.md asks
   the agent to copy it across.
4. **Declare dependencies.** Every third-party import goes in `requirements.txt`.
5. **Prove it with the eval.** Because `run_pipeline.py` is a deterministic
   entry-point, you run it on a golden input to produce output, then have
   `run_evals.py --output <that-output>` assert it against the skill's binary
   checks. The two chain together into a real end-to-end check (see
   `phase2-eval-assessment.md`) — turning "the agent runs the right scripts in
   order" from a hope into a verified result. (`run_evals.py` does not invoke the
   pipeline itself; you run the orchestrator, then score its output.)

## Orchestrator shape

```python
#!/usr/bin/env python3
"""Single entry-point: runs the skill's steps in order."""
import argparse
from pathlib import Path

from fetch import fetch          # step 1
from parse import parse          # step 2
from analyze import analyze      # step 3


def run_pipeline(source: str, out: Path) -> Path:
    raw = fetch(source)          # step 1 output ...
    clean = parse(raw)           # ... feeds step 2 in code ...
    result = analyze(clean)      # ... feeds step 3 in code
    out.write_text(result)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", default="output.json")
    args = ap.parse_args()
    run_pipeline(args.source, Path(args.out))


if __name__ == "__main__":
    main()
```

The SKILL.md then documents one command: `python scripts/run_pipeline.py --source <X>`.

## Verify in Phase 5

Run the verifier alongside `validate.py` and `security_scan.py`:

```bash
python3 scripts/check_pipeline.py <skill-dir>
```

It enforces the mechanical half of the contract and must report no errors:

- **compile** — every `.py` under `scripts/` and `shared/` compiles (a broken
  script is the top reason an agent flails).
- **deps** — if any third-party module is imported, `requirements.txt` must be
  present and non-empty. (Checks declaration, not per-package coverage — avoids the
  import-name vs distribution-name false-positive trap.)
- **entry** *(warning)* — 2+ runnable step scripts but no `scripts/run_pipeline.py`.

## Honest boundary

A rigid orchestrator is **wrong** for skills that are genuinely interactive or
branch on agent judgment per step (e.g. "ask the user, then decide which analysis
to run"). For those, keep the prose workflow — the agent's decisions are the point.
The rule is: **one deterministic orchestrator for the deterministic happy-path;
prose only for the parts that truly need agent judgment.** Do not force every skill
into a runner, and do not collapse a genuinely branching workflow into a fake linear
one.

Two things to know about the verifier's limits:

- `check_pipeline.py` checks that `run_pipeline.py` *exists*, not that it correctly
  wires every step — the eval (check 5) is the wiring proof. A skeleton orchestrator
  passes the existence check but fails the eval.
- The `entry` warning fires whenever 2+ scripts have a `__main__` guard. If your
  skill is intentionally a set of **independent CLIs** (not a sequenced pipeline),
  the warning is a false positive — ignore it.

## Acceptance checks (locked)

A multi-script skill satisfies this step when all five are yes:

1. It emits **one** orchestrator entry-point that runs the steps in order.
2. Its SKILL.md gives the agent **exactly one** happy-path command, not N steps.
3. Step-to-step data dependencies are wired **in code**, never carried by the agent.
4. It declares its deps (`requirements.txt`) and `check_pipeline.py` reports no
   compile or undeclared-dependency errors.
5. The pipeline is **end-to-end checkable**: `run_pipeline.py` produces output on
   a golden input, and `run_evals.py --output <that-output>` asserts the final
   result against the binary checks (a two-command chain).

## Out of scope

- Rewriting genuinely interactive/branching skills into linear pipelines.
- A workflow engine / DAG framework — a plain Python entry-point is the design.
- Per-package requirement coverage matching (declaration presence only).
