# Phase 2 — Eval Criteria Definition

This step runs inside Phase 2 (Design), after the skill's use cases are
defined and before the SKILL.md is generated. It decides the skill's **loss
function**: a small set of binary checks plus a few golden cases that define
what "the skill worked" means. The criteria are derived here; the files are
written in Phase 5.

A skill that ships its own eval spec is *born optimizable* — the bundled metric
is an instant regression test, and it is formatted so `autoresearch-universal`
can pick it up directly (see "Handoff" below).

## Why this exists

The hard part of optimizing a skill is not running a loop — it is defining the
metric. The user can recognize a good result but rarely articulates the success
criteria as measurable checks. So **you** do the decomposition: propose 3–6
binary checks, and the user only approves or vetoes. This is the metric-first
mindset applied to skill authoring.

## Inputs

- `description` (str) — the user's workflow description (raw or normalized by
  Phase 1 Triage)
- the use cases / outputs defined earlier in Phase 2
- any artifacts the user provided (files, URLs, screenshots) — these are the
  primary source of golden cases

## Step 1 — Derive 3–6 binary criteria

Each criterion must be:

1. **Binary** — answerable yes/no. Never scales, scores, or "rate out of 10".
2. **Specific & observable** — checkable by reading the output or running a
   command. "Output is valid JSON" not "the output is good".
3. **Independent** — each tests a different dimension; no overlap.
4. **Not gameable** — avoid criteria the skill can satisfy by parroting the
   wording without doing the work.

Tag each criterion as one of two grader types:

- **`command`** — graded by a shell command. Passes when the command exits 0.
  Carry the command in `cmd`; use the `{output}` placeholder where the produced
  (or expected) output file path belongs, e.g. `jq -e . {output}` or
  `test "$(wc -w < {output})" -lt 150`. **Prefer `command` wherever a reliable
  programmatic check exists.**
- **`llm-judge`** — graded by a model reading the output. Use only when meaning,
  tone, or quality cannot be checked by a command. The bundled runner does
  **not** grade these; it prints them as a checklist.

Present the criteria to the user for a thumbs-up before writing them (one short
confirmation, not a questionnaire).

## Step 2 — Assemble 3+ golden cases

A skill that does not exist yet has no "expected output". Use this order — it is
a design rule, not a user question:

1. **Seed from user artifacts (primary).** When the user provided files, URLs,
   or screenshots, those ARE golden cases — the creator already treats the
   artifact as the spec, so it doubles as `input` (and often `expected`). Reuse
   them; do not ask the user for examples.
2. **Synthesize input-only cases (fallback).** When no artifact fits, synthesize
   a representative `input` and set `expected: null` with
   `expected_status: "pending-first-green"`. On the skill's first successful
   run, capture the output and — with the user's approval — promote it to the
   `expected` baseline.
3. **Never interrogate the user for examples.** That re-introduces the cognitive
   constraint the factory exists to remove.

Mark each case `"split": "val"` — these become `autoresearch-universal`'s fixed
validation set.

## Step 3 — Emit the spec in Phase 5

Write, inside the generated skill:

```
<skill>/
  scripts/run_evals.py        # copied verbatim from scripts/run_evals_template.py
  evals/
    <skill-name>.eval.md      # prose + the ```json block below
    golden/
      case-1/{input.*, expected.*}
      case-2/{input.*, expected.*}
      case-3/{input.*}        # expected omitted when pending-first-green
```

`evals/<skill-name>.eval.md` is human-readable prose (the criteria and cases in
words) **plus** one fenced ` ```json ` block the runner and autoresearch parse:

```json
{
  "skill": "weekly-sales-report-skill",
  "run": "python3 scripts/run_pipeline.py --input {input} --output {output}",
  "criteria": [
    {"id": "valid-json", "text": "Output is valid JSON", "type": "command", "cmd": "jq -e . {output}"},
    {"id": "has-region-totals", "text": "Every region has a numeric total", "type": "llm-judge"}
  ],
  "golden": [
    {"id": "case-1", "input": "golden/case-1/input.csv", "expected": "golden/case-1/expected.json", "split": "val"},
    {"id": "case-2", "input": "golden/case-2/input.csv", "expected": "golden/case-2/expected.json", "split": "val"},
    {"id": "case-3", "input": "golden/case-3/input.csv", "expected": null, "split": "val", "expected_status": "pending-first-green"}
  ]
}
```

