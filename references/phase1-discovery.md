# Phase 1: Discovery and API Research

## Objective

Research and **DECIDE** autonomously which API or data source to use for the agent.

## Detailed Process

### Step 1: Identify Domain

From user input, extract the main domain:

| User Input | Identified Domain |
|------------------|---------------------|
| "US crop data" | Agriculture (US) |
| "stock market analysis" | Finance / Stock Market |
| "global climate data" | Climate / Meteorology |
| "economic indicators" | Economy / Macro |
| "commodity data" | Trading / Commodities |

### Step 2: Search Available APIs

For the identified domain, use WebSearch to find public APIs:

**Search queries**:
```
"[domain] API free public data"
"[domain] government API documentation"
"best API for [domain] historical data"
"[domain] open data sources"
```

**Example (US agriculture)**:
```bash
WebSearch: "US agriculture API free historical data"
WebSearch: "USDA API documentation"
WebSearch: "agricultural statistics API United States"
```

**Typical result**: 5-10 candidate APIs

### Step 3: Research Documentation

For each candidate API, use WebFetch to load:
- Homepage/overview
- Getting started guide
- API reference
- Rate limits and pricing

**Extract information**:

```markdown
## API 1: [Name]

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
- Throttling: [yes/no]

**Quality**:
- Source: [official government / private]
- Reliability: [high/medium/low]
- Update frequency: [frequency]

**Documentation**:
- Quality: [excellent/good/poor]

### Step 4: API Capability Inventory (NEW v2.0 - CRITICAL!)

**OBJECTIVE:** Ensure the skill uses 100% of API capabilities, not just the basics!

**LEARNING:** us-crop-monitor v1.0 used only CONDITION (1 of 5 NASS metrics).
v2.0 had to add PROGRESS, YIELD, PRODUCTION, AREA (+3,500 lines of rework).

**Process:**

**Step 4.1: Complete Inventory**

For the chosen API, catalog ALL data types:

```markdown
## Complete Inventory - {API Name}

**Available Metrics/Endpoints:**

| Endpoint/Metric | Returns | Granularity | Coverage | Value |
|-----------------|---------------|---------------|-----------|-------|
| {metric1}       | {description}   | {daily/weekly}| {geo}     | ⭐⭐⭐⭐⭐ |
| {metric2}       | {description}   | {monthly}     | {geo}     | ⭐⭐⭐⭐⭐ |
| {metric3}       | {description}   | {annual}      | {geo}     | ⭐⭐⭐⭐  |
...

**Real Example (NASS):**

| Metric Type    | Data               | Frequency | Value    | Implement? |
|----------------|--------------------| ----------|----------|------------|
| CONDITION      | Quality ratings    | Weekly    | ⭐⭐⭐⭐⭐ | ✅ YES     |
| PROGRESS       | % planted/harvested| Weekly    | ⭐⭐⭐⭐⭐ | ✅ YES     |
| YIELD          | Bu/acre            | Monthly   | ⭐⭐⭐⭐⭐ | ✅ YES     |
| PRODUCTION     | Total bushels      | Monthly   | ⭐⭐⭐⭐⭐ | ✅ YES     |
| AREA           | Acres planted      | Annual    | ⭐⭐⭐⭐  | ✅ YES     |
| PRICE          | $/bushel           | Monthly   | ⭐⭐⭐    | ⚪ v2.0    |
```

**Step 4.2: Coverage Decision**

**GOLDEN RULE:**
- If metric has ⭐⭐⭐⭐ or ⭐⭐⭐⭐⭐ value → Implement in v1.0
- If API has 5 high-value metrics → Implement all 5!
- Never leave >50% of API unused without strong justification

**Step 4.3: Document Decision**

In DECISIONS.md:
```markdown
## API Coverage Decision

API {name} offers {N} types of metrics.

**Implemented in v1.0 ({X} of {N}):**
- {metric1} - {justification}
- {metric2} - {justification}
...

**Not implemented ({Y} of {N}):**
- {metricZ} - {why not} (planned for v2.0)

