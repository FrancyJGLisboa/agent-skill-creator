# Cross-Platform Export Guide

**Version:** 3.2
**Purpose:** Complete guide to exporting agent-skill-creator skills for use across all Claude platforms

---

## 🎯 Overview

Skills created by agent-skill-creator are optimized for **Claude Code**, but can be exported for use across all Claude platforms:

- **Claude Code** (CLI) - Native directory-based format
- **Claude Desktop** - Manual .zip file upload
- **claude.ai** (Web) - Manual .zip file upload
- **Claude API** - Programmatic .zip upload

This guide explains how to export skills for cross-platform compatibility.

---

## 📦 Why Export?

### The Challenge

Different Claude platforms use different distribution methods:

| Platform | Installation Method | Requires Export? |
|----------|-------------------|------------------|
| Claude Code | Plugin/directory | ❌ No (native) |
| Claude Desktop | .zip upload | ✅ Yes |
| claude.ai | .zip upload | ✅ Yes |
| Claude API | Programmatic upload | ✅ Yes |

### The Solution

The export system creates **optimized .zip packages** with:
- ✅ Platform-specific optimization
- ✅ Version numbering
- ✅ Automatic validation
- ✅ Installation guides
- ✅ Size optimization

---

## 🚀 Quick Start

### Automatic Export (Recommended)

After creating a skill, agent-skill-creator will prompt:

```
✅ Skill created: financial-analysis-cskill/

📦 Export Options:
   1. Desktop/Web (.zip for manual upload)
   2. API (.zip for programmatic use)
   3. Both (comprehensive package)
   4. Skip (Claude Code only)

Choice: 3

🔨 Creating export packages...
✅ Desktop package: exports/financial-analysis-cskill-desktop-v1.0.0.zip
✅ API package: exports/financial-analysis-cskill-api-v1.0.0.zip
📄 Installation guide: exports/financial-analysis-cskill-v1.0.0_INSTALL.md
```

### On-Demand Export

Export any existing skill anytime:

```
"Export stock-analyzer for Desktop and API"
"Package financial-analysis for claude.ai"
"Create API export for climate-analyzer with version 2.1.0"
```

### Manual Export (Advanced)

Using the export script directly:

```bash
# Export both variants
python scripts/export_utils.py ./my-skill-cskill

# Export only Desktop variant
python scripts/export_utils.py ./my-skill-cskill --variant desktop

# Export with specific version
python scripts/export_utils.py ./my-skill-cskill --version 2.0.1

# Export to custom directory
python scripts/export_utils.py ./my-skill-cskill --output-dir ./dist
```

---

## 📊 Export Variants

### Desktop/Web Package (`*-desktop-*.zip`)

**Optimized for:** Claude Desktop and claude.ai manual upload

**Includes:**
- ✅ Complete SKILL.md
- ✅ All scripts/
- ✅ Full references/ documentation
- ✅ All assets/ and templates
- ✅ README.md
- ✅ requirements.txt

**Excludes:**
- ❌ .claude-plugin/ (not used by Desktop/Web)
- ❌ .git/ (version control not needed)
- ❌ Development artifacts

**Typical Size:** 2-5 MB

**Use when:**
- Sharing with Desktop users
- Uploading to claude.ai
- Need full documentation

### API Package (`*-api-*.zip`)

**Optimized for:** Programmatic Claude API integration

**Includes:**
- ✅ SKILL.md (required)
- ✅ Essential scripts only
- ✅ Critical references only
- ✅ requirements.txt

**Excludes:**
- ❌ .claude-plugin/ (not used by API)
- ❌ .git/ (not needed)
- ❌ Heavy documentation files
- ❌ Example files (size optimization)
- ❌ Large reference materials

**Typical Size:** 0.5-2 MB (< 8MB limit)

**Use when:**
- Integrating with API
- Need size optimization
- Programmatic deployment
- Execution-focused use

---

## 🔍 Version Management

### Auto-Detection

The export system automatically detects versions from:

1. **Git tags** (highest priority)
   ```bash
   git tag v1.0.0
   # Export will use v1.0.0
   ```

2. **SKILL.md frontmatter**
   ```yaml
   ---
   name: my-skill
   version: 1.2.3
   ---
   ```

3. **Default fallback**
   - If no version found: `v1.0.0`

### Manual Override

Specify version explicitly:

```bash
# Via CLI
python scripts/export_utils.py ./my-skill --version 2.1.0

# Via natural language
"Export my-skill with version 3.0.0"
```

### Versioning Best Practices

Follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR (X.0.0)**: Breaking changes to skill behavior
- **MINOR (x.X.0)**: New features, backward compatible
- **PATCH (x.x.X)**: Bug fixes, optimizations