Paths in `input`/`expected` are relative to the `evals/` directory.

Copy the runner verbatim:

```bash
cp scripts/run_evals_template.py <skill>/scripts/run_evals.py
chmod +x <skill>/scripts/run_evals.py
```

Then confirm the spec is well-formed before delivery (parallel to `validate.py`
and `security_scan.py`):

```bash
python3 <skill>/scripts/run_evals.py --validate
```

It must report `VALID` (exit 0). Fix and re-run if not.

## Step 3.5 — Declare a `run` command (enables end-to-end rollout)

If the skill is runnable from one command (it has a `scripts/run_pipeline.py`
orchestrator, or a single entry script), add a `run` field to the spec: a command
template binding `{input}` (the golden case input) and `{output}` (where the skill
writes its result). Then `run_evals.py --rollout` executes the skill on each golden
input and scores the **real** produced output through the same `command` criteria.

```json
"run": "python3 scripts/run_pipeline.py --input {input} --output {output}"
```

Rules:
- `{output}` is **required** in `run`; `{input}` is optional (omit for skills that
  take no input file). `--validate` enforces this.
- The `run` field is **optional**. A spec without it still validates and scores the
  golden baseline exactly as before — `--rollout` then prints "rollout unavailable"
  and exits 0 (nothing to run is not a failure).
- For genuinely interactive/branching skills (no single deterministic command),
  omit `run` — the rollout harness is for the deterministic happy path, same
  boundary as the `run_pipeline.py` orchestrator (see `phase5-orchestration.md`).

## Step 4 — Tell the user how to use it

After creation, alongside the install/share messaging, print:

> This skill ships an eval spec at `evals/<skill-name>.eval.md`.
> Check it against the golden baseline anytime: `python3 scripts/run_evals.py`
> Run it end-to-end and score the real output: `python3 scripts/run_evals.py --rollout`
> Capture the first passing output as the baseline for pending cases:
> `python3 scripts/run_evals.py --rollout --promote`
> To optimize the skill against its metric:
> `/autoresearch-universal optimize . using evals/<skill-name>.eval.md`
> (`--rollout` runs the skill's `run` command; `llm-judge` checks are still a
> printed checklist, not auto-graded.)

## Handoff to autoresearch-universal (rule 18)

`autoresearch-universal` accepts externally-supplied eval criteria and skips its
own metric-definition phase (its rule 18). The emitted spec is the contract:

- the `criteria` array maps directly to its Phase-3 criteria (same `type` values:
  `command` with `cmd`, or `llm-judge`);
- the `golden` entries with `"split": "val"` map to its fixed `validation_items`.

So the spec is consumable with no manual reformatting. This is a **format
contract plus a documented one-liner**, not an automated trainer.

## Bypassing

- `/agent-skill-creator --no-eval <description>` — skip this step entirely; the
  generated skill carries no `evals/` directory and no `run_evals.py`. Strip the
  token from the prompt before passing it to Phase 1.

Eval generation is **on by default** (every skill should define its loss
function). `--no-eval` is the opt-out.

## Failure handling

| Condition | Action |
|---|---|
| Criteria derivation fails or raises | Log a warning, skip eval emission, proceed exactly as without evals. **Skill creation does not fail.** |
| `run_evals.py --validate` reports errors | Fix the spec and re-run; do not deliver an invalid spec. |
| No usable artifact for golden cases | Synthesize input-only cases marked `pending-first-green`. |

Eval emission is never allowed to block or fail skill creation (mirrors the
`--no-artifact` behavior of the Artifact Opportunity Assessment).

## Out of scope for this version

- Automated grading of `llm-judge` criteria (printed as a checklist).
- A held-out `test` split distinct from `val` (all golden cases are `val`).
- Multiple eval specs per skill.
- Making `--rollout` a hard pre-delivery gate: it runs arbitrary skill code and
  `pending-first-green` cases have no baseline to score, so it stays opt-in.
  `--validate` remains the delivery gate.

Now supported (previously out of scope): an end-to-end **rollout harness** —
`run_evals.py --rollout` runs the skill's declared `run` command on each golden
input and scores the real output (see Step 3.5).
