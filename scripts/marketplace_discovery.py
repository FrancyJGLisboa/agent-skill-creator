#!/usr/bin/env python3
"""Pure discovery metadata, search, and skill-page helpers for marketplaces."""

from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import Any, Mapping, Sequence

DISCOVERY_FIELDS = (
    "question", "trigger", "decision", "evidence", "success_measure", "outcome",
    "intended_users", "input_types", "output_artifacts", "use_cases",
    "examples", "permissions_systems", "typical_completion_time", "compatibility",
    "support_tier", "environment", "risk", "routing_tests",
    "metadata_completeness",
)
SUPPORT_TIERS = {"supported", "community", "deprecated"}
RISK_TIERS = {"low", "moderate", "high", "critical"}
MUTATION_BOUNDARIES = {"read-only", "approval-required", "prohibited"}
INSTALLABLE_LIFECYCLE_STATES = {"published"}
_TOKEN = re.compile(r"[a-z0-9]+")
_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_SEMVER = re.compile(r"^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:[-+][0-9A-Za-z.-]+)?$")
_DANGEROUS_SCHEME = re.compile(r"(?i)(?:javascript|data|vbscript)\s*:")


class DiscoveryError(ValueError):
    """Discovery metadata is unsafe or structurally invalid."""


def _text(value: object, *, default: str = "Not provided", limit: int = 500) -> str:
    if not isinstance(value, str) or not value.strip():
        return default
    clean = " ".join(value.replace("\x00", "").split())
    return clean[:limit]


def _list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted({_text(item, default="", limit=200) for item in value if _text(item, default="", limit=200)})


def _examples(value: object, name: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    result: list[dict[str, str]] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise DiscoveryError("each example must contain invocation and description")
        invocation = _text(item.get("invocation"), default="", limit=300)
        description = _text(item.get("description"), default="", limit=300)
        if not invocation.startswith(f"/{name}") or ".." in invocation or not description:
            raise DiscoveryError("example invocation must safely invoke this skill and include a description")
        result.append({"invocation": invocation, "description": description})
    return sorted(result, key=lambda item: (item["invocation"], item["description"]))


def _compatibility(value: object, version: str) -> dict[str, list[str]]:
    value = value if isinstance(value, Mapping) else {}
    declared = _list(value.get("declared"))
    raw = value.get("certified", [])
    certified: set[str] = set()
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, str):  # Explicit legacy compatibility, not certified evidence.
                continue
            if (
                isinstance(item, Mapping)
                and item.get("passed") is True
                and str(item.get("version", "")) == version
            ):
                platform = _text(item.get("platform"), default="", limit=80).lower()
                if platform:
                    certified.add(platform)
    return {"declared": declared, "certified": sorted(certified)}


def _environment(value: object) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        return {}
    result = {
        "documentation_sources": _list(value.get("documentation_sources")),
        "data_sources": _list(value.get("data_sources")),
        "required_capabilities": _list(value.get("required_capabilities")),
        "readiness_checks": _list(value.get("readiness_checks")),
    }
    missing = [key for key, items in result.items() if not items]
    if missing:
        raise DiscoveryError(
            "required environment field(s) missing or empty: " + ", ".join(missing)
        )
    return result


def _risk(value: object) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        return {}
    tier = _text(value.get("tier"), default="", limit=20).lower()
    boundary = _text(value.get("mutation_boundary"), default="", limit=40).lower()
    permissions = _list(value.get("permissions"))
    approvals = _list(value.get("approval_required"))
    if tier not in RISK_TIERS:
        raise DiscoveryError("risk.tier must be low, moderate, high, or critical")
    if boundary not in MUTATION_BOUNDARIES:
        raise DiscoveryError(
            "risk.mutation_boundary must be read-only, approval-required, or prohibited"
        )
    if not permissions:
        raise DiscoveryError("risk.permissions must name every required capability")
    if tier == "low" and boundary != "read-only":
        raise DiscoveryError("low-risk skills must be read-only")
    if tier in {"high", "critical"} and boundary == "approval-required" and not approvals:
        raise DiscoveryError("high/critical mutations must name an approval requirement")
    return {
        "tier": tier,
        "permissions": permissions,
        "mutation_boundary": boundary,
        "approval_required": approvals,
    }


