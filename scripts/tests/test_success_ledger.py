"""Tests for the local, privacy-preserving product success ledger."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from success_ledger import ALLOWED_EVENTS, record_event, summarize  # noqa: E402


UTC = timezone.utc


def run_id(label: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, label))


class SuccessLedgerPrivacyTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.ledger = self.root / "events.jsonl"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_record_contains_only_allowlisted_metadata_and_hashes_skill_name(self) -> None:
        record_event(
            "skill_run",
            skill="acme-secret-revenue-skill",
            ledger_path=self.ledger,
            timestamp=datetime(2026, 8, 1, 12, tzinfo=UTC),
            run_id=run_id("run-1"),
            duration_seconds=4.25,
        )

        raw = self.ledger.read_text(encoding="utf-8")
        event = json.loads(raw)
        self.assertNotIn("acme-secret-revenue-skill", raw)
        self.assertEqual(
            set(event),
            {"schema_version", "event", "skill_id", "timestamp", "run_id", "result", "duration_seconds"},
        )
        self.assertEqual(event["event"], "skill_run")
        self.assertRegex(event["skill_id"], r"^[0-9a-f]{20}$")

    def test_same_local_salt_produces_stable_pseudonymous_skill_id(self) -> None:
        for label in ("run-1", "run-2"):
            record_event(
                "skill_run",
                skill="private-skill",
                ledger_path=self.ledger,
                run_id=run_id(label),
            )

        events = [json.loads(line) for line in self.ledger.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(events[0]["skill_id"], events[1]["skill_id"])
        self.assertTrue((self.root / ".success-ledger-salt").exists())

    def test_unknown_events_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown event"):
            record_event("uploaded_customer_data", skill="demo", ledger_path=self.ledger)

    def test_run_id_must_be_an_opaque_uuid(self) -> None:
        with self.assertRaisesRegex(ValueError, "run_id must be a UUID"):
            record_event(
                "skill_run",
                skill="demo",
                ledger_path=self.ledger,
                run_id="customer-name-or-other-business-data",
            )

    def test_parallel_first_events_share_one_stable_salt(self) -> None:
        def write(index: int) -> str:
            item = record_event(
                "skill_run",
                skill="parallel-skill",
                ledger_path=self.ledger,
                run_id=run_id(f"parallel-{index}"),
            )
            assert item is not None
            return item["skill_id"]

        with ThreadPoolExecutor(max_workers=8) as pool:
            skill_ids = list(pool.map(write, range(20)))

        self.assertEqual(len(set(skill_ids)), 1)
        events = [json.loads(line) for line in self.ledger.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(events), 20)

    def test_event_vocabulary_is_fixed(self) -> None:
        self.assertEqual(
            ALLOWED_EVENTS,
            {
                "creation_started",
                "intent_confirmed",
                "gates_passed",
                "representative_run_passed",
                "skill_run",
                "correction_recorded",
                "regression_detected",
                "skill_shared",
            },
        )


class ProductMetricTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.ledger = self.root / "events.jsonl"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def record(self, event: str, skill: str, stamp: str, *, run_label: str, result: str = "success") -> None:
        record_event(
            event,
            skill=skill,
            ledger_path=self.ledger,
            timestamp=datetime.fromisoformat(stamp.replace("Z", "+00:00")),
            run_id=run_id(run_label),
            result=result,
        )

    def test_summary_computes_activation_retention_quality_and_distribution(self) -> None:
        # Skill A completes creation, returns within 14 days, reaches three runs
        # across two days, recovers from a correction, and is shared.
        self.record("creation_started", "skill-a", "2026-07-01T10:00:00Z", run_label="create-a")
        self.record("intent_confirmed", "skill-a", "2026-07-01T10:01:00Z", run_label="create-a")
        self.record("gates_passed", "skill-a", "2026-07-01T10:07:00Z", run_label="create-a")
        self.record("representative_run_passed", "skill-a", "2026-07-01T10:08:00Z", run_label="create-a")
        self.record("skill_run", "skill-a", "2026-07-05T09:00:00Z", run_label="use-a-1")
        self.record("correction_recorded", "skill-a", "2026-07-06T09:00:00Z", run_label="fix-a")
        self.record("regression_detected", "skill-a", "2026-07-06T09:01:00Z", run_label="fix-a")
        self.record("gates_passed", "skill-a", "2026-07-06T09:05:00Z", run_label="fix-a")
        self.record("skill_run", "skill-a", "2026-07-06T10:00:00Z", run_label="use-a-2")
        self.record("skill_shared", "skill-a", "2026-07-07T10:00:00Z", run_label="share-a")

        # Skill B starts but never verifies.
        self.record("creation_started", "skill-b", "2026-07-02T10:00:00Z", run_label="create-b")

        summary = summarize(
            self.ledger,
            as_of=datetime(2026, 7, 20, tzinfo=UTC),
            active_window_days=28,
            second_run_days=14,
        )

        self.assertEqual(summary["counts"]["creations_started"], 2)
        self.assertEqual(summary["counts"]["verified_creations"], 1)
        self.assertEqual(summary["verified_creation_rate"], 0.5)
        self.assertEqual(summary["median_minutes_to_first_result"], 8.0)
        self.assertEqual(summary["fourteen_day_second_run_rate"], 1.0)
        self.assertEqual(summary["durable_active_skills"], 1)
        self.assertEqual(summary["correction_recovery_rate"], 1.0)
        self.assertEqual(summary["shared_durable_skill_rate"], 1.0)

    def test_unresolved_regression_excludes_otherwise_durable_skill(self) -> None:
        self.record("gates_passed", "skill-a", "2026-08-01T08:00:00Z", run_label="gate")
        self.record("representative_run_passed", "skill-a", "2026-08-01T09:00:00Z", run_label="first")
        self.record("skill_run", "skill-a", "2026-08-02T09:00:00Z", run_label="second")
        self.record("skill_run", "skill-a", "2026-08-03T09:00:00Z", run_label="third")
        self.record("regression_detected", "skill-a", "2026-08-04T09:00:00Z", run_label="regression")

        summary = summarize(self.ledger, as_of=datetime(2026, 8, 5, tzinfo=UTC))

        self.assertEqual(summary["durable_active_skills"], 0)

    def test_new_regression_after_recovery_gate_keeps_correction_unresolved(self) -> None:
        self.record("correction_recorded", "skill-a", "2026-08-01T08:00:00Z", run_label="fix")
        self.record("gates_passed", "skill-a", "2026-08-01T09:00:00Z", run_label="gate")
        self.record("regression_detected", "skill-a", "2026-08-01T10:00:00Z", run_label="regression")

        summary = summarize(self.ledger, as_of=datetime(2026, 8, 2, tzinfo=UTC))

        self.assertEqual(summary["correction_recovery_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
