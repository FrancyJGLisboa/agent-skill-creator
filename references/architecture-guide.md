# Architecture Decision Guide

**Version:** 6.0
**Purpose:** Comprehensive guide for choosing the right architecture when creating agent skills, including directory structures, naming conventions, sizing patterns, and performance strategies.

---

## 1. Architecture Decision Framework

Before creating any skill, determine whether it should be a **Simple Skill** or a **Complex Suite**. This decision drives the entire directory structure, file organization, and whether a `marketplace.json` is needed.

### 1.1 Decision Criteria

| Factor | Simple Skill | Complex Suite |
|--------|-------------|---------------|
| **Number of workflows** | 1-2 related workflows | 3+ distinct workflows |
| **Code complexity** | <1000 lines total | >2000 lines total |
| **SKILL.md files** | 1 | Multiple (one per component) |
| **Maintenance scope** | Single developer | Team or multi-concern |
| **Domain breadth** | Single domain focus | Spans multiple sub-domains |
| **Deployment** | Install as one unit | Components may be used independently |
| **marketplace.json** | **Not needed** | Optional (official fields only) |

### 1.2 Decision Flowchart

Follow this logic sequentially:

```
START
  |
  v
How many distinct workflows does this skill address?
  |
  +-- 1-2 workflows --> Does the total code exceed 2000 lines?
  |                       |
  |                       +-- No  --> SIMPLE SKILL
  |                       +-- Yes --> Can it be split into independent sub-skills?
  |                                     |
  |                                     +-- No  --> SIMPLE SKILL (large)
  |                                     +-- Yes --> COMPLEX SUITE
  |
  +-- 3+ workflows --> Are the workflows tightly coupled?
                        |
                        +-- Yes (shared state/data) --> SIMPLE SKILL (organized)
                        +-- No  (independent concerns) --> COMPLEX SUITE
```

### 1.3 Decision Examples

| User Request | Decision | Rationale |
|-------------|----------|-----------|
| "Analyze stock prices with technical indicators" | Simple Skill | Single domain, 1-2 workflows (fetch + analyze) |
| "Format markdown tables" | Simple Skill | Single workflow, <500 lines |
| "Full-stack web dev with frontend, backend, deployment" | Complex Suite | 3 independent sub-domains |
| "USDA agriculture data with 6 analysis types" | Simple Skill (organized) | Multiple analyses but single domain, shared data pipeline |
| "Financial suite: stock analysis, portfolio tracking, tax reporting" | Complex Suite | 3 distinct workflows, each usable independently |

---

## 2. Simple Skill Structure

A Simple Skill is a single, self-contained agent skill that follows the Agent Skills Open Standard. It has one SKILL.md file and no `marketplace.json`.

### 2.1 Standard Directory Layout

```
skill-name/
├── SKILL.md          # <500 lines, spec-compliant frontmatter
├── scripts/          # Functional Python code
├── references/       # Detailed documentation (loaded on demand)
├── assets/           # Templates, schemas, data files
├── install.sh        # Cross-platform auto-detect installer
└── README.md         # Multi-platform installation instructions
```

**Key rule:** NO `.claude-plugin/marketplace.json` for simple skills. The SKILL.md file is the sole manifest and activation mechanism.

### 2.2 SKILL.md Frontmatter (Required)

```yaml
---
name: skill-name            # 1-64 chars, lowercase + hyphens, must match directory
description: >-             # 1-1024 chars, activation keywords included
  Description with domain keywords for agent discovery...
license: MIT                # or appropriate license
metadata:
  author: Author Name
  version: 1.0.0
compatibility: >-           # optional, use when platform-specific features exist
  Works on all platforms supporting the SKILL.md standard.
---
```

### 2.3 File Responsibilities

