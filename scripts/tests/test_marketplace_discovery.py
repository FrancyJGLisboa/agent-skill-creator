"""Outcome-oriented discovery and skill-page contracts."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import marketplace_discovery as discovery  # noqa: E402


def entry(name: str = "revenue-review", outcome: str = "Prepare a monthly revenue review") -> dict[str, object]:
    return {
        "name": name,
        "department": "finance",
        "version": "1.2.3",
        "description": "Analyze revenue trends and prepare a concise executive report.",
        "path": f"skills/finance/{name}",
        "lifecycle_state": "published",
        "discovery": {
            "question": "Why did monthly revenue deviate from plan?",
            "trigger": ["Monthly close data is available"],
            "decision": ["Escalate material variances", "Accept the reported result"],
            "evidence": ["Revenue ledger", "Approved operating plan"],
            "success_measure": "Leadership can explain and act on every material variance.",
            "outcome": outcome,
            "intended_users": ["finance analysts", "revenue leaders"],
            "input_types": ["CSV", "spreadsheet"],
            "output_artifacts": ["executive Markdown report"],
            "use_cases": ["monthly close", "board reporting"],
            "examples": [{"invocation": f"/{name} revenue.csv", "description": "Review one month of revenue."}],
            "permissions_systems": ["Read local input files", "No network access"],
            "typical_completion_time": "2-5 minutes",
            "compatibility": {
                "declared": ["codex", "cursor"],
                "certified": [{"platform": "codex", "passed": True, "version": "1.2.3"}],
            },
            "support_tier": "supported",
            "environment": {
                "documentation_sources": ["Finance schema"],
                "data_sources": ["Revenue ledger"],
                "required_capabilities": ["Read local input files"],
                "readiness_checks": ["Revenue columns exist"],
            },
            "risk": {"tier": "low", "permissions": ["Read local input files"],
                     "mutation_boundary": "read-only", "approval_required": []},
            "routing_tests": {
                "should_trigger": ["Review monthly revenue", "Explain revenue variance", "Analyze revenue plan"],
                "should_not_trigger": ["Write sales email", "Merge pull request", "Delete customer account"],
            },
        },
    }


def test_normalize_preserves_all_required_discovery_metadata() -> None:
    normalized = discovery.normalize_discovery(entry())
    assert set(normalized) == set(discovery.DISCOVERY_FIELDS)
    assert normalized["outcome"] == "Prepare a monthly revenue review"
    assert normalized["question"] == "Why did monthly revenue deviate from plan?"
    assert normalized["examples"][0]["invocation"].startswith("/revenue-review")
    assert normalized["compatibility"]["certified"] == ["codex"]
    assert discovery.search_skills([entry()], "monthly revenue")[0]["question"] == (
        "Why did monthly revenue deviate from plan?"
    )


def test_backward_compatible_defaults_are_explicit_and_low_confidence() -> None:
    legacy = {"name": "old-skill", "version": "1.0.0", "description": "Legacy helper", "approval_status": "approved"}
    normalized = discovery.normalize_discovery(legacy)
    assert normalized["outcome"] == "Not provided"
    assert normalized["support_tier"] == "community"
    assert normalized["metadata_completeness"] == 0
    results = discovery.search_skills([legacy, entry()], "revenue")
    assert results[0]["name"] == "revenue-review"


@pytest.mark.parametrize("tier", ["supported", "community", "deprecated"])
def test_support_tiers_are_normalized(tier: str) -> None:
    item = entry()
    item["discovery"]["support_tier"] = tier  # type: ignore[index]
    assert discovery.normalize_discovery(item)["support_tier"] == tier


def test_invalid_structured_values_fail_closed() -> None:
    item = entry()
    item["discovery"]["examples"] = [{"invocation": "../escape", "description": "bad"}]  # type: ignore[index]
    with pytest.raises(discovery.DiscoveryError, match="invocation"):
        discovery.normalize_discovery(item)


@pytest.mark.parametrize("field", ["question", "trigger", "decision", "evidence", "success_measure"])
def test_required_decision_contract_fails_when_missing(field: str) -> None:
    item = entry()
    item["discovery"].pop(field)  # type: ignore[index]
    with pytest.raises(discovery.DiscoveryError, match=field):
        discovery.require_decision_contract(item)


def test_operating_contract_requires_environment_risk_and_routing() -> None:
    operating = {
        "environment": {"documentation_sources": ["Docs"], "data_sources": ["Input"],
                        "required_capabilities": ["Read input"],
                        "readiness_checks": ["Input exists"]},
        "risk": {"tier": "low", "permissions": ["Read input"],
                 "mutation_boundary": "read-only", "approval_required": []},
        "routing_tests": {"should_trigger": ["Positive one", "Positive two", "Positive three"],
                          "should_not_trigger": ["Negative one", "Negative two", "Negative three"]},
    }
    for field in ("environment", "risk", "routing_tests"):
        broken = entry()
        broken["discovery"].update(operating)  # type: ignore[union-attr]
        broken["discovery"].pop(field, None)  # type: ignore[index]
        with pytest.raises(discovery.DiscoveryError, match=field):
            discovery.require_operating_contract(broken)


def test_operating_contract_accepts_bounded_read_only_skill() -> None:
    item = entry()
    item["discovery"].update({  # type: ignore[union-attr]
        "environment": {
            "documentation_sources": ["Fixture docs"],
            "data_sources": ["Fixture input"],
            "required_capabilities": ["Read fixture input"],
            "readiness_checks": ["Fixture input exists"],
        },
        "risk": {"tier": "low", "permissions": ["Read fixture input"],
                 "mutation_boundary": "read-only", "approval_required": []},
        "routing_tests": {
            "should_trigger": ["Review revenue", "Explain revenue", "Report revenue"],
            "should_not_trigger": ["Write email", "Merge code", "Delete ledger"],
        },
    })
    assert discovery.require_operating_contract(item)["risk"]["tier"] == "low"


def test_search_prioritizes_outcome_over_name_and_description() -> None:
    outcome_match = entry("close-helper", "Prepare quarterly tax filings")
    name_match = entry("tax-filings-tool", "Prepare generic finance summaries")
    name_match["description"] = "Tax filings tax filings"
    results = discovery.search_skills([name_match, outcome_match], "quarterly tax filings")
    assert [result["name"] for result in results] == ["close-helper", "tax-filings-tool"]
    assert results[0]["score"] > results[1]["score"]


def test_search_uses_use_cases_description_and_name_with_deterministic_ties() -> None:
    beta = entry("beta-skill", "Unrelated output")
    alpha = entry("alpha-skill", "Unrelated output")
    for item in (beta, alpha):
        item["discovery"]["use_cases"] = ["monthly close"]  # type: ignore[index]
    results = discovery.search_skills([beta, alpha], "monthly close")
    assert [result["name"] for result in results] == ["alpha-skill", "beta-skill"]


def test_search_filters_certified_platform_and_support_tier() -> None:
    supported = entry()
    community = entry("community-skill", "Prepare a monthly revenue review")
    community["discovery"]["support_tier"] = "community"  # type: ignore[index]
    assert [r["name"] for r in discovery.search_skills([community, supported], "revenue", platform="codex", support_tier="supported")] == ["revenue-review"]
    assert discovery.search_skills([supported], "revenue", platform="cursor") == []


def test_portfolio_evaluation_runs_positive_and_negative_routes() -> None:
    report = discovery.evaluate_portfolio([entry()])
    assert report == {"status": "passed", "skills": 1, "queries": 6, "failures": []}


@pytest.mark.parametrize("state", ["draft", "in-review", "approved", "quarantined", "deprecated", "retired"])
def test_search_excludes_non_installable_lifecycle_states(state: str) -> None:
    item = entry()
    item["lifecycle_state"] = state
    assert discovery.search_skills([item], "revenue") == []


def test_legacy_approved_entry_remains_installable() -> None:
    item = entry()
    item.pop("lifecycle_state")
    item["approval_status"] = "approved"
    assert discovery.search_skills([item], "revenue")


def test_markdown_page_is_structured_deterministic_and_safe() -> None:
    item = entry()
    item["discovery"]["outcome"] = "Create [report](javascript:alert(1))\n# injected"  # type: ignore[index]
    item["discovery"]["examples"] = [{"invocation": "/revenue-review ``` evil", "description": "Safe example"}]  # type: ignore[index]
    page = discovery.render_skill_page(item)
    assert page == discovery.render_skill_page(item)
    assert "## Outcome" in page and "## Inputs and outputs" in page
    assert "## Compatibility and support" in page and "## Examples" in page
    assert "javascript:" not in page
    assert "\n# injected" not in page
    assert "```" not in page


def test_markdown_page_rejects_unsafe_registry_path() -> None:
    item = entry()
    item["path"] = "../secrets"
    with pytest.raises(discovery.DiscoveryError, match="path"):
        discovery.render_skill_page(item)
