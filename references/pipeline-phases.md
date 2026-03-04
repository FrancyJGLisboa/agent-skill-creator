# Pipeline Phases: Complete 5-Phase Skill Creation Reference

**Version:** 4.0
**Purpose:** Consolidated reference for the autonomous 5-phase skill creation pipeline used by agent-skill-creator v4.0.

This document contains the detailed instructions for each phase of skill creation, updated for the Agent Skills Open Standard (SKILL.md-first, no `-cskill` suffix, spec-compliant frontmatter, cross-platform support).

---

## Pipeline Overview

```
Phase 1: DISCOVERY       -> Research APIs, data sources, domain mapping
Phase 2: DESIGN          -> Define use cases, analyses, methodologies
Phase 3: ARCHITECTURE    -> Structure skill directory (standard-compliant)
Phase 4: DETECTION       -> Generate description + keywords for activation
Phase 5: IMPLEMENTATION  -> Create all files, validate, security scan
```

**Key v4.0 principles:**

- SKILL.md is the **primary file**, created first in Phase 5
- Generated names use **kebab-case** (no `-cskill` suffix)
- Name: 1-64 chars, lowercase letters, numbers, hyphens; must match directory
- Description: 1-1024 chars; this IS the activation mechanism
- Generated SKILL.md must be **<500 lines** (move detail to `references/`)
- Frontmatter must include: `name`, `description`, `license`, `metadata` (author, version)
- `install.sh` is generated for cross-platform support
- `marketplace.json` is **NOT** needed for simple skills
- Validation and security scan run at the end of Phase 5

---

# Phase 1: Discovery

## Objective

Research and **DECIDE** autonomously which API or data source to use for the skill being created.

## Detailed Process

### Step 1: Identify Domain

From user input, extract the main domain:

| User Input | Identified Domain |
|---|---|
| "US crop data" | Agriculture (US) |
| "stock market analysis" | Finance / Stock Market |
| "global climate data" | Climate / Meteorology |
| "economic indicators" | Economy / Macro |
| "commodity data" | Trading / Commodities |

### Step 2: Search Available APIs

For the identified domain, use WebSearch to find public APIs:

**Search queries:**
```
"[domain] API free public data"
"[domain] government API documentation"
"best API for [domain] historical data"
"[domain] open data sources"
```

**Example (US agriculture):**
```bash
WebSearch: "US agriculture API free historical data"
WebSearch: "USDA API documentation"
WebSearch: "agricultural statistics API United States"
```

**Typical result:** 5-10 candidate APIs.

### Step 3: Research Documentation

For each candidate API, use WebFetch to load:
- Homepage/overview
- Getting started guide
- API reference
- Rate limits and pricing

**Extract information per API:**

```markdown
## API: [Name]

**URL**: [base URL]
**Docs**: [docs URL]

**Authentication**:
- Type: API key / OAuth / None
- Cost: Free / Paid
- How to obtain: [steps]

**Available Data**:
- Temporal coverage: [from when to when]
- Geographic coverage: [countries, regions]
- Metrics: [list]
- Granularity: [daily, monthly, annual]

**Limitations**:
- Rate limit: [requests per day/hour]
- Max records: [per request]

**Quality**:
- Source: [official government / private]
- Reliability: [high/medium/low]
- Update frequency: [frequency]
- Documentation quality: [excellent/good/poor]

**Ease of Use**:
- Format: JSON / CSV / XML
- SDKs: [Python/R/None]
- Quirks: [any non-obvious behavior]
```

### Step 4: API Capability Inventory

Ensure the skill uses the maximum useful surface of the chosen API.

**Step 4.1: Complete Inventory**

For the chosen API, catalog ALL data types:

```markdown
## Complete Inventory - {API Name}

| Endpoint/Metric | Returns | Granularity | Coverage | Value |
|---|---|---|---|---|
| {metric1} | {description} | {daily/weekly} | {geo} | High |
| {metric2} | {description} | {monthly} | {geo} | High |
| {metric3} | {description} | {annual} | {geo} | Medium |
```

**Step 4.2: Coverage Decision**

- If metric has high value: implement in v1.0
- If API has 5 high-value metrics: implement all 5
- Never leave >50% of API unused without strong justification

**Step 4.3: Document Decision**

In `DECISIONS.md`:

```markdown
## API Coverage Decision

API {name} offers {N} types of metrics.

**Implemented in v1.0 ({X} of {N}):**
- {metric1} - {justification}
- {metric2} - {justification}

**Not implemented ({Y} of {N}):**
- {metricZ} - {why not} (planned for v2.0)

**Coverage:** {X/N * 100}%
```

**Output of this step:** Exact list of all `get_*()` methods to implement.

### Step 5: Compare Options

