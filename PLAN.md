# Plan: Governed skill marketplace product

Depth: tree 4   Mode: orchestrated
Budget note: Five product subsystems implemented in dependency order with per-stage tests and a final regression sweep.

## Contract

- Interfaces: `team_marketplace.py` remains the CLI entry point and `registry.json` remains the source of truth. New modules expose pure functions plus argparse-facing orchestration.
- Data ownership: each stage owns its module and tests; shared CLI integration is performed by the driver after each stage is verified.
- Naming and conventions: schema version remains 2 with backward-compatible defaults; machine output is JSON; policy failures raise `MarketplaceError`; all persisted timestamps are UTC ISO-8601.
- Ordering: trust is integrated and verified before maintenance; maintenance before discovery; discovery before measurement; measurement before distribution.

## File ownership

| Leaf | Owns (create/modify) | Reads only |
|---|---|---|
| 1.1.1 | `scripts/marketplace_trust.py`, `scripts/tests/test_marketplace_trust.py`, `gates/leaf-1.1.1.md` | `scripts/team_marketplace.py`, eval and ledger modules |
| 1.2.1 | `scripts/marketplace_health.py`, `scripts/tests/test_marketplace_health.py`, `gates/leaf-1.2.1.md` | registry schema and maintenance modules |
| 1.3.1 | `scripts/marketplace_discovery.py`, `scripts/tests/test_marketplace_discovery.py`, `gates/leaf-1.3.1.md` | registry schema and platform registry |
| 1.4.1 | `scripts/marketplace_metrics.py`, `scripts/tests/test_marketplace_metrics.py`, `gates/leaf-1.4.1.md` | success ledger event conventions |
| 1.5.1 | `scripts/marketplace_distribution.py`, `scripts/tests/test_marketplace_distribution.py`, `gates/leaf-1.5.1.md` | platform and installer modules |
| driver | `scripts/team_marketplace.py`, `scripts/tests/test_team_marketplace.py`, docs, `GATES.md`, node gates | all files |

## Tree

- 1 Governed skill marketplace product .......... `GATES.md`
  - 1.1 Trust and governance .......... `gates/node-1.1.md`
    - 1.1.1 Trust primitives .......... `gates/leaf-1.1.1.md`
  - 1.2 Maintenance .......... `gates/node-1.2.md`
    - 1.2.1 Health engine .......... `gates/leaf-1.2.1.md`
  - 1.3 Discovery .......... `gates/node-1.3.md`
    - 1.3.1 Discovery engine .......... `gates/leaf-1.3.1.md`
  - 1.4 Measurement .......... `gates/node-1.4.md`
    - 1.4.1 Consented metrics .......... `gates/leaf-1.4.1.md`
  - 1.5 Distribution .......... `gates/node-1.5.md`
    - 1.5.1 Adapters and certification .......... `gates/leaf-1.5.1.md`

## Waves

- Wave 0: contract, registry compatibility, acceptance gates
- Wave 1: 1.1.1
- Wave 2: 1.2.1
- Wave 3: 1.3.1
- Wave 4: 1.4.1
- Wave 5: 1.5.1
- Integration: driver connects each verified module to CLI/schema/docs before advancing

## Status log

- 2026-08-25 plan written; contract, stage ordering, and file ownership fixed.
- 2026-08-25 waves 1-5 integrated in order; adversarial compatibility/release review completed; 23/23 gates met.
- 2026-08-25 implementation and verification completed; compatibility claims from discovery metadata now feed intake and health governance, and all marketplace gates were re-run with current evidence.
