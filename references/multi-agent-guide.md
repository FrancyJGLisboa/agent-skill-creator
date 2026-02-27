# Multi-Agent Suite Creation

## Overview

A multi-agent suite is a collection of related skills that work together as a unified system. Instead of creating one monolithic skill, the suite splits responsibilities across multiple focused skills that share references and coordinate through a common integration layer.

The 5-phase pipeline applies to each component skill, but Phase 3 (Architecture) makes the critical decision: simple skill vs. complex suite.

## When to Use Batch Creation

| Scenario | Single Skill | Multi-Agent Suite |
|----------|-------------|-------------------|
| 1-2 distinct workflows | Recommended | Overkill |
| 3+ distinct workflows | Unwieldy | Recommended |
| Total code > 2,000 lines | Hard to maintain | Organized by component |
| Team maintenance | Single owner ok | Multiple contributors benefit |
| Shared data sources across workflows | Duplicated logic | Shared reference layer |
| Independent scaling of capabilities | Not possible | Each skill evolves independently |

**Rule of thumb**: If you find yourself describing more than two unrelated tasks in a single skill description, you need a suite.

## Suite Creation Process

### Step 1: Analyze Relationships

The system examines the user's requirements and identifies distinct workflow clusters.

```
User: "I need to track our e-commerce store -- monitor sales,
       analyze customer behavior, track inventory levels, and
       generate executive reports."

Analysis:
  Cluster 1: Sales Monitoring (revenue, orders, conversion)
  Cluster 2: Customer Analytics (segmentation, cohorts, churn)
  Cluster 3: Inventory Tracking (stock levels, reorder alerts)
  Cluster 4: Executive Reporting (aggregated dashboards)

  Shared resources: Shopify API connection, date utilities,
  report generation templates
```

### Step 2: Determine Structure

Based on the cluster analysis, the system designs the suite directory:

```
ecommerce-suite/
├── SKILL.md                        # Suite-level overview (<500 lines)
├── .claude-plugin/
│   └── marketplace.json            # Suite manifest (official fields only)
├── skills/
│   ├── sales-monitor/
│   │   ├── SKILL.md                # Sales-specific instructions
│   │   └── scripts/
│   │       └── monitor_sales.py
│   ├── customer-analytics/
│   │   ├── SKILL.md                # Customer-specific instructions
│   │   └── scripts/
│   │       └── analyze_customers.py
│   ├── inventory-tracker/
│   │   ├── SKILL.md                # Inventory-specific instructions
│   │   └── scripts/
│   │       └── track_inventory.py
│   └── executive-reports/
│       ├── SKILL.md                # Reporting instructions
│       └── scripts/
│           └── generate_reports.py
├── shared/
│   ├── api_client.py               # Shared Shopify API connection
│   ├── date_utils.py               # Common date handling
│   └── report_templates/           # Shared report assets
│       └── executive_template.html
├── references/
│   └── api-guide.md                # Shared API documentation
├── install.sh                      # Installs entire suite
└── README.md                       # Multi-platform instructions
```

### Step 3: Create Individual Skills

Each component skill goes through Phases 1-5 independently, but with awareness of the shared resources:

1. **Discovery** -- Each skill identifies its specific API endpoints (e.g., sales-monitor uses Shopify Orders API, inventory-tracker uses Shopify Inventory API).
2. **Design** -- Each skill defines its own analyses, scoped to its cluster.
3. **Architecture** -- Each skill follows the simple skill structure within the suite.
4. **Detection** -- Each skill gets its own description and keywords for independent activation.
5. **Implementation** -- Each skill references shared utilities from `shared/`.

### Step 4: Integration Layer

The suite-level `SKILL.md` serves as the orchestration layer. It describes how the component skills relate and when to invoke which one:

```markdown
# E-commerce Suite

## Component Skills

This suite contains four specialized skills:

- **sales-monitor**: Activate for revenue, orders, and conversion queries
- **customer-analytics**: Activate for segmentation, cohort, and churn queries
- **inventory-tracker**: Activate for stock levels, reorder, and supply queries
- **executive-reports**: Activate for dashboards, summaries, and executive briefings

## Cross-Skill Workflows

When the user asks for a "full store overview" or "weekly executive summary",
invoke executive-reports which aggregates data from all three other skills.
```

## Suite-Level marketplace.json

For complex suites that need Claude Code plugin registration, a `marketplace.json` is generated with **only official fields**:

```json
{
  "name": "ecommerce-suite",
  "plugins": [
    {
      "name": "sales-monitor",
      "description": "Monitor e-commerce sales, revenue trends, order volumes, and conversion rates using Shopify data.",
      "source": "./skills/sales-monitor/",
      "skills": ["./skills/sales-monitor/"]
    },
    {
      "name": "customer-analytics",
      "description": "Analyze customer behavior, segmentation, cohort retention, and churn patterns from e-commerce data.",
      "source": "./skills/customer-analytics/",
      "skills": ["./skills/customer-analytics/"]
    },
    {
      "name": "inventory-tracker",
      "description": "Track inventory stock levels, predict reorder points, and alert on low-stock items.",
      "source": "./skills/inventory-tracker/",
      "skills": ["./skills/inventory-tracker/"]
    },
    {
      "name": "executive-reports",
      "description": "Generate executive dashboards and PDF summaries aggregating sales, customer, and inventory data.",
      "source": "./skills/executive-reports/",
      "skills": ["./skills/executive-reports/"]
    }
  ]
}
```

**Important**: The marketplace.json uses ONLY the official fields: `name` and `plugins` at the top level, and `name`, `description`, `source`, `skills` per plugin entry. No `version`, `author`, `repository`, `tags`, `icon`, or other non-standard fields.

## Suite Examples

### Financial Suite

**User request**: "Create a suite for comprehensive financial analysis -- stock tracking, portfolio management, and market research."

```
financial-suite/
├── SKILL.md
├── .claude-plugin/marketplace.json
├── skills/
│   ├── stock-tracker/         # Real-time and historical price data
│   ├── portfolio-manager/     # Holdings, allocation, performance
│   └── market-research/       # Sector analysis, news sentiment
├── shared/
│   ├── market_data_client.py  # Alpha Vantage + Yahoo Finance
│   └── financial_utils.py     # Common calculations (returns, ratios)
├── references/
├── install.sh
└── README.md
```

### E-commerce Suite

**User request**: "I manage an online store and need to track everything -- sales, customers, inventory, and generate weekly reports."

(See the detailed structure in the Suite Creation Process section above.)

### Climate Suite

**User request**: "Build a climate analysis system with historical trend analysis, forecast monitoring, and extreme event alerting."

```
climate-suite/
├── SKILL.md
├── .claude-plugin/marketplace.json
├── skills/
│   ├── historical-trends/     # Long-term climate data analysis
│   ├── forecast-monitor/      # Short-term forecast tracking
│   └── extreme-events/        # Severe weather alerting
├── shared/
│   ├── climate_data_client.py # NOAA + Open-Meteo connections
│   └── geo_utils.py           # Geographic region handling
├── references/
├── install.sh
└── README.md
```

## Suite Orchestration Patterns

The suite-level SKILL.md is the most important file in a suite. It doesn't just list components — it tells the agent *how to think* about routing, sequencing, and combining them.

### Pattern 1: Intent-Based Routing

The simplest pattern. The suite SKILL.md maps user intent to component skills:

```markdown
# /ecommerce-suite — E-commerce Intelligence

You coordinate four specialized e-commerce skills. Route every user
query to the right component based on intent.

## Routing Table

| If the user asks about... | Invoke | Examples |
|---------------------------|--------|---------|
| Revenue, orders, sales, conversion, AOV | /sales-monitor | "What were last week's sales?" |
| Customers, segments, cohorts, churn, retention | /customer-analytics | "Show me customer retention" |
| Stock, inventory, reorder, supply, out-of-stock | /inventory-tracker | "Which SKUs need reordering?" |
| Summary, dashboard, executive, weekly report | /executive-reports | "Generate the weekly report" |

If the query doesn't clearly match one component, ask the user to clarify.
If the query spans multiple components, use the cross-component workflows below.
```

### Pattern 2: Sequential Pipeline

Some workflows require components in sequence — the output of one feeds the next:

```markdown
## Cross-Component Workflows

### Weekly Executive Report
When user asks for "weekly report", "executive summary", or "full store overview":

1. Run /sales-monitor: Get revenue, orders, conversion for the past 7 days
2. Run /customer-analytics: Get new vs returning customer split, churn rate
3. Run /inventory-tracker: Get low-stock alerts and reorder recommendations
4. Run /executive-reports: Compile all three into a single PDF dashboard

The executive-reports component expects data from the other three.
Pass the outputs as context — do not ask the user to run each step manually.

### Churn Revenue Impact
When user asks about "revenue impact of churn" or "how much are we losing":

1. Run /customer-analytics: Get churned customer segments and churn rate
2. Run /sales-monitor: Get revenue breakdown by customer segment
3. Calculate: revenue_at_risk = churned_segment_revenue × churn_rate
4. Present combined analysis with both the churn data and revenue impact
```

### Pattern 3: Parallel Aggregation

When components can run independently and results are combined:

```markdown
### Store Health Check
When user asks for "store health" or "how's the business":

Run these in parallel (no dependencies between them):
- /sales-monitor → revenue trend (up/down/flat)
- /customer-analytics → retention rate
- /inventory-tracker → stock health score

Then synthesize:
- All green: "Store is healthy — revenue trending up, retention stable, stock well-managed"
- Mixed: Report which areas need attention
- All concerning: "Multiple areas need attention" + specific recommendations
```

### Pattern 4: Conditional Routing

When the right component depends on data discovered during the conversation:

```markdown
## Conditional Workflows

### Deep Dive Analysis
When user asks to "deep dive" or "investigate" a metric:

1. Identify which metric they're asking about
2. Route to the appropriate component:
   - Revenue metric → /sales-monitor with detailed=true
   - Customer metric → /customer-analytics with detailed=true
   - Stock metric → /inventory-tracker with detailed=true
3. If the deep dive reveals a cross-domain issue (e.g., revenue dropped
   because of stockouts), invoke the relevant second component
4. Present the combined root-cause analysis
```

### Orchestration Anti-Patterns

| Anti-Pattern | Why It's Wrong | Do This Instead |
|-------------|---------------|-----------------|
| Suite SKILL.md just lists components without routing logic | Agent has to guess which component to use | Provide explicit routing table with example queries |
| Components call each other's scripts directly | Creates tight coupling, breaks independence | Agent orchestrates — passes output from A as context to B |
| Suite SKILL.md duplicates component instructions | Maintenance nightmare, instructions drift apart | Reference component skills: "Invoke /sales-monitor for this" |
| No cross-component workflow examples | Agent doesn't know how to combine results | Document 2-3 concrete multi-component workflows |
| Every query goes through all components | Wastes tokens and time | Route to specific component; only aggregate when explicitly asked |

### Complete Suite SKILL.md Example

```markdown
# /financial-suite — Comprehensive Financial Analysis

You are a financial analysis coordinator managing three specialized skills.
Your job is to route queries to the right specialist and combine results
when needed.

## Component Skills

- **/stock-analyzer**: Real-time and historical price data, technical indicators
- **/portfolio-tracker**: Holdings, allocation, performance, rebalancing
- **/market-research**: Sector analysis, news sentiment, peer comparison

## Routing Logic

| User Intent | Route To |
|-------------|----------|
| Price, chart, technical indicator, RSI, MACD | /stock-analyzer |
| My portfolio, allocation, performance, rebalance | /portfolio-tracker |
| Sector trends, news, competitor, peer comparison | /market-research |

## Cross-Skill Workflows

### Portfolio Review with Market Context
When user asks for "portfolio review" or "how am I doing":
1. Invoke /portfolio-tracker for current holdings and performance
2. Invoke /market-research for sector trends affecting held positions
3. Synthesize: performance attribution + market context + recommendations

### Buy/Sell Analysis
When user asks "should I buy X" or "should I sell X":
1. Invoke /stock-analyzer for technical analysis of the specific stock
2. Invoke /market-research for sector sentiment and peer comparison
3. Invoke /portfolio-tracker to check current exposure and allocation impact
4. Synthesize: technical signal + market context + portfolio fit

## When to Combine vs. Route Directly

- Single-domain question → Route to one component
- "How am I doing" or "full analysis" → Combine all components
- If unsure → Ask the user: "Would you like a quick check on [X]
  or a comprehensive analysis across your portfolio?"
```

---

## Benefits of Suite Creation

### Time Efficiency

Creating a suite through the batch process is significantly faster than creating individual skills separately:

| Approach | API Research | Shared Code | Integration | Total |
|----------|-------------|-------------|-------------|-------|
| 4 separate skills | 4x (redundant) | 0 (duplicated) | Manual | ~4 hours |
| 1 suite (batch) | 1x (shared) | 1x (reused) | Automatic | ~1.5 hours |

### Built-in Integration

Component skills within a suite share:
- API client code (no duplicated connection logic)
- Utility functions (date handling, formatting, calculations)
- Reference documentation (API guides written once)
- Report templates (consistent styling across outputs)

### Independent Maintenance

Each component skill can be:
- Updated independently without affecting others
- Tested in isolation
- Replaced with an improved version
- Extended with new analyses

The suite structure makes it possible to update the inventory-tracker without touching the sales-monitor, while still sharing the underlying Shopify API client.

### Marketplace Discoverability

Each plugin entry in `marketplace.json` has its own `description` field. This means a suite's individual components can be discovered by different searches:
- "track sales" finds the sales-monitor plugin
- "customer churn" finds the customer-analytics plugin
- "inventory alerts" finds the inventory-tracker plugin

The suite functions as both a single installable unit and a collection of independently discoverable capabilities.
