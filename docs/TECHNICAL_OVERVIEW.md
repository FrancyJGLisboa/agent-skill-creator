---
permalink: /TECHNICAL_OVERVIEW.html
---

# Technical Overview

This guide is for platform engineers and evaluators. It complements the short
[README](../README.md), which is intentionally written for people deciding whether to
create or operate a skill.

## Product model

An agent skill is a reusable workflow package that guides an agent from a recognized
situation to a verified outcome. It can use retrieved knowledge, MCP tools, APIs,
deterministic scripts, and agent judgment. It is not itself a RAG system, MCP server,
or agent runtime.

The factory turns workflow evidence into a skill with a decision contract: the
question, trigger, supported decision, required evidence, and success measure. It
validates structure, scans for security patterns, runs evals, and performs a safe
representative run before handoff.

## Governance model

The marketplace lifecycle is:

```text
create → attest → admit → approve → publish → discover → install
       → use → update → rollback → quarantine → retire
```

The marketplace is the governance layer for ownership, lifecycle state, immutable
versions, compatibility evidence, rollout, quarantine, and rollback. The skill
factory creates the artifact; the marketplace operator governs distribution. Full
procedures: [Governed Team Marketplace](TEAM_MARKETPLACE.md).

## Technical references

- [Skill creation and validation instructions](../SKILL.md)
- [Marketplace implementation and operations](TEAM_MARKETPLACE.md)
- [Platform installation adapters](INSTALL.md)
- [Structured interview protocol](../references/structured-interview.md)
- [Capability resolver contract](../references/capability-resolver-contract.md)
- [Product boundaries](PRODUCT_SCOPE.md)
- [Organizational acceptance protocol](ORGANIZATIONAL_ACCEPTANCE.md)
