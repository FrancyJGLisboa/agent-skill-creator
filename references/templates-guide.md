# Template-Based Creation System

## Overview

The template-based creation system accelerates skill creation by providing pre-built scaffolds for common domains. Instead of starting from Phase 1 (Discovery) with a blank slate, templates provide a curated starting point with known-good APIs, proven analysis patterns, and tested configurations. The 5-phase pipeline still runs, but Phase 1 and Phase 2 are pre-populated with vetted decisions.

## Available Templates

> **Status note:** the templates below are **blueprints, not shipped scaffold
> directories**. `references/templates/` currently contains only the
> [README activation template](templates/README-activation-template.md).
> When a user requests template-based creation, the agent
> synthesizes the scaffold from the blueprint tables in this guide (APIs,
> analyses, script layout) rather than copying files from disk. Shipping these
> as ready-made directories is planned; contributions welcome.

### Financial Analysis

**Template ID**: `financial-analysis`
**Target domain**: Stock market, portfolio analysis, economic indicators

| Component | Details |
|-----------|---------|
| Primary API | Alpha Vantage (free tier, 500 requests/day) |
| Secondary API | Yahoo Finance via `yfinance` (unofficial, unlimited) |
| Pre-built analyses | Technical indicators (RSI, MACD, SMA), price trends, volume analysis, sector comparison |
| Output formats | Tabular summaries, time-series data, PDF reports |
| Authentication | API key via environment variable `ALPHA_VANTAGE_KEY` |

**Pre-configured scripts**:
- `scripts/fetch_market_data.py` -- OHLCV data retrieval with rate limiting
- `scripts/analyze_technicals.py` -- RSI, MACD, Bollinger Bands calculations
- `scripts/generate_report.py` -- PDF/HTML report generation

### Climate Analysis

**Template ID**: `climate-analysis`
**Target domain**: Weather patterns, historical climate data, forecasting

| Component | Details |
|-----------|---------|
| Primary API | Open-Meteo (free, no API key, 10,000 requests/day) |
| Secondary API | NOAA Climate Data Online (free, API key, 1,000 requests/day) |
| Pre-built analyses | Temperature trends, precipitation patterns, extreme events, historical comparisons |
| Output formats | Time-series data, geographic summaries, PDF reports |
| Authentication | Open-Meteo: none. NOAA: API key via `NOAA_API_KEY` |

**Pre-configured scripts**:
- `scripts/fetch_climate_data.py` -- Multi-source data retrieval with caching
- `scripts/analyze_trends.py` -- Statistical trend analysis and anomaly detection
- `scripts/generate_report.py` -- Climate summary report generation

### E-commerce Analytics

**Template ID**: `ecommerce-analytics`
**Target domain**: Sales tracking, customer behavior, revenue analysis

| Component | Details |
|-----------|---------|
| Primary API | Google Analytics Data API (free tier) |
| Secondary APIs | Stripe API (transaction data), Shopify Admin API (store data) |
| Pre-built analyses | Revenue trends, conversion funnels, customer segmentation, product performance |
| Output formats | Dashboard data, CSV exports, PDF reports |
| Authentication | OAuth2 (Google), API key (Stripe/Shopify) |

**Pre-configured scripts**:
- `scripts/fetch_analytics.py` -- Multi-platform data aggregation
- `scripts/analyze_sales.py` -- Revenue, conversion, and cohort analysis
- `scripts/generate_dashboard.py` -- HTML dashboard and PDF report

## Template Matching Process

When a user describes their workflow, the system matches it to the best template through a two-step process.

### Step 1: Keyword Extraction

The system extracts domain-relevant keywords from the user's request:

```
User: "I need to analyze stock performance and generate weekly reports"

Extracted keywords:
  - Domain: ["stock", "performance", "reports"]
  - Actions: ["analyze", "generate"]
  - Frequency: ["weekly"]
  - Implied domain: finance
```

### Step 2: Similarity Scoring

Each template is scored against the extracted keywords:

| Template | Keyword Match | Domain Match | Action Match | Total Score |
|----------|--------------|--------------|--------------|-------------|
| Financial Analysis | 3/3 | 1.0 | 0.9 | 0.95 |
| Climate Analysis | 0/3 | 0.0 | 0.4 | 0.10 |
| E-commerce Analytics | 1/3 | 0.2 | 0.6 | 0.30 |

