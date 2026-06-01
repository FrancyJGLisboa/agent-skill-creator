# Eval Spec: pr-blocker-summarizer

The skill's loss function: structural binary checks plus golden PR exports. Run
`python3 scripts/run_evals.py` or, end-to-end,
`python3 scripts/run_evals.py --rollout`.

## Criteria

1. **valid-json** (command) — the digest parses as JSON.
2. **has-summary-line** (command) — a non-empty `summary` string is present.
3. **counts-consistent** (command) — `blocked` + `ready` counts do not exceed `total`.

## Golden cases

Three PR exports spanning blocked, ready, and stale states. Cases are
`pending-first-green`; capture a baseline with `--rollout --promote`.

## Spec

```json
{
  "skill": "pr-blocker-summarizer",
  "run": "python3 scripts/run_pipeline.py --input {input} --output {output}",
  "criteria": [
    {"id": "valid-json", "text": "Digest parses as JSON", "type": "command", "cmd": "python3 -c \"import json,sys; json.load(open(sys.argv[1]))\" {output}"},
    {"id": "has-summary-line", "text": "Non-empty summary string", "type": "command", "cmd": "python3 -c \"import json,sys; d=json.load(open(sys.argv[1])); assert isinstance(d['summary'],str) and d['summary']\" {output}"},
    {"id": "counts-consistent", "text": "blocked+ready <= total", "type": "command", "cmd": "python3 -c \"import json,sys; d=json.load(open(sys.argv[1])); assert len(d['blocked'])+len(d['ready']) <= d['total']\" {output}"}
  ],
  "golden": [
    {"id": "case-1", "input": "golden/case-1/input.json", "expected": null, "split": "val", "expected_status": "pending-first-green"},
    {"id": "case-2", "input": "golden/case-2/input.json", "expected": null, "split": "val", "expected_status": "pending-first-green"},
    {"id": "case-3", "input": "golden/case-3/input.json", "expected": null, "split": "val", "expected_status": "pending-first-green"}
  ]
}
```
