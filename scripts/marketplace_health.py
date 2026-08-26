#!/usr/bin/env python3
"""Deterministic, network-free health reporting for schema-v2 marketplaces."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, Mapping

from platforms import normalize_platform_name

from review_staleness import DEFAULT_REVIEW_INTERVAL_DAYS, classify_staleness, _parse_date
from skill_document import SkillDoc
from marketplace_discovery import DiscoveryError, normalize_discovery

HEALTH_DIMENSIONS = (
    "review_staleness",
    "semantic_freshness",
    "dependency_health",
    "eval_regression",
    "owner_presence",
    "compatibility",
)
_SEVERITY_ORDER = {"critical": 0, "warning": 1}


def _finding(identity: str, dimension: str, severity: str, reason: str, remediation: str) -> dict[str, str]:
    return {
        "skill": identity,
        "dimension": dimension,
        "severity": severity,
        "reason": reason,
        "remediation": remediation,
    }


def _safe_skill_doc(root: Path, relative: object) -> tuple[SkillDoc | None, str | None]:
    if not isinstance(relative, str) or not relative.strip() or "\x00" in relative:
        return None, "Skill path is missing or unsafe."
    try:
        target = (root / relative).resolve()
        base = root.resolve()
        if target == base or not target.is_relative_to(base):
            return None, "Skill path is unsafe because it escapes the marketplace root."
        skill_md = target / "SKILL.md"
        return SkillDoc.from_text(skill_md.read_text(encoding="utf-8")), None
    except (FileNotFoundError, OSError, ValueError) as exc:
        return None, f"Local SKILL.md is unavailable or invalid: {exc}"


def _review_check(entry: Mapping[str, Any], root: Path, today: date, identity: str) -> tuple[dict[str, str], list[dict[str, str]]]:
    doc, error = _safe_skill_doc(root, entry.get("path"))
    if error or doc is None:
        item = _finding(identity, "review_staleness", "critical", error or "Review metadata is unavailable.", "Restore a valid in-repository SKILL.md and record its review date.")
        return {"status": "critical", "detail": item["reason"]}, [item]
    raw_reviewed = doc.subfield("metadata", "last_reviewed")
    reviewed = _parse_date(raw_reviewed) if raw_reviewed else None
    raw_interval = doc.subfield("metadata", "review_interval_days")
    try:
        interval = int(raw_interval) if raw_interval else DEFAULT_REVIEW_INTERVAL_DAYS
        if interval <= 0:
            raise ValueError
    except ValueError:
        interval = DEFAULT_REVIEW_INTERVAL_DAYS
        item = _finding(identity, "review_staleness", "warning", "Review interval is invalid.", f"Set metadata.review_interval_days to a positive integer; the default is {DEFAULT_REVIEW_INTERVAL_DAYS}.")
        return {"status": "warning", "detail": item["reason"]}, [item]
    if reviewed is None:
        item = _finding(identity, "review_staleness", "warning", "No valid metadata.last_reviewed date is recorded.", "Review the skill and set metadata.last_reviewed to YYYY-MM-DD.")
        return {"status": "warning", "detail": item["reason"]}, [item]
    status, days_since, deadline = classify_staleness(reviewed, interval, today)
    if status == "overdue":
        item = _finding(identity, "review_staleness", "critical", f"Review is overdue: {days_since} days since review; deadline was {deadline.isoformat()}.", "Complete owner review and update metadata.last_reviewed.")
        return {"status": "critical", "detail": item["reason"]}, [item]
    if status == "due_soon":
        item = _finding(identity, "review_staleness", "warning", f"Review is due soon on {deadline.isoformat()}.", "Schedule owner review before the deadline.")
        return {"status": "warning", "detail": item["reason"]}, [item]
    return {"status": "healthy", "detail": f"Reviewed {reviewed.isoformat()}; deadline {deadline.isoformat()}."}, []


def _semantic_freshness_check(
    entry: Mapping[str, Any], today: date, identity: str,
) -> tuple[dict[str, str], list[dict[str, str]]]:
    discovery = entry.get("discovery", {})
    discovery = discovery if isinstance(discovery, Mapping) else {}
    try:
        semantic = normalize_discovery({
            "name": str(entry.get("name", "")),
            "version": str(entry.get("version", "")),
            "discovery": discovery,
        })["semantic_contract"]
    except DiscoveryError as exc:
        reason = f"Semantic contract is invalid: {exc}."
        item = _finding(identity, "semantic_freshness", "critical", reason,
                        "Repair the semantic contract and obtain owner review.")
        return {"status": "critical", "detail": reason}, [item]
    if not semantic.get("applies"):
        return {"status": "healthy", "detail": "No semantic contract is required."}, []
    stale: list[str] = []
    due_soon: list[str] = []
    for definition in semantic["definitions"]:
        reviewed = date.fromisoformat(definition["last_reviewed"])
        status, _, _ = classify_staleness(
            reviewed, definition["review_interval_days"], today,
        )
        label = f"{definition['id']}@{definition['version']}"
        if status == "overdue":
            stale.append(label)
        elif status == "due_soon":
            due_soon.append(label)
    if stale:
        reason = "Semantic review is overdue for: " + ", ".join(stale) + "."
        item = _finding(identity, "semantic_freshness", "critical", reason,
                        "Have each semantic owner review the meaning and publish a current version.")
        return {"status": "critical", "detail": reason}, [item]
    if due_soon:
        reason = "Semantic review is due soon for: " + ", ".join(due_soon) + "."
        item = _finding(identity, "semantic_freshness", "warning", reason,
                        "Schedule semantic owner review before the deadline.")
        return {"status": "warning", "detail": reason}, [item]
    return {
        "status": "healthy",
        "detail": f"{len(semantic['definitions'])} semantic definition(s) are current.",
    }, []


def _dependency_check(entry: Mapping[str, Any], identity: str) -> tuple[dict[str, str], list[dict[str, str]]]:
    declared = entry.get("dependencies", [])
    declared = declared if isinstance(declared, list) else []
    evidence = entry.get("dependency_health", [])
    evidence = evidence if isinstance(evidence, list) else []
    by_name = {str(item.get("name", "")): item for item in evidence if isinstance(item, Mapping)}
    missing: list[str] = []
    unhealthy: list[str] = []
    for dependency in declared:
        if not isinstance(dependency, Mapping):
            missing.append("<invalid dependency>")
            continue
        name = str(dependency.get("name") or dependency.get("url") or "<unnamed>")
        record = by_name.get(name)
        if record is None or not record.get("checked_at"):
            missing.append(name)
        elif str(record.get("status", "")).lower() not in {"healthy", "ok", "passed"}:
            unhealthy.append(name)
    if unhealthy:
        reason = "Unhealthy dependency evidence for: " + ", ".join(sorted(unhealthy)) + "."
        item = _finding(identity, "dependency_health", "critical", reason, "Restore or replace each dependency, then record a passing offline health result.")
        return {"status": "critical", "detail": reason}, [item]
    if missing:
        reason = "Dependency health evidence is missing for: " + ", ".join(sorted(missing)) + "."
        item = _finding(identity, "dependency_health", "warning", reason, "Run the approved dependency checker separately and store its timestamped result in the registry.")
        return {"status": "warning", "detail": reason}, [item]
    return {"status": "healthy", "detail": f"{len(declared)} declared dependencies have passing evidence."}, []


def _eval_check(entry: Mapping[str, Any], identity: str) -> tuple[dict[str, str], list[dict[str, str]]]:
    quality = entry.get("quality", {})
    quality = quality if isinstance(quality, Mapping) else {}
    evals = quality.get("evals", {})
    evals = evals if isinstance(evals, Mapping) else {}
    passed = evals.get("passed") is True
    regressions = evals.get("regressions", 0)
    clean_count = isinstance(regressions, int) and not isinstance(regressions, bool) and regressions == 0
    if not passed or not clean_count:
        reason = f"Latest eval evidence failed or reports regressions={regressions!r}."
        item = _finding(identity, "eval_regression", "critical", reason, "Fix the regression and attach a new passing eval result for this skill version.")
        return {"status": "critical", "detail": reason}, [item]
    return {"status": "healthy", "detail": "Latest eval passed with zero regressions."}, []


def _owner_check(entry: Mapping[str, Any], active_owners: set[str], identity: str) -> tuple[dict[str, str], list[dict[str, str]]]:
    raw = entry.get("owners", [])
    owners = [str(owner).lstrip("@").strip() for owner in raw] if isinstance(raw, list) else []
    active = sorted(set(owners) & {owner.lstrip("@").strip() for owner in active_owners})
    if not active:
        reason = "No declared owner is present in the active owner directory."
        item = _finding(identity, "owner_presence", "critical", reason, "Add at least one active owner and obtain that owner's acknowledgement.")
        return {"status": "critical", "detail": reason}, [item]
    return {"status": "healthy", "detail": "Active owners: " + ", ".join(active) + "."}, []


def _compatibility_check(entry: Mapping[str, Any], identity: str) -> tuple[dict[str, str], list[dict[str, str]]]:
    declared: list[str] = []
    valid: set[str] = set()
    version = str(entry.get("version", ""))
    value = entry.get("compatibility", {})
    if isinstance(value, Mapping) and value:
        raw_declared = value.get("declared", [])
        declared = sorted({normalize_platform_name(str(item)) for item in raw_declared if str(item).strip()}) if isinstance(raw_declared, list) else []
        raw_certified = value.get("certified", [])
        certified = raw_certified if isinstance(raw_certified, list) else []
        valid = {
            normalize_platform_name(str(item.get("platform", "")))
            for item in certified
            if isinstance(item, Mapping) and item.get("passed") is True and str(item.get("version", "")) == version
        }
    else:
        discovery = entry.get("discovery", {})
        discovery = discovery if isinstance(discovery, Mapping) else {}
        try:
            metadata = normalize_discovery({
                "name": str(entry.get("name", "")),
                "version": str(entry.get("version", "")),
                "discovery": discovery,
            })
        except DiscoveryError as exc:
            reason = f"Discovery metadata is invalid: {exc}."
            item = _finding(identity, "compatibility", "warning", reason, "Repair discovery compatibility metadata so platform claims can be governed.")
            return {"status": "warning", "detail": reason}, [item]
        declared = metadata["compatibility"]["declared"]
        valid = set(metadata["compatibility"]["certified"])
    missing = sorted(set(declared) - valid)
    if missing:
        reason = "Declared platforms lack passing certification for this version: " + ", ".join(missing) + "."
        item = _finding(identity, "compatibility", "warning", reason, "Remove unsupported claims or certify each platform against the current skill version.")
        return {"status": "warning", "detail": reason}, [item]
    return {"status": "healthy", "detail": f"{len(declared)} declared platforms are certified for {version}."}, []


def build_health_report(registry: Mapping[str, Any], root: Path, today: date, active_owners: set[str]) -> dict[str, Any]:
    """Evaluate every governed local health dimension for each schema-v2 skill."""
    if registry.get("schema_version") != 2:
        raise ValueError("marketplace health requires registry schema_version 2")
    marketplace = registry.get("marketplace", {})
    marketplace = marketplace if isinstance(marketplace, Mapping) else {}
    raw_skills = registry.get("skills", [])
    entries = [item for item in raw_skills if isinstance(item, Mapping)] if isinstance(raw_skills, list) else []
    entries.sort(key=lambda item: (str(item.get("department", "")), str(item.get("name", ""))))
    skill_reports: list[dict[str, Any]] = []
    findings: list[dict[str, str]] = []
    for entry in entries:
        identity = f"{entry.get('department', '')}/{entry.get('name', '')}"
        checks: dict[str, dict[str, str]] = {}
        for dimension, result in (
            ("review_staleness", _review_check(entry, root, today, identity)),
            ("semantic_freshness", _semantic_freshness_check(entry, today, identity)),
            ("dependency_health", _dependency_check(entry, identity)),
            ("eval_regression", _eval_check(entry, identity)),
            ("owner_presence", _owner_check(entry, active_owners, identity)),
            ("compatibility", _compatibility_check(entry, identity)),
        ):
            checks[dimension], new_findings = result
            findings.extend(new_findings)
        skill_reports.append({"identity": identity, "version": str(entry.get("version", "")), "checks": checks})
    findings.sort(key=lambda item: (_SEVERITY_ORDER[item["severity"]], item["skill"], HEALTH_DIMENSIONS.index(item["dimension"]), item["reason"]))
    critical = sum(item["severity"] == "critical" for item in findings)
    warning = sum(item["severity"] == "warning" for item in findings)
    status = "critical" if critical else "warning" if warning else "healthy"
    return {
        "schema_version": 1,
        "marketplace": str(marketplace.get("name", "Marketplace")),
        "as_of": today.isoformat(),
        "summary": {"status": status, "skills": len(skill_reports), "findings": len(findings), "critical": critical, "warning": warning},
        "skills": skill_reports,
        "findings": findings,
    }


def report_json(report: Mapping[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"


def _markdown(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def report_markdown(report: Mapping[str, Any]) -> str:
    """Render stable, scan-friendly Markdown from a health report."""
    summary = report["summary"]
    lines = [
        f"# {_markdown(report['marketplace'])} Health Report", "",
        f"As of `{_markdown(report['as_of'])}`.", "", "## Summary", "",
        "| Status | Skills | Findings | Critical | Warning |",
        "|---|---:|---:|---:|---:|",
        f"| {_markdown(summary['status'])} | {summary['skills']} | {summary['findings']} | {summary['critical']} | {summary['warning']} |",
        "", "## Findings", "",
    ]
    findings = report.get("findings", [])
    if not findings:
        lines.append("No health findings.")
    else:
        lines += ["| Severity | Skill | Dimension | Reason | Remediation |", "|---|---|---|---|---|"]
        for item in findings:
            lines.append("| " + " | ".join(_markdown(item[key]) for key in ("severity", "skill", "dimension", "reason", "remediation")) + " |")
    return "\n".join(lines) + "\n"
