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

### **🎯 Implementation in Agent-Skill-Creator**

**Updated Phase 4 Process:**
1. **Generate base keywords** (traditional method)
2. **Apply systematic expansion** (enhanced method)
3. **Validate coverage** (minimum 50 keywords)
4. **Test natural language** (20+ variations)
5. **Verify activation reliability** (98%+ target)

**Template Updates:**
- Enhanced keyword generation in phase4-detection.md
- Expanded pattern libraries in activation-patterns-guide.md
- Rich examples in marketplace-robust-template.json

---

# 🎯 **Phase 4 Enhanced v3.0: 3-Layer Activation System**

## Overview: Why 3 Layers?

**Problem:** Skills with only description-based activation can:
- Miss valid user queries (false negatives)
- Activate for wrong queries (false positives)
- Be unpredictable across phrasings

**Solution:** Implement activation in **3 complementary layers**:

```
Layer 1: Keywords     → High precision, moderate coverage
Layer 2: Patterns     → High coverage, good precision
Layer 3: Description  → Full coverage, Claude NLU fallback
```

**Result:** 95%+ activation reliability!

---

## 🔑 Layer 1: Structured Keywords (marketplace.json)

### Purpose
Provide **exact phrase matching** for common, specific queries.

### Structure in marketplace.json

```json
{
  "activation": {
    "keywords": [
      "complete phrase 1",
      "complete phrase 2",
      "complete phrase 3",
      // ... 10-15 total
    ]
  }
}
```

### Keyword Design Rules

#### ✅ DO: Use Complete Phrases
```json
✅ "create an agent for"
✅ "analyze stock data"
✅ "compare year over year"
```

#### ❌ DON'T: Use Single Words
```json
❌ "create"      // Too generic
❌ "agent"       // Too broad
❌ "data"        // Meaningless alone
```

### Keyword Categories (10-15 keywords minimum)

**Category 1: Action + Entity (5-7 keywords)**
```json
[
  "create an agent for",
  "create a skill for",
  "build an agent for",
  "develop a skill for",
  "make an agent that"
]
```

**Category 2: Workflow Patterns (3-5 keywords)**
```json
[
  "automate this workflow",
  "automate this process",
  "every day I have to",
  "daily I need to"
]
```

**Category 3: Domain-Specific (2-3 keywords)**
```json
[
  "stock market analysis",  // For finance skill
  "crop monitoring data",   // For agriculture skill
  "pdf text extraction"     // For document skill
]
```

### Keyword Generation Process

**Step 1:** List all primary capabilities
```
Skill: us-crop-monitor
Capabilities:
1. Crop condition monitoring
2. Harvest progress tracking
3. Yield data analysis
```

**Step 2:** Create 3-4 keywords per capability
```
Capability 1 → Keywords:
- "crop condition data"
- "crop health monitoring"
- "condition ratings for crops"

Capability 2 → Keywords:
- "harvest progress report"
- "planting progress data"
- "percent harvested"

Capability 3 → Keywords:
- "crop yield analysis"
- "productivity data"
- "bushels per acre"
```

**Step 3:** Add action variations
```
- "analyze crop conditions"
- "monitor harvest progress"
- "track planting status"
```

**Result:** 10-15 keywords covering main use cases

---

## 🔍 Layer 2: Regex Patterns (marketplace.json)

### Purpose
Capture **flexible variations** while maintaining specificity.

### Structure in marketplace.json

```json
{
  "activation": {
    "patterns": [
      "(?i)(verb1|verb2)\\s+.*\\s+(entity|object)",
      "(?i)(action)\\s+(context)\\s+(target)",
      // ... 5-7 total
    ]
  }
}
```

### Pattern Design Rules

#### Pattern Anatomy
```regex
(?i)                    → Case insensitive
(verb1|verb2|verb3)     → Action verbs (create, build, make)
\s+                     → Whitespace (required)
(an?\s+)?               → Optional article (a, an)
(entity)                → Target entity
\s+(for|to|that)        → Context connector
```

### Pattern Categories (5-7 patterns minimum)

**Pattern 1: Action + Object**
```regex
(?i)(create|build|develop|make)\s+(an?\s+)?(agent|skill)\s+(for|to|that)
```
Matches:
- "create an agent for"
- "build a skill to"
- "develop agent that"