Create comparison table:

| API | Coverage | Cost | Rate Limit | Quality | Docs | Ease | Score |
|---|---|---|---|---|---|---|---|
| API 1 | 5/5 | Free | 1000/day | Official | 4/5 | 5/5 | 9.2/10 |
| API 2 | 4/5 | $49/mo | Unlimited | Private | 5/5 | 4/5 | 7.8/10 |

**Scoring criteria:**
- Coverage (fit with need): 30% weight
- Cost (prefer free): 20% weight
- Rate limit (sufficient?): 15% weight
- Quality (official > private): 15% weight
- Documentation (facilitates implementation): 10% weight
- Ease of use (format, structure): 10% weight

### Step 6: DECIDE

**Consider user constraints:**
- Mentioned "free"? Eliminate paid options
- Mentioned "10+ years historical data"? Check coverage
- Mentioned "real-time"? Prioritize streaming APIs

**Apply logic:**
1. Eliminate APIs that violate constraints
2. Of remaining, choose highest score
3. If tie, prefer: official > private, better docs, easier to use

**Document the final decision:**

```markdown
## Selected API: [API Name]

**Score**: X.X/10

**Justification**:
- Coverage: [specific details]
- Cost: [free/paid + details]
- Rate limit: [number] requests/day
- Quality: [official/private + reliability]
- Documentation: [quality + examples]

**Alternatives Considered**:
- API X: Score 7.5/10 - Rejected because [reason]
- API Y: Score 6.2/10 - Rejected because [reason]
```

### Step 7: Research Technical Details

After deciding, dive deep into documentation via WebFetch:
- Getting started guide
- Complete API reference
- Authentication guide
- Rate limiting details
- Best practices

**Extract for implementation:**

```markdown
## Technical Details - [API]

### Authentication
- Method: API key in header
- Header: `X-Api-Key: YOUR_KEY`
- Obtaining key: [step-by-step]

### Main Endpoints
- URL, parameters, response format, errors

### Rate Limiting
- Limit, response headers, behavior when exceeded

### Quirks and Gotchas
- Data formatting issues (e.g., values as strings with commas)
- Suppressed data markers
- Any non-obvious behavior

### Performance Tips
- What to cache and for how long
- Pagination
- Parallel requests
```

### Step 8: Document for Later Use

Save everything in `references/api-guide.md` of the skill to be created.

## Phase 1 Checklist

- [ ] Research completed (WebSearch + WebFetch)
- [ ] Minimum 3 APIs compared
- [ ] Decision made with clear justification
- [ ] User constraints respected
- [ ] API capability inventory completed
- [ ] Technical details extracted
- [ ] DECISIONS.md content prepared
- [ ] Ready for analysis design

---

# Phase 2: Design

## Objective

**DEFINE** autonomously which analyses the skill will perform and how.

## Detailed Process

### Step 1: Brainstorm Use Cases

From the workflow described by the user, think of typical questions they will ask.

**Technique:** "If I were this user, what would I ask?"

**Example (US agriculture):**

User said: "download crop data, compare year vs year, make rankings"

Typical questions:
1. "What's the corn production in 2023?"
2. "How's soybean compared to last year?"
3. "Did production grow or fall?"
4. "Does growth come from area or productivity?"
5. "Which states produce most wheat?"
6. "Top 5 soybean producers"
7. "Production trend last 5 years?"
8. "Average US yield"
9. "Compare Midwest vs South"
10. "Production by region"

**Goal:** List 15-20 typical questions.

### Step 2: Group by Analysis Type

Group similar questions:

**Group 1: Simple Queries** (fetching + formatting)
- Required analysis: **Data Retrieval**
- Complexity: Low

**Group 2: Temporal Comparisons** (YoY)
- Required analysis: **YoY Comparison + Decomposition**
- Complexity: Medium

**Group 3: Rankings** (sorting + share)
- Required analysis: **State/Entity Ranking**
- Complexity: Medium

**Group 4: Trends** (time series)
- Required analysis: **Trend Analysis**
- Complexity: Medium-High

**Group 5: Projections** (forecasting)
- Required analysis: **Forecasting**
- Complexity: High

**Group 6: Geographic Aggregations**
- Required analysis: **Regional Aggregation**
- Complexity: Medium

### Step 3: Prioritize Analyses

**Prioritization criteria:**
1. **Frequency of use** (based on described workflow)
2. **Analytical value** (insight vs effort)
3. **Implementation complexity** (easier first)
4. **Dependencies** (does one analysis depend on another?)

Score each analysis on these criteria and implement the top 4-6 that cover 80% of use cases. Always include a **comprehensive report function** that combines multiple analyses into a single summary.

### Step 4: Specify Each Analysis

For each selected analysis, document:

```markdown
## Analysis: [Name]

**Objective**: [What it does in 1 sentence]
**When to use**: [Types of questions that trigger it]

**Required inputs**:
- Input 1: [type, description]
- Input 2: [type, description]

**Expected outputs**:
- Output 1: [type, description]

**Methodology**: [Explanation in natural language]

**Formulas**:
- Formula 1 = ...

**Validations**:
- Validation 1: [criteria]

**Interpretation**:
- If result > X: [interpretation]
- If result < Y: [interpretation]

**Concrete example**:
- Input: [specific values]
- Processing: [step by step calculation]
- Output: [JSON with result]
- Response to user: [formatted answer]
```

### Step 5: Specify Methodologies

For quantitative analyses, detail methodology with formulas.

**Example: YoY Decomposition**

```
Production = Area x Yield

Change_Production ~ Change_Area x Yield(t-1) + Area(t-1) x Change_Yield

Contrib_Area = (Change_Area% / Change_Production%) x 100
Contrib_Yield = (Change_Yield% / Change_Production%) x 100
```

**Interpretation:**
- Contrib_Area > 60%: Extensive growth (area expansion is main driver)
- Contrib_Yield > 60%: Intensive growth (technology improvement is main driver)
- Both ~50%: Balanced growth

**Validation:**
- Production(t) approximately equals Area(t) x Yield(t) (margin 1%)
- Contrib_Area + Contrib_Yield approximately equals 100% (margin 5%)

### Step 6: Comprehensive Report Function

Always design a comprehensive report function that:
- Combines data from multiple analyses
- Provides an executive summary
- Includes key metrics, comparisons, and trends
- Is the single most useful output of the skill

### Step 7: Document Analyses

Save all specifications in `references/analysis-methods.md` of the skill.

## Phase 2 Checklist

- [ ] 15+ typical questions listed
- [ ] Questions grouped by analysis type
- [ ] 4-6 analyses prioritized (with scoring)
- [ ] Each analysis specified (objective, inputs, outputs, methodology)
- [ ] Methodologies detailed with formulas
- [ ] Validations defined
- [ ] Interpretations specified
- [ ] Concrete examples included
- [ ] Comprehensive report function designed

---

# Phase 3: Architecture

## Objective

**STRUCTURE** the skill using the Agent Skills Open Standard: directory layout, files, responsibilities, cache, performance.

## Detailed Process

### Step 1: Define Skill Name

**Format:** Standard kebab-case per the Agent Skills Open Standard.

**Rules:**
- 1-64 characters
- Lowercase letters, numbers, and hyphens only
- Must not start or end with hyphen
- Must not contain consecutive hyphens
- Must match parent directory name
- **NO `-cskill` suffix**

**Examples:**
- `stock-analyzer`
- `csv-data-cleaner`
- `weekly-report-generator`
- `nass-agriculture-monitor`
- `noaa-climate-analysis`

### Step 2: Directory Structure

All skills follow the Agent Skills Open Standard structure:

**Simple Skill (1-2 workflows, <1000 lines):**

```
skill-name/
├── SKILL.md              # Primary file, <500 lines
├── scripts/
│   └── main.py
├── references/
│   └── guide.md
├── assets/
│   └── config.json
├── install.sh            # Cross-platform installer
└── README.md             # Multi-platform install instructions
```

**Organized Skill (3-5 scripts, medium complexity):**

```
skill-name/
├── SKILL.md
├── scripts/
│   ├── fetch.py
│   ├── parse.py
│   ├── analyze.py
│   └── utils/
│       ├── cache.py
│       └── validators.py
├── references/
│   ├── api-guide.md
│   └── analysis-methods.md
├── assets/
│   └── config.json
├── install.sh
└── README.md
```

**Complex Skill (6+ scripts, large scope):**

```
skill-name/
├── SKILL.md
├── scripts/
│   ├── core/
│   │   ├── fetch_source.py
│   │   ├── parse_source.py
│   │   └── analyze_source.py
│   ├── models/
│   │   └── forecasting.py
│   └── utils/
│       ├── cache_manager.py
│       ├── rate_limiter.py
│       └── validators.py
├── references/
│   ├── api-guide.md
│   ├── analysis-methods.md
│   └── troubleshooting.md
├── assets/
│   ├── config.json
│   └── metadata.json
├── install.sh
└── README.md
```

**Important:** There is NO `.claude-plugin/marketplace.json` required for simple skills. The SKILL.md file with its frontmatter is sufficient for discovery and activation on all platforms.

### Step 3: Simple vs Complex Suite Decision

| Factor | Simple Skill | Complex Suite |
|---|---|---|
| Workflows | 1-2 | 3+ distinct |
| Code size | <1000 lines | >2000 lines |
| Maintenance | Single developer | Team |
| Structure | Single SKILL.md | Multiple component SKILL.md files |
| marketplace.json | Not needed | Optional (official fields only) |

