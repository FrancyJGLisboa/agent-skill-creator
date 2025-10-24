# Cross-Platform Compatibility Guide

**Version:** 3.2
**Purpose:** Complete compatibility matrix for Claude Skills across all platforms

---

## 🎯 Overview

This guide explains how skills created by agent-skill-creator work across **four Claude platforms**, their differences, and how to optimize for each.

### The Four Platforms

1. **Claude Code** (CLI) - Command-line tool for developers
2. **Claude Desktop** (Native App) - Desktop application
3. **claude.ai** (Web) - Browser-based interface
4. **Claude API** - Programmatic integration

---

## 📊 Compatibility Matrix

### Core Functionality

| Feature | Claude Code | Claude Desktop | claude.ai | Claude API |
|---------|-------------|----------------|-----------|------------|
| **SKILL.md support** | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| **Python scripts** | ✅ Full | ✅ Full | ✅ Full | ⚠️ Limited* |
| **References/docs** | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| **Assets/templates** | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| **requirements.txt** | ✅ Full | ✅ Full | ✅ Full | ⚠️ Limited* |

\* API has execution constraints (no network, no pip install at runtime)

### Installation & Distribution

| Feature | Claude Code | Claude Desktop | claude.ai | Claude API |
|---------|-------------|----------------|-----------|------------|
| **Installation method** | Plugin/directory | Manual .zip | Manual .zip | API upload |
| **Marketplace support** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **marketplace.json** | ✅ Used | ❌ Ignored | ❌ Ignored | ❌ Not used |
| **Auto-updates** | ✅ Via git/plugins | ❌ Manual | ❌ Manual | ✅ Via API |
| **Version control** | ✅ Native git | ⚠️ Manual | ⚠️ Manual | ✅ Programmatic |
| **Team sharing** | ✅ Via plugins | ❌ Individual | ❌ Individual | ✅ Via API |

### Technical Specifications

| Specification | Claude Code | Claude Desktop | claude.ai | Claude API |
|---------------|-------------|----------------|-----------|------------|
| **Max skill size** | No limit | ~10MB recommended | ~10MB recommended | 8MB hard limit |
| **Skills per user** | Unlimited | Platform limit | Platform limit | 8 per request |
| **Execution environment** | Full | Full | Full | Sandboxed |
| **Network access** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |
| **Package install** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |
| **File system access** | ✅ Yes | ✅ Yes | ✅ Yes | ⚠️ Limited |

---

## 🔍 Platform Details

### Claude Code (CLI)

**Best for:** Developers, power users, teams with git workflows

**Strengths:**
- ✅ Native skill support (no export needed)
- ✅ Plugin marketplace distribution
- ✅ Git-based version control
- ✅ Automatic updates
- ✅ Full execution environment
- ✅ No size limits
- ✅ Team collaboration via plugins

**Installation:**
```bash
# Method 1: Plugin marketplace
/plugin marketplace add ./skill-name-cskill

# Method 2: Personal skills
~/.claude/skills/skill-name-cskill/

# Method 3: Project skills
.claude/skills/skill-name-cskill/
```

**Workflow:**
1. Create skill with agent-skill-creator
2. Install via plugin command
3. Use immediately
4. Update via git pull

**Optimal for:**
- Development workflows
- Team projects
- Version-controlled skills
- Complex skill suites
- Rapid iteration

---

### Claude Desktop (Native App)

**Best for:** Individual users, desktop workflows, offline use

**Strengths:**
- ✅ Native app performance
- ✅ Offline capability
- ✅ Full skill functionality
- ✅ System integration
- ✅ Privacy (local execution)

**Limitations:**
- ❌ No marketplace
- ❌ Manual .zip upload required
- ❌ Individual installation (no team sharing)
- ❌ Manual updates

**Installation:**
```
1. Locate exported .zip package
2. Open Claude Desktop
3. Go to: Settings → Capabilities → Skills
4. Click: Upload skill
5. Select the .zip file
6. Wait for confirmation
```

**Workflow:**
1. Export: Create Desktop package
2. Upload: Manual .zip upload
3. Update: Re-upload new version
4. Share: Send .zip to colleagues

**Optimal for:**
- Personal productivity
- Privacy-sensitive work
- Offline usage
- Desktop-integrated workflows

---

### claude.ai (Web Interface)

**Best for:** Quick access, browser-based work, cross-device

**Strengths:**
- ✅ No installation required
- ✅ Access from any browser
- ✅ Cross-device availability
- ✅ Always up-to-date interface
- ✅ Full skill functionality

**Limitations:**
- ❌ No marketplace
- ❌ Manual .zip upload required
- ❌ Individual installation
- ❌ Manual updates
- ❌ Requires internet connection

**Installation:**
```
1. Visit https://claude.ai
2. Log in to account
3. Click profile → Settings
4. Navigate to: Skills
5. Click: Upload skill
6. Select the .zip file
7. Confirm upload
```

**Workflow:**
1. Export: Create Desktop package (same as Desktop)
2. Upload: Via web interface
3. Update: Re-upload new version
4. Share: Send .zip to colleagues

**Optimal for:**
- Browser-based workflows
- Quick skill access
- Multi-device usage
- Casual/infrequent use

---

### Claude API (Programmatic)

**Best for:** Production apps, automation, enterprise integration

**Strengths:**
- ✅ Programmatic control
- ✅ Version management via API
- ✅ Automated deployment
- ✅ CI/CD integration
- ✅ Workspace-level sharing
- ✅ Production scalability

**Limitations:**
- ⚠️ 8MB size limit (hard)
- ⚠️ No network access in execution
- ⚠️ No pip install at runtime
- ⚠️ Sandboxed environment
- ⚠️ Max 8 skills per request