**Pattern 2: Automation Request**
```regex
(?i)(automate|automation)\s+(this\s+)?(workflow|process|task|repetitive)
```
Matches:
- "automate this workflow"
- "automation process"
- "automate task"

**Pattern 3: Repetitive Workflow**
```regex
(?i)(every day|daily|repeatedly)\s+(I|we)\s+(have to|need to|do|must)
```
Matches:
- "every day I have to"
- "daily we need to"
- "repeatedly I must"

**Pattern 4: Transformation**
```regex
(?i)(turn|convert|transform)\s+(this\s+)?(process|workflow|task)\s+into\s+(an?\s+)?agent
```
Matches:
- "turn this process into an agent"
- "convert workflow to agent"
- "transform task into agent"

**Pattern 5: Domain-Specific**
```regex
(?i)(analyze|analysis|monitor|track)\s+.*\s+(crop|stock|customer|data)
```
Matches:
- "analyze crop conditions"
- "monitor stock performance"
- "track customer behavior"

**Pattern 6-7:** Add more based on specific skill needs

### Pattern Testing

**Test each pattern independently:**

```markdown
Pattern: (?i)(create|build)\s+(an?\s+)?agent\s+for

Test queries:
✅ "create an agent for processing PDFs"
✅ "build agent for data analysis"
✅ "Create a Agent For automation"
❌ "I want to create something"  // No "agent"
❌ "agent creation guide"        // No action verb
```

### Common Regex Components

**Verbs - Action:**
```regex
(create|build|develop|make|generate|design)
(analyze|analysis|monitor|track|measure)
(compare|rank|sort|list|show)
(automate|automation|streamline)
```

**Entities:**
```regex
(agent|skill|workflow|process|task)
(crop|stock|customer|product|invoice)
(data|report|dashboard|analysis)
```

**Connectors:**
```regex
(for|to|that|with|using|from)
(about|on|regarding|concerning)
```

---

## 📝 Layer 3: Description + NLU (Existing, Enhanced)

### Purpose
Provide **Claude-interpretable** context for cases not covered by keywords/patterns.

### Enhanced Description Template

```yaml
description: |
  This skill should be used when the user {primary use case}.

  Activates for queries about:
  - {capability 1} ({synonyms, keywords})
  - {capability 2} ({synonyms, keywords})
  - {capability 3} ({synonyms, keywords})

  Supports {actions list}: {action synonyms}.

  Uses {technology/API} to {what it does}.

  Examples: {example queries}.

  Does NOT activate for: {counter-examples}.
```

### Enhanced Requirements

**Must Include:**
- ✅ All 60+ keywords from Step 2.5
- ✅ Each capability explicitly mentioned
- ✅ Synonyms in parentheses
- ✅ Technology/API names
- ✅ 3-5 example queries
- ✅ 2-3 counter-examples

**Length:** 300-500 characters (yes, longer than typical!)

---

## ✅ Step 8: Validation & Testing (NEW)

### Testing Requirements

**Minimum Test Coverage:**
- 10+ query variations per major capability
- All test queries documented in marketplace.json
- Manual testing of each variation
- No false positives in counter-examples

### Test Query Structure in marketplace.json

```json
{
  "test_queries": [
    "Query variation 1 (tests keyword X)",
    "Query variation 2 (tests pattern Y)",
    "Query variation 3 (tests description)",
    "Query variation 4 (natural phrasing)",
    "Query variation 5 (shortened form)",
    "Query variation 6 (verbose form)",
    "Query variation 7 (domain synonym)",
    "Query variation 8 (action synonym)",
    "Query variation 9 (multilingual variant)",
    "Query variation 10 (edge case)"
  ]
}
```

### Validation Checklist

```markdown
## Layer 1: Keywords Validation
- [ ] 10-15 keywords defined?
- [ ] Keywords are complete phrases (not single words)?
- [ ] Keywords cover main use cases?
- [ ] No overly generic keywords?

## Layer 2: Patterns Validation
- [ ] 5-7 patterns defined?
- [ ] Patterns require action verbs?
- [ ] Patterns tested independently?
- [ ] No overly broad patterns?

## Layer 3: Description Validation
- [ ] 60+ unique keywords included?
- [ ] All capabilities mentioned?
- [ ] Synonyms provided?
- [ ] Counter-examples listed?

## Integration Testing
- [ ] 10+ test queries per capability?
- [ ] All test queries activate skill?
- [ ] Counter-examples don't activate?
- [ ] No conflicts with other skills?
```

