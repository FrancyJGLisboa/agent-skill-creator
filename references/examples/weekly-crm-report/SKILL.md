---
name: weekly-crm-report
description: Cleans a weekly CRM export and produces a regional sales summary. Activates when the user asks to clean a CRM export, deduplicate sales rows, calculate regional totals, or generate a weekly sales report from a CSV.
license: MIT
metadata:
  author: agent-skill-creator
  version: 1.0.0
  created: 2026-06-27
  last_reviewed: 2026-07-20
  review_interval_days: 180
---

# Weekly CRM Report

Turn a raw weekly CRM export (CSV) into a clean regional sales summary: drop
duplicate rows, total revenue per region, and emit a structured JSON summary an
agent can narrate or hand to a PDF/dashboard step.

This is a bundled **example** skill — small but real, and used to demonstrate the
creator's validation, pipeline, and eval-rollout machinery end to end.

## Activation

Activates on requests like "clean this CRM export", "weekly sales report",
"regional totals from this CSV". Do **not** activate on general spreadsheet or
analytics questions that don't involve a CRM export.

## Input

A CSV with at least `region` and `amount` columns (extra columns are ignored).
Duplicate rows (identical across all columns) are removed before totalling.

## Run

One command produces the summary:

```bash
python3 scripts/run_pipeline.py --input <export.csv> --output summary.json
```

Output JSON shape:

```json
{
  "rows_in": 120,
  "rows_after_dedup": 118,
  "regions": {"West": 40210.5, "East": 38110.0},
  "grand_total": 78320.5
}
```

## Gotchas

- **`rows_after_dedup` does not reconcile with `grand_total`.** Rows with a blank
  or missing `region` are skipped when totalling but still counted in
  `rows_after_dedup`, so a CSV with unassigned rows reports more rows than it
  actually summed. Do not present the two numbers as if one explains the other —
  if they must reconcile, filter blank regions before running.
- **An unparseable `amount` silently becomes `0.0`,** it does not raise. A column
  of `N/A` or `—` produces a region total of `0.0` that looks like a real zero.
  Check the input for non-numeric amounts before trusting a suspiciously low total.
- **Dedup compares every column, not just `region` and `amount`.** Two rows with
  identical sales data but a differing timestamp or record-ID column are both kept.
  The "extra columns are ignored" note above applies to totalling, not to dedup.

## Anti-goals

- Not a general BI tool; it totals one numeric column per region.
- Does not fetch from a live CRM API; it operates on an exported CSV.
