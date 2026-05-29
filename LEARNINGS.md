# Project learnings — agent-skill-creator

## When adding a new Phase-5 gate, also touch the AGENTS.md Files block and the Step-10 report template

When introducing a new Phase-5 verifier, artifact, or generated file (eval spec,
pipeline orchestrator, etc.), update **two recurring spots** in
`references/pipeline-phases.md` that are easy to miss:

- **Step 2.5** — the AGENTS.md template's `## Files` block. Tools that read
  AGENTS.md but **not** SKILL.md (Augment, Continue.dev, Zed, etc.) only see
  the file listing here. A missing entry means an incomplete view for those
  tools.
- **Step 10** — the "Report Results" template. Add a `Pass: PASSED` line for
  the new gate so the agent's final summary reflects every check it ran.

**Why:** missed on the eval feature (caught by review) and again on the
orchestration feature (caught by review — same blind spot). The obvious
touchpoints — SKILL.md output-structure block, pipeline-phases.md file-order
table, the Phase 5 checklist — were handled both times; these two are
secondary mirrors of the same information and are silently incomplete unless
you remember them.

**When to apply:** any change that adds a generated file, validator, or
Phase-5 step. Treat as a checklist item before declaring a Phase-5 feature
done. Quick grep: `grep -n "## Files\|Report Results\|Validation: PASSED" references/pipeline-phases.md`.