### Test Report Template

```markdown
## Activation Test Report

**Skill:** {skill-name}
**Date:** {date}
**Tester:** {name}

### Test Results

**Keywords (Layer 1):**
- Total keywords: {count}
- Tested: {count}
- Pass rate: {X/Y}%

**Patterns (Layer 2):**
- Total patterns: {count}
- Tested: {count}
- Pass rate: {X/Y}%

**Test Queries:**
- Total test queries: {count}
- Activated correctly: {count}
- False negatives: {count}
- False positives: {count}

### Issues Found
1. {Issue description}
2. {Issue description}

### Recommendations
1. {Recommendation}
2. {Recommendation}
```

---

## 🎯 Complete Example: Robust Detection Implementation

### Example Skill: stock-analyzer-cskill

**marketplace.json:**

```json
{
  "name": "stock-analyzer-cskill",
  "description": "Technical stock analysis using indicators",

  "activation": {
    "keywords": [
      "analyze stock",
      "stock technical analysis",
      "RSI for stocks",
      "MACD analysis",
      "moving average crossover",
      "Bollinger Bands",
      "buy sell signals",
      "technical indicators",
      "chart patterns",
      "stock momentum"
    ],

    "patterns": [
      "(?i)(analyze|analysis)\\s+.*\\s+(stock|stocks|ticker|equity)",
      "(?i)(technical|chart)\\s+(analysis|indicators?)\\s+(for|of)",
      "(?i)(RSI|MACD|moving average|Bollinger|momentum)\\s+(for|of|analysis)",
      "(?i)(buy|sell)\\s+(signal|signals|recommendation)\\s+(for|using)",
      "(?i)(compare|rank)\\s+.*\\s+stocks?\\s+(using|with|by)"
    ]
  },

  "usage": {
    "example": "Analyze AAPL using RSI and MACD indicators",
    "when_to_use": [
      "User asks for technical stock analysis",
      "User wants to analyze indicators (RSI, MACD, etc.)",
      "User needs buy/sell signals based on technicals",
      "User wants to compare stocks using technical metrics"
    ],
    "when_not_to_use": [
      "Fundamental analysis (P/E ratios, earnings)",
      "News-based analysis",
      "Portfolio optimization",
      "Options pricing"
    ]
  },

  "test_queries": [
    "Analyze AAPL stock using RSI",
    "What's the MACD for Tesla?",
    "Show me technical indicators for MSFT",
    "Buy or sell signals for Google stock?",
    "Moving average crossover for SPY",
    "Bollinger Bands analysis for Bitcoin",
    "Compare technical strength of AAPL vs MSFT",
    "Is TSLA overbought based on RSI?",
    "Chart patterns for NVDA",
    "Momentum indicators for tech stocks"
  ]
}
```

---

## 📋 Final Phase 4 Checklist (Enhanced v3.0)

### Traditional Detection (Steps 1-7)
- [ ] Entities listed
- [ ] Actions/verbs listed
- [ ] Question variations mapped
- [ ] Negative scope defined
- [ ] Description created
- [ ] Keywords documented

### Layer 1: Keywords
- [ ] 10-15 keywords defined
- [ ] Keywords are complete phrases
- [ ] Keywords categorized (action, workflow, domain)
- [ ] Keywords added to marketplace.json

### Layer 2: Patterns
- [ ] 5-7 regex patterns defined
- [ ] Patterns require action verbs + context
- [ ] Each pattern tested individually
- [ ] Patterns added to marketplace.json

### Layer 3: Description
- [ ] 60+ unique keywords included
- [ ] All capabilities mentioned with synonyms
- [ ] Example queries provided
- [ ] Counter-examples documented

### Testing & Validation
- [ ] 10+ test queries per capability
- [ ] All queries added to test_queries array
- [ ] Manual testing completed
- [ ] No false positives/negatives found
- [ ] Test report documented

### Integration
- [ ] when_to_use / when_not_to_use defined
- [ ] No conflicts with other skills identified
- [ ] Activation priority appropriate
- [ ] Documentation complete

---

## 💡 Quick Reference: 3-Layer Activation Checklist