| File/Directory | Purpose | Required? |
|---------------|---------|-----------|
| `SKILL.md` | Primary skill definition, frontmatter, instructions | Yes |
| `scripts/` | Executable Python code (functional, no placeholders) | Yes (if skill has code) |
| `references/` | Detailed documentation, API guides, methodology docs | Recommended |
| `assets/` | Configuration files, templates, schemas, static data | Optional |
| `install.sh` | Cross-platform installer script | Yes |
| `README.md` | Installation instructions for 5+ platforms | Yes |

### 2.4 Why No marketplace.json for Simple Skills

Per the Agent Skills Open Standard and FR-005:

- SKILL.md is the universal discovery mechanism across all 26+ platforms
- `marketplace.json` is a Claude Code-specific plugin manifest, not part of the standard
- Simple skills activate via their SKILL.md `description` field alone
- Adding `marketplace.json` to a simple skill creates a non-standard structure that may confuse other platforms
- Skills placed in `~/.claude/skills/` or `.claude/skills/` are discovered automatically by Claude Code without `marketplace.json`

---

## 3. Complex Suite Structure

A Complex Suite bundles multiple related but independently usable skills under a single parent directory. It optionally includes a `marketplace.json` for Claude Code plugin registration.

### 3.1 Standard Directory Layout

```
suite-name/
├── .claude-plugin/
│   └── marketplace.json    # ONLY official fields (see below)
├── component-1/
│   ├── SKILL.md            # Independent skill definition
│   ├── scripts/
│   └── references/
├── component-2/
│   ├── SKILL.md            # Independent skill definition
│   ├── scripts/
│   └── references/
├── shared/                 # Shared utilities, data, config
│   ├── utils.py
│   └── config.json
├── install.sh              # Installs all components
└── README.md               # Suite-level documentation
```

### 3.2 marketplace.json Schema (Official Fields Only)

When a Complex Suite includes a `marketplace.json`, it must contain **only** the official Claude Code fields. No custom or non-standard fields are permitted.

```json
{
  "name": "suite-name",
  "plugins": [
    {
      "name": "component-1",
      "description": "What component-1 does",
      "source": "component-1/SKILL.md",
      "skills": ["component-1"]
    },
    {
      "name": "component-2",
      "description": "What component-2 does",
      "source": "component-2/SKILL.md",
      "skills": ["component-2"]
    }
  ]
}
```

**Allowed top-level fields:**
- `name` (string): The suite name
- `plugins` (array): List of plugin entries

**Allowed fields per plugin entry:**
- `name` (string): Component skill name
- `description` (string): What the component does
- `source` (string): Relative path to the component's SKILL.md
- `skills` (array of strings): Skill identifiers

**Forbidden fields** (non-standard, will cause validation failure):
- `version` -- use `metadata.version` in SKILL.md instead
- `author` -- use `metadata.author` in SKILL.md instead
- `repository` -- not part of the official schema
- `tags` -- not part of the official schema
- Any other custom fields

### 3.3 When to Use marketplace.json

| Scenario | Include marketplace.json? |
|----------|--------------------------|
| Simple skill (1 SKILL.md) | No |
| Complex suite for Claude Code distribution | Yes (optional) |
| Complex suite targeting only non-Claude platforms | No |
| Suite where components must be independently discoverable in Claude Code | Yes |

### 3.4 Component Independence

Each component in a Complex Suite should be independently functional:

- Each component has its own `SKILL.md` with valid frontmatter
- Each component can be installed separately if extracted from the suite
- Shared resources in `shared/` are optional enhancements, not hard dependencies
- Each component's `name` field matches its directory name

---

## 4. Naming Convention

All skill and suite names follow standard kebab-case per the Agent Skills Open Standard.

### 4.1 Rules

| Rule | Requirement |
|------|-------------|
| Length | 1-64 characters |
| Characters | Lowercase letters (`a-z`), numbers (`0-9`), hyphens (`-`) |
| Format | kebab-case |
| First character | Must be a letter or number (not a hyphen) |
| Last character | Must be a letter or number (not a hyphen) |
| Consecutive hyphens | Not allowed (`my--skill` is invalid) |
| Directory match | The `name` field in SKILL.md frontmatter must exactly match the parent directory name |

