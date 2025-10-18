# Mandatory Quality Standards

## Fundamental Principles

**Production-Ready, Not Prototype**
- Code must work without modifications
- Doesn't need "now implement X"
- Can be used immediately

**Functional, Not Placeholder**
- Complete code in all functions
- No TODO, pass, NotImplementedError
- Robust error handling

**Useful, Not Generic**
- Specific and detailed content
- Concrete examples, not abstract
- Not just external links

---

## Standards by File Type

### Python Scripts

#### ✅ MANDATORY

**1. Complete structure**:
```python
#!/usr/bin/env python3
"""Module docstring"""

# Imports
import ...

# Constants
CONST = value

# Classes/Functions
class/def ...

# Main
def main():
    ...

if __name__ == "__main__":
    main()
```

**2. Docstrings**:
- Module docstring: 3-5 lines
- Class docstring: Description + Example
- Method docstring: Args, Returns, Raises, Example

**3. Type hints**:
```python
def function(param1: str, param2: int = 10) -> Dict[str, Any]:
    ...
```

**4. Error handling**:
```python
try:
    result = risky_operation()
except SpecificError as e:
    # Handle specifically
    log_error(e)
    raise CustomError(f"Context: {e}")
```

**5. Validations**:
```python
def process(data: Dict) -> pd.DataFrame:
    # Validate input
    if not data:
        raise ValueError("Data cannot be empty")

    if 'required_field' not in data:
        raise ValueError("Missing required field")

    # Process
    ...

    # Validate output
    assert len(result) > 0, "Result cannot be empty"
    assert result['value'].notna().all(), "No null values allowed"

    return result
```

**6. Appropriate logging**:
```python
import logging

logger = logging.getLogger(__name__)

def fetch_data():
    logger.info("Fetching data from API...")
    # ...
    logger.debug(f"Received {len(data)} records")
    # ...
    logger.error(f"API error: {e}")
```

#### ❌ FORBIDDEN

```python
# ❌ DON'T DO THIS:

def analyze():
    # TODO: implement analysis
    pass

def process(data):  # ❌ No type hints
    # ❌ No docstring
    result = data  # ❌ No real logic
    return result  # ❌ No validation

def fetch_api(url):
    response = requests.get(url)  # ❌ No timeout
    return response.json()  # ❌ No error handling
```

#### ✅ DO THIS:

```python
def analyze_yoy(df: pd.DataFrame, commodity: str, year1: int, year2: int) -> Dict:
    """
    Perform year-over-year analysis

    Args:
        df: DataFrame with parsed data
        commodity: Commodity name (e.g., "CORN")
        year1: Current year
        year2: Previous year

    Returns:
        Dict with keys:
            - production_current: float
            - production_previous: float
            - change_percent: float
            - interpretation: str

    Raises:
        ValueError: If data not found for specified years
        DataQualityError: If data fails validation

    Example:
        >>> analyze_yoy(df, "CORN", 2023, 2022)
        {'production_current': 15.3, 'change_percent': 11.7, ...}
    """
    # Validate inputs
    if commodity not in df['commodity'].unique():
        raise ValueError(f"Commodity {commodity} not found in data")

    # Filter data
    df1 = df[(df['commodity'] == commodity) & (df['year'] == year1)]
    df2 = df[(df['commodity'] == commodity) & (df['year'] == year2)]

    if len(df1) == 0 or len(df2) == 0:
        raise ValueError(f"Data not found for {commodity} in {year1} or {year2}")

    # Extract values
    prod1 = df1['production'].iloc[0]
    prod2 = df2['production'].iloc[0]

    # Calculate
    change = prod1 - prod2
    change_pct = (change / prod2) * 100

    # Interpret
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

    # Return
    return {
        "commodity": commodity,
        "production_current": round(prod1, 1),
        "production_previous": round(prod2, 1),
        "change_absolute": round(change, 1),
        "change_percent": round(change_pct, 1),
        "interpretation": interpretation
    }
```

---

### SKILL.md

#### ✅ MANDATORY

**1. Valid frontmatter**:
```yaml
---
name: agent-name
description: [150-250 words with keywords]
---
```

**2. Size**: 5000-7000 words