**Selection threshold**: A template is suggested when its score exceeds 0.70. Below that threshold, the system falls back to the standard 5-phase pipeline with full discovery.

## Template Usage

### Direct Request

Explicitly ask for a template:

```
User: "Create a financial analysis skill using the financial template"

Result: System loads the financial-analysis template, pre-populates
Phase 1 (Alpha Vantage + Yahoo Finance) and Phase 2 (technical
indicators), then proceeds through Phases 3-5.
```

### Auto-Detection

Describe your workflow and let the system match:

```
User: "Every week I check weather trends for the Pacific Northwest
       and compare them to historical averages"

Result: System detects climate-analysis template (score: 0.92),
confirms with user, then proceeds with Open-Meteo + NOAA as
pre-selected data sources.
```

### Customization After Selection

Templates are starting points, not rigid constraints. After selection, the user can customize any aspect:

```
User: "Use the financial template but replace Alpha Vantage with
       IEX Cloud and add cryptocurrency support"

Result: System loads financial-analysis template, swaps the primary
API to IEX Cloud, adds crypto endpoints to Phase 2 design, then
proceeds through Phases 3-5 with the modifications.
```

## Creating Custom Templates

Custom templates follow the same structure as built-in ones. Place them in `references/templates/custom/`.

### Template File Structure

```
references/templates/custom/
└── my-template/
    ├── template.json        # Template definition
    ├── phase1-config.md     # Pre-populated Discovery decisions
    ├── phase2-config.md     # Pre-populated Design decisions
    └── scripts/             # Starter scripts (optional)
        └── fetch_data.py
```

### Template Definition (template.json)

```json
{
  "id": "my-custom-template",
  "name": "My Custom Template",
  "domain": "logistics",
  "keywords": ["shipping", "tracking", "delivery", "freight", "supply chain"],
  "apis": [
    {
      "name": "ShipEngine",
      "url": "https://www.shipengine.com/docs/",
      "auth": "api_key",
      "free_tier": true,
      "rate_limit": "500/day"
    }
  ],
  "analyses": [
    "shipment_tracking",
    "delivery_performance",
    "cost_optimization",
    "route_analysis"
  ],
  "output_formats": ["tabular", "pdf", "csv"]
}
```

### Registering the Template

After creating the template files, register it by adding an entry to `references/templates/registry.json` (this registry does not ship yet — create it alongside your first template directory):

```json
{
  "templates": [
    {"id": "financial-analysis", "path": "references/templates/financial/", "builtin": true},
    {"id": "climate-analysis", "path": "references/templates/climate/", "builtin": true},
    {"id": "ecommerce-analytics", "path": "references/templates/ecommerce/", "builtin": true},
    {"id": "my-custom-template", "path": "references/templates/custom/my-template/", "builtin": false}
  ]
}
```

### Template Best Practices

1. **Include at least 10 keywords** to ensure reliable matching during auto-detection.
2. **Document API quirks** in `phase1-config.md` so the pipeline does not rediscover known gotchas.
3. **Provide working starter scripts** when possible -- this accelerates Phase 5 significantly.
4. **Test the template** by running a full creation cycle and verifying the output passes validation.
5. **Keep APIs current** -- review rate limits and endpoints periodically, since free tiers change.

## Template vs. Full Pipeline

| Scenario | Recommended Approach |
|----------|---------------------|
| Domain matches a built-in template | Use template (saves 30-50% of creation time) |
| Domain is adjacent to a template | Use template with customization |
| Entirely new domain | Full 5-phase pipeline from scratch |
| User explicitly requests no template | Full 5-phase pipeline |
| User provides a transcript of their workflow | Full pipeline with transcript processing |

Templates are an optimization, not a replacement. The 5-phase pipeline always runs. Templates simply pre-populate the early phases with proven decisions.

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
even when no real data is provided -- the artifact shows the user what
the skill will produce.

### Extending

User-provided templates are not in scope for v6.0. Adding a fifth bundled
template requires:

1. Add the `.jsx` file under `references/artifact-templates/`
2. Add a structural test class in `scripts/tests/test_template_structure.py`
3. Add a signal in `scripts/artifact_detector.py` that maps to it
4. Add labeled examples to `scripts/tests/fixtures/labeled_examples.json`
5. Re-run the accuracy gate