def _routing_tests(value: object) -> dict[str, list[str]]:
    if not isinstance(value, Mapping):
        return {}
    result = {
        "should_trigger": _list(value.get("should_trigger")),
        "should_not_trigger": _list(value.get("should_not_trigger")),
    }
    if len(result["should_trigger"]) < 3 or len(result["should_not_trigger"]) < 3:
        raise DiscoveryError("routing_tests requires at least 3 positive and 3 negative queries")
    overlap = set(result["should_trigger"]) & set(result["should_not_trigger"])
    if overlap:
        raise DiscoveryError("routing_tests queries cannot be both positive and negative")
    return result


def normalize_discovery(entry: Mapping[str, Any]) -> dict[str, Any]:
    """Return canonical metadata with explicit low-confidence legacy defaults."""
    name = _text(entry.get("name"), default="", limit=100)
    if not _SLUG.fullmatch(name):
        raise DiscoveryError("skill name must be a safe lowercase slug")
    version = _text(entry.get("version"), default="", limit=80)
    if version and not _SEMVER.fullmatch(version):
        raise DiscoveryError("skill version must use semantic versioning")
    raw = entry.get("discovery", {})
    raw = raw if isinstance(raw, Mapping) else {}
    question = _text(raw.get("question"))
    trigger = _list(raw.get("trigger"))
    decision = _list(raw.get("decision"))
    evidence = _list(raw.get("evidence"))
    success_measure = _text(raw.get("success_measure"))
    outcome = _text(raw.get("outcome"))
    intended_users = _list(raw.get("intended_users"))
    input_types = _list(raw.get("input_types"))
    output_artifacts = _list(raw.get("output_artifacts"))
    use_cases = _list(raw.get("use_cases"))
    examples = _examples(raw.get("examples"), name)
    permissions = _list(raw.get("permissions_systems"))
    completion = _text(raw.get("typical_completion_time"))
    support = _text(raw.get("support_tier"), default="community", limit=40).lower()
    if support not in SUPPORT_TIERS:
        raise DiscoveryError("support_tier must be supported, community, or deprecated")
    compatibility = _compatibility(raw.get("compatibility"), version)
    environment = _environment(raw.get("environment"))
    risk = _risk(raw.get("risk"))
    routing_tests = _routing_tests(raw.get("routing_tests"))
    present = sum((
        question != "Not provided", bool(trigger), bool(decision), bool(evidence),
        success_measure != "Not provided",
        outcome != "Not provided", bool(intended_users), bool(input_types),
        bool(output_artifacts), bool(examples), bool(permissions),
        completion != "Not provided", bool(compatibility["declared"]),
        "support_tier" in raw,
    ))
    return {
        "question": question,
        "trigger": trigger,
        "decision": decision,
        "evidence": evidence,
        "success_measure": success_measure,
        "outcome": outcome,
        "intended_users": intended_users,
        "input_types": input_types,
        "output_artifacts": output_artifacts,
        "use_cases": use_cases,
        "examples": examples,
        "permissions_systems": permissions,
        "typical_completion_time": completion,
        "compatibility": compatibility,
        "support_tier": support,
        "environment": environment,
        "risk": risk,
        "routing_tests": routing_tests,
        "metadata_completeness": present,
    }


def require_decision_contract(entry: Mapping[str, Any]) -> dict[str, Any]:
    """Return normalized metadata or reject an incomplete decision contract."""
    metadata = normalize_discovery(entry)
    missing = [
        field for field in ("question", "success_measure")
        if metadata[field] == "Not provided"
    ]
    missing.extend(
        field for field in ("trigger", "decision", "evidence")
        if not metadata[field]
    )
    if missing:
        raise DiscoveryError(
            "required discovery field(s) missing or empty: " + ", ".join(missing)
        )
    return metadata