### 4.2 The -skill Suffix

Every generated skill name **must end with `-skill`**. This suffix makes skills instantly discoverable across GitHub and GitLab organizations — teams can search `*-skill` and find every skill in their org.

**Suites** use the `-suite` suffix instead (e.g., `financial-suite`). Suites contain skills but are not themselves invoked as skills.

The previous `-cskill` suffix convention is **deprecated**. If encountered, replace with `-skill`.

### 4.3 Naming Pattern

```
{domain}-{objective}-skill
```

**Examples:**
- `stock-analyzer-skill` -- domain: stock, objective: analyzer
- `csv-data-cleaner-skill` -- domain: csv-data, objective: cleaner
- `sales-report-skill` -- domain: sales, objective: report
- `deploy-checklist-skill` -- domain: deploy, objective: checklist
- `financial-suite` -- complex suite (uses `-suite`, not `-skill`)

**Guidelines:**
- Must end with `-skill` (or `-suite` for multi-skill suites)
- Be descriptive but concise — aim for under 30 characters
- Include the primary domain for discoverability
- Avoid generic names like `my-skill` or `tool-1`

### 4.4 Naming Validation

A valid name passes all of these checks:

```python
import re

def validate_skill_name(name: str) -> tuple[bool, list[str]]:
    errors = []
    if not name:
        errors.append("Name is required")
    if len(name) > 64:
        errors.append(f"Name exceeds 64 chars ({len(name)})")
    if name != name.lower():
        errors.append("Name must be lowercase")
    if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$', name) and len(name) > 1:
        errors.append("Name must start/end with letter or number, contain only a-z, 0-9, hyphens")
    if '--' in name:
        errors.append("Consecutive hyphens not allowed")
    if name.endswith('-cskill'):
        errors.append("The -cskill suffix is deprecated; use -skill instead")
    if not name.endswith('-skill') and not name.endswith('-suite'):
        errors.append("Name must end with '-skill' (or '-suite' for multi-skill suites)")
    return (len(errors) == 0, errors)
```

---

## 5. Directory Sizing Patterns

Choose a sizing pattern based on the skill's complexity. These patterns apply to both Simple Skills and individual components within a Complex Suite.

### 5.1 Small Agent Pattern

**When to use:** Single workflow, 1-2 scripts, <500 total lines of code.

```
skill-name/
├── SKILL.md              # <200 lines
├── scripts/
│   └── main.py           # 200-400 lines, single entry point
├── references/
│   └── guide.md          # API docs, methodology
├── assets/
│   └── config.json       # Minimal configuration
├── install.sh
└── README.md
```

**Characteristics:**
- One main script handles the entire workflow
- Minimal configuration
- Single reference document
- Estimated total: 500-800 lines across all files

**Examples:** markdown-table-formatter, url-shortener, json-validator

### 5.2 Medium Agent Pattern

**When to use:** 2-3 workflows, 3-5 scripts, 500-2000 total lines of code.

```
skill-name/
├── SKILL.md              # 200-400 lines
├── scripts/
│   ├── fetch.py          # Data acquisition (200-300 lines)
│   ├── parse.py          # Data processing (150-200 lines)
│   ├── analyze.py        # Analysis logic (300-500 lines)
│   └── utils/
│       ├── cache.py      # Cache management (100-150 lines)
│       └── validators.py # Input validation (100-150 lines)
├── references/
│   ├── api-guide.md      # ~1500 words
│   └── methodology.md    # ~2000 words
├── assets/
│   └── config.json
├── install.sh
└── README.md
```

**Characteristics:**
- Separation of concerns: fetch, parse, analyze
- Utility modules for cross-cutting concerns (caching, validation)
- Multiple reference documents
- Estimated total: 1000-2500 lines across all files

**Examples:** stock-analyzer, weather-dashboard, csv-data-cleaner

### 5.3 Large Agent Pattern

**When to use:** 3+ workflows within a single domain, 6+ scripts, 2000+ total lines of code. Still a Simple Skill if all workflows share a single domain and data pipeline.