**3. Mandatory sections**:
- When to use (specific triggers)
- Data source (detailed API)
- Workflows (complete step-by-step)
- Scripts (each one explained)
- Analyses (methodologies)
- Errors (complete handling)
- Validations (mandatory)
- Keywords (complete list)
- Examples (5+ complete)

**4. Detailed workflows**:

✅ **GOOD**:
```markdown
### Workflow: YoY Comparison

1. **Identify question parameters**
   - Commodity: [extract from question]
   - Years: Current vs previous (or specified)

2. **Fetch data**
   ```bash
   python scripts/fetch_nass.py \
     --commodity CORN \
     --years 2023,2022 \
     --output data/raw/corn_2023_2022.json
   ```

3. **Parse**
   ```bash
   python scripts/parse_nass.py \
     --input data/raw/corn_2023_2022.json \
     --output data/processed/corn.csv
   ```

4. **Analyze**
   ```bash
   python scripts/analyze_nass.py \
     --input data/processed/corn.csv \
     --analysis yoy \
     --commodity CORN \
     --year1 2023 \
     --year2 2022 \
     --output data/analysis/corn_yoy.json
   ```

5. **Interpret results**

   File `data/analysis/corn_yoy.json` contains:
   ```json
   {
     "production_current": 15.3,
     "change_percent": 11.7,
     "interpretation": "significant_increase"
   }
   ```

   Respond to user:
   "Corn production grew 11.7% in 2023..."
```

❌ **BAD**:
```markdown
### Workflow: Comparison

1. Get data
2. Compare
3. Return result
```

**5. Complete examples**:

✅ **GOOD**:
```markdown
### Example 1: YoY Comparison

**Question**: "How's corn production compared to last year?"

**Executed flow**:
[Specific commands with outputs]

**Generated answer**:
"Corn production in 2023 is 15.3 billion bushels,
growth of 11.7% vs 2022 (13.7 billion). Growth
comes mainly from area increase (+8%) with stable yield."
```

❌ **BAD**:
```markdown
### Example: Comparison

User asks about comparison. Agent compares and responds.
```

#### ❌ FORBIDDEN

- Empty sections
- "See documentation"
- Workflows without specific commands
- Generic examples

---

### References

#### ✅ MANDATORY

**1. Useful and self-contained content**:

✅ **GOOD** (references/api-guide.md):
```markdown
## Endpoint: Get Production Data

**URL**: `GET https://quickstats.nass.usda.gov/api/api_GET/`

**Parameters**:
- `commodity_desc`: Commodity name
  - Example: "CORN", "SOYBEANS"
  - Case-sensitive
- `year`: Desired year
  - Example: 2023
  - Range: 1866-present

**Complete request example**:
```bash
curl -H "X-Api-Key: YOUR_KEY" \
  "https://quickstats.nass.usda.gov/api/api_GET/?commodity_desc=CORN&year=2023&format=JSON"
```

**Expected response**:
```json
{
  "data": [
    {
      "year": 2023,
      "commodity_desc": "CORN",
      "value": "15,300,000,000",
      "unit_desc": "BU"
    }
  ]
}
```

**Important fields**:
- `value`: Comes as STRING with commas
  - Solution: `value.replace(',', '')`
  - Convert to float after
```

❌ **BAD**:
```markdown
## API Endpoint

For details on how to use the API, consult the official documentation at:
https://quickstats.nass.usda.gov/api

