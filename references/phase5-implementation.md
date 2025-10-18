# Phase 5: Complete Implementation

## Objective

**IMPLEMENT** everything with FUNCTIONAL code, USEFUL documentation, and REAL configs.

## ⚠️ FUNDAMENTAL RULES

### What to NEVER Do

❌ **FORBIDDEN**:
```python
# TODO: implement this function
def analyze():
    pass
```

❌ **FORBIDDEN**:
```markdown
For more details, consult the official documentation at [external link].
```

❌ **FORBIDDEN**:
```json
{
  "api_key": "YOUR_API_KEY_HERE"
}
```

### What to ALWAYS Do

✅ **MANDATORY**: Complete and functional code
✅ **MANDATORY**: Detailed docstrings
✅ **MANDATORY**: Useful content in references
✅ **MANDATORY**: Configs with real values + instructions

## Implementation Order (Updated v2.0)

```
1. Create directory structure
2. Create marketplace.json (MANDATORY!)
3. Implement base utils (cache, rate limiter)
4. Implement utils/helpers.py (NEW! - Temporal context)
5. Create utils/validators/ (NEW! - Validation system)
6. Implement fetch (API client - ALL endpoints!)
7. Implement parsers (1 per data type - NEW!)
8. Implement analyze (analyses + comprehensive report)
9. Create tests/ (NEW! - Test suite)
10. Create examples/ (NEW! - Real-world examples)
11. Write SKILL.md
12. Write references
13. Create assets
14. Write README
15. Create QUICK-START.md (NEW!)
16. Create CHANGELOG.md and VERSION (NEW!)
17. Create DECISIONS.md
```

