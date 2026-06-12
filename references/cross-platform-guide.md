# Cross-Platform Compatibility Guide

**Version:** 6.0
**Purpose:** Research-backed compatibility matrix for Agent Skills across all platforms. Data sourced from agentic-tool-skill-systems research (27 tools analyzed, March 2026).

---

## Overview

Skills created by agent-skill-creator output both **SKILL.md** (agentskills.io spec, ~15 tools) and **AGENTS.md** (AAIF-governed spec, ~15 tools) to maximize cross-tool reach. Together they cover 17 tools across 3 support tiers.

**Standards governance:**
- **SKILL.md** — maintained by Anthropic (agentskills.io). Defines skill format, frontmatter schema, progressive disclosure.
- **AGENTS.md** — governed by AAIF (Agentic AI Foundation, Linux Foundation). Defines project instruction files. Adopted by 15+ tools.
- **MCP** — governed by AAIF. Model Context Protocol for tool extension. 97M+ SDK downloads.

---

## Tier 1 — Native SKILL.md Support

These platforms read SKILL.md natively with no conversion needed:

| Platform | Type | Native Global Path | Native Project Path | Fallback Paths |
|----------|------|--------------------|--------------------|----|
| **Claude Code** | CLI | `~/.claude/skills/` | `.claude/skills/` | `.claude/commands/` (legacy) |
| **GitHub Copilot** | CLI + IDE | `~/.copilot/skills/` | `.github/skills/`, `.claude/skills/` | Also reads `~/.claude/skills/` |
| **Codex CLI** | CLI | `~/.agents/skills/` | `.agents/skills/` | Configurable |
| **Gemini CLI** | CLI | `~/.gemini/skills/` | `.gemini/skills/` | `.agents/skills/` (alias) |
| **Kiro** | IDE | `~/.kiro/skills/` | `.kiro/skills/` | Reads AGENTS.md |
| **Goose** | CLI | `~/.config/goose/skills/` | `.goose/skills/`, `.agents/skills/`, `.claude/skills/` | Multiple tiers |
| **OpenCode** | CLI | `~/.config/opencode/skills/` | `.opencode/skills/`, `.claude/skills/`, `.agents/skills/` | Walks git root |
| **Cline** | VS Code Ext | `~/.cline/skills/` | `.clinerules/skills/`, `.agents/skills/` | `.clinerules/` (legacy) |
| **Roo Code** | VS Code Ext | `~/.roo/skills/` | `.roo/skills/`, `.agents/skills/` | `.roorules`, `.clinerules` (legacy) |
| **Kilo Code** | VS Code + JetBrains + CLI | `~/.kilocode/skills/` | `.kilocode/skills/` | `.roorules`, `.clinerules` (backward compat) |
| **Factory Droid** | Enterprise CLI | `~/.factory/skills/` | `.factory/skills/` | `.agent/skills/` (legacy) |
| **Antigravity** | IDE | `~/.gemini/antigravity/skills/` | `.agent/skills/` | Note: `.agent/` (singular, not `.agents/`) |

## Tier 2 — SKILL.md via Format Adapter

These platforms use their own rule format. The installer auto-generates the native format from SKILL.md:

| Platform | Type | Native Format | Adaptation | Install Path | Limitations |
|----------|------|--------------|------------|-------------|-------------|
| **Cursor** | IDE | `.mdc` | Generates `.mdc` with `alwaysApply`/`globs`/`description` frontmatter | `.cursor/skills/` (project only, **no global path**) | Per-project only; 4 activation modes (Always Apply, Agent Decides, Glob, Manual) |
| **Windsurf** | IDE | `.md` rules | Generates plain `.md` rule file | `.windsurf/rules/` (project) or `~/.codeium/windsurf/` (global) | **6,000 char per-file limit, 12,000 total combined** |
| **Trae** | IDE | `.md` rules | Generates plain `.md` with `type:` frontmatter | `.trae/rules/` | 4 modes: Always Apply, File-specific, Intelligent, Manual |
| **Junie** | JetBrains | `guidelines.md` | Extracts body as plain markdown | `.junie/skills/` | Public catalog at github.com/JetBrains/junie-guidelines |

## Tier 3 — Manual Integration

These platforms require manual setup:

| Platform | Config File | Instructions | AGENTS.md? |
|----------|------------|-------------|------------|
| **Zed** | `.rules` file + Rules Library | Copy SKILL.md body into `.rules` at project root. Or add to Rules Library via UI. | YES (reads AGENTS.md) |
| **Augment** | `.augment/rules/` | Copy as `.md` with `type: Always` or `type: Auto` frontmatter | YES (hierarchical AGENTS.md) |
| **Aider** | `CONVENTIONS.md` | Copy SKILL.md body into CONVENTIONS.md. Configure `read:` in `.aider.conf.yml` | NO |
| **Continue.dev** | `.continue/rules/` | Copy as `.md` with Continue-specific frontmatter (`alwaysApply`, `globs`, `regex`) | YES (recently added) |

---

## AGENTS.md — Companion Output

