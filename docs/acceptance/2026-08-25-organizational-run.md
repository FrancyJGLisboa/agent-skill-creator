# Four-role organizational acceptance run — 2026-08-25

## Result

The first blind run exposed product and documentation defects. After fixes, fresh
administrator, operator-recreation, and consumer sessions passed the previously
blocked gates without implementation inspection or undocumented product commands.

This is agent-session evidence of documentation-driven operability. It is not a
substitute for the same trial with people who did not build the product.

## Roles

Four isolated sessions acted as:

1. Organizational administrator
2. Finance workflow expert
3. Marketplace operator
4. Operations consumer

Each received a separate workspace and only public documentation plus artifacts
legitimately published by the preceding role. Reading tests or implementation to find
an intended command counted as a failed gate.

## Lifecycle evidence

| Gate | Initial run | Post-fix verification |
|---|---|---|
| Define two departments, owners, approvers, platform, and starter bundle | Failed: required manual policy edits | Passed in a fresh administrator session using `init` options |
| Create and verify a real Finance skill | Passed | Passed |
| Reject an incomplete decision contract | Passed | Passed |
| Admit and publish immutable `v1.0.0` | Passed with local-tag intervention | Local bare release now creates and verifies its tag |
| Discover by consequential question | Passed without assistance | Passed |
| Install into a clean consumer project | Failed: local transport was hidden | Passed in a fresh consumer session with documented `--local --pin` |
| Invoke twice | Passed | Passed |
| Publish and install a newer version | Passed with local-transport assistance | Exact-tag local transport is now public and verified |
| Roll back and prove old behavior | Passed with local-transport assistance | Exact-tag contract is now enforced by the CLI |
| Quarantine and block installation before transport | Passed without assistance | Passed |
| Retire | Passed without assistance | Passed |
| Recreate as generation 2 | Failed: command absent | Passed with fresh lineage and legacy-lineage migration |
| Install generation 2 and prove new behavior | Not reachable | Passed in a fresh consumer session without assistance |

## Product defects fixed from the run

- Added organization-aware initialization for departments, owners, approvers,
  supported platforms, and empty starter bundles.
- Removed generated ACME placeholders when an organization supplies its policy.
- Added bytecode and mutation-lock exclusions to generated marketplaces.
- Added actionable gate diagnostics.
- Added public, exact-tag local installation.
- Made local bare-repository releases create, push, and verify their tag.
- Added governed `recreate` with fresh lineage, minimal predecessor tombstone,
  certification reset, bundle preservation, and legacy-lineage migration.
- Made custom installer paths containment boundaries with no unrequested home writes.
- Updated factory instructions so known marketplace ownership and approval metadata
  are included without inventing organizational authority.

## Remaining proof

Repeat the same protocol with one workflow expert, one marketplace operator, and one
consumer from another department who have not worked on this repository. Every request
for procedural help remains a defect or onboarding observation, even if the person
eventually completes the task.