**Coverage:** {X/N * 100}% = {evaluation}
- If < 70%: Clearly explain why low coverage
- If > 70%: ✅ Good coverage
```

**Output of this phase:** Exact list of all `get_*()` methods to implement
- Examples: [many/few/none]
- SDKs: [Python/R/None]

**Ease of Use**:
- Format: JSON / CSV / XML
- Structure: [simple/complex]
- Quirks: [any strange behavior?]
```

### Step 4: Compare Options

Create comparison table:

| API | Coverage | Cost | Rate Limit | Quality | Docs | Ease | Score |
|-----|-----------|-------|------------|-----------|------|------------|-------|
| API 1 | ⭐⭐⭐⭐⭐ | Free | 1000/day | Official | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 9.2/10 |
| API 2 | ⭐⭐⭐⭐ | $49/mo | Unlimited | Private | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 7.8/10 |
| API 3 | ⭐⭐⭐ | Free | 100/day | Private | ⭐⭐ | ⭐⭐⭐ | 5.5/10 |

**Scoring criteria**:
- Coverage (fit with need): 30% weight
- Cost (prefer free): 20% weight
- Rate limit (sufficient?): 15% weight
- Quality (official > private): 15% weight
- Documentation (facilitates implementation): 10% weight
- Ease of use (format, structure): 10% weight

### Step 5: DECIDE

**Consider user constraints**:
- Mentioned "free"? → Eliminate paid options
- Mentioned "10+ years historical data"? → Check coverage
- Mentioned "real-time"? → Prioritize streaming APIs

**Apply logic**:
1. Eliminate APIs that violate constraints
2. Of remaining, choose highest score
3. If tie, prefer:
   - Official > private
   - Better documentation
   - Easier to use

**FINAL DECISION**:

```markdown
## Selected API: [API Name]

**Score**: X.X/10

**Justification**:
- ✅ Coverage: [specific details]
- ✅ Cost: [free/paid + details]
- ✅ Rate limit: [number] requests/day (sufficient for [estimated usage])
- ✅ Quality: [official/private + reliability]
- ✅ Documentation: [quality + examples]
- ✅ Ease of use: [format, structure]

**Fit with requirements**:
- Constraint 1 (e.g., free): ✅ Met
- Constraint 2 (e.g., 10+ years history): ✅ Met (since [year])
- Primary need (e.g., crop production): ✅ Covered

**Alternatives Considered**:

**API X**: Score 7.5/10
- Rejected because: [specific reason]
- Trade-off: [what we lose vs gain]

**API Y**: Score 6.2/10
- Rejected because: [reason]

**Conclusion**:
[API Name] is the best option because [1-2 sentence synthesis].
```

### Step 6: Research Technical Details

After deciding, dive deep into documentation:

**Load via WebFetch**:
- Getting started guide
- Complete API reference
- Authentication guide
- Rate limiting details
- Best practices

**Extract for implementation**:

```markdown
## Technical Details - [API]

### Authentication

**Method**: API key in header
**Header**: `X-Api-Key: YOUR_KEY`
**Obtaining key**:
1. [step 1]
2. [step 2]
3. [step 3]

### Main Endpoints

**Endpoint 1**: [Name]
- **URL**: `GET https://api.example.com/v1/endpoint`
- **Parameters**:
  - `param1` (required): [description, type, example]
  - `param2` (optional): [description, type, default]
- **Response** (200 OK):
```json
{
  "data": [...],
  "meta": {...}
}
```
- **Errors**:
  - 400: [when occurs, how to handle]
  - 401: [when occurs, how to handle]
  - 429: [rate limit, how to handle]

**Example request**:
```bash
curl -H "X-Api-Key: YOUR_KEY" \
  "https://api.example.com/v1/endpoint?param1=value"
```

[Repeat for all relevant endpoints]

### Rate Limiting

- Limit: [number] requests per [period]
- Response headers:
  - `X-RateLimit-Limit`: Total limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp
- Behavior when exceeded: [429 error, throttling, ban?]
- Best practice: [how to implement rate limiting]

### Quirks and Gotchas

**Quirk 1**: Values come as strings with formatting
- Example: `"2,525,000"` instead of `2525000`
- Solution: Remove commas before converting

**Quirk 2**: Suppressed data marked as "(D)"
- Meaning: Withheld to avoid disclosing data
- Solution: Treat as NULL, signal to user

**Quirk 3**: [other non-obvious behavior]
- Solution: [how to handle]

