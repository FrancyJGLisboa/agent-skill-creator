# Gates: Marketplace health engine

Scope: Aggregate staleness, dependencies, regressions, ownership, and compatibility.

- [x] G1: All five health dimensions are evaluated with actionable findings.
  CHECK: python3 -m pytest scripts/tests/test_marketplace_health.py -q
  EXPECT: /passed/
  EVIDENCE: 2026-08-25 — 11 marketplace health tests passed; five-dimension failure fixture plus discovery-backed compatibility coverage assert severity, reason, remediation, and healthy fallback behavior.
- [x] G2: Reports are deterministic JSON and readable Markdown.
  CHECK: python3 -m pytest scripts/tests/test_marketplace_health.py -q -k report
  EXPECT: /passed/
  EVIDENCE: 2026-08-25 — deterministic JSON round-trip and stable Markdown report tests passed.
