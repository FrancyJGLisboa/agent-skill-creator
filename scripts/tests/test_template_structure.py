"""Structural tests for the four artifact JSX templates.

These do not parse JSX (no JSX parser in stdlib). Instead they assert
that each template file exists, contains the substitution marker, and
references the expected library (recharts/shadcn) so an agent wiring
Phase 2 can rely on a stable shape.
"""

import unittest
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent.parent.parent / "references" / "artifact-templates"
SUBSTITUTION_MARKER = "/* AGENT_SKILL_DATA */"


class LineChartTemplateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.path = TEMPLATES_DIR / "line-chart.jsx"

    def test_template_file_exists(self) -> None:
        self.assertTrue(self.path.exists(), f"Missing: {self.path}")

    def test_template_has_substitution_marker(self) -> None:
        content = self.path.read_text()
        self.assertIn(SUBSTITUTION_MARKER, content)

    def test_template_references_recharts(self) -> None:
        content = self.path.read_text()
        self.assertIn("recharts", content)

    def test_template_exports_default_component(self) -> None:
        content = self.path.read_text()
        self.assertIn("export default", content)


class BarChartTemplateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.path = TEMPLATES_DIR / "bar-chart.jsx"

    def test_template_file_exists(self) -> None:
        self.assertTrue(self.path.exists(), f"Missing: {self.path}")

    def test_template_has_substitution_marker(self) -> None:
        self.assertIn(SUBSTITUTION_MARKER, self.path.read_text())

    def test_template_references_recharts(self) -> None:
        self.assertIn("recharts", self.path.read_text())

    def test_template_exports_default_component(self) -> None:
        self.assertIn("export default", self.path.read_text())


class KpiCardsTemplateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.path = TEMPLATES_DIR / "kpi-cards.jsx"

    def test_template_file_exists(self) -> None:
        self.assertTrue(self.path.exists(), f"Missing: {self.path}")

    def test_template_has_substitution_marker(self) -> None:
        self.assertIn(SUBSTITUTION_MARKER, self.path.read_text())

    def test_template_exports_default_component(self) -> None:
        self.assertIn("export default", self.path.read_text())


class DataTableTemplateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.path = TEMPLATES_DIR / "data-table.jsx"

    def test_template_file_exists(self) -> None:
        self.assertTrue(self.path.exists(), f"Missing: {self.path}")

    def test_template_has_substitution_marker(self) -> None:
        self.assertIn(SUBSTITUTION_MARKER, self.path.read_text())

    def test_template_exports_default_component(self) -> None:
        self.assertIn("export default", self.path.read_text())


if __name__ == "__main__":
    unittest.main()