### Performance Tips

- Historical data doesn't change → cache permanently
- Recent data may be revised → short cache (7 days)
- Use pagination parameters if large response
- Make parallel requests when possible (respecting rate limit)
```

### Step 7: Document for Later Use

Save everything in `references/api-guide.md` of the agent to be created.

## Discovery Examples

### Example 1: US Agriculture

**Input**: "US crop data"

**Research**:
```
WebSearch: "USDA API agricultural data"
→ Found: NASS QuickStats, ERS, FAS

WebFetch: https://quickstats.nass.usda.gov/api
→ Free, data since 1866, 1000/day rate limit

WebFetch: https://www.ers.usda.gov/developer/
→ Free, economic focus, less granular

WebFetch: https://apps.fas.usda.gov/api
→ International focus, not domestic
```

**Comparison**:
| API | Coverage (US domestic) | Cost | Production Data | Score |
|-----|---------------------------|-------|-------------------|-------|
| NASS | ⭐⭐⭐⭐⭐ (excellent) | Free | ⭐⭐⭐⭐⭐ | 9.5/10 |
| ERS | ⭐⭐⭐⭐ (good) | Free | ⭐⭐⭐ (economic) | 7.0/10 |
| FAS | ⭐⭐ (international) | Free | ⭐⭐ (global) | 4.0/10 |

**DECISION**: NASS QuickStats API
- Best coverage for US domestic agriculture
- Free with reasonable rate limit
- Complete production, area, yield data

### Example 2: Stock Market

**Input**: "technical stock analysis"

**Research**:
```
WebSearch: "stock market API free historical data"
→ Alpha Vantage, Yahoo Finance, IEX Cloud, Polygon.io

WebFetch: Alpha Vantage docs
→ Free, 5 requests/min, 500/day

WebFetch: Yahoo Finance (yfinance)
→ Free, unlimited but unofficial

WebFetch: IEX Cloud
→ Freemium, good docs, 50k free credits/month
```

**Comparison**:
| API | Data | Cost | Rate Limit | Official | Score |
|-----|-------|-------|------------|---------|-------|
| Alpha Vantage | Complete | Free | 500/day | ⭐⭐⭐ | 8.0/10 |
| Yahoo Finance | Complete | Free | Unlimited | ❌ Unofficial | 7.5/10 |
| IEX Cloud | Excellent | Freemium | 50k/month | ⭐⭐⭐⭐ | 8.5/10 |

**DECISION**: IEX Cloud (free tier)
- Official and reliable
- 50k requests/month sufficient
- Excellent documentation
- Complete data (OHLCV + volume)

### Example 3: Global Climate

**Input**: "global climate data"

**Research**:
```
WebSearch: "weather API historical data global"
→ NOAA, OpenWeather, Weather.gov, Meteostat

[Research each one...]
```

**DECISION**: NOAA Climate Data Online (CDO) API
- Official (US government)
- Free
- Global and historical coverage (1900+)
- Rate limit: 1000/day

## Decision Documentation

Create `DECISIONS.md` file in agent:

```markdown
# Architecture Decisions

## Date: [creation date]

## Phase 1: API Selection

### Chosen API

**[API Name]**

### Selection Process

**APIs Researched**: [list]

**Evaluation Criteria**:
1. Data coverage (fit with need)
2. Cost (preference for free)
3. Rate limits (viability)
4. Quality (official > private)
5. Documentation (facilitates development)

### Comparison

[Comparison table]

### Final Justification

[2-3 paragraphs explaining why this API was chosen]

### Trade-offs

**What we gain**:
- [benefit 1]
- [benefit 2]

**What we lose** (vs alternatives):
- [accepted limitation 1]
- [accepted limitation 2]

### Technical Details

[Summary of endpoints, authentication, rate limits, etc]

**Complete documentation**: See `references/api-guide.md`
```

## Phase 1 Checklist

Before proceeding to Phase 2, verify:

- [ ] Research completed (WebSearch + WebFetch)
- [ ] Minimum 3 APIs compared
- [ ] Decision made with clear justification
- [ ] User constraints respected
- [ ] Technical details extracted
- [ ] DECISIONS.md created
- [ ] Ready for analysis design
