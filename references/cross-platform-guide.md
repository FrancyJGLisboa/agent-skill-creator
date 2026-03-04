# Cross-Platform Compatibility Guide

**Version:** 5.0
**Purpose:** Complete compatibility matrix for Agent Skills across all platforms supporting the Agent Skills Open Standard

---

## Overview

Skills created by agent-skill-creator are compliant with the **Agent Skills Open Standard** and work across all platforms that support the SKILL.md format. As of v5.0, this includes 14+ platforms across 3 support tiers.

### Supported Platforms

#### Tier 1 — Native SKILL.md Support

These platforms read SKILL.md natively with no conversion needed:

| Platform | Type | User-Level Path | Project-Level Path |
|----------|------|-----------------|-------------------|
| **Claude Code** | CLI | `~/.claude/skills/` | `.claude/skills/` |
| **GitHub Copilot CLI** | CLI | `~/.copilot/skills/` | `.github/skills/` |
| **VS Code Copilot** | IDE Extension | `~/.claude/skills/` | `.github/skills/` |
| **Codex CLI** | CLI | `~/.agents/skills/` | `.agents/skills/` |
| **Gemini CLI** | CLI | `~/.gemini/skills/` | `.gemini/skills/` |
| **Kiro** | IDE | — | `.kiro/skills/` |
| **Antigravity** | CLI | — | `.agents/skills/` |
| **Goose** | CLI | `~/.config/goose/skills/` | — |
| **OpenCode** | CLI | `~/.config/opencode/skills/` | — |

#### Tier 2 — SKILL.md via Format Adapter

These platforms use their own rule format. The installer auto-generates the native format from SKILL.md:

| Platform | Type | Native Format | Adapter Output | Install Path |
|----------|------|--------------|----------------|-------------|
| **Cursor** | IDE | `.mdc` | Auto-generated `.mdc` with frontmatter | `.cursor/rules/` |
| **Windsurf** | IDE | `.md` rules | `.md` rule file or `global_rules.md` append | `.windsurf/rules/` (project) or `~/.codeium/windsurf/memories/global_rules.md` (global) |
| **Cline** | VS Code Ext | Plain `.md` | Stripped frontmatter `.md` | `.clinerules/` |
| **Roo Code** | VS Code Ext | Plain `.md` | Stripped frontmatter `.md` | `.roo/rules/` |
| **Trae** | IDE | Plain `.md` | Stripped frontmatter `.md` | `.trae/rules/` |

#### Tier 3 — Manual Configuration

These platforms require manual integration:

| Platform | Config File | Instructions |
|----------|------------|-------------|
| **Zed** | `.rules` | Copy SKILL.md body into `.rules` file |
| **Junie** | `.junie/guidelines.md` | Copy SKILL.md body into guidelines |
| **Aider** | `CONVENTIONS.md` | Copy SKILL.md body into CONVENTIONS.md |

### The Unifying Standard

All Tier 1 and Tier 2 platforms read from the same SKILL.md source:

```yaml
---
name: skill-name
description: What the skill does and when to activate it
license: MIT
metadata:
  author: Author Name
  version: 1.0.0
---
# Skill content here...
```

A skill created once works everywhere — directly on Tier 1, via auto-adapter on Tier 2.

---

## Universal Path: `.agents/skills/`

The `.agents/skills/` directory is an emerging cross-tool convention for agent skill discovery. Multiple tools already read from this path:

- **Codex CLI** — reads `~/.agents/skills/` and `.agents/skills/`
- **Gemini CLI** — discovers skills in `~/.agents/skills/`
- **Kiro** — reads `.agents/skills/` (project-level)
- **Antigravity** — reads `.agents/skills/` (project-level)

The installer creates a **secondary symlink** at `~/.agents/skills/<skill-name>` after every install (unless the primary target is already `.agents/`). This means a skill installed for Claude Code is also discoverable by Codex CLI, Gemini CLI, and other universal-path tools automatically.

```bash
# Install for Claude Code — also creates ~/.agents/skills/ symlink
./install.sh --platform claude-code

# Install directly to universal path
./install.sh --platform universal

# Install to ALL detected platforms at once
./install.sh --all
```

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

### Windsurf (.md rules)

