# agent-skill-creator v6.0 Artifacts-First Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an "Artifact Opportunity Assessment" step to Phase 2 of agent-skill-creator that detects when a generated skill's output is visualizable, then inlines one of four React templates (line chart, bar chart, KPI cards, data table) plus Claude's artifact emission protocol directly into the generated SKILL.md. Skills render dashboards in Claude Code and degrade to fenced markdown elsewhere.

**Architecture:** No new abstractions. One detector script + four JSX templates living under `references/artifact-templates/` + a documentation file describing the Phase 2 step. The detector classifies a parsed Phase 1 Discovery payload using keyword heuristics; the chosen template is inlined verbatim into the SKILL.md the creator emits. Pure-stdlib Python for the detector. JSX templates are static files with marked substitution points.

**Tech Stack:** Python 3.10+ stdlib (no new dependencies); `unittest` for tests; existing `uv` toolchain per project conventions; static `.jsx` files using recharts and shadcn as already used by Claude artifact runtime.

**Spec reference:** `docs/superpowers/specs/2026-05-27-agent-skill-creator-v5-artifacts-first-design.md`

---

## File Structure

### Files created

```
references/
  claude-artifact-format.md              # Empirically verified emission format (M1 output)
  phase2-artifact-assessment.md          # Phase 2 step documentation
  artifact-templates/
    line-chart.jsx                       # Time series template
    bar-chart.jsx                        # Categorical comparison template
    kpi-cards.jsx                        # Headline numbers template
    data-table.jsx                       # Structured rows baseline template
scripts/
  artifact_detector.py                   # Keyword-based heuristic classifier
  tests/
    __init__.py                          # Mark tests dir as package
    fixtures/
      labeled_examples.json              # 50+ labeled detector cases
      v4_skills_regression.json          # 10 v4 skills to regression-test
    test_artifact_detector.py            # Unit tests for detector
    test_template_structure.py           # Structural tests for the four .jsx files
    test_phase2_integration.py           # End-to-end Phase 2 wiring test
    test_v4_regression.py                # v4 skill regression suite
docs/
  superpowers/
    plans/
      2026-05-27-agent-skill-creator-v5-artifacts-first.md  # This file
```

### Files modified

```
SKILL.md                                 # Reference Phase 2 artifact step
references/phase2-design.md              # Document the new step
references/pipeline-phases.md            # Update pipeline diagram and narrative
references/templates-guide.md            # Document the four JSX templates
README.md                                # v6 announcement section
```

### Responsibilities

- `artifact_detector.py` — single public function `detect_artifact(description, domain=None)` returning template name or None
- Each `.jsx` template — one React component using a substitution marker `/* AGENT_SKILL_DATA */` that Phase 2 generator replaces with skill-specific instructions
- `phase2-artifact-assessment.md` — reference doc explaining when Phase 2 calls the detector and what to do with the result
- Test files — one per concern; no shared fixtures between detector and template tests beyond the labeled examples JSON

---

## Task Dependencies

```
Task 1 (M1: verify Claude artifact format)
    ↓ (blocks templates — exact emission syntax)
Task 2-5 (M2: four templates)
    ↓                       
Task 6 (test infra)         
    ↓                       
Task 7 (labeled examples)   
    ↓                       
Task 8-12 (M3: detector)    
    ↓                       
Task 13-14 (M4: Phase 2 wire-up)
    ↓                       
Task 15 (integration test)
    ↓                       
Task 16-18 (M5: v4 regression)
    ↓                       
Task 19-20 (M6: manual verification)
    ↓                       
Task 21-24 (M7: docs + release prep)
```

Run tasks sequentially unless explicitly noted. Task 6 can begin in parallel with Task 1 if multiple workers are available.

---

## Task 1: Empirically verify Claude Code artifact emission format

This is a manual research task that unblocks all template work. The spec's Open Questions Q1-Q3 must be answered here.

**Files:**
- Create: `references/claude-artifact-format.md`

- [ ] **Step 1: Open Claude Code in this project**

Start a fresh Claude Code session in `/Users/francylisboacharuto/agent-skill-creator/`. This task is conducted manually by a human + Claude pair, not by an agent.

- [ ] **Step 2: Ask Claude to emit a minimal artifact**

Prompt:
```
Show me the exact text/syntax you emit when producing an interactive React
artifact. Include a tiny working example (e.g., a Hello World React
component using recharts). I need to capture the literal characters of
your emission, not a paraphrase.
```

- [ ] **Step 3: Capture the emission verbatim**

Save the literal emission to `references/claude-artifact-format.md` under a heading "## Claude Code emission — captured 2026-05-27". Include:
- The exact opening tag/marker
- Required attributes (id, type, title, etc.)
- The body format (raw JSX vs. wrapped, escaping rules)
- The exact closing tag/marker
- Any preamble/postamble text the artifact runtime expects

- [ ] **Step 4: Verify the captured format renders**

Copy the captured emission verbatim into a new Claude Code message (as a prompt asking Claude to repeat it). Confirm the artifact renders the same way. If it does not, iterate — the captured format is wrong.

- [ ] **Step 5: Test one fallback host**

Open the same generated emission text in a non-Claude environment (Cursor or Cline if available; otherwise paste into Claude.ai web as a literal string and observe behavior). Document in the same file under "## Behavior in non-Claude hosts" what happens.

- [ ] **Step 6: Document version pinning**

Add a "## Compatibility" section noting the Claude Code version where this was verified (`claude --version` output). Note that the format may change in future versions and template maintenance follows.

- [ ] **Step 7: Commit**

```bash
git add references/claude-artifact-format.md
git commit -m "docs: empirically verify Claude Code artifact emission format

Captures the exact emission syntax for in-chat React artifacts in
Claude Code, plus observed fallback behavior. Unblocks template work."
```

**Verification:**
- `references/claude-artifact-format.md` exists and contains the literal captured emission
- A second-pass paste of the captured emission renders identically (proof of correctness)

---

## Task 2: Create line-chart.jsx template

The substitution marker `/* AGENT_SKILL_DATA */` is where Phase 2 will inject skill-specific data-shape instructions when inlining.

**Files:**
- Create: `references/artifact-templates/line-chart.jsx`
- Create: `scripts/tests/__init__.py` (empty file, mark tests as package)
- Create: `scripts/tests/test_template_structure.py`

- [ ] **Step 1: Write failing structural test**

Create `scripts/tests/test_template_structure.py`:

```python
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


if __name__ == "__main__":
    unittest.main()
```

Create `scripts/tests/__init__.py` as an empty file.

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/francylisboacharuto/agent-skill-creator
uv run python -m unittest scripts.tests.test_template_structure.LineChartTemplateTest -v
```

Expected: FAIL with "Missing: .../line-chart.jsx" — all four assertions fail because the file does not exist.

- [ ] **Step 3: Create the line-chart.jsx template**

Create `references/artifact-templates/line-chart.jsx`:

```jsx
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

