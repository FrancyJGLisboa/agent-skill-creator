# Agent Skill Creator

**Turn lived expertise into trusted, reusable agent skills.**

![Agent Skill Creator: question to tested skill to governed marketplace](docs/assets/agent-skill-creator-social-preview.png)

[![CI](https://github.com/FrancyJGLisboa/agent-skill-creator/actions/workflows/ci.yml/badge.svg)](https://github.com/FrancyJGLisboa/agent-skill-creator/actions/workflows/ci.yml)
[![Agent Skills Open Standard](https://img.shields.io/badge/Agent%20Skills-Open%20Standard-blue)](https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx)
[![Platforms](https://img.shields.io/badge/installs%20on-17%20platforms-7c3aed)](docs/INSTALL.md)
[![Version](https://img.shields.io/badge/version-6.1.0-brightgreen)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)]()

[Website](https://francyjglisboa.github.io/agent-skill-creator/) ·
[Installation](docs/INSTALL.md) ·
[Worker runbook](docs/WORKER_RUNBOOK.md) ·
[Team marketplace](docs/TEAM_MARKETPLACE.md) ·
[Product scope](docs/PRODUCT_SCOPE.md)

Agent Skill Creator turns the way people already work into tested, installable agent
skills. Give it a prompt plus the evidence behind the work—spreadsheets, reports,
emails, screenshots, transcripts, links, or scripts—and it builds a reusable workflow
that an organization can review, publish, and improve.

## Start here

### I have expertise to turn into a skill — no code required

Open the AI agent you already use, attach examples of the work, and paste this:

```text
/agent-skill-creator

Turn my monthly revenue-variance review into a reusable internal skill.
I attached past reports and the source spreadsheets. The decision is whether to
escalate a material variance. It must not modify source data.
```

The creator asks for the business decisions only you can authorize, builds and tests
the skill, and shows a representative result. When it is correct, say: **“Publish
this to the Finance marketplace.”**

Do not use Git, edit registry files, or run marketplace commands. If the creator is
not installed in your agent, send this section to your marketplace operator.

### I run the marketplace

Use the [governed team marketplace guide](docs/TEAM_MARKETPLACE.md) to admit,
approve, release, distribute, update, quarantine, and roll back tested skills.

### I am evaluating the platform

Read the [product scope](docs/PRODUCT_SCOPE.md),
[organizational acceptance protocol](docs/ORGANIZATIONAL_ACCEPTANCE.md), and
[technical implementation guide](docs/TECHNICAL_OVERVIEW.md).

## Why teams use it

- **Preserve expert judgment.** A skill captures the question, evidence, decision,
  and success measure behind recurring work.
- **Trust what is shared.** Skills carry validation, security checks, evals, and a
  representative run before they are published.
- **Govern team use.** The marketplace provides ownership, approvals, versioned
  releases, discovery, rollback, quarantine, and compatibility evidence.

## How work moves through the organization

```text
SME supplies examples and approves the result
        ↓
Creator builds and verifies a skill
        ↓
Marketplace operator governs and publishes it
        ↓
Colleagues install an approved version and use it
```

The SME owns business meaning. The marketplace operator owns distribution and policy.
See [roles and handoffs](docs/TEAM_MARKETPLACE.md#roles-and-handoffs).

## Read more when needed

| Need | Read |
|---|---|
| Install on a supported AI tool | [Installation](docs/INSTALL.md) |
| Create, correct, and hand off a first skill | [Worker runbook](docs/WORKER_RUNBOOK.md) |
| Run a governed internal marketplace | [Team marketplace](docs/TEAM_MARKETPLACE.md) |
| Understand scope and product boundaries | [Product scope](docs/PRODUCT_SCOPE.md) |
| Review architecture, validation, and technical controls | [Technical overview](docs/TECHNICAL_OVERVIEW.md) |
| Contribute | [Contributing](CONTRIBUTING.md) |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
Contributions require the [contributor assignment](CONTRIBUTOR_ASSIGNMENT.md).

## License

MIT. See [LICENSE](LICENSE). Copyright © 2026 Francy J G Lisboa, also known as
Charuto. See [ownership](COPYRIGHT.md).