**Default:** Start with simple skill. Upgrade to complex suite only when warranted.

### Step 4: Define Script Responsibilities

**Principle:** Separation of Concerns.

**Typical scripts:**

| Script | Responsibility | Does NOT | Size |
|---|---|---|---|
| `fetch_source.py` | API requests, auth, rate limiting | Parse, transform, analyze | 200-300 lines |
| `parse_source.py` | Parsing, cleaning, validation | Fetch, analyze | 150-200 lines |
| `analyze_source.py` | All analyses (YoY, ranking, etc.) | Fetch, parse | 300-500 lines |

**Typical utils:**

| Util | Responsibility | Size |
|---|---|---|
| `cache_manager.py` | Response cache, differentiated TTL | 100-150 lines |
| `rate_limiter.py` | Rate limit control, persistent counter | 100-150 lines |
| `validators.py` | Data validations, consistency checks | 100-150 lines |

### Step 5: Plan References

Detailed documentation files loaded on demand:

| File | Content | Size |
|---|---|---|
| `api-guide.md` | How to get API key, endpoints, parameters, response format, quirks | ~1500 words |
| `analysis-methods.md` | Each analysis explained, formulas, interpretations, examples | ~2000 words |
| `troubleshooting.md` | Common problems, step-by-step solutions, FAQs | ~1000 words |

### Step 6: Plan Assets

**config.json** structure:

```json
{
  "api": {
    "base_url": "https://api.example.com/v1",
    "api_key_env": "API_KEY_VAR",
    "_instructions": "Get free key from: https://example.com/register",
    "rate_limit_per_day": 1000,
    "timeout_seconds": 30
  },
  "cache": {
    "enabled": true,
    "ttl_historical_days": 365,
    "ttl_current_days": 7
  },
  "defaults": {
    "param1": "value1"
  }
}
```

### Step 7: Cache and Rate Limiting Strategy

**Cache rules:**
- Historical data (year < current): Permanent cache (365+ days)
- Current year data: Short cache (7 days, may be revised)
- Metadata (lists, mappings): Permanent cache

**Rate limiting:**
- Persistent counter (file-based)
- Pre-request verification
- Alerts when near limit (>90%)
- Blocking when limit reached

### Step 8: Document Architecture

Prepare content for `DECISIONS.md`:
- Chosen directory structure and justification
- Script responsibilities
- Cache strategy and TTLs
- Rate limiting approach

## Phase 3 Checklist

- [ ] Skill name defined (kebab-case, no `-cskill`, 1-64 chars)
- [ ] Directory structure chosen
- [ ] Responsibilities of each script defined
- [ ] References planned (which files, content)
- [ ] Assets planned (which configs, structure)
- [ ] Cache strategy defined (what, TTL)
- [ ] Rate limiting strategy defined
- [ ] Architecture documented

---

# Phase 4: Detection

## Objective

Generate a **description** (<=1024 characters) with domain keywords for agent discovery. The description in the SKILL.md frontmatter IS the primary activation mechanism across all platforms.

**Key v4.0 change:** There are NO `activation.keywords` or `activation.patterns` fields in marketplace.json. The `description` field in SKILL.md frontmatter is the single activation mechanism. All keywords must be embedded in the description itself.

## Detailed Process

### Step 1: List Domain Entities

Identify all relevant entities users may mention:

**Entity categories:**

1. **Organizations/Sources**: Names, acronyms, full names (USDA, NASS, NOAA)
2. **Main Objects**: Domain-specific items (commodities, instruments, metrics)
3. **Geography**: Countries, regions, states
4. **Metrics**: production, area, yield, price, revenue, temperature
5. **Temporality**: years, seasons, current, historical, YoY

### Step 2: List Actions/Verbs

Which verbs does the user use to request analyses?

**Categories:**
- **Query**: what is, how much, show me, get, tell me, find
- **Compare**: compare, versus, vs, difference, change, growth
- **Rank**: top, best, leading, biggest, rank, ranking, list
- **Analyze**: analyze, trend, pattern, evolution, breakdown
- **Forecast**: predict, project, forecast, outlook, estimate
- **Report**: report, dashboard, summary, overview

### Step 3: Generate Comprehensive Keywords

For EACH metric/capability the skill implements, generate keywords:

```markdown
Metric 1: [metric name]
Primary keywords: [3-5 keywords]
Secondary keywords: [3-5 synonyms]
Action keywords: [2-3 verbs specific to this metric]
Total: ~10-15 keywords per metric
```

**Goal:** 50-80 unique keywords total across all metrics.