[End of file]
```

**2. Adequate size**:
- API guide: 1500-2000 words
- Analysis methods: 2000-3000 words
- Troubleshooting: 1000-1500 words

**3. Concrete examples**:
- Always include examples with real values
- Executable code blocks
- Expected outputs

#### ❌ FORBIDDEN

- "For more information, see [link]"
- Sections with only 2-3 lines
- Lists without details
- Circular references ("see other doc that sees other doc")

---

### Assets (Configs)

#### ✅ MANDATORY

**1. Syntactically valid JSON**:
```bash
# ALWAYS validate:
python -c "import json; json.load(open('config.json'))"
```

**2. Real values**:

✅ **GOOD**:
```json
{
  "api": {
    "base_url": "https://quickstats.nass.usda.gov/api",
    "api_key_env": "NASS_API_KEY",
    "_instructions": "Get free API key from: https://quickstats.nass.usda.gov/api#registration",
    "rate_limit_per_day": 1000,
    "timeout_seconds": 30
  }
}
```

❌ **BAD**:
```json
{
  "api": {
    "base_url": "YOUR_API_URL_HERE",
    "api_key": "YOUR_KEY_HERE"
  }
}
```

**3. Inline comments** (using `_comment` or `_note`):
```json
{
  "_comment": "Differentiated TTL by data type",
  "cache": {
    "ttl_historical_days": 365,
    "_note_historical": "Historical data doesn't change",
    "ttl_current_days": 7,
    "_note_current": "Current year data may be revised"
  }
}
```

---

### README.md

#### ✅ MANDATORY

**1. Complete installation instructions**:

✅ **GOOD**:
```markdown
## Installation

### 1. Get API Key (Free)

1. Access https://quickstats.nass.usda.gov/api#registration
2. Fill form:
   - Name: [your name]
   - Email: [your email]
   - Purpose: "Personal research"
3. Click "Submit"
4. You'll receive email with API key in ~1 minute
5. Key format: `A1B2C3D4-E5F6-G7H8-I9J0-K1L2M3N4O5P6`

### 2. Configure Environment

**Option A - Export** (temporary):
```bash
export NASS_API_KEY="your_key_here"
```

**Option B - .bashrc/.zshrc** (permanent):
```bash
echo 'export NASS_API_KEY="your_key_here"' >> ~/.bashrc
source ~/.bashrc
```

**Option C - .env file** (per project):
```bash
echo "NASS_API_KEY=your_key_here" > .env
```

### 3. Install Dependencies

```bash
cd nass-usda-agriculture
pip install -r requirements.txt
```

Requirements:
- requests
- pandas
- numpy
```

❌ **BAD**:
```markdown
## Installation

1. Get API key from the official website
2. Configure environment
3. Install dependencies
4. Done!
```

**2. Concrete usage examples**:

✅ **GOOD**:
```markdown
## Examples

### Example 1: Current Production

```
You: "What's US corn production in 2023?"

Claude: "Corn production in 2023 was 15.3 billion
bushels (389 million metric tons)..."
```

### Example 2: YoY Comparison

```
You: "Compare soybeans this year vs last year"

Claude: "Soybean production in 2023 is 2.6% below 2022:
- 2023: 4.165 billion bushels
- 2022: 4.276 billion bushels
- Drop from area (-4.5%), yield improved (+0.8%)"
```

[3-5 more examples]
```

❌ **BAD**:
```markdown
## Usage

Ask questions about agriculture and the agent will respond.
```

**3. Specific troubleshooting**:

✅ **GOOD**:
```markdown
### Error: "NASS_API_KEY environment variable not found"

**Cause**: API key not configured

**Step-by-step solution**:
1. Verify key was obtained: https://...
2. Configure environment:
   ```bash
   export NASS_API_KEY="your_key_here"
   ```
3. Verify:
   ```bash
   echo $NASS_API_KEY
   ```
4. Should show your key
5. If doesn't work, restart terminal

**Still not working?**
- Check for extra spaces in key
- Verify key hasn't expired (validity: 1 year)
- Re-generate key if needed
```

---

## Quality Checklist

### Per Python Script

- [ ] Shebang: `#!/usr/bin/env python3`
- [ ] Module docstring (3-5 lines)
- [ ] Organized imports (stdlib, 3rd party, local)
- [ ] Constants at top (if applicable)
- [ ] Type hints in all public functions
- [ ] Docstrings in classes (description + attributes + example)
- [ ] Docstrings in methods (Args, Returns, Raises, Example)
- [ ] Error handling for risky operations
- [ ] Input validations
- [ ] Output validations
- [ ] Appropriate logging
- [ ] Main function with argparse
- [ ] if __name__ == "__main__"
- [ ] Functional code (no TODO/pass)
- [ ] Valid syntax (test: `python -m py_compile script.py`)

### Per SKILL.md

