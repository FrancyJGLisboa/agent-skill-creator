# Weekly CRM report — representative verification

Run date: 2026-08-27

## Workflow

A sales-operations user provides a Friday CRM export. The skill removes duplicate
rows and produces regional totals without sending email or changing production data.

## Evidence

```text
rollout: 6 passed, 0 failed, 0 errored, 0 regressed
held out (split=test, use --include-holdout): case-2
```

The representative input produced:

```json
{
  "rows_in": 4,
  "rows_after_dedup": 3,
  "regions": {"West": 100.5, "East": 350.25},
  "grand_total": 450.75
}
```

The skill package also declares support for 17 agent environments through its
cross-platform installer. This is compatibility coverage, not a claim that this
single verification run exercised all 17 environments.

## Reproduce

```bash
python3 scripts/skill_graph.py run references/examples/weekly-crm-report --jobs 4
python3 references/examples/weekly-crm-report/scripts/run_evals.py \
  references/examples/weekly-crm-report --rollout
python3 references/examples/weekly-crm-report/scripts/run_pipeline.py \
  --input references/examples/weekly-crm-report/evals/golden/case-1/input.csv \
  --output /tmp/weekly-crm-report.json
```
