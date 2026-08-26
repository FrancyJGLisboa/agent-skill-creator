#!/usr/bin/env python3
"""Score the bounded three-skill semantic-contract product experiment."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Mapping

CONFIGURATIONS = (
    "model_data",
    "model_data_documents",
    "model_semantic_contracts",
    "model_contracts_skills_evals",
)
ARCHETYPES = {"single_authority", "context_resolution", "semantic_drift"}
DIMENSIONS = (
    "skill",
    "action",
    "source",
    "definition_version",
    "vintage",
    "drift_detected",
)
ACTIONS = {"answer", "ask", "refuse_unknown"}
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class ExperimentError(ValueError):
    """The experiment cannot support a causal comparison as supplied."""


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ExperimentError(f"{field} must be a non-empty string")
    return " ".join(value.split())


def validate_experiment(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Validate a complete four-configuration, three-archetype evidence matrix."""
    cases = payload.get("cases")
    if not isinstance(cases, list) or len(cases) < 3:
        raise ExperimentError("experiment requires at least three real question cases")
    archetypes: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, case in enumerate(cases):
        if not isinstance(case, Mapping):
            raise ExperimentError(f"cases[{index}] must be an object")
        case_id = _text(case.get("id"), f"cases[{index}].id")
        archetype = _text(case.get("archetype"), f"{case_id}.archetype")
        if archetype not in ARCHETYPES:
            raise ExperimentError(f"{case_id}.archetype is unsupported")
        archetypes.add(archetype)
        expected = case.get("expected")
        if not isinstance(expected, Mapping):
            raise ExperimentError(f"{case_id}.expected must be an object")
        canonical_expected = {field: expected.get(field) for field in DIMENSIONS}
        if canonical_expected["action"] not in ACTIONS:
            raise ExperimentError(f"{case_id}.expected.action is unsupported")
        observations = case.get("observations")
        if not isinstance(observations, Mapping) or set(observations) != set(CONFIGURATIONS):
            raise ExperimentError(f"{case_id} must contain every experiment configuration exactly once")
        canonical_observations: dict[str, dict[str, Any]] = {}
        for configuration in CONFIGURATIONS:
            observation = observations[configuration]
            if not isinstance(observation, Mapping):
                raise ExperimentError(f"{case_id}.{configuration} must be an object")
            evidence = _text(observation.get("evidence_path"), f"{case_id}.{configuration}.evidence_path")
            evidence_sha256 = _text(
                observation.get("evidence_sha256"),
                f"{case_id}.{configuration}.evidence_sha256",
            ).lower()
            if not SHA256.fullmatch(evidence_sha256):
                raise ExperimentError(
                    f"{case_id}.{configuration}.evidence_sha256 must be a lowercase SHA-256"
                )
            if observation.get("action") not in ACTIONS:
                raise ExperimentError(f"{case_id}.{configuration}.action is unsupported")
            canonical_observations[configuration] = {
                field: observation.get(field) for field in DIMENSIONS
            } | {"evidence_path": evidence, "evidence_sha256": evidence_sha256}
        normalized.append({
            "id": case_id,
            "archetype": archetype,
            "expected": canonical_expected,
            "observations": canonical_observations,
        })
    missing = ARCHETYPES - archetypes
    if missing:
        raise ExperimentError("experiment is missing archetype(s): " + ", ".join(sorted(missing)))
    return normalized


def score_experiment(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return transparent binary scores without attributing causality automatically."""
    cases = validate_experiment(payload)
    configurations: dict[str, Any] = {}
    for configuration in CONFIGURATIONS:
        checks: list[dict[str, Any]] = []
        for case in cases:
            observed = case["observations"][configuration]
            dimension_scores = {
                field: observed[field] == case["expected"][field] for field in DIMENSIONS
            }
            checks.append({
                "case": case["id"],
                "archetype": case["archetype"],
                "passed": all(dimension_scores.values()),
                "dimensions": dimension_scores,
                "evidence_path": observed["evidence_path"],
                "evidence_sha256": observed["evidence_sha256"],
            })
        passed = sum(check["passed"] for check in checks)
        configurations[configuration] = {
            "reliable_cases": passed,
            "total_cases": len(checks),
            "reliable_answer_rate": passed / len(checks),
            "checks": checks,
        }
    return {
        "schema_version": 1,
        "configurations": configurations,
        "causal_claim": "not_established_by_score_alone",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        report = score_experiment(payload)
    except (OSError, json.JSONDecodeError, ExperimentError) as exc:
        parser.error(str(exc))
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
