#!/usr/bin/env python3
"""Pure, fail-closed trust primitives for the schema-v2 marketplace.

This module deliberately performs no network or Git operations. Callers resolve the
submitted commit, run gates, and then pass those facts here for validation and a
portable JSON attestation.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import PurePosixPath
from typing import Any, Mapping

ATTESTATION_SCHEMA = "agent-skill-creator.marketplace-attestation"
ATTESTATION_SCHEMA_VERSION = 1
LIFECYCLE_STATES = {
    "draft", "in-review", "approved", "published", "quarantined",
    "deprecated", "retired",
}
ALLOWED_LIFECYCLE_TRANSITIONS: dict[str, frozenset[str]] = {
    "draft": frozenset({"in-review"}),
    "in-review": frozenset({"draft", "approved", "quarantined"}),
    "approved": frozenset({"in-review", "published", "quarantined"}),
    "published": frozenset({"quarantined", "deprecated"}),
    "quarantined": frozenset({"in-review", "published", "deprecated", "retired"}),
    "deprecated": frozenset({"quarantined", "retired"}),
    "retired": frozenset(),
}

_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_SEMVER = re.compile(
    r"^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?"
    r"(?:\+[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?$"
)
_COMMIT_SHA = re.compile(r"^[0-9a-fA-F]{40}(?:[0-9a-fA-F]{24})?$")


class TrustError(ValueError):
    """Trust evidence or a lifecycle operation violates marketplace policy."""


def rfc3339(value: datetime) -> str:
    """Serialize an aware datetime as a stable UTC RFC 3339 timestamp."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise TrustError("timestamp datetime must include a timezone")
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _timestamp_valid(value: object) -> bool:
    if not isinstance(value, str) or not value or not value.endswith(("Z", "+00:00")):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def _safe_runner_path(value: object) -> bool:
    if not isinstance(value, str) or "\\" in value or "\x00" in value:
        return False
    path = PurePosixPath(value)
    return (
        not path.is_absolute()
        and value == path.as_posix()
        and ".." not in path.parts
        and path.parts == ("scripts", "run_evals.py")
    )


def validate_eval_evidence(evidence: object) -> list[str]:
    """Return policy errors for executable eval evidence; absence always fails."""
    if not isinstance(evidence, Mapping):
        return ["eval evidence is required and must be an object"]
    if not evidence:
        return ["eval evidence is required"]
    errors: list[str] = []
    if not _safe_runner_path(evidence.get("runner")):
        errors.append("eval runner must be the safe relative path scripts/run_evals.py")
    if evidence.get("executable") is not True:
        errors.append("eval runner must be present and executable")
    if evidence.get("validation_passed") is not True:
        errors.append("eval schema validation must have passed")
    if evidence.get("run_passed") is not True:
        errors.append("eval run must have passed")
    if not _timestamp_valid(evidence.get("checked_at")):
        errors.append("eval checked_at must be an RFC 3339 timestamp with timezone")
    return errors


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def validate_attestation(
    artifact: object, *, expected_skill: str, expected_version: str, expected_commit: str,
) -> list[str]:
    """Validate an attestation and bind it to the exact submitted identity and commit."""
    if not isinstance(artifact, Mapping):
        return ["attestation must be a JSON object"]
    errors: list[str] = []
    if artifact.get("schema") != ATTESTATION_SCHEMA:
        errors.append(f"attestation schema must be {ATTESTATION_SCHEMA}")
    if artifact.get("schema_version") != ATTESTATION_SCHEMA_VERSION:
        errors.append(f"attestation schema version must be {ATTESTATION_SCHEMA_VERSION}")

    skill = _mapping(artifact.get("skill"))
    name, version = skill.get("name"), skill.get("version")
    if not isinstance(name, str) or not _SLUG.fullmatch(name):
        errors.append("attestation skill name must be a safe lowercase slug")
    if name != expected_skill:
        errors.append("attestation skill identity does not match the submitted skill")
    if not isinstance(version, str) or not _SEMVER.fullmatch(version):
        errors.append("attestation skill version must use semantic versioning")
    if version != expected_version:
        errors.append("attestation skill version does not match the submitted version")

    commit = artifact.get("commit_sha")
    if not isinstance(commit, str) or not _COMMIT_SHA.fullmatch(commit):
        errors.append("attestation commit_sha must be a full 40- or 64-character Git commit hash")
    elif not _COMMIT_SHA.fullmatch(expected_commit) or commit.lower() != expected_commit.lower():
        errors.append("attestation commit does not match the submitted Git commit")

    gates = _mapping(artifact.get("gates"))
    errors.extend(validate_eval_evidence(gates.get("evals")))
    representative = _mapping(artifact.get("representative_run"))
    if representative.get("passed") is not True:
        errors.append("representative run must have passed")
    run_id = representative.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip() or len(run_id) > 200:
        errors.append("representative run_id is required and must be at most 200 characters")
    if not _timestamp_valid(representative.get("completed_at")):
        errors.append("representative run completed_at must be an RFC 3339 timestamp with timezone")
    if not _timestamp_valid(artifact.get("issued_at")):
        errors.append("attestation issued_at must be an RFC 3339 timestamp with timezone")
    return errors


def create_attestation(
    *, skill_name: str, skill_version: str, commit_sha: str,
    eval_evidence: Mapping[str, object], representative_run: Mapping[str, object],
    issued_at: str | datetime | None = None,
) -> dict[str, object]:
    """Create a validated JSON-compatible attestation for one submitted commit."""
    if isinstance(issued_at, datetime):
        issued = rfc3339(issued_at)
    elif issued_at is None:
        issued = rfc3339(datetime.now(timezone.utc))
    else:
        issued = issued_at
    artifact: dict[str, object] = {
        "schema": ATTESTATION_SCHEMA,
        "schema_version": ATTESTATION_SCHEMA_VERSION,
        "skill": {"name": skill_name, "version": skill_version},
        "commit_sha": commit_sha.lower(),
        "gates": {"evals": dict(eval_evidence)},
        "representative_run": dict(representative_run),
        "issued_at": issued,
    }
    errors = validate_attestation(
        artifact, expected_skill=skill_name, expected_version=skill_version,
        expected_commit=commit_sha,
    )
    if errors:
        raise TrustError("; ".join(errors))
    return artifact


def attestation_json(artifact: Mapping[str, object]) -> str:
    """Serialize a validated-looking artifact deterministically for repository storage."""
    try:
        return json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    except (TypeError, ValueError) as exc:
        raise TrustError(f"attestation is not valid JSON data: {exc}") from exc


def validate_lifecycle_transition(source: object, target: object) -> list[str]:
    """Return errors unless a lifecycle transition is explicitly authorized."""
    if source not in LIFECYCLE_STATES:
        return [f"unknown lifecycle source state: {source!r}"]
    if target not in LIFECYCLE_STATES:
        return [f"unknown lifecycle target state: {target!r}"]
    if target not in ALLOWED_LIFECYCLE_TRANSITIONS[str(source)]:
        return [f"lifecycle transition {source!r} -> {target!r} is not authorized"]
    return []


def transition_lifecycle(source: object, target: object) -> str:
    """Return the target state or raise when marketplace policy forbids it."""
    errors = validate_lifecycle_transition(source, target)
    if errors:
        raise TrustError("; ".join(errors))
    return str(target)
