"""Plugin manifests: factory .claude-plugin/ files and the generated-skill templates.

Guards the /plugin install path: manifests must be valid JSON, names must match
the SKILL.md frontmatter, and template placeholders must substitute into valid
JSON the way pipeline-phases.md Step 6.5 documents.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from skill_document import SkillDoc  # noqa: E402

PLUGIN_JSON = REPO_ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE_JSON = REPO_ROOT / ".claude-plugin" / "marketplace.json"
TEMPLATE_DIR = REPO_ROOT / "scripts" / "claude-plugin-template"

PLACEHOLDERS = {
    "{{SKILL_NAME}}": "sample-skill",
    "{{SKILL_VERSION}}": "1.0.0",
    "{{SKILL_AUTHOR}}": "Sample Author",
    "{{SKILL_DESCRIPTION}}": "One-line description without quotes",
}


def test_factory_plugin_json_matches_skill_md():
    plugin = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
    doc = SkillDoc.from_path(REPO_ROOT / "SKILL.md")
    assert plugin["name"] == doc.field("name")
    assert plugin["version"] == doc.subfield("metadata", "version")
    assert plugin["description"]
    assert plugin["author"]["name"]


def test_factory_marketplace_json_points_at_plugin():
    marketplace = json.loads(MARKETPLACE_JSON.read_text(encoding="utf-8"))
    plugin = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
    assert marketplace["name"] == plugin["name"]
    assert marketplace["owner"]["name"]
    entries = marketplace["plugins"]
    assert len(entries) == 1
    assert entries[0]["name"] == plugin["name"]
    assert entries[0]["source"] == "./"


@pytest.mark.parametrize("template_name", ["plugin.json", "marketplace.json"])
def test_template_substitutes_to_valid_json(template_name):
    text = (TEMPLATE_DIR / template_name).read_text(encoding="utf-8")
    for placeholder, value in PLACEHOLDERS.items():
        text = text.replace(placeholder, value)
    assert "{{" not in text, f"unsubstituted placeholder left in {template_name}"
    parsed = json.loads(text)
    assert parsed["name"] == "sample-skill"


CROSS_RUNTIME_MANIFESTS = [
    ".codex-plugin/plugin.json",
    ".agents/plugins/marketplace.json",
    ".github/plugin/plugin.json",
    ".github/plugin/marketplace.json",
    ".cursor-plugin/plugin.json",
    ".cursor-plugin/marketplace.json",
    "gemini-extension.json",
]


@pytest.mark.parametrize("rel", CROSS_RUNTIME_MANIFESTS)
def test_cross_runtime_manifest_parses_and_names_match(rel):
    data = json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))
    assert data["name"] == "agent-skill-creator", rel
    if "version" in data:
        doc = SkillDoc.from_path(REPO_ROOT / "SKILL.md")
        assert data["version"] == doc.subfield("metadata", "version"), rel


def test_gemini_context_file_exists():
    data = json.loads((REPO_ROOT / "gemini-extension.json").read_text(encoding="utf-8"))
    context = data.get("contextFileName")
    assert context, "gemini-extension.json must declare contextFileName"
    assert (REPO_ROOT / context).exists(), (
        f"gemini-extension.json points at {context}, which is missing — "
        "apply the staged AGENTS.md before merging"
    )


def test_templates_use_only_documented_placeholders():
    import re

    documented = set(PLACEHOLDERS)
    for template_name in ("plugin.json", "marketplace.json"):
        text = (TEMPLATE_DIR / template_name).read_text(encoding="utf-8")
        found = set(re.findall(r"\{\{[A-Z_]+\}\}", text))
        assert found <= documented, f"{template_name} uses undocumented placeholders: {found - documented}"