```
skill-name/
├── SKILL.md              # 400-500 lines (at the limit)
├── scripts/
│   ├── core/
│   │   ├── fetch_source_a.py    # 200-300 lines
│   │   ├── fetch_source_b.py    # 200-300 lines
│   │   ├── parse_source_a.py    # 150-200 lines
│   │   ├── parse_source_b.py    # 150-200 lines
│   │   └── analyze.py           # 400-600 lines
│   ├── models/
│   │   ├── forecasting.py       # 200-300 lines
│   │   └── ml_models.py         # 200-300 lines
│   └── utils/
│       ├── cache_manager.py     # 100-150 lines
│       ├── rate_limiter.py      # 100-150 lines
│       └── validators.py        # 100-150 lines
├── references/
│   ├── api/
│   │   ├── source-a-guide.md
│   │   └── source-b-guide.md
│   ├── methods/
│   │   └── analysis-methods.md
│   └── troubleshooting.md
├── assets/
│   ├── config.json
│   └── metadata.json
├── install.sh
└── README.md
```

**Characteristics:**
- Sub-directories within `scripts/` for organization (core, models, utils)
- Multiple data sources with dedicated fetch/parse scripts
- Dedicated models directory for analysis/ML logic
- Organized reference documentation
- Estimated total: 2500-5000 lines across all files

**Examples:** nass-usda-agriculture, conab-crop-yield-analysis, noaa-climate-analysis

### 5.4 Sizing Comparison Table

| Aspect | Small | Medium | Large |
|--------|-------|--------|-------|
| Total code lines | <500 | 500-2000 | 2000+ |
| Script files | 1 | 3-5 | 6+ |
| Script sub-dirs | None | `utils/` | `core/`, `models/`, `utils/` |
| Reference files | 1 | 2-3 | 4+ (may use sub-dirs) |
| Asset files | 0-1 | 1 | 2+ |
| SKILL.md length | <200 lines | 200-400 lines | 400-500 lines |
| Typical domains | Formatters, validators | Data analyzers, dashboards | Multi-source analysis, forecasting |

---

## 6. Performance Strategy

All generated skills should incorporate performance considerations appropriate to their size and use case.

### 6.1 Caching Strategy

Cache API responses and computed results to avoid redundant work and reduce API usage.

**Cache TTL Decision Logic:**

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| Historical data (past years) | 365 days (effectively permanent) | Historical data does not change |
| Current-year data | 7 days | May be revised/updated |
| Metadata (lists, enums) | 365 days | Rarely changes |
| Real-time data | 1-60 minutes | Freshness required |
| User preferences | Session-scoped | Per-execution only |

**Implementation Pattern:**

```python
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta

class FileCache:
    """Simple file-based cache with TTL support."""

    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key_path(self, key: str) -> Path:
        hashed = hashlib.sha256(key.encode()).hexdigest()[:16]
        return self.cache_dir / f"{hashed}.json"

    def get(self, key: str, ttl: timedelta) -> dict | None:
        path = self._key_path(key)
        if not path.exists():
            return None
        data = json.loads(path.read_text())
        cached_at = datetime.fromisoformat(data["cached_at"])
        if datetime.now() - cached_at > ttl:
            return None  # Expired
        return data["value"]

    def set(self, key: str, value: dict) -> None:
        path = self._key_path(key)
        path.write_text(json.dumps({
            "cached_at": datetime.now().isoformat(),
            "value": value
        }, indent=2))

    def get_or_fetch(self, key: str, ttl: timedelta, fetch_fn) -> dict:
        cached = self.get(key, ttl)
        if cached is not None:
            return cached
        value = fetch_fn()
        self.set(key, value)
        return value
```

**Cache Location:** Store cache files under `data/cache/` within the skill directory. This keeps cache local and avoids polluting system directories.

**Graceful Degradation:** If the cache file is corrupted or unreadable, log a warning and proceed without cache (fetch fresh data).