### Step 4: List Question Variations

For each analysis type, enumerate how users might ask:

**YoY Comparison:**
- "Compare X this year vs last year"
- "How does X compare to last year"
- "X growth rate"
- "X change YoY"
- "Did X increase or decrease"

**Ranking:**
- "Top states for X"
- "Which states produce most X"
- "Leading X producers"
- "Ranking of X"

**Trend:**
- "X trend last N years"
- "How has X changed over time"
- "Historical X data"

### Step 5: Define Negative Scope

What should NOT activate the skill? Avoid false positives.

```markdown
## Skill Scope

### WITHIN scope:
- [specific capability 1]
- [specific capability 2]

### OUT of scope:
- [related but unsupported topic 1]
- [related but unsupported topic 2]
```

### Step 6: Create the Description

The description must be <=1024 characters and serve as the sole activation mechanism. Pack it with the most important keywords.

**Template:**

```yaml
description: >-
  [What the skill does]. Activates when users ask to [primary use case],
  [secondary use case], or [tertiary use case]. Triggers on phrases like
  [keyword phrase 1], [keyword phrase 2], [keyword phrase 3], [keyword
  phrase 4]. Supports [capability 1], [capability 2], [capability 3].
  Uses [technology/API] to [what it does with real data].
```

**Mandatory components:**
1. Domain with specific entities (not just "crops" but "corn, soybeans, wheat")
2. Each major API metric explicitly mentioned
3. Action verbs covered (compare, rank, analyze, report)
4. Temporal context (current, historical, year-over-year)
5. Geographic context if relevant (states, regions, national)
6. Data source name (USDA NASS, Alpha Vantage, etc.)

**Constraints:**
- Must be 1-1024 characters
- Must be a single string (use `>-` for YAML folding)
- No line breaks in the final output

**Real example:**

```yaml
description: >-
  Analyze US agricultural production using official USDA NASS data.
  Activates when users ask about crop production, area planted, yield,
  harvest progress, or crop conditions for corn, soybeans, wheat, and
  other commodities. Triggers on phrases like compare corn production,
  top soybean states, wheat yield trend, crop condition report, harvest
  progress update. Supports year-over-year comparisons, state rankings,
  trend analyses, growth decomposition, regional aggregations, and
  comprehensive crop reports. Uses Python with NASS QuickStats API to
  fetch real data on production, area, yield, conditions, and progress.
```

### Step 7: Mental Testing

For each example question from Phase 2, verify:
- Does the description contain relevant keywords?
- Would an LLM reading the description match this query?

If any use case would NOT be detected, add missing keywords to the description.

### Step 8: Document Keywords in SKILL.md Body

In the SKILL.md body (not frontmatter), include a keywords section for transparency:

```markdown
## Keywords for Automatic Detection

This skill is activated when user mentions:

**Entities**: [list]
**Geography**: [list]
**Metrics**: [list]
**Actions**: [list]

**Activation examples:**
- "[example 1]"
- "[example 2]"
- "[example 3]"

**Does NOT activate for:**
- "[out of scope 1]"
- "[out of scope 2]"
```

## Phase 4 Checklist

- [ ] Domain entities listed (organizations, objects, geography)
- [ ] Actions/verbs listed
- [ ] 50+ keywords generated across all metrics
- [ ] Question variations mapped
- [ ] Negative scope defined
- [ ] Description created (<=1024 chars, packed with keywords)
- [ ] Keywords documented in SKILL.md body
- [ ] Activation examples (positive and negative)
- [ ] Mental detection simulation (all use cases covered)

---

# Phase 5: Implementation

## Objective

**IMPLEMENT** everything with functional code, useful documentation, and real configs. Then **validate** against the spec and run a **security scan**.

## Quality Rules (Non-Negotiable)

### NEVER:

```python
# FORBIDDEN: placeholder code
def analyze():
    # TODO: implement this function
    pass
```

```markdown
<!-- FORBIDDEN: empty reference -->
For more details, consult the official documentation at [external link].
```

```json
// FORBIDDEN: placeholder config
{ "api_key": "YOUR_API_KEY_HERE" }
```

### ALWAYS:

- Complete, functional code in every function
- Detailed docstrings with Args, Returns, Raises, Example
- Type hints on all public functions
- Robust error handling with specific exceptions
- Input and output validations
- Real values in configs with instructions for user-provided values
- Self-contained content in references (not just links)

## Implementation Order

Execute these 10 steps in order:

### Step 1: Create Directory Structure

```bash
mkdir -p skill-name/{scripts,references,assets}
```

No `.claude-plugin/` directory needed for simple skills.

### Step 2: Write SKILL.md (PRIMARY FILE - CREATE FIRST)

The SKILL.md is the most important file. It must have spec-compliant frontmatter and be <500 lines.

