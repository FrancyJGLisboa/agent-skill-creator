# Eval Spec: weekly-crm-report

The skill's loss function: structural binary checks plus golden CRM exports. Run
`python3 scripts/run_evals.py` (scores the golden baseline) or
`python3 scripts/run_evals.py --rollout` (runs the skill on each input and scores
the real output).

## Criteria

1. **valid-json** (command) — the summary parses as JSON.
2. **has-grand-total** (command) — a numeric `grand_total` is present.
3. **dedup-happened** (command) — `rows_after_dedup` ≤ `rows_in`.

## Golden cases

Three CRM exports with intentional duplicates. Output totals are computed at
runtime, so cases are `pending-first-green`; capture a baseline with
`python3 scripts/run_evals.py --rollout --promote`.

## Spec

```json
{
  "skill": "weekly-crm-report",
  "run": "python3 scripts/run_pipeline.py --input {input} --output {output}",
  "criteria": [
    {"id": "valid-json", "text": "Summary parses as JSON", "type": "command", "cmd": "python3 -c \"import json,sys; json.load(open(sys.argv[1]))\" {output}"},
    {"id": "has-grand-total", "text": "Numeric grand_total present", "type": "command", "cmd": "python3 -c \"import json,sys; d=json.load(open(sys.argv[1])); assert isinstance(d['grand_total'],(int,float))\" {output}"},
    {"id": "dedup-happened", "text": "rows_after_dedup <= rows_in", "type": "command", "cmd": "python3 -c \"import json,sys; d=json.load(open(sys.argv[1])); assert d['rows_after_dedup'] <= d['rows_in']\" {output}"}
  ],
  "golden": [
    {"id": "case-1", "input": "golden/case-1/input.csv", "expected": null, "split": "val", "expected_status": "pending-first-green"},
    {"id": "case-2", "input": "golden/case-2/input.csv", "expected": null, "split": "val", "expected_status": "pending-first-green"},
    {"id": "case-3", "input": "golden/case-3/input.csv", "expected": null, "split": "val", "expected_status": "pending-first-green"}
  ]
}
```
