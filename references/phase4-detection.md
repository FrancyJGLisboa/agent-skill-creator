# Phase 4: Automatic Detection

## Objective

**DETERMINE** keywords and create description so Claude Code activates the skill automatically.

## Detailed Process

### Step 1: List Domain Entities

Identify all relevant entities that users may mention:

**Entity categories**:

**1. Organizations/Sources**
- Organization names (USDA, CONAB, NOAA, IMF)
- Acronyms (NASS, ERS, FAS)
- Full names (National Agricultural Statistics Service)

**2. Main Objects**
- For agriculture: commodities (corn, soybeans, wheat)
- For finance: instruments (stocks, bonds, options)
- For climate: metrics (temperature, precipitation)

**3. Geography**
- Countries (US, Brazil, China)
- Regions (Midwest, Centro-Oeste, Southeast)
- States/Provinces (Iowa, Mato Grosso, Texas)

**4. Metrics**
- Production, area, yield, price
- Revenue, profit, growth
- Temperature, rainfall, humidity

**5. Temporality**
- Years, seasons, quarters, months
- Current, historical, forecast
- YoY, QoQ, MoM

**Example (US agriculture)**:

```markdown
**Organizations**:
- USDA, NASS, National Agricultural Statistics Service
- Department of Agriculture
- QuickStats

**Commodities**:
- Corn, soybeans, wheat
- Cotton, rice, sorghum
- Barley, oats, hay, peanuts
- [list all major ones - 20+]

**Geography**:
- US, United States, national
- States: Iowa, Illinois, Nebraska, Kansas, Texas, etc [list top 15]
- Regions: Midwest, Great Plains, Southeast, etc

**Metrics**:
- Production, area planted, area harvested
- Yield, productivity
- Price received, value of production
- Inventory, stocks

**Temporality**:
- Year, season, crop year
- Current, latest, this year, last year
- Historical, trend, past 5 years
- Forecast, projection, outlook
```

### Step 2: List Actions/Verbs

Which verbs does the user use to request analyses?

**Categories**:

**Query (fetch information)**:
- What is, how much, show me, get
- Tell me, find, retrieve

**Compare**:
- Compare, versus, vs, against
- Difference, change, growth
- Higher, lower, better, worse

**Rank (sort)**:
- Top, best, leading, biggest
- Rank, ranking, list
- Which states, which countries

**Analyze**:
- Analyze, analysis
- Trend, pattern, evolution
- Breakdown, decompose, explain

**Forecast (project)**:
- Predict, project, forecast
- Outlook, expectation, estimate
- Future, next year, coming season

**Visualize**:
- Plot, chart, graph, visualize
- Show chart, generate graph

### Step 2.5: Generate Exhaustive Keywords (NEW v2.0 - CRITICAL!)

**OBJECTIVE:** Generate 60+ keywords to ensure correct activation in ALL relevant queries.

**LEARNING:** us-crop-monitor v1.0 had ~20 keywords. Missing "yield", "harvest", "production" → Claude Code didn't activate for those queries. v2.0 expanded to 60+ keywords.

**Mandatory Process:**

**Step A: Keywords per API Metric**

For EACH metric/endpoint the skill implements, generate keywords:

```markdown
Metric 1: CONDITION (quality ratings)
Primary keywords: condition, conditions, quality, ratings
Secondary keywords: status, health, state
Technical keywords: excellent, good, fair, poor
Action keywords: rate, rated, rating, classify
Portuguese: condição, condições, qualidade, estado, classificação
→ Total: ~15 keywords

Metric 2: PROGRESS (% planted/harvested)
Primary keywords: progress, harvest, planted, harvested
Secondary keywords: planting, harvesting, completion
Technical keywords: percentage, percent, %
Action keywords: advancing, complete, completed
Portuguese: progresso, plantio, colheita, plantado, colhido
→ Total: ~15 keywords

Metric 3: YIELD (productivity)
Primary keywords: yield, productivity, performance
Technical keywords: bushels per acre, bu/acre, bu/ac
Secondary keywords: output per unit
Portuguese: rendimento, produtividade, bushels por acre
→ Total: ~12 keywords

... Repeat for ALL implemented metrics
```