**Required frontmatter:**

```yaml
---
name: skill-name
description: >-
  Description here, <=1024 chars, packed with activation keywords.
license: MIT
metadata:
  author: Author Name
  version: 1.0.0
  created: 2026-02-27
  last_reviewed: 2026-02-27
  review_interval_days: 90
  dependencies:
    - url: https://api.example.com/v1
      name: Example API
      type: api
---
```

**Frontmatter field rules:**
- `name`: 1-64 chars, lowercase + hyphens, must match directory name
- `description`: 1-1024 chars, the activation mechanism
- `license`: Required (MIT, Apache-2.0, etc.)
- `metadata.author`: Required
- `metadata.version`: Required, semver format

**Body structure (must be <500 lines total including frontmatter):**

```markdown
# Skill Name

[Introduction: 2-3 paragraphs]

## When to Use This Skill

[Activation triggers with examples]

## Data Source

[API summary, link to references/api-guide.md for details]

## Workflows

### Workflow 1: [Name]
[Step-by-step with commands and examples]

### Workflow 2: [Name]
[Step-by-step with commands and examples]

## Available Scripts

[Brief description of each script, inputs, outputs]

## Available Analyses

[Brief description of each analysis, link to references/ for details]

## Error Handling

[Common errors and how the skill handles them]

## Keywords for Detection

[Organized keyword list]

## Usage Examples

[3-5 complete examples with question, flow, and answer]

## References

[Table of reference files and what they contain]
```

**Keeping under 500 lines:** Move detailed content to `references/`:
- Detailed API docs go to `references/api-guide.md`
- Detailed methodologies go to `references/analysis-methods.md`
- Troubleshooting goes to `references/troubleshooting.md`

### Step 3: Implement Python Scripts

Every script must follow this quality standard:

```python
#!/usr/bin/env python3
"""
Script title in 1 line.

Detailed description: what it does, how it works,
when to use, inputs and outputs.

Example:
    $ python script.py --param1 value1
"""

# 1. Standard library imports
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# 2. Third-party imports
import requests

# 3. Local imports
from utils.cache_manager import CacheManager


# Constants
API_BASE_URL = "https://..."
DEFAULT_TIMEOUT = 30


class MainClass:
    """
    Class description.

    Attributes:
        attr1: description
        attr2: description

    Example:
        >>> obj = MainClass(param)
        >>> result = obj.method()
    """

    def __init__(self, param1: str, param2: int = 10):
        """
        Initialize MainClass.

        Args:
            param1: detailed description
            param2: detailed description. Defaults to 10.

        Raises:
            ValueError: If param1 is invalid
        """
        if not param1:
            raise ValueError("param1 cannot be empty")
        self.param1 = param1
        self.param2 = param2

    def main_method(self, input_val: str) -> Dict:
        """
        What the method does.

        Args:
            input_val: description

        Returns:
            Dict with keys:
                - key1: description
                - key2: description

        Raises:
            APIError: If API request fails

        Example:
            >>> obj.main_method("value")
            {'key1': 123, 'key2': 'abc'}
        """
        if not self._validate_input(input_val):
            raise ValueError(f"Invalid input: {input_val}")

        try:
            result = self._do_work(input_val)
            return result
        except Exception as e:
            print(f"Error: {e}")
            raise


def main():
    """Main function with argparse."""
    import argparse

    parser = argparse.ArgumentParser(description="Script description")
    parser.add_argument('--param1', required=True, help="Parameter description")
    parser.add_argument('--output', default='output.json', help="Output file path")

    args = parser.parse_args()
    obj = MainClass(args.param1)
    result = obj.main_method(args.param1)

    import json
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
```

**Checklist per script:**
- Correct shebang (`#!/usr/bin/env python3`)
- Complete module docstring
- Organized imports (stdlib, third-party, local)
- Type hints on all public functions
- Docstrings with Args, Returns, Raises, Example
- Error handling for risky operations
- Input and output validations
- Main function with argparse
- `if __name__ == "__main__"` guard
- No TODO, no `pass`, no `NotImplementedError`

**Script patterns by type:**

**fetch_source.py** (200-300 lines):
- API client class with authentication
- Rate limiting integration
- Request retry with exponential backoff
- Response validation
- Cache integration (check cache before API call)

**parse_source.py** (150-200 lines):
- Parse raw API JSON to structured data
- Clean data (remove formatting, handle nulls)
- Transform data (standardize names, convert units)
- Validate data (required fields, ranges, no duplicates)

**analyze_source.py** (300-500 lines):
- All analysis functions (YoY, ranking, trend, etc.)
- Comprehensive report function
- Each function: validate inputs, compute, interpret, return structured result

### Step 4: Write References

