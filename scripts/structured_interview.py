#!/usr/bin/env python3
"""Run a resumable, evidence-backed interview before generating an agent skill.

The agent investigates, structures, and proposes. Consequential meaning remains
blocked until an identified human confirms it. Exit code 2 from ``gate`` means
the interview is valid but not ready for generation.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, MutableMapping, Sequence

STATUSES = {"unknown", "proposed", "conflicting", "confirmed", "not_applicable"}
CORE_FIELDS = (
    "objective",
    "decision_consumer",
    "decision_consequence",
    "success_measure",
    "failure_impact",
    "environment_requirements",
    "authority_owner",
    "semantic_contract_applies",
)
SEMANTIC_FIELDS = (
    "semantic.definitions",
    "semantic.source_precedence",
    "semantic.grain_unit",
    "semantic.time_semantics",
    "semantic.ambiguity_behavior",
    "semantic.freshness_policy",
)


class InterviewError(ValueError):
    """Interview state or transition is invalid."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _entry() -> dict[str, Any]:
    return {
        "status": "unknown", "value": None, "evidence": [],
        "proposed_by": None, "confirmed_by": None, "updated_at": None,
    }


def new_interview(problem: str, *, created_by: str) -> dict[str, Any]:
    """Create a state document without treating the user's problem as a specification."""
    if not isinstance(problem, str) or not problem.strip():
        raise InterviewError("problem must be a non-empty string")
    if not isinstance(created_by, str) or not created_by.strip():
        raise InterviewError("created_by must be a non-empty string")
    timestamp = _now()
    state: dict[str, Any] = {
        "schema_version": 1,
        "created_at": timestamp,
        "updated_at": timestamp,
        "created_by": created_by.strip(),
        "problem": {
            "status": "confirmed", "value": " ".join(problem.split()),
            "evidence": ["user_statement"], "proposed_by": None,
            "confirmed_by": created_by.strip(), "updated_at": timestamp,
        },
        "semantic": {name.split(".", 1)[1]: _entry() for name in SEMANTIC_FIELDS},
        "history": [],
    }
    for field in CORE_FIELDS:
        state[field] = _entry()
    return state


def _field_entry(state: MutableMapping[str, Any], field: str) -> MutableMapping[str, Any]:
    if field in CORE_FIELDS or field == "problem":
        entry = state.get(field)
    elif field in SEMANTIC_FIELDS:
        semantic = state.get("semantic")
        entry = semantic.get(field.split(".", 1)[1]) if isinstance(semantic, Mapping) else None
    else:
        raise InterviewError(f"unknown interview field: {field}")
    if not isinstance(entry, MutableMapping):
        raise InterviewError(f"malformed interview field: {field}")
    return entry


def _evidence(values: Sequence[str] | None) -> list[str]:
    if isinstance(values, (str, bytes)):
        raise InterviewError("evidence must be a list of strings")
    if values is not None and not all(isinstance(item, str) for item in values):
        raise InterviewError("evidence must be a list of strings")
    normalized = [" ".join(item.split()) for item in (values or []) if item.strip()]
    return list(dict.fromkeys(normalized))


def _record(state: MutableMapping[str, Any], action: str, field: str, actor: str) -> None:
    timestamp = _now()
    state["updated_at"] = timestamp
    history = state.setdefault("history", [])
    if not isinstance(history, list):
        raise InterviewError("history must be a list")
    history.append({"at": timestamp, "action": action, "field": field, "actor": actor})


def propose(
    state: MutableMapping[str, Any], field: str, value: Any, *, actor: str,
    evidence: Sequence[str] | None = None,
) -> None:
    """Record an evidence-backed proposal without granting it human authority."""
    sources = _evidence(evidence)
    if not sources:
        raise InterviewError("agent proposals require evidence")
    if value is None or value == "":
        raise InterviewError("proposal value must not be empty")
    entry = _field_entry(state, field)
    entry.update({
        "status": "proposed", "value": value, "evidence": sources,
        "proposed_by": actor, "confirmed_by": None, "updated_at": _now(),
    })
    entry.pop("candidates", None)
    _record(state, "propose", field, actor)


