# Gates: Maintenance integration

Scope: Health checks run locally and on a schedule without bypassing trust policy.

- [x] G1: Maintenance tests and marketplace integration tests pass.
  CHECK: python3 -m pytest scripts/tests/test_marketplace_health.py scripts/tests/test_team_marketplace.py -q
  EXPECT: /passed/
  EVIDENCE: .......................................                                  [100%] | 39 passed in 22.35s
