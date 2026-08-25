# Gates: Governed distribution

Scope: Platform adapters use exact releases and certify real compatibility.

- [x] G1: Adapters resolve safe native destinations and exact-version artifacts.
  CHECK: python3 -m pytest scripts/tests/test_marketplace_distribution.py -q -k adapter
  EXPECT: /passed/
  EVIDENCE: 2026-08-25 — canonical destination, unsafe path, native/adapted plan, immutable ref, and version mismatch tests passed.
- [x] G2: Certification records verified platforms and rejects unsupported claims.
  CHECK: python3 -m pytest scripts/tests/test_marketplace_distribution.py -q -k certif
  EXPECT: /passed/
  EVIDENCE: 2026-08-25 — explicit checks, timestamp/adapter/version record, unknown platform, unsupported claim, missing/failed check tests passed.
