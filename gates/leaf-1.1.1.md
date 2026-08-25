# Gates: Trust primitives

Scope: Enforce evals, commit-bound representative evidence, and lifecycle transitions.

- [x] G1: Missing or failing evals are rejected.
  CHECK: python3 -m pytest scripts/tests/test_marketplace_trust.py -q -k eval
  EXPECT: /passed/
  EVIDENCE: 2026-08-25 — targeted eval cases passed in scripts/tests/test_marketplace_trust.py.
- [x] G2: Attestations reject commit mismatch, failed runs, and malformed evidence.
  CHECK: python3 -m pytest scripts/tests/test_marketplace_trust.py -q -k attestation
  EXPECT: /passed/
  EVIDENCE: 2026-08-25 — commit mismatch and malformed/failed attestation cases passed.
- [x] G3: Only policy-authorized lifecycle transitions succeed.
  CHECK: python3 -m pytest scripts/tests/test_marketplace_trust.py -q -k lifecycle
  EXPECT: /passed/
  EVIDENCE: 2026-08-25 — allowed and forbidden lifecycle transition matrices passed.
