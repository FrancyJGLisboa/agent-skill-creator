# Gates: Distribution integration

Scope: Certification and governed install work through the marketplace CLI.

- [x] G1: Distribution and marketplace tests pass.
  CHECK: python3 -m pytest scripts/tests/test_marketplace_distribution.py scripts/tests/test_team_marketplace.py -q
  EXPECT: /passed/
  EVIDENCE: .................................................                        [100%] | 49 passed in 16.46s