def confirm(
    state: MutableMapping[str, Any], field: str, *, value: Any, actor: str,
    evidence: Sequence[str] | None = None, authorized_human: bool,
) -> None:
    """Confirm a consequential field as an identified human decision."""
    if not authorized_human:
        raise InterviewError("confirmation requires an authorized human")
    if value is None or value == "":
        raise InterviewError("confirmed value must not be empty")
    sources = _evidence(evidence)
    entry = _field_entry(state, field)
    if not sources:
        sources = list(entry.get("evidence", []))
    if not sources:
        raise InterviewError("confirmation requires evidence")
    entry.update({
        "status": "confirmed", "value": value, "evidence": sources,
        "confirmed_by": actor, "updated_at": _now(),
    })
    entry.pop("candidates", None)
    _record(state, "confirm", field, actor)


def mark_not_applicable(
    state: MutableMapping[str, Any], field: str, *, actor: str, reason: str,
    authorized_human: bool,
) -> None:
    if not authorized_human:
        raise InterviewError("not-applicable decisions require an authorized human")
    if not reason.strip():
        raise InterviewError("not-applicable decisions require a reason")
    entry = _field_entry(state, field)
    entry.update({
        "status": "not_applicable", "value": reason.strip(),
        "evidence": [f"human_reason:{reason.strip()}"], "confirmed_by": actor,
        "updated_at": _now(),
    })
    entry.pop("candidates", None)
    _record(state, "not_applicable", field, actor)


def record_conflict(
    state: MutableMapping[str, Any], field: str, *,
    candidates: Sequence[Mapping[str, Any]], actor: str,
) -> None:
    if len(candidates) < 2:
        raise InterviewError("a conflict requires at least two candidates")
    normalized: list[dict[str, Any]] = []
    for candidate in candidates:
        value = candidate.get("value")
        sources = _evidence(candidate.get("evidence"))
        if value is None or value == "" or not sources:
            raise InterviewError("every conflict candidate requires a value and evidence")
        normalized.append({"value": value, "evidence": sources})
    entry = _field_entry(state, field)
    entry.update({
        "status": "conflicting", "value": None, "evidence": [],
        "candidates": normalized, "proposed_by": actor, "confirmed_by": None,
        "updated_at": _now(),
    })
    _record(state, "record_conflict", field, actor)


def resolve_conflict(
    state: MutableMapping[str, Any], field: str, *, choice: Any, actor: str,
    authorized_human: bool,
) -> None:
    if not authorized_human:
        raise InterviewError("conflict resolution requires an authorized human")
    entry = _field_entry(state, field)
    if entry.get("status") != "conflicting":
        raise InterviewError(f"{field} is not conflicting")
    candidates = entry.get("candidates", [])
    selected = next((item for item in candidates if item.get("value") == choice), None)
    if selected is None:
        raise InterviewError("choice must match one recorded candidate")
    confirm(
        state, field, value=choice, actor=actor, evidence=selected["evidence"],
        authorized_human=True,
    )


def readiness_report(state: Mapping[str, Any]) -> dict[str, Any]:
    """Return the exact decisions still blocking generation."""
    blocking: list[str] = []
    invalid: list[str] = []
    for field in CORE_FIELDS:
        entry = state.get(field)
        status = entry.get("status") if isinstance(entry, Mapping) else None
        if status not in STATUSES:
            invalid.append(field)
        elif status not in {"confirmed", "not_applicable"}:
            blocking.append(field)
    applies_entry = state.get("semantic_contract_applies")
    applies = applies_entry.get("value") if isinstance(applies_entry, Mapping) else None
    if (
        isinstance(applies_entry, Mapping)
        and applies_entry.get("status") in {"confirmed", "not_applicable"}
        and (applies_entry.get("status") != "confirmed" or not isinstance(applies, bool))
    ):
        invalid.append("semantic_contract_applies")
    if applies_entry and applies_entry.get("status") == "confirmed" and applies is True:
        semantic = state.get("semantic")
        for field in SEMANTIC_FIELDS:
            key = field.split(".", 1)[1]
            entry = semantic.get(key) if isinstance(semantic, Mapping) else None
            status = entry.get("status") if isinstance(entry, Mapping) else None
            if status not in STATUSES:
                invalid.append(field)
            elif status not in {"confirmed", "not_applicable"}:
                blocking.append(field)
    return {
        "ready": not blocking and not invalid,
        "blocking_fields": blocking,
        "invalid_fields": invalid,
        "next_question": _next_question(blocking[0]) if blocking else None,
    }