def require_operating_contract(entry: Mapping[str, Any]) -> dict[str, Any]:
    """Reject packages that cannot prove readiness, boundaries, and routing."""
    metadata = require_decision_contract(entry)
    raw = entry.get("discovery", {})
    raw = raw if isinstance(raw, Mapping) else {}
    metadata["environment"] = _environment_required(raw.get("environment"))
    metadata["risk"] = _risk_required(raw.get("risk"))
    metadata["routing_tests"] = _routing_tests_required(raw.get("routing_tests"))
    return metadata


def _environment_required(value: object) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise DiscoveryError("environment must be an object")
    return _environment(value)


def _risk_required(value: object) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise DiscoveryError("risk must be an object")
    return _risk(value)


def _routing_tests_required(value: object) -> dict[str, list[str]]:
    if not isinstance(value, Mapping):
        raise DiscoveryError("routing_tests must be an object")
    return _routing_tests(value)


def _tokens(value: object) -> set[str]:
    return set(_TOKEN.findall(str(value).lower()))


def _field_score(query: set[str], value: object, weight: int) -> int:
    if isinstance(value, list):
        tokens = set().union(*(_tokens(item) for item in value)) if value else set()
    else:
        tokens = _tokens(value)
    return len(query & tokens) * weight


def _installable(entry: Mapping[str, Any]) -> bool:
    if "lifecycle_state" in entry:
        return entry.get("lifecycle_state") in INSTALLABLE_LIFECYCLE_STATES
    if "lifecycle" in entry:
        return entry.get("lifecycle") in INSTALLABLE_LIFECYCLE_STATES
    return entry.get("approval_status") == "approved"  # schema-v2 legacy compatibility


def search_skills(
    skills: Sequence[Mapping[str, Any]], query: str, *, platform: str | None = None,
    support_tier: str | None = None,
) -> list[dict[str, Any]]:
    """Rank installable skills by outcomes first, with deterministic filtering."""
    query_tokens = _tokens(query)
    platform = platform.lower().strip() if platform else None
    support_tier = support_tier.lower().strip() if support_tier else None
    results: list[dict[str, Any]] = []
    for entry in skills:
        if not _installable(entry):
            continue
        metadata = normalize_discovery(entry)
        if platform and platform not in metadata["compatibility"]["certified"]:
            continue
        if support_tier and metadata["support_tier"] != support_tier:
            continue
        score = (
            _field_score(query_tokens, metadata["question"], 16)
            + _field_score(query_tokens, metadata["decision"], 10)
            + _field_score(query_tokens, metadata["trigger"], 8)
            + _field_score(query_tokens, metadata["evidence"], 7)
            + _field_score(query_tokens, metadata["success_measure"], 7)
            + _field_score(query_tokens, metadata["outcome"], 12)
            + _field_score(query_tokens, metadata["use_cases"], 6)
            + _field_score(query_tokens, entry.get("description", ""), 3)
            + _field_score(query_tokens, entry.get("name", ""), 2)
            + metadata["metadata_completeness"]
        )
        if query_tokens and score <= metadata["metadata_completeness"]:
            continue
        results.append({
            "name": str(entry.get("name", "")),
            "department": str(entry.get("department", "")),
            "version": str(entry.get("version", "")),
            "question": metadata["question"],
            "outcome": metadata["outcome"],
            "support_tier": metadata["support_tier"],
            "certified_platforms": metadata["compatibility"]["certified"],
            "score": score,
        })
    results.sort(key=lambda item: (-item["score"], item["department"], item["name"], item["version"]))
    return results