Detailed documentation files. Each must be self-contained with real content.

**api-guide.md** (~1500 words):
- How to get API key (step-by-step)
- Main endpoints with example requests and responses
- Parameter details with types and valid values
- Response format with field descriptions
- Rate limits and how to handle them
- Known quirks and workarounds

**analysis-methods.md** (~2000 words):
- Each analysis explained with objective and methodology
- Mathematical formulas
- Interpretation guidelines
- Validation criteria
- Complete numerical examples with real values

**troubleshooting.md** (~1000 words):
- Common problems with symptoms, causes, and solutions
- Error messages and what they mean
- Step-by-step debugging procedures

### Step 5: Write Assets

**config.json**: Real API URLs, env var names for keys, rate limits, cache TTLs, default parameters. Always include `_instructions` or `_note` fields explaining user-provided values.

**metadata.json** (if needed): Domain-specific mappings, aliases, conversions, groupings.

### Step 6: Generate install.sh

Generate the installer from `scripts/install-template.sh` — the canonical template. Replace `{{SKILL_NAME}}` with the actual skill name and `chmod +x`:

```bash
# During skill generation:
sed "s/{{SKILL_NAME}}/skill-name/g" scripts/install-template.sh > skill-name/install.sh
chmod +x skill-name/install.sh
```

The template handles:
- POSIX-compatible shell (`set -eu`, no bashisms)
- 14 platforms: claude-code, copilot, cursor, windsurf, cline, codex, gemini, kiro, trae, goose, opencode, roo-code, antigravity, universal
- Corrected paths: Codex → `~/.agents/skills/`, Windsurf → `.windsurf/rules/` (project) / `global_rules.md` (global)
- Format adapters: auto-generates `.mdc` for Cursor, `.md` rules for Windsurf, plain `.md` for Cline/Roo/Trae
- Universal `.agents/skills/` secondary symlink after every install
- `--all` flag to install to every detected tool at once
- `--dry-run` for preview without changes

### Step 7: Write README.md

Multi-platform installation instructions:

```markdown
# Skill Name

Brief description.

## Installation

### Universal Path (works with 6+ tools)

```bash
git clone <repo-url> ~/.agents/skills/skill-name
```

Works with Codex CLI, Gemini CLI, Kiro, Antigravity, and other tools that read `~/.agents/skills/`.

### Using install.sh (Recommended)

```bash
chmod +x install.sh
./install.sh                          # Auto-detect platform
./install.sh --platform claude-code   # Claude Code
./install.sh --platform cursor        # Cursor (auto-generates .mdc)
./install.sh --all                    # All detected platforms
./install.sh --dry-run                # Preview without installing
```

### Alternative: npx

```bash
npx skills add <repo-url>
```

### Manual Installation

| Platform | Copy to |
|---|---|
| Universal | `~/.agents/skills/skill-name/` |
| Claude Code | `~/.claude/skills/skill-name/` or `.claude/skills/skill-name/` |
| GitHub Copilot | `.github/skills/skill-name/` |
| Cursor | `.cursor/rules/skill-name/` |
| Windsurf | `.windsurf/rules/skill-name/` |
| Cline | `.clinerules/skill-name/` |
| Codex CLI | `~/.agents/skills/skill-name/` |
| Gemini CLI | `~/.gemini/skills/skill-name/` |
| Kiro | `.kiro/skills/skill-name/` |
| Trae | `.trae/rules/skill-name/` |
| Goose | `~/.config/goose/skills/skill-name/` |
| OpenCode | `~/.config/opencode/skills/skill-name/` |
| Roo Code | `.roo/rules/skill-name/` |
| Antigravity | `.agents/skills/skill-name/` |

## Prerequisites

[API key instructions, dependencies]

## Usage Examples

[3-5 examples]

## Troubleshooting

[Common issues and solutions]
```

### Step 8: Run Spec Validation

After creating all files, run the validation script:

```bash
python3 scripts/validate.py path/to/skill/
```

**What it checks:**
- Frontmatter fields present and valid (name, description, license, metadata)
- Name matches directory name
- Name format: 1-64 chars, lowercase + hyphens, no leading/trailing hyphens, no consecutive hyphens
- Description: 1-1024 chars
- SKILL.md under 500 lines
- Required files present

**If validation fails:** Fix the issues and re-run. Do not proceed until validation passes.

### Step 9: Run Security Scan

```bash
python3 scripts/security_scan.py path/to/skill/
```

**What it checks:**
- Hardcoded API keys or secrets
- `.env` files with credentials
- Shell injection patterns
- Sensitive data in committed files

**If security scan finds issues:** Fix them (replace hardcoded keys with env var references, remove `.env` files, sanitize shell inputs) and re-run.

### Step 10: Report Results

