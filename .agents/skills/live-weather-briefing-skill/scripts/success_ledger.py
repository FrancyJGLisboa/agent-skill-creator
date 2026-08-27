#!/usr/bin/env python3
"""Local lifecycle ledger and product-success metrics for generated skills.

The ledger is deliberately narrow: it stores fixed event names, timestamps,
pseudonymous skill IDs, run IDs, outcomes, and optional durations. It never
stores prompts, workflow descriptions, inputs, outputs, corrections, paths,
credentials, or network destinations, and it never transmits data.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import secrets
import statistics
import sys
import time
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path


SCHEMA_VERSION = 1
DISABLE_VALUE = "off"
ALLOWED_EVENTS = {
    "creation_started",
    "intent_confirmed",
    "gates_passed",
    "representative_run_passed",
    "skill_run",
    "correction_recorded",
    "regression_detected",
    "skill_shared",
}
RESULTS = {"success", "failure"}
SALT_FILE = ".success-ledger-salt"
SALT_SIZE = 32
SALT_LOCK_TIMEOUT_SECONDS = 5.0


def default_ledger_path() -> Path | None:
    """Return the local ledger path, or None when recording is disabled."""
    configured = os.environ.get("ASC_SUCCESS_LEDGER")
    if configured and configured.lower() == DISABLE_VALUE:
        return None
    if configured:
        return Path(configured).expanduser()
    state_root = os.environ.get("XDG_STATE_HOME")
    if state_root:
        return Path(state_root) / "agent-skill-creator" / "success-events.jsonl"
    if os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        return Path(os.environ["LOCALAPPDATA"]) / "agent-skill-creator" / "success-events.jsonl"
    return Path.home() / ".local" / "state" / "agent-skill-creator" / "success-events.jsonl"


def _salt(ledger_path: Path) -> bytes:
    salt_path = ledger_path.parent / SALT_FILE
    ledger_path.parent.mkdir(parents=True, exist_ok=True)

    def read_valid_salt() -> bytes | None:
        try:
            value = salt_path.read_bytes()
        except (FileNotFoundError, PermissionError):
            return None
        return value if len(value) == SALT_SIZE else None

    existing = read_valid_salt()
    if existing is not None:
        return existing

    lock_path = salt_path.with_name(f"{salt_path.name}.lock")
    deadline = time.monotonic() + SALT_LOCK_TIMEOUT_SECONDS
    while True:
        try:
            lock_descriptor = os.open(
                lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
            )
        except (FileExistsError, PermissionError):
            # Windows can report a sharing violation as PermissionError while
            # another thread owns an O_EXCL-created lock file.
            existing = read_valid_salt()
            if existing is not None:
                return existing
            if time.monotonic() >= deadline:
                raise TimeoutError(f"timed out initializing privacy salt: {salt_path}")
            time.sleep(0.01)
            continue

        os.close(lock_descriptor)
        temporary_path = salt_path.with_name(
            f"{salt_path.name}.{secrets.token_hex(8)}.tmp"
        )
        try:
            existing = read_valid_salt()
            if existing is None:
                value = secrets.token_bytes(SALT_SIZE)
                descriptor = os.open(
                    temporary_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
                )
                try:
                    with os.fdopen(descriptor, "wb") as handle:
                        handle.write(value)
                        handle.flush()
                        os.fsync(handle.fileno())
                except BaseException:
                    temporary_path.unlink(missing_ok=True)
                    raise
                os.replace(temporary_path, salt_path)
                try:
                    salt_path.chmod(0o600)
                except OSError:
                    pass
                return value
            return existing
        finally:
            temporary_path.unlink(missing_ok=True)
            lock_path.unlink(missing_ok=True)


def _skill_id(skill: str, ledger_path: Path) -> str:
    normalized = skill.strip()
    if not normalized:
        raise ValueError("skill identifier is empty")
    return hmac.new(_salt(ledger_path), normalized.encode("utf-8"), hashlib.sha256).hexdigest()[:20]


def _append_line(destination: Path, line: str) -> None:
    lock_path = destination.with_name(f"{destination.name}.lock")
    deadline = time.monotonic() + SALT_LOCK_TIMEOUT_SECONDS
    while True:
        try:
            descriptor = os.open(
                lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
            )
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise TimeoutError(f"timed out appending to success ledger: {destination}")
            time.sleep(0.01)
            continue
        os.close(descriptor)
        break

    try:
        with destination.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        lock_path.unlink(missing_ok=True)


def _timestamp(value: datetime | None) -> datetime:
    stamp = value or datetime.now(timezone.utc)
    if stamp.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return stamp.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return value.isoformat(timespec="seconds").replace("+00:00", "Z")


def record_event(
    event: str,
    *,
    skill: str,
    ledger_path: str | Path | None = None,
    timestamp: datetime | None = None,
    run_id: str | None = None,
    result: str = "success",
    duration_seconds: float | None = None,
) -> dict | None:
    """Append one allowlisted event without storing the skill's name or content."""
    if event not in ALLOWED_EVENTS:
        raise ValueError(f"unknown event: {event}")
    if result not in RESULTS:
        raise ValueError(f"result must be one of: {', '.join(sorted(RESULTS))}")
    if duration_seconds is not None and duration_seconds < 0:
        raise ValueError("duration_seconds must be non-negative")
    destination = Path(ledger_path) if ledger_path is not None else default_ledger_path()
    if destination is None:
        return None

    if run_id is not None:
        try:
            normalized_run_id = str(uuid.UUID(run_id))
        except ValueError as exc:
            raise ValueError("run_id must be a UUID from the new-run command") from exc
    else:
        normalized_run_id = str(uuid.uuid4())
    item = {
        "schema_version": SCHEMA_VERSION,
        "event": event,
        "skill_id": _skill_id(skill, destination),
        "timestamp": _iso(_timestamp(timestamp)),
        "run_id": normalized_run_id,
        "result": result,
        "duration_seconds": duration_seconds,
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    _append_line(
        destination, json.dumps(item, separators=(",", ":"), sort_keys=True) + "\n"
    )
    try:
        destination.chmod(0o600)
    except OSError:
        pass
    return item


def _parse_stamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _read_events(ledger_path: Path, as_of: datetime) -> tuple[list[dict], int]:
    events: list[dict] = []
    malformed = 0
    if not ledger_path.exists():
        return events, malformed
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
            stamp = _parse_stamp(item["timestamp"])
            if item["event"] not in ALLOWED_EVENTS or item["result"] not in RESULTS:
                raise ValueError("invalid vocabulary")
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            malformed += 1
            continue
        if stamp <= as_of:
            events.append({**item, "_stamp": stamp})
    events.sort(key=lambda item: item["_stamp"])
    return events, malformed


def _rate(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 4) if denominator else None


def summarize(
    ledger_path: str | Path,
    *,
    as_of: datetime | None = None,
    active_window_days: int = 28,
    second_run_days: int = 14,
) -> dict:
    """Compute activation, retention, quality, and distribution metrics."""
    now = _timestamp(as_of)
    if active_window_days < 1 or second_run_days < 1:
        raise ValueError("metric windows must be positive")
    events, malformed = _read_events(Path(ledger_path), now)
    by_skill: dict[str, list[dict]] = defaultdict(list)
    by_run: dict[str, list[dict]] = defaultdict(list)
    for event in events:
        by_skill[event["skill_id"]].append(event)
        by_run[event["run_id"]].append(event)

    starts = [event for event in events if event["event"] == "creation_started"]
    verified: list[tuple[dict, dict]] = []
    for start in starts:
        completions = [
            event
            for event in by_run[start["run_id"]]
            if event["event"] == "representative_run_passed"
            and event["result"] == "success"
            and event["_stamp"] >= start["_stamp"]
        ]
        if completions:
            verified.append((start, completions[0]))

    minutes = [
        (completion["_stamp"] - start["_stamp"]).total_seconds() / 60
        for start, completion in verified
    ]
    eligible_second_runs = [
        pair for pair in verified if pair[1]["_stamp"] <= now - timedelta(days=second_run_days)
    ]
    returned = 0
    for _, completion in eligible_second_runs:
        deadline = completion["_stamp"] + timedelta(days=second_run_days)
        if any(
            event["event"] == "skill_run"
            and event["result"] == "success"
            and completion["_stamp"] < event["_stamp"] <= deadline
            for event in by_skill[completion["skill_id"]]
        ):
            returned += 1

    active_since = now - timedelta(days=active_window_days)
    durable: set[str] = set()
    for skill_id, skill_events in by_skill.items():
        successful_runs = [
            event
            for event in skill_events
            if event["event"] in {"representative_run_passed", "skill_run"}
            and event["result"] == "success"
            and event["_stamp"] >= active_since
        ]
        last_gate = max(
            (
                event["_stamp"]
                for event in skill_events
                if event["event"] == "gates_passed" and event["result"] == "success"
            ),
            default=None,
        )
        last_regression = max(
            (event["_stamp"] for event in skill_events if event["event"] == "regression_detected"),
            default=None,
        )
        regression_resolved = last_regression is None or (
            last_gate is not None and last_gate > last_regression
        )
        if (
            len(successful_runs) >= 3
            and len({event["_stamp"].date() for event in successful_runs}) >= 2
            and last_gate is not None
            and regression_resolved
        ):
            durable.add(skill_id)

    corrections = [event for event in events if event["event"] == "correction_recorded"]
    recovered = 0
    for correction in corrections:
        later = [
            event
            for event in by_skill[correction["skill_id"]]
            if event["_stamp"] > correction["_stamp"]
        ]
        latest_gate = max(
            (
                event["_stamp"]
                for event in later
                if event["event"] == "gates_passed" and event["result"] == "success"
            ),
            default=None,
        )
        latest_regression = max(
            (event["_stamp"] for event in later if event["event"] == "regression_detected"),
            default=None,
        )
        if latest_gate is not None and (
            latest_regression is None or latest_gate > latest_regression
        ):
            recovered += 1

    shared_durable = sum(
        any(
            event["event"] == "skill_shared" and event["result"] == "success"
            for event in by_skill[skill_id]
        )
        for skill_id in durable
    )
    return {
        "as_of": _iso(now),
        "active_window_days": active_window_days,
        "second_run_window_days": second_run_days,
        "counts": {
            "events": len(events),
            "malformed_events_skipped": malformed,
            "creations_started": len(starts),
            "verified_creations": len(verified),
            "eligible_for_second_run": len(eligible_second_runs),
            "corrections": len(corrections),
        },
        "verified_creation_rate": _rate(len(verified), len(starts)),
        "median_minutes_to_first_result": round(statistics.median(minutes), 2) if minutes else None,
        "fourteen_day_second_run_rate": _rate(returned, len(eligible_second_runs)),
        "durable_active_skills": len(durable),
        "correction_recovery_rate": _rate(recovered, len(corrections)),
        "shared_durable_skill_rate": _rate(shared_durable, len(durable)),
    }


def _print_summary(summary: dict) -> None:
    def percentage(value: float | None) -> str:
        return "n/a" if value is None else f"{value * 100:.1f}%"

    print(f"Durable active skills:       {summary['durable_active_skills']}")
    print(f"Verified creation rate:      {percentage(summary['verified_creation_rate'])}")
    median = summary["median_minutes_to_first_result"]
    print(f"Median to first result:      {'n/a' if median is None else f'{median:.1f} min'}")
    print(f"14-day second-run rate:      {percentage(summary['fourteen_day_second_run_rate'])}")
    print(f"Correction recovery rate:    {percentage(summary['correction_recovery_rate'])}")
    print(f"Shared durable-skill rate:   {percentage(summary['shared_durable_skill_rate'])}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Record local skill lifecycle events and summarize product success.")
    parser.add_argument("--ledger", help="Override the local JSONL ledger path.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    record = subparsers.add_parser("record")
    record.add_argument("event", choices=sorted(ALLOWED_EVENTS))
    record.add_argument("--skill", required=True, help="Hashed locally; never written in plaintext.")
    record.add_argument("--run-id")
    record.add_argument("--result", choices=sorted(RESULTS), default="success")
    record.add_argument("--duration-seconds", type=float)
    summary_parser = subparsers.add_parser("summary")
    summary_parser.add_argument("--json", action="store_true")
    summary_parser.add_argument("--as-of", help="ISO-8601 timestamp for reproducible reports.")
    summary_parser.add_argument("--active-window-days", type=int, default=28)
    summary_parser.add_argument("--second-run-days", type=int, default=14)
    subparsers.add_parser("path")
    subparsers.add_parser("new-run")
    args = parser.parse_args(argv)

    destination = Path(args.ledger) if args.ledger else default_ledger_path()
    if args.command == "new-run":
        print(uuid.uuid4())
        return 0
    if args.command == "path":
        print("disabled" if destination is None else destination)
        return 0
    if args.command == "record":
        try:
            item = record_event(
                args.event,
                skill=args.skill,
                ledger_path=destination,
                run_id=args.run_id,
                result=args.result,
                duration_seconds=args.duration_seconds,
            )
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        print("recording disabled" if item is None else f"recorded {item['event']} for {item['skill_id']}")
        return 0
    if destination is None:
        print("error: recording is disabled; set ASC_SUCCESS_LEDGER to a local path", file=sys.stderr)
        return 2
    try:
        as_of = _parse_stamp(args.as_of) if args.as_of else None
        report = summarize(
            destination,
            as_of=as_of,
            active_window_days=args.active_window_days,
            second_run_days=args.second_run_days,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        _print_summary(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
