# Gates: Discovery integration

Scope: Registry metadata, catalog generation, and CLI discovery compose correctly.

- [x] G1: Discovery and marketplace tests pass.
  CHECK: python3 -m pytest scripts/tests/test_marketplace_discovery.py scripts/tests/test_team_marketplace.py -q
  EXPECT: /passed/
  EVIDENCE: ................................................                         [100%] | 48 passed in 18.54s