**Project-level**: Creates a `.md` file in `.windsurf/rules/`.

**User-level (global)**: Appends to `~/.codeium/windsurf/memories/global_rules.md` with idempotent markers:

```markdown
<!-- BEGIN skill-name -->
<SKILL.md body>
<!-- END skill-name -->
```

Re-running the installer replaces the existing block rather than duplicating.

### Cline / Roo Code / Trae (plain .md)

The adapter strips YAML frontmatter and outputs plain markdown. These tools read `.md` files from their respective rule directories.

---

## Installation by Platform

### Claude Code

```bash
# Using install.sh (recommended)
./install.sh

# Manual: User-level
cp -r skill-name/ ~/.claude/skills/skill-name/

# Manual: Project-level
cp -r skill-name/ .claude/skills/skill-name/
```

**Best for:** Developers, power users, teams with git workflows.

### GitHub Copilot

```bash
# Using install.sh
./install.sh --platform copilot

# Manual: Project-level
cp -r skill-name/ .github/skills/skill-name/
```

**Best for:** GitHub-integrated workflows, VS Code users.

### Cursor

```bash
# Using install.sh (auto-generates .mdc)
./install.sh --platform cursor

# Manual
cp -r skill-name/ .cursor/rules/skill-name/
```

**Best for:** Cursor IDE users. The installer auto-generates a `.mdc` file alongside SKILL.md.

### Windsurf

```bash
# Using install.sh (project-level — creates .windsurf/rules/ rule)
./install.sh --platform windsurf --project

# Using install.sh (user-level — appends to global_rules.md)
./install.sh --platform windsurf
```

**Best for:** Windsurf IDE users.

### Cline

```bash
# Using install.sh
./install.sh --platform cline

# Manual
cp -r skill-name/ .clinerules/skill-name/
```

**Best for:** Cline extension users in VS Code.

### Codex CLI

```bash
# Using install.sh (installs to ~/.agents/skills/)
./install.sh --platform codex

# Manual
cp -r skill-name/ ~/.agents/skills/skill-name/
```

**Best for:** OpenAI Codex CLI users. Codex reads from `~/.agents/skills/`.

### Gemini CLI

```bash
# Using install.sh
./install.sh --platform gemini

# Manual
cp -r skill-name/ ~/.gemini/skills/skill-name/
```

**Best for:** Gemini CLI users.

### Kiro

```bash
# Using install.sh
./install.sh --platform kiro

# Manual
cp -r skill-name/ .kiro/skills/skill-name/
```

**Best for:** Kiro IDE users (project-level).

### Trae

```bash
# Using install.sh (auto-generates plain .md)
./install.sh --platform trae

# Manual
cp -r skill-name/ .trae/rules/skill-name/
```

**Best for:** Trae IDE users.

### Goose

```bash
# Using install.sh
./install.sh --platform goose

# Manual
cp -r skill-name/ ~/.config/goose/skills/skill-name/
```

**Best for:** Goose CLI users.

### OpenCode

```bash
# Using install.sh
./install.sh --platform opencode

# Manual
cp -r skill-name/ ~/.config/opencode/skills/skill-name/
```

**Best for:** OpenCode CLI users.

### Roo Code

```bash
# Using install.sh (auto-generates plain .md)
./install.sh --platform roo-code

# Manual
cp -r skill-name/ .roo/rules/skill-name/
```

**Best for:** Roo Code extension users in VS Code.

### Antigravity

```bash
# Using install.sh
./install.sh --platform antigravity

# Manual
cp -r skill-name/ .agents/skills/skill-name/
```

**Best for:** Antigravity CLI users.

### Universal Path

```bash
# Using install.sh
./install.sh --platform universal

# Manual
cp -r skill-name/ ~/.agents/skills/skill-name/
```

**Best for:** Multi-tool users. One install discoverable by Codex CLI, Gemini CLI, Kiro, Antigravity, and other tools that read `.agents/skills/`.

### Install All

```bash
# Install to every detected tool at once
./install.sh --all
```

### Alternative: npx

```bash
npx skills add <repo-url>
npx skills add ./local-skill-dir
```

### Claude Desktop / claude.ai (Web)

These platforms use .zip upload instead of directory copying:

