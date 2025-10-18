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
