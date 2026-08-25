# Gates: Measurement integration

Scope: Marketplace commands emit consented events without affecting core operations.

- [x] G1: Measurement and marketplace tests pass.
  CHECK: python3 -m pytest scripts/tests/test_marketplace_metrics.py scripts/tests/test_team_marketplace.py -q
  EXPECT: /passed/
  EVIDENCE: ....................................................                     [100%] | 52 passed in 17.58s
