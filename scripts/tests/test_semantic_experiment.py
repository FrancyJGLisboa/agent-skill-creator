"""Tests for the evidence-bound semantic-contract product experiment."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import semantic_experiment as experiment  # noqa: E402


def matrix() -> dict[str, object]:
    cases = []
    for archetype, action, drift in (
        ("single_authority", "answer", False),
        ("context_resolution", "ask", False),
        ("semantic_drift", "refuse_unknown", True),
    ):
        expected = {
            "skill": f"{archetype}-skill", "action": action,
            "source": "authoritative-source", "definition_version": "1.0.0",
            "vintage": "2026-08-01", "drift_detected": drift,
        }
        observations = {}
        for configuration in experiment.CONFIGURATIONS:
            observations[configuration] = expected | {
                "evidence_path": f"evidence/{configuration}/{archetype}.json",
                "evidence_sha256": "a" * 64,
            }
        cases.append({"id": archetype, "archetype": archetype,
                      "expected": expected, "observations": observations})
    return {"cases": cases}


def test_complete_matrix_scores_every_required_behavior() -> None:
    report = experiment.score_experiment(matrix())
    assert report["causal_claim"] == "not_established_by_score_alone"
    for result in report["configurations"].values():
        assert result["reliable_cases"] == 3
        assert all(set(check["dimensions"]) == set(experiment.DIMENSIONS)
                   for check in result["checks"])


def test_missing_configuration_is_rejected() -> None:
    payload = matrix()
    payload["cases"][0]["observations"].pop("model_data")  # type: ignore[index]
    with pytest.raises(experiment.ExperimentError, match="every experiment configuration"):
        experiment.score_experiment(payload)


def test_missing_archetype_is_rejected() -> None:
    payload = matrix()
    payload["cases"] = payload["cases"][:2]  # type: ignore[index]
    with pytest.raises(experiment.ExperimentError, match="at least three"):
        experiment.score_experiment(payload)


def test_unbound_evidence_is_rejected() -> None:
    payload = matrix()
    payload["cases"][0]["observations"]["model_data"]["evidence_sha256"] = "pending"  # type: ignore[index]
    with pytest.raises(experiment.ExperimentError, match="SHA-256"):
        experiment.score_experiment(payload)


def test_wrong_clarification_behavior_fails_whole_case() -> None:
    payload = matrix()
    case = payload["cases"][1]  # type: ignore[index]
    case["observations"]["model_data"]["action"] = "answer"  # type: ignore[index]
    result = experiment.score_experiment(payload)["configurations"]["model_data"]
    assert result["reliable_cases"] == 2
    assert result["checks"][1]["dimensions"]["action"] is False