**Rule:** Each metric = minimum 10 unique keywords

**Step B: Categorize Keywords by Type**

```markdown
### Keyword Matrix - {Skill Name}

**1. Main Entities** (20+ keywords)
- Official name: {entity}
- Variations: {variations}
- Singular + plural
- Acronyms: {acronyms}
- Full names: {full names}
- Portuguese: {portuguese terms}

**2. Metrics - ONE SECTION PER API METRIC!** (30+ keywords)
- Metric 1: {list 10-15 keywords}
- Metric 2: {list 10-15 keywords}
- Metric 3: {list 10-15 keywords}
...

**3. Actions/Verbs** (20+ keywords)
- Query: what, how, show, get, tell, find, retrieve
- Compare: compare, vs, versus, against, difference
- Rank: top, best, rank, leading, biggest
- Analyze: analyze, trend, pattern, evolution
- Report: report, dashboard, summary, overview
- Portuguese: comparar, ranking, análise, relatório

**4. Temporal Qualifiers** (15+ keywords)
- Current: current, now, today, latest, recent, atual, agora, hoje
- Historical: historical, past, previous, last year, histórico
- Comparative: this year vs last year, YoY, year-over-year
- Forecast: forecast, projection, estimate, outlook, previsão

**5. Geographic Qualifiers** (15+ keywords)
- National: national, US, United States, country-wide
- Regional: region, Midwest, South, regional
- State: state, by state, state-level, estado
- Specific names: Iowa, Illinois, Nebraska, ...

**6. Data Context** (10+ keywords)
- Source: {API name}, {organization}, {data source}
- Type: data, statistics, metrics, indicators, dados
```

**Goal:** Total 60-80 unique keywords!

**Step C: Test Coverage Matrix**

For each analysis function, generate 10 different queries:

```markdown
Function: harvest_progress_report()

Query variations (test coverage):
1. "What's the corn harvest progress?" ✅ harvest, progress
2. "How much corn has been harvested?" ✅ harvested
3. "Percent corn harvested?" ✅ percent, harvested
4. "Harvest completion status?" ✅ harvest, completion, status
5. "Progresso de colheita do milho?" ✅ progresso, colheita
6. "Quanto foi colhido?" ✅ colhido
7. "Harvest advancement?" ✅ harvest, advancement
8. "How advanced is harvest?" ✅ harvest, advanced
9. "Colheita completa?" ✅ colheita
10. "Percentage complete harvest?" ✅ percentage, harvest

ALL keywords present in description? → Verify!
```

**Do this for ALL 11 functions** = 110 query variations tested!

### Step 3: List Question Variations

For each analysis type, how can user ask?

**YoY Comparison**:
- "Compare X this year vs last year"
- "How does X compare to last year"
- "Is X up or down from last year"
- "X growth rate"
- "X change YoY"
- "X vs previous year"
- "Did X increase or decrease"

**Ranking**:
- "Top states for X"
- "Which states produce most X"
- "Leading X producers"
- "Best X production"
- "Biggest X producers"
- "Ranking of X"
- "List top 10 X"

**Trend**:
- "X trend last N years"
- "How has X changed over time"
- "X evolution"
- "Historical X data"
- "X growth rate historical"
- "Long term trend of X"

**Simple Query**:
- "What is X production"
- "X production in [year]"
- "How much X"
- "X data"
- "Current X"

### Step 4: Define Negative Scope

**Important**: What should NOT activate?