```markdown
✅ **Layer 1: Keywords** (10-15 keywords)
   - Complete phrases (not single words)
   - Cover main use cases
   - Categorized by type

✅ **Layer 2: Patterns** (5-7 regex)
   - Require action verbs
   - Flexible but specific
   - Tested independently

✅ **Layer 3: Description** (300-500 chars)
   - 60+ unique keywords
   - All capabilities mentioned
   - Examples + counter-examples

✅ **Testing** (10+ variations)
   - All test queries activate
   - No false positives
   - Documented results
```

**Remember:** More layers = More reliability = Happier users!

---

## 🧠 **NEW: Context-Aware Detection (Layer 4)**

### **Enhanced 4-Layer Detection System**

The Agent-Skill-Creator v3.1 now includes a fourth layer for context-aware filtering, making the system **4-Layer Detection**:

```
Layer 1: Keywords          → Direct keyword matching
Layer 2: Patterns          → Regex pattern matching
Layer 3: Description + NLU → Semantic understanding
Layer 4: Context-Aware     → Contextual filtering (NEW)
```

### **Context-Aware Detection Process**

#### **Step 4A: Context Extraction**
1. **Domain Context**: Identify primary and secondary domains
2. **Task Context**: Determine user's current task and stage
3. **Intent Context**: Extract primary and secondary intents
4. **Conversational Context**: Analyze conversation history and coherence

#### **Step 4B: Context Relevance Analysis**
1. **Domain Relevance**: Match query domains with skill's expected domains
2. **Task Relevance**: Match user tasks with skill's supported tasks
3. **Capability Relevance**: Match required capabilities with skill's capabilities
4. **Context Coherence**: Evaluate conversation consistency

#### **Step 4C: Negative Context Detection**
1. **Excluded Domains**: Check for explicitly excluded domains
2. **Conflicting Intents**: Identify conflicting user intents
3. **Inappropriate Contexts**: Detect tutorial, help, or debugging contexts
4. **Resource Constraints**: Check for unavailable resources or permissions

#### **Step 4D: Context-Aware Decision**
1. **Relevance Scoring**: Calculate weighted context relevance score
2. **Threshold Comparison**: Compare against confidence thresholds
3. **Negative Filtering**: Apply negative context filters
4. **Final Decision**: Make context-aware activation decision

### **Context-Aware Configuration**

```json
{
  "activation": {
    "keywords": [...],
    "patterns": [...],

    "_comment": "Context-aware filtering (v1.0)",
    "contextual_filters": {
      "required_context": {
        "domains": ["finance", "trading"],
        "tasks": ["analysis", "calculation"],
        "confidence_threshold": 0.8
      },
      "excluded_context": {
        "domains": ["education", "tutorial"],
        "tasks": ["help", "explanation"]
      },
      "activation_rules": {
        "min_relevance_score": 0.75,
        "max_negative_score": 0.3
      }
    }
  }
}
```

### **Context Testing Examples**

**Positive Context (Should Activate):**
```json
{
  "query": "Analyze AAPL stock using RSI indicator",
  "context": {
    "domain": "finance",
    "task": "analysis",
    "intent": "analyze"
  },
  "expected": true,
  "reason": "Perfect domain and task match"
}
```

**Negative Context (Should NOT Activate):**
```json
{
  "query": "Explain what stock analysis is",
  "context": {
    "domain": "education",
    "task": "explanation",
    "intent": "learn"
  },
  "expected": false,
  "reason": "Educational context, not task execution"
}
```

### **Context-Aware Validation Checklist**

```markdown
## Layer 4: Context-Aware Validation
- [ ] Required domains defined in contextual_filters?
- [ ] Excluded domains defined to prevent false positives?
- [ ] Confidence thresholds set appropriately?
- [ ] Context weights configured for domain needs?
- [ ] Negative context rules implemented?
- [ ] Context test cases generated and validated?
- [ ] False positive rate measured <1%?
- [ ] Context analysis time <100ms?
```

### **Expected Performance Improvements**

- **False Positive Rate**: 2% → **<1%**
- **Context Precision**: 60% → **85%**
- **User Satisfaction**: 85% → **95%**
- **Overall Reliability**: 98% → **99.5%**

**Enhanced Remember:** 4 Layers = Maximum Reliability = Exceptional UX!
