# Gates: Marketplace measurement

Scope: Explicitly consented, privacy-safe organizational event aggregation.

- [x] G1: Recording is disabled without valid consent.
  CHECK: python3 -m pytest scripts/tests/test_marketplace_metrics.py -q -k consent
  EXPECT: /passed/
  EVIDENCE: 2026-08-25 — missing, disabled, malformed, incomplete, and expired consent tests passed without creating a ledger.
- [x] G2: Only closed-vocabulary, non-content events are stored and summarized.
  CHECK: python3 -m pytest scripts/tests/test_marketplace_metrics.py -q -k 'privacy or summary'
  EXPECT: /passed/
  EVIDENCE: 2026-08-25 — field rejection, salted IDs, deterministic funnel/correction, malformed count, and 7/28-day retention tests passed.
