# Gates: Trust integration

Scope: Trust primitives are integrated into marketplace intake, checking, and release.

- [x] G1: Trust and marketplace tests pass together.
  CHECK: python3 -m pytest scripts/tests/test_marketplace_trust.py scripts/tests/test_team_marketplace.py -q
  EXPECT: /passed/
  EVIDENCE: ...................................................................      [100%] | 67 passed in 18.20s