### 6.2 Rate Limiting Strategy

Protect against API rate limit exhaustion with proactive tracking.

**Rate Limiter Pattern:**

```python
import json
from pathlib import Path
from datetime import datetime, timedelta

class RateLimiter:
    """File-based rate limiter with persistent counter."""

    def __init__(
        self,
        max_requests: int,
        period: timedelta,
        counter_file: str = "data/cache/rate_limit.json"
    ):
        self.max_requests = max_requests
        self.period = period
        self.counter_file = Path(counter_file)
        self.counter_file.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict:
        if not self.counter_file.exists():
            return {"requests": [], "period_start": datetime.now().isoformat()}
        return json.loads(self.counter_file.read_text())

    def _save(self, data: dict) -> None:
        self.counter_file.write_text(json.dumps(data, indent=2))

    def _prune_old(self, data: dict) -> dict:
        cutoff = (datetime.now() - self.period).isoformat()
        data["requests"] = [r for r in data["requests"] if r > cutoff]
        return data

    def allow_request(self) -> bool:
        data = self._prune_old(self._load())
        count = len(data["requests"])
        if count >= self.max_requests:
            return False
        if count > self.max_requests * 0.9:
            remaining = self.max_requests - count
            print(f"WARNING: Rate limit nearly reached ({count}/{self.max_requests}), {remaining} requests remaining")
        return True

    def record_request(self) -> None:
        data = self._prune_old(self._load())
        data["requests"].append(datetime.now().isoformat())
        self._save(data)
```

**Rate Limit Configuration:** Define rate limits in `assets/config.json` so they can be adjusted without code changes:

```json
{
  "rate_limit": {
    "max_requests_per_day": 1000,
    "warn_threshold_percent": 90
  }
}
```

### 6.3 Optimization Techniques

**For Small Agents:**
- Keep it simple. A single script with basic caching is sufficient.
- Avoid premature optimization.

**For Medium Agents:**
- File-based caching for API responses.
- Rate limiter for external APIs.
- Lazy loading of reference data (only load when a specific analysis is requested).

**For Large Agents:**
- All Medium optimizations, plus:
- Batch API requests where the API supports it.
- Parallel processing for independent data sources (use `concurrent.futures`).
- Tiered caching: in-memory for hot data, file-based for cold data.
- Progress reporting for long-running operations.

**General Rules:**
- Never make the same API call twice in a single execution -- always check cache first.
- Use exponential backoff for transient API failures (start at 1 second, max 3 retries).
- Log all API calls with timestamps for debugging rate limit issues.
- Keep cached data in `data/cache/` and provide a way to clear it (`--clear-cache` flag or a function).

### 6.4 Error Handling Strategy

Every script must handle errors gracefully:

```python
import sys
from pathlib import Path

def safe_api_call(url: str, params: dict, retries: int = 3) -> dict:
    """Make an API call with retry logic and graceful error handling."""
    import urllib.request
    import urllib.error
    import json
    import time

    for attempt in range(retries):
        try:
            query = "&".join(f"{k}={v}" for k, v in params.items())
            full_url = f"{url}?{query}" if params else url
            req = urllib.request.Request(full_url)
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:  # Rate limited
                wait = 2 ** attempt
                print(f"Rate limited. Retrying in {wait}s...")
                time.sleep(wait)
            elif e.code >= 500:  # Server error
                wait = 2 ** attempt
                print(f"Server error ({e.code}). Retrying in {wait}s...")
                time.sleep(wait)
            else:
                print(f"HTTP error {e.code}: {e.reason}")
                return {"error": str(e), "code": e.code}
        except urllib.error.URLError as e:
            print(f"Network error: {e.reason}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                return {"error": f"Network error after {retries} attempts: {e.reason}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    return {"error": f"Failed after {retries} retries"}
```

### 6.5 SKILL.md Size Management

The SKILL.md body must stay under 500 lines. Use progressive disclosure:

| Content Type | Where It Goes |
|-------------|---------------|
| Activation triggers, overview, core workflow | `SKILL.md` body (required) |
| API documentation, endpoint details | `references/api-guide.md` |
| Analysis methodology, formulas | `references/methodology.md` |
| Troubleshooting, FAQs | `references/troubleshooting.md` |
| Domain context, terminology | `references/domain-context.md` |
| Configuration schema documentation | `references/config-guide.md` |

Reference content from SKILL.md using `See references/filename.md for details.` directives. The agent will load referenced files on demand, reducing initial context consumption.

---

## 7. When to Refactor a Growing Skill

Skills evolve. A simple skill that started at 500 lines can grow to 5000+ as the team adds analyses, data sources, and edge case handling. Recognize the signs early and refactor before the skill becomes unmaintainable.

### 7.1 Signs It's Time to Refactor

| Signal | What It Means |
|--------|--------------|
| SKILL.md approaching 500 lines | Body is stuffed — move content to references |
| Total code exceeding 3000 lines | Single-domain skill is becoming unwieldy |
| 3+ unrelated workflows emerging | The skill is doing too many different jobs |
| Different people maintaining different parts | Ownership boundaries need to be explicit |
| Users invoking the skill for fundamentally different tasks | The skill should be split into focused components |
| New data sources that don't share the existing pipeline | Independent fetch/parse/analyze chains = independent skills |

### 7.2 Refactoring Patterns

**Pattern 1: Extract to References (lightest touch)**

When the skill body is too long but the code is fine:

```
Before: SKILL.md at 480 lines with inline methodology docs
After:  SKILL.md at 250 lines, references/methodology.md with the detail
```

This is not a structural refactor — just progressive disclosure. Do this first.

**Pattern 2: Extract Utility Module**

When multiple scripts duplicate logic:

```
Before: fetch.py has cache logic, analyze.py has cache logic
After:  utils/cache.py extracted, both scripts import from it
```

**Pattern 3: Split by Domain (simple → suite)**

When the skill covers multiple independent domains:

```
Before:
  financial-analyzer/
    scripts/
      stock_analysis.py      # 800 lines
      portfolio_tracking.py   # 600 lines
      tax_reporting.py        # 500 lines

After:
  financial-suite/
    skills/
      stock-analyzer/         # Independent skill
      portfolio-tracker/      # Independent skill
      tax-reporter/           # Independent skill
    shared/
      market_data_client.py   # Shared API connection
```

**Pattern 4: Extract Shared Resources**

When converting to a suite, identify code that multiple components need:

1. API client code → `shared/api_client.py`
2. Common data models → `shared/models.py`
3. Utility functions (date handling, formatting) → `shared/utils.py`
4. Configuration → `shared/config.json`

### 7.3 Refactoring Decision Process

```
Is SKILL.md > 400 lines?
  → Yes: Extract to references (Pattern 1)
  → Still growing?
      ↓
Is total code > 3000 lines with 3+ unrelated workflows?
  → Yes: Split into suite (Pattern 3)
  → No, but code is duplicated across scripts?
      → Extract utilities (Pattern 2)
  → No: Keep as large simple skill — not everything needs to be a suite
```

**Critical rule**: Do not split prematurely. Three similar scripts in one domain is better than a suite with three trivially small components. Only split when the workflows are genuinely independent — different data sources, different users, different maintenance cadences.

### 7.4 Refactoring Checklist

- [ ] Identified which pattern applies (1-4)
- [ ] Each new component is independently functional
- [ ] Shared resources extracted to `shared/` (not duplicated)
- [ ] All SKILL.md files are <500 lines
- [ ] All component names follow kebab-case naming
- [ ] install.sh updated to handle new structure
- [ ] README.md updated with new structure
- [ ] Validation passes on all components

---

## 8. Cross-Component Communication in Suites

When a suite has multiple component skills, they need clear patterns for sharing code, data, and orchestration.

### 8.1 The shared/ Directory

The `shared/` directory contains code that multiple components use. It is **not** a component skill — it has no SKILL.md and is never invoked directly.

