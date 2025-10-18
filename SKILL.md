---
name: agent-creator-en
description: This skill should be used when the user asks to create an agent, automate a repetitive workflow, or create a custom skill. Activates with phrases like every day, daily I have to, I need to repeat, create agent for, automate workflow, create skill for, need to automate, turn process into agent. Claude will use the 5-phase protocol to research APIs, define analyses, structure everything, implement functional code, and create a complete skill autonomously in a subdirectory.
---
# Agent Creator - Meta-Skill

This skill teaches Claude Code how to autonomously create complete agents with Claude Skills.

## When to Use This Skill

Claude should automatically activate this skill when the user:

✅ **Asks to create an agent**

- "Create an agent for [objective]"
- "I need an agent that [description]"
- "Develop an agent to automate [workflow]"

✅ **Asks to automate a workflow**

- "Automate this process: [description]"
- "Every day I do [repetitive task], automate this"
- "Turn this workflow into an agent"

✅ **Asks to create a skill**

- "Create a skill for [objective]"
- "Develop a custom skill for [domain]"

✅ **Describes a repetitive process**

- "Every day I [process]... takes Xh"
- "I repeatedly need to [task]"
- "Manual workflow: [description]"

## Overview

When activated, this skill guides Claude through **5 autonomous phases** to create a complete production-ready agent:

```
PHASE 1: DISCOVERY
├─ Research available APIs
├─ Compare options
└─ DECIDE which to use (with justification)

PHASE 2: DESIGN
├─ Think about use cases
├─ DEFINE useful analyses
└─ Specify methodologies

PHASE 3: ARCHITECTURE
├─ STRUCTURE folders and files
├─ Define necessary scripts
└─ Plan caching and performance

PHASE 4: DETECTION
├─ DETERMINE keywords
└─ Create precise description

PHASE 5: IMPLEMENTATION
├─ 🚨 FIRST: Create marketplace.json (MANDATORY!)
├─ Create SKILL.md (5000+ words)
├─ Implement Python scripts (functional!)
├─ Write references (useful!)
├─ Generate configs (real!)
├─ Create README
└─ ✅ FINAL: Test installation
```

**Output**: Complete agent in subdirectory ready to install.

## Autonomous Creation Protocol

### Fundamental Principles

**Autonomy**:

- ✅ Claude DECIDES which API to use (doesn't ask user)
- ✅ Claude DEFINES which analyses to perform (based on value)
- ✅ Claude STRUCTURES optimally (best practices)
- ✅ Claude IMPLEMENTS complete code (no placeholders)

**Quality**:

- ✅ Production-ready code (no TODOs)
- ✅ Useful documentation (not "see docs")
- ✅ Real configs (no placeholders)
- ✅ Robust error handling

**Completeness**:

- ✅ Complete SKILL.md (5000+ words)
- ✅ Functional scripts (1000+ lines total)
- ✅ References with content (3000+ words)
- ✅ Valid assets/configs
- ✅ README with instructions

### Requirements Extraction

When user describes workflow vaguely, extract:

**From what the user said**:

- Domain (agriculture? finance? weather?)
- Data source (mentioned? if not, research)
- Main tasks (download? analyze? compare?)
- Frequency (daily? weekly? on-demand?)
- Current time spent (to calculate ROI)

**Questions to ask** (only if critical and not inferable):

- "Prefer free API or paid is ok?"
- "Need historical data for how many years?"
- "Focus on which geography/country?"

**Rule**: Minimize questions. Infer/decide whenever possible.

## PHASE 1: Discovery and Research

**Objective**: DECIDE which API/data source to use

### Process

**1.1 Identify domain**

From user input, what is the domain?

- Agriculture → APIs: USDA NASS, FAO, World Bank Ag
- Finance → APIs: Alpha Vantage, Yahoo Finance, Fed Economic Data
- Weather → APIs: NOAA, OpenWeather, Weather.gov
- Economy → APIs: World Bank, IMF, FRED

**1.2 Research available APIs**

For the domain, use WebSearch to find:

- Available public APIs
- Documentation
- Characteristics (free? rate limits? coverage?)

**Example**:

```
WebSearch: "US agriculture API free historical data"
WebSearch: "USDA API documentation"
WebFetch: [doc URLs found]
```

**1.3 Compare options**

Create mental table comparing:

- Data coverage (fit with need)
- Cost (free vs paid)
- Rate limits (sufficient?)
- Data quality (official? reliable?)
- Documentation (good? examples?)
- Ease of use

**1.4 DECIDE**

Choose 1 API and justify.

**Document decision** in separate file:

```markdown
# Architecture Decisions

## Selected API: [Name]

**Justification**:
- ✅ Coverage: [details]
- ✅ Cost: [free/paid]
- ✅ Rate limit: [number]
- ✅ Quality: [official/private]
- ✅ Docs: [quality]

**Alternatives considered**:
- API X: Rejected because [reason]
- API Y: Rejected because [reason]

**Conclusion**: [Chosen API] is the best option because [synthesis]
```

**1.5 Research technical details**

Use WebFetch to load API documentation and extract:

- Base URL
- Main endpoints
- Authentication
- Important parameters
- Response format
- Rate limits
- Request/response examples

**See** `references/phase1-discovery.md` for complete details.

## PHASE 2: Analysis Design

**Objective**: DEFINE which analyses the agent will perform

### Process

**2.1 Think about use cases**

For the described workflow, which questions will the user ask frequently?

**Brainstorm**: List 10-15 typical questions

**2.2 Group by analysis type**

Group similar questions:

- Simple queries (fetch + format)
- Temporal comparisons (YoY)
- Rankings (sort + share)
- Trends (time series + CAGR)
- Projections (forecasting)
- Aggregations (regional/categorical)

**2.3 DEFINE priority analyses**

Choose 4-6 analyses that cover 80% of use cases.

For each analysis:

- Name
- Objective
- Required inputs
- Expected outputs
- Methodology (formulas, transformations)
- Interpretation

**2.4 ADD Comprehensive Report Function** (🆕 Enhancement #8 - MANDATORY!)

**⚠️ COMMON PROBLEM:** v1.0 skills had isolated functions. When user asks for "complete report", Claude didn't know how to combine all analyses.

**Solution:** ALWAYS include as last analysis function:

```python
def comprehensive_{domain}_report(
    entity: str,
    year: Optional[int] = None,
    include_metrics: Optional[List[str]] = None,
    client: Optional[Any] = None
) -> Dict:
    """
    Generate comprehensive report combining ALL available metrics.

    This is a "one-stop" function that users can call to get
    complete picture without knowing individual functions.

    Args:
        entity: Entity to analyze (e.g., commodity, stock, location)
        year: Year (None for current year with auto-detection)
        include_metrics: Which metrics to include (None = all available)
        client: API client instance (optional, created if None)

    Returns:
        Dict with ALL metrics consolidated:
        {
            'entity': str,
            'year': int,
            'year_info': str,
            'generated_at': str (ISO timestamp),
            'metrics': {
                'metric1_name': {metric1_data},
                'metric2_name': {metric2_data},
                ...
            },
            'summary': str (overall insights),
            'alerts': List[str] (important findings)
        }

    Example:
        >>> report = comprehensive_{domain}_report("CORN")
        >>> print(report['summary'])
        "CORN 2025: Production up 5% YoY, yield at record high..."
    """
    from datetime import datetime
    from utils.helpers import get_{domain}_year_with_fallback, format_year_message

    # Auto-detect year
    year_requested = year
    if year is None:
        year, _ = get_{domain}_year_with_fallback()

    # Initialize report
    report = {
        'entity': entity,
        'year': year,
        'year_requested': year_requested,
        'year_info': format_year_message(year, year_requested),
        'generated_at': datetime.now().isoformat(),
        'metrics': {},
        'alerts': []
    }

    # Determine which metrics to include
    if include_metrics is None:
        # Include ALL available metrics
        metrics_to_fetch = ['{metric1}', '{metric2}', '{metric3}', ...]
    else:
        metrics_to_fetch = include_metrics

    # Call ALL individual analysis functions
    # Graceful degradation: if one fails, others still run

    if '{metric1}' in metrics_to_fetch:
        try:
            report['metrics']['{metric1}'] = {metric1}_analysis(entity, year, client)
        except Exception as e:
            report['metrics']['{metric1}'] = {
                'error': str(e),
                'status': 'unavailable'
            }
            report['alerts'].append(f"{metric1} data unavailable: {e}")

    if '{metric2}' in metrics_to_fetch:
        try:
            report['metrics']['{metric2}'] = {metric2}_analysis(entity, year, client)
        except Exception as e:
            report['metrics']['{metric2}'] = {
                'error': str(e),
                'status': 'unavailable'
            }

    # Repeat for ALL metrics...

    # Generate summary based on all available data
    report['summary'] = _generate_summary(report['metrics'], entity, year)

    # Detect important findings
    report['alerts'].extend(_detect_alerts(report['metrics']))

    return report


def _generate_summary(metrics: Dict, entity: str, year: int) -> str:
    """Generate human-readable summary from all metrics."""
    insights = []

    # Extract key insights from each metric
    for metric_name, metric_data in metrics.items():
        if 'error' not in metric_data:
            # Extract most important insight from this metric
            key_insight = _extract_key_insight(metric_name, metric_data)
            if key_insight:
                insights.append(key_insight)

    # Combine into coherent summary
    if insights:
        summary = f"{entity} {year}: " + ". ".join(insights[:3])  # Top 3 insights
    else:
        summary = f"{entity} {year}: No data available"

    return summary


def _detect_alerts(metrics: Dict) -> List[str]:
    """Detect significant findings that need attention."""
    alerts = []

    # Check each metric for alert conditions
    for metric_name, metric_data in metrics.items():
        if 'error' in metric_data:
            continue

        # Domain-specific alert logic
        # Example: Large changes, extreme values, anomalies
        if metric_name == '{metric1}' and 'change_percent' in metric_data:
            if abs(metric_data['change_percent']) > 15:
                alerts.append(
                    f"⚠ Large {metric1} change: {metric_data['change_percent']:.1f}%"
                )

    return alerts
```

**Why it's mandatory:**
- ✅ Users want "complete report" → 1 function does everything
- ✅ Ideal for executive dashboards
- ✅ Facilitates sales ("everything in one report")
- ✅ Much better UX (no need to know individual functions)

**When to mention in SKILL.md:**

```markdown
## Comprehensive Analysis (All-in-One)

To get a complete report combining ALL metrics:

Use the `comprehensive_{domain}_report()` function.

This function:
- Fetches ALL available metrics
- Combines into single report
- Generates automatic summary
- Detects important alerts
- Degrades gracefully (if 1 metric fails, others work)

Usage example:
"Generate complete report for {entity}"
"Complete dashboard for {entity}"
"All metrics for {entity}"
```

**Impact:**
- ✅ 10x better UX (1 query = everything)
- ✅ More useful skills for end users
- ✅ Facilitates commercial adoption

**2.5 Specify methodologies**

For quantitative analyses, define:

- Mathematical formulas
- Statistical validations
- Interpretations
- Edge cases

**See** `references/phase2-design.md` for detailed methodologies.

## PHASE 3: Architecture

**Objective**: STRUCTURE the agent optimally

### Process

**3.1 Define folder structure**

Based on analyses and API:

```
agent-name/
├── SKILL.md
├── scripts/
│   ├── [fetch/parse/analyze separate or together?]
│   └── utils/
│       └── [cache? rate limiter? validators?]
├── references/
│   └── [API docs? methodologies? troubleshooting?]
└── assets/
    └── [configs? metadata?]
```

**Decisions**:

- Separate scripts (modular) vs monolithic?
- Which utilities needed?
- Which references useful?
- Which configs/assets?

**3.2 Define responsibilities**

For each script, specify:

- File name
- Function/purpose
- Input and output
- Specific responsibilities
- ~Expected number of lines

**3.3 Plan references**

Which reference files to create?

- API guide (how to use API)
- Analysis methods (methodologies)
- Troubleshooting (common errors)
- Domain knowledge (domain context)

**3.4 Performance strategy**

- Cache: What to cache? TTL?
- Rate limiting: How to control?
- Optimizations: Parallelization? Lazy loading?

**See** `references/phase3-architecture.md` for structuring patterns.

## PHASE 4: Automatic Detection

**Objective**: DETERMINE keywords for automatic activation

### Process

**4.1 List domain entities**

- Organizations/data sources
- Main metrics
- Geography (countries, regions, states)
- Temporality (years, periods)

**4.2 List typical actions**

- Query: "what", "how much", "show"
- Compare: "compare", "vs", "versus"
- Rank: "top", "best", "ranking"
- Analyze: "trend", "growth", "analyze"
- Forecast: "predict", "project", "forecast"

**4.3 List question variations**

For each analysis type, how might the user ask?

**4.4 Define negative scope**

Important! What should NOT activate the skill?

**4.5 Create precise description**

With all keywords identified, create ~200 word description that:

- Mentions domain
- Lists main keywords
- Gives examples
- Defines negative scope

**See** `references/phase4-detection.md` for complete guide.

## PHASE 5: Complete Implementation

**Objective**: IMPLEMENT everything with REAL code

### ⚠️ MANDATORY QUALITY STANDARDS

Before starting implementation, read `references/quality-standards.md`.

**NEVER DO**:

- ❌ `# TODO: implement`
- ❌ `pass` in functions
- ❌ "See external documentation"
- ❌ Configs with "YOUR_KEY_HERE" without instructions
- ❌ Empty references or just links

**ALWAYS DO**:

- ✅ Complete and functional code
- ✅ Detailed docstrings
- ✅ Robust error handling
- ✅ Type hints
- ✅ Validations
- ✅ Real content in references
- ✅ Configs with real values

### 🚨 STEP 0: BEFORE EVERYTHING - Marketplace.json (MANDATORY)

**STOP! READ THIS BEFORE CONTINUING!**

🛑 **CRITICAL BLOCKER**: You CANNOT create ANY other file until completing this step.

**Why marketplace.json is step 0:**

- ❌ Without this file, the skill CANNOT be installed via `/plugin marketplace add`
- ❌ All the work creating the agent will be USELESS without it
- ❌ This is the most common error when creating agents - DO NOT make this mistake!

#### Step 0.1: Create basic structure

```bash
mkdir -p agent-name/.claude-plugin
```

#### Step 0.2: Create marketplace.json IMMEDIATELY

Create `.claude-plugin/marketplace.json` with this content:

```json
{
  "name": "agent-name",
  "owner": {
    "name": "Agent Creator",
    "email": "noreply@example.com"
  },
  "metadata": {
    "description": "Brief agent description",
    "version": "1.0.0",
    "created": "2025-10-17"
  },
  "plugins": [
    {
      "name": "agent-plugin",
      "description": "THIS DESCRIPTION MUST BE IDENTICAL to the description in SKILL.md frontmatter that you'll create in the next step",
      "source": "./",
      "strict": false,
      "skills": ["./"]
    }
  ]
}
```

**⚠️ CRITICAL FIELDS:**

- `name`: Agent name (same as directory name)
- `plugins[0].description`: **MUST BE EXACTLY EQUAL** to SKILL.md frontmatter description
- `plugins[0].skills`: `["./"]` points to SKILL.md in root
- `plugins[0].source`: `"./"` points to agent root

#### Step 0.3: VALIDATE IMMEDIATELY (before continuing!)

**Execute NOW these validation commands:**

```bash
# 1. Validate JSON syntax
python3 -c "import json; print('✅ Valid JSON'); json.load(open('agent-name/.claude-plugin/marketplace.json'))"

# 2. Verify file exists
ls -la agent-name/.claude-plugin/marketplace.json

# If any command fails: STOP and fix before continuing!
```

**✅ CHECKLIST - You MUST complete ALL before proceeding:**

- [ ] ✅ File `.claude-plugin/marketplace.json` created
- [ ] ✅ JSON is syntactically valid (validated with python)
- [ ] ✅ Field `name` is correct
- [ ] ✅ Field `plugins[0].description` ready to receive SKILL.md description
- [ ] ✅ Field `plugins[0].skills` = `["./"]`
- [ ] ✅ Field `plugins[0].source` = `"./"`

**🛑 ONLY PROCEED AFTER VALIDATING ALL ITEMS ABOVE!**

---

### Implementation Order (AFTER marketplace.json validated)

Now that marketplace.json is created and validated, proceed:

**1. Create rest of directory structure**

```bash
mkdir -p agent-name/{scripts/utils,references,assets,data/{raw,processed,cache,analysis}}
```

**2. Create SKILL.md**

Mandatory structure:

- Frontmatter (name, description)
- When to use
- How it works (overview)
- Data source (detailed API)
- Workflows (step-by-step by question type)
- Available scripts (each explained)
- Available analyses (each explained)
- Error handling (all expected errors)
- Mandatory validations
- Performance and cache
- Keywords for detection
- Usage examples (5+ complete)

**Size**: 5000-7000 words

**⚠️ AFTER creating SKILL.md: SYNCHRONIZE description with marketplace.json!**

**CRITICAL**: Now that SKILL.md is created with its frontmatter, you MUST:

```bash
# Edit marketplace.json to update description
# Copy EXACTLY the description from SKILL.md frontmatter
# Paste in .claude-plugin/marketplace.json → plugins[0].description
```

**Verify synchronization:**

- SKILL.md frontmatter description = marketplace.json plugins[0].description
- Must be IDENTICAL (word for word!)
- Without this, skill won't activate automatically

**3. Implement Python scripts**

**Order** (MANDATORY):

1. **Utils first** (including helpers.py + validators/ - CRITICAL!)
   - `utils/helpers.py` (🔴 MANDATORY - already specified previously)
   - `utils/cache_manager.py`
   - `utils/rate_limiter.py`
   - `utils/validators/` (🔴 MANDATORY - see Step 3.5 below)
2. **Fetch** (API client - 1 method per API metric)
3. **Parse** (🔴 MODULAR: 1 parser per data type! - see Step 3.2 below)
4. **Analyze** (analyses - include comprehensive_report already specified!)

**Each script (in general)**:

- Shebang: `#!/usr/bin/env python3`
- Complete module docstring
- Organized imports
- Classes/functions with docstrings
- Type hints
- Error handling
- Logging
- Main function with argparse
- if __name__ == "__main__"

---

### Step 3.2: Modular Parser Architecture (🆕 Enhancement #5 - MANDATORY!)

**⚠️ COMMON PROBLEM:** v1.0 had 1 generic parser. When adding new data types, architecture broke.

**Solution:** **1 specific parser per API data type!**

**Rule:** If API returns N data types (identified in Phase 1.6) → create N specific parsers

**Mandatory structure:**

```
scripts/
├── parse_{type1}.py    # Ex: parse_conditions.py
├── parse_{type2}.py    # Ex: parse_progress.py
├── parse_{type3}.py    # Ex: parse_yield.py
├── parse_{type4}.py    # Ex: parse_production.py
└── parse_{type5}.py    # Ex: parse_area.py
```

**Template for each parser:**

```python
#!/usr/bin/env python3
"""
Parser for {type} data from {API_name}.
Handles {type}-specific transformations and validations.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def parse_{type}_response(data: List[Dict]) -> pd.DataFrame:
    """
    Parse API response for {type} data.

    Args:
        data: Raw API response (list of dicts)

    Returns:
        DataFrame with standardized schema:
        - entity: str
        - year: int
        - {type}_value: float
        - unit: str
        - {type}_specific_fields: various

    Raises:
        ValueError: If data is invalid
        ParseError: If parsing fails

    Example:
        >>> data = [{'entity': 'CORN', 'year': 2025, 'value': '15,300,000'}]
        >>> df = parse_{type}_response(data)
        >>> df.shape
        (1, 5)
    """
    if not data:
        raise ValueError("Data cannot be empty")

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # {Type}-specific transformations
    df = _clean_{type}_values(df)
    df = _extract_{type}_metadata(df)
    df = _standardize_{type}_schema(df)

    # Validate
    _validate_{type}_schema(df)

    return df


def _clean_{type}_values(df: pd.DataFrame) -> pd.DataFrame:
    """Clean {type}-specific values (remove formatting, convert types)."""
    # Example: Remove commas from numbers
    if 'value' in df.columns:
        df['value'] = df['value'].astype(str).str.replace(',', '')
        df['value'] = pd.to_numeric(df['value'], errors='coerce')

    # {Type}-specific cleaning
    # ...

    return df


def _extract_{type}_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """Extract {type}-specific metadata fields."""
    # Example for progress data: extract % from "75% PLANTED"
    # Example for condition data: extract rating from "GOOD (60%)"
    # Customize per data type!

    return df


def _standardize_{type}_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column names and schema for {type} data.

    Output schema:
    - entity: str
    - year: int
    - {type}_value: float (main metric)
    - unit: str
    - additional_{type}_fields: various
    """
    # Rename columns to standard names
    column_mapping = {
        'api_entity_field': 'entity',
        'api_year_field': 'year',
        'api_value_field': '{type}_value',
        # Add more as needed
    }
    df = df.rename(columns=column_mapping)

    # Ensure types
    df['year'] = df['year'].astype(int)
    df['{type}_value'] = pd.to_numeric(df['{type}_value'], errors='coerce')

    return df


def _validate_{type}_schema(df: pd.DataFrame) -> None:
    """Validate {type} DataFrame schema."""
    required_columns = ['entity', 'year', '{type}_value']

    missing = set(required_columns) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Type validations
    if not pd.api.types.is_integer_dtype(df['year']):
        raise TypeError("'year' must be integer type")

    if not pd.api.types.is_numeric_dtype(df['{type}_value']):
        raise TypeError("'{type}_value' must be numeric type")


def aggregate_{type}(df: pd.DataFrame, by: str) -> pd.DataFrame:
    """
    Aggregate {type} data by specified level.

    Args:
        df: Parsed {type} DataFrame
        by: Aggregation level ('national', 'state', 'region')

    Returns:
        Aggregated DataFrame

    Example:
        >>> agg = aggregate_{type}(df, by='state')
    """
    # Aggregation logic specific to {type}
    if by == 'national':
        return df.groupby(['year']).agg({
            '{type}_value': 'sum',
            # Add more as needed
        }).reset_index()

    elif by == 'state':
        return df.groupby(['year', 'state']).agg({
            '{type}_value': 'sum',
        }).reset_index()

    # Add more levels...


def format_{type}_report(df: pd.DataFrame) -> str:
    """
    Format {type} data as human-readable report.

    Args:
        df: Parsed {type} DataFrame

    Returns:
        Formatted string report

    Example:
        >>> report = format_{type}_report(df)
        >>> print(report)
        "{Type} Report: ..."
    """
    lines = [f"## {Type} Report\n"]

    # Format based on {type} data
    # Customize per type!

    return "\n".join(lines)


def main():
    """Test parser with sample data."""
    # Sample data for testing
    sample_data = [
        {
            'entity': 'CORN',
            'year': 2025,
            'value': '15,300,000',
            # Add {type}-specific fields
        }
    ]

    print("Testing parse_{type}_response()...")
    df = parse_{type}_response(sample_data)
    print(f"✓ Parsed {len(df)} records")
    print(f"✓ Columns: {list(df.columns)}")
    print(f"\n{df.head()}")

    print("\nTesting aggregate_{type}()...")
    agg = aggregate_{type}(df, by='national')
    print(f"✓ Aggregated: {agg}")

    print("\nTesting format_{type}_report()...")
    report = format_{type}_report(df)
    print(report)


if __name__ == "__main__":
    main()
```

**Why create modular parsers:**
- ✅ Each data type has peculiarities (progress has %, yield has bu/acre, etc)
- ✅ Scalable architecture (easy to add new types)
- ✅ Isolated tests (each parser tested independently)
- ✅ Simple maintenance (bug in 1 type doesn't affect others)
- ✅ Organized code (clear responsibilities)

**Impact:** Professional and scalable architecture from v1.0!

---

### Step 3.5: Validation System (🆕 Enhancement #10 - MANDATORY!)

**⚠️ COMMON PROBLEM:** v1.0 without data validation. User doesn't know if data is reliable.

**Solution:** Complete validation system in `utils/validators/`

**Mandatory structure:**

```
scripts/utils/validators/
├── __init__.py
├── parameter_validator.py    # Validate function parameters
├── data_validator.py         # Validate API responses
├── temporal_validator.py     # Validate temporal consistency
└── completeness_validator.py # Validate data completeness
```

**Template 1: parameter_validator.py**

```python
#!/usr/bin/env python3
"""
Parameter validators for {skill-name}.
Validates user inputs before making API calls.
"""

from typing import Any, List, Optional
from datetime import datetime


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


def validate_entity(entity: str, valid_entities: Optional[List[str]] = None) -> str:
    """
    Validate entity parameter.

    Args:
        entity: Entity name (e.g., "CORN", "SOYBEANS")
        valid_entities: List of valid entities (None to skip check)

    Returns:
        str: Validated and normalized entity name

    Raises:
        ValidationError: If entity is invalid

    Example:
        >>> validate_entity("corn")
        "CORN"  # Normalized to uppercase
    """
    if not entity:
        raise ValidationError("Entity cannot be empty")

    if not isinstance(entity, str):
        raise ValidationError(f"Entity must be string, got {type(entity)}")

    # Normalize
    entity = entity.strip().upper()

    # Check if valid (if list provided)
    if valid_entities and entity not in valid_entities:
        suggestions = [e for e in valid_entities if entity[:3] in e]
        raise ValidationError(
            f"Invalid entity: {entity}\n"
            f"Valid options: {', '.join(valid_entities[:10])}\n"
            f"Did you mean: {', '.join(suggestions[:3])}?"
        )

    return entity


def validate_year(
    year: Optional[int],
    min_year: int = 1900,
    allow_future: bool = False
) -> int:
    """
    Validate year parameter.

    Args:
        year: Year to validate (None returns current year)
        min_year: Minimum valid year
        allow_future: Whether future years are allowed

    Returns:
        int: Validated year

    Raises:
        ValidationError: If year is invalid

    Example:
        >>> validate_year(2025)
        2025
        >>> validate_year(None)
        2025  # Current year
    """
    current_year = datetime.now().year

    if year is None:
        return current_year

    if not isinstance(year, int):
        raise ValidationError(f"Year must be integer, got {type(year)}")

    if year < min_year:
        raise ValidationError(
            f"Year {year} is too old (minimum: {min_year})"
        )

    if not allow_future and year > current_year:
        raise ValidationError(
            f"Year {year} is in the future (current: {current_year})"
        )

    return year


def validate_state(state: str, country: str = "US") -> str:
    """Validate state/region parameter."""
    # Country-specific validation
    # ...
    return state.upper()


# Add more validators for domain-specific parameters...
```

**Template 2: data_validator.py**

```python
#!/usr/bin/env python3
"""
Data validators for {skill-name}.
Validates API responses and analysis outputs.
"""

import pandas as pd
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class ValidationLevel(Enum):
    """Severity levels for validation results."""
    CRITICAL = "critical"  # Must fix
    WARNING = "warning"    # Should review
    INFO = "info"          # FYI


@dataclass
class ValidationResult:
    """Single validation check result."""
    check_name: str
    level: ValidationLevel
    passed: bool
    message: str
    details: Optional[Dict] = None


class ValidationReport:
    """Collection of validation results."""

    def __init__(self):
        self.results: List[ValidationResult] = []

    def add(self, result: ValidationResult):
        """Add validation result."""
        self.results.append(result)

    def has_critical_issues(self) -> bool:
        """Check if any critical issues found."""
        return any(
            r.level == ValidationLevel.CRITICAL and not r.passed
            for r in self.results
        )

    def all_passed(self) -> bool:
        """Check if all validations passed."""
        return all(r.passed for r in self.results)

    def get_warnings(self) -> List[str]:
        """Get all warning messages."""
        return [
            r.message for r in self.results
            if r.level == ValidationLevel.WARNING and not r.passed
        ]

    def get_summary(self) -> str:
        """Get summary of validation results."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        critical = sum(
            1 for r in self.results
            if r.level == ValidationLevel.CRITICAL and not r.passed
        )

        return (
            f"Validation: {passed}/{total} passed "
            f"({critical} critical issues)"
        )


class DataValidator:
    """Validates API responses and DataFrames."""

    def validate_response(self, data: Any) -> ValidationReport:
        """
        Validate raw API response.

        Args:
            data: Raw API response

        Returns:
            ValidationReport with results
        """
        report = ValidationReport()

        # Check 1: Not empty
        report.add(ValidationResult(
            check_name="not_empty",
            level=ValidationLevel.CRITICAL,
            passed=bool(data),
            message="Data is empty" if not data else "Data present"
        ))

        # Check 2: Correct type
        expected_type = (list, dict)
        is_correct_type = isinstance(data, expected_type)
        report.add(ValidationResult(
            check_name="correct_type",
            level=ValidationLevel.CRITICAL,
            passed=is_correct_type,
            message=f"Expected {expected_type}, got {type(data)}"
        ))

        # Check 3: Has expected structure
        if isinstance(data, dict):
            has_data_key = 'data' in data
            report.add(ValidationResult(
                check_name="has_data_key",
                level=ValidationLevel.WARNING,
                passed=has_data_key,
                message="Response has 'data' key" if has_data_key else "No 'data' key"
            ))

        return report

    def validate_dataframe(self, df: pd.DataFrame, data_type: str) -> ValidationReport:
        """
        Validate parsed DataFrame.

        Args:
            df: Parsed DataFrame
            data_type: Type of data (for type-specific checks)

        Returns:
            ValidationReport
        """
        report = ValidationReport()

        # Check 1: Not empty
        report.add(ValidationResult(
            check_name="not_empty",
            level=ValidationLevel.CRITICAL,
            passed=len(df) > 0,
            message=f"DataFrame has {len(df)} rows"
        ))

        # Check 2: Required columns
        required = ['entity', 'year']  # Customize per type
        missing = set(required) - set(df.columns)
        report.add(ValidationResult(
            check_name="required_columns",
            level=ValidationLevel.CRITICAL,
            passed=len(missing) == 0,
            message=f"Missing columns: {missing}" if missing else "All required columns present"
        ))

        # Check 3: No excessive NaN values
        if len(df) > 0:
            nan_pct = (df.isna().sum() / len(df) * 100).max()
            report.add(ValidationResult(
                check_name="nan_threshold",
                level=ValidationLevel.WARNING,
                passed=nan_pct < 30,
                message=f"Max NaN: {nan_pct:.1f}% ({'OK' if nan_pct < 30 else 'HIGH'})"
            ))

        # Check 4: Data types correct
        if 'year' in df.columns:
            is_int = pd.api.types.is_integer_dtype(df['year'])
            report.add(ValidationResult(
                check_name="year_type",
                level=ValidationLevel.CRITICAL,
                passed=is_int,
                message="'year' is integer" if is_int else "'year' is not integer"
            ))

        return report


def validate_{type}_output(result: Dict) -> ValidationReport:
    """
    Validate analysis output for {type}.

    Args:
        result: Analysis result dict

    Returns:
        ValidationReport
    """
    report = ValidationReport()

    # Check required keys
    required_keys = ['year', 'year_info', 'data']
    for key in required_keys:
        report.add(ValidationResult(
            check_name=f"has_{key}",
            level=ValidationLevel.CRITICAL,
            passed=key in result,
            message=f"'{key}' present" if key in result else f"Missing '{key}'"
        ))

    # Check data quality
    if 'data' in result and result['data']:
        report.add(ValidationResult(
            check_name="data_not_empty",
            level=ValidationLevel.CRITICAL,
            passed=True,
            message="Data is present"
        ))

    return report


# Main for testing
if __name__ == "__main__":
    print("Testing validators...")

    # Test entity validator
    print("\n1. Testing validate_entity():")
    try:
        entity = validate_entity("corn", ["CORN", "SOYBEANS"])
        print(f"   ✓ Valid: {entity}")
    except ValidationError as e:
        print(f"   ✗ Error: {e}")

    # Test year validator
    print("\n2. Testing validate_year():")
    year = validate_year(2025)
    print(f"   ✓ Valid: {year}")

    # Test DataValidator
    print("\n3. Testing DataValidator:")
    validator = DataValidator()
    sample_data = [{'entity': 'CORN', 'year': 2025}]
    report = validator.validate_response(sample_data)
    print(f"   {report.get_summary()}")
```

**Template 3: temporal_validator.py**

```python
#!/usr/bin/env python3
"""
Temporal validators for {skill-name}.
Checks temporal consistency and data age.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import List
from .data_validator import ValidationResult, ValidationReport, ValidationLevel


def validate_temporal_consistency(df: pd.DataFrame) -> ValidationReport:
    """
    Check temporal consistency in data.

    Validations:
    - No future dates
    - Years in valid range
    - No suspicious gaps in time series
    - Data age is acceptable

    Args:
        df: DataFrame with 'year' column

    Returns:
        ValidationReport
    """
    report = ValidationReport()
    current_year = datetime.now().year

    if 'year' not in df.columns:
        report.add(ValidationResult(
            check_name="has_year_column",
            level=ValidationLevel.CRITICAL,
            passed=False,
            message="Missing 'year' column"
        ))
        return report

    # Check 1: No future years
    max_year = df['year'].max()
    report.add(ValidationResult(
        check_name="no_future_years",
        level=ValidationLevel.CRITICAL,
        passed=max_year <= current_year,
        message=f"Max year: {max_year} ({'valid' if max_year <= current_year else 'FUTURE!'})"
    ))

    # Check 2: Years in reasonable range
    min_year = df['year'].min()
    is_reasonable = min_year >= 1900
    report.add(ValidationResult(
        check_name="reasonable_year_range",
        level=ValidationLevel.WARNING,
        passed=is_reasonable,
        message=f"Year range: {min_year}-{max_year}"
    ))

    # Check 3: Data age (is data recent enough?)
    data_age_years = current_year - max_year
    is_recent = data_age_years <= 2
    report.add(ValidationResult(
        check_name="data_freshness",
        level=ValidationLevel.WARNING,
        passed=is_recent,
        message=f"Data age: {data_age_years} years ({'recent' if is_recent else 'STALE'})"
    ))

    # Check 4: No suspicious gaps in time series
    if len(df['year'].unique()) > 2:
        years_sorted = sorted(df['year'].unique())
        gaps = [
            years_sorted[i+1] - years_sorted[i]
            for i in range(len(years_sorted)-1)
        ]
        max_gap = max(gaps) if gaps else 0
        has_large_gap = max_gap > 2

        report.add(ValidationResult(
            check_name="no_large_gaps",
            level=ValidationLevel.WARNING,
            passed=not has_large_gap,
            message=f"Max gap: {max_gap} years" + (" (suspicious)" if has_large_gap else "")
        ))

    return report


def validate_week_number(week: int, year: int) -> ValidationResult:
    """Validate week number is in valid range for year."""
    # Most data types use weeks 1-53
    is_valid = 1 <= week <= 53

    return ValidationResult(
        check_name="valid_week",
        level=ValidationLevel.CRITICAL,
        passed=is_valid,
        message=f"Week {week} ({'valid' if is_valid else 'INVALID: must be 1-53'})"
    )


# Add more temporal validators as needed...
```

**Template 4: completeness_validator.py**

```python
#!/usr/bin/env python3
"""
Completeness validators for {skill-name}.
Checks data completeness and coverage.
"""

import pandas as pd
from typing import List, Set
from .data_validator import ValidationResult, ValidationReport, ValidationLevel


def validate_completeness(
    df: pd.DataFrame,
    expected_entities: Optional[List[str]] = None,
    expected_years: Optional[List[int]] = None
) -> ValidationReport:
    """
    Validate data completeness.

    Args:
        df: DataFrame to validate
        expected_entities: Expected entities (None to skip)
        expected_years: Expected years (None to skip)

    Returns:
        ValidationReport
    """
    report = ValidationReport()

    # Check 1: All expected entities present
    if expected_entities:
        actual_entities = set(df['entity'].unique())
        expected_set = set(expected_entities)
        missing = expected_set - actual_entities

        report.add(ValidationResult(
            check_name="all_entities_present",
            level=ValidationLevel.WARNING,
            passed=len(missing) == 0,
            message=f"Missing entities: {missing}" if missing else "All entities present",
            details={'missing': list(missing)}
        ))

    # Check 2: All expected years present
    if expected_years:
        actual_years = set(df['year'].unique())
        expected_set = set(expected_years)
        missing = expected_set - actual_years

        report.add(ValidationResult(
            check_name="all_years_present",
            level=ValidationLevel.WARNING,
            passed=len(missing) == 0,
            message=f"Missing years: {missing}" if missing else "All years present"
        ))

    # Check 3: No excessive nulls in critical columns
    critical_columns = ['entity', 'year']  # Customize
    for col in critical_columns:
        if col in df.columns:
            null_count = df[col].isna().sum()
            report.add(ValidationResult(
                check_name=f"{col}_no_nulls",
                level=ValidationLevel.CRITICAL,
                passed=null_count == 0,
                message=f"'{col}' has {null_count} nulls"
            ))

    # Check 4: Coverage percentage
    if expected_entities and expected_years:
        expected_total = len(expected_entities) * len(expected_years)
        actual_total = len(df)
        coverage_pct = (actual_total / expected_total) * 100 if expected_total > 0 else 0

        report.add(ValidationResult(
            check_name="coverage_percentage",
            level=ValidationLevel.INFO,
            passed=coverage_pct >= 80,
            message=f"Coverage: {coverage_pct:.1f}% ({actual_total}/{expected_total})"
        ))

    return report
```

**Integration in analysis functions:**

```python
def {analysis_function}(entity: str, year: Optional[int] = None, ...) -> Dict:
    """Analysis function with validation."""
    from utils.validators.parameter_validator import validate_entity, validate_year
    from utils.validators.data_validator import DataValidator
    from utils.validators.temporal_validator import validate_temporal_consistency

    # VALIDATE INPUTS (before doing anything!)
    entity = validate_entity(entity, valid_entities=[...])
    year = validate_year(year)

    # Fetch data
    data = fetch_{metric}(entity, year)

    # VALIDATE API RESPONSE
    validator = DataValidator()
    response_validation = validator.validate_response(data)

    if response_validation.has_critical_issues():
        raise DataQualityError(
            f"API response validation failed: {response_validation.get_summary()}"
        )

    # Parse
    df = parse_{type}(data)

    # VALIDATE PARSED DATA
    df_validation = validator.validate_dataframe(df, '{type}')
    temporal_validation = validate_temporal_consistency(df)

    if df_validation.has_critical_issues():
        raise DataQualityError(
            f"Data validation failed: {df_validation.get_summary()}"
        )

    # Analyze
    results = analyze(df)

    # Return with validation info
    return {
        'data': results,
        'year': year,
        'year_info': format_year_message(year, year_requested),
        'validation': {
            'passed': df_validation.all_passed(),
            'warnings': df_validation.get_warnings(),
            'report': df_validation.get_summary()
        }
    }
```

**Impact:**
- ✅ Reliable data (validated at multiple layers)
- ✅ Transparency (user sees validation report)
- ✅ Clear error messages (not just "generic error")
- ✅ Problem detection (gaps, nulls, inconsistencies)

---

**4. Write references**

For each reference file:

- 1000-2000 words
- Useful content (examples, methodologies, guides)
- Well structured (headings, lists, code blocks)
- Well-formatted markdown

**5. Create assets**

- Syntactically valid JSONs
- Real values with comments
- Logical structure

**6. Write README.md**

- Step-by-step installation
- Required configuration
- Usage examples
- Troubleshooting

**7. Create DECISIONS.md**

Document all decisions made:

- Which API chosen and why
- Which analyses defined and justification
- Structure chosen and rationale
- Trade-offs considered

**8. Create VERSION and CHANGELOG.md** (🆕 Enhancement #7 - Versioning)

**8.1 Create VERSION file:**

```
1.0.0
```

**8.2 Create CHANGELOG.md:**

```markdown
# Changelog

All notable changes to {skill-name} will be documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

## [1.0.0] - {current_date}

### Added

**Core Functionality:**
- {function1}: {Description of what it does}
- {function2}: {Description of what it does}
- {function3}: {Description of what it does}
...

**Data Sources:**
- {API_name}: {Coverage description}
- Authentication: {auth_method}
- Rate limit: {limit}

**Analysis Capabilities:**
- {analysis1}: {Description and methodology}
- {analysis2}: {Description and methodology}
...

**Utilities:**
- Cache system with {TTL} TTL
- Rate limiting: {limit} per {period}
- Error handling with automatic retries
- Data validation and quality checks

### Data Coverage

**Metrics implemented:**
- {metric1}: {Coverage details}
- {metric2}: {Coverage details}
...

**Geographic coverage:** {geo_coverage}
**Temporal coverage:** {temporal_coverage}

### Known Limitations

- {limitation1}
- {limitation2}
...

### Planned for v2.0

- {planned_feature1}
- {planned_feature2}
...

## [Unreleased]

### Planned

- Add support for {feature}
- Improve performance for {scenario}
- Expand coverage to {new_area}
```

**8.3 Update marketplace.json with version:**

Edit `.claude-plugin/marketplace.json` to include:

```json
{
  "metadata": {
    "description": "...",
    "version": "1.0.0",
    "created": "{current_date}",
    "updated": "{current_date}"
  }
}
```

**8.4 Create .bumpversion.cfg (optional):**

If you want version automation:

```ini
[bumpversion]
current_version = 1.0.0
commit = False
tag = False

[bumpversion:file:VERSION]

[bumpversion:file:.claude-plugin/marketplace.json]
search = "version": "{current_version}"
replace = "version": "{new_version}"

[bumpversion:file:CHANGELOG.md]
search = ## [Unreleased]
replace = ## [Unreleased]

## [{new_version}] - {now:%Y-%m-%d}
```

**Impact:**
- ✅ Change traceability
- ✅ Professionalism
- ✅ Facilitates future updates
- ✅ Users know what changed between versions

**9. Create INSTALLATION.md** (Didactic Tutorial)

[Content of INSTALLATION.md as previously specified]

### Practical Implementation

**Create agent in subdirectory**:

```bash
# Agent name based on domain/objective
agent_name="nass-usda-agriculture"  # example

# Create structure
mkdir -p $agent_name/{scripts/utils,references,assets,data}

# Implement each file
# [Claude creates each file with Write tool]
```

**At the end, inform user**:

```
✅ Agent created in ./{agent_name}/

📁 Structure:
- .claude-plugin/marketplace.json ✅ (installation + version)
- SKILL.md (6,200 words)
- scripts/ (2,500+ lines of code)
  ├─ utils/helpers.py ✅ (temporal context)
  ├─ utils/validators/ ✅ (4 validators, ~800 lines)
  ├─ parse_{type}*.py ✅ (1 per data type, modular)
  └─ comprehensive_{domain}_report() ✅
- tests/ (25+ tests, ~800 lines) ✅
  ├─ test_integration.py (end-to-end)
  ├─ test_parse.py (all parsers)
  ├─ test_helpers.py (temporal)
  └─ test_validation.py (validators)
- references/ (5,000 words)
- assets/ (2 configs)
- README.md (1,000+ words with Testing section)
- INSTALLATION.md (1,500 words) ✅
- DECISIONS.md (justifications)
- VERSION (1.0.0) ✅
- CHANGELOG.md (release notes) ✅

🚀 To install:
/plugin marketplace add ./{agent_name}

💡 Usage examples:
"[example 1]"
"[example 2]"
```

**See** `references/phase5-implementation.md` for complete implementation guide.

## Complete Flow: Step-by-Step

### User Input

User describes workflow/objective:

```
"Every day I download US crop data from USDA,
compare current year vs previous, create state ranking
by production, and generate report. Takes 2 hours.
Automate this."
```

### Autonomous Execution

**Claude executes internally** (doesn't need to show everything):

**PHASE 1**: Discovery (~5-10 min)

```
[WebSearch: "USDA API free agriculture data"]
[WebFetch: NASS API docs]
[Compare: NASS vs ERS vs FAO]
→ DECISION: NASS QuickStats API
   Justification: Free, data since 1866, all crops, state-level
```

**PHASE 2**: Design (~5 min)

```
[Analyze: "compare years", "state ranking", "generate report"]
→ DEFINE analyses:
  1. YoY comparison (compare years)
  2. State ranking (state ranking)
  3. Trend analysis (if user asks for trends)
  4. Report generator (generate report)
```

**PHASE 3**: Architecture (~5 min)

```
→ STRUCTURE:
  scripts/
    - fetch_nass.py (API requests)
    - parse_nass.py (parsing)
    - analyze_nass.py (YoY, ranking, trends)
    - generate_report.py (report)
    utils/
      - cache_manager.py
      - rate_limiter.py
  references/
    - nass-api-guide.md
    - analysis-methods.md
    - report-templates.md
  assets/
    - config.json
    - metadata.json
```

**PHASE 4**: Detection (~2 min)

```
→ KEYWORDS:
  Entities: USDA, NASS, agriculture, crops
  Commodities: corn, soybeans, wheat
  Metrics: production, area, yield
  Actions: compare, ranking, trend
  Geography: US, states, Iowa, Illinois

→ DESCRIPTION: "This skill should be used when user
  asks about US agriculture, production, area,
  crop yield..."
```

**PHASE 5**: Implementation (~45 min)

```
[Write: SKILL.md] ✅ 6,000 words
[Write: fetch_nass.py] ✅ 280 lines
[Write: parse_nass.py] ✅ 180 lines
[Write: analyze_nass.py] ✅ 520 lines
[Write: generate_report.py] ✅ 200 lines
[Write: utils/cache_manager.py] ✅ 120 lines
[Write: utils/rate_limiter.py] ✅ 110 lines
[Write: references/nass-api-guide.md] ✅ 1,500 words
[Write: references/analysis-methods.md] ✅ 2,000 words
[Write: references/report-templates.md] ✅ 1,000 words
[Write: assets/config.json] ✅
[Write: assets/metadata.json] ✅
[Write: README.md] ✅ 800 words
[Write: DECISIONS.md] ✅ 600 words
```

### User Output

```
✅ Agent created: ./usda-agriculture-agent/

📊 Technical Decisions:
- API: USDA NASS QuickStats (free, data since 1866)
- Analyses: YoY, Ranking, Trends, Report Generation
- Structure: 4 main scripts + 2 utils
- Cache: Historical permanent, current 7 days

📁 Files Created:
- SKILL.md: 6,000 words
- Python code: 2,500+ lines
  ├─ Modular parsers (1 per type)
  ├─ Validation system (800 lines)
  ├─ Temporal helpers
  └─ comprehensive_report()
- Tests: 25+ tests (800 lines)
- References: 4,500 words
- Configs: 2 files
- README: Complete (with Testing)
- INSTALLATION.md: Didactic tutorial
- VERSION: 1.0.0
- CHANGELOG.md: Complete release notes

🎯 Estimated Savings:
- Before: 2 hours/day
- After: 3 minutes/day
- Savings: 98.5% (117h/month → 1.5h/month)

🚀 To install and use:

# 1. Get API key (free):
Visit: https://quickstats.nass.usda.gov/api#registration

# 2. Configure:
export NASS_API_KEY="your_key_here"

# 3. Install skill:
/plugin marketplace add ./usda-agriculture-agent

# 4. Use (examples):
"US corn production in 2023"
"Compare soybeans this year vs last year"
"Ranking of wheat producing states"
"Generate current crop report"
```

## Detailed References

For details of each phase, load references:

- `references/phase1-discovery.md`: API research and decision
- `references/phase2-design.md`: Analysis definition
- `references/phase3-architecture.md`: Project structuring
- `references/phase4-detection.md`: Keywords and automatic activation
- `references/phase5-implementation.md`: Code implementation
- `references/quality-standards.md`: Mandatory standards
- `references/examples.md`: Complete examples of created agents

## Meta-Skill Usage Examples

### Example 1: Simple Workflow

```
👤 "Automate: download weather data, calculate averages,
    generate chart. I do this every week, takes 1h."

🤖 [Activates agent-creator]
   [Phase 1]: Research → NOAA API
   [Phase 2]: Defines → Download, Aggregation, Visualization
   [Phase 3]: Structure → 3 scripts + 2 utils
   [Phase 4]: Keywords → weather, climate, temperature, NOAA
   [Phase 5]: Implements everything

   ✅ Agent created: ./weather-analysis-agent/
   [Installation instructions]
```

### Example 2: Complex Workflow

```
👤 "I need an agent for stock financial analysis:
    fetch prices, calculate technical indicators (RSI, MACD),
    compare with benchmarks, generate alerts. Daily, 3h."

🤖 [Activates agent-creator]
   [Phase 1]: Research → Alpha Vantage API (or Yahoo Finance)
   [Phase 2]: Defines → Price fetching, Technical indicators,
             Benchmark comparison, Alert system
   [Phase 3]: Structure → 5 scripts + 4 utils
   [Phase 4]: Keywords → stock, RSI, MACD, technical analysis
   [Phase 5]: Implements

   ✅ Agent created: ./stock-technical-analysis-agent/
```

### Example 3: Just Vague Description

```
👤 "Create an agent for Brazilian agriculture"

🤖 [Activates agent-creator]

   "Got it! I'll create an agent for Brazilian agriculture.

   A few quick questions:
   - Focus on which crops? (soy, corn, coffee, all?)
   - Desired analyses? (production, prices, exports?)
   - Preferred source? (CONAB, IBGE, both?)

   Or I can decide based on most common use cases
   (grain production via CONAB). Prefer I decide?"

👤 "You decide, focus on grain production."

🤖 [Phase 1]: CONAB Grain Survey
   [Phase 2]: YoY, Ranking, Regional, Trends
   [Phase 3-5]: Creates everything

   ✅ Agent created: ./conab-agriculture-agent/
```

---

## PHASE 6: Test Suite Generation (🆕 Enhancement #4 - MANDATORY!)

**Objective**: Generate comprehensive test suite that validates ALL functions

**⚠️ COMMON PROBLEM:** v1.0 without tests. Difficult to validate code works, impossible to do regression testing.

**Solution:** Automatically generate 25+ tests covering all layers!

### Test Structure

```
tests/
├── __init__.py
├── test_fetch.py            # Test API fetch functions
├── test_parse.py            # Test each parser
├── test_analyze.py          # Test analysis functions
├── test_integration.py      # End-to-end tests
├── test_validation.py       # Test validators
├── test_helpers.py          # Test temporal helpers
└── conftest.py              # Shared fixtures (pytest)
```

### Template 1: test_integration.py (MAIN!)

```python
#!/usr/bin/env python3
"""
Integration tests for {skill-name}.
Tests complete workflows from query to result.
"""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from analyze_{domain} import (
    {function1},
    {function2},
    {function3},
    comprehensive_{domain}_report
)


def test_{function1}_basic():
    """Test {function1} with auto-year detection."""
    print(f"\n✓ Testing {function1}()...")

    try:
        # Test auto-year detection (year=None)
        result = {function1}('{example_entity}')

        # Validations
        assert 'year' in result, "Missing 'year' in result"
        assert 'year_info' in result, "Missing 'year_info'"
        assert 'data' in result, "Missing 'data'"
        assert result['year'] >= 2024, f"Year too old: {result['year']}"

        print(f"  ✓ Auto-year working: {result['year']}")
        print(f"  ✓ Year info: {result['year_info']}")
        print(f"  ✓ Data present: {len(result.get('data', {}))} fields")

        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_{function1}_specific_year():
    """Test {function1} with specific year."""
    print(f"\n✓ Testing {function1}(year=2024)...")

    try:
        result = {function1}('{example_entity}', year=2024)

        assert result['year'] == 2024, "Requested year not used"
        assert result['year_requested'] == 2024, "year_requested not tracked"

        print(f"  ✓ Specific year working: {result['year']}")

        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_{function2}_comparison():
    """Test {function2} (comparison function)."""
    print(f"\n✓ Testing {function2}()...")

    try:
        result = {function2}('{example_entity}', year1=2024, year2=2023)

        # Validations specific to comparison
        assert 'change_percent' in result, "Missing 'change_percent'"
        assert isinstance(result['change_percent'], (int, float)), "change_percent not numeric"

        print(f"  ✓ Comparison working: {result.get('change_percent')}% change")

        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_comprehensive_report():
    """Test comprehensive report (all-in-one function)."""
    print(f"\n✓ Testing comprehensive_{domain}_report()...")

    try:
        result = comprehensive_{domain}_report('{example_entity}')

        # Validations
        assert 'metrics' in result, "Missing 'metrics'"
        assert 'summary' in result, "Missing 'summary'"
        assert 'alerts' in result, "Missing 'alerts'"
        assert isinstance(result['metrics'], dict), "'metrics' must be dict"

        metrics_count = len(result['metrics'])
        print(f"  ✓ Comprehensive report working")
        print(f"  ✓ Metrics combined: {metrics_count}")
        print(f"  ✓ Summary: {result['summary'][:100]}...")
        print(f"  ✓ Alerts: {len(result['alerts'])}")

        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_validation_integration():
    """Test that validation is integrated in functions."""
    print(f"\n✓ Testing validation integration...")

    try:
        result = {function1}('{example_entity}')

        # Check validation info is present
        assert 'validation' in result, "Missing 'validation' info"
        assert 'passed' in result['validation'], "Missing validation.passed"
        assert 'report' in result['validation'], "Missing validation.report"

        print(f"  ✓ Validation present: {result['validation']['report']}")

        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def main():
    """Run all integration tests."""
    print("=" * 70)
    print("INTEGRATION TESTS - {skill-name}")
    print("=" * 70)

    tests = [
        ("Auto-year detection", test_{function1}_basic),
        ("Specific year", test_{function1}_specific_year),
        ("Comparison function", test_{function2}_comparison),
        ("Comprehensive report", test_comprehensive_report),
        ("Validation integration", test_validation_integration),
    ]

    results = []
    for test_name, test_func in tests:
        passed = test_func()
        results.append((test_name, passed))

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)

    print(f"\nResults: {passed_count}/{total_count} passed")

    return passed_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

### Template 2: test_parse.py

```python
#!/usr/bin/env python3
"""Tests for parsers."""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from parse_{type1} import parse_{type1}_response
from parse_{type2} import parse_{type2}_response
# Import all parsers...


def test_parse_{type1}():
    """Test {type1} parser."""
    print("\n✓ Testing parse_{type1}_response()...")

    sample_data = [
        {'{field1}': 'VALUE1', '{field2}': 2025, '{field3}': '1,234,567'}
    ]

    try:
        df = parse_{type1}_response(sample_data)

        # Validations
        assert isinstance(df, pd.DataFrame), "Must return DataFrame"
        assert len(df) == 1, f"Expected 1 row, got {len(df)}"
        assert 'entity' in df.columns, "Missing 'entity' column"
        assert 'year' in df.columns, "Missing 'year' column"

        print(f"  ✓ Parsed: {len(df)} records")
        print(f"  ✓ Columns: {list(df.columns)}")

        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


# Repeat for all parsers...

def main():
    """Run parser tests."""
    tests = [
        test_parse_{type1},
        test_parse_{type2},
        # Add all...
    ]

    passed = sum(1 for test in tests if test())
    print(f"\nResults: {passed}/{len(tests)} passed")

    return passed == len(tests)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
```

### Template 3: test_helpers.py

```python
#!/usr/bin/env python3
"""Tests for temporal helpers."""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from utils.helpers import (
    get_current_{domain}_year,
    get_{domain}_year_with_fallback,
    should_try_previous_year,
    format_year_message
)


def test_get_current_year():
    """Test current year detection."""
    year = get_current_{domain}_year()
    current = datetime.now().year

    assert year == current, f"Expected {current}, got {year}"
    print(f"✓ Current year: {year}")
    return True


def test_year_with_fallback():
    """Test year fallback logic."""
    primary, fallback = get_{domain}_year_with_fallback(2024)

    assert primary == 2024, "Primary should be 2024"
    assert fallback == 2023, "Fallback should be 2023"

    print(f"✓ Fallback: {primary} → {fallback}")
    return True


def test_format_year_message():
    """Test year message formatting."""
    msg = format_year_message(2024, 2025)

    assert '2024' in msg, "Must mention year used"
    assert '2025' in msg, "Must mention year requested"

    print(f"✓ Message: {msg}")
    return True


def main():
    """Run helper tests."""
    tests = [
        test_get_current_year,
        test_year_with_fallback,
        test_format_year_message
    ]

    passed = sum(1 for test in tests if test())
    print(f"\nResults: {passed}/{len(tests)} passed")

    return passed == len(tests)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
```

### Minimum Test Coverage

**For skill to be considered complete, needs:**

- [ ] test_integration.py with ≥5 end-to-end tests
- [ ] test_parse.py with 1 test per parser
- [ ] test_analyze.py with 1 test per analysis function
- [ ] test_helpers.py with ≥3 tests
- [ ] test_validation.py with ≥5 tests
- [ ] **Total:** ≥25 tests
- [ ] **Coverage:** ≥80% of code
- [ ] **All tests PASS**

### How to test

Include in README.md:

```markdown
## Testing

### Run All Tests

```bash
cd {skill-name}
python3 tests/test_integration.py
```

### Run Specific Tests

```bash
python3 tests/test_parse.py
python3 tests/test_helpers.py
python3 tests/test_validation.py
```

### Expected Output

```
======================================================================
INTEGRATION TESTS - {skill-name}
======================================================================

✓ Testing {function1}()...
  ✓ Auto-year working: 2025
  ✓ Data present: 8 fields

✓ Testing {function2}()...
  ✓ Comparison working: +12.3% change

...

======================================================================
SUMMARY
======================================================================
✅ PASS: Auto-year detection
✅ PASS: Specific year
✅ PASS: Comparison function
✅ PASS: Comprehensive report
✅ PASS: Validation integration

Results: 5/5 passed
```
```

### Test Suite Benefits

- ✅ Reliability: Tested and working code
- ✅ Regression testing: Detects breaks when modifying
- ✅ Executable documentation: Tests show how to use
- ✅ CI/CD ready: Can run automatically
- ✅ Professionalism: Production-quality skills

**Impact:** Generated skills are tested and reliable from v1.0!

---

## Agent Creation Workflow: Checklist

When creating an agent, follow this checklist RIGOROUSLY in order:

---

### 🚨 STEP 0: MANDATORY - FIRST STEP

**Execute BEFORE anything else:**

- [ ] 🚨 Create `.claude-plugin/marketplace.json`
- [ ] 🚨 Validate JSON syntax with python
- [ ] 🚨 Verify mandatory fields filled
- [ ] 🚨 Confirm: "Marketplace.json created and validated - can proceed"

**🛑 DO NOT PROCEED without completing ALL items above!**

---

### ✅ Phase 1-4: Planning

- [ ] Domain identified
- [ ] API researched and decided (with justification)
- [ ] **API completeness analysis** (Phase 1.6 - coverage ≥50%)
- [ ] Analyses defined (4-6 main + comprehensive_report)
- [ ] Structure planned (modular parsers, validators/)
- [ ] Keywords determined (≥60 unique)

---

### ✅ Phase 5: Implementation

- [ ] .claude-plugin/marketplace.json created FIRST
- [ ] marketplace.json validated (syntax + fields)
- [ ] SKILL.md created with correct frontmatter
- [ ] **CRITICAL:** SKILL.md description copied to marketplace.json → plugins[0].description (IDENTICAL!)
- [ ] Validate synchronization: SKILL.md description === marketplace.json
- [ ] **MANDATORY:** utils/helpers.py created (temporal context)
- [ ] **MANDATORY:** utils/validators/ created (4 validators)
- [ ] **MANDATORY:** Modular parsers (1 per data type)
- [ ] **MANDATORY:** comprehensive_{domain}_report() implemented
- [ ] DECISIONS.md documenting choices
- [ ] VERSION file created (e.g., 1.0.0)
- [ ] CHANGELOG.md created with complete v1.0.0 entry
- [ ] marketplace.json with version field
- [ ] Implement functional code (no TODOs)
- [ ] Write complete docstrings
- [ ] Add error handling
- [ ] Write references with useful content
- [ ] Create real configs
- [ ] Write complete README
- [ ] INSTALLATION.md with complete tutorial

---

### ✅ Phase 6: Test Suite

- [ ] tests/ directory created
- [ ] test_integration.py with ≥5 end-to-end tests
- [ ] test_parse.py with 1 test per parser
- [ ] test_analyze.py with 1 test per analysis function
- [ ] test_helpers.py with ≥3 tests
- [ ] test_validation.py with ≥5 tests
- [ ] **Total:** ≥25 tests implemented
- [ ] **ALL tests PASS** (execute and validate!)
- [ ] "Testing" section added to README.md

---

### ✅ Final Validation

- [ ] Validate marketplace.json again (syntax + synchronized description)
- [ ] Validate other JSONs (configs, assets)
- [ ] Verify imports work
- [ ] Check no placeholder/TODO
- [ ] Test main logic manually
- [ ] Verify README has all instructions
- [ ] Calculate estimated ROI (time before vs after)

---

### 🚀 MANDATORY TEST - DO NOT SKIP THIS STEP!

**Execute this command MANDATORY before delivering:**

```bash
cd /path/to/skills
/plugin marketplace add ./agent-name
```

**Verifications:**

- [ ] ✅ Command executed without errors
- [ ] ✅ Skill appears in installed plugins list
- [ ] ✅ Claude recognizes the skill (do test question)

**🛑 If test fails:**

1. Verify marketplace.json exists
2. Verify JSON is valid
3. Verify description is synchronized
4. Fix and test again

**Only deliver to user AFTER installation test passes!**

---

### ✅ Deliver to User

- [ ] Show created structure
- [ ] Summarize main decisions
- [ ] List files and sizes
- [ ] Give installation instructions (command tested above)
- [ ] Give 3-5 usage examples
- [ ] Inform estimated ROI
- [ ] **Confirm: "Skill tested and installed successfully"**

## User Communication

### During Creation

**Show high-level progress**:

```
🔍 Phase 1: Researching APIs...
   ✓ 5 options found
   ✓ Decided: NASS API (free, complete data)

🎨 Phase 2: Defining analyses...
   ✓ 15 typical questions identified
   ✓ 5 main analyses defined

🏗️ Phase 3: Structuring project...
   ✓ 3 scripts + 2 utils planned

🎯 Phase 4: Defining detection...
   ✓ 50+ keywords identified

⚙️ Phase 5: Implementing code...
   [Progress while creating files]
   ✓ SKILL.md (6,200 words)
   ✓ fetch_nass.py (280 lines)
   ✓ parse_nass.py (180 lines)
   [...]
```

**Don't show**: Technical details during creation (code blocks, etc). Just progress.

### After Completion

**Executive summary**:

```
✅ AGENT CREATED SUCCESSFULLY!

📂 Location: ./usda-agriculture-agent/

📊 Main Decisions:
- API: USDA NASS QuickStats
- Analyses: YoY, Ranking, Trends, Reports
- Implementation: 1,410 lines Python + 4,500 words docs

💰 Estimated ROI:
- Time before: 2h/day
- Time after: 3min/day
- Savings: 117h/month

🎓 See DECISIONS.md for complete justifications.

🚀 NEXT STEPS:

1. Get API key (free):
   https://quickstats.nass.usda.gov/api#registration

2. Configure:
   export NASS_API_KEY="your_key"

3. Install:
   /plugin marketplace add ./usda-agriculture-agent

4. Test:
   "US corn production in 2023"
   "Compare soybeans this year vs last year"

See README.md for complete instructions.
```

## Keywords for This Meta-Skill Detection

This meta-skill (agent-creator) is activated when user mentions:

**Create/Develop**:

- "Create an agent"
- "Develop agent"
- "Create skill"
- "Develop skill"
- "Build agent"

**Automate**:

- "Automate this workflow"
- "Automate this process"
- "Automate this task"
- "Need to automate"
- "Turn into agent"

**Repetitive Workflow**:

- "Every day I do"
- "Repeatedly need to"
- "Manual process"
- "Workflow that takes Xh"
- "Task I repeat"

**Agent for Domain**:

- "Agent for [domain]"
- "Custom skill for [domain]"
- "Specialize Claude in [domain]"

## ⚠️ Troubleshooting: Common Marketplace.json Errors

### Error: "Failed to install plugin"

**Most common cause:** marketplace.json doesn't exist or is poorly formatted

**Diagnosis:**

```bash
# 1. Verify file exists
ls -la agent-name/.claude-plugin/marketplace.json

# 2. Validate JSON
python3 -c "import json; json.load(open('agent-name/.claude-plugin/marketplace.json'))"

# 3. View content
cat agent-name/.claude-plugin/marketplace.json
```

**Solutions:**

1. If file doesn't exist: Go back to STEP 0 and create
2. If invalid JSON: Fix syntax errors
3. If missing fields: Compare with STEP 0 template

### Error: "Skill not activating"

**Cause:** marketplace.json description ≠ SKILL.md description

**Diagnosis:**

```bash
# Compare descriptions
grep "description:" agent-name/SKILL.md
grep "\"description\":" agent-name/.claude-plugin/marketplace.json
```

**Solution:**

1. Copy EXACT description from SKILL.md frontmatter
2. Paste in marketplace.json → plugins[0].description
3. Ensure they are IDENTICAL (word for word)
4. Save and test installation again

### Error: "Invalid plugin structure"

**Cause:** Mandatory marketplace.json fields incorrect

**Verify:**

- ✅ `plugins[0].skills` = `["./"]` (not `["SKILL.md"]` or other value)
- ✅ `plugins[0].source` = `"./"` (not empty or other value)
- ✅ `name` in JSON root matches directory name

**Solution:**
Edit marketplace.json and fix fields above according to STEP 0 template.

## Limitations and Warnings

### When NOT to use

❌ Don't use this skill for:

- Editing existing skills (use directly)
- Debugging skills (use directly)
- Questions about skills (answer directly)

### Warnings

⚠️ **Creation time**:

- Simple agents: ~30-60 min
- Complex agents: ~60-120 min
- It's normal to take time (creating everything from scratch)

⚠️ **Review needed**:

- Created agent is functional but may need adjustments
- Test examples in README
- Iterate if necessary

⚠️ **API keys**:

- User needs to obtain API key
- Instructions in created agent's README
