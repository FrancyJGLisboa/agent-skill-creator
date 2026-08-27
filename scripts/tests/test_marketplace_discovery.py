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
            "software_mutation": {"applies": False},
            "data_interfaces": {"applies": False},
            "semantic_contract": {"applies": False},
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


def test_skill_page_links_to_the_generated_verification_report() -> None:
    page = discovery.render_skill_page(entry())
    assert "## Reliability evidence" in page
    assert "[View VERIFICATION.md](skills/finance/revenue-review/VERIFICATION.md)" in page


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
    for field in (
        "environment", "risk", "software_mutation", "data_interfaces",
        "routing_tests"
    ):
        broken = entry()
        broken["discovery"].update(operating)  # type: ignore[union-attr]
        broken["discovery"].pop(field, None)  # type: ignore[index]
        with pytest.raises(discovery.DiscoveryError, match=field):
            discovery.require_operating_contract(broken)


def test_software_mutation_requires_representation_review() -> None:
    item = entry()
    item["discovery"]["software_mutation"] = {"applies": True}  # type: ignore[index]
    with pytest.raises(discovery.DiscoveryError, match="affected_structures"):
        discovery.require_operating_contract(item)


def test_software_mutation_accepts_complete_representation_review() -> None:
    item = entry()
    item["discovery"]["software_mutation"] = {  # type: ignore[index]
        "applies": True,
        "affected_structures": ["Seat", "SeatState"],
        "invariants": ["A seat has exactly one state"],
        "sources_of_truth": ["Seat state: Seat.state"],
        "invalid_states_prevented": ["A seat cannot be held and sold"],
        "state_transitions": ["open -> held", "held -> sold"],
    }
    contract = discovery.require_operating_contract(item)["software_mutation"]
    assert contract["applies"] is True
    assert contract["affected_structures"] == ["Seat", "SeatState"]


def test_structured_data_requires_interface_contract() -> None:
    item = entry()
    item["discovery"]["data_interfaces"] = {"applies": True}  # type: ignore[index]
    with pytest.raises(discovery.DiscoveryError, match="interface_types"):
        discovery.require_operating_contract(item)


def test_structured_data_accepts_complete_interface_contract() -> None:
    item = entry()
    item["discovery"]["data_interfaces"] = {  # type: ignore[index]
        "applies": True,
        "interface_types": ["api"],
        "authoritative_sources": ["CRM OpenAPI specification"],
        "entities": ["Account", "Opportunity"],
        "identifiers": ["Account.id", "Opportunity.account_id"],
        "relationships": ["Opportunity.account_id -> Account.id"],
        "field_semantics": ["Opportunity.amount is decimal account currency"],
        "invariants": ["Closed opportunities have a close_date"],
        "freshness_and_pagination": ["Cursor pagination", "Five-minute cache maximum"],
        "nullability": ["close_date is null before closure"],
        "readiness_checks": ["A safe sample matches the documented schema"],
    }
    contract = discovery.require_operating_contract(item)["data_interfaces"]
    assert contract["applies"] is True
    assert contract["interface_types"] == ["api"]


def semantic_contract() -> dict[str, object]:
    return {
        "applies": True,
        "definitions": [{
            "id": "active-customer",
            "version": "2.1.0",
            "definition": "Customer eligible for commercial active-base reporting",
            "scope": "Direct B2B customers",
            "grain": "customer_id",
            "unit": "customers",
            "source_precedence": ["billing.customer_contract", "crm.account_status"],
            "owner": "commercial-analytics",
            "valid_from": "2026-07-01",
            "last_reviewed": "2026-08-18",
            "review_interval_days": 30,
        }],
        "dependencies": [{"id": "active-customer", "version": "2.1.0"}],
        "ambiguity": {
            "allowed_outcomes": ["answer", "ask", "refuse_unknown"],
            "unresolved_action": "ask",
            "clarification": "Which active-customer context do you mean?",
        },
    }


def test_semantic_meaning_requires_complete_contract() -> None:
    item = entry()
    item["discovery"]["semantic_contract"] = {"applies": True}  # type: ignore[index]
    with pytest.raises(discovery.DiscoveryError, match="definitions"):
        discovery.require_operating_contract(item)


