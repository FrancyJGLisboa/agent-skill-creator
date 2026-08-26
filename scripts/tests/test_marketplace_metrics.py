"""Privacy and aggregation contracts for marketplace product metrics."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import marketplace_metrics as metrics  # noqa: E402


NOW = datetime(2026, 8, 25, 12, tzinfo=timezone.utc)
SALT = b"local-secret-salt-32-bytes-long"


def consent() -> dict[str, object]:
    return {
        "schema": metrics.CONSENT_SCHEMA,
        "schema_version": 1,
        "enabled": True,
        "approved_at": "2026-08-01T00:00:00Z",
        "expires_at": "2027-08-01T00:00:00Z",
        "allowed_events": sorted(metrics.EVENT_TYPES),
    }


def event(kind: str, skill: str = "revenue-review", *, success: bool = True, minute: int = 0) -> dict[str, object]:
    return metrics.create_event(
        kind, skill_name=skill, salt=SALT,
        timestamp=datetime(2026, 8, 25, 12, minute, tzinfo=timezone.utc),
        success=success, duration_ms=1200, platform="codex",
    )


def test_closed_event_vocabulary_covers_product_funnel() -> None:
    assert metrics.EVENT_TYPES == {"install", "activation", "successful_run", "correction", "regression", "retention"}


def test_skill_identifier_is_local_salted_and_stable() -> None:
    first = metrics.pseudonymous_skill_id("revenue-review", SALT)
    assert first == metrics.pseudonymous_skill_id("revenue-review", SALT)
    assert first != metrics.pseudonymous_skill_id("revenue-review", b"another-local-secret-salt")
    assert "revenue" not in first


def test_event_contains_only_privacy_safe_allowlisted_fields() -> None:
    created = event("activation")
    assert set(created) == {"schema_version", "event", "skill_id", "timestamp", "success", "duration_ms", "platform"}
    assert "revenue-review" not in json.dumps(created)


def test_copilot_metrics_alias_is_stored_canonically() -> None:
    created = metrics.create_event(
        "install", skill_name="x", salt=SALT, timestamp=NOW,
        success=True, platform="copilot",
    )
    assert created["platform"] == "github-copilot"


@pytest.mark.parametrize("field", ["prompt", "input", "output", "path", "person_id", "organization", "email", "run_id"])
def test_event_rejects_extra_or_content_shaped_fields(field: str) -> None:
    created = event("activation")
    created[field] = "sensitive"
    with pytest.raises(metrics.MetricsError, match="field"):
        metrics.validate_event(created)


def test_invalid_platform_and_duration_fail_closed() -> None:
    with pytest.raises(metrics.MetricsError, match="platform"):
        metrics.create_event("install", skill_name="x", salt=SALT, timestamp=NOW, success=True, platform="unknown-agent")
    with pytest.raises(metrics.MetricsError, match="duration"):
        metrics.create_event("install", skill_name="x", salt=SALT, timestamp=NOW, success=True, duration_ms=-1)


@pytest.mark.parametrize("change", [{}, {"enabled": False}, {"schema_version": 9}, {"expires_at": "2020-01-01T00:00:00Z"}, {"allowed_events": ["install"]}])
def test_recording_without_valid_explicit_consent_is_noop(tmp_path: Path, change: dict[str, object]) -> None:
    artifact = consent() if change else {}
    artifact.update(change)
    ledger = tmp_path / "metrics.jsonl"
    assert metrics.record_event(ledger, event("install"), artifact, now=NOW) is False
    assert not ledger.exists()


def test_recording_with_consent_appends_local_jsonl(tmp_path: Path) -> None:
    ledger = tmp_path / "metrics.jsonl"
    assert metrics.record_event(ledger, event("install"), consent(), now=NOW) is True
    assert metrics.record_event(ledger, event("activation", minute=1), consent(), now=NOW) is True
    assert len(ledger.read_text(encoding="utf-8").splitlines()) == 2


def test_summary_metrics_are_deterministic_and_malformed_is_counted() -> None:
    rows = [
        event("install", "a"), event("activation", "a", minute=1),
        event("successful_run", "a", minute=2), event("retention", "a", minute=3),
        event("install", "b"), event("regression", "b", minute=1),
        event("correction", "b", minute=2),
    ]
    lines = [json.dumps(row) for row in reversed(rows)] + ["not-json", json.dumps({"event": "install"})]
    summary = metrics.aggregate_events(lines)
    assert summary == metrics.aggregate_events(list(reversed(lines)))
    assert summary["counts"]["valid"] == 7
    assert summary["counts"]["malformed"] == 2
    assert summary["rates"]["install_to_activation"] == {"numerator": 1, "denominator": 2, "rate": 0.5}
    assert summary["rates"]["successful_use"] == {"numerator": 1, "denominator": 1, "rate": 1.0}
    assert summary["rates"]["correction_recovery"] == {"numerator": 1, "denominator": 1, "rate": 1.0}
    assert summary["rates"]["retention"] == {"numerator": 1, "denominator": 1, "rate": 1.0}


def test_failed_events_do_not_count_as_funnel_success() -> None:
    rows = [event("install"), event("activation", success=False, minute=1), event("successful_run", success=False, minute=2)]
    summary = metrics.aggregate_events([json.dumps(row) for row in rows])
    assert summary["rates"]["install_to_activation"]["numerator"] == 0
    assert summary["rates"]["successful_use"]["denominator"] == 0


def test_correction_only_recovers_a_prior_regression() -> None:
    rows = [event("correction", minute=1), event("regression", minute=2)]
    summary = metrics.aggregate_events([json.dumps(row) for row in rows])
    assert summary["rates"]["correction_recovery"]["numerator"] == 0


def test_retention_windows_use_elapsed_utc_time() -> None:
    base = datetime(2026, 7, 1, tzinfo=timezone.utc)
    rows = [
        metrics.create_event("install", skill_name="a", salt=SALT, timestamp=base, success=True),
        metrics.create_event("activation", skill_name="a", salt=SALT, timestamp=base, success=True),
        metrics.create_event("successful_run", skill_name="a", salt=SALT, timestamp=base, success=True),
        metrics.create_event("retention", skill_name="a", salt=SALT, timestamp=datetime(2026, 7, 9, tzinfo=timezone.utc), success=True),
        metrics.create_event("retention", skill_name="a", salt=SALT, timestamp=datetime(2026, 7, 30, tzinfo=timezone.utc), success=True),
    ]
    summary = metrics.aggregate_events([json.dumps(row) for row in rows])
    assert summary["retention_windows"]["7_day"] == {"numerator": 1, "denominator": 1, "rate": 1.0}
    assert summary["retention_windows"]["28_day"] == {"numerator": 1, "denominator": 1, "rate": 1.0}