- [ ] Frontmatter with name and description
- [ ] Description 150-250 characters with keywords
- [ ] Size 5000+ words
- [ ] "When to Use" section with specific triggers
- [ ] "Data Source" section detailed
- [ ] Step-by-step workflows with commands
- [ ] Scripts explained individually
- [ ] Analyses documented (objective, methodology)
- [ ] Errors handled (all expected)
- [ ] Validations listed
- [ ] Performance/cache explained
- [ ] Complete keywords
- [ ] Complete examples (5+)

### Per Reference File

- [ ] 1000+ words
- [ ] Useful content (not just links)
- [ ] Concrete examples with real values
- [ ] Executable code blocks
- [ ] Well structured (headings, lists)
- [ ] No empty sections
- [ ] No "TODO: write"

### Per Asset (Config)

- [ ] Syntactically valid JSON (validate!)
- [ ] Real values (not "YOUR_X_HERE" without context)
- [ ] Inline comments (_comment, _note)
- [ ] Instructions for values user must fill
- [ ] Logical and organized structure

### Per README.md

- [ ] Step-by-step installation
- [ ] How to get API key (detailed)
- [ ] How to configure (3 options)
- [ ] How to install dependencies
- [ ] How to install in Claude Code
- [ ] Usage examples (5+)
- [ ] Troubleshooting (10+ problems)
- [ ] License
- [ ] Contact/contribution (if applicable)

### Complete Agent

- [ ] DECISIONS.md documents all choices
- [ ] **VERSION** file created (e.g. 1.0.0)
- [ ] **CHANGELOG.md** created with complete v1.0.0 entry
- [ ] **INSTALACAO.md** with complete didactic tutorial
- [ ] **comprehensive_{domain}_report()** implemented
- [ ] marketplace.json with version field
- [ ] 18+ files created
- [ ] ~1500+ lines of Python code
- [ ] ~10,000+ words of documentation
- [ ] 2+ configs
- [ ] requirements.txt
- [ ] .gitignore (if needed)
- [ ] No placeholder/TODO
- [ ] Valid syntax (Python, JSON, YAML)
- [ ] Ready to use (production-ready)

---

## Quality Examples

### Example: Error Handling

❌ **BAD**:
```python
def fetch(url):
    return requests.get(url).json()
```

✅ **GOOD**:
```python
def fetch(url: str, timeout: int = 30) -> Dict:
    """
    Fetch data from URL with error handling

    Args:
        url: URL to fetch
        timeout: Timeout in seconds

    Returns:
        JSON response as dict

    Raises:
        NetworkError: If connection fails
        TimeoutError: If request times out
        APIError: If API returns error
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()

        data = response.json()

        if 'error' in data:
            raise APIError(f"API error: {data['error']}")

        return data

    except requests.Timeout:
        raise TimeoutError(f"Request timed out after {timeout}s")

    except requests.ConnectionError as e:
        raise NetworkError(f"Connection failed: {e}")

    except requests.HTTPError as e:
        if e.response.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        else:
            raise APIError(f"HTTP {e.response.status_code}: {e}")
```

### Example: Validations

❌ **BAD**:
```python
def parse(data):
    df = pd.DataFrame(data)
    return df
```

✅ **GOOD**:
```python
def parse(data: List[Dict]) -> pd.DataFrame:
    """Parse and validate data"""

    # Validate input
    if not data:
        raise ValueError("Data cannot be empty")

    if not isinstance(data, list):
        raise TypeError(f"Expected list, got {type(data)}")

    # Parse
    df = pd.DataFrame(data)

    # Validate schema
    required_cols = ['year', 'commodity', 'value']
    missing = set(required_cols) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Validate types
    df['year'] = pd.to_numeric(df['year'], errors='raise')
    df['value'] = pd.to_numeric(df['value'], errors='raise')

    # Validate ranges
    current_year = datetime.now().year
    if (df['year'] > current_year).any():
        raise ValueError(f"Future years found (max allowed: {current_year})")

    if (df['value'] < 0).any():
        raise ValueError("Negative values found")

    # Validate no duplicates
    if df.duplicated(subset=['year', 'commodity']).any():
        raise ValueError("Duplicate records found")

    return df
```

### Example: Docstrings