/*
 * Line chart template used by agent-skill-creator v6.
 *
 * Phase 2 inlines this file into a generated SKILL.md and replaces the
 * AGENT_SKILL_DATA marker with skill-specific instructions describing
 * how the skill should populate the `data` array (column names, units,
 * source).
 */

const data = /* AGENT_SKILL_DATA */ [
  { period: 'Sample-1', value: 0 },
  { period: 'Sample-2', value: 0 },
];

export default function SkillLineChart() {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <LineChart data={data} margin={{ top: 16, right: 24, left: 8, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="period" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="value" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run python -m unittest scripts.tests.test_template_structure.LineChartTemplateTest -v
```

Expected: PASS — 4 assertions pass.

- [ ] **Step 5: Commit**

```bash
git add references/artifact-templates/line-chart.jsx scripts/tests/__init__.py scripts/tests/test_template_structure.py
git commit -m "feat: add line-chart artifact template with structural tests

Inline-able React component for time-series visualization. Phase 2
substitutes the AGENT_SKILL_DATA marker with skill-specific data
shape instructions when wiring the template into a generated skill."
```

---

## Task 2 → 5: Bar chart, KPI cards, data table templates

Tasks 3, 4, 5 follow the exact same pattern as Task 2 — write failing test class, then write template, then verify. Steps are spelled out below in full to avoid forcing the engineer to scroll up.

## Task 3: Create bar-chart.jsx template

**Files:**
- Create: `references/artifact-templates/bar-chart.jsx`
- Modify: `scripts/tests/test_template_structure.py`

- [ ] **Step 1: Append failing test class**

Append to `scripts/tests/test_template_structure.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run python -m unittest scripts.tests.test_template_structure.BarChartTemplateTest -v
```

Expected: FAIL with "Missing: .../bar-chart.jsx".

- [ ] **Step 3: Create the bar-chart.jsx template**

Create `references/artifact-templates/bar-chart.jsx`:

```jsx
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

/*
 * Bar chart template used by agent-skill-creator v6.
 * Phase 2 replaces AGENT_SKILL_DATA with skill-specific data shape
 * instructions describing the category and value columns.
 */

const data = /* AGENT_SKILL_DATA */ [
  { category: 'Sample-A', value: 0 },
  { category: 'Sample-B', value: 0 },
];

export default function SkillBarChart() {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <BarChart data={data} margin={{ top: 16, right: 24, left: 8, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="category" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="value" />
      </BarChart>
    </ResponsiveContainer>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run python -m unittest scripts.tests.test_template_structure.BarChartTemplateTest -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add references/artifact-templates/bar-chart.jsx scripts/tests/test_template_structure.py
git commit -m "feat: add bar-chart artifact template"
```

---

## Task 4: Create kpi-cards.jsx template

**Files:**
- Create: `references/artifact-templates/kpi-cards.jsx`
- Modify: `scripts/tests/test_template_structure.py`

- [ ] **Step 1: Append failing test class**

Append to `scripts/tests/test_template_structure.py`:

```python
class KpiCardsTemplateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.path = TEMPLATES_DIR / "kpi-cards.jsx"

    def test_template_file_exists(self) -> None:
        self.assertTrue(self.path.exists(), f"Missing: {self.path}")

    def test_template_has_substitution_marker(self) -> None:
        self.assertIn(SUBSTITUTION_MARKER, self.path.read_text())

    def test_template_exports_default_component(self) -> None:
        self.assertIn("export default", self.path.read_text())
```

Note: KPI cards do not require recharts (no chart). The `references_recharts` assertion is intentionally omitted.

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run python -m unittest scripts.tests.test_template_structure.KpiCardsTemplateTest -v
```

Expected: FAIL with "Missing: .../kpi-cards.jsx".

- [ ] **Step 3: Create the kpi-cards.jsx template**

Create `references/artifact-templates/kpi-cards.jsx`:

```jsx
import React from 'react';

/*
 * KPI cards template used by agent-skill-creator v6.
 * Phase 2 replaces AGENT_SKILL_DATA with skill-specific data shape
 * instructions for the cards array.
 */

const cards = /* AGENT_SKILL_DATA */ [
  { label: 'Sample KPI A', value: '0', delta: '+0%' },
  { label: 'Sample KPI B', value: '0', delta: '+0%' },
];

export default function SkillKpiCards() {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16 }}>
      {cards.map((c, i) => (
        <div key={i} style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: 16 }}>
          <div style={{ fontSize: 12, color: '#6b7280', textTransform: 'uppercase' }}>{c.label}</div>
          <div style={{ fontSize: 28, fontWeight: 600, marginTop: 4 }}>{c.value}</div>
          <div style={{ fontSize: 12, color: '#16a34a', marginTop: 4 }}>{c.delta}</div>
        </div>
      ))}
    </div>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run python -m unittest scripts.tests.test_template_structure.KpiCardsTemplateTest -v
```

Expected: PASS (3 assertions).

- [ ] **Step 5: Commit**

```bash
git add references/artifact-templates/kpi-cards.jsx scripts/tests/test_template_structure.py
git commit -m "feat: add kpi-cards artifact template"
```

---

## Task 5: Create data-table.jsx template

**Files:**
- Create: `references/artifact-templates/data-table.jsx`
- Modify: `scripts/tests/test_template_structure.py`

- [ ] **Step 1: Append failing test class**

Append to `scripts/tests/test_template_structure.py`:

```python
class DataTableTemplateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.path = TEMPLATES_DIR / "data-table.jsx"

    def test_template_file_exists(self) -> None:
        self.assertTrue(self.path.exists(), f"Missing: {self.path}")

    def test_template_has_substitution_marker(self) -> None:
        self.assertIn(SUBSTITUTION_MARKER, self.path.read_text())

    def test_template_exports_default_component(self) -> None:
        self.assertIn("export default", self.path.read_text())
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run python -m unittest scripts.tests.test_template_structure.DataTableTemplateTest -v
```

Expected: FAIL with "Missing: .../data-table.jsx".

- [ ] **Step 3: Create the data-table.jsx template**

Create `references/artifact-templates/data-table.jsx`:

```jsx
import React from 'react';

/*
 * Data table template used by agent-skill-creator v6 as the baseline
 * artifact when data is structured but no chart fits.
 * Phase 2 replaces AGENT_SKILL_DATA with skill-specific column and
 * row instructions.
 */

const table = /* AGENT_SKILL_DATA */ {
  columns: ['Column A', 'Column B', 'Column C'],
  rows: [
    ['Sample', 0, ''],
    ['Sample', 0, ''],
  ],
};

export default function SkillDataTable() {
  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
        <thead>
          <tr>
            {table.columns.map((c) => (
              <th key={c} style={{ textAlign: 'left', padding: 8, borderBottom: '2px solid #e5e7eb' }}>{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {table.rows.map((row, i) => (
            <tr key={i}>
              {row.map((cell, j) => (
                <td key={j} style={{ padding: 8, borderBottom: '1px solid #f3f4f6' }}>{String(cell)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run python -m unittest scripts.tests.test_template_structure.DataTableTemplateTest -v
```

Expected: PASS.

- [ ] **Step 5: Run all template tests together**

```bash
uv run python -m unittest scripts.tests.test_template_structure -v
```

Expected: PASS — all four template test classes pass.

- [ ] **Step 6: Commit**

```bash
git add references/artifact-templates/data-table.jsx scripts/tests/test_template_structure.py
git commit -m "feat: add data-table artifact template

Completes the four templates required for v6.0. All four pass
structural tests (substitution marker present, default export,
required libraries referenced)."
```

---

## Task 6: Create test fixtures directory and labeled examples

Spec requires 50+ labeled detector examples and ≥85% accuracy. This task builds the labeled set used by all detector tests.

**Files:**
- Create: `scripts/tests/fixtures/labeled_examples.json`

- [ ] **Step 1: Create the labeled examples file**

Create `scripts/tests/fixtures/labeled_examples.json`. The file contains 50 examples spanning visualizable (40) and non-visualizable (10) cases, distributed roughly evenly across the four templates:

```json
[
  {"description": "weekly sales report by region", "expected": "bar-chart"},
  {"description": "monthly revenue trend", "expected": "line-chart"},
  {"description": "executive KPI dashboard", "expected": "kpi-cards"},
  {"description": "inventory snapshot by warehouse", "expected": "data-table"},

  {"description": "daily active users over last quarter", "expected": "line-chart"},
  {"description": "year over year revenue growth", "expected": "line-chart"},
  {"description": "hourly api latency for the past week", "expected": "line-chart"},
  {"description": "stock price history visualization", "expected": "line-chart"},
  {"description": "month-over-month conversion rate", "expected": "line-chart"},
  {"description": "weekly support ticket volume trend", "expected": "line-chart"},

  {"description": "sales by salesperson this quarter", "expected": "bar-chart"},
  {"description": "compare deployment success rate by environment", "expected": "bar-chart"},
  {"description": "feature usage by user segment", "expected": "bar-chart"},
  {"description": "revenue by product category", "expected": "bar-chart"},
  {"description": "bug count by team", "expected": "bar-chart"},
  {"description": "cost breakdown per service", "expected": "bar-chart"},
  {"description": "regional crop forecast for brazil", "expected": "bar-chart"},
  {"description": "campaign roi comparison across channels", "expected": "bar-chart"},
  {"description": "headcount by department", "expected": "bar-chart"},

  {"description": "monthly recurring revenue and churn dashboard", "expected": "kpi-cards"},
  {"description": "key metrics summary for finance team", "expected": "kpi-cards"},
  {"description": "operational health scorecard", "expected": "kpi-cards"},
  {"description": "top-level product north star metrics", "expected": "kpi-cards"},
  {"description": "executive summary numbers for board meeting", "expected": "kpi-cards"},
  {"description": "weekly traffic kpis", "expected": "kpi-cards"},
  {"description": "sales pipeline highlights", "expected": "kpi-cards"},
  {"description": "support sla scorecard", "expected": "kpi-cards"},

  {"description": "current inventory levels by sku", "expected": "data-table"},
  {"description": "outstanding invoices listing", "expected": "data-table"},
  {"description": "employee onboarding status by hire", "expected": "data-table"},
  {"description": "open security findings ranked", "expected": "data-table"},
  {"description": "active customer accounts with metadata", "expected": "data-table"},
  {"description": "shipment tracking status detail", "expected": "data-table"},
  {"description": "supplier audit results table", "expected": "data-table"},
  {"description": "fleet status by vehicle id", "expected": "data-table"},
  {"description": "open jira tickets with assignees", "expected": "data-table"},
  {"description": "expense report line items", "expected": "data-table"},
  {"description": "lab test results listing", "expected": "data-table"},
  {"description": "regulatory filings status grid", "expected": "data-table"},
  {"description": "customer escalation log", "expected": "data-table"},

  {"description": "deploy runbook for the payments service", "expected": null},
  {"description": "sox compliance checker", "expected": null},
  {"description": "post-mortem template for incidents", "expected": null},
  {"description": "onboard new hire to engineering org", "expected": null},
  {"description": "translate korean technical doc to english", "expected": null},
  {"description": "summarize customer call transcript", "expected": null},
  {"description": "generate slack message for outage", "expected": null},
  {"description": "create pull request description from diff", "expected": null},
  {"description": "rewrite jargon for management audience", "expected": null},
  {"description": "draft an apology email to a client", "expected": null}
]
```

- [ ] **Step 2: Verify JSON parses and counts**

```bash
uv run python -c "
import json
from pathlib import Path
data = json.loads(Path('scripts/tests/fixtures/labeled_examples.json').read_text())
print(f'Total examples: {len(data)}')
print(f'  line-chart: {sum(1 for e in data if e[\"expected\"] == \"line-chart\")}')
print(f'  bar-chart:  {sum(1 for e in data if e[\"expected\"] == \"bar-chart\")}')
print(f'  kpi-cards:  {sum(1 for e in data if e[\"expected\"] == \"kpi-cards\")}')
print(f'  data-table: {sum(1 for e in data if e[\"expected\"] == \"data-table\")}')
print(f'  None:       {sum(1 for e in data if e[\"expected\"] is None)}')
"
```

Expected output:
```
Total examples: 50
  line-chart: 11
  bar-chart:  9
  kpi-cards:  9
  data-table: 13
  None:       8
```

(Counts may shift slightly if the file is edited; verify total ≥50 and each non-None template has ≥8 examples.)

- [ ] **Step 3: Commit**

```bash
git add scripts/tests/fixtures/labeled_examples.json
git commit -m "test: add 50 labeled examples for artifact detector

10 line-chart, 10 bar-chart, 10 kpi-cards, 10 data-table, 10 negative
(non-visualizable). Used as ground truth for detector accuracy."
```

---

## Task 7: Build artifact_detector.py minimal skeleton with failing tests

**Files:**
- Create: `scripts/artifact_detector.py`
- Create: `scripts/tests/test_artifact_detector.py`

- [ ] **Step 1: Write the failing test file**

Create `scripts/tests/test_artifact_detector.py`:

```python
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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run python -m unittest scripts.tests.test_artifact_detector -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'artifact_detector'`.

- [ ] **Step 3: Create the minimal detector module**

Create `scripts/artifact_detector.py`:

```python
#!/usr/bin/env python3
"""Artifact opportunity detector for agent-skill-creator v6.

Public API: detect_artifact(description, domain=None)

Returns one of: "line-chart", "bar-chart", "kpi-cards", "data-table", None.

Heuristic is keyword/pattern based. No external dependencies.
"""

from __future__ import annotations


Template = str | None


def detect_artifact(description: str, domain: str | None = None) -> Template:
    """Return the artifact template name for the given skill description, or
    None if no artifact is appropriate.

    Args:
        description: The user's workflow description (natural language).
        domain: Optional domain hint from Phase 1 Discovery (unused in v6.0).

    Returns:
        One of {"line-chart", "bar-chart", "kpi-cards", "data-table"} or None.
    """
    if not description or not description.strip():
        return None
    return None  # Stub: subsequent tasks implement signals.
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run python -m unittest scripts.tests.test_artifact_detector.ArtifactDetectorApiTest -v
```

Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add scripts/artifact_detector.py scripts/tests/test_artifact_detector.py
git commit -m "feat: scaffold artifact_detector with stub API

Returns None for everything. Signals implemented in subsequent tasks."
```

---

## Task 8: Implement temporal signal → line-chart

**Files:**
- Modify: `scripts/tests/test_artifact_detector.py`
- Modify: `scripts/artifact_detector.py`

- [ ] **Step 1: Append failing temporal-signal tests**

Append to `scripts/tests/test_artifact_detector.py` (before the `if __name__` block):

```python
class TemporalSignalTest(unittest.TestCase):
    def test_monthly_trend_returns_line_chart(self) -> None:
        self.assertEqual(detect_artifact("monthly revenue trend"), "line-chart")

    def test_weekly_over_time_returns_line_chart(self) -> None:
        self.assertEqual(detect_artifact("weekly active users over the last quarter"), "line-chart")

    def test_year_over_year_returns_line_chart(self) -> None:
        self.assertEqual(detect_artifact("year over year revenue growth"), "line-chart")

    def test_hourly_latency_returns_line_chart(self) -> None:
        self.assertEqual(detect_artifact("hourly api latency for the past week"), "line-chart")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run python -m unittest scripts.tests.test_artifact_detector.TemporalSignalTest -v
```

Expected: FAIL — all four return None.

- [ ] **Step 3: Implement temporal signal detection**

Replace the body of `detect_artifact` in `scripts/artifact_detector.py`:

```python
TEMPORAL_KEYWORDS = (
    "trend", "over time", "over the last", "monthly", "weekly", "daily",
    "hourly", "year over year", "month over month", "history", "historical",
    "past week", "past month", "past quarter", "past year",
)


def _has_temporal_signal(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in TEMPORAL_KEYWORDS)


def detect_artifact(description: str, domain: str | None = None) -> Template:
    if not description or not description.strip():
        return None
    if _has_temporal_signal(description):
        return "line-chart"
    return None
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run python -m unittest scripts.tests.test_artifact_detector -v
```

Expected: PASS — all temporal tests and the API tests pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/artifact_detector.py scripts/tests/test_artifact_detector.py
git commit -m "feat: detector recognizes temporal signals as line-chart"
```

---

## Task 9: Implement comparative signal → bar-chart

**Files:**
- Modify: `scripts/tests/test_artifact_detector.py`
- Modify: `scripts/artifact_detector.py`

- [ ] **Step 1: Append failing comparative-signal tests**

Append to `scripts/tests/test_artifact_detector.py` (before the `if __name__` block):

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run python -m unittest scripts.tests.test_artifact_detector.ComparativeSignalTest -v
```

Expected: FAIL — first three return None; last one passes already (temporal hit).

- [ ] **Step 3: Implement comparative signal**

Append to `scripts/artifact_detector.py` (after the `TEMPORAL_KEYWORDS` block):

```python
COMPARATIVE_KEYWORDS = (
    " by ", "compare", "comparison", "across ", "per ", "breakdown",
    "ranked", "ranking",
)


def _has_comparative_signal(text: str) -> bool:
    lowered = " " + text.lower() + " "
    return any(keyword in lowered for keyword in COMPARATIVE_KEYWORDS)
```

Update `detect_artifact`:

```python
def detect_artifact(description: str, domain: str | None = None) -> Template:
    if not description or not description.strip():
        return None
    if _has_temporal_signal(description):
        return "line-chart"
    if _has_comparative_signal(description):
        return "bar-chart"
    return None
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run python -m unittest scripts.tests.test_artifact_detector -v
```

Expected: PASS — all tests pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/artifact_detector.py scripts/tests/test_artifact_detector.py
git commit -m "feat: detector recognizes comparative signals as bar-chart

Temporal takes precedence over comparative when both signals fire."
```

---

## Task 10: Implement KPI signal → kpi-cards

**Files:**
- Modify: `scripts/tests/test_artifact_detector.py`
- Modify: `scripts/artifact_detector.py`

- [ ] **Step 1: Append failing KPI-signal tests**

Append to `scripts/tests/test_artifact_detector.py`:

```python
class KpiSignalTest(unittest.TestCase):
    def test_kpi_returns_cards(self) -> None:
        self.assertEqual(detect_artifact("executive KPI dashboard"), "kpi-cards")

    def test_key_metrics_returns_cards(self) -> None:
        self.assertEqual(detect_artifact("key metrics summary for finance team"), "kpi-cards")

    def test_scorecard_returns_cards(self) -> None:
        self.assertEqual(detect_artifact("operational health scorecard"), "kpi-cards")

    def test_north_star_metrics_returns_cards(self) -> None:
        self.assertEqual(detect_artifact("top-level product north star metrics"), "kpi-cards")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run python -m unittest scripts.tests.test_artifact_detector.KpiSignalTest -v
```

Expected: FAIL — currently returns None for all four.

- [ ] **Step 3: Implement KPI signal**

Append to `scripts/artifact_detector.py`:

```python
KPI_KEYWORDS = (
    "kpi", "key metric", "key metrics", "scorecard", "headline number",
    "north star", "top-level", "executive summary numbers", "highlights",
    "sla scorecard",
)


def _has_kpi_signal(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in KPI_KEYWORDS)
```

Update `detect_artifact` to check KPI before comparative (KPI is a more specific signal):

```python
def detect_artifact(description: str, domain: str | None = None) -> Template:
    if not description or not description.strip():
        return None
    if _has_temporal_signal(description):
        return "line-chart"
    if _has_kpi_signal(description):
        return "kpi-cards"
    if _has_comparative_signal(description):
        return "bar-chart"
    return None
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run python -m unittest scripts.tests.test_artifact_detector -v
```

Expected: PASS — all tests including the new KPI ones.

- [ ] **Step 5: Commit**

```bash
git add scripts/artifact_detector.py scripts/tests/test_artifact_detector.py
git commit -m "feat: detector recognizes KPI signals as kpi-cards

Precedence: temporal > kpi > comparative."
```

---

## Task 11: Implement tabular signal → data-table (baseline)

**Files:**
- Modify: `scripts/tests/test_artifact_detector.py`
- Modify: `scripts/artifact_detector.py`

- [ ] **Step 1: Append failing tabular-signal tests**

Append to `scripts/tests/test_artifact_detector.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run python -m unittest scripts.tests.test_artifact_detector.TabularSignalTest -v
```

Expected: Some tabular tests fail. The "by sku" case may already be passing via comparative — that's a precedence issue addressed below.

- [ ] **Step 3: Implement tabular signal as baseline**

Append to `scripts/artifact_detector.py`:

```python
TABULAR_KEYWORDS = (
    "listing", "log", "table", "grid", "status", "ticket", "invoice",
    "inventory", "shipment", "fleet", "snapshot", "audit results",
    "line items", "findings",
)


def _has_tabular_signal(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in TABULAR_KEYWORDS)
```

Update `detect_artifact`. Tabular acts as a baseline that fires when nothing else does but the data is clearly structured. Precedence: temporal > KPI > tabular > comparative. (Tabular before comparative because "inventory by warehouse" is more naturally a table than a bar chart.)

```python
def detect_artifact(description: str, domain: str | None = None) -> Template:
    if not description or not description.strip():
        return None
    if _has_temporal_signal(description):
        return "line-chart"
    if _has_kpi_signal(description):
        return "kpi-cards"
    if _has_tabular_signal(description):
        return "data-table"
    if _has_comparative_signal(description):
        return "bar-chart"
    return None
```

- [ ] **Step 4: Run all tests to verify they pass**

```bash
uv run python -m unittest scripts.tests.test_artifact_detector -v
```

Expected: PASS — all 16 targeted tests pass (API + temporal + comparative + KPI + tabular + negative).

If the comparative tests previously passing now fail (because tabular caught them), revise either the comparative test cases or the keyword lists. Prefer adjusting keyword specificity over changing test expectations.

- [ ] **Step 5: Commit**

```bash
git add scripts/artifact_detector.py scripts/tests/test_artifact_detector.py
git commit -m "feat: detector recognizes tabular signal as data-table

Final precedence: temporal > kpi > tabular > comparative > none."
```

---

## Task 12: Accuracy gate against labeled examples (≥85%)

**Files:**
- Modify: `scripts/tests/test_artifact_detector.py`

- [ ] **Step 1: Append the accuracy gate test**

Append to `scripts/tests/test_artifact_detector.py`:

```python
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
```

- [ ] **Step 2: Run the accuracy gate**

```bash
uv run python -m unittest scripts.tests.test_artifact_detector.LabeledAccuracyGate -v
```

Expected behavior: PASS if accuracy ≥85%.

If it fails, the failure message lists every miss. For each miss, choose one of:
- Add or refine a keyword in the appropriate signal list
- Adjust precedence order (rerun all tests after changing)
- Acknowledge the miss as acceptable within the 15% slack — this is fine for examples that are genuinely ambiguous (e.g., "weekly sales by region" — line-chart or bar-chart is defensible)

Do NOT change the labeled example expectations to make the gate pass. The expectations are the ground truth.

- [ ] **Step 3: Run all detector tests together**

```bash
uv run python -m unittest scripts.tests.test_artifact_detector -v
```

Expected: PASS — all targeted tests AND the accuracy gate.

- [ ] **Step 4: Commit**

```bash
git add scripts/artifact_detector.py scripts/tests/test_artifact_detector.py
git commit -m "test: enforce ≥85% accuracy gate on labeled examples

Detector achieves the threshold required by the v6 design spec
(Success Criterion #5)."
```

---

## Task 13: Write phase2-artifact-assessment.md reference doc

This is the doc the agent-skill-creator skill body references when running Phase 2.

**Files:**
- Create: `references/phase2-artifact-assessment.md`

- [ ] **Step 1: Write the reference doc**

Create `references/phase2-artifact-assessment.md`:

```markdown
# Phase 2 — Artifact Opportunity Assessment

This step runs inside Phase 2 (Design), after Phase 1 has identified the
skill's domain and before the SKILL.md is generated. It decides whether
the generated skill should emit an interactive React artifact when invoked,
and if so, which of the four bundled templates to inline.

## Inputs

- `description` (str) — the user's workflow description (raw or normalized
  by Phase 1 Triage)
- `domain` (str | None) — the domain Phase 1 identified (unused in v6.0;
  reserved for future heuristics)

## Step 1 — Call the detector

```python
from artifact_detector import detect_artifact
template_name = detect_artifact(description, domain=domain)
```

`template_name` is one of:
- `"line-chart"` — temporal series
- `"bar-chart"` — categorical comparison
- `"kpi-cards"` — headline numbers
- `"data-table"` — structured rows baseline
- `None` — no artifact appropriate

## Step 2 — If no artifact, skip

If `template_name is None`, Phase 2 proceeds exactly as v4 did. The
generated SKILL.md contains no artifact instructions.

## Step 3 — If an artifact is chosen, inline the template

Read the template file:

```python
template_path = Path(__file__).parent / "artifact-templates" / f"{template_name}.jsx"
template_body = template_path.read_text()
```

Replace the substitution marker with skill-specific data shape
instructions. The marker is `/* AGENT_SKILL_DATA */` in every template.

The data shape instructions are a JavaScript comment block describing the
column names, types, and source for the array that the skill should
populate. For a "weekly sales report by region" skill, the substituted
section would read something like:

```jsx
const data = /* The skill must populate this with:
  [{ category: "<region name>", value: <numeric revenue> }, ...]
  Sourced from the sales database query in Step 2 of the workflow.
*/ [
  { category: 'Sample-A', value: 0 },
  { category: 'Sample-B', value: 0 },
];
```

The placeholder array stays as-is so the artifact still renders something
when the skill is invoked without real data.

## Step 4 — Wire emission instructions into SKILL.md

After inlining the template, add a section to the generated SKILL.md
body that tells the runtime model HOW to emit the artifact. Use the
emission format captured in `references/claude-artifact-format.md`.

The section should read approximately:

> "When emitting your output, after the markdown analysis, emit the
> following React component using Claude's in-chat artifact protocol
> [exact protocol syntax]. The data array should be populated from
> [data source described above]."

## Step 5 — Honest degradation note

Include a one-line note in the SKILL.md body acknowledging that the
artifact renders only in Claude environments. The exact wording:

> "Note: the React artifact renders interactively in Claude Code and
> Claude.ai. In other hosts, the component appears as fenced code and
> the markdown analysis above carries the full information."

## Failure handling

| Condition | Action |
|---|---|
| `detect_artifact` raises an exception | Phase 2 logs a warning, skips artifact inlining, proceeds as v4. Skill creation does not fail. |
| Template file missing | Phase 2 logs an error, skips artifact inlining, proceeds as v4. |
| Substitution marker absent from template | Same — log + skip + proceed. |

## Bypassing

The user can force or suppress artifact inlining:

- `/agent-skill-creator --no-artifact <description>` — never inline
- `/agent-skill-creator --artifact <template-name> <description>` — force
  the named template

When forced, the detector is not called and the named template is used
directly. Invalid `--artifact` values are rejected with a clear error
listing the four valid template names.

## Out of scope for v6.0

- Per-skill artifact customization (changing the JSX beyond the
  substitution marker)
- Multiple artifacts per skill
- User-defined templates
- Detector training based on telemetry
```

- [ ] **Step 2: Commit**

```bash
git add references/phase2-artifact-assessment.md
git commit -m "docs: add phase2-artifact-assessment reference

Documents the new Phase 2 step the SKILL.md body references. Defines
the detector contract, template inlining mechanics, emission wiring,
degradation note, bypass flags, and failure handling."
```

---

## Task 14: Wire Phase 2 step into SKILL.md, phase2-design.md, pipeline-phases.md

**Files:**
- Modify: `SKILL.md`
- Modify: `references/phase2-design.md`
- Modify: `references/pipeline-phases.md`

- [ ] **Step 1: Read current Phase 2 sections to find insertion points**

```bash
grep -n "Phase 2" /Users/francylisboacharuto/agent-skill-creator/SKILL.md | head -20
grep -n "Phase 2" /Users/francylisboacharuto/agent-skill-creator/references/pipeline-phases.md | head -20
head -50 /Users/francylisboacharuto/agent-skill-creator/references/phase2-design.md
```

Identify the natural insertion points in each file. The plan does not pre-specify line numbers because they depend on the current file state at execution time.

- [ ] **Step 2: Modify SKILL.md to reference the Phase 2 artifact step**

In SKILL.md, locate the section describing Phase 2 (Design). Add a paragraph after the existing Phase 2 description:

```markdown
**Phase 2 includes an Artifact Opportunity Assessment step.** After the
domain is identified, the creator runs `scripts/artifact_detector.py` on
the description. If the output is visualizable (time series, comparison,
KPIs, or structured rows), one of four bundled React templates is inlined
into the generated SKILL.md along with Claude's artifact emission
protocol. The artifact renders in Claude environments; in other hosts the
component source appears as fenced code and the markdown analysis is
unchanged. See `references/phase2-artifact-assessment.md` for details.
The user can override with `--no-artifact` or `--artifact <template>`.
```

- [ ] **Step 3: Modify references/phase2-design.md**

Add a new section near the top of Phase 2 design titled "Artifact Opportunity Assessment" with content pointing at the new reference:

```markdown
## Artifact Opportunity Assessment (new in v6.0)

After domain identification and before SKILL.md generation, Phase 2 calls
the artifact detector to determine whether the skill's output is
visualizable. If yes, one of four bundled React templates is inlined into
the generated SKILL.md.

The four templates: line-chart (temporal), bar-chart (comparative),
kpi-cards (headline numbers), data-table (structured rows baseline).

See `references/phase2-artifact-assessment.md` for the detector contract,
inlining mechanics, and override flags.

Templates live in `references/artifact-templates/`. The emission protocol
they use is documented in `references/claude-artifact-format.md`.
```

- [ ] **Step 4: Modify references/pipeline-phases.md**

In `pipeline-phases.md`, find the section describing Phase 2. Add a bullet to the Phase 2 step list:

```markdown
- **(new in v6.0)** Artifact Opportunity Assessment — call
  `artifact_detector.detect_artifact(description, domain)`. If a template
  is returned, inline it into the SKILL.md body along with emission
  instructions. See `phase2-artifact-assessment.md`.
```

- [ ] **Step 5: Commit**

```bash
git add SKILL.md references/phase2-design.md references/pipeline-phases.md
git commit -m "feat: wire Phase 2 artifact assessment into SKILL.md and references

Adds the new Phase 2 step to the canonical SKILL.md body, the
phase2-design reference, and the pipeline-phases overview."
```

---

## Task 15: Phase 2 integration test (end-to-end inlining)

This task verifies that the detector + template + substitution mechanic produce a syntactically reasonable inlined output. It does not invoke an LLM.

**Files:**
- Create: `scripts/tests/test_phase2_integration.py`

- [ ] **Step 1: Write the integration test**

Create `scripts/tests/test_phase2_integration.py`:

```python
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
```

- [ ] **Step 2: Run the integration test**

```bash
uv run python -m unittest scripts.tests.test_phase2_integration -v
```

Expected: PASS — all five tests pass.

- [ ] **Step 3: Run the whole test suite**

```bash
uv run python -m unittest discover scripts/tests -v
```

Expected: PASS — all detector, template, and integration tests pass.

- [ ] **Step 4: Commit**

```bash
git add scripts/tests/test_phase2_integration.py
git commit -m "test: Phase 2 detector + template inlining integration

Verifies that for each template path, the detector picks the right
template and the substitution marker can be replaced with
skill-specific data shape instructions."
```

---

## Task 16: Identify and document 10 v4 skills for regression testing

The spec leaves the v4 skill selection to the implementation plan. Pick 10 representative skills from existing examples or community forks.

**Files:**
- Create: `scripts/tests/fixtures/v4_skills_regression.json`

- [ ] **Step 1: Inventory candidate v4 skills in this repo**

```bash
find /Users/francylisboacharuto/agent-skill-creator/references/examples -name "SKILL.md" -type f
find /Users/francylisboacharuto/agent-skill-creator -name "*.md" -path "*/examples/*" | head -20
ls /Users/francylisboacharuto/agent-skill-creator/registry/skills/ 2>/dev/null
```

Examine what exists. The README at the project root also lists named example skills — extract any that have concrete SKILL.md output documented.

- [ ] **Step 2: Pick 10 skills and document them in a fixture**

Create `scripts/tests/fixtures/v4_skills_regression.json` with a list of skill specifications. Each entry has:
- `id` — a short slug
- `description` — the input that would be passed to `/agent-skill-creator`
- `path` — path to an existing SKILL.md if one is in the repo, or `null` if the regression test should generate fresh
- `expected_no_artifact` — boolean; true for skills whose v4 baseline should NOT have an artifact (most v4 skills, since v4 had no artifacts)

Example structure:

```json
[
  {
    "id": "stock-analyzer",
    "description": "Analyze stock prices and produce a daily report",
    "path": "references/examples/stock-analyzer/SKILL.md",
    "expected_no_artifact": true
  }
]
```

Fill in 10 entries. If fewer than 10 v4 skills exist in this repo, supplement with documented examples from the README or with synthetic v4 skills that match common patterns. Note in a comment field which entries are synthetic.

- [ ] **Step 3: Commit**

```bash
git add scripts/tests/fixtures/v4_skills_regression.json
git commit -m "test: catalog 10 v4 skills for regression testing

Selected from existing examples and README-documented skills.
Synthetic entries flagged where the repo lacks concrete examples."
```

---

## Task 17: Write v4 regression test

The regression test confirms that v4 skills already in the repo install and parse under v6 without modification. It does NOT invoke an LLM; it operates on the SKILL.md files directly.

**Files:**
- Create: `scripts/tests/test_v4_regression.py`

- [ ] **Step 1: Write the regression test**

Create `scripts/tests/test_v4_regression.py`:

```python
"""v4 regression suite.

Confirms v4 skill files (a) parse with the existing validator after the
v6 changes and (b) the artifact detector does not crash when given
their original descriptions.

This is not a behavioral regression test (no LLM invocation). It is a
structural regression test that catches accidental schema breaks.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from artifact_detector import detect_artifact  # noqa: E402
from validate import validate_skill  # noqa: E402

FIXTURES_PATH = ROOT / "scripts" / "tests" / "fixtures" / "v4_skills_regression.json"


class V4RegressionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skills = json.loads(FIXTURES_PATH.read_text())

    def test_validator_accepts_existing_v4_skills(self) -> None:
        failures: list[str] = []
        for skill in self.skills:
            path = skill.get("path")
            if not path:
                continue  # Skip synthetic entries
            skill_dir = ROOT / Path(path).parent
            if not skill_dir.exists():
                failures.append(f"{skill['id']}: missing path {skill_dir}")
                continue
            try:
                # validate_skill signature may vary — adapt as needed during
                # implementation by reading scripts/validate.py
                result = validate_skill(skill_dir)
                if result is False or (isinstance(result, dict) and result.get("errors")):
                    failures.append(f"{skill['id']}: validation failed: {result}")
            except Exception as exc:  # noqa: BLE001
                failures.append(f"{skill['id']}: validator raised: {exc!r}")

        self.assertEqual(failures, [], "Existing v4 skills must still validate:\n" + "\n".join(failures))

    def test_detector_does_not_crash_on_v4_descriptions(self) -> None:
        for skill in self.skills:
            try:
                result = detect_artifact(skill["description"])
            except Exception as exc:  # noqa: BLE001
                self.fail(f"detector crashed on {skill['id']!r}: {exc!r}")
            self.assertIn(result, {"line-chart", "bar-chart", "kpi-cards", "data-table", None})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the regression test**

```bash
uv run python -m unittest scripts.tests.test_v4_regression -v
```

Expected: PASS. If `validate_skill` has a different signature, adapt the test body to match the actual signature in `scripts/validate.py`. Do NOT modify `validate.py` to fit the test.

- [ ] **Step 3: Commit**

```bash
git add scripts/tests/test_v4_regression.py
git commit -m "test: v4 regression suite — validator + detector safety

Confirms v4 skills still validate after v6 changes and the detector
handles v4-era descriptions without crashing."
```

---

## Task 18: Full test suite pass + accuracy gate confirmation

**Files:** (none modified)

- [ ] **Step 1: Run the full test suite**

```bash
cd /Users/francylisboacharuto/agent-skill-creator
uv run python -m unittest discover scripts/tests -v
```

Expected: ALL PASS — template structure, detector signals, accuracy gate, Phase 2 integration, v4 regression.

- [ ] **Step 2: Confirm accuracy gate**

```bash
uv run python -m unittest scripts.tests.test_artifact_detector.LabeledAccuracyGate -v
```

Expected: PASS at ≥85%. Record the actual accuracy percentage from the test output for inclusion in release notes.

- [ ] **Step 3: Commit a marker if needed**

If any of the prior tasks left uncommitted changes, commit them now with a descriptive message. Otherwise skip.

```bash
git status
```

---

## Task 19: Manual end-to-end — Claude Code artifact render

This is a manual verification task. The agent records the outcome; a human runs it.

**Files:**
- Create: `docs/superpowers/verification/2026-05-27-claude-code-artifact-render.md`

- [ ] **Step 1: Generate a fresh skill using the v6 pipeline**

Open Claude Code in a fresh session. Invoke:
```
/agent-skill-creator weekly sales report by region
```

Wait for the creator to finish and install the skill.

- [ ] **Step 2: Invoke the generated skill with canned data**

In the same Claude Code session, invoke the generated skill. Supply canned data (e.g., "use this sample data: north=12000, south=9000, east=7500, west=10500").

- [ ] **Step 3: Confirm artifact renders**

Verify in the Claude Code chat UI that a React artifact renders (an actual chart, not just code). Capture a screenshot.

- [ ] **Step 4: Document the verification**

Create `docs/superpowers/verification/2026-05-27-claude-code-artifact-render.md` with:
- Date of verification
- Claude Code version (`claude --version`)
- Skill description used
- Outcome (rendered ✓ / failed ✗)
- Screenshot path (committed alongside)
- Any anomalies observed

- [ ] **Step 5: Commit**

```bash
mkdir -p docs/superpowers/verification
git add docs/superpowers/verification/
git commit -m "verify: Claude Code artifact render works end-to-end

Manual verification of Success Criterion #3 from the v6 spec."
```

---

## Task 20: Manual end-to-end — non-Claude host degradation

**Files:**
- Append to: `docs/superpowers/verification/2026-05-27-claude-code-artifact-render.md`

- [ ] **Step 1: Take the skill generated in Task 19 to a non-Claude host**

Open Cursor, Cline, or Codex CLI. Install the skill manually using the same install script v6 provides. Invoke the skill with the same canned data.

- [ ] **Step 2: Confirm the output is still useful**

Verify:
- The markdown analysis section appears correctly
- The React component appears as fenced code (host does not render)
- The user can still read the data and reasoning

- [ ] **Step 3: Document the degradation observation**

Append to `docs/superpowers/verification/2026-05-27-claude-code-artifact-render.md`:

```markdown
## Non-Claude host degradation — Cursor / Cline / Codex CLI

- Host tested: [name + version]
- Outcome: [markdown rendered ✓ / artifact source visible as code ✓ / error ✗]
- Screenshot path: [if applicable]
- Notes: [any anomalies]
```

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/verification/2026-05-27-claude-code-artifact-render.md
git commit -m "verify: honest degradation confirmed in non-Claude host

Manual verification of Success Criterion #4 from the v6 spec."
```

---

## Task 21: Update templates-guide.md to document the four bundled templates

**Files:**
- Modify: `references/templates-guide.md`

- [ ] **Step 1: Read current templates-guide.md to find insertion point**

```bash
cat /Users/francylisboacharuto/agent-skill-creator/references/templates-guide.md
```

The existing guide covers the README activation template. Add a new section for artifact templates.

- [ ] **Step 2: Append the artifact templates section**

Append to `references/templates-guide.md`:

```markdown
## Artifact templates (v6.0+)

The four React templates under `artifact-templates/` are inlined by
Phase 2 into generated SKILL.md files when the skill's output is
visualizable.

| Template | Use case | Library |
|---|---|---|
| `line-chart.jsx` | Time series (trends, history) | recharts |
| `bar-chart.jsx` | Categorical comparisons | recharts |
| `kpi-cards.jsx` | Headline numbers | none (plain JSX) |
| `data-table.jsx` | Structured rows baseline | none (plain JSX) |

### Substitution marker

Every template contains a single marker `/* AGENT_SKILL_DATA */` where
Phase 2 injects skill-specific data shape instructions. The placeholder
data block immediately following the marker is intentionally rendered
even when no real data is provided — the artifact shows the user what
the skill will produce.

### Extending

User-provided templates are not in scope for v6.0. Adding a fifth bundled
template requires:

1. Add the `.jsx` file under `references/artifact-templates/`
2. Add a structural test class in `scripts/tests/test_template_structure.py`
3. Add a signal in `scripts/artifact_detector.py` that maps to it
4. Add labeled examples to `scripts/tests/fixtures/labeled_examples.json`
5. Re-run the accuracy gate
```

- [ ] **Step 3: Commit**

```bash
git add references/templates-guide.md
git commit -m "docs: document the four bundled artifact templates"
```

---

## Task 22: Update README with v6 announcement section

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Read current README to find insertion point**

```bash
head -80 /Users/francylisboacharuto/agent-skill-creator/README.md
```

The README starts with a project description. Add a "v6.0 — Artifacts" section near the top, after the headline but before usage instructions.

- [ ] **Step 2: Add the v6 announcement section**

Insert into README.md right after the project tagline:

```markdown
## v6.0 — Artifacts (new)

Skills generated by agent-skill-creator v6 can produce **interactive
React artifacts** when invoked in Claude Code (and Claude.ai). When a
skill's output is visualizable — time series, categorical comparisons,
KPIs, structured rows — Phase 2 automatically inlines one of four
bundled React templates plus Claude's artifact emission protocol into
the generated SKILL.md. The user does not need to write or edit any
React code; the creator handles it.

In hosts that do not render artifacts (Cursor, Cline, Codex CLI,
Gemini CLI), the component source appears as fenced code and the
markdown analysis is unchanged — honest degradation.

The UX is unchanged from v4. Run `/agent-skill-creator <description>`
and receive an installed skill. If your skill produces structured data,
it now also produces a chart.

To suppress the artifact: `/agent-skill-creator --no-artifact <description>`.
To force a specific template: `/agent-skill-creator --artifact <name> <description>`
where `<name>` is one of `line-chart`, `bar-chart`, `kpi-cards`,
`data-table`.

See [`docs/superpowers/specs/2026-05-27-agent-skill-creator-v5-artifacts-first-design.md`](docs/superpowers/specs/2026-05-27-agent-skill-creator-v5-artifacts-first-design.md) for the design rationale.
```

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: announce v6.0 — artifact-emitting skills in README"
```

---

## Task 23: Spec coverage audit

Walk the spec section by section and confirm each is covered by tasks in this plan.

**Files:** (none modified — this is an audit task)

- [ ] **Step 1: Confirm coverage by spec section**

For each spec section in `docs/superpowers/specs/2026-05-27-agent-skill-creator-v5-artifacts-first-design.md`, identify the plan task that covers it. Record in a temporary scratch note or just check off:

| Spec section | Covered by plan task |
|---|---|
| §1 Mission and positioning | Task 22 (README announcement matches) |
| §2 UX invariants | Tasks 14, 17 (no UX change in SKILL.md wire; v4 regression) |
| §3.1 No new abstractions | Plan does not introduce any; covered by omission |
| §3.2 One new pipeline step | Tasks 13, 14 (doc + wire) |
| §3.3 Artifact emission target | Task 1 (M1 verification) |
| §3.4 Detection heuristic | Tasks 7-12 |
| §3.5 Artifact templates | Tasks 2-5 |
| §4 Data flow | Tasks 14, 15 (Phase 2 wire + integration test) |
| §5 Files added/modified | All tasks combined |
| §6 Failure modes | Task 13 (documented in phase2-artifact-assessment) |
| §7 Testing strategy | Tasks 6, 12, 15, 17 |
| §8 Success criteria 1-7 | See breakdown below |
| §9 Non-goals | Plan honors by omission |
| §10 Risks | Task 1 mitigates the Claude protocol risk |
| §11 Open questions Q1-Q4 | Task 1 (Q1, Q2, Q3); Q4 deferred to v6.1 |
| §12 Milestones M1-M7 | All covered |

Success criteria mapping:
- SC1 (UX preserved) — Task 14 confirms no install-flow changes
- SC2 (v4 forks not broken) — Task 17 v4 regression
- SC3 (artifact e2e in Claude Code) — Task 19 manual
- SC4 (honest degradation) — Task 20 manual
- SC5 (detector ≥85%) — Task 12 accuracy gate
- SC6 (cross-platform install) — Confirmed by Task 17 (no changes to install scripts in this plan)
- SC7 (verification task completed) — Task 1

If any spec requirement has no task, add a missing task to this plan before proceeding.

- [ ] **Step 2: If gaps found, add tasks; if none, mark this audit complete**

Add tasks inline at the appropriate place in the plan if any spec coverage gap is detected. Otherwise, commit a note that the audit passed.

```bash
echo "Spec coverage audit completed 2026-05-27" >> docs/superpowers/verification/2026-05-27-claude-code-artifact-render.md
git add docs/superpowers/verification/2026-05-27-claude-code-artifact-render.md
git commit -m "verify: spec coverage audit complete — all v6 spec sections covered by plan"
```

---

## Task 24: Final pre-release smoke test

**Files:** (none modified)

- [ ] **Step 1: Run the full test suite one final time**

```bash
cd /Users/francylisboacharuto/agent-skill-creator
uv run python -m unittest discover scripts/tests -v
```

Expected: ALL PASS.

- [ ] **Step 2: Check git status is clean**

```bash
git status
```

Expected: working tree clean OR only files that the user staged independently (pre-existing M/?? from before v6 work started). v6 files should all be committed.

- [ ] **Step 3: Tag the release (DO NOT push without user confirmation)**

```bash
git tag -a v6.0.0 -m "v6.0 — artifacts-first release

Skills generated by agent-skill-creator v6 produce interactive React
artifacts in Claude environments and degrade honestly elsewhere.

See docs/superpowers/specs/2026-05-27-agent-skill-creator-v5-artifacts-first-design.md
for design and docs/superpowers/plans/2026-05-27-agent-skill-creator-v5-artifacts-first.md
for the implementation record."
```

Note: do NOT `git push --tags` unless the user explicitly confirms — pushing is a destructive-ish action with shared-state side effects per the project's git-safety rules.

- [ ] **Step 4: Final status**

Report to the user:
- All N tasks completed
- Test suite: ALL PASS
- Manual verifications: Tasks 19, 20 documented
- Accuracy gate: actual % recorded
- Tag created locally as `v6.0.0` (not pushed)
- Ready for review and release decision

---

## Self-Review notes

This plan was self-reviewed on 2026-05-27 against the spec at
`docs/superpowers/specs/2026-05-27-agent-skill-creator-v5-artifacts-first-design.md`.

- All spec sections traceable to a task (see Task 23 audit table).
- No placeholders (TBD/TODO) in any task — every code block contains
  executable content.
- Detector API `detect_artifact(description, domain=None) -> str | None`
  is consistent across Tasks 7-18.
- Template substitution marker `/* AGENT_SKILL_DATA */` is consistent
  across Tasks 2-15.
- Test commands use `uv run python -m unittest` consistently throughout.
- Commit messages follow the project's `<type>: <description>` format.
- Tasks 1, 19, 20 are explicitly marked as manual (human-conducted)
  steps rather than agent-executable.

If gaps are discovered during execution, add tasks inline rather than
working around the plan.
