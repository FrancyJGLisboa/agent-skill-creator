"""Tests for the deterministic schema-v2 marketplace health engine."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import marketplace_health as health  # noqa: E402


TODAY = date(2026, 8, 25)


def skill_entry(name: str = "report-skill") -> dict[str, object]:
    return {
        "name": name,
        "department": "finance",
        "version": "1.2.3",
        "path": f"skills/finance/{name}",
        "owners": ["alice", "finance-team"],
        "quality": {"evals": {"passed": True, "regressions": 0}},
        "dependencies": [{"name": "ledger-api", "url": "https://ledger.example/v1"}],
        "dependency_health": [{"name": "ledger-api", "status": "healthy", "checked_at": "2026-08-24T12:00:00Z"}],
        "compatibility": {
            "declared": ["codex", "cursor"],
            "certified": [
                {"platform": "codex", "passed": True, "version": "1.2.3"},
                {"platform": "cursor", "passed": True, "version": "1.2.3"},
            ],
        },
    }


def write_skill(root: Path, name: str = "report-skill", reviewed: str = "2026-08-01") -> None:
    directory = root / "skills" / "finance" / name
    directory.mkdir(parents=True)
    (directory / "SKILL.md").write_text(
        f"""---
name: {name}
description: Generate a governed finance report from approved inputs.
metadata:
  last_reviewed: {reviewed}
  review_interval_days: 90