❌ **BAD**:
```python
def analyze(df, commodity):
    """Analyze data"""
    # ...
```

✅ **GOOD**:
```python
def analyze_yoy(
    df: pd.DataFrame,
    commodity: str,
    year1: int,
    year2: int
) -> Dict[str, Any]:
    """
    Perform year-over-year comparison analysis

    Compares production, area, and yield between two years
    and decomposes growth into area vs yield contributions.

    Args:
        df: DataFrame with columns ['year', 'commodity', 'production', 'area', 'yield']
        commodity: Commodity name (e.g., "CORN", "SOYBEANS")
        year1: Current year to compare
        year2: Previous year to compare against

    Returns:
        Dict containing:
            - production_current (float): Production in year1 (million units)
            - production_previous (float): Production in year2
            - change_absolute (float): Absolute change
            - change_percent (float): Percent change
            - decomposition (dict): Area vs yield contribution
            - interpretation (str): "increase", "decrease", or "stable"

    Raises:
        ValueError: If commodity not found in data
        ValueError: If either year not found in data
        DataQualityError: If production != area * yield (tolerance > 1%)

    Example:
        >>> df = pd.DataFrame([
        ...     {'year': 2023, 'commodity': 'CORN', 'production': 15.3, 'area': 94.6, 'yield': 177},
        ...     {'year': 2022, 'commodity': 'CORN', 'production': 13.7, 'area': 89.2, 'yield': 173}
        ... ])
        >>> result = analyze_yoy(df, "CORN", 2023, 2022)
        >>> result['change_percent']
        11.7
    """
    # [Complete implementation]
```

---

## Anti-Patterns

### Anti-Pattern 1: Partial Implementation

❌ **NO**:
```python
def yoy_comparison(df, commodity, year1, year2):
    # Implement YoY comparison
    pass

def state_ranking(df, commodity):
    # TODO: implement ranking
    raise NotImplementedError()
```

✅ **YES**:
```python
# [Complete and functional code for BOTH functions]
```

### Anti-Pattern 2: Empty References

❌ **NO**:
```markdown
# Analysis Methods

## YoY Comparison

This method compares two years.

## Ranking

This method ranks states.
```

✅ **YES**:
```markdown
# Analysis Methods

## YoY Comparison

### Objective
Compare metrics between current and previous year...

### Detailed Methodology

**Formulas**:
```
Δ X = X(t) - X(t-1)
Δ X% = (Δ X / X(t-1)) × 100
```

**Decomposition** (for production):
[Complete mathematics]

**Interpretation**:
- |Δ| < 2%: Stable
- Δ > 10%: Significant increase
[...]

### Validations
[List]

### Complete Numerical Example
[With real values]
```

### Anti-Pattern 3: Useless Configs

❌ **NO**:
```json
{
  "api_url": "INSERT_URL",
  "api_key": "INSERT_KEY"
}
```

✅ **YES**:
```json
{
  "_comment": "Configuration for NASS USDA Agent",
  "api": {
    "base_url": "https://quickstats.nass.usda.gov/api",
    "_note": "This is the official USDA NASS API base URL",
    "api_key_env": "NASS_API_KEY",
    "_key_instructions": "Get free API key from: https://quickstats.nass.usda.gov/api#registration"
  }
}
```

---

## Final Validation

Before delivering to user, verify:

### Sanity Test

```bash
# 1. Python syntax
find scripts -name "*.py" -exec python -m py_compile {} \;

# 2. JSON syntax
python -c "import json; json.load(open('assets/config.json'))"

# 3. Imports make sense
grep -r "^import\|^from" scripts/*.py | sort | uniq
# Verify all libs are: stdlib, requests, pandas, numpy
# No imports of uninstalled libs

# 4. SKILL.md has frontmatter
head -5 SKILL.md | grep "^---$"

# 5. SKILL.md size
wc -w SKILL.md
# Should be > 5000 words
```

### Final Checklist

- [ ] Syntax check passed (Python, JSON)
- [ ] No import of non-existent lib
- [ ] No TODO or pass
- [ ] SKILL.md > 5000 words
- [ ] References with content
- [ ] README with complete instructions
- [ ] DECISIONS.md created
- [ ] requirements.txt created