Avoid false positives (skill activates when it shouldn't).

**Technique**: Think of similar questions but OUT of scope.

**Example (US agriculture)**:

❌ **DO NOT activate for**:
- Futures market prices
  - "CBOT corn futures price"
  - "Soybean futures December contract"
  - Reason: Skill is USDA data (physical production), not trading

- Other countries' agriculture
  - "Brazil soybean production"
  - "Argentina corn exports"
  - Reason: Skill is US only

- Consumption/demand
  - "US corn consumption"
  - "Soybean demand forecast"
  - Reason: NASS has production, not consumption

- Private company data
  - "Monsanto corn seed sales"
  - "Cargill soybean crush"
  - Reason: Corporate data, not national statistics

**Document**:
```markdown
## Skill Scope

### ✅ WITHIN scope:
- Physical crop production in US
- Planted/harvested area
- Yield/productivity
- Prices RECEIVED by farmers (farm gate)
- Inventories
- Historical and current data
- Comparisons, rankings, trends

### ❌ OUT of scope:
- Futures market prices (CBOT, CME)
- Agriculture outside US
- Consumption/demand
- Private company data
- Market price forecasting
```

### Step 5: Create Precise Description (Updated v2.0)

**NEW RULE:** Description must contain ALL 60+ identified keywords!

**Expanded Template:**

```yaml
description: This skill should be used when the user asks about
{domain} ({main entities with variations}). Automatically activates
for queries about {metric1} ({metric1 keywords}), {metric2}
({metric2 keywords}), {metric3} ({metric3 keywords}), {metric4}
({metric4 keywords}), {metric5} ({metric5 keywords}), {actions_list},
{temporal qualifiers}, {geographic qualifiers}, comparisons
{comparison types}, rankings, trends, {data source} data,
comprehensive reports, and dashboards. Uses {language} with {API name}
to fetch real data on {complete list of all metrics}.
```

**Mandatory components**:
1. ✅ **Domain** with entities (corn, soybeans, wheat - not just "crops")
2. ✅ **EACH API metric** explicitly mentioned
3. ✅ **Synonyms** in parentheses (harvest = colheita, yield = rendimento)
4. ✅ **Actions** covered (compare, rank, analyze, report)
5. ✅ **Temporal context** (current, today, year-over-year)
6. ✅ **Geographic** context (states, regions, national)
7. ✅ **Data source** (USDA NASS, etc.)
8. ✅ **Portuguese + English** keywords mixed

**Real size:** 300-500 characters (yes, larger than "recommended" - but necessary!)

**Real Example (us-crop-monitor v2.0):**
```yaml
description: This skill should be used when the user asks about
agricultural crops in the United States (soybeans, corn, wheat).
Automatically activates for queries about crop conditions (condições),
crop progress (progresso de plantio/colheita), harvest progress
(progresso de colheita), planting progress (plantio), yield
(produtividade/rendimento em bushels per acre), production (produção
total em bushels), area planted (área plantada), area harvested
(área colhida), acres, forecasts (estimativas), crop monitoring,
weekly comparisons (week-over-week) or annual (year-over-year),
state producer rankings, trend analyses, USDA NASS data, comprehensive
reports, and crop dashboards. Uses Python with NASS API to fetch
real data on condition, progress, productivity, production and area.
```

**Analysis:**
- Entities: soybeans, corn, wheat (3)
- Metrics: conditions, progress, harvest, planting, yield, production, area (7)
- Each metric with PT synonym: (condições), (colheita), (rendimento), etc.
- Actions: queries, comparisons, rankings, analyses, reports
- Temporal: weekly, annual, week-over-week, year-over-year
- Source: USDA NASS
- Total unique keywords: ~65+

**Step D: Validate Keyword Coverage**

Final checklist:
```markdown
- [ ] All API metrics mentioned? (if API has 5 → 5 in description)
- [ ] Each metric has PT synonym? (yield = rendimento)
- [ ] Action verbs included? (compare, rank, analyze)
- [ ] Temporal context? (current, today, YoY)
- [ ] Geographic context? (states, national)
- [ ] Data source mentioned? (USDA NASS)
- [ ] Total >= 60 unique keywords? (count!)
```

**Example 2 (stock analysis)**:
```yaml
description: This skill should be used for technical stock analysis using indicators like RSI, MACD, Bollinger Bands, moving averages. Activates when user asks about technical analysis, indicators, buy/sell signals for stocks. Supports multiple tickers, benchmark comparisons, alert generation. DO NOT use for fundamental analysis, financial statements, or news.
```

### Step 6: List Complete Keywords

In SKILL.md, include complete keywords section:

```markdown
## Keywords for Automatic Detection

This skill is activated when user mentions:

**Entities**:
- [complete list of organizations]
- [complete list of main objects]

**Geography**:
- [list of countries/regions/states]

**Metrics**:
- [list of metrics]

**Actions**:
- [list of verbs]

**Temporality**:
- [list of temporal terms]

**Activation examples**:
✅ "[example 1]"
✅ "[example 2]"
✅ "[example 3]"
✅ "[example 4]"
✅ "[example 5]"

**Does NOT activate for**:
❌ "[out of scope example]"
❌ "[out of scope example]"
❌ "[out of scope example]"
```

### Step 7: Mental Testing

**Simulate detection**:

For each example question from use cases (Phase 2), verify:
- Description contains relevant keywords? ✅
- Doesn't contain negative scope keywords? ✅
- Claude would detect automatically? ✅

**If any use case would NOT be detected**:
→ Add missing keywords to description

## Detection Design Examples

### Example 1: US Agriculture (NASS)

**Identified keywords**:
- Entities: USDA (5x), NASS (8x), agriculture (3x)
- Commodities: corn (12x), soybeans (10x), wheat (8x)
- Metrics: production (15x), area (10x), yield (8x)
- Geography: US (10x), states (5x), Iowa (2x)
- Actions: compare (5x), ranking (3x), trend (2x)

**Description**:
"This skill should be used for analyses about United States agriculture using official USDA NASS data. Activates when user asks about production, area, yield of commodities like corn, soybeans, wheat. Supports YoY comparisons, rankings, trends. DO NOT use for futures or other countries."

**Coverage**: 95% of typical use cases

### Example 2: Global Climate (NOAA)

**Keywords**:
- Entities: NOAA, weather, climate
- Metrics: temperature, precipitation, humidity
- Geography: global, countries, stations
- Temporality: historical, current, forecast

**Description**:
"This skill should be used for climate analyses using NOAA data. Activates when user asks about temperature, precipitation, historical climate data or forecasts. Supports temporal and geographic aggregations, anomalies, long-term trends."

## Phase 4 Checklist

- [ ] Entities listed (organizations, objects, geography)
- [ ] Actions/verbs listed
- [ ] Question variations mapped
- [ ] Negative scope defined
- [ ] Description created (150-250 chars)
- [ ] Complete keywords documented in SKILL.md
- [ ] Activation examples (positive and negative)
- [ ] Mental detection simulation (all use cases covered)

---

## 🚀 **Enhanced Keyword Generation System v3.1**

### **Problem Solved: False Negatives Prevention**

**Issue**: Skills created with limited keywords (10-15) fail to activate for natural language variations, causing users to lose confidence when their installed skills are ignored by Claude.

**Solution**: Systematic keyword expansion achieving 50+ keywords with 98%+ activation reliability.

### **🔧 Enhanced Keyword Generation Process**

#### **Step 1: Base Keywords (Traditional Method)**
```
Domain: Data Extraction & Analysis
Base Keywords: "extract data", "normalize data", "analyze data"
Coverage: ~30% (limited)
```

#### **Step 2: Systematic Expansion (New Method)**

**A. Direct Variations Generator**
```
For each base capability, generate variations:
- "extract data" → "extract and analyze data", "extract and process data"
- "normalize data" → "normalize extracted data", "data normalization"
- "analyze data" → "analyze web data", "online data analysis"
```

**B. Synonym Expansion System**
```
Data Synonyms: ["information", "content", "details", "records", "dataset", "metrics"]
Extract Synonyms: ["scrape", "get", "pull", "retrieve", "collect", "harvest", "obtain"]
Analyze Synonyms: ["process", "handle", "work with", "examine", "study", "evaluate"]
Normalize Synonyms: ["clean", "format", "standardize", "structure", "organize"]
```

**C. Technical & Business Language**
```
Technical Terms: ["web scraping", "data mining", "API integration", "ETL process"]
Business Terms: ["process information", "handle reports", "work with data", "analyze metrics"]
Workflow Terms: ["daily I have to", "need to process", "automate this workflow"]
```

**D. Natural Language Patterns**
```
Question Forms: ["How to extract data", "What data can I get", "Can you analyze this"]
Command Forms: ["Extract data from", "Process this information", "Analyze the metrics"]
Informal Forms: ["get data from site", "handle this data", "work with information"]
```

#### **Step 3: Pattern-Based Keyword Generation**

**Action + Object Patterns:**
```
{action} + {object} + {source}
Examples:
- "extract data from website"
- "process information from API"
- "analyze metrics from database"
- "normalize records from file"
```

**Workflow Patterns:**
```
{workflow_trigger} + {action} + {data_type}
Examples:
- "I need to extract data daily"
- "Have to process reports every week"
- "Need to analyze metrics monthly"
- "Must normalize information regularly"
```

### **📊 Coverage Expansion Results**

#### **Before Enhancement:**
```
Total Keywords: 10-15
Coverage Types:
├── Direct phrases: 8-10
├── Domain terms: 2-5
└── Success rate: ~70%
```

#### **After Enhancement:**
```
Total Keywords: 50-80
Coverage Types:
├── Direct variations: 15-20
├── Synonym expansions: 10-15
├── Technical terms: 8-12
├── Business language: 7-10
├── Workflow patterns: 5-8
├── Natural language: 5-10
└── Success rate: 98%+
```

### **🔍 Implementation Template**

#### **Enhanced Keyword Generation Algorithm:**
```python
def generate_expanded_keywords(domain, capabilities):
    keywords = set()

    # 1. Base capabilities
    for capability in capabilities:
        keywords.add(capability)

    # 2. Direct variations
    for capability in capabilities:
        keywords.update(generate_variations(capability))

    # 3. Synonym expansion
    keywords.update(expand_with_synonyms(keywords, domain))

    # 4. Technical terms
    keywords.update(get_technical_terms(domain))

    # 5. Business language
    keywords.update(get_business_phrases(domain))

    # 6. Workflow patterns
    keywords.update(generate_workflow_patterns(domain))

    # 7. Natural language variations
    keywords.update(generate_natural_variations(domain))

    return list(keywords)
```

#### **Example: Data Extraction Skill**
```
Input Domain: "Data extraction and analysis from online sources"

Generated Keywords (55 total):
# Direct Variations (15)
extract data, extract and analyze data, extract and process data,
normalize data, normalize extracted data, analyze online data,
process web data, handle information from websites

# Synonym Expansions (12)
scrape data, get information, pull content, retrieve records,
harvest data, collect metrics, process information, handle data

# Technical Terms (10)
web scraping, data mining, API integration, ETL process, data extraction,
content parsing, information retrieval, data processing, web harvesting

# Business Language (8)
process business data, handle reports, analyze metrics, work with datasets,
manage information, extract insights, normalize business records

# Workflow Patterns (5)
daily data extraction, weekly report processing, monthly metrics analysis,
regular information handling, continuous data monitoring

# Natural Language (5)
get data from this site, process information here, analyze the content,
work with these records, handle this dataset
```

### **✅ Quality Assurance Checklist**

**Keyword Generation:**
- [ ] 50+ keywords generated for each skill
- [ ] All capability variations covered
- [ ] Synonym expansions included
- [ ] Technical and business terms added
- [ ] Workflow patterns implemented
- [ ] Natural language variations present

**Coverage Verification:**
- [ ] Test 20+ natural language variations
- [ ] All major use cases covered
- [ ] Technical terminology included
- [ ] Business language present
- [ ] No gaps in keyword coverage

**Testing Requirements:**
- [ ] 98%+ activation reliability achieved
- [ ] False negatives < 5%
- [ ] No activation for out-of-scope queries
- [ ] Consistent activation across variations

### Implementation in Agent-Skill-Creator

**Updated Phase 4 Process:**
1. **Generate base keywords** (traditional method)
2. **Apply systematic expansion** (enhanced method)
3. **Validate coverage** (minimum 50 keywords)
4. **Embed all keywords into the SKILL.md description field**
5. **Test natural language** (20+ variations)
6. **Verify activation reliability** (98%+ target)

> **IMPORTANT:** All keywords and activation data go into the SKILL.md `description` field. Do NOT create separate activation files, marketplace.json fields, or pattern files. The description IS the activation mechanism.

---

# Phase 4 Enhanced: Description-Based Activation

## How Skill Activation Works

The agent (Claude Code, VS Code Copilot, Cursor, etc.) reads the `description` field in SKILL.md frontmatter and uses natural language understanding to decide when to activate the skill. There is no separate activation file, no keywords file, and no regex matching layer.

The `description` field is the **only** activation mechanism. A well-crafted description with 50+ embedded keywords achieves 95%+ activation reliability.

> **CRITICAL:** Do NOT create `activation.keywords`, `activation.patterns`, `test_queries`, `usage.when_to_use`, or `usage.when_not_to_use` fields in marketplace.json or any other file. These are non-standard fields that **break Claude Code installation**. All activation data belongs in the SKILL.md `description` field.

---


## Writing Effective Descriptions

The description serves all activation purposes — keyword matching and natural language understanding — in a single field.

### Description Template

```yaml
description: >-
  {Primary use case in one sentence}. Activates for queries about
  {capability 1} ({synonyms}), {capability 2} ({synonyms}), and
  {capability 3} ({synonyms}). Supports {action verbs}: {action synonyms}.
  Uses {technology/API} to {what it does}. Does NOT activate for:
  {counter-examples}.
```

### Description Requirements

**Must Include:**
- Primary use case clearly stated upfront
- Each capability explicitly mentioned with synonyms in parentheses
- Action verbs the user might say
- Technology/API names
- 3-5 example phrasings embedded naturally
- 2-3 counter-examples (what this skill is NOT for)
- 50+ unique keywords woven into natural prose

**Length:** 200-500 characters. Longer than typical but necessary for reliable activation.

### Keyword Design Rules

**DO: Use Complete Phrases in the Description**
```
"technical analysis for stocks"
"analyze stock data"
"buy and sell signals"
```

**DON'T: Keyword-Stuff the Description**
```
"stock RSI MACD Bollinger buy sell signal compare rank" (not prose)
```

### Embedding Keywords Naturally

Take your keyword research from Steps 1-7 and weave them into coherent prose:

**Bad (keyword stuffing):**
```yaml
description: "stock analysis RSI MACD Bollinger buy sell signal compare rank chart patterns momentum moving average"
```

**Good (natural prose with keywords embedded):**
```yaml
description: >-
  Provides comprehensive technical analysis for stocks and ETFs using RSI
  (Relative Strength Index), MACD (Moving Average Convergence Divergence),
  Bollinger Bands, moving averages, and chart patterns. Generates buy and
  sell signals based on technical indicator combinations. Compares and ranks
  multiple stocks by momentum and technical strength. Does NOT activate for
  fundamental analysis (P/E ratios, earnings), news, or options pricing.
```

---

## Complete Example: stock-analyzer

### SKILL.md Frontmatter (the ONLY activation mechanism)

```yaml
---
name: stock-analyzer
description: >-
  Provides comprehensive technical analysis for stocks and ETFs using RSI
  (Relative Strength Index), MACD (Moving Average Convergence Divergence),
  Bollinger Bands, moving averages, and chart patterns. Generates buy and
  sell signals based on technical indicator combinations. Compares multiple
  stocks and ranks them by momentum and technical strength. Monitors stock
  performance and tracks price alerts. Activates when user asks to analyze
  stocks, calculate technical indicators, get trading signals, compare
  tickers, or assess market momentum. Does NOT activate for fundamental
  analysis (P/E ratios, earnings), news-based analysis, portfolio
  optimization, or options pricing.
version: 1.0.0
license: MIT
metadata:
  author: finance-team
  version: 1.0.0
---
```

**Why this achieves 95%+ activation:**
- Contains 60+ unique keywords naturally embedded
- All capabilities mentioned with synonyms
- Action verbs match how users phrase requests
- Counter-examples prevent false positives
- Technical terms (RSI, MACD, Bollinger) enable precise matching
- General terms ("technical analysis", "trading signals") catch broad queries

### Testing the Description

**Positive Tests (should activate):**
```
1. "Analyze AAPL stock using RSI" -> activates
2. "What's the MACD for Tesla?" -> activates
3. "Show me buy signals for tech stocks" -> activates
4. "Compare AAPL vs GOOGL using technical analysis" -> activates
5. "Moving average crossover for SPY" -> activates
6. "Bollinger Bands analysis for Bitcoin" -> activates
7. "Is TSLA overbought based on RSI?" -> activates
8. "Chart patterns for NVDA" -> activates
9. "Momentum indicators for tech stocks" -> activates
10. "Track AMZN for MACD crossover signals" -> activates
```

**Negative Tests (should NOT activate):**
```
1. "What's the P/E ratio of AAPL?" -> fundamental, not technical
2. "Latest news about TSLA?" -> news, not analysis
3. "Execute a buy order for NVDA" -> brokerage, not analysis
4. "Options strategies for AAPL" -> options, not indicators
```

---

## Validation & Testing

### Testing Process

**Minimum Test Coverage:**
- 10+ query variations per major capability
- Document all test queries in your SKILL.md body (under a Testing section)
- Manual testing of each variation
- No false positives in counter-examples

### Improving Activation Reliability

If a test query fails to activate the skill:

1. **Check if the query's key terms appear in the description.** If "momentum" isn't there but users ask about momentum, add it.
2. **Add synonyms in parentheses.** If users say "technical indicators" but the description only says "RSI, MACD", add the general term too.
3. **Add counter-examples.** If the skill activates for wrong queries, add "Does NOT activate for: {those cases}" to the description.

### Validation Checklist

```markdown
## Description Quality
- [ ] Primary use case stated upfront?
- [ ] All capabilities mentioned with synonyms?
- [ ] 50+ unique keywords embedded as natural prose?
- [ ] Action verbs included?
- [ ] Counter-examples documented?
- [ ] 200-500 characters length?

## Testing
- [ ] 10+ positive test queries per capability?
- [ ] All test queries activate the skill?
- [ ] Negative test queries do NOT activate?
- [ ] No false positives found?
- [ ] No false negatives found?
```

---

## Final Phase 4 Checklist

### Keyword Research (Steps 1-7)
- [ ] Domain entities listed (organizations, objects, metrics)
- [ ] Action verbs listed (analyze, compare, monitor, track)
- [ ] 50+ keywords generated via systematic expansion
- [ ] Question variations mapped
- [ ] Negative scope defined

### Description Writing
- [ ] All keywords embedded into SKILL.md `description` as natural prose
- [ ] Primary use case stated upfront
- [ ] All capabilities mentioned with synonyms
- [ ] Counter-examples documented ("Does NOT activate for")
- [ ] 200-500 characters length

### Testing
- [ ] 10+ positive test queries per capability
- [ ] Negative test queries for out-of-scope requests
- [ ] All test queries activate correctly
- [ ] Counter-examples correctly do NOT activate
- [ ] No false positives found

---