def test_legacy_missing_semantic_contract_defaults_to_not_applicable() -> None:
    item = entry()
    item["discovery"].pop("semantic_contract")  # type: ignore[index]
    assert discovery.require_operating_contract(item)["semantic_contract"] == {
        "applies": False,
    }


def test_semantic_contract_preserves_source_precedence_and_dependencies() -> None:
    item = entry()
    item["discovery"]["semantic_contract"] = semantic_contract()  # type: ignore[index]
    contract = discovery.require_operating_contract(item)["semantic_contract"]
    assert contract["definitions"][0]["source_precedence"] == [
        "billing.customer_contract", "crm.account_status",
    ]
    assert contract["dependencies"] == [{"id": "active-customer", "version": "2.1.0"}]
    assert contract["ambiguity"]["unresolved_action"] == "ask"


def test_ask_outcome_requires_clarification_prompt() -> None:
    item = entry()
    contract = semantic_contract()
    contract["ambiguity"].pop("clarification")  # type: ignore[union-attr]
    item["discovery"]["semantic_contract"] = contract  # type: ignore[index]
    with pytest.raises(discovery.DiscoveryError, match="clarification"):
        discovery.require_operating_contract(item)


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


def test_search_ignores_generic_language_and_weak_single_token_matches() -> None:
    earthquake = entry("earthquake-brief-skill", "Summarize earthquake activity for review")
    earthquake["discovery"]["question"] = "Which earthquakes warrant situational review?"  # type: ignore[index]
    earthquake["discovery"]["trigger"] = ["A user asks to review earthquake activity"]  # type: ignore[index]
    assert discovery.search_skills([earthquake], "Translate a contract to French") == []


def test_search_uses_negative_routing_examples_as_exclusion_evidence() -> None:
    item = entry()
    item["discovery"]["routing_tests"]["should_not_trigger"] = [  # type: ignore[index]
        "Draft a revenue sales email", "Write a sales email", "Prepare customer outreach"
    ]
    assert discovery.search_skills([item], "Write a revenue sales email") == []


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


def test_markdown_page_distinguishes_approval_and_lifecycle() -> None:
    item = entry()
    item["approval_status"] = "approved"
    item["lifecycle"] = "published"
    page = discovery.render_skill_page(item)
    assert "Approval: **approved**" in page
    assert "Lifecycle: **published**" in page


def test_markdown_page_exposes_software_representation_review() -> None:
    item = entry()
    item["discovery"]["software_mutation"] = {  # type: ignore[index]
        "applies": True,
        "affected_structures": ["SeatState"],
        "invariants": ["A seat has exactly one state"],
        "sources_of_truth": ["Seat state: Seat.state"],
        "invalid_states_prevented": ["A seat cannot be held and sold"],
        "state_transitions": ["open -> held", "held -> sold"],
    }
    page = discovery.render_skill_page(item)
    assert "## Software representation review" in page
    assert "### Invariants" in page
    assert "A seat has exactly one state" in page


def test_markdown_page_exposes_data_interface_contract() -> None:
    item = entry()
    item["discovery"]["data_interfaces"] = {  # type: ignore[index]
        "applies": True,
        "interface_types": ["mcp-resource"],
        "authoritative_sources": ["CRM MCP resource schema"],
        "entities": ["Account"],
        "identifiers": ["Account.id"],
        "relationships": ["Account.id identifies one account"],
        "field_semantics": ["Account.arr is annual recurring revenue"],
        "invariants": ["ARR is non-negative"],
        "freshness_and_pagination": ["Cursor pagination; refreshed hourly"],
        "nullability": ["Account.arr is required"],
        "readiness_checks": ["One safe resource sample matches the schema"],
    }
    page = discovery.render_skill_page(item)
    assert "## Data interface contract" in page
    assert "### Authoritative sources" in page
    assert "CRM MCP resource schema" in page


def test_markdown_page_rejects_unsafe_registry_path() -> None:
    item = entry()
    item["path"] = "../secrets"
    with pytest.raises(discovery.DiscoveryError, match="path"):
        discovery.render_skill_page(item)