**Examples:**
- `v1.0.0` → Initial release
- `v1.1.0` → Added new analysis feature
- `v1.1.1` → Fixed calculation bug
- `v2.0.0` → Changed API interface (breaking)

---

## ✅ Validation

### Automatic Validation

Every export is validated for:

**Structure Checks:**
- ✅ SKILL.md exists
- ✅ SKILL.md has valid frontmatter
- ✅ Frontmatter has `name:` field
- ✅ Frontmatter has `description:` field

**Content Checks:**
- ✅ Name ≤ 64 characters
- ✅ Description ≤ 1024 characters
- ✅ No sensitive files (.env, credentials.json)

**Size Checks:**
- ✅ Desktop package: reasonable size
- ✅ API package: < 8MB (hard limit)

### Validation Failures

If validation fails, you'll see detailed error messages:

```
❌ Export failed!

Issues found:
   - SKILL.md missing 'name:' field in frontmatter
   - description too long: 1500 chars (max 1024)
   - API package too large: 9.2 MB (max 8 MB)
```

**Common fixes:**
- Add missing frontmatter fields
- Shorten description to ≤ 1024 chars
- Remove large files for API variant
- Check SKILL.md formatting

---

## 📁 Output Organization

### Directory Structure

```
exports/
├── skill-name-desktop-v1.0.0.zip
├── skill-name-api-v1.0.0.zip
├── skill-name-v1.0.0_INSTALL.md
├── skill-name-desktop-v1.1.0.zip
├── skill-name-api-v1.1.0.zip
└── skill-name-v1.1.0_INSTALL.md
```

### File Naming Convention

```
{skill-name}-{variant}-v{version}.zip
{skill-name}-v{version}_INSTALL.md
```

**Components:**
- `skill-name`: Directory name (e.g., `financial-analysis-cskill`)
- `variant`: `desktop` or `api`
- `version`: Semantic version (e.g., `v1.0.0`)

**Examples:**
- `stock-analyzer-cskill-desktop-v1.0.0.zip`
- `stock-analyzer-cskill-api-v1.0.0.zip`
- `stock-analyzer-cskill-v1.0.0_INSTALL.md`

---

## 🛡️ Security & Exclusions

### Automatically Excluded

**Directories:**
- `.git/` - Version control (contains history)
- `__pycache__/` - Python compiled files
- `node_modules/` - JavaScript dependencies
- `.venv/`, `venv/`, `env/` - Virtual environments
- `.claude-plugin/` - Claude Code specific (API variant only)

**Files:**
- `.env` - Environment variables (may contain secrets)
- `credentials.json` - API keys and secrets
- `secrets.json` - Secret configuration
- `.DS_Store` - macOS metadata
- `.gitignore` - Git configuration
- `*.pyc`, `*.pyo` - Python compiled
- `*.log` - Log files

### Why Exclude These?

1. **Security**: Prevent accidental exposure of API keys/secrets
2. **Size**: Reduce package size (especially for API variant)
3. **Relevance**: Remove development artifacts not needed at runtime
4. **Portability**: Exclude platform-specific files

### What's Always Included

**Required:**
- `SKILL.md` - Core skill definition (mandatory)

**Strongly Recommended:**
- `scripts/` - Execution code
- `README.md` - Usage documentation
- `requirements.txt` - Python dependencies

**Optional:**
- `references/` - Additional documentation
- `assets/` - Templates, prompts, examples

---

## 🎯 Use Cases

### Use Case 1: Share with Desktop Users

**Scenario:** You created a skill in Claude Code, colleague uses Desktop

**Solution:**
```
1. Export: "Export my-skill for Desktop"
2. Share: Send {skill}-desktop-v1.0.0.zip to colleague
3. Install: Colleague uploads to Desktop → Settings → Skills
```

### Use Case 2: Deploy via API

**Scenario:** Integrate skill into production application

**Solution:**
```python
# 1. Export API variant
"Export my-skill for API"

# 2. Upload programmatically
import anthropic
client = anthropic.Anthropic(api_key=os.env['ANTHROPIC_API_KEY'])

with open('my-skill-api-v1.0.0.zip', 'rb') as f:
    skill = client.skills.create(file=f, name="my-skill")

# 3. Use in production
response = client.messages.create(
    model="claude-sonnet-4",
    messages=[{"role": "user", "content": query}],
    container={"type": "custom_skill", "skill_id": skill.id},
    betas=["code-execution-2025-08-25", "skills-2025-10-02"]
)
```

### Use Case 3: Versioned Releases

**Scenario:** Maintain multiple skill versions

