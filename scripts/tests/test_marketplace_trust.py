"""Fail-closed contracts for governed marketplace trust evidence."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import marketplace_trust as trust  # noqa: E402


COMMIT = "a" * 40
NOW = "2026-08-25T12:00:00Z"


def valid_eval() -> dict[str, object]:
    return {
        "runner": "scripts/run_evals.py",
        "executable": True,
        "validation_passed": True,
        "run_passed": True,
        "checked_at": NOW,
    }


def valid_attestation() -> dict[str, object]:
    return trust.create_attestation(
        skill_name="report-skill",
        skill_version="1.2.3",
        commit_sha=COMMIT,
        eval_evidence=valid_eval(),
        representative_run={
            "passed": True,
            "run_id": "representative-001",
            "completed_at": NOW,
            "safe_mode": "dry-run",
        },
        issued_at=NOW,
    )


def test_eval_evidence_accepts_executable_passing_runner() -> None:
    assert trust.validate_eval_evidence(valid_eval()) == []


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({}, "required"),
        ({"runner": "../run_evals.py"}, "runner"),
        ({"runner": "README.md"}, "run_evals.py"),
        ({"executable": False}, "executable"),
        ({"validation_passed": False}, "validation"),
        ({"run_passed": False}, "run"),
        ({"checked_at": "yesterday"}, "timestamp"),
    ],
)
def test_eval_evidence_rejects_missing_malformed_or_failing_proof(
    change: dict[str, object], message: str
) -> None:
    evidence = valid_eval() if change else {}
    evidence.update(change)
    assert any(message in error.lower() for error in trust.validate_eval_evidence(evidence))


def test_attestation_round_trips_as_json_artifact() -> None:
    artifact = valid_attestation()
    encoded = trust.attestation_json(artifact)
    assert json.loads(encoded) == artifact
    assert trust.validate_attestation(
        json.loads(encoded), expected_skill="report-skill",
        expected_version="1.2.3", expected_commit=COMMIT,
    ) == []


def test_attestation_rejects_commit_mismatch() -> None:
    errors = trust.validate_attestation(
        valid_attestation(), expected_skill="report-skill",
        expected_version="1.2.3", expected_commit="b" * 40,
    )
    assert any("commit" in error.lower() for error in errors)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("schema", "unknown.example", "schema"),
        ("schema_version", 99, "version"),
        ("skill.name", "../escape", "skill"),
        ("skill.version", "latest", "semantic"),
        ("commit_sha", "not-a-sha", "commit"),
        ("gates.evals.run_passed", False, "eval"),
        ("representative_run.passed", False, "representative"),
        ("representative_run.run_id", "", "run_id"),
        ("representative_run.completed_at", "soon", "timestamp"),
    ],
)
def test_attestation_rejects_malformed_or_failed_facts(
    field: str, value: object, message: str
) -> None:
    artifact = valid_attestation()
    target: dict[str, object] = artifact
    parts = field.split(".")
    for part in parts[:-1]:
        target = target[part]  # type: ignore[assignment,index]
    target[parts[-1]] = value
    errors = trust.validate_attestation(
        artifact, expected_skill="report-skill",
        expected_version="1.2.3", expected_commit=COMMIT,
    )
    assert any(message in error.lower() for error in errors)


def test_attestation_creation_rejects_naive_datetime() -> None:
    with pytest.raises(trust.TrustError, match="timezone"):
        trust.create_attestation(
            skill_name="report-skill", skill_version="1.2.3", commit_sha=COMMIT,
            eval_evidence=valid_eval(), representative_run={
                "passed": True, "run_id": "x", "completed_at": NOW,
            }, issued_at=datetime(2026, 8, 25),
        )


def test_lifecycle_declares_all_required_states() -> None:
    assert trust.LIFECYCLE_STATES == {
        "draft", "in-review", "approved", "published", "quarantined",
        "deprecated", "retired",
    }


@pytest.mark.parametrize(
    ("source", "target"),
    [
        ("draft", "in-review"),
        ("in-review", "approved"),
        ("approved", "published"),
        ("published", "quarantined"),
        ("published", "deprecated"),
        ("quarantined", "published"),
        ("deprecated", "retired"),
    ],
)
def test_lifecycle_allows_policy_transitions(source: str, target: str) -> None:
    assert trust.validate_lifecycle_transition(source, target) == []
    assert trust.transition_lifecycle(source, target) == target


@pytest.mark.parametrize(
    ("source", "target"),
    [
        ("draft", "published"),
        ("in-review", "published"),
        ("retired", "published"),
        ("published", "approved"),
        ("unknown", "draft"),
        ("draft", "unknown"),
        ("draft", "draft"),
    ],
)
def test_lifecycle_rejects_unauthorized_transitions(source: str, target: str) -> None:
    assert trust.validate_lifecycle_transition(source, target)
    with pytest.raises(trust.TrustError):
        trust.transition_lifecycle(source, target)


def test_timestamp_helper_emits_utc_rfc3339() -> None:
    assert trust.rfc3339(datetime(2026, 8, 25, 12, tzinfo=timezone.utc)) == NOW
