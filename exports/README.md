# Exports Directory

This directory contains cross-platform export packages for skills created by agent-skill-creator.

## 📦 What's Here

This directory stores `.zip` packages optimized for different Claude platforms:

- **Desktop packages** (`*-desktop-v*.zip`) - For Claude Desktop and claude.ai manual upload
- **API packages** (`*-api-v*.zip`) - For programmatic Claude API integration
- **Installation guides** (`*_INSTALL.md`) - Platform-specific instructions for each export

## 🚀 Using Exported Packages

### For Claude Desktop

1. Locate the `-desktop-` package for your skill
2. Open Claude Desktop → Settings → Capabilities → Skills
3. Click "Upload skill" and select the `.zip` file
4. Follow any additional instructions in the corresponding `_INSTALL.md` file

### For claude.ai (Web)

1. Locate the `-desktop-` package (same as Desktop)
2. Visit https://claude.ai → Settings → Skills
3. Click "Upload skill" and select the `.zip` file
4. Confirm the upload

### For Claude API

1. Locate the `-api-` package for your skill
2. Use the Claude API to upload programmatically:

```python
import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

with open('skill-name-api-v1.0.0.zip', 'rb') as f:
    skill = client.skills.create(
        file=f,
        name="skill-name"
    )

# Use in API requests
response = client.messages.create(
    model="claude-sonnet-4",
    messages=[{"role": "user", "content": "Your query"}],
    container={"type": "custom_skill", "skill_id": skill.id},
    betas=["code-execution-2025-08-25", "skills-2025-10-02"]
)
```

3. See the `_INSTALL.md` file for complete API integration instructions

## 📁 File Organization

### Naming Convention

```
skill-name-{variant}-v{version}.zip
skill-name-{variant}-v{version}_INSTALL.md
```

**Examples:**
- `financial-analysis-cskill-desktop-v1.0.0.zip`
- `financial-analysis-cskill-api-v1.0.0.zip`
- `financial-analysis-cskill-desktop-v1.0.0_INSTALL.md`

### Version Numbering

Versions follow semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes to skill behavior
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, optimizations

## 🔧 Generating Exports

### Automatic (Opt-In)

After creating a skill, agent-skill-creator will prompt:

```
📦 Export Options:
   1. Desktop/Web (.zip for manual upload)
   2. API (.zip for programmatic use)
   3. Both (comprehensive package)
   4. Skip (Claude Code only)
```

Choose your option and exports will be generated here automatically.

### On-Demand

Export any existing skill anytime:

```
"Export [skill-name] for Desktop"
"Export [skill-name] for API with version 2.1.0"
"Create cross-platform package for [skill-name]"
```

## 📊 Package Differences

| Feature | Desktop Package | API Package |
|---------|-----------------|-------------|
| **Size** | Full (2-5 MB typical) | Optimized (< 8MB required) |
| **Documentation** | Complete | Minimal (execution-focused) |
| **Examples** | Included | Excluded (size optimization) |
| **References** | Full | Essential only |
| **Scripts** | All | Execution-critical only |

## 🛡️ Security Notes

**What's Excluded** (for security):
- `.env` files (environment variables)
- `credentials.json` (API keys)
- `.git/` directories (version control history)
- `__pycache__/` (compiled Python)
- `.DS_Store` (macOS metadata)

**What's Included**:
- `SKILL.md` (required core functionality)
- `scripts/` (execution code)
- `references/` (documentation)
- `assets/` (templates, prompts)
- `requirements.txt` (dependencies)
- `README.md` (usage instructions)

## 📚 Additional Resources

- **Export Guide**: `../references/export-guide.md`
- **Cross-Platform Guide**: `../references/cross-platform-guide.md`
- **Main README**: `../README.md`

## ⚠️ Git Ignore

This directory is configured to ignore `.zip` files and `_INSTALL.md` files in git (they're generated artifacts). Only this README is tracked.

If you need to share exports, distribute them directly to users or host them externally.

---

**Questions?** See the export guide or cross-platform compatibility guide in the `references/` directory.