---
# Report
""",
        encoding="utf-8",
    )


def registry(entry: dict[str, object]) -> dict[str, object]:
    return {"schema_version": 2, "marketplace": {"name": "ACME Skills"}, "skills": [entry]}


def test_healthy_skill_evaluates_every_health_dimension(tmp_path: Path) -> None:
    write_skill(tmp_path)
    report = health.build_health_report(registry(skill_entry()), tmp_path, TODAY, {"alice"})
    item = report["skills"][0]
    assert list(item["checks"]) == list(health.HEALTH_DIMENSIONS)
    assert all(check["status"] == "healthy" for check in item["checks"].values())
    assert report["summary"] == {"status": "healthy", "skills": 1, "findings": 0, "critical": 0, "warning": 0}


def test_all_dimensions_emit_actionable_findings(tmp_path: Path) -> None:
    write_skill(tmp_path, reviewed="2025-01-01")
    entry = skill_entry()
    entry["dependency_health"] = [{"name": "ledger-api", "status": "unreachable", "checked_at": "2026-08-24T12:00:00Z"}]
    entry["quality"] = {"evals": {"passed": False, "regressions": 2}}
    entry["owners"] = ["former-user"]
    entry["compatibility"] = {
        "declared": ["codex", "cursor"],
        "certified": [{"platform": "codex", "passed": True, "version": "1.2.3"}],
    }
    entry["discovery"] = {
        "semantic_contract": {
            "applies": True,
            "definitions": [{
                "id": "revenue", "version": "1.0.0", "definition": "Booked revenue",
                "scope": "Finance reporting", "grain": "invoice_id", "unit": "USD",
                "source_precedence": ["ledger"], "owner": "finance",
                "valid_from": "2025-01-01", "last_reviewed": "2025-01-01",
                "review_interval_days": 30,
            }],
            "dependencies": [{"id": "revenue", "version": "1.0.0"}],
            "ambiguity": {"allowed_outcomes": ["answer", "ask", "refuse_unknown"],
                          "unresolved_action": "ask", "clarification": "Which revenue?"},
        },
    }
    report = health.build_health_report(registry(entry), tmp_path, TODAY, {"alice"})
    findings = report["findings"]
    assert {finding["dimension"] for finding in findings} == set(health.HEALTH_DIMENSIONS)
    assert all(finding["severity"] in {"warning", "critical"} for finding in findings)
    assert all(finding["reason"] and finding["remediation"] for finding in findings)
    assert report["summary"]["status"] == "critical"


def test_missing_dependency_evidence_is_not_treated_as_healthy(tmp_path: Path) -> None:
    write_skill(tmp_path)
    entry = skill_entry()
    entry["dependency_health"] = []
    finding = next(
        item for item in health.build_health_report(registry(entry), tmp_path, TODAY, {"alice"})["findings"]
        if item["dimension"] == "dependency_health"
    )
    assert finding["severity"] == "warning"
    assert "evidence" in finding["reason"].lower()


def test_inactive_team_owner_does_not_mask_active_person(tmp_path: Path) -> None:
    write_skill(tmp_path)
    report = health.build_health_report(registry(skill_entry()), tmp_path, TODAY, {"finance-team"})
    assert not [f for f in report["findings"] if f["dimension"] == "owner_presence"]


def test_compatibility_certification_must_match_skill_version(tmp_path: Path) -> None:
    write_skill(tmp_path)
    entry = skill_entry()
    entry["compatibility"]["certified"][1]["version"] = "1.2.2"  # type: ignore[index]
    findings = health.build_health_report(registry(entry), tmp_path, TODAY, {"alice"})["findings"]
    assert any(f["dimension"] == "compatibility" and "cursor" in f["reason"] for f in findings)


def test_compatibility_declared_only_in_discovery_is_still_governed(tmp_path: Path) -> None:
    write_skill(tmp_path)
    entry = skill_entry()
    entry.pop("compatibility")
    entry["discovery"] = {
        "outcome": "Prepare monthly finance reporting",
        "support_tier": "supported",
        "compatibility": {
            "declared": ["codex", "cursor"],
            "certified": [{"platform": "codex", "passed": True, "version": "1.2.3"}],
        },
    }
    findings = health.build_health_report(registry(entry), tmp_path, TODAY, {"alice"})["findings"]
    assert any(f["dimension"] == "compatibility" and "cursor" in f["reason"] for f in findings)


def test_healthy_discovery_compatibility_renders_without_legacy_registry_field(tmp_path: Path) -> None:
    write_skill(tmp_path)
    entry = skill_entry()
    entry.pop("compatibility")
    entry["discovery"] = {
        "outcome": "Prepare monthly finance reporting",
        "support_tier": "supported",
        "compatibility": {
            "declared": ["codex"],
            "certified": [{"platform": "codex", "passed": True, "version": "1.2.3"}],
        },
    }
    report = health.build_health_report(registry(entry), tmp_path, TODAY, {"alice"})
    assert report["skills"][0]["checks"]["compatibility"]["status"] == "healthy"


def test_stale_semantic_definition_is_critical(tmp_path: Path) -> None:
    write_skill(tmp_path)
    entry = skill_entry()
    entry["discovery"] = {
        "semantic_contract": {
            "applies": True,
            "definitions": [{
                "id": "active-customer", "version": "1.0.0",
                "definition": "Commercial active customer", "scope": "Direct B2B",
                "grain": "customer_id", "unit": "customers",
                "source_precedence": ["billing.contract"], "owner": "finance",
                "valid_from": "2025-01-01", "last_reviewed": "2025-01-01",
                "review_interval_days": 30,
            }],
            "dependencies": [{"id": "active-customer", "version": "1.0.0"}],
            "ambiguity": {"allowed_outcomes": ["answer", "ask", "refuse_unknown"],
                          "unresolved_action": "ask", "clarification": "Which context?"},
        },
    }
    findings = health.build_health_report(registry(entry), tmp_path, TODAY, {"alice"})["findings"]
    finding = next(item for item in findings if item["dimension"] == "semantic_freshness")
    assert finding["severity"] == "critical"
    assert "active-customer" in finding["reason"]


def test_report_json_is_deterministic_and_round_trippable(tmp_path: Path) -> None:
    write_skill(tmp_path)
    report = health.build_health_report(registry(skill_entry()), tmp_path, TODAY, {"alice"})
    first = health.report_json(report)
    second = health.report_json(health.build_health_report(registry(skill_entry()), tmp_path, TODAY, {"alice"}))
    assert first == second
    assert json.loads(first) == report
    assert "generated_at" not in report


def test_report_markdown_is_readable_deterministic_and_escaped(tmp_path: Path) -> None:
    write_skill(tmp_path)
    entry = skill_entry("report-skill")
    entry["owners"] = []
    report = health.build_health_report(registry(entry), tmp_path, TODAY, set())
    first = health.report_markdown(report)
    assert first == health.report_markdown(report)
    assert "# ACME Skills Health Report" in first
    assert "## Summary" in first and "## Findings" in first
    assert "Add at least one active owner" in first


def test_skill_paths_cannot_escape_marketplace_root(tmp_path: Path) -> None:
    entry = skill_entry()
    entry["path"] = "../outside"
    report = health.build_health_report(registry(entry), tmp_path, TODAY, {"alice"})
    review = next(f for f in report["findings"] if f["dimension"] == "review_staleness")
    assert review["severity"] == "critical"
    assert "unsafe" in review["reason"].lower()


def test_skill_order_and_findings_are_stable(tmp_path: Path) -> None:
    write_skill(tmp_path, "zeta-skill")
    write_skill(tmp_path, "alpha-skill")
    data = registry(skill_entry("zeta-skill"))
    data["skills"].append(skill_entry("alpha-skill"))  # type: ignore[union-attr]
    report = health.build_health_report(data, tmp_path, TODAY, {"alice"})
    assert [item["identity"] for item in report["skills"]] == ["finance/alpha-skill", "finance/zeta-skill"]