def _next_question(field: str) -> str:
    questions = {
        "objective": "What useful outcome should this workflow produce?",
        "decision_consumer": "Who uses the result to make or execute a decision?",
        "decision_consequence": "What will they do differently because of the result?",
        "success_measure": "What observable result proves the workflow succeeded?",
        "failure_impact": "What happens if the result is wrong?",
        "environment_requirements": "Which data, tools, schemas, and permissions does the workflow require?",
        "authority_owner": "Who has authority to approve the workflow's meaning and risk?",
        "semantic_contract_applies": "Could organizational definitions or source precedence change the correct answer?",
        "semantic.definitions": "Which business concepts require an authoritative definition?",
        "semantic.source_precedence": "When sources disagree, which source wins in each context?",
        "semantic.grain_unit": "What grain and unit must the result preserve?",
        "semantic.time_semantics": "Which time basis, period, and vintage apply?",
        "semantic.ambiguity_behavior": "When meaning is unresolved, should the skill ask, refuse, or escalate?",
        "semantic.freshness_policy": "Who reviews the definitions, and what makes them stale?",
    }
    return questions[field]


def validate_state(state: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if state.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not isinstance(state.get("problem"), Mapping):
        errors.append("problem is required")
    report = readiness_report(state)
    errors.extend(f"invalid field: {field}" for field in report["invalid_fields"])
    return errors


def load(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InterviewError(f"cannot read interview state: {exc}") from exc
    if not isinstance(payload, dict):
        raise InterviewError("interview state must be a JSON object")
    errors = validate_state(payload)
    if errors:
        raise InterviewError("; ".join(errors))
    return payload


def save(path: Path, state: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _json_value(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("start")
    start.add_argument("path", type=Path)
    start.add_argument("--problem", required=True)
    start.add_argument("--created-by", required=True)
    proposal = sub.add_parser("propose")
    proposal.add_argument("path", type=Path)
    proposal.add_argument("--field", required=True)
    proposal.add_argument("--value", required=True)
    proposal.add_argument("--actor", required=True)
    proposal.add_argument("--evidence", action="append", default=[])
    confirmation = sub.add_parser("confirm")
    confirmation.add_argument("path", type=Path)
    confirmation.add_argument("--field", required=True)
    confirmation.add_argument("--value", required=True)
    confirmation.add_argument("--authorized-human", required=True)
    confirmation.add_argument("--evidence", action="append", default=[])
    na = sub.add_parser("not-applicable")
    na.add_argument("path", type=Path)
    na.add_argument("--field", required=True)
    na.add_argument("--authorized-human", required=True)
    na.add_argument("--reason", required=True)
    conflict = sub.add_parser("conflict")
    conflict.add_argument("path", type=Path)
    conflict.add_argument("--field", required=True)
    conflict.add_argument("--actor", required=True)
    conflict.add_argument(
        "--candidate", action="append", required=True,
        help='JSON object: {"value": ..., "evidence": [...]}; repeat at least twice',
    )
    resolve = sub.add_parser("resolve")
    resolve.add_argument("path", type=Path)
    resolve.add_argument("--field", required=True)
    resolve.add_argument("--choice", required=True)
    resolve.add_argument("--authorized-human", required=True)
    for command in ("status", "gate"):
        item = sub.add_parser(command)
        item.add_argument("path", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "start":
            state = new_interview(args.problem, created_by=args.created_by)
            save(args.path, state)
            print(f"Started interview at {args.path}")
            return 0
        state = load(args.path)
        if args.command == "propose":
            propose(state, args.field, _json_value(args.value), actor=args.actor, evidence=args.evidence)
        elif args.command == "confirm":
            confirm(
                state, args.field, value=_json_value(args.value),
                actor=args.authorized_human, evidence=args.evidence, authorized_human=True,
            )
        elif args.command == "not-applicable":
            mark_not_applicable(
                state, args.field, actor=args.authorized_human, reason=args.reason,
                authorized_human=True,
            )
        elif args.command == "conflict":
            candidates = [_json_value(item) for item in args.candidate]
            if not all(isinstance(item, Mapping) for item in candidates):
                raise InterviewError("every candidate must be a JSON object")
            record_conflict(state, args.field, candidates=candidates, actor=args.actor)
        elif args.command == "resolve":
            resolve_conflict(
                state, args.field, choice=_json_value(args.choice), actor=args.authorized_human,
                authorized_human=True,
            )
        report = readiness_report(state)
        if args.command in {"status", "gate"}:
            print(json.dumps(report, indent=2, sort_keys=True))
            if args.command == "gate":
                print("READY" if report["ready"] else "BLOCKED")
                return 0 if report["ready"] else 2
            return 0
        save(args.path, state)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except InterviewError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
