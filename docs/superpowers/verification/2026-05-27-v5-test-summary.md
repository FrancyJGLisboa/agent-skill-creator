# v5.0 Test Suite Summary — 2026-05-27

## Final test counts

- Template structure tests: 14
- Detector unit tests: 21
- Detector accuracy gate: 1 (passing at 92.0%)
- Phase 2 integration tests: 5
- v4 regression tests: 2
- **Total: 43 tests, all passing**

## Detector accuracy

- Accuracy on labeled set: 92.0% (46/50)
- Threshold required by spec: 85%
- Headroom above threshold: 7.0 percentage points

## v4 regression

- v4 skills tested: 10 fixture entries (1 real + 9 synthetic)
- Real-path skills validated: 1/1 — `references/examples/stock-analyzer/SKILL.md` validates with `valid=True` under the v5 validator. (Warnings on missing `-skill` suffix, `license`, `metadata`, and `AGENTS.md` are non-blocking and expected for v4-era skills.)
- Detector did not crash on any v4 description; all 10 returned a value in the allowed set `{line-chart, bar-chart, kpi-cards, data-table, None}`.

## Notes

- The repo ships only one concrete v4 SKILL.md (`stock-analyzer`). The other 9 fixture entries are synthetic descriptions modelled after README-documented community skills (`sales-report-skill`, `deploy-checklist-skill`, `quarterly-compliance-skill`, `customer-churn-skill`, `incident-runbook-skill`) plus four common workflow archetypes (invoice processor, meeting notes, API doc generator, data cleaner). They exercise the detector's no-crash contract against v4-era workflow language.
- Running `uv run python -m unittest discover scripts/tests -v` produces `Ran 43 tests in 0.011s — OK`.