**Why this order** (updated)?
- Marketplace.json FIRST (without it, skill can't install)
- Helpers early (used by analyze functions)
- Validators before analyze (integration)
- ALL fetch methods (not just 1!)
- Modular parsers (1 per type)
- Tests and examples before docs (validate before documenting)
- Distribution docs (QUICK-START) to facilitate usage

## Implementation: Directory Structure

```bash
# Create using Bash tool
mkdir -p {agent-name}/{scripts/utils,references,assets,data/{raw,processed,cache,analysis},.claude-plugin}

# Verify
ls -la {agent-name}/
```

## Implementation: Marketplace.json (MANDATORY!)

### ⚠️ CRITICAL: Without marketplace.json, skill CANNOT be installed!

**Create FIRST**, before any other file!

### Location

```
{agent-name}/.claude-plugin/marketplace.json
```

### Complete Template

```json
{
  "name": "{agent-name}",
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
      "name": "{agent-name}-plugin",
      "description": "COPY EXACTLY the description from SKILL.md frontmatter",
      "source": "./",
      "strict": false,
      "skills": ["./"]
    }
  ]
}
```

### Required Fields

**`name` (root level)**:
- Agent name (same as directory name)
- Example: `"climate-analysis-sorriso-mt"`

**`plugins[0].name`**:
- Plugin name (can be agent-name + "-plugin")
- Example: `"climate-analysis-plugin"`

**`plugins[0].description`** (VERY IMPORTANT!):
- **MUST BE EXACTLY EQUAL** to `description` in SKILL.md frontmatter
- This is the description Claude uses to detect when to activate the skill
- Copy word-for-word, including keywords
- Size: 150-250 words

**`plugins[0].source`**:
- Always `"./"`  (points to agent root)

**`plugins[0].skills`**:
- Always `["./"]`  (points to SKILL.md in root)

### Complete Example (Climate Agent)

```json
{
  "name": "climate-analysis-sorriso-mt",
  "owner": {
    "name": "Agent Creator",
    "email": "noreply@example.com"
  },
  "metadata": {
    "description": "Climate analysis agent for Sorriso, Mato Grosso",
    "version": "1.0.0",
    "created": "2025-10-17"
  },
  "plugins": [
    {
      "name": "climate-analysis",
      "description": "This skill should be used for climate analysis of Sorriso in Mato Grosso State, Brazil. Activates when user asks about temperature, precipitation, rainfall or climate in Sorriso-MT. Supports historical data analyses since 1940 including time series, year-over-year comparisons (YoY), long-term trends, climate anomaly detection, seasonal patterns and descriptive statistics. Uses Open-Meteo Historical Weather API data based on ERA5 reanalysis.",
      "source": "./",
      "strict": false,
      "skills": ["./"]
    }
  ]
}
```

### Validation

**After creating, ALWAYS validate**:

```bash
# Syntax check
python -c "import json; print(json.load(open('.claude-plugin/marketplace.json')))"

# If no error, it's valid!
```

**Verify**:
- ✅ JSON syntactically correct
- ✅ `plugins[0].description` **identical** to SKILL.md frontmatter
- ✅ `skills` points to `["./"]`
- ✅ `source` is `"./"`

### Creation Order

```bash
1. ✅ mkdir .claude-plugin
2. ✅ Write: .claude-plugin/marketplace.json  ← FIRST!
3. ✅ Write: SKILL.md (with frontmatter)
4. ... (rest of files)
```

### Why Marketplace.json is Mandatory

Without this file:
- ❌ `/plugin marketplace add ./agent-name` FAILS
- ❌ Skill cannot be installed
- ❌ Claude cannot use the skill
- ❌ All work creating agent is useless

**NEVER forget to create marketplace.json!**

## Implementation: Python Scripts

### Quality Standard for EVERY Script

**Mandatory template**:

```python
#!/usr/bin/env python3
"""
[Script title in 1 line]

[Detailed description in 2-3 paragraphs explaining:
- What the script does
- How it works
- When to use
- Inputs and outputs
- Dependencies]

Example:
    $ python script.py --param1 value1 --param2 value2
"""

# Organized imports
# 1. Standard library
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# 2. Third-party
import requests
import pandas as pd

# 3. Local
from utils.cache_manager import CacheManager


# Constants at top
API_BASE_URL = "https://..."
DEFAULT_TIMEOUT = 30


class MainClass:
    """
    [Class description]

    Attributes:
        attr1: [description]
        attr2: [description]

    Example:
        >>> obj = MainClass(param)
        >>> result = obj.method()
    """

    def __init__(self, param1: str, param2: int = 10):
        """
        Initialize [MainClass]

        Args:
            param1: [detailed description]
            param2: [detailed description]. Defaults to 10.

        Raises:
            ValueError: If param1 is invalid
        """
        if not param1:
            raise ValueError("param1 cannot be empty")

        self.param1 = param1
        self.param2 = param2

    def main_method(self, input_val: str) -> Dict:
        """
        [What the method does]

        Args:
            input_val: [description]

        Returns:
            Dict with keys:
                - key1: [description]
                - key2: [description]

        Raises:
            APIError: If API request fails
            ValueError: If input is invalid

        Example:
            >>> obj.main_method("value")
            {'key1': 123, 'key2': 'abc'}
        """
        # Validate input
        if not self._validate_input(input_val):
            raise ValueError(f"Invalid input: {input_val}")

        try:
            # Complete implementation here
            result = self._do_work(input_val)

            return result

        except Exception as e:
            # Specific error handling
            print(f"Error: {e}")
            raise

    def _validate_input(self, value: str) -> bool:
        """Helper for validation"""
        # Complete implementation
        return len(value) > 0

    def _do_work(self, value: str) -> Dict:
        """Internal helper"""
        # Complete implementation
        return {"result": "value"}


def main():
    """Main function with argparse"""
    import argparse

    parser = argparse.ArgumentParser(
        description="[Script description]"
    )
    parser.add_argument(
        '--param1',
        required=True,
        help="[Parameter description with example]"
    )
    parser.add_argument(
        '--output',
        default='output.json',
        help="Output file path"
    )

    args = parser.parse_args()

    # Execute
    obj = MainClass(args.param1)
    result = obj.main_method(args.param1)

    # Save output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"✓ Saved: {output_path}")


if __name__ == "__main__":
    main()
```

**Verify each script has**:
- ✅ Correct shebang
- ✅ Complete module docstring
- ✅ Organized imports
- ✅ Type hints in functions
- ✅ Docstrings in classes and methods
- ✅ Error handling
- ✅ Input validations
- ✅ Main function with argparse
- ✅ if __name__ == "__main__"

### Script 1: fetch_*.py

**Responsibility**: API requests

**Must implement**:

```python
class APIClient:
    """Client for [API]"""

    def __init__(self, api_key: str):
        """
        Initialize API client

        Args:
            api_key: API key (get from [where])

        Raises:
            ValueError: If API key is None or empty
        """
        if not api_key:
            raise ValueError("API key required")

        self.api_key = api_key
        self.session = requests.Session()
        self.rate_limiter = RateLimiter(...)

    def fetch(self, **params) -> Dict:
        """
        Fetch data from API

        Args:
            **params: Query parameters

        Returns:
            API response as dict

        Raises:
            RateLimitError: If rate limit exceeded
            APIError: If API returns error
        """
        # 1. Check rate limit
        if not self.rate_limiter.allow():
            raise RateLimitError("Rate limit exceeded")

        # 2. Build request
        url = f"{BASE_URL}/endpoint"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        # 3. Make request with retry
        response = self._request_with_retry(url, headers, params)

        # 4. Validate response
        self._validate_response(response)

        # 5. Record request
        self.rate_limiter.record()

        return response.json()

    def _request_with_retry(self, url, headers, params, max_retries=3):
        """Request with exponential retry"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=30
                )
                response.raise_for_status()
                return response

            except requests.Timeout:
                if attempt < max_retries - 1:
                    wait = 2 ** attempt
                    time.sleep(wait)
                else:
                    raise

            except requests.HTTPError as e:
                if e.response.status_code == 429:  # Rate limit
                    raise RateLimitError("Rate limit exceeded")
                elif e.response.status_code in [500, 502, 503]:
                    if attempt < max_retries - 1:
                        wait = 2 ** attempt
                        time.sleep(wait)
                    else:
                        raise APIError(f"API error: {e}")
                else:
                    raise APIError(f"HTTP {e.response.status_code}: {e}")
```

**Size**: 200-300 lines

### Script 2: parse_*.py

**Responsibility**: Parsing and validation

**Must implement**:

```python
class DataParser:
    """Parser for [API] data"""

    def parse(self, raw_data: Dict) -> pd.DataFrame:
        """
        Parse raw API response to structured DataFrame

        Args:
            raw_data: Raw response from API

        Returns:
            Cleaned DataFrame with columns: [list]

        Raises:
            ParseError: If data format is unexpected
        """
        # 1. Extract data
        records = raw_data.get('data', [])

        if not records:
            raise ParseError("No data in response")

        # 2. Convert to DataFrame
        df = pd.DataFrame(records)

        # 3. Cleaning
        df = self._clean_data(df)

        # 4. Transformations
        df = self._transform(df)

        # 5. Validation
        self._validate(df)

        return df

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Data cleaning"""
        # Remove number formatting
        for col in ['production', 'area', 'yield']:
            if col in df.columns:
                df[col] = df[col].str.replace(',', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Handle suppressed values
        df = df.replace('(D)', pd.NA)
        df = df.replace('(E)', pd.NA)  # Or mark as estimate

        return df

    def _transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transformations"""
        # Standardize names
        df['state'] = df['state_name'].str.upper()

        # Convert units (if needed)
        if 'unit' in df.columns and df['unit'].iloc[0] == 'BU':
            # Bushels to metric tons
            df['value_mt'] = df['value'] * 0.0254

        return df

    def _validate(self, df: pd.DataFrame):
        """Validations"""
        # Required fields
        required = ['state', 'year', 'commodity', 'value']
        missing = set(required) - set(df.columns)
        if missing:
            raise ParseError(f"Missing columns: {missing}")

        # Values in expected ranges
        if (df['value'] < 0).any():
            raise ParseError("Negative values found")

        # No duplicates
        duplicates = df.duplicated(subset=['state', 'year', 'commodity'])
        if duplicates.any():
            raise ParseError(f"Duplicates found: {duplicates.sum()}")
```

**Size**: 150-200 lines

### Script 3: analyze_*.py

**Responsibility**: All analyses

**Must implement**:

```python
class Analyzer:
    """Analyses for [domain] data"""

    def __init__(self, df: pd.DataFrame):
        """
        Initialize analyzer

        Args:
            df: Cleaned DataFrame from parser
        """
        self.df = df
        self._validate_dataframe()

    def yoy_comparison(
        self,
        commodity: str,
        current_year: int,
        previous_year: int,
        geography: str = "US"
    ) -> Dict:
        """
        Year-over-year comparison

        Args:
            commodity: Commodity name
            current_year: Current year
            previous_year: Previous year
            geography: Geography level (US, STATE, etc)

        Returns:
            Dict with comparison results:
                - production_current
                - production_previous
                - change_absolute
                - change_percent
                - decomposition (if production)
                - interpretation

        Example:
            >>> analyzer.yoy_comparison("CORN", 2023, 2022)
            {'production_current': 15.3, 'change_percent': 11.7, ...}
        """
        # Filter data
        df_current = self.df[
            (self.df['commodity'] == commodity) &
            (self.df['year'] == current_year) &
            (self.df['geography'] == geography)
        ]

        df_previous = self.df[
            (self.df['commodity'] == commodity) &
            (self.df['year'] == previous_year) &
            (self.df['geography'] == geography)
        ]

        if len(df_current) == 0 or len(df_previous) == 0:
            raise ValueError(f"Data not found for {commodity} in {current_year} or {previous_year}")

        # Extract values
        prod_curr = df_current['production'].iloc[0]
        prod_prev = df_previous['production'].iloc[0]

        # Calculate changes
        change_abs = prod_curr - prod_prev
        change_pct = (change_abs / prod_prev) * 100

        # Decomposition (if has area and yield)
        decomp = None
        if 'area' in df_current.columns and 'yield' in df_current.columns:
            decomp = self._decompose_growth(df_current, df_previous)

        # Interpretation
        if abs(change_pct) < 2:
            interpretation = "stable"
        elif change_pct > 10:
            interpretation = "significant_increase"
        elif change_pct > 2:
            interpretation = "moderate_increase"
        elif change_pct < -10:
            interpretation = "significant_decrease"
        else:
            interpretation = "moderate_decrease"

        return {
            "commodity": commodity,
            "geography": geography,
            "year_current": current_year,
            "year_previous": previous_year,
            "production_current": round(prod_curr, 1),
            "production_previous": round(prod_prev, 1),
            "change_absolute": round(change_abs, 1),
            "change_percent": round(change_pct, 1),
            "decomposition": decomp,
            "interpretation": interpretation
        }

    def _decompose_growth(self, df_current, df_previous) -> Dict:
        """Area vs yield decomposition"""
        area_curr = df_current['area'].iloc[0]
        area_prev = df_previous['area'].iloc[0]
        yield_curr = df_current['yield'].iloc[0]
        yield_prev = df_previous['yield'].iloc[0]

        area_change_pct = ((area_curr - area_prev) / area_prev) * 100
        yield_change_pct = ((yield_curr - yield_prev) / yield_prev) * 100

        prod_change_pct = ((df_current['production'].iloc[0] - df_previous['production'].iloc[0]) /
                          df_previous['production'].iloc[0]) * 100

        if prod_change_pct != 0:
            area_contrib = (area_change_pct / prod_change_pct) * 100
            yield_contrib = (yield_change_pct / prod_change_pct) * 100
        else:
            area_contrib = yield_contrib = 0

        return {
            "area_change_pct": round(area_change_pct, 1),
            "yield_change_pct": round(yield_change_pct, 1),
            "area_contribution": round(area_contrib, 1),
            "yield_contribution": round(yield_contrib, 1),
            "growth_type": "intensive" if yield_contrib > 60 else
                          "extensive" if area_contrib > 60 else
                          "balanced"
        }

    # Implement ALL other analyses
    # state_ranking(), trend_analysis(), etc.
    # [Complete code for each one]
```

**Size**: 400-500 lines

## Implementation: SKILL.md

### Mandatory Structure

```markdown
---
name: [agent-name]
description: [description of 150-250 words with all keywords]
---

# [Agent Name]

[Introduction of 2-3 paragraphs explaining what the agent is]

## When to Use This Skill

Claude should automatically activate when user:

✅ [Trigger 1 with examples]
✅ [Trigger 2 with examples]
✅ [Trigger 3 with examples]

## Data Source

**API**: [Name]
**URL**: [URL]
**Documentation**: [link]
**Authentication**: [how to get key]

[API summary in 1-2 paragraphs]

See `references/api-guide.md` for complete details.

## Workflows

### Workflow 1: [Name]

**When to execute**: [trigger conditions]

**Step-by-step**:

1. **Identify parameters**
   - [what to extract from user's question]

2. **Fetch data**
   ```bash
   python scripts/fetch_[source].py \
     --param1 value1 \
     --output data/raw/file.json
   ```

3. **Parse data**
   ```bash
   python scripts/parse_[source].py \
     --input data/raw/file.json \
     --output data/processed/file.csv
   ```

4. **Analyze**
   ```bash
   python scripts/analyze_[source].py \
     --input data/processed/file.csv \
     --analysis yoy \
     --output data/analysis/result.json
   ```

5. **Interpret results**
   [How to interpret the result JSON]

**Complete example**:

Question: "[example]"

[Step-by-step flow with commands and outputs]

Answer: "[expected response]"

### Workflow 2: [Name]
[...]

[Repeat for all main workflows]

## Available Scripts

### scripts/fetch_[source].py

**Function**: Make API requests

**Inputs**:
- `--param1`: [description]
- `--param2`: [description]

**Output**: JSON in `data/raw/`

**Example**:
```bash
python scripts/fetch_[source].py --commodity CORN --year 2023
```

**Error handling**:
- API unavailable: [action]
- Rate limit: [action]
- [other errors]

### scripts/parse_[source].py

[Same level of detail...]

### scripts/analyze_[source].py

**Available analyses**:
- `--analysis yoy`: Year-over-year comparison
- `--analysis ranking`: State ranking
- [complete list]

[Detail each one...]

## Available Analyses

### 1. YoY Comparison

**Objective**: [...]
**When to use**: [...]
**Methodology**: [...]
**Output**: [...]
**Interpretation**: [...]

See `references/analysis-methods.md` for detailed formulas.

### 2. State Ranking

[...]

[For all analyses]

## Error Handling

### Error: API Unavailable

**Symptom**: [...]
**Cause**: [...]
**Automatic action**: [...]
**Fallback**: [...]
**User message**: [...]

### Error: Rate Limit Exceeded

[...]

[All expected errors]

## Mandatory Validations

1. **API key validation**: [...]
2. **Data validation**: [...]
3. **Consistency checks**: [...]

## Performance and Cache

**Cache strategy**:
- Historical data: [TTL]
- Current data: [TTL]
- Justification: [...]

**Rate limiting**:
- Limit: [number]
- Implementation: [...]

## References

- `references/api-guide.md`: Complete API documentation
- `references/analysis-methods.md`: Detailed methodologies
- `references/troubleshooting.md`: Troubleshooting guide

## Keywords for Detection

[Complete keyword list organized by category]

## Usage Examples

### Example 1: [Scenario]

**Question**: "[exact question]"

**Internal flow**: [commands executed]

**Answer**: "[complete and formatted answer]"

### Examples 2-5: [...]

[Minimum 5 complete examples]
```

**Size**: 5000-7000 words

## File Creation

**Use Write tool for each file**:

```bash
# Creation order (UPDATED with marketplace.json):
1. ✅ Write: .claude-plugin/marketplace.json  ← MANDATORY FIRST!
2. Write: SKILL.md (frontmatter with description)
3. Write: DECISIONS.md
4. Write: scripts/utils/cache_manager.py
5. Write: scripts/utils/rate_limiter.py
6. Write: scripts/utils/validators.py
7. Write: scripts/fetch_[source].py
8. Write: scripts/parse_[source].py
9. Write: scripts/analyze_[source].py
10. Write: references/api-guide.md
11. Write: references/analysis-methods.md
12. Write: references/troubleshooting.md
13. Write: assets/config.json
14. Write: assets/metadata.json (if needed)
15. Write: README.md
16. Write: requirements.txt
17. Write: .gitignore
18. Bash: chmod +x scripts/*.py

# ⚠️ CRITICAL: marketplace.json ALWAYS FIRST!
# Reason: Without it, skill cannot be installed
```

## Post-Implementation Validation

### Verify Each File

**Python scripts**:
```bash
# Syntax check
python -m py_compile scripts/fetch_*.py
python -m py_compile scripts/parse_*.py
python -m py_compile scripts/analyze_*.py

# Import check (mental - verify imports make sense)
```

**JSONs**:
```bash
# Validate syntax
python -c "import json; json.load(open('assets/config.json'))"
```

**Markdown**:
- [ ] SKILL.md has valid frontmatter
- [ ] No broken links
- [ ] Code blocks have syntax highlighting

### Final Checklist

- [ ] All files created (15+ files)
- [ ] No TODO or pass
- [ ] Code has correct imports
- [ ] JSONs are valid
- [ ] References have useful content
- [ ] README has complete instructions
- [ ] DECISIONS.md documents choices

## Final Communication to User

After creating everything:

```
✅ AGENT CREATED SUCCESSFULLY!

📂 Location: ./[agent-name]/

📊 Statistics:
- SKILL.md: [N] words
- Python code: [N] lines
- References: [N] words
- Total files: [N]

🎯 Main Decisions:
- API: [name] ([short justification])
- Analyses: [list]
- Structure: [type]

💰 Estimated ROI:
- Before: [X]h/[frequency]
- After: [Y]min/[frequency]
- Savings: [%]

🚀 NEXT STEPS:

1. Get API key:
   [Instructions or link]

2. Configure:
   export API_KEY_VAR="your_key"

3. Install:
   /plugin marketplace add ./[agent-name]

4. Test:
   "[example 1]"
   "[example 2]"

📖 See README.md for complete instructions.
📋 See DECISIONS.md for decision justifications.
```

## Phase 5 Checklist

- [ ] Directory structure created (including .claude-plugin/)
- [ ] ✅ **marketplace.json created (MANDATORY!)**
- [ ] **marketplace.json validated (syntax + description identical to SKILL.md)**
- [ ] SKILL.md created with correct frontmatter
- [ ] DECISIONS.md created
- [ ] Utils implemented (functional code)
- [ ] Main scripts implemented (functional code)
- [ ] SKILL.md written (5000+ words)
- [ ] References written (useful content)
- [ ] Assets created (valid JSONs)
- [ ] README.md written
- [ ] requirements.txt created
- [ ] Syntax validation passed
- [ ] No TODO or placeholder
- [ ] **Test installation**: `/plugin marketplace add ./agent-name`
- [ ] Final message to user formatted
