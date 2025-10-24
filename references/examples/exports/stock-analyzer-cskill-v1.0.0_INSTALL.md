# stock-analyzer-cskill - Installation Guide

**Version:** v1.0.0
**Generated:** 2025-10-24 12:56:28

---

## 📦 Export Packages

### Desktop/Web Package

**File:** `stock-analyzer-cskill-desktop-v1.0.0.zip`
**Size:** 0.01 MB
**Files:** 4 files included

✅ Optimized for Claude Desktop and claude.ai manual upload

### API Package

**File:** `stock-analyzer-cskill-api-v1.0.0.zip`
**Size:** 0.01 MB
**Files:** 4 files included

✅ Optimized for programmatic Claude API integration

---

## 🚀 Installation Instructions

### For Claude Desktop

1. **Locate the Desktop package**
   - File: `{skill}-desktop-{version}.zip`

2. **Open Claude Desktop**
   - Launch the Claude Desktop application

3. **Navigate to Skills settings**
   - Go to: **Settings → Capabilities → Skills**

4. **Upload the skill**
   - Click: **Upload skill**
   - Select the desktop package .zip file
   - Wait for upload confirmation

5. **Verify installation**
   - The skill should now appear in your Skills list
   - Try using it with a relevant query

✅ **Your skill is now available in Claude Desktop!**

---

### For claude.ai (Web Interface)

1. **Locate the Desktop package**
   - File: `{skill}-desktop-{version}.zip`
   - (Same package as Desktop - optimized for both)

2. **Visit claude.ai**
   - Open https://claude.ai in your browser
   - Log in to your account

3. **Open Settings**
   - Click your profile icon
   - Select **Settings**

4. **Navigate to Skills**
   - Click on the **Skills** section

5. **Upload the skill**
   - Click: **Upload skill**
   - Select the desktop package .zip file
   - Confirm the upload

6. **Start using**
   - Create a new conversation
   - The skill will activate automatically when relevant

✅ **Your skill is now available at claude.ai!**

---

### For Claude API (Programmatic Integration)

1. **Locate the API package**
   - File: `{skill}-api-{version}.zip`
   - Optimized for API use (smaller, execution-focused)

2. **Install required packages**
   ```bash
   pip install anthropic
   ```

3. **Upload skill programmatically**
   ```python
   import anthropic

   client = anthropic.Anthropic(api_key="your-api-key")

   # Upload the skill
   with open('{skill}-api-{version}.zip', 'rb') as f:
       skill = client.skills.create(
           file=f,
           name="{skill}"
       )

   print(f"Skill uploaded! ID: {{skill.id}}")
   ```

4. **Use in API requests**
   ```python
   response = client.messages.create(
       model="claude-sonnet-4",
       messages=[
           {{"role": "user", "content": "Your query here"}}
       ],
       container={{
           "type": "custom_skill",
           "skill_id": skill.id
       }},
       betas=[
           "code-execution-2025-08-25",
           "skills-2025-10-02"
       ]
   )

   print(response.content)
   ```

5. **Important API requirements**
   - Must include beta headers: `code-execution-2025-08-25` and `skills-2025-10-02`
   - Maximum 8 skills per request
   - Skills run in isolated containers (no network access, no pip install)

✅ **Your skill is now integrated with the Claude API!**

---

## 📋 Platform Comparison

| Feature | Claude Code | Desktop/Web | Claude API |
|---------|-------------|-------------|------------|
| **Installation** | Plugin command | Manual upload | Programmatic |
| **Updates** | Git pull | Re-upload .zip | New upload |
| **Version Control** | ✅ Native | ⚠️ Manual | ✅ Versioned |
| **Team Sharing** | ✅ Via plugins | ❌ Individual | ✅ Via API |
| **marketplace.json** | ✅ Used | ❌ Ignored | ❌ Not used |

---

## ⚙️ Technical Details

### What's Included

**Desktop Package:**
- SKILL.md (core functionality)
- Complete scripts/ directory
- Full references/ documentation
- All assets/ and templates
- README.md and requirements.txt

**API Package:**
- SKILL.md (required)
- Essential scripts only
- Minimal documentation (execution-focused)
- Size-optimized (< 8MB)

### What's Excluded (Security)

For both packages:
- `.git/` (version control history)
- `__pycache__/` (compiled Python)
- `.env` files (environment variables)
- `credentials.json` (API keys/secrets)
- `.DS_Store` (system metadata)

For API package additionally:
- `.claude-plugin/` (Claude Code specific)
- Large documentation files
- Example files (size optimization)

---

## 🔧 Troubleshooting

### Upload fails with "File too large"

**Desktop/Web:**
- Maximum size varies by platform
- Try the API package instead (smaller)
- Contact support if needed

**API:**
- Maximum: 8MB
- The API package is already optimized
- May need to reduce documentation or scripts

### Skill doesn't activate

**Check:**
1. SKILL.md has valid frontmatter
2. `name:` field is present and ≤ 64 characters
3. `description:` field is present and ≤ 1024 characters
4. Description clearly explains when to use the skill

### API errors

**Common issues:**
- Missing beta headers (required!)
- Skill ID incorrect (check `skill.id` after upload)
- Network/pip install attempted (not allowed in API environment)

---

## 📚 Additional Resources

- **Export Guide:** See `references/export-guide.md` in the main repository
- **Cross-Platform Guide:** See `references/cross-platform-guide.md`
- **Main Documentation:** See the main README.md

---

## ✅ Verification Checklist

After installation, verify:

- [ ] Skill appears in Skills list
- [ ] Skill activates with relevant queries
- [ ] Scripts execute correctly
- [ ] Documentation is accessible
- [ ] No error messages on activation

---

**Need help?** Refer to the platform-specific documentation or the main repository guides.

**Generated by:** agent-skill-creator v3.2 cross-platform export system
