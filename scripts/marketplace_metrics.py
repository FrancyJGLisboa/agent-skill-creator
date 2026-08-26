#!/usr/bin/env python3
"""Consent-gated, privacy-safe local marketplace product measurement."""

from __future__ import annotations

import hashlib
import hmac
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from platforms import normalize_platform_name

CONSENT_SCHEMA = "agent-skill-creator.marketplace-metrics-consent"
EVENT_TYPES = {"install", "activation", "successful_run", "correction", "regression", "retention"}
PLATFORM_ALLOWLIST = {
    "codex", "claude-code", "github-copilot", "cursor", "windsurf", "cline",
    "gemini-cli", "vscode-copilot", "other-approved",
}
EVENT_FIELDS = {
    "schema_version", "event", "skill_id", "timestamp", "success",
    "duration_ms", "platform",
}
_SKILL_ID = re.compile(r"^skill_[0-9a-f]{32}$")


class MetricsError(ValueError):
    """Consent or event data violates the privacy contract."""


def _rfc3339(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise MetricsError("timestamp must include a timezone")
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None


def pseudonymous_skill_id(skill_name: str, salt: bytes) -> str:
    """Derive a non-reversible, installation-local identifier."""
    if not isinstance(salt, bytes) or len(salt) < 16:
        raise MetricsError("local metrics salt must contain at least 16 bytes")
    if not isinstance(skill_name, str) or not skill_name.strip() or "\x00" in skill_name:
        raise MetricsError("skill name is required for local pseudonymization")
    digest = hmac.new(salt, skill_name.strip().encode("utf-8"), hashlib.sha256).hexdigest()
    return "skill_" + digest[:32]


def create_event(
    event: str, *, skill_name: str, salt: bytes, timestamp: datetime, success: bool,
    duration_ms: int | None = None, platform: str | None = None,
) -> dict[str, object]:
    """Create one allowlisted event without workflow or identity content."""
    if event not in EVENT_TYPES:
        raise MetricsError(f"event must be one of: {', '.join(sorted(EVENT_TYPES))}")
    if type(success) is not bool:
        raise MetricsError("success must be a boolean")
    result: dict[str, object] = {
        "schema_version": 1,
        "event": event,
        "skill_id": pseudonymous_skill_id(skill_name, salt),
        "timestamp": _rfc3339(timestamp),
        "success": success,
    }
    if duration_ms is not None:
        if type(duration_ms) is not int or not 0 <= duration_ms <= 86_400_000:
            raise MetricsError("duration_ms must be an integer from 0 through 86400000")
        result["duration_ms"] = duration_ms
    if platform is not None:
        normalized = normalize_platform_name(platform) if isinstance(platform, str) else ""
        if normalized not in PLATFORM_ALLOWLIST:
            raise MetricsError("platform is not in the approved allowlist")
        result["platform"] = normalized
    validate_event(result)
    return result


def validate_event(event: object) -> list[str]:
    """Validate exact event shape; raise on extra fields to prevent content capture."""
    if not isinstance(event, Mapping):
        raise MetricsError("event must be a JSON object")
    extras = set(event) - EVENT_FIELDS
    if extras:
        raise MetricsError("event contains forbidden field(s): " + ", ".join(sorted(extras)))
    errors: list[str] = []
    required = {"schema_version", "event", "skill_id", "timestamp", "success"}
    missing = required - set(event)
    if missing:
        errors.append("missing required field(s): " + ", ".join(sorted(missing)))
    if event.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if event.get("event") not in EVENT_TYPES:
        errors.append("event type is not allowed")
    if not isinstance(event.get("skill_id"), str) or not _SKILL_ID.fullmatch(str(event.get("skill_id", ""))):
        errors.append("skill_id must be a salted pseudonymous identifier")
    if _parse_timestamp(event.get("timestamp")) is None:
        errors.append("timestamp must be UTC RFC 3339")
    if type(event.get("success")) is not bool:
        errors.append("success must be a boolean")
    duration = event.get("duration_ms")
    if duration is not None and (type(duration) is not int or not 0 <= duration <= 86_400_000):
        errors.append("duration_ms is invalid")
    platform = event.get("platform")
    if platform is not None and platform not in PLATFORM_ALLOWLIST:
        errors.append("platform is not allowed")
    return errors


def validate_consent(consent: object, *, now: datetime) -> list[str]:
    """Require an explicit, current artifact authorizing the complete closed vocabulary."""
    if not isinstance(consent, Mapping):
        return ["metrics consent artifact is required"]
    errors: list[str] = []
    if consent.get("schema") != CONSENT_SCHEMA:
        errors.append("consent schema is invalid")
    if consent.get("schema_version") != 1:
        errors.append("consent schema_version must be 1")
    if consent.get("enabled") is not True:
        errors.append("organizational metrics consent is not enabled")
    approved = _parse_timestamp(consent.get("approved_at"))
    expires = _parse_timestamp(consent.get("expires_at"))
    reference = now.astimezone(timezone.utc) if now.tzinfo and now.utcoffset() is not None else None
    if reference is None:
        errors.append("consent validation time must include a timezone")
    if approved is None or (reference is not None and approved > reference):
        errors.append("consent approved_at is invalid or in the future")
    if expires is None or (reference is not None and expires <= reference):
        errors.append("consent has expired or expires_at is invalid")
    allowed = consent.get("allowed_events")
    safe_allowed = {item for item in allowed if isinstance(item, str)} if isinstance(allowed, list) else set()
    if not isinstance(allowed, list) or safe_allowed != EVENT_TYPES or len(allowed) != len(EVENT_TYPES):
        errors.append("consent must explicitly allow the closed event vocabulary")
    return errors


def record_event(path: Path, event: Mapping[str, object], consent: object, *, now: datetime) -> bool:
    """Append local JSONL only with valid consent; invalid consent is a safe no-op."""
    if validate_consent(consent, now=now):
        return False
    errors = validate_event(event)
    if errors:
        raise MetricsError("; ".join(errors))
    if path.suffix != ".jsonl" or path.exists() and path.is_symlink():
        raise MetricsError("metrics ledger must be a non-symlink local .jsonl file")
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(encoded + "\n")
    return True


def _rate(numerator: int, denominator: int) -> dict[str, int | float]:
    return {
        "numerator": numerator,
        "denominator": denominator,
        "rate": round(numerator / denominator, 4) if denominator else 0.0,
    }


def aggregate_events(lines: Iterable[str]) -> dict[str, Any]:
    """Aggregate privacy-safe funnel and retention measures deterministically."""
    valid: list[Mapping[str, Any]] = []
    malformed = 0
    for line in lines:
        try:
            value = json.loads(line)
            errors = validate_event(value)
            if errors:
                malformed += 1
            else:
                valid.append(value)
        except (json.JSONDecodeError, TypeError, MetricsError):
            malformed += 1
    valid.sort(key=lambda item: (str(item["timestamp"]), str(item["skill_id"]), str(item["event"])))
    successful: dict[str, set[str]] = {kind: set() for kind in EVENT_TYPES}
    regressed_at: dict[str, str] = {}
    recovered: set[str] = set()
    first_use: dict[str, datetime] = {}
    retention_at: dict[str, list[datetime]] = {}
    event_counts = {kind: 0 for kind in sorted(EVENT_TYPES)}
    for item in valid:
        kind, skill_id = str(item["event"]), str(item["skill_id"])
        event_counts[kind] += 1
        if item["success"] is True:
            successful[kind].add(skill_id)
            timestamp = _parse_timestamp(item["timestamp"])
            if kind == "successful_run" and timestamp is not None:
                first_use.setdefault(skill_id, timestamp)
            elif kind == "retention" and timestamp is not None:
                retention_at.setdefault(skill_id, []).append(timestamp)
        if kind == "regression" and item["success"] is True:
            regressed_at[skill_id] = str(item["timestamp"])
        elif kind == "correction" and item["success"] is True and skill_id in regressed_at and str(item["timestamp"]) > regressed_at[skill_id]:
            recovered.add(skill_id)
    installed = successful["install"]
    activated = successful["activation"] & installed
    used = successful["successful_run"] & activated
    retained = successful["retention"] & used
    latest = max((_parse_timestamp(item["timestamp"]) for item in valid), default=None)
    window_rates: dict[str, dict[str, int | float]] = {}
    for days in (7, 28):
        eligible = {
            skill_id for skill_id in used
            if latest is not None and skill_id in first_use and latest - first_use[skill_id] >= timedelta(days=days)
        }
        reached = {
            skill_id for skill_id in eligible
            if any(moment - first_use[skill_id] >= timedelta(days=days) for moment in retention_at.get(skill_id, []))
        }
        window_rates[f"{days}_day"] = _rate(len(reached), len(eligible))
    return {
        "schema_version": 1,
        "counts": {"valid": len(valid), "malformed": malformed, "events": event_counts},
        "rates": {
            "install_to_activation": _rate(len(activated), len(installed)),
            "successful_use": _rate(len(used), len(activated)),
            "correction_recovery": _rate(len(recovered), len(regressed_at)),
            "retention": _rate(len(retained), len(used)),
        },
        "retention_windows": window_rates,
    }
