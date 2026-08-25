# Gates: Marketplace discovery

Scope: Outcome-based search and structured skill pages expose decision-useful metadata.

- [x] G1: Search ranks outcome matches and filters compatibility/support.
  CHECK: python3 -m pytest scripts/tests/test_marketplace_discovery.py -q -k search
  EXPECT: /passed/
  EVIDENCE: 2026-08-25 — outcome weighting, stable ties, lifecycle, certification, and support filter tests passed.
- [x] G2: Structured pages include outcomes, examples, permissions, compatibility, and support.
  CHECK: python3 -m pytest scripts/tests/test_marketplace_discovery.py -q -k page
  EXPECT: /passed/
  EVIDENCE: 2026-08-25 — required metadata, structured page, Markdown injection, and unsafe path tests passed.
