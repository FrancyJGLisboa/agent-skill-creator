# Agent Skill Creator

**Turn work you already do into a reusable agent workflow—and see it work once before calling it done.**

[![CI](https://github.com/FrancyJGLisboa/agent-skill-creator/actions/workflows/ci.yml/badge.svg)](https://github.com/FrancyJGLisboa/agent-skill-creator/actions/workflows/ci.yml)
[![Agent Skills Open Standard](https://img.shields.io/badge/Agent%20Skills-Open%20Standard-blue)](https://github.com/anthropics/agent-skills-spec)
[![Platforms](https://img.shields.io/badge/installs%20on-17%20platforms-7c3aed)](docs/INSTALL.md)
[![Version](https://img.shields.io/badge/version-6.1.0-brightgreen)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)]()

[Website](https://francyjglisboa.github.io/agent-skill-creator/) ·
[Installation](docs/INSTALL.md) ·
[Governed team marketplace](docs/TEAM_MARKETPLACE.md) ·
[GitLab team registry](docs/GITLAB_TEAM_REGISTRY.md) ·
[Changelog](CHANGELOG.md)

The governed marketplace includes commit-bound trust attestations, seven-state
lifecycle policy, scheduled health reports, outcome-based search, consent-gated
product metrics, and cross-platform distribution certification.

You do not need to write a specification or understand skill engineering. Give the
creator a sentence, spreadsheet, PDF, link, screenshot, transcript, or half-working
script. It reconstructs the workflow, confirms what a correct result means, builds and
checks the skill, installs it, and safely tries it on representative input.

## Create your first skill

### 1. Choose your AI tool

| You use | Paste this in | Installation |
|---|---|---|
| **Claude Code** | Claude Code | `/plugin marketplace add FrancyJGLisboa/agent-skill-creator` then `/plugin install agent-skill-creator@agent-skill-creator` |
| **Codex, Cursor, Copilot, Gemini, or another supported tool on macOS/Linux** | Terminal | `curl -fsSL https://raw.githubusercontent.com/FrancyJGLisboa/agent-skill-creator/main/scripts/bootstrap.sh \| sh` |
| **Any supported tool on Windows** | PowerShell | `irm https://raw.githubusercontent.com/FrancyJGLisboa/agent-skill-creator/main/scripts/bootstrap.ps1 \| iex` |

The installer detects the AI tools already on your computer and installs the creator
in their native locations. For a single-tool install or the complete 17-platform list,
use the [installation guide](docs/INSTALL.md).

**Success check:** reopen your AI tool and ask `What can agent-skill-creator do?` It
should describe turning a workflow into a reusable skill.

### 2. Give it work you already have

Paste this in your AI tool—not in Terminal:

```text
/agent-skill-creator Every Friday I clean the CRM export, calculate regional
totals, and email a PDF sales report.
```

You can attach the CRM export, an old report, or the script you currently use. The
creator first gives you a short understanding to confirm:

```text
Input: the Friday CRM export
Work: remove duplicates and total sales by region
Output: a PDF summary for the VP
Success: totals reconcile to the source and every region appears

Reply “yes” or correct the part I got wrong.
```

### 3. Judge the first result

The creator owns the technical work and reports four visible stages:

```text
Understand  ✓ workflow and success criteria confirmed
Build       ✓ reusable skill created
Check       ✓ structure, code, security patterns, and examples checked
Try         ✓ installed and run once on representative input
```

A successful handoff leads with the result:

```text
The weekly sales report now works from a CRM export.

Result: ./output/weekly-sales-report.pdf
Use it: /weekly-crm-report-skill data/crm-export.csv

Checks: structural requirements passed · 4 parallel checks passed · representative run passed
```

If a safe test needs credentials, data, or permission, the creator says
`verification-blocked` and gives one exact setup action. It does not send a real email,
publish, purchase, or write production data merely to prove the skill works.

If the result is wrong, describe the correction once:

```bash
python3 ./weekly-crm-report-skill/scripts/evolve.py --correct "UK sales arrive one day late"
```

The correction becomes part of the skill's maintained knowledge.

## What happens behind the four stages

You do not need this section to create a skill. It explains what the creator is doing
when you want to inspect the process.

Every skill is checked as one connected system. The skill graph links its
instructions, scripts, evaluations, and expected outputs. Two structural
requirements confirm that every expected result is tested and every predictable
multi-step workflow has one reliable entry point. Four checks—specification,
pipeline, security, and evaluation schema—run in parallel. Finally, a representative
run proves that the skill produces a useful result.

| What you see | What the factory does | Evidence left behind |
|---|---|---|
| **Understand** | Reads all material, reconstructs the workflow, identifies inputs, outputs, and success criteria | A plain-language hypothesis you approve or correct |
| **Build** | Researches sources, designs use cases, chooses the structure, writes instructions and functional scripts | A complete installable skill package |
| **Check** | Connects the package in a skill graph, applies two structural requirements, and runs four checks in parallel | A connected artifact map, requirement results, and reusable check evidence |
| **Try** | Installs to the detected tool and runs a safe representative example | An output you can inspect and correct |

Internally, Build covers the five engineering phases: discovery, design, architecture,
detection, and implementation. Details live in [the pipeline reference](references/pipeline-phases.md).

The graph is the release gate behind **Check**:

```bash
python3 scripts/skill_graph.py run ./the-skill/ --jobs 4
```

The two requirements have technical identifiers for automation.
`every_expected_is_reachable` prevents an expected output from sitting in the package
without participating in an evaluation. `deterministic_multistep_has_orchestrator`
requires a predictable multi-step skill to expose one reliable
`scripts/run_pipeline.py` entry point. Unchanged check results are reused by content
hash.

## What you receive

Every generated skill includes:

- A focused `SKILL.md` and companion `AGENTS.md`.
- Functional scripts with one pipeline entry point when the workflow is sequential.
- Golden examples and regression checks, unless explicitly disabled with `--no-eval`.
- Validation, dependency, staleness, and correction tooling.
- A private local success ledger that measures verified creation, reuse, recovery,
  and durable activity without storing skill names or workflow content.
- Native installation support across 17 agent tools.

Generated skills use the Agent Skills Open Standard and invoke as `/skill-name` on
tools that support slash commands.

Inspect product success locally:

```bash
python3 scripts/success_ledger.py summary
```

The ledger has no network transport. Read the [event schema, privacy boundary, and
metric formulas](references/product-success.md), or set `ASC_SUCCESS_LEDGER=off` to
disable recording.

## Why the checks matter

The creator blocks delivery when required structure, pipeline compilation, declared
dependencies, or security checks fail. It scans for hardcoded secrets, dangerous code
patterns, prompt-injection indicators, hidden Unicode, encoded blobs, and undeclared
network endpoints.

**A clean scan is not proof of safety.** It means no known scanner pattern matched.
Skills execute with your filesystem access and available credentials, so imported
skills still require ordinary software-dependency judgment.

Audit a skill you did not create:

```text
/agent-skill-creator --audit ./downloaded-skill/
```

The audit reports what the skill reads, writes, and reaches; instruction-body risks;
and whether the code matches its description. A high-severity finding blocks install.
See [the skill-audit reference](references/skill-audit.md).

## Runnable examples

| Skill | Example request | Verified output |
|---|---|---|
| [weekly-crm-report](references/examples/weekly-crm-report/) | “Clean this CRM export and total sales by region” | Deduplicated regional totals |
| [pr-blocker-summarizer](references/examples/pr-blocker-summarizer/) | “Summarize my open PRs, blockers first” | Standup-ready blocker digest |
| [stock-analyzer](references/examples/stock-analyzer/) | “Analyze AAPL with RSI and MACD” | Indicators and a reasoned signal |

Try the smallest example without installing the creator:

```bash
git clone https://github.com/FrancyJGLisboa/agent-skill-creator
cd agent-skill-creator/references/examples/weekly-crm-report
python3 scripts/run_pipeline.py --input evals/golden/case-1/input.csv --output /tmp/summary.json
python3 scripts/run_evals.py --rollout
```

## Governed team marketplace

Follow the [complete marketplace timeline](docs/TEAM_MARKETPLACE.md) for every
command in operational order: prerequisites, initialization, GitHub protection,
skill intake, review, release, installation, update, rollback, and correction.

Create a central GitHub or GitLab repository for department-owned skills, reviewed
bundles, and version-pinned installs in VS Code Copilot Agent Mode:

```bash
python3 scripts/team_marketplace.py init \
  --name "ACME Skills" \
  --repository ACME/acme-skills \
  --marketplace ./acme-skills

python3 scripts/team_marketplace.py add ./report-skill \
  --department finance \
  --bundle analyst-starter \
  --marketplace ./acme-skills
```

The generated repository includes `registry.json` schema v2, departmental skill
paths, bundle manifests, `CATALOG.md`, `CODEOWNERS`, governance instructions, and
provider-native CI. Add `--provider gitlab` and, for self-managed instances,
`--host gitlab.acme.test` during `init`. `add` blocks failed validation,
security, pipeline, or eval gates. It also rejects path traversal, duplicate skill
identities, undeclared network endpoints, embedded secrets, instruction injection,
and pre-approved `shell` or `bash` access.

Install an approved bundle at an immutable release:

```bash
python3 scripts/team_marketplace.py install \
  --bundle analyst-starter \
  --scope user \
  --pin v1.2.0 \
  --marketplace ./acme-skills
```

Use `--scope project` for a repository-local install. Update by installing a newer
tag; roll back by reinstalling the previous tag with `--force`. GitHub uses exact
`gh skill install` paths. GitLab clones the exact protected tag and copies the
bundle into Copilot's user or project skill directory.

The [complete marketplace timeline](docs/TEAM_MARKETPLACE.md) is the canonical
operator page. The [distribution reference](references/distribution-guide.md#governed-github-copilot-marketplace)
contains the factory's internal routing and fallback behavior.

GitLab teams use the first-class [GitLab marketplace backend](docs/GITLAB_TEAM_REGISTRY.md),
including generated GitLab CI, `glab` releases, schema-v2 bundles, nested groups,
self-managed hosts, and pinned copy-based Copilot installation.

## Advanced capabilities

- [MCP capability audit](references/mcp-audit.md): map a vendor MCP server into buildable and missing skill opportunities.
- [Cross-platform export](references/export-guide.md): adapt an existing skill for supported tools.
- [Multi-agent suites](references/multi-agent-guide.md): create coordinated skills for genuinely distinct workflows.
- [Team distribution](references/distribution-guide.md): choose the governed Copilot marketplace or lightweight cross-Git registry.
- [Eval and evolution](references/phase2-eval-assessment.md): inspect golden cases, rollouts, holdouts, judges, and model comparisons.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md), then run:

```bash
uv run pytest scripts/tests/ -q
uv run ruff check --target-version py310
```

Changes to installation scripts must preserve Bash/PowerShell parity. Changes to the
factory contract must keep `SKILL.md`, the pipeline, interactive guidance, distribution
guidance, README, and website aligned.

## License

MIT — see [LICENSE](LICENSE).
