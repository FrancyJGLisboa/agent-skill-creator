# weekly-crm-report

A bundled example skill: turns a raw weekly CRM export (CSV) into a clean
regional sales summary — drops duplicate rows, totals revenue per region, and
emits structured JSON.

It is small but real, and demonstrates the creator's full machinery end to
end: SKILL.md activation, a `run_pipeline.py` orchestrator, and a bundled
eval spec with golden cases.

## Requirements

Python 3.10+ only — the pipeline uses the standard library (no third-party
dependencies, no requirements.txt needed).

## Run it

```bash
python3 scripts/run_pipeline.py \
  --input evals/golden/case-1/input.csv \
  --output /tmp/crm-summary.json
cat /tmp/crm-summary.json
```

Input: a CSV with at least `region` and `amount` columns (extra columns are
ignored; fully duplicated rows are removed before totalling).

## Run the evals

```bash
python3 scripts/run_evals.py . --validate   # check the eval spec is well-formed
python3 scripts/run_evals.py . --rollout    # execute the skill on golden inputs
python3 scripts/run_evals.py . --rollout --promote   # capture first baselines
```

The eval spec lives in `evals/weekly-crm-report.eval.md` with three golden
cases under `evals/golden/`.

## Layout

```
weekly-crm-report/
├── SKILL.md                  # activation + usage contract
├── scripts/run_pipeline.py   # CSV → dedup → regional totals → JSON
├── scripts/run_evals.py      # eval runner (validate / rollout / promote)
└── evals/                    # eval spec + golden cases
```
