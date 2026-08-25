# Gates: Governed skill marketplace product

Scope: All five ordered product stages work through the marketplace CLI and remain regression-safe.

- [x] G1: Trust admission requires executable evals, representative-run evidence bound to the submitted commit, and valid lifecycle state.
  CHECK: python3 -m pytest scripts/tests/test_marketplace_trust.py scripts/tests/test_team_marketplace.py -q
  EXPECT: /passed/
  EVIDENCE: ...................................................................      [100%] | 67 passed in 18.20s

- [x] G2: Scheduled maintenance checks produce machine-readable and human-readable marketplace health reports.
  CHECK: python3 -m pytest scripts/tests/test_marketplace_health.py -q
  EXPECT: /passed/
  EVIDENCE: ...........                                                              [100%] | 11 passed in 0.20s

- [x] G3: Outcome-oriented discovery supports structured pages, filtering/search, examples, compatibility, and support labels.
  CHECK: python3 -m pytest scripts/tests/test_marketplace_discovery.py -q
  EXPECT: /passed/
  EVIDENCE: ..................                                                       [100%] | 18 passed in 0.12s

- [x] G4: Marketplace measurement is disabled without explicit organizational consent and aggregates only approved privacy-safe events.
  CHECK: python3 -m pytest scripts/tests/test_marketplace_metrics.py -q
  EXPECT: /passed/
  EVIDENCE: ......................                                                   [100%] | 22 passed in 0.29s

- [x] G5: Governed distribution adapters install exact releases and compatibility certification blocks unsupported claims.
  CHECK: python3 -m pytest scripts/tests/test_marketplace_distribution.py -q
  EXPECT: /passed/
  EVIDENCE: ...................                                                      [100%] | 19 passed in 0.21s

- [x] G6: Full automated test and static-quality suites pass.
  CHECK: python3 -m pytest scripts/tests -q && uvx ruff check --target-version py310 scripts
  EXPECT: /passed/
  EVIDENCE: 479 passed, 41 subtests passed in 58.02s | All checks passed!

- [x] G7: Marketplace operator and user documentation covers the complete lifecycle and commands.
  CHECK: python3 -c "from pathlib import Path; p=Path('docs/TEAM_MARKETPLACE.md').read_text(); assert all(x in p for x in ['attestation','health','search','metrics','certif']); print('documentation complete')"
  EXPECT: documentation complete
  EVIDENCE: documentation complete
