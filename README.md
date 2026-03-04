# Agent Skill Creator

**Turn any workflow into reusable AI agent software that installs on 14+ tools — no spec writing, no prompt engineering, no coding required.**

[![Agent Skills Open Standard](https://img.shields.io/badge/Agent%20Skills-Open%20Standard-blue)](https://github.com/anthropics/agent-skills-spec)
[![Version](https://img.shields.io/badge/version-5.0.0-brightgreen)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)]()

![Agent Skill Creator Overview](Dynamous/agentskillimage.png)

---

## The Problem

Every AI coding tool — Claude Code, GitHub Copilot, Cursor, Windsurf, Codex, Gemini, Kiro, and more — starts from zero. It doesn't know your company's processes, data sources, or compliance requirements. So every person re-explains the same workflows in every conversation. Knowledge stays in individual chat histories. New hires start from scratch.

**Agent skills fix this.** A skill is structured knowledge your agent loads automatically — like installing an app. Once installed, anyone on your team can invoke it and get consistent results, every time, on any platform.

**The catch:** building a proper skill requires understanding the spec format, writing clear prompt instructions, designing how information loads progressively, writing functional code, and getting activation keywords right. Even simple skills take [multiple rounds of iteration](https://www.youtube.com/watch?v=izJkgLqlbN8) to get right.

**Agent Skill Creator removes that barrier entirely.** You pass in whatever you have — messy docs, links, code, PDFs, transcripts, vague descriptions — and it produces a validated, security-scanned skill ready to install on 14+ tools and share with your team. You describe what you do; it builds the software.

---

## Quick Start

### 1. Install

**Option A — One-liner (installs to all detected tools):**

```bash
curl -fsSL https://raw.githubusercontent.com/FrancyJGLisboa/agent-skill-creator/main/scripts/bootstrap.sh | sh
```

This clones to `~/.agents/skills/agent-skill-creator` and symlinks to every detected global platform (Claude Code, Gemini CLI, Goose, OpenCode, Copilot). Run `git pull` once to update everywhere.

**Option B — Git clone (pick your tool):**

```bash
# Claude Code / VS Code Copilot (global — works in all projects)
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git ~/.claude/skills/agent-skill-creator

# Cursor (per-project)
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git .cursor/rules/agent-skill-creator

# Codex CLI / Gemini CLI / Kiro / Antigravity (universal path)
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git ~/.agents/skills/agent-skill-creator
```

**Option C — Already cloned? Symlink to all tools:**

```bash
cd agent-skill-creator
./install.sh              # Symlink to all detected platforms
./install.sh --dry-run    # Preview without changes
./install.sh --uninstall  # Remove all symlinks
```

One install at `~/.claude/skills/` works for both Claude Code and VS Code Copilot. One install at `~/.agents/skills/` works for Codex CLI, Gemini CLI, Kiro, Antigravity, and other tools that read the universal path.

All 14 platforms: [see full list below](#all-platforms).

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

The generated skill includes a cross-platform installer (`install.sh`) that auto-detects all 14 supported tools, generates format adapters for Cursor (.mdc) and Windsurf (.md rules) automatically, and creates a universal `~/.agents/skills/` symlink so the skill is discoverable by multiple tools at once.

```
sales-report-skill/
├── SKILL.md          # Skill definition (activates with /sales-report-skill)
├── scripts/          # Functional Python code
├── references/       # Detailed documentation
├── assets/           # Templates, configs
├── install.sh        # Cross-platform installer (14 tools, format adapters, --all flag)
└── README.md         # Installation instructions
```

Your team installs it the same way — one `git clone` to their tool's path — and invokes it with `/sales-report-skill`.

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

## All Platforms

14 tools supported. Same skill, same invocation, same results everywhere.

### How it works

Skills are authored as **SKILL.md** (the open standard). Tools in **Tier 1** read SKILL.md natively. Tools in **Tier 2** need a different format — the installer auto-generates it (`.mdc` for Cursor, `.md` rules for Windsurf, plain markdown for Cline/Roo/Trae). You never deal with format conversion.

| Tier | Platforms | What happens |
|------|-----------|-------------|
| **Tier 1 — Native** | Claude Code, Copilot, Codex CLI, Gemini CLI, Kiro, Antigravity, Goose, OpenCode | Reads SKILL.md directly |
| **Tier 2 — Auto-adapted** | Cursor, Windsurf, Cline, Roo Code, Trae | Installer converts SKILL.md to native format |
| **Tier 3 — Manual** | Zed, Junie, Aider | Copy skill body into tool's config file |

### Universal path (`~/.agents/skills/`)

The emerging cross-tool convention. One install, multiple tools discover it automatically:

```bash
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git ~/.agents/skills/agent-skill-creator
```

Tools that read this path today: **Codex CLI, Gemini CLI, Kiro, Antigravity** — and growing.

### Global install (one install, all projects)

```bash
# Claude Code + VS Code Copilot (shared path — one install works for both)
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git ~/.claude/skills/agent-skill-creator

# Gemini CLI
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git ~/.gemini/skills/agent-skill-creator

# Goose
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git ~/.config/goose/skills/agent-skill-creator

# OpenCode
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git ~/.config/opencode/skills/agent-skill-creator
```

VS Code Copilot (1.108+) adopted the [Agent Skills Open Standard](https://code.visualstudio.com/docs/copilot/customization/agent-skills) and searches `~/.claude/skills/` by default. One install makes a skill globally available on both Claude Code and VS Code Copilot.

### Per-project install

```bash
# Copilot (per-project alternative)
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git .github/skills/agent-skill-creator

# Cursor (auto-generates .mdc)
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git .cursor/rules/agent-skill-creator

# Windsurf (auto-generates .md rule)
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git .windsurf/rules/agent-skill-creator

# Cline
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git .clinerules/agent-skill-creator

# Kiro
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git .kiro/skills/agent-skill-creator

# Trae
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git .trae/rules/agent-skill-creator

# Roo Code
git clone https://github.com/FrancyJGLisboa/agent-skill-creator.git .roo/rules/agent-skill-creator
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

### Using install.sh (for generated skills)

Every skill generated by agent-skill-creator includes a cross-platform installer:

```bash
./install.sh                          # Auto-detect platform
./install.sh --platform cursor        # Force specific platform (auto-generates .mdc)
./install.sh --platform windsurf      # Force Windsurf (auto-generates .md rule)
./install.sh --all                    # Install to every detected tool at once
./install.sh --dry-run                # Preview without installing
```

The installer is POSIX-compatible (works in bash, dash, zsh, ash), handles all 14 platforms, and creates a universal `~/.agents/skills/` symlink after every install for cross-tool discoverability.

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

Skills that fail validation cannot be published. Skills with high-severity security issues are blocked.

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

```bash
# From git URL — clones and symlinks to all detected platforms
./scripts/install-skill.sh https://github.com/someone/sales-report-skill.git

# From local path — copies and symlinks to all detected platforms
./scripts/install-skill.sh ./sales-report-skill

# To a specific platform only
./scripts/install-skill.sh ./sales-report-skill --platform cursor --project

# Preview / remove
./scripts/install-skill.sh ./sales-report-skill --dry-run
./scripts/install-skill.sh ./sales-report-skill --uninstall
```

### Export

```bash
python3 scripts/export_utils.py ./skill/ --variant desktop    # For Claude Desktop
python3 scripts/export_utils.py ./skill/ --variant api        # For Claude API
```

All commands use exit code `0` for success, `1` for errors. All support `--json` for CI/CD integration.

---

## Troubleshooting

**Skill not activating**: Check that the SKILL.md `description` field contains keywords matching your query. The description is how the agent decides when to activate the skill.

**Validation fails on name**: Names must be lowercase, use hyphens between words, 1-64 characters. Examples: `sales-report-skill`, `deploy-checklist`.

**SKILL.md too long**: Move detailed content to `references/` files and link from the main SKILL.md.

**Platform not auto-detected**: Use `--platform cursor` (or copilot, windsurf, codex, gemini, kiro, trae, goose, opencode, roo-code, antigravity, universal) to specify explicitly.

**Install to all tools at once**: Inside a generated skill, use `./install.sh --all` to install to every detected platform in one command.

---

## Project Structure

```
agent-skill-creator/
  SKILL.md                      # The skill definition (what the agent reads)
  README.md                     # This file
  install.sh                    # Symlink self-installer (for cloned repos)
  scripts/
    bootstrap.sh                # Curl one-liner bootstrap (installs everywhere)
    install-skill.sh            # Universal skill installer (any skill, any tool)
    install-template.sh         # Template for generated installers (14 platforms)
    validate.py                 # Spec compliance checker
    security_scan.py            # Security scanner
    staleness_check.py          # Staleness detection (review, deps, drift)
    export_utils.py             # Cross-platform export
    skill_registry.py           # Team skill registry
  references/                   # Detailed docs (loaded by the agent on demand)
    pipeline-phases.md          # Full creation pipeline
    architecture-guide.md       # Skill structure decisions
    quality-standards.md        # Code and documentation standards
    multi-agent-guide.md        # Multi-skill suite creation
    cross-platform-guide.md     # Platform compatibility (tiers, adapters, paths)
    export-guide.md             # Export documentation
    templates-guide.md          # Template system
    interactive-mode.md         # Interactive wizard
    agentdb-integration.md      # Learning system
    phase1-discovery.md         # Phase 1 deep dive
    phase2-design.md            # Phase 2 deep dive
    phase3-architecture.md      # Phase 3 deep dive
    phase4-detection.md         # Phase 4 deep dive
    phase5-implementation.md    # Phase 5 deep dive
    templates/                  # Skill templates
    examples/stock-analyzer/    # Example skill
  registry/                     # Shared skill catalog
    registry.json
    skills/
  exports/                      # Export output
```

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `python3 scripts/validate.py ./` and `python3 scripts/security_scan.py ./`
5. Submit a pull request

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
