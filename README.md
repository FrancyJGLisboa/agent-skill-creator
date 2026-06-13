# Agent Skill Creator

**Turn any workflow into reusable AI agent software that installs on 17 platforms — no spec writing, no prompt engineering, no coding required.**

[![CI](https://github.com/FrancyJGLisboa/agent-skill-creator/actions/workflows/ci.yml/badge.svg)](https://github.com/FrancyJGLisboa/agent-skill-creator/actions/workflows/ci.yml)
[![Agent Skills Open Standard](https://img.shields.io/badge/Agent%20Skills-Open%20Standard-blue)](https://github.com/anthropics/agent-skills-spec)
[![Platforms](https://img.shields.io/badge/installs%20on-17%20platforms-7c3aed)](#all-platforms)
[![Version](https://img.shields.io/badge/version-6.0.0-brightgreen)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)]()

<p align="center">
  <img src="assets/demo.gif" alt="A real run of a generated skill's quality gates: validate → security scan → eval rollout, all passing." width="820">
</p>

<!-- demo.gif is built from assets/demo.cast (see assets/DEMO.md). hero.svg is the static flow diagram, linked below as the conceptual overview / fallback. -->
<p align="center"><em>Genuine output from a real run — <code>validate</code> → <code>security_scan</code> → eval <code>--rollout</code> on a generated skill (paced for readability). <a href="assets/hero.svg">See the flow diagram</a>.</em></p>

**What you get:** describe a workflow in plain English (or hand over a PDF, a link, a script) → a complete, **validated and security-scanned** agent skill, with functional code, its own **eval spec**, and a cross-platform installer → the same skill running on **Claude Code, Cursor, Copilot, Gemini, Windsurf, and 12 more** with one command.

---

## Quick start

```bash
# macOS / Linux — paste into Terminal
curl -fsSL https://raw.githubusercontent.com/FrancyJGLisboa/agent-skill-creator/main/scripts/bootstrap.sh | sh
```

Then open your AI tool and describe what you do:

```
/agent-skill-creator Every Friday I clean the CRM export, calculate regional
totals, and email a PDF sales report.
```

…and watch it build the skill end to end:

```
▸ Phase 1  Discovery     ▸ Phase 4  Detection
▸ Phase 2  Design+evals   ▸ Phase 5  Build · validate · security-scan
▸ Phase 3  Architecture

✓ weekly-crm-report-skill  (12 files, evals, installer)
  installed on Claude Code, Cursor, Gemini CLI

Use it:  /weekly-crm-report-skill data/crm-export.csv
  → report.pdf   → dashboard.html
```

No clone, no `pip`, no API key to get started — just `git` and any one of 17 supported tools. Windows one-liners and single-tool installs are in [Advanced Install](#advanced-install).

---

## Why this vs. the alternatives

|                              | **Agent Skill Creator** | Hand-writing a `SKILL.md` | Anthropic's `skill-creator` |
|------------------------------|:-----------------------:|:-------------------------:|:---------------------------:|
| Time to a working skill      | ~minutes, one prompt    | hours of spec + iteration | minutes (interactive Q&A)   |
| Coding required              | none — it writes the code | yes                     | some                        |
| Cross-platform install       | **17 platforms**, auto-detected + format adapters | one tool, by hand | Claude-focused |
| Built-in validation + security scan | yes (hard gates)  | manual                    | partial                     |
| Ships an **eval spec** (regression metric) | yes, per skill | no               | no                          |
| Optimizable (autoresearch handoff) | yes               | no                        | no                          |
| Input you can hand it        | prose, PDF, URL, code, transcript | you write it from scratch | guided prompts |

Anthropic's `skill-creator` is excellent for authoring a Claude skill interactively. This is for turning **whatever you already have** into a validated skill that installs **everywhere**, with the testing and security gates wired in.

---

## Examples

Three runnable example skills ship in [`references/examples/`](references/examples/). Each one passes the same gates the creator applies to your skills — `validate.py`, `check_pipeline.py`, and its own bundled eval spec (`run_evals.py --rollout`):

| Skill | You'd say… | It produces |
|-------|-----------|-------------|
| [**weekly-crm-report**](references/examples/weekly-crm-report/) | "clean this CRM export and total sales by region" | a deduped regional-totals JSON summary |
| [**pr-blocker-summarizer**](references/examples/pr-blocker-summarizer/) | "summarize my open PRs, blockers first" | a standup digest: blocked vs. ready, one-line count |
| [**stock-analyzer**](references/examples/stock-analyzer/) | "analyze AAPL with RSI and MACD" | indicators + a buy/sell/hold signal with reasoning |

Try one without installing anything:

```bash
git clone https://github.com/FrancyJGLisboa/agent-skill-creator
cd agent-skill-creator/references/examples/weekly-crm-report
python3 scripts/run_pipeline.py --input evals/golden/case-1/input.csv --output /tmp/summary.json
python3 scripts/run_evals.py --rollout      # runs the skill on its golden inputs and scores them
```

---

## The Problem

Every AI coding tool — Claude Code, GitHub Copilot, Cursor, Windsurf, Codex, Gemini, Kiro, and more — starts from zero. It doesn't know your company's processes, data sources, or compliance requirements. So every person re-explains the same workflows in every conversation. Knowledge stays in individual chat histories. New hires start from scratch.

**Agent skills fix this.** A skill is structured knowledge your agent loads automatically — like installing an app. Once installed, anyone on your team can invoke it and get consistent results, every time, on any platform.

**The catch:** building a proper skill requires understanding the spec format, writing clear prompt instructions, designing how information loads progressively, writing functional code, and getting activation keywords right. Even simple skills take [multiple rounds of iteration](https://www.youtube.com/watch?v=izJkgLqlbN8) to get right.

**Agent Skill Creator removes that barrier entirely.** You pass in whatever you have — messy docs, links, code, PDFs, transcripts, vague descriptions — and it produces a validated, security-scanned skill ready to install on 17 platforms and share with your team. You describe what you do; it builds the software.

---

## Install & first skill — in detail

### 1. Install

The macOS/Linux one-liner is in [Quick start](#quick-start) above. Windows:

**Windows (PowerShell):**

```powershell
irm https://raw.githubusercontent.com/FrancyJGLisboa/agent-skill-creator/main/scripts/bootstrap.ps1 | iex
```

**Windows (Command Prompt):**

```cmd
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/FrancyJGLisboa/agent-skill-creator/main/scripts/bootstrap.ps1 | iex"
```

The installer clones to `~/.agents/skills/agent-skill-creator` and links to every detected platform (Claude Code, Copilot, Gemini CLI, Kiro, Cline, Roo Code, Kilo Code, Factory Droid, Cursor, Goose, OpenCode). To update later, run `cd ~/.agents/skills/agent-skill-creator && git pull`.

> **Advanced:** Want to install to a single tool, or already have a local clone? See [Advanced Install](#advanced-install) below.

### 2. Use it

Open your agent and type `/agent-skill-creator` followed by whatever you have:

```
/agent-skill-creator Every week I pull sales data from our CRM, clean
duplicate entries, calculate regional totals, and generate a PDF report.
```

You can pass anything — plain English, documentation links, existing code, API docs, PDFs, database schemas, transcripts. Combine multiple sources in one message. The more context, the better the result.

```
/agent-skill-creator Based on our deployment runbook: https://wiki.internal/deploy-process
```

```
/agent-skill-creator See scripts/invoice_processor.py — turn it into a reusable skill
```

### 3. What comes out

A complete skill, automatically installed on your platform:

```
Skill installed successfully.

To use it, open a new session and type:

  /sales-report-skill Generate the weekly report for the West region

Installed at: ~/.claude/skills/sales-report-skill
```

The agent detects your platform, installs the skill to the right location, and tells you exactly how to invoke it. No manual steps.

The generated skill includes a cross-platform installer (`install.sh`) that auto-detects all 17 supported platforms, generates format adapters for Cursor (.mdc), Windsurf (.md rules), and Junie (guidelines.md) automatically, and creates a universal `~/.agents/skills/` symlink so the skill is discoverable by multiple tools at once.

```
sales-report-skill/
├── SKILL.md          # Skill definition (activates with /sales-report-skill)
├── AGENTS.md         # Companion file (read by many tools for cross-tool reach)
├── scripts/          # Functional Python code
├── references/       # Detailed documentation
├── assets/           # Templates, configs
├── install.sh        # Cross-platform installer (17 platforms, format adapters, --all flag)
└── README.md         # Installation instructions
```

Your team installs it the same way — one `git clone` to their tool's path — and invokes it with `/sales-report-skill`.

---

## What's new

**v6 — Artifacts.** Skills can emit **interactive React artifacts** in Claude Code (and Claude.ai). When output is visualizable — time series, comparisons, KPIs, tables — Phase 2 inlines one of four bundled React templates plus the artifact protocol into the generated SKILL.md; you write no React. In hosts that don't render artifacts (Cursor, Cline, Codex CLI, Gemini CLI) the source appears as fenced code and the markdown analysis is unchanged — honest degradation. Suppress with `--no-artifact`; force a template with `--artifact <line-chart|bar-chart|kpi-cards|data-table>`. ([design notes](docs/superpowers/specs/2026-05-27-agent-skill-creator-v5-artifacts-first-design.md))

**Every skill ships its own metric.** Each generated skill carries an **eval spec** (`evals/<name>.eval.md`) plus a `scripts/run_evals.py` runner. In Phase 2 the creator derives 3–6 **binary** checks and ≥3 golden cases (seeded from your own files); you give a one-word thumbs-up. It's an instant regression test — `python3 scripts/run_evals.py` exits non-zero on failure, so it drops into CI. With a declared `run` command, `run_evals.py --rollout` executes the skill on each golden input and scores the real output (`--rollout --promote` captures the first passing baseline). The spec is consumable by `autoresearch-universal` for optimization with no reformatting. *Honest limits:* `--rollout` is opt-in (it runs arbitrary skill code), and `llm-judge` checks print as a checklist rather than being auto-graded. On by default; skip with `--no-eval`.

---

## How It Works

You don't need to understand any of this to use it. But if you're curious:

The agent doesn't just follow your description literally. Humans describe what they *do*, not what they *need*. "I pull sales data and make a report" hides a dozen implicit requirements — who reads the report, what format, what happens when data is missing. The agent reads all your material, uncovers these implicit requirements, and generates its own internal specification before writing any code. It builds from that deeper understanding, not from your surface description.

```
UNDERSTAND    Read all material → uncover real intent → generate internal spec
BUILD         Structure directory → write code and docs → craft activation keywords
VERIFY        Spec validation → security scan → block delivery if either fails
```

Every skill is automatically validated (correct structure, naming, metadata) and security-scanned (no hardcoded keys, no credential exposure, no injection risks) before delivery. Skills that fail these checks are blocked.

---

## Share Skills Across Your Team

After the agent builds and installs your skill, it asks:

```
Want to share this skill with your team so they can install it too?
```

Say yes. The agent detects whether your team uses GitHub or GitLab, creates a repo, pushes the skill, and gives you a one-liner to share:

```
Shared! Your colleagues can install it by pasting this in their terminal:

  git clone https://github.com/your-org/sales-report-skill.git ~/.agents/skills/sales-report-skill
```

One `git clone` to `~/.agents/skills/` makes it available on Codex CLI, Gemini CLI, Kiro, and Antigravity simultaneously. For Claude Code users: `~/.claude/skills/sales-report-skill`. For Cursor: `.cursor/rules/sales-report-skill`.

Send that line to your colleague on Slack or Teams. They paste it. Done. They can now type `/sales-report-skill` in their agent.

No registry commands, no publishing steps, no terminal knowledge beyond paste. The agent handles the repo creation, the push, and generates install commands for every platform.

### The result over time

Each team member creates skills from their own domain and shares them. Over months the organization accumulates a library of reusable skills:

- Sales team shares `/sales-report-skill`
- Engineering shares `/deploy-checklist-skill`
- Legal shares `/quarterly-compliance-skill`
- Data science shares `/customer-churn-skill`
- SRE shares `/incident-runbook-skill`

Any colleague installs any skill with one `git clone`. Any agent on any platform can invoke it. Knowledge compounds instead of evaporating.

### For teams and consultants: the skill registry

When an organization has more than a few skills, the agent offers to set up a **team skill registry** — a shared git repo where all team members publish their skills and anyone can browse and install them.

The consultant (or team lead) sets it up once:

```bash
python3 scripts/skill_registry.py init --name "Acme Corp Skills"
```

Then every team member can:

```bash
# Publish a skill they created
python3 scripts/skill_registry.py publish ./sales-report-skill/ --tags sales,reports

# Browse what's available
python3 scripts/skill_registry.py list

# Search for a specific skill
python3 scripts/skill_registry.py search "sales"

# Install a colleague's skill (auto-detects platform)
python3 scripts/skill_registry.py install sales-report-skill
```

The registry is a git repo on GitHub or GitLab. Clone it once, and every team member can publish and install. No servers, no databases — just git.

**For AI consultants:** The engagement model is teach, not build. Install agent-skill-creator on each team member's machine, create the shared `{team}-skills-registry` repo, teach the team the 5-step workflow (install, clone registry, create skill, publish, install from registry), and hand over a self-sustaining system. After you leave, the team keeps creating and sharing skills on their own. They know their workflows better than you do — your job is to remove the friction.

---

## Advanced Install

If you prefer to install to a single tool, or you already cloned the repo:

**Clone to a specific tool:**

```bash
# Claude Code
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git ~/.claude/skills/agent-skill-creator

# GitHub Copilot
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git ~/.copilot/skills/agent-skill-creator

# Gemini CLI
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git ~/.gemini/skills/agent-skill-creator

# Cursor (per-project — no global path)
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git .cursor/skills/agent-skill-creator

# Universal path (Codex CLI, OpenCode, Goose, and others)
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git ~/.agents/skills/agent-skill-creator
```

**Already cloned? Link to all tools:**

macOS / Linux:
```bash
cd agent-skill-creator
./install.sh              # Link to all detected platforms
./install.sh --dry-run    # Preview without changes
./install.sh --uninstall  # Remove all links
```

Windows (PowerShell):
```powershell
cd agent-skill-creator
.\install.ps1              # Link to all detected platforms
.\install.ps1 -DryRun     # Preview without changes
.\install.ps1 -Uninstall  # Remove all links
```

See the full platform table below for every supported tool and path.

---

## All Platforms

17 platforms supported. Same skill, same invocation, same results everywhere.

### How it works

Every generated skill outputs both **SKILL.md** (~15 tools read it natively) and **AGENTS.md** (~15 tools read it) to maximize reach. Tools in **Tier 2** need format conversion — the installer handles it automatically.

| Tier | Platforms | What happens |
|------|-----------|-------------|
| **Tier 1 — Native SKILL.md** | Claude Code, Copilot, Codex CLI, Gemini CLI, Kiro, Cline, Roo Code, Kilo Code, Goose, OpenCode, Factory Droid, Antigravity | Reads SKILL.md directly |
| **Tier 2 — Auto-adapted** | Cursor, Windsurf, Trae, Junie | Installer converts SKILL.md to native format (.mdc, .md rules, guidelines) |
| **Tier 3 — Manual** | Zed, Augment, Aider, Continue.dev | Copy skill body into tool's config file |

### Global install (each tool's native path)

```bash
# Claude Code
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git ~/.claude/skills/agent-skill-creator

# GitHub Copilot
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git ~/.copilot/skills/agent-skill-creator

# Gemini CLI
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git ~/.gemini/skills/agent-skill-creator

# Kiro
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git ~/.kiro/skills/agent-skill-creator

# Cline
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git ~/.cline/skills/agent-skill-creator

# Roo Code
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git ~/.roo/skills/agent-skill-creator

# Kilo Code
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git ~/.kilocode/skills/agent-skill-creator

# Factory Droid
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git ~/.factory/skills/agent-skill-creator

# Goose
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git ~/.config/goose/skills/agent-skill-creator

# OpenCode
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git ~/.config/opencode/skills/agent-skill-creator

# Codex CLI / universal path (read by 7+ tools as fallback)
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git ~/.agents/skills/agent-skill-creator
```

Use each tool's own native path. The universal `~/.agents/skills/` path works as a fallback for Codex CLI, Gemini CLI, OpenCode, Goose, Cline, Roo Code, and Kilo Code.

### Per-project install

```bash
# GitHub Copilot
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git .github/skills/agent-skill-creator

# Cursor (project only — no global path exists)
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git .cursor/skills/agent-skill-creator

# Windsurf
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git .windsurf/rules/agent-skill-creator

# Cline
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git .clinerules/skills/agent-skill-creator

# Kiro
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git .kiro/skills/agent-skill-creator

# Trae
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git .trae/rules/agent-skill-creator

# Roo Code
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git .roo/skills/agent-skill-creator

# Kilo Code
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git .kilocode/skills/agent-skill-creator

# Junie (JetBrains)
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git .junie/skills/agent-skill-creator

# Antigravity (note: .agent/ singular, NOT .agents/)
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git .agent/skills/agent-skill-creator
```

### Cursor — global workaround

Cursor has no global skills directory. Clone once and symlink per project:

```bash
# 1. Clone once
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git ~/agent-skills/agent-skill-creator

# 2. In any project, symlink
mkdir -p .cursor/rules && ln -s ~/agent-skills/agent-skill-creator .cursor/rules/agent-skill-creator
```

Add a shell alias to automate this (`~/.zshrc` or `~/.bashrc`):

```bash
alias install-skills='mkdir -p .cursor/rules && ln -s ~/agent-skills/agent-skill-creator .cursor/rules/agent-skill-creator'
```

Then in any project: `install-skills`. Updates propagate automatically via the symlink.

### Using the installer (for generated skills)

Every skill generated by agent-skill-creator includes a cross-platform installer — both `install.sh` (macOS/Linux) and `install.ps1` (Windows):

**macOS / Linux:**

```bash
./install.sh                          # Auto-detect platform
./install.sh --platform cursor        # Force specific platform (auto-generates .mdc)
./install.sh --all                    # Install to every detected tool at once
./install.sh --dry-run                # Preview without installing
```

**Windows (PowerShell):**

```powershell
.\install.ps1                          # Auto-detect platform
.\install.ps1 -Platform cursor         # Force specific platform
.\install.ps1 -All                     # Install to every detected tool at once
.\install.ps1 -DryRun                  # Preview without installing
```

Both installers handle all 17 platforms and create a universal `~/.agents/skills/` link after every install for cross-tool discoverability.

### Claude Desktop / claude.ai

```bash
python3 scripts/export_utils.py ./agent-skill-creator/ --variant desktop
# Then: Settings > Skills > Upload the generated .zip
```

### Update

```bash
cd ~/.agents/skills/agent-skill-creator && git pull
```

If you used the one-liner (Option A) or `./install.sh` (Option C), all symlinks update automatically — just `git pull` once from the canonical location. The skill also performs a silent git-based version check when loaded and will mention if a newer version is available.

---

## Quality Gates

Every skill goes through automated checks before delivery and on every publish:

| Gate | What It Checks |
|------|---------------|
| **Spec Validation** | SKILL.md structure, frontmatter format, naming rules, file references |
| **Security Scan** | No hardcoded API keys, no credentials, no injection patterns |
| **Staleness Check** | Review dates, dependency health, API schema drift |

Run them independently anytime:

```bash
python3 scripts/validate.py ./my-skill/
python3 scripts/security_scan.py ./my-skill/
python3 scripts/staleness_check.py ./my-skill/
python3 scripts/staleness_check.py ./my-skill/ --check-deps --check-drift
```

Skills that fail validation cannot be published. On publish, high-severity security issues block the skill (override with `--force`). On export, findings are reported but don't block by default — pass `--strict` to fail the export on any high-severity issue.

---

## Staleness Detection

Skills go stale. APIs change, compliance rules update, data sources move. A skill that worked six months ago may silently produce wrong results today. Staleness detection surfaces this before users hit it.

Three layers, each opt-in:

**Review tracking** — Every skill can declare when it was last reviewed and how often it should be. The staleness checker compares these dates and flags overdue skills. Skills without explicit dates fall back to the last git commit date on SKILL.md.

```bash
python3 scripts/staleness_check.py ./my-skill/
# Exit code 0 = fresh, 1 = overdue for review
```

**Dependency health** — Skills can declare external URLs they depend on (APIs, data sources). The `--check-deps` flag HTTP-checks each one and reports failures.

```bash
python3 scripts/staleness_check.py ./my-skill/ --check-deps
# Exit code 2 = one or more dependencies unreachable
```

**Schema drift** — Skills can declare the expected top-level keys in API responses. The `--check-drift` flag fetches each endpoint and compares actual keys against expected. Missing keys = the API changed under you.

```bash
python3 scripts/staleness_check.py ./my-skill/ --check-drift
```

All three layers are controlled by optional frontmatter fields. Existing skills work unchanged — the tool just suggests adding the metadata:

```yaml
metadata:
  created: 2026-02-27
  last_reviewed: 2026-02-27
  review_interval_days: 90
  dependencies:
    - url: https://api.example.com/v1
      name: Example API
      type: api
  schema_expectations:
    - url: https://api.example.com/v1/data
      method: GET
      expected_keys:
        - id
        - price
        - volume
```

For teams using the skill registry, `stale` scans every published skill at once:

```bash
python3 scripts/skill_registry.py stale
# NAME            VERSION  STATUS   DAYS SINCE  SOURCE          INTERVAL
# sales-report    1.2.0    OVERDUE  127         last_reviewed   90
# deploy-check    2.0.1    FRESH    12          published       90
```

---

## Tools Reference

### Registry Commands

```bash
python3 scripts/skill_registry.py init --name "Acme Corp Skills"     # First-time setup
python3 scripts/skill_registry.py publish ./skill/ --tags t1,t2      # Publish a skill
python3 scripts/skill_registry.py list                                # Browse all skills
python3 scripts/skill_registry.py search "query"                     # Search skills
python3 scripts/skill_registry.py info skill-name                    # Skill details
python3 scripts/skill_registry.py install skill-name                 # Install a skill
python3 scripts/skill_registry.py install skill-name --author alice  # Disambiguate a shared name
python3 scripts/skill_registry.py remove skill-name --force          # Remove a skill
python3 scripts/skill_registry.py stale                              # Report stale skills
python3 scripts/skill_registry.py stale --json                       # Machine-readable output
```

### Validation, Security, and Staleness

```bash
python3 scripts/validate.py ./skill/               # Spec compliance
python3 scripts/validate.py ./skill/ --json         # Machine-readable output
python3 scripts/security_scan.py ./skill/           # Security audit
python3 scripts/security_scan.py ./skill/ --json    # Machine-readable output
python3 scripts/staleness_check.py ./skill/                      # Review staleness
python3 scripts/staleness_check.py ./skill/ --check-deps         # + dependency health
python3 scripts/staleness_check.py ./skill/ --check-drift        # + schema drift
python3 scripts/staleness_check.py ./skill/ --json               # Machine-readable output
```

### Install Any Skill (Universal Installer)

**macOS / Linux:**

```bash
# From git URL
./scripts/install-skill.sh https://github.com/someone/sales-report-skill.git

# From local path
./scripts/install-skill.sh ./sales-report-skill

# To a specific platform only
./scripts/install-skill.sh ./sales-report-skill --platform cursor --project

# Preview / remove
./scripts/install-skill.sh ./sales-report-skill --dry-run
./scripts/install-skill.sh ./sales-report-skill --uninstall
```

**Windows (PowerShell):**

```powershell
# From git URL
.\scripts\install-skill.ps1 https://github.com/someone/sales-report-skill.git

# From local path
.\scripts\install-skill.ps1 .\sales-report-skill

# To a specific platform only
.\scripts\install-skill.ps1 .\sales-report-skill -Platform cursor -Project

# Preview / remove
.\scripts\install-skill.ps1 .\sales-report-skill -DryRun
.\scripts\install-skill.ps1 .\sales-report-skill -Uninstall
```

### Export

```bash
python3 scripts/export_utils.py ./skill/ --variant desktop    # For Claude Desktop
python3 scripts/export_utils.py ./skill/ --variant api        # For Claude API
python3 scripts/export_utils.py ./skill/ --strict             # Block export on high-severity findings
```

All commands use exit code `0` for success, `1` for errors. All support `--json` for CI/CD integration.

---

## Troubleshooting

**Skill not activating**: Check that the SKILL.md `description` field contains keywords matching your query. The description is how the agent decides when to activate the skill.

**Validation fails on name**: Names must be lowercase, use hyphens between words, 1-64 characters. Examples: `sales-report-skill`, `deploy-checklist`.

**SKILL.md too long**: Move detailed content to `references/` files and link from the main SKILL.md.

**Platform not auto-detected**: Use `--platform cursor` (or copilot, windsurf, codex, gemini, kiro, trae, goose, opencode, roo-code, kilo-code, factory, junie, cline, antigravity, universal) to specify explicitly.

**Install to all tools at once**: Inside a generated skill, use `./install.sh --all` (macOS/Linux) or `.\install.ps1 -All` (Windows) to install to every detected platform in one command.

---

## Project Structure

```
agent-skill-creator/
  SKILL.md                      # The skill definition (what the agent reads)
  README.md                     # This file
  CONTRIBUTING.md               # How to contribute (incl. adding a platform)
  CODE_OF_CONDUCT.md            # Contributor Covenant
  CHANGELOG.md                  # Version history
  LICENSE                       # MIT
  install.sh / install.ps1      # Self-installer for cloned repos (macOS/Linux, Windows)
  scripts/
    bootstrap.sh / .ps1 / .bat  # One-liner bootstrap (macOS/Linux, PowerShell, cmd)
    install-skill.sh / .ps1     # Universal skill installer
    install-template.sh / .ps1  # Template for generated skills' installers
    platforms.py                # Canonical 17-platform registry (single source of truth)
    validate.py                 # SKILL.md spec compliance checker
    security_scan.py            # Secret / injection scanner
    check_pipeline.py           # Verifies generated scripts compile + declare deps
    export_utils.py             # Cross-platform export (desktop / API packages)
    skill_registry.py           # Git-based team skill registry
    skill_document.py           # SKILL.md parser (shared by the tools above)
    run_evals_template.py       # Eval runner bundled into generated skills
    staleness_check.py          # Staleness: review dates, deps, schema drift
    dependency_health.py        # API dependency reachability check
    schema_drift.py             # API schema drift detection
    review_staleness.py         # Review-date staleness logic
    artifact_detector.py        # Picks a React artifact shape for a skill
    tests/                      # pytest suite (CI runs this)
  references/                   # Detailed docs (loaded by the agent on demand)
    pipeline-phases.md          # Full 5-phase creation pipeline
    architecture-guide.md       # Skill structure decisions
    quality-standards.md        # Code and documentation standards
    multi-agent-guide.md        # Multi-skill suite creation
    cross-platform-guide.md     # Platform compatibility (tiers, adapters, paths)
    export-guide.md             # Export documentation
    templates-guide.md          # Template system (blueprints)
    interactive-mode.md         # Interactive wizard
    agentdb-integration.md      # Learning system
    phase2-eval-assessment.md      # Eval-spec design reference
    phase2-artifact-assessment.md  # Artifact-detection reference
    phase4-detection.md         # Detection & keyword-design craft reference
    phase5-orchestration.md     # run_pipeline.py orchestration reference
    claude-artifact-format.md   # Artifact emission protocol
    artifact-templates/         # React artifact templates
    templates/                  # Skill templates (activation README template)
    examples/                   # Three runnable example skills
      weekly-crm-report/
      pr-blocker-summarizer/
      stock-analyzer/
  registry/                     # Shared skill catalog
    registry.json
    skills/
  exports/                      # Export output
```

---

## Contributing

Contributions are welcome — see **[CONTRIBUTING.md](CONTRIBUTING.md)** for the
workflow, local checks, and a step-by-step guide to **adding a new platform**.
By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

The short version: fork, branch, make your change, run `uv run pytest
scripts/tests/` plus `python3 scripts/validate.py ./` and
`python3 scripts/security_scan.py ./`, then open a PR.

---

## License

MIT

---

## Links

- [Agent Skills Open Standard](https://github.com/anthropics/agent-skills-spec)
- [What are Claude Skills? (video)](https://www.youtube.com/watch?v=izJkgLqlbN8)
- [Cross-Platform Guide](references/cross-platform-guide.md)
- [Architecture Guide](references/architecture-guide.md)
- [Pipeline Phases](references/pipeline-phases.md)
- [Export Guide](references/export-guide.md)
