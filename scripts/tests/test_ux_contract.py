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


def test_homepage_markets_reproducible_reliability_evidence() -> None:
    page = read("docs/index.html")
    evidence = read("docs/verification/2026-08-27-live-weather-briefing.md")

    assert "6 regression checks passed" in page
    assert "live API request passed" in page
    assert "local Codex package install recorded" in page
    assert "other runtime compatibility requires separate evidence" in page
    assert "compatible with 17 agent environments" not in page
    assert "View verification evidence" in page
    assert "6 passed, 0 failed, 0 errored, 0 regressed" in evidence


def test_worker_runbook_is_linked_from_readme_and_homepage() -> None:
    runbook = read("docs/WORKER_RUNBOOK.md")
    assert "/agent-skill-creator Every Friday" in runbook
    assert "verification-blocked" in runbook
    assert "docs/WORKER_RUNBOOK.md" in read("README.md")
    assert 'href="WORKER_RUNBOOK.html"' in read("docs/index.html")


def test_public_docs_distinguish_skills_from_rag_mcp_and_runtime() -> None:
    definition = (
        "An Agent Skill is a reusable workflow package that guides an agent from a "
        "recognized situation to a verified outcome. It can use retrieved knowledge, "
        "MCP tools, APIs, deterministic scripts, and agent judgment, but it is not "
        "itself a RAG system, MCP server, or agent runtime."
    )
    distinction = (
        "RAG supplies knowledge. MCP supplies capabilities. The harness supplies "
        "execution. A skill organizes them into a governed path toward a verified "
        "outcome."
    )
    for path in ("README.md", "docs/PRODUCT_SCOPE.md", "docs/index.html"):
        normalized = " ".join(re.sub(r"<[^>]+>", " ", read(path)).split())
        assert definition in normalized, f"{path} is missing the canonical definition"
        assert distinction in normalized, f"{path} is missing the canonical distinction"


def test_public_docs_state_semantic_authority_boundary_and_evidence_limit() -> None:
    readme = read("README.md").lower()
    marketplace = read("docs/TEAM_MARKETPLACE.md").lower()
    page = re.sub(r"<[^>]+>", " ", read("docs/index.html")).lower()

    assert "humans establish meaning" in readme
    assert "domain owner" in marketplace and "six checks" in marketplace
    assert "agents may structure, document, test, and apply organizational meaning" in page
    assert "no accuracy improvement is claimed" in page
    assert "semantic-contract experiment" in page


def test_public_onboarding_does_not_require_a_perfect_prompt_or_schema() -> None:
    readme = " ".join(read("README.md").lower().split())
    page = " ".join(re.sub(r"<[^>]+>", " ", read("docs/index.html")).lower().split())
    factory = read("SKILL.md").lower()

    assert "does not expect you to know the correct prompt or semantic contract" in readme
    assert "one bounded question at a time" in readme
    assert "no perfect prompt required" in page
    assert "agent proposals cannot silently become organizational truth" in page
    assert "structured interview gate" in factory
    assert "structured_interview.py gate" in factory


def test_public_surfaces_state_reasoning_and_reproducibility_boundary() -> None:
    readme = " ".join(read("README.md").lower().replace(">", " ").split())
    page = " ".join(re.sub(r"<[^>]+>", " ", read("docs/index.html")).lower().split())

    for surface in (readme, page):
        assert "reason where interpretation is necessary" in surface
        assert "deterministic controls where reproducibility matters" in surface
        assert "rather than promising identical outputs" in surface


def test_public_onboarding_shows_the_resumable_interview_flow() -> None:
    readme = read("README.md")
    page = read("docs/index.html")

    for label in (
        "Messy problem",
        "Agent inspects evidence",
        "Proposed / conflicting meanings",
        "Human authority decision",
        "Interview READY",
        "Build, prove, publish",
    ):
        assert label in readme
    assert 'class="skill-flow skill-flow--interview"' in page
    assert "Missing evidence or authority remains BLOCKED and resumable." in page


def test_marketplace_governance_begins_with_a_ready_human_authorized_interview() -> None:
    marketplace = " ".join(read("docs/TEAM_MARKETPLACE.md").split())

    assert "Governance begins before generation" in marketplace
    assert "Only a `READY` interview permits skill generation" in marketplace
    assert "evidence-and-authority trail" in marketplace
    assert "does not silently supply missing business authority" in marketplace
    assert "../references/structured-interview.md" in marketplace


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