```
suite-name/
├── shared/
│   ├── api_client.py       # Shared API connection + authentication
│   ├── models.py           # Shared data classes and type definitions
│   ├── utils.py            # Common utilities (date formatting, etc.)
│   └── config.json         # Shared configuration
├── skills/
│   ├── component-a/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       └── analyze.py  # imports from ../../shared/api_client.py
│   └── component-b/
│       ├── SKILL.md
│       └── scripts/
│           └── report.py   # imports from ../../shared/api_client.py
```

### 8.2 Import Patterns

Components import from `shared/` using path manipulation:

```python
import sys
from pathlib import Path

# Add shared/ to path
_SUITE_ROOT = Path(__file__).resolve().parent.parent.parent
_SHARED_DIR = _SUITE_ROOT / "shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

from api_client import SuiteAPIClient
from utils import format_date, parse_currency
```

**Rules:**
- Always use `Path(__file__).resolve()` for reliable path resolution
- Add `shared/` to `sys.path` — do not copy files into each component
- Import specific names, not `from shared import *`
- Each component must still work if `shared/` provides enhanced functionality but is not strictly required (graceful degradation)

### 8.3 Orchestration: Suite-Level SKILL.md

The suite-level SKILL.md is the router. When a user's query could match multiple components, the suite SKILL.md tells the agent how to decide:

```markdown
# /ecommerce-suite — E-commerce Intelligence

You are an e-commerce analytics coordinator. Route user queries
to the right component skill based on intent:

## Routing Logic

| User Intent | Route To | Example Queries |
|-------------|----------|-----------------|
| Revenue, orders, conversion | /sales-monitor | "What were last week's sales?" |
| Segments, cohorts, churn | /customer-analytics | "Show customer retention by cohort" |
| Stock levels, reorder | /inventory-tracker | "Which products need reordering?" |
| Executive summary, dashboard | /executive-reports | "Generate the weekly executive report" |

## Cross-Component Workflows

Some requests require multiple components:

### Full Store Report
When the user asks for a "full report" or "store overview":
1. Invoke /sales-monitor for revenue summary
2. Invoke /customer-analytics for retention metrics
3. Invoke /inventory-tracker for stock alerts
4. Invoke /executive-reports to compile everything into a single report

### Churn Impact Analysis
When the user asks about churn's revenue impact:
1. Invoke /customer-analytics for churn rate and segments
2. Invoke /sales-monitor for revenue by customer segment
3. Combine: revenue at risk = churned segment revenue × churn rate
```

### 8.4 Data Flow Between Components

Components do not call each other's functions directly. Instead, they communicate through:

1. **Shared data files**: Component A writes to `data/sales_summary.json`, Component B reads it
2. **Shared API client**: Both components use the same `shared/api_client.py` to fetch data
3. **Agent orchestration**: The agent (LLM) reads output from Component A and passes relevant parts to Component B

**Anti-patterns to avoid:**
- Component A importing Component B's scripts directly (creates tight coupling)
- Components writing to each other's directories
- Circular dependencies between components

### 8.5 Component Independence Rule

Each component must be independently functional. This means:

- A component extracted from the suite and installed alone must still work
- `shared/` utilities enhance performance (avoid duplicate API calls, consistent formatting) but are not hard requirements
- If a component absolutely requires `shared/`, document this in its README.md
- The suite-level install.sh must install `shared/` alongside all components

---

## 9. Versioning Strategy

### 9.1 Semver for Skills