def evaluate_portfolio(skills: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Evaluate routing ownership across the complete published portfolio."""
    failures: list[dict[str, str]] = []
    published = [item for item in skills if _installable(item)]
    executed = 0
    for entry in published:
        metadata = require_operating_contract(entry)
        identity = f"{entry.get('department', '')}/{entry.get('name', '')}"
        for expectation, queries in metadata["routing_tests"].items():
            for query in queries:
                executed += 1
                results = search_skills(published, query)
                owner = (
                    f"{results[0]['department']}/{results[0]['name']}" if results else "none"
                )
                strong_match = bool(
                    results and results[0]["score"] >= metadata["metadata_completeness"] + 8
                )
                if expectation == "should_trigger" and (owner != identity or not strong_match):
                    failures.append({"skill": identity, "query": query,
                                     "expectation": expectation, "observed_owner": owner})
                if expectation == "should_not_trigger" and owner == identity and strong_match:
                    failures.append({"skill": identity, "query": query,
                                     "expectation": expectation, "observed_owner": owner})
                if len(results) > 1 and results[0]["score"] == results[1]["score"]:
                    failures.append({"skill": identity, "query": query,
                                     "expectation": "unambiguous routing",
                                     "observed_owner": f"tie:{owner}"})
    return {
        "status": "passed" if not failures else "failed",
        "skills": len(published),
        "queries": executed,
        "failures": failures,
    }


def _safe_path(value: object) -> str:
    if not isinstance(value, str) or "\\" in value or "\x00" in value:
        raise DiscoveryError("skill path is unsafe")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value or len(path.parts) < 3 or path.parts[0] != "skills":
        raise DiscoveryError("skill path must be a safe relative marketplace path")
    return value


def _md(value: object) -> str:
    text = _text(value, default="", limit=1000)
    text = _DANGEROUS_SCHEME.sub("blocked-scheme:", text)
    return (text.replace("\\", "\\\\").replace("`", "\\`")
            .replace("[", "\\[").replace("]", "\\]")
            .replace("<", "&lt;").replace(">", "&gt;").replace("|", "\\|"))


def _bullets(values: list[str]) -> list[str]:
    return [f"- {_md(item)}" for item in values] or ["- Not provided"]


def render_skill_page(entry: Mapping[str, Any]) -> str:
    """Render one deterministic, injection-resistant structured Markdown page."""
    _safe_path(entry.get("path"))
    metadata = normalize_discovery(entry)
    name = str(entry["name"])
    compatibility = metadata["compatibility"]
    lines = [
        f"# /{_md(name)}", "", _md(entry.get("description", "Not provided")), "",
        "## Question", "", _md(metadata["question"]), "",
        "## Trigger", "", *_bullets(metadata["trigger"]), "",
        "## Decisions supported", "", *_bullets(metadata["decision"]), "",
        "## Evidence required", "", *_bullets(metadata["evidence"]), "",
        "## Success measure", "", _md(metadata["success_measure"]), "",
        "## Outcome", "", _md(metadata["outcome"]), "",
        "## Intended users", "", *_bullets(metadata["intended_users"]), "",
        "## Inputs and outputs", "", "### Input types", "", *_bullets(metadata["input_types"]), "",
        "### Output artifacts", "", *_bullets(metadata["output_artifacts"]), "",
        "## Permissions and systems", "", *_bullets(metadata["permissions_systems"]), "",
        "## Typical completion time", "", _md(metadata["typical_completion_time"]), "",
        "## Compatibility and support", "", f"Support tier: **{_md(metadata['support_tier'])}**", "",
        "Declared platforms: " + (", ".join(_md(item) for item in compatibility["declared"]) or "Not provided"), "",
        "Certified platforms: " + (", ".join(_md(item) for item in compatibility["certified"]) or "None"), "",
        "## Examples", "",
    ]
    if not metadata["examples"]:
        lines.append("No examples provided.")
    else:
        for example in metadata["examples"]:
            lines += [f"- {_md(example['description'])}", f"    {_md(example['invocation'])}"]
    return "\n".join(lines) + "\n"
