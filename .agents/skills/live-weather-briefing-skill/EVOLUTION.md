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

