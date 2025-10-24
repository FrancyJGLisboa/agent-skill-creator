#!/usr/bin/env python3
"""
Cross-Platform Export Utilities for Agent-Skill-Creator

Packages Claude Code skills for Desktop/Web/API use with versioning and validation.
"""

import os
import sys
import zipfile
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Directories and files to exclude from exports
EXCLUDE_DIRS = {
    '.git', '__pycache__', 'node_modules', '.claude-plugin',
    'venv', 'env', '.venv', '.pytest_cache', '.mypy_cache',
    'dist', 'build', '*.egg-info'
}

EXCLUDE_FILES = {
    '.DS_Store', '.gitignore', 'Thumbs.db', '*.pyc', '*.pyo',
    '.env', 'credentials.json', '*.log', '.python-version'
}

# API package size limit (8MB per Claude API requirements)
MAX_API_SIZE_MB = 8
MAX_API_SIZE_BYTES = MAX_API_SIZE_MB * 1024 * 1024

# SKILL.md validation limits
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024


def get_skill_version(skill_path: str, override_version: str = None) -> str:
    """
    Determine skill version from git tags, SKILL.md, or use default.

    Args:
        skill_path: Path to skill directory
        override_version: User-specified version (takes precedence)

    Returns:
        Version string in format "vX.Y.Z"
    """
    if override_version:
        return override_version if override_version.startswith('v') else f'v{override_version}'

    # Try git tags first
    try:
        os.chdir(skill_path)
        result = subprocess.run(
            ['git', 'describe', '--tags', '--abbrev=0'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            return version if version.startswith('v') else f'v{version}'
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass

    # Try SKILL.md frontmatter
    skill_md_path = os.path.join(skill_path, 'SKILL.md')
    if os.path.exists(skill_md_path):
        try:
            with open(skill_md_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Look for version: in frontmatter
                if content.startswith('---'):
                    frontmatter_end = content.find('---', 3)
                    if frontmatter_end > 0:
                        frontmatter = content[3:frontmatter_end]
                        for line in frontmatter.split('\n'):
                            if line.strip().startswith('version:'):
                                version = line.split(':', 1)[1].strip()
                                return version if version.startswith('v') else f'v{version}'
        except Exception:
            pass

    # Default version
    return 'v1.0.0'


def validate_skill_structure(skill_path: str) -> Tuple[bool, List[str]]:
    """
    Validate that skill has required structure for export.

    Args:
        skill_path: Path to skill directory

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []

    # Check if path exists and is directory
    if not os.path.exists(skill_path):
        issues.append(f"Path does not exist: {skill_path}")
        return False, issues

    if not os.path.isdir(skill_path):
        issues.append(f"Path is not a directory: {skill_path}")
        return False, issues

    # Check for SKILL.md
    skill_md_path = os.path.join(skill_path, 'SKILL.md')
    if not os.path.exists(skill_md_path):
        issues.append("SKILL.md not found (required)")
        return False, issues

    # Validate SKILL.md frontmatter
    try:
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

            if not content.startswith('---'):
                issues.append("SKILL.md missing frontmatter (must start with ---)")
            else:
                # Extract frontmatter
                frontmatter_end = content.find('---', 3)
                if frontmatter_end == -1:
                    issues.append("SKILL.md frontmatter not closed (missing second ---)")
                else:
                    frontmatter = content[3:frontmatter_end]

                    # Check for required fields
                    has_name = False
                    has_description = False
                    name_length = 0
                    desc_length = 0

                    for line in frontmatter.split('\n'):
                        line = line.strip()
                        if line.startswith('name:'):
                            has_name = True
                            name = line.split(':', 1)[1].strip()
                            name_length = len(name)
                            if name_length > MAX_NAME_LENGTH:
                                issues.append(f"name too long: {name_length} chars (max {MAX_NAME_LENGTH})")
                        elif line.startswith('description:'):
                            has_description = True
                            desc = line.split(':', 1)[1].strip()
                            desc_length = len(desc)
                            if desc_length > MAX_DESCRIPTION_LENGTH:
                                issues.append(f"description too long: {desc_length} chars (max {MAX_DESCRIPTION_LENGTH})")

                    if not has_name:
                        issues.append("SKILL.md missing 'name:' field in frontmatter")
                    if not has_description:
                        issues.append("SKILL.md missing 'description:' field in frontmatter")

    except Exception as e:
        issues.append(f"Error reading SKILL.md: {str(e)}")

    return len(issues) == 0, issues


def should_include_file(file_path: str, filename: str) -> bool:
    """
    Determine if a file should be included in export.

    Args:
        file_path: Full path to file
        filename: Just the filename

    Returns:
        True if file should be included
    """
    # Check excluded filenames
    if filename in EXCLUDE_FILES:
        return False

    # Check excluded patterns
    for pattern in EXCLUDE_FILES:
        if '*' in pattern:
            extension = pattern.replace('*', '')
            if filename.endswith(extension):
                return False

    # Check for sensitive files
    if filename in {'.env', 'credentials.json', 'secrets.json', 'api_keys.json'}:
        return False

    return True


def get_directory_size(path: str) -> int:
    """
    Calculate total size of directory in bytes.

    Args:
        path: Directory path

    Returns:
        Total size in bytes
    """
    total = 0
    for root, dirs, files in os.walk(path):
        # Filter excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            if should_include_file(os.path.join(root, file), file):
                try:
                    total += os.path.getsize(os.path.join(root, file))
                except OSError:
                    pass
    return total


def create_export_package(
    skill_path: str,
    output_dir: str,
    variant: str = 'desktop',
    version: str = 'v1.0.0',
    skill_name: str = None
) -> Dict:
    """
    Create optimized export package for specified variant.

    Args:
        skill_path: Path to skill directory
        output_dir: Where to save the .zip file
        variant: 'desktop' or 'api'
        version: Version string (e.g., 'v1.0.0')
        skill_name: Override skill name (default: directory name)

    Returns:
        Dict with 'success', 'zip_path', 'size_mb', 'files_included', 'message'
    """
    if skill_name is None:
        skill_name = os.path.basename(os.path.abspath(skill_path))

    # Create output filename
    zip_filename = f"{skill_name}-{variant}-{version}.zip"
    zip_path = os.path.join(output_dir, zip_filename)

    files_included = []
    total_size = 0

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
            for root, dirs, files in os.walk(skill_path):
                # Filter excluded directories
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

                # For API variant, exclude .claude-plugin
                if variant == 'api' and '.claude-plugin' in dirs:
                    dirs.remove('.claude-plugin')

                for file in files:
                    if not should_include_file(os.path.join(root, file), file):
                        continue

                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, skill_path)

                    # For API variant, apply additional filtering
                    if variant == 'api':
                        # Skip large documentation files
                        if file.endswith('.md') and file not in {'SKILL.md', 'README.md'}:
                            continue
                        # Skip example files
                        if 'examples' in arcname.lower():
                            continue

                    try:
                        zipf.write(file_path, arcname)
                        files_included.append(arcname)
                        total_size += os.path.getsize(file_path)
                    except Exception as e:
                        print(f"Warning: Could not add {arcname}: {e}", file=sys.stderr)

        # Check final size
        final_size = os.path.getsize(zip_path)
        size_mb = final_size / (1024 * 1024)

        # Warn if API package is too large
        if variant == 'api' and final_size > MAX_API_SIZE_BYTES:
            return {
                'success': False,
                'zip_path': zip_path,
                'size_mb': size_mb,
                'files_included': files_included,
                'message': f"API package too large: {size_mb:.2f} MB (max {MAX_API_SIZE_MB} MB)"
            }

        return {
            'success': True,
            'zip_path': zip_path,
            'size_mb': size_mb,
            'files_included': files_included,
            'message': f"Package created successfully: {len(files_included)} files, {size_mb:.2f} MB"
        }

    except Exception as e:
        return {
            'success': False,
            'zip_path': None,
            'size_mb': 0,
            'files_included': [],
            'message': f"Error creating package: {str(e)}"
        }


def generate_installation_guide(
    skill_name: str,
    version: str,
    desktop_package: Dict = None,
    api_package: Dict = None,
    output_dir: str = None
) -> str:
    """
    Generate platform-specific installation guide.

    Args:
        skill_name: Name of the skill
        version: Version string
        desktop_package: Desktop package info dict (optional)
        api_package: API package info dict (optional)
        output_dir: Where to save the guide

    Returns:
        Path to generated installation guide
    """
    guide_filename = f"{skill_name}-{version}_INSTALL.md"
    guide_path = os.path.join(output_dir, guide_filename)

    # Build guide content
    content = f"""# {skill_name} - Installation Guide

**Version:** {version}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📦 Export Packages

"""

    if desktop_package and desktop_package['success']:
        content += f"""### Desktop/Web Package

**File:** `{os.path.basename(desktop_package['zip_path'])}`
**Size:** {desktop_package['size_mb']:.2f} MB
**Files:** {len(desktop_package['files_included'])} files included

✅ Optimized for Claude Desktop and claude.ai manual upload

"""

    if api_package and api_package['success']:
        content += f"""### API Package

**File:** `{os.path.basename(api_package['zip_path'])}`
**Size:** {api_package['size_mb']:.2f} MB
**Files:** {len(api_package['files_included'])} files included

✅ Optimized for programmatic Claude API integration

"""

    content += """---

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

"""

    if desktop_package and desktop_package['success']:
        content += f"""**Desktop Package:**
- SKILL.md (core functionality)
- Complete scripts/ directory
- Full references/ documentation
- All assets/ and templates
- README.md and requirements.txt

"""

    if api_package and api_package['success']:
        content += f"""**API Package:**
- SKILL.md (required)
- Essential scripts only
- Minimal documentation (execution-focused)
- Size-optimized (< 8MB)

"""

    content += """### What's Excluded (Security)

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
"""

    # Write guide to file
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return guide_path


def export_skill(
    skill_path: str,
    variants: List[str] = ['desktop', 'api'],
    version_override: str = None,
    output_dir: str = None
) -> Dict:
    """
    Main export function - validates, packages, and generates guides.

    Args:
        skill_path: Path to skill directory
        variants: List of variants to create ('desktop', 'api', or both)
        version_override: User-specified version (optional)
        output_dir: Where to save exports (default: exports/ in parent dir)

    Returns:
        Dict with export results
    """
    # Normalize path
    skill_path = os.path.abspath(skill_path)
    skill_name = os.path.basename(skill_path)

    # Determine output directory
    if output_dir is None:
        # Use exports/ in parent directory
        parent_dir = os.path.dirname(skill_path)
        output_dir = os.path.join(parent_dir, 'exports')

    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)

    # Validate skill structure
    print("🔍 Validating skill structure...")
    valid, issues = validate_skill_structure(skill_path)
    if not valid:
        return {
            'success': False,
            'message': 'Skill validation failed',
            'issues': issues
        }
    print("✅ Skill structure valid")

    # Determine version
    version = get_skill_version(skill_path, version_override)
    print(f"📌 Version: {version}")

    # Create packages
    results = {
        'success': True,
        'version': version,
        'packages': {}
    }

    if 'desktop' in variants:
        print(f"\n🔨 Creating Desktop/Web package...")
        desktop_result = create_export_package(
            skill_path, output_dir, 'desktop', version, skill_name
        )
        results['packages']['desktop'] = desktop_result
        if desktop_result['success']:
            print(f"✅ Desktop package: {os.path.basename(desktop_result['zip_path'])} ({desktop_result['size_mb']:.2f} MB)")
        else:
            print(f"❌ Desktop package failed: {desktop_result['message']}")
            results['success'] = False

    if 'api' in variants:
        print(f"\n🔨 Creating API package...")
        api_result = create_export_package(
            skill_path, output_dir, 'api', version, skill_name
        )
        results['packages']['api'] = api_result
        if api_result['success']:
            print(f"✅ API package: {os.path.basename(api_result['zip_path'])} ({api_result['size_mb']:.2f} MB)")
        else:
            print(f"❌ API package failed: {api_result['message']}")
            results['success'] = False

    # Generate installation guide
    if results['success']:
        print(f"\n📄 Generating installation guide...")
        guide_path = generate_installation_guide(
            skill_name,
            version,
            desktop_package=results['packages'].get('desktop'),
            api_package=results['packages'].get('api'),
            output_dir=output_dir
        )
        results['guide_path'] = guide_path
        print(f"✅ Installation guide: {os.path.basename(guide_path)}")

    return results


def main():
    """CLI interface for export_utils.py"""
    if len(sys.argv) < 2:
        print("""
Usage: python export_utils.py <skill-path> [options]

Arguments:
  skill-path              Path to skill directory

Options:
  --variant VARIANT       Export variant: desktop, api, or both (default: both)
  --version VERSION       Override version (default: auto-detect)
  --output-dir DIR        Output directory (default: exports/)

Examples:
  python export_utils.py ./my-skill-cskill
  python export_utils.py ./my-skill-cskill --variant desktop
  python export_utils.py ./my-skill-cskill --version 2.0.1
  python export_utils.py ./my-skill-cskill --variant api --output-dir ./dist
""")
        sys.exit(1)

    skill_path = sys.argv[1]

    # Parse options
    variants = ['desktop', 'api']  # default: both
    version_override = None
    output_dir = None

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--variant':
            variant_arg = sys.argv[i + 1]
            if variant_arg == 'both':
                variants = ['desktop', 'api']
            else:
                variants = [variant_arg]
            i += 2
        elif sys.argv[i] == '--version':
            version_override = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--output-dir':
            output_dir = sys.argv[i + 1]
            i += 2
        else:
            print(f"Unknown option: {sys.argv[i]}")
            sys.exit(1)

    # Run export
    print(f"\n🚀 Exporting skill: {os.path.basename(skill_path)}\n")
    results = export_skill(skill_path, variants, version_override, output_dir)

    # Print summary
    print(f"\n{'='*60}")
    if results['success']:
        print("✅ Export completed successfully!")
        print(f"\n📦 Packages created:")
        for variant, package in results['packages'].items():
            if package['success']:
                print(f"   - {variant.capitalize()}: {os.path.basename(package['zip_path'])}")
        if 'guide_path' in results:
            print(f"\n📄 Installation guide: {os.path.basename(results['guide_path'])}")
        print(f"\n🎯 All files saved to: {output_dir or 'exports/'}")
    else:
        print("❌ Export failed!")
        if 'issues' in results:
            print("\nIssues found:")
            for issue in results['issues']:
                print(f"   - {issue}")
    print(f"{'='*60}\n")

    sys.exit(0 if results['success'] else 1)


if __name__ == '__main__':
    main()
