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

---

# Gates: Agent-run technical emulation

Scope: Exercise technical build, run, governance, correction, and maintenance paths. These are not evidence of independent human adoption. Evidence is retained under `docs/verification/`.

- [x] E1: A technical workflow makes live, read-only external API calls and produces a source-linked result.
  CHECK: python3 references/examples/live-weather-briefing-skill/scripts/run_pipeline.py --city "Sao Paulo, BR" --output /tmp/asc-weather-emulation.md && rg '^# Current weather:' /tmp/asc-weather-emulation.md
  EXPECT: /Current weather:/
  EVIDENCE: # Current weather: São Paulo, São Paulo, Brazil

- [x] E2: A second, distinct technical workflow runs successfully against a live public API with its own evaluation suite and verification artifact.
  CHECK: python3 references/examples/github-release-briefing-skill/scripts/run_pipeline.py --repository openai/openai-python --output /tmp/asc-release-emulation.md && python3 scripts/generate_verification.py references/examples/github-release-briefing-skill --run-kind live --environment codex && rg '^# Latest release:' /tmp/asc-release-emulation.md
  EXPECT: /Latest release/
  EVIDENCE: /Users/francylisboacharuto/agent-skill-creator/references/examples/github-release-briefing-skill/VERIFICATION.md | # Latest release: openai/openai-python

- [x] E3: A governed marketplace admits independently version-bound, verified skills and exposes their reliability evidence.
  CHECK: python3 scripts/team_marketplace.py check --release --marketplace /tmp/asc-marketplace-emulation
  EXPECT: Marketplace checks passed
  EVIDENCE: Marketplace checks passed

- [x] E4: A simulated correction becomes a proposed edit, a regression record, a versioned reason, and fresh verification evidence.
  CHECK: python3 references/examples/live-weather-briefing-skill/scripts/evolve.py --correct "Treat a trailing two-letter country code as a geographic qualifier, not part of the city name." && python3 scripts/generate_verification.py references/examples/live-weather-briefing-skill --run-kind live --environment codex
  EXPECT: /correction recorded/
  EVIDENCE: next: run scripts/evolve.py to verify the proposed edit and correction regression | /Users/francylisboacharuto/agent-skill-creator/references/examples/live-weather-briefing-skill/VERIFICATION.md

- [x] E5: The changed-skill CI gate and focused regression suite accept current evidence and reject stale evidence.
  CHECK: python3 -m pytest scripts/tests/test_generate_verification.py scripts/tests/test_check_verification.py scripts/tests/test_team_marketplace.py -q
  EXPECT: /passed/
  EVIDENCE: .................................................................        [100%] | 65 passed in 26.03s

- [x] E6: Marketplace measurement records reliability outcomes only after explicit, current consent and stores no skill names.
  CHECK: python3 scripts/team_marketplace.py metrics-summary --marketplace /tmp/asc-marketplace-emulation
  EXPECT: /successful_run/
  EVIDENCE: "schema_version": 1 | }

- [x] E7: A published, certified skill produces a non-mutating exact install plan for its certified runtime.
  CHECK: python3 scripts/team_marketplace.py plan-install github-release-briefing-skill --department engineering --platforms codex --scope project --local --project-root /tmp/asc-install-target --marketplace /tmp/asc-marketplace-emulation
  EXPECT: /native-skill/
  EVIDENCE: ] | }

- [x] E8: Verification refuses a report when its bound skill changes, then accepts a regenerated report.
  CHECK: python3 -m pytest scripts/tests/test_generate_verification.py -q
  EXPECT: /passed/
  EVIDENCE: ...                                                                      [100%] | 3 passed in 0.17s