**Solution:**
```bash
# Release v1.0.0
git tag v1.0.0
"Export my-skill for both"
# Creates: my-skill-desktop-v1.0.0.zip, my-skill-api-v1.0.0.zip

# Later: Release v1.1.0 with new features
git tag v1.1.0
"Export my-skill for both"
# Creates: my-skill-desktop-v1.1.0.zip, my-skill-api-v1.1.0.zip

# Both versions coexist in exports/ for compatibility
```

### Use Case 4: Team Distribution

**Scenario:** Share skill with entire team

**Options:**

**Option A: Git Repository**
```bash
# Claude Code users (recommended)
git clone repo-url
/plugin marketplace add ./skill-name
```

**Option B: Direct Download**
```bash
# Desktop/Web users
1. Download {skill}-desktop-v1.0.0.zip
2. Upload to Claude Desktop or claude.ai
3. Follow installation guide
```

---

## 🔧 Troubleshooting

### Export Fails: "Path does not exist"

**Cause:** Incorrect skill path

**Fix:**
```bash
# Check path exists
ls -la ./my-skill-cskill

# Use absolute path
python scripts/export_utils.py /full/path/to/skill
```

### Export Fails: "SKILL.md missing frontmatter"

**Cause:** SKILL.md doesn't start with `---`

**Fix:**
```markdown
---
name: my-skill
description: What this skill does
---

# Rest of SKILL.md content
```

### Export Fails: "API package too large"

**Cause:** Package exceeds 8MB API limit

**Fix Options:**
1. Remove large documentation files from skill
2. Remove example files
3. Compress images/assets
4. Use Desktop variant instead (no size limit)

### Desktop upload fails

**Cause:** Various platform-specific issues

**Check:**
1. File size reasonable (< 10MB recommended)
2. SKILL.md has valid frontmatter
3. Name ≤ 64 characters
4. Description ≤ 1024 characters
5. Try re-exporting with latest version

### API returns error

**Common causes:**
```python
# Missing beta headers
betas=["code-execution-2025-08-25", "skills-2025-10-02"]  # REQUIRED

# Wrong container type
container={"type": "custom_skill", "skill_id": skill.id}  # Use custom_skill

# Skill ID not found
# Ensure skill.id from upload matches container skill_id
```

---

## 📚 Advanced Topics

### Custom Output Directory

```bash
# Default: exports/ in parent directory
python scripts/export_utils.py ./skill

# Custom location
python scripts/export_utils.py ./skill --output-dir /path/to/releases

# Within skill directory
python scripts/export_utils.py ./skill --output-dir ./dist
```

### Batch Export

Export multiple skills:

```bash
# Loop through skills
for skill in *-cskill; do
    python scripts/export_utils.py "./$skill"
done

# Or via agent-skill-creator
"Export all skills in current directory"
```

### CI/CD Integration

Automate exports in build pipeline:

```yaml
# .github/workflows/release.yml
name: Release Skill
on:
  push:
    tags:
      - 'v*'

jobs:
  export:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Export skill
        run: |
          python scripts/export_utils.py . --version ${{ github.ref_name }}
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: skill-packages
          path: exports/*.zip
```

---

## 🎓 Best Practices

### ✅ Do

1. **Version everything** - Use semantic versioning
2. **Test exports** - Verify packages work on target platforms
3. **Include README** - Clear usage instructions
4. **Keep secrets out** - Never include .env or credentials
5. **Document dependencies** - Maintain requirements.txt
6. **Validate before sharing** - Run validation checks
7. **Use installation guides** - Auto-generated for each export

### ❌ Don't

1. **Don't commit .zip files to git** - They're generated artifacts
2. **Don't include secrets** - Use environment variables instead
3. **Don't skip validation** - Ensures compatibility
4. **Don't ignore size limits** - API has 8MB maximum
5. **Don't forget documentation** - Users need guidance
6. **Don't mix versions** - Clear version numbering prevents confusion

---

## 📖 Related Documentation

- **Cross-Platform Guide**: `cross-platform-guide.md` - Platform compatibility matrix
- **Main README**: `../README.md` - Agent-skill-creator overview
- **SKILL.md**: `../SKILL.md` - Core skill definition
- **CHANGELOG**: `../docs/CHANGELOG.md` - Version history

---

## 🆘 Getting Help

**Questions about:**
- Export process → This guide
- Platform compatibility → `cross-platform-guide.md`
- Skill creation → Main `README.md`
- API integration → Claude API documentation

**Report issues:**
- GitHub Issues: [agent-skill-creator issues](https://github.com/FrancyJGLisboa/agent-skill-creator/issues)

---

**Generated by:** agent-skill-creator v3.2
**Last updated:** October 2025
