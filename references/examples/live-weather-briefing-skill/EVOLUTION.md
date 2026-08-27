# Evolution log

Appended automatically by scripts/run_evals.py (and scripts/evolve.py) when a check fails. Each entry is the raw evidence for a fix/regenerate step.

## 2026-08-27T12:46:45Z — run_evals --rollout FAILED

- counts: passed=0, failed=0, errors=2, regressions=0, judge_failed=0
- failing checks (raw):

```json
[
  {
    "case": "sao-paulo",
    "criterion": "<run>",
    "status": "error"
  },
  {
    "case": "new-york",
    "criterion": "<run>",
    "status": "error"
  }
]
```

## 2026-08-27T12:47:46Z — run_evals --rollout FAILED

- counts: passed=3, failed=0, errors=1, regressions=0, judge_failed=0
- failing checks (raw):

```json
[
  {
    "case": "new-york",
    "criterion": "<run>",
    "status": "error"
  }
]
```

## 2026-08-27T13:57:41Z — correction from use

Change ID: `correction-20260827-135741-90678cdffd`

Reported while using the skill, not caught by any automated check.

> Treat a trailing two-letter country code as a geographic qualifier, not part of the city name.

Proposed skill edit: add the corrected behavior to `SKILL.md` → `## Gotchas`.

Regression test: `evals/corrections/correction-20260827-135741-90678cdffd.json` must keep this behavior in the skill.

Version recommendation: patch — correction from real use.

## 2026-08-27T13:58:17Z — correction from use

Change ID: `correction-20260827-135817-90678cdffd`

Reported while using the skill, not caught by any automated check.

> Treat a trailing two-letter country code as a geographic qualifier, not part of the city name.

Proposed skill edit: add the corrected behavior to `SKILL.md` → `## Gotchas`.

Regression test: `evals/corrections/correction-20260827-135817-90678cdffd.json` must keep this behavior in the skill.

Version recommendation: patch — correction from real use.

## 2026-08-27T13:59:10Z — correction from use

Change ID: `correction-20260827-135910-90678cdffd`

Reported while using the skill, not caught by any automated check.

> Treat a trailing two-letter country code as a geographic qualifier, not part of the city name.

Proposed skill edit: add the corrected behavior to `SKILL.md` → `## Gotchas`.

Regression test: `evals/corrections/correction-20260827-135910-90678cdffd.json` must keep this behavior in the skill.

Version recommendation: patch — correction from real use.

