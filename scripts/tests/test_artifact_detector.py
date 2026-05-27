"""Unit tests for scripts.artifact_detector.

Tests come in two flavors:
1. Targeted unit tests for each signal detector (temporal, comparative,
   KPI, tabular).
2. An accuracy sweep over scripts/tests/fixtures/labeled_examples.json
   with a ≥85% accuracy gate.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from artifact_detector import detect_artifact  # noqa: E402


FIXTURES = ROOT / "scripts" / "tests" / "fixtures" / "labeled_examples.json"


class ArtifactDetectorApiTest(unittest.TestCase):
    def test_detect_artifact_returns_none_for_empty_description(self) -> None:
        self.assertIsNone(detect_artifact(""))

    def test_detect_artifact_returns_str_or_none(self) -> None:
        result = detect_artifact("weekly sales report")
        self.assertIn(result, {"line-chart", "bar-chart", "kpi-cards", "data-table", None})


class TemporalSignalTest(unittest.TestCase):
    def test_monthly_trend_returns_line_chart(self) -> None:
        self.assertEqual(detect_artifact("monthly revenue trend"), "line-chart")

    def test_weekly_over_time_returns_line_chart(self) -> None:
        self.assertEqual(detect_artifact("weekly active users over the last quarter"), "line-chart")

    def test_year_over_year_returns_line_chart(self) -> None:
        self.assertEqual(detect_artifact("year over year revenue growth"), "line-chart")

    def test_hourly_latency_returns_line_chart(self) -> None:
        self.assertEqual(detect_artifact("hourly api latency for the past week"), "line-chart")


class ComparativeSignalTest(unittest.TestCase):
    def test_by_region_returns_bar_chart(self) -> None:
        self.assertEqual(detect_artifact("revenue by region"), "bar-chart")

    def test_by_category_returns_bar_chart(self) -> None:
        self.assertEqual(detect_artifact("sales by product category"), "bar-chart")

    def test_compare_returns_bar_chart(self) -> None:
        self.assertEqual(detect_artifact("compare deployment success rate by environment"), "bar-chart")

    def test_temporal_takes_precedence_over_comparative(self) -> None:
        # "weekly ... by region" is both temporal and comparative.
        # Temporal precedence is intentional (line is more informative for trends).
        self.assertEqual(detect_artifact("weekly sales by region"), "line-chart")


class KpiSignalTest(unittest.TestCase):
    def test_kpi_returns_cards(self) -> None:
        self.assertEqual(detect_artifact("executive KPI dashboard"), "kpi-cards")

    def test_key_metrics_returns_cards(self) -> None:
        self.assertEqual(detect_artifact("key metrics summary for finance team"), "kpi-cards")

    def test_scorecard_returns_cards(self) -> None:
        self.assertEqual(detect_artifact("operational health scorecard"), "kpi-cards")

    def test_north_star_metrics_returns_cards(self) -> None:
        self.assertEqual(detect_artifact("top-level product north star metrics"), "kpi-cards")


class TabularSignalTest(unittest.TestCase):
    def test_listing_returns_data_table(self) -> None:
        self.assertEqual(detect_artifact("outstanding invoices listing"), "data-table")

    def test_inventory_levels_returns_data_table(self) -> None:
        self.assertEqual(detect_artifact("current inventory levels by sku"), "data-table")

    def test_status_table_returns_data_table(self) -> None:
        self.assertEqual(detect_artifact("regulatory filings status grid"), "data-table")

    def test_log_returns_data_table(self) -> None:
        self.assertEqual(detect_artifact("customer escalation log"), "data-table")


class NegativeSignalTest(unittest.TestCase):
    def test_runbook_returns_none(self) -> None:
        self.assertIsNone(detect_artifact("deploy runbook for the payments service"))

    def test_email_returns_none(self) -> None:
        self.assertIsNone(detect_artifact("draft an apology email to a client"))

    def test_translation_returns_none(self) -> None:
        self.assertIsNone(detect_artifact("translate korean technical doc to english"))


class LabeledAccuracyGate(unittest.TestCase):
    ACCURACY_THRESHOLD = 0.85

    def setUp(self) -> None:
        self.examples = json.loads(FIXTURES.read_text())

    def test_accuracy_meets_threshold(self) -> None:
        correct = 0
        misses: list[tuple[str, str | None, str | None]] = []
        for example in self.examples:
            actual = detect_artifact(example["description"])
            if actual == example["expected"]:
                correct += 1
            else:
                misses.append((example["description"], example["expected"], actual))

        accuracy = correct / len(self.examples)
        message = (
            f"Accuracy {accuracy:.2%} below threshold "
            f"{self.ACCURACY_THRESHOLD:.0%}. Misses:\n"
            + "\n".join(f"  - {d!r}: expected={e!r} got={a!r}" for d, e, a in misses)
        )
        self.assertGreaterEqual(accuracy, self.ACCURACY_THRESHOLD, message)


if __name__ == "__main__":
    unittest.main()
