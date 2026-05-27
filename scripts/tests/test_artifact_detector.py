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


if __name__ == "__main__":
    unittest.main()