Skills follow [Semantic Versioning](https://semver.org/):

| Change Type | Version Bump | Examples |
|------------|-------------|---------|
| **Patch** (x.y.Z) | Bug fixes, typo corrections, minor doc improvements | Fix API timeout handling, correct calculation formula |
| **Minor** (x.Y.0) | New analyses, new data sources, new output formats | Add trend analysis, support CSV export, add new API endpoint |
| **Major** (X.0.0) | Breaking changes to inputs, outputs, or invocation | Change script arguments, rename skill, restructure output format |

### 9.2 What Counts as Breaking

A change is breaking if existing users of the skill would get different behavior or errors:

| Breaking | Not Breaking |
|----------|-------------|
| Changing script CLI arguments | Adding new optional arguments |
| Changing output JSON structure | Adding new fields to output |
| Removing an analysis function | Adding new analysis functions |
| Renaming the skill | Updating the description keywords |
| Changing required environment variables | Adding optional environment variables |

### 9.3 Suite Versioning

Suite versions are independent of component versions:

```
ecommerce-suite/        version: 2.0.0  (added new component)
├── sales-monitor/      version: 1.3.0  (3 minor updates since suite v1)
├── customer-analytics/  version: 1.1.0  (1 minor update)
├── inventory-tracker/   version: 2.0.0  (breaking change in its own output)
└── executive-reports/   version: 1.0.0  (unchanged)
```

**Suite version bump rules:**

| Change | Suite Version Bump |
|--------|--------------------|
| Bug fix in one component | No suite bump (component patch only) |
| New capability in one component | No suite bump (component minor only) |
| Breaking change in one component | Suite minor bump (warn users) |
| Add new component to suite | Suite minor bump |
| Remove component from suite | Suite major bump |
| Restructure shared/ | Suite major bump |

### 9.4 Version in Practice

The version lives in SKILL.md frontmatter:

```yaml
metadata:
  version: 1.2.0
```

When publishing to the registry, `skill_registry.py` reads this version. Publishing the same name+version is rejected unless `--force` is used.

**When to create a new skill vs. version an existing one:**

| Situation | Action |
|-----------|--------|
| Same domain, improved implementation | Version bump (minor or major) |
| Same domain, fundamentally different approach | New skill (e.g., `stock-analyzer-v2`) |
| Different domain entirely | New skill |
| Extending to cover adjacent domain | If tightly coupled: version bump. If independent: new skill or convert to suite |

---

## 10. Architecture Checklist

Use this checklist before proceeding to implementation (Phase 5):

### Decision

- [ ] Determined Simple Skill vs Complex Suite
- [ ] Justified the decision based on workflow count, code size, and domain scope
- [ ] If suite: identified shared resources and component boundaries
- [ ] If suite: designed orchestration logic (routing, cross-component workflows)

### Naming

- [ ] Name is 1-64 characters, kebab-case
- [ ] Name matches the parent directory
- [ ] No `-cskill` suffix
- [ ] Name is descriptive and includes the primary domain
- [ ] If suite: all component names are unique and follow kebab-case

### Structure

- [ ] Directory layout matches the chosen sizing pattern (Small/Medium/Large)
- [ ] SKILL.md planned at <500 lines
- [ ] Scripts have clear separation of concerns
- [ ] References planned for detailed content
- [ ] `install.sh` included
- [ ] `README.md` planned with multi-platform install instructions
- [ ] No `marketplace.json` for Simple Skills
- [ ] If Complex Suite with `marketplace.json`, only official fields used
- [ ] If suite: shared/ directory planned with import patterns documented
- [ ] If suite: each component is independently functional

### Performance

- [ ] Cache strategy defined (what to cache, TTL for each data type)
- [ ] Rate limiting planned for external APIs
- [ ] Error handling approach defined (retries, backoff, fallbacks)
- [ ] SKILL.md size managed via progressive disclosure to `references/`

### Dependencies

- [ ] Dependency strategy decided (stdlib-only vs. third-party)
- [ ] requirements.txt planned if third-party packages needed
- [ ] No unnecessary heavy dependencies

### Versioning

- [ ] Initial version set (1.0.0)
- [ ] Version bump rules understood (patch/minor/major)
- [ ] If suite: component versions independent of suite version

### Documentation

- [ ] Architecture decisions documented
- [ ] Script responsibilities defined (input, output, line count estimate)
- [ ] Reference files planned (topic, estimated word count)
- [ ] Asset files planned (config structure, metadata)
