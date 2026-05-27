"""Integration test for the Phase 2 artifact assessment + inlining.

This test does not call an LLM. It validates that, given a workflow
description, the detector picks a template and the template's
substitution marker can be replaced with skill-specific instructions
without leaving placeholder data unrenderable.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from artifact_detector import detect_artifact  # noqa: E402


TEMPLATES_DIR = ROOT / "references" / "artifact-templates"
SUBSTITUTION_MARKER = "/* AGENT_SKILL_DATA */"


class Phase2InliningTest(unittest.TestCase):
    def _inline(self, template_name: str, instructions: str) -> str:
        template_body = (TEMPLATES_DIR / f"{template_name}.jsx").read_text()
        return template_body.replace(SUBSTITUTION_MARKER, f"/* {instructions} */")

    def test_temporal_inlining(self) -> None:
        template_name = detect_artifact("monthly revenue trend")
        self.assertEqual(template_name, "line-chart")
        result = self._inline(template_name, "data shape: [{period, value}]")
        self.assertNotIn(SUBSTITUTION_MARKER, result)
        self.assertIn("data shape: [{period, value}]", result)
        self.assertIn("export default", result)

    def test_comparative_inlining(self) -> None:
        template_name = detect_artifact("revenue by product category")
        self.assertEqual(template_name, "bar-chart")
        result = self._inline(template_name, "data shape: [{category, value}]")
        self.assertNotIn(SUBSTITUTION_MARKER, result)
        self.assertIn("data shape: [{category, value}]", result)

    def test_kpi_inlining(self) -> None:
        template_name = detect_artifact("executive KPI dashboard")
        self.assertEqual(template_name, "kpi-cards")
        result = self._inline(template_name, "cards: [{label, value, delta}]")
        self.assertNotIn(SUBSTITUTION_MARKER, result)
        self.assertIn("cards:", result)

    def test_tabular_inlining(self) -> None:
        template_name = detect_artifact("current inventory levels by sku")
        self.assertEqual(template_name, "data-table")
        result = self._inline(template_name, "columns: [...]; rows: [...]")
        self.assertNotIn(SUBSTITUTION_MARKER, result)

    def test_negative_case_no_inlining(self) -> None:
        template_name = detect_artifact("deploy runbook for the payments service")
        self.assertIsNone(template_name)


if __name__ == "__main__":
    unittest.main()
