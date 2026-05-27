# Claude Code Artifact Emission Format

**Status:** PENDING — Task 1 (M1) of the v6 plan has not yet been
executed. This file exists as a stub so other docs that cite it do not
dereference a missing path.

## What this file will contain when M1 completes

The literal emission syntax that Claude Code recognizes as an in-chat
interactive React artifact, captured empirically by:

1. Opening Claude Code in a fresh session
2. Asking Claude to emit a minimal React artifact
3. Capturing the exact text/tag/marker syntax verbatim
4. Verifying that a second paste of the captured emission renders
   identically (round-trip proof)

Plus:

- Required and optional attributes (id, type, title, etc.)
- Body format (raw JSX vs. wrapped, escaping rules)
- Compatibility notes — which Claude Code version range was verified
- Observed behavior in non-Claude hosts (fenced code, plain text, etc.)

## Until then

Phase 2 of agent-skill-creator MUST NOT inline artifact emission
instructions into generated skills, because the protocol is unverified.
The four bundled React templates under
`references/artifact-templates/` can be assembled correctly — they are
syntactically valid React — but the runtime instruction to emit them
using "Claude's artifact protocol" has no concrete syntax to point at
until this file is populated.

If you are following the plan in
`docs/superpowers/plans/2026-05-27-agent-skill-creator-v5-artifacts-first.md`,
Task 1 produces the content for this file. Do not skip it.

## References

- Spec: `docs/superpowers/specs/2026-05-27-agent-skill-creator-v5-artifacts-first-design.md`, §3.3 and §11 Q1-Q3
- Plan: `docs/superpowers/plans/2026-05-27-agent-skill-creator-v5-artifacts-first.md`, Task 1
- Phase 2 reference: `references/phase2-artifact-assessment.md`, Step 4