1. Export: `python scripts/export_utils.py ./skill-name --variant desktop`
2. Open Claude Desktop or claude.ai
3. Go to Settings > Skills > Upload skill
4. Select the .zip file

### Claude API

```python
import anthropic

client = anthropic.Anthropic()

with open('skill-name-api-v1.0.0.zip', 'rb') as f:
    skill = client.skills.create(file=f, name="skill-name")

response = client.messages.create(
    model="claude-sonnet-4",
    messages=[{"role": "user", "content": "Your query here"}],
    container={"type": "custom_skill", "skill_id": skill.id},
    betas=["code-execution-2025-08-25", "skills-2025-10-02"]
)
```

---

## Compatibility Matrix

### Core Functionality

| Feature | Tier 1 Platforms | Tier 2 Platforms | Desktop/Web | Claude API |
|---------|-----------------|-----------------|-------------|------------|
| **SKILL.md support** | Native | Via adapter | Full | Full |
| **Python scripts** | Full | Full | Full | Sandboxed* |
| **References/docs** | Full | Full | Full | Full |
| **Assets/templates** | Full | Full | Full | Full |
| **install.sh** | Full | Full | N/A | N/A |
| **Format adapters** | N/A | Auto | N/A | N/A |

\* API: No network access, no pip install at runtime

### Technical Specifications

| Specification | CLI/IDE Platforms | Desktop/Web | Claude API |
|---------------|-----------------|-------------|------------|
| **Max skill size** | No limit | ~10MB | 8MB hard limit |
| **Network access** | Yes | Yes | No |
| **Package install** | Yes | Yes | No |
| **File system** | Full | Full | Limited |
| **Updates** | git pull | Re-upload | API upload |

---

## Platform-Specific Notes

### marketplace.json

- **Required by**: Claude Code (for plugin marketplace distribution only)
- **Not needed by**: All other platforms
- **Recommendation**: For simple skills, do not include `marketplace.json`. Only add it for complex skill suites that need Claude Code plugin distribution.
- **Format**: If included, use ONLY official fields: `name`, `plugins[].name`, `plugins[].description`, `plugins[].source`, `plugins[].skills`

### Skill Activation

All platforms that support the SKILL.md standard use the `description` field in frontmatter as the primary activation mechanism. The description should contain:

- Clear explanation of when to use the skill
- Domain-specific keywords
- Example trigger phrases

No platform-specific activation configuration is needed.

### File Structure

The standard skill directory works on all platforms:

```
skill-name/
├── SKILL.md          # Required - primary skill definition
├── scripts/          # Optional - executable code
├── references/       # Optional - detailed documentation
├── assets/           # Optional - templates, schemas, data
├── install.sh        # Optional - cross-platform installer
└── README.md         # Recommended - install instructions
```

---

## Migration Between Platforms

### CLI Platform to CLI Platform

Skills are directly portable. Just copy the directory to the target platform's skill location:

```bash
# From Claude Code to Codex CLI
cp -r ~/.claude/skills/my-skill/ ~/.agents/skills/my-skill/

# From Cursor to Cline
cp -r .cursor/rules/my-skill/ .clinerules/my-skill/
```

### CLI Platform to Desktop/Web

Export as .zip:

```bash
python scripts/export_utils.py ./my-skill --variant desktop
# Output: exports/my-skill-desktop-v1.0.0.zip
```

### CLI Platform to API

Export as optimized .zip:

```bash
python scripts/export_utils.py ./my-skill --variant api
# Output: exports/my-skill-api-v1.0.0.zip (< 8MB)
```

---

## Best Practices

1. **Develop once, deploy everywhere**: Create and test in your preferred CLI tool, then install on other platforms.
2. **Use install.sh**: Include the cross-platform installer for easy deployment.
3. **Use `--all` for multi-tool users**: Install to every detected tool with a single command.
4. **Keep SKILL.md lean**: Under 500 lines, detailed content in `references/`.
5. **Test activation**: Verify the `description` triggers correctly on your target platform.
6. **Include README.md**: Document installation instructions for all platforms.
7. **No platform hacks**: Avoid platform-specific code or configuration. The standard format works everywhere; adapters handle the rest.

---

**Generated by:** agent-skill-creator v5.0
**Standard:** Agent Skills Open Standard (agentskills.io/specification)