**Installation:**
```python
import anthropic

client = anthropic.Anthropic(api_key="your-key")

# Upload skill
with open('skill-api-v1.0.0.zip', 'rb') as f:
    skill = client.skills.create(
        file=f,
        name="skill-name"
    )

# Use in requests
response = client.messages.create(
    model="claude-sonnet-4",
    messages=[{"role": "user", "content": query}],
    container={"type": "custom_skill", "skill_id": skill.id},
    betas=["code-execution-2025-08-25", "skills-2025-10-02"]
)
```

**Workflow:**
1. Export: Create API package (optimized)
2. Upload: Programmatic via API
3. Deploy: Integrate in production
4. Update: Upload new version
5. Manage: Version control via API

**Optimal for:**
- Production applications
- Automated workflows
- Enterprise integration
- Scalable deployments
- CI/CD pipelines

---

## 🔄 Migration Between Platforms

### Code → Desktop/Web

**Scenario:** Developed in Claude Code, share with Desktop users

**Process:**
```bash
# 1. Export Desktop package
"Export my-skill for Desktop"

# 2. Share .zip file
# Output: exports/my-skill-desktop-v1.0.0.zip

# 3. Desktop users upload
# Settings → Skills → Upload skill
```

**Considerations:**
- ✅ Full functionality preserved
- ✅ All scripts/docs included
- ⚠️ No auto-updates (manual)
- ⚠️ Each user uploads separately

### Code → API

**Scenario:** Deploy production skill via API

**Process:**
```bash
# 1. Export API package (optimized)
"Export my-skill for API"

# 2. Upload programmatically
python deploy_skill.py

# 3. Integrate in production
# Use skill_id in API requests
```

**Considerations:**
- ⚠️ Size limit: < 8MB
- ⚠️ No network access
- ⚠️ No runtime pip install
- ✅ Automated deployment
- ✅ Version management

### Desktop/Web → Code

**Scenario:** Import skill to Claude Code

**Process:**
```bash
# 1. Unzip package
unzip skill-name-desktop-v1.0.0.zip -d skill-name-cskill/

# 2. Install in Claude Code
/plugin marketplace add ./skill-name-cskill

# 3. Optional: Add to git
git add skill-name-cskill/
git commit -m "Import skill from Desktop"
```

**Considerations:**
- ✅ Full functionality
- ✅ Can add version control
- ✅ Can share via plugins
- ⚠️ marketplace.json may be missing (create if needed)

---

## 🎯 Optimization Strategies

### For Desktop/Web

**Goal:** Complete, user-friendly package

**Strategy:**
- ✅ Include all documentation
- ✅ Include examples and references
- ✅ Keep README comprehensive
- ✅ Add usage instructions
- ✅ Include all assets

**Package characteristics:**
- Size: 2-5 MB typical
- Focus: User experience
- Documentation: Complete

### For API

**Goal:** Small, execution-focused package

**Strategy:**
- ⚠️ Minimize size (< 8MB)
- ⚠️ Remove heavy docs
- ⚠️ Remove examples
- ✅ Keep essential scripts
- ✅ Keep SKILL.md lean

**Package characteristics:**
- Size: 0.5-2 MB typical
- Focus: Execution efficiency
- Documentation: Minimal

---

## 🛠️ Platform-Specific Issues

### Claude Code Issues

**Issue:** Plugin not loading
- Check marketplace.json syntax
- Verify plugin path correct
- Run `/plugin list` to debug

**Issue:** Skill not activating
- Check SKILL.md frontmatter
- Verify activation patterns
- Test with explicit queries

### Desktop/Web Issues

**Issue:** Upload fails
- Check file size < 10MB
- Verify .zip format correct
- Try re-exporting package

**Issue:** Skill doesn't activate
- Check name ≤ 64 chars
- Check description ≤ 1024 chars
- Verify frontmatter valid

### API Issues

**Issue:** Size limit exceeded
- Export API variant (optimized)
- Remove large files
- Compress assets

**Issue:** Skill execution fails
- No network calls allowed
- No pip install at runtime
- Check sandboxing constraints

**Issue:** Beta headers missing
```python
# REQUIRED headers
betas=[
    "code-execution-2025-08-25",
    "skills-2025-10-02"
]
```

---

## 📋 Feature Comparison

### What Works Everywhere

✅ **Universal Features:**
- SKILL.md core functionality
- Basic Python scripts (with constraints)
- Text-based references
- Asset files (templates, prompts)
- Markdown documentation

### Platform-Specific Features

**Claude Code Only:**
- marketplace.json distribution
- Plugin marketplace
- Git-based updates
- .claude-plugin/ directory

**API Only:**
- Programmatic upload
- Workspace-level sharing
- Version control via API
- Automated deployment

**Desktop/Web Only:**
- Native app integration (Desktop)
- Browser access (Web)
- Offline capability (Desktop)

---

## 🎓 Best Practices

### Development Workflow

**Recommended:** Develop in Claude Code, export for others

```
Claude Code (Development)
    ↓
Create & Test Locally
    ↓
Export Desktop Package → Share with Desktop users
Export API Package → Deploy to production
```

### Distribution Strategy

**For Teams:**
- **Developers**: Claude Code via plugins
- **Others**: Desktop/Web via .zip
- **Production**: API via programmatic deployment

**For Open Source:**
- **Primary**: Claude Code marketplace
- **Releases**: Export packages for Desktop/Web
- **Documentation**: Installation guides for all platforms

---

## 📚 Related Documentation

- **Export Guide**: `export-guide.md` - How to export skills
- **Main README**: `../README.md` - Agent-skill-creator overview
- **API Documentation**: Claude API docs (official)

---

**Generated by:** agent-skill-creator v3.2
**Last updated:** October 2025