Every generated skill outputs an AGENTS.md alongside SKILL.md. This is the AAIF-governed instruction file format read by 15+ tools:

**Tools that read AGENTS.md:** Codex CLI (primary), Cursor, Roo Code, Kilo Code, Kiro, Goose, OpenCode, Continue.dev, Factory Droid, Augment, Gemini Code Assist, GitHub Copilot, Windsurf, Zed, Antigravity

The AGENTS.md contains:
- Skill purpose and description
- Activation triggers and usage instructions
- Reference to SKILL.md for full implementation details

This means a generated skill is discoverable by virtually every major tool — either via SKILL.md or AGENTS.md or both.

---

## Activation Mechanisms by Platform

Not all platforms activate skills the same way:

| Platform | Slash Command | Auto-Detect (Description) | File Pattern | Other |
|----------|:---:|:---:|:---:|------|
| Claude Code | `/skill-name` | Yes | — | Bundled skills auto-activate on SDK detection |
| GitHub Copilot | `/skill-name` | Yes | `.instructions.md` applyTo | @agent-name, specialized agents |
| Codex CLI | `/skills`, `$skill-name` | Yes | — | System skills |
| Gemini CLI | `/command-name` | Yes | — | Custom commands via .toml |
| Kiro | `/` invocation | Yes | fileMatch | 4 modes: always, auto, fileMatch, manual |
| Cursor | Slash menu | Yes (Agent Decides) | Glob patterns | Always Apply, Manual @mention |
| Windsurf | — | Yes | Glob patterns | Always On, Model Decision modes |
| Cline | — | Yes (use_skill tool) | — | Always-on rules |
| Roo Code | `/orchestrator`, `/code` | Yes | Mode rules | Mode switching |
| Kilo Code | Mode commands | Yes | Within modes | 5 named modes |
| Goose | — | Yes | — | "Use the X skill" |
| OpenCode | — | Yes (skill() tool) | — | @mention for subagents |
| Factory Droid | `/skill-name` | Yes | — | /droids menu |
| Trae | — | Yes (Intelligent mode) | File-specific | `#Rule` syntax |
| Zed | — | — | — | @mention (Rules Library) |
| Augment | @mention | Yes (Auto type) | Auto mode | Always/Manual/Auto types |
| Aider | `/read` only | — | — | Manual only |
| Continue.dev | `/` slash commands | Yes | Globs, regex | alwaysApply: true |
| Junie | Slash menu | Yes | For rules | Always-on for guidelines |

---

## Cross-Tool Path Sharing

Which paths are read by multiple tools:

