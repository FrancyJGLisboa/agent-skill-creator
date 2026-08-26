"""Tests for the resumable, evidence-backed workflow interview."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import structured_interview as interview  # noqa: E402


def test_new_interview_captures_problem_without_pretending_meaning_is_resolved() -> None:
    state = interview.new_interview(
        "Monthly customer totals disagree between CRM and billing.",
        created_by="sales-operations",
    )

    assert state["problem"]["status"] == "confirmed"
    assert state["objective"]["status"] == "unknown"
    assert state["semantic_contract_applies"]["status"] == "unknown"
    assert interview.readiness_report(state)["ready"] is False


def test_agent_proposal_requires_evidence_and_does_not_count_as_confirmation() -> None:
    state = interview.new_interview("Define active customers.", created_by="ops")

    with pytest.raises(interview.InterviewError, match="evidence"):
        interview.propose(state, "objective", "Report active customers", actor="agent")

    interview.propose(
        state,
        "objective",
        "Report active customers for revenue planning",
        actor="agent",
        evidence=["accepted-report-2026-07.xlsx"],
    )
    assert state["objective"]["status"] == "proposed"
    assert "objective" in interview.readiness_report(state)["blocking_fields"]


def test_semantic_contract_expands_only_when_meaning_matters() -> None:
    state = _minimum_confirmed_state(semantic_applies=True)
    report = interview.readiness_report(state)

    assert report["ready"] is False
    assert "semantic.definitions" in report["blocking_fields"]
    assert "semantic.ambiguity_behavior" in report["blocking_fields"]

    for field in interview.SEMANTIC_FIELDS:
        interview.confirm(
            state,
            field,
            value=f"approved {field}",
            actor="domain-owner",
            evidence=["domain-owner-review"],
            authorized_human=True,
        )

    assert interview.readiness_report(state)["ready"] is True


def test_conflicting_meanings_block_until_authorized_resolution() -> None:
    state = _minimum_confirmed_state(semantic_applies=True)
    interview.record_conflict(
        state,
        "semantic.definitions",
        candidates=[
            {"value": "open CRM account", "evidence": ["crm-schema"]},
            {"value": "billable event in 30 days", "evidence": ["billing-policy"]},
        ],
        actor="agent",
    )

    with pytest.raises(interview.InterviewError, match="authorized human"):
        interview.resolve_conflict(
            state,
            "semantic.definitions",
            choice="billable event in 30 days",
            actor="agent",
            authorized_human=False,
        )

    interview.resolve_conflict(
        state,
        "semantic.definitions",
        choice="billable event in 30 days",
        actor="commercial-analytics-owner",
        authorized_human=True,
    )
    assert state["semantic"]["definitions"]["status"] == "confirmed"
    assert state["semantic"]["definitions"]["confirmed_by"] == "commercial-analytics-owner"


def test_agent_cannot_use_confirmation_transition() -> None:
    state = interview.new_interview("Build report", created_by="owner")
    with pytest.raises(interview.InterviewError, match="authorized human"):
        interview.confirm(
            state, "objective", value="Build report", actor="agent",
            evidence=["report-example"], authorized_human=False,
        )


def test_conflict_evidence_must_be_an_array_not_a_string() -> None:
    state = interview.new_interview("Build report", created_by="owner")
    with pytest.raises(interview.InterviewError, match="evidence must be a list"):
        interview.record_conflict(
            state, "semantic.definitions", actor="agent",
            candidates=[
                {"value": "one", "evidence": "document-one"},
                {"value": "two", "evidence": ["document-two"]},
            ],
        )


def test_round_trip_is_resumable_and_generation_gate_has_machine_exit_code(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "interview.json"
    assert interview.main([
        "start", str(path), "--problem", "Build a governed report",
        "--created-by", "workflow-expert",
    ]) == 0
    persisted = json.loads(path.read_text(encoding="utf-8"))
    assert persisted["schema_version"] == 1

    assert interview.main(["gate", str(path)]) == 2
    output = capsys.readouterr().out
    assert "BLOCKED" in output


def test_nonsemantic_workflow_can_become_ready_without_semantic_fields() -> None:
    state = _minimum_confirmed_state(semantic_applies=False)
    assert interview.readiness_report(state)["ready"] is True


def test_semantic_applicability_requires_a_confirmed_boolean() -> None:
    state = _minimum_confirmed_state(semantic_applies=False)
    state["semantic_contract_applies"]["value"] = "false"  # type: ignore[index]

    report = interview.readiness_report(state)

    assert report["ready"] is False
    assert "semantic_contract_applies" in report["invalid_fields"]


def _minimum_confirmed_state(*, semantic_applies: bool) -> dict[str, object]:
    state = interview.new_interview("Build the recurring workflow.", created_by="expert")
    for field in interview.CORE_FIELDS:
        if field == "semantic_contract_applies":
            value: object = semantic_applies
        else:
            value = f"approved {field}"
        interview.confirm(
            state, field, value=value, actor="workflow-owner", evidence=["owner-interview"],
            authorized_human=True,
        )
    return state
