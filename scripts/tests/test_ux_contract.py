"""Regression tests for the first-skill success journey.

These checks protect behavioral agreements shared by the factory instructions and
the public onboarding. They intentionally avoid pinning full prose or page layout.
"""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from platforms import list_supported_platforms  # noqa: E402
from skill_document import SkillDoc  # noqa: E402


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class _PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.labels: set[str] = set()
        self.live_regions = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"] or "")
        if tag == "label" and values.get("for"):
            self.labels.add(values["for"] or "")
        if values.get("aria-live"):
            self.live_regions += 1


def test_completion_states_are_consistent_across_factory_references() -> None:
    expected = {"verified", "verification-blocked", "installed", "failed"}
    sources = (
        read("SKILL.md"),
        read("references/pipeline-phases.md"),
        read("references/interactive-mode.md"),
    )

    for source in sources:
        assert expected <= {f"{state}" for state in expected if state in source}

    interactive = sources[2]
    assert "Would you like to install it now?" not in interactive
    assert "Run: ./install.sh" not in interactive


def test_verified_requires_representative_execution_and_safe_side_effects() -> None:
    skill = read("SKILL.md")
    pipeline = read("references/pipeline-phases.md")

    assert "representative safe run" in skill
    assert "representative run" in pipeline
    for prohibited_effect in ("send", "publish", "purchase", "production data"):
        assert prohibited_effect in pipeline.lower()


def test_public_onboarding_is_human_centered_and_result_first() -> None:
    readme = read("README.md")
    page = read("docs/index.html")

    assert readme.index("## Create your first skill") < readme.index("## What happens behind")
    assert page.index('id="start"') < page.index('id="trust"')
    for source in (readme, page, read("SKILL.md")):
        assert "humans are cognitively incapable" not in source.lower()
        assert "dark factory" not in source.lower()


def test_public_docs_present_the_normalized_graph_release_gate() -> None:
    command = "python3 scripts/skill_graph.py run ./the-skill/ --jobs 4"
    readme = read("README.md")
    install = read("docs/INSTALL.md")
    marketplace = read("docs/TEAM_MARKETPLACE.md")
    page = read("docs/index.html")

    assert "every_expected_is_reachable" in readme
    assert "deterministic_multistep_has_orchestrator" in readme
    assert command in install
    assert "both structural requirements, all" in marketplace
    assert "four checks, and the representative run pass" in marketplace
    assert "skill graph" in page.lower()
    assert 'class="skill-flow"' in page
    for label in (
        "Artifacts",
        "Skill graph",
        "Structural requirements",
        "Parallel checks",
        "Representative run",
    ):
        assert label in page


def test_public_docs_use_one_plain_language_graph_explanation() -> None:
    canonical = (
        "Every skill is checked as one connected system. The skill graph links its "
        "instructions, scripts, evaluations, and expected outputs. Two structural "
        "requirements confirm that every expected result is tested and every "
        "predictable multi-step workflow has one reliable entry point. Four "
        "checks—specification, pipeline, security, and evaluation schema—run in "
        "parallel. Finally, a representative run proves that the skill produces a "
        "useful result."
    )
    public_docs = {
        "README.md": read("README.md"),
        "docs/INSTALL.md": read("docs/INSTALL.md"),
        "docs/TEAM_MARKETPLACE.md": read("docs/TEAM_MARKETPLACE.md"),
        "docs/index.html": re.sub(r"<[^>]+>", " ", read("docs/index.html")),
    }
    deprecated_phrases = (
        "validation, pipeline checks, scan, evals",
        "graph constraints and gates",
        "parallel spec, pipeline, security, and eval-schema",
    )

    for path, source in public_docs.items():
        without_markdown_quotes = re.sub(r"(?m)^>\s?", "", source)
        normalized = " ".join(without_markdown_quotes.split())
        assert canonical in normalized, f"{path} is missing the canonical explanation"
        for phrase in deprecated_phrases:
            assert phrase not in normalized.lower(), f"{path} uses deprecated wording: {phrase}"


def test_website_platform_chooser_matches_canonical_registry() -> None:
    page = read("docs/index.html")
    chooser_block = page.split("var platforms = [", 1)[1].split("];", 1)[0]
    chooser_names = re.findall(r"\['([^']+)',\s*'[^']+'\]", chooser_block)

    assert chooser_names == list_supported_platforms()
    assert "<noscript>" in page
    assert "bootstrap.sh" in page
    assert "bootstrap.ps1" in page


def test_website_controls_have_labels_unique_ids_and_live_feedback() -> None:
    parser = _PageParser()
    parser.feed(read("docs/index.html"))

    assert len(parser.ids) == len(set(parser.ids))
    assert {"tool-select", "os-select"} <= parser.labels
    assert parser.live_regions >= 1


def test_release_metadata_stays_in_sync() -> None:
    version = SkillDoc.from_path(ROOT / "SKILL.md").subfield("metadata", "version")
    assert version == "6.1.0"

    json_manifests = (
        ".claude-plugin/plugin.json",
        ".codex-plugin/plugin.json",
        ".cursor-plugin/plugin.json",
        ".github/plugin/plugin.json",
        "gemini-extension.json",
    )
    for path in json_manifests:
        assert json.loads(read(path))["version"] == version

    assert f"version: {version}" in read("CITATION.cff")