| Path | Tools That Read It |
|------|-------------------|
| `~/.claude/skills/` | Claude Code, GitHub Copilot (fallback), Cursor (fallback), OpenCode (fallback), Goose (fallback) |
| `~/.agents/skills/` | Codex CLI (primary), Gemini CLI (alias), OpenCode, Goose, Cline (fallback), Roo Code (fallback), Kilo Code (fallback) |
| `.agents/skills/` | Codex CLI, Gemini CLI, OpenCode, Goose, Cline, Roo Code |
| `.claude/skills/` | Claude Code, GitHub Copilot, Cursor, OpenCode, Goose |
| `AGENTS.md` (file) | 15+ tools (widest reach format) |
| `SKILL.md` (file) | 15+ tools (when in tool's native skill path) |

**Important:** `.agents/skills/` (plural) and `.agent/skills/` (singular, used by Antigravity) are different paths.

---

## Format Adapters

The installer automatically converts SKILL.md to platform-native formats when needed. No separate format files are committed to the skill repo — SKILL.md remains the single source of truth.

### Cursor (.mdc)

The adapter generates a `.mdc` file with Cursor-specific frontmatter:

```
---
description: <extracted from SKILL.md frontmatter>
globs:
alwaysApply: true
---
<SKILL.md body without YAML frontmatter>
```

**Limitations:** Cursor has no global skills path. Skills must be installed per-project in `.cursor/skills/`.

### Windsurf (.md rules)

**Project-level**: Creates a `.md` file in `.windsurf/rules/`.

**User-level (global)**: Appends to `~/.codeium/windsurf/memories/global_rules.md` with idempotent markers:

```markdown
<!-- BEGIN skill-name -->
<SKILL.md body>
<!-- END skill-name -->
```

**Limitations:** 6,000 character limit per rule file, 12,000 total combined. Long skills must be truncated or split.

### Trae (.md rules)

Generates plain `.md` with type frontmatter:

```markdown
---
type: Always
---
<SKILL.md body>
```

### Cline / Roo Code / Kilo Code (plain .md)

The adapter strips YAML frontmatter and outputs plain markdown. These tools read `.md` files from their respective skill directories.

### Junie (guidelines.md)

Extracts SKILL.md body as plain markdown into `.junie/skills/` directory.

---

## Installation by Platform

### Claude Code

```bash
# User-level (global)
cp -r skill-name/ ~/.claude/skills/skill-name/

# Project-level
cp -r skill-name/ .claude/skills/skill-name/
```

### GitHub Copilot

```bash
# User-level (Copilot's native global path)
cp -r skill-name/ ~/.copilot/skills/skill-name/

# Project-level
cp -r skill-name/ .github/skills/skill-name/
```

Copilot also reads `~/.claude/skills/` as a fallback, but its native path is `~/.copilot/skills/`.

### Cursor

```bash
# Project-level ONLY (no global path exists)
cp -r skill-name/ .cursor/skills/skill-name/
```

For cross-project use, clone once and symlink per project:
```bash
git clone <repo> ~/agent-skills/skill-name
mkdir -p .cursor/skills && ln -s ~/agent-skills/skill-name .cursor/skills/skill-name
```

### Codex CLI

```bash
cp -r skill-name/ ~/.agents/skills/skill-name/
```

### Gemini CLI

```bash
# Native path (preferred)
cp -r skill-name/ ~/.gemini/skills/skill-name/

# Also reads ~/.agents/skills/ as fallback
```

### Kiro

```bash
# Project-level
cp -r skill-name/ .kiro/skills/skill-name/
```

### Windsurf

```bash
# Project-level
./install.sh --platform windsurf --project

# User-level (appends to global_rules.md)
./install.sh --platform windsurf
```

### Cline

```bash
cp -r skill-name/ .clinerules/skills/skill-name/
```

### Roo Code

```bash
cp -r skill-name/ .roo/skills/skill-name/
```

### Kilo Code

```bash
cp -r skill-name/ .kilocode/skills/skill-name/
```

### Goose

```bash
cp -r skill-name/ ~/.config/goose/skills/skill-name/
```

### OpenCode

```bash
cp -r skill-name/ ~/.config/opencode/skills/skill-name/
```

### Trae

```bash
./install.sh --platform trae
# Generates plain .md with type: frontmatter in .trae/rules/
```

### Junie

```bash
./install.sh --platform junie
# Generates guidelines.md in .junie/skills/
```

### Factory Droid

```bash
cp -r skill-name/ ~/.factory/skills/skill-name/
```

### Antigravity

```bash
cp -r skill-name/ .agent/skills/skill-name/
# Note: .agent/ (singular), NOT .agents/
```

### Universal Path

```bash
cp -r skill-name/ ~/.agents/skills/skill-name/
```

Read by: Codex CLI, Gemini CLI (fallback), OpenCode, Goose, Cline (fallback), Roo Code (fallback), Kilo Code (fallback).

### Install All

```bash
./install.sh --all
```

### Alternative: npx

```bash
npx skills add <repo-url>
npx skills add ./local-skill-dir
```

### Claude Desktop / claude.ai (Web)

```bash
python scripts/export_utils.py ./skill-name --variant desktop
# Upload the .zip via Settings > Skills
```

---

## Compatibility Matrix

### Format Support

| Feature | Tier 1 | Tier 2 | Desktop/Web | Claude API |
|---------|--------|--------|-------------|------------|
| **SKILL.md** | Native | Via adapter | Full | Full |
| **AGENTS.md** | Most tools | Some tools | N/A | N/A |
| **Python scripts** | Full | Full | Full | Sandboxed* |
| **References/docs** | Full | Full | Full | Full |
| **install.sh** | Full | Full | N/A | N/A |

\* API: No network access, no pip install at runtime

### Platform Limitations

| Platform | Key Limitation |
|----------|---------------|
| **Cursor** | No global skills path — per-project only |
| **Windsurf** | 6,000 char per-file limit, 12,000 total combined |
| **Trae** | Does not read SKILL.md natively; requires format adapter |
| **Zed** | No SKILL.md support; uses `.rules` file and Rules Library UI |
| **Augment** | No SKILL.md support; uses `.augment/rules/` with type frontmatter |
| **Aider** | No SKILL.md or auto-activation; manual CONVENTIONS.md only |
| **Antigravity** | Uses `.agent/skills/` (singular), NOT `.agents/skills/` (plural) |

---

## Best Practices

1. **Use each tool's native path**: Don't install Copilot skills to `~/.claude/`. Use `~/.copilot/skills/` for Copilot, `~/.gemini/skills/` for Gemini, etc.
2. **Output both SKILL.md and AGENTS.md**: Maximizes reach across the entire ecosystem.
3. **Use install.sh or `npx skills`**: Handles path detection and format conversion automatically.
4. **Use `--all` for multi-tool users**: Install to every detected tool with a single command.
5. **Keep SKILL.md lean**: Under 500 lines. Critical for Windsurf's 6K char limit.
6. **Test activation on your target platform**: Description-based auto-detect works on ~15 tools. Slash commands on ~12. Manual activation needed for Zed, Aider.
7. **No platform hacks**: Avoid platform-specific code. The standard format + adapters handle the rest.

---

**Generated by:** agent-skill-creator v6.0
**Standards:** SKILL.md (agentskills.io), AGENTS.md (AAIF/Linux Foundation)
**Data source:** agentic-tool-skill-systems research, 27 tools analyzed, March 2026