After successful validation and security scan, report to the user:

```
SKILL CREATED SUCCESSFULLY

Location: ./skill-name/

Statistics:
- SKILL.md: [N] lines (<500)
- Python code: [N] lines across [N] scripts
- References: [N] files
- Total files: [N]

Validation: PASSED
Security Scan: PASSED

Main Decisions:
- API: [name] ([short justification])
- Analyses: [list]
- Structure: [simple/organized/complex]

Next Steps:
1. Get API key: [instructions or link]
2. Configure: export API_KEY_VAR="your_key"
3. Install: ./install.sh
4. Test: "[example query 1]"

See README.md for complete multi-platform installation instructions.
```

## File Creation Order Summary

| Order | File | Notes |
|---|---|---|
| 1 | Directory structure | `mkdir -p skill-name/{scripts,references,assets}` |
| 2 | `SKILL.md` | PRIMARY file, <500 lines, spec-compliant frontmatter |
| 3 | `scripts/*.py` | Functional Python code, no placeholders |
| 4 | `references/*.md` | Detailed documentation, self-contained |
| 5 | `assets/*.json` | Real values, validated JSON |
| 6 | `install.sh` | Cross-platform installer, `chmod +x` |
| 7 | `README.md` | Multi-platform install instructions |
| 8 | Run `validate.py` | Must pass before delivery |
| 9 | Run `security_scan.py` | Must pass before delivery |
| 10 | Report results | Summary to user |

## Phase 5 Checklist

- [ ] Directory structure created (NO `.claude-plugin/` for simple skills)
- [ ] SKILL.md created FIRST with spec-compliant frontmatter
- [ ] SKILL.md is <500 lines
- [ ] Frontmatter has: name, description (<=1024 chars), license, metadata (author, version)
- [ ] Temporal metadata included (metadata.created, metadata.last_reviewed, metadata.review_interval_days)
- [ ] Name is kebab-case, no `-cskill`, matches directory
- [ ] All Python scripts implemented with functional code
- [ ] No TODO, no `pass`, no `NotImplementedError`, no placeholders
- [ ] All scripts have: shebang, docstrings, type hints, error handling
- [ ] References written with real, self-contained content
- [ ] Assets created with valid JSON and real values
- [ ] `install.sh` generated with cross-platform support
- [ ] `README.md` written with multi-platform install instructions
- [ ] `requirements.txt` created (if third-party dependencies used)
- [ ] Spec validation passed (`scripts/validate.py`)
- [ ] Security scan passed (`scripts/security_scan.py`)
- [ ] Staleness check passed (`scripts/staleness_check.py`)
- [ ] Results reported to user

---

# Quality Standards Reminders

These standards apply across ALL phases and ALL generated files.

## Code Quality

**Every function must be:**
- Complete and functional (no stubs)
- Documented with docstrings (Args, Returns, Raises, Example)
- Type-hinted on all public interfaces
- Protected by error handling
- Validated on inputs and outputs

**Every script must have:**
- `#!/usr/bin/env python3` shebang
- Module-level docstring
- Organized imports (stdlib, third-party, local)
- Constants at top level
- `main()` function with argparse
- `if __name__ == "__main__"` guard

## Documentation Quality

**References must be:**
- Self-contained (not just links to external docs)
- Concrete (real values, executable examples)
- Substantial (1000+ words for main reference files)
- Well-structured (headings, lists, code blocks)

**SKILL.md must be:**
- Under 500 lines (move detail to references)
- Frontmatter-compliant (name, description, license, metadata)
- Actionable (workflows with specific commands)

## Configuration Quality

**JSON configs must be:**
- Syntactically valid (always validate with `python -c "import json; ..."`)
- Populated with real values (real API URLs, real rate limits)
- Annotated with `_instructions` or `_note` fields for user-provided values
- Never contain hardcoded secrets

## Naming Quality

- Skill names: kebab-case, 1-64 chars, no `-cskill` suffix
- Python files: snake_case
- Classes: PascalCase
- Functions/methods: snake_case
- Constants: UPPER_SNAKE_CASE

## Anti-Patterns to Avoid

| Anti-Pattern | Correct Approach |
|---|---|
| `def analyze(): pass` | Complete implementation with real logic |
| `# TODO: implement` | Implement it now |
| `api_key: YOUR_KEY_HERE` | `api_key_env: "ENV_VAR_NAME"` with instructions |
| `See official docs at [link]` | Include the relevant information directly |
| SKILL.md over 500 lines | Move detail to `references/` |
| marketplace.json as step 0 | SKILL.md is the primary file, created first |
| `-cskill` suffix in names | Standard kebab-case: `stock-analyzer` |
| Description over 1024 chars | Trim to essential keywords within limit |
