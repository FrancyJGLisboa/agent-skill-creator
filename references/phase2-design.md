# Phase 2: Analysis Design

## Objective

**DEFINE** autonomously which analyses the agent will perform and how.

## Detailed Process

### Step 1: Brainstorm Use Cases

From the workflow described by the user, think of typical questions they will ask.

**Technique**: "If I were this user, what would I ask?"

**Example (US agriculture)**:

User said: "download crop data, compare year vs year, make rankings"

**Questions they likely ask**:
1. "What's the corn production in 2023?"
2. "How's soybean compared to last year?"
3. "Did production grow or fall?"
4. "How much did it grow?"
5. "Does growth come from area or productivity?"
6. "Which states produce most wheat?"
7. "Top 5 soybean producers"
8. "Did the ranking change vs last year?"
9. "Production trend last 5 years?"
10. "Forecast for next year?"
11. "Average US yield"
12. "Which state has best productivity?"
13. "Did planted area increase?"
14. "Compare Midwest vs South"
15. "Production by region"

**Objective**: List 15-20 typical questions

### Step 2: Group by Analysis Type

Group similar questions:

**Group 1: Simple Queries** (fetching + formatting)
- Questions: 1, 11, 13
- Required analysis: **Data Retrieval**
- Complexity: Low

**Group 2: Temporal Comparisons** (YoY)
- Questions: 2, 3, 4, 5
- Required analysis: **YoY Comparison + Decomposition**
- Complexity: Medium

**Group 3: Rankings** (sorting + share)
- Questions: 6, 7, 8
- Required analysis: **State Ranking**
- Complexity: Medium

**Group 4: Trends** (time series)
- Questions: 9
- Required analysis: **Trend Analysis**
- Complexity: Medium-High

**Group 5: Projections** (forecasting)
- Questions: 10
- Required analysis: **Forecasting**
- Complexity: High

**Group 6: Geographic Aggregations**
- Questions: 12, 14, 15
- Required analysis: **Regional Aggregation**
- Complexity: Medium

### Step 3: Prioritize Analyses

**Prioritization criteria**:
1. **Frequency of use** (based on described workflow)
2. **Analytical value** (insight vs effort)
3. **Implementation complexity** (easier first)
4. **Dependencies** (does one analysis depend on another?)

**Scoring**:

| Analysis | Frequency | Value | Ease | Score |
|---------|------------|-------|------------|-------|
| YoY Comparison | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 9.3/10 |
| State Ranking | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 9.3/10 |
| Regional Agg | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 8.0/10 |
| Trend Analysis | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 7.3/10 |
| Data Retrieval | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 8.3/10 |
| Forecasting | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | 5.3/10 |

**DECISION**: Implement top 5
1. YoY Comparison (9.3)
2. State Ranking (9.3)
3. Data Retrieval (8.3)
4. Regional Aggregation (8.0)
5. Trend Analysis (7.3)

**Don't implement initially** (can add later):
- Forecasting (5.3) - complex, occasional use

### Step 4: Specify Each Analysis

For each selected analysis:

```markdown
## Analysis: [Name]

**Objective**: [What it does in 1 sentence]

**When to use**: [Types of questions that trigger it]

**Required inputs**:
- Input 1: [type, description]
- Input 2: [type, description]

**Expected outputs**:
- Output 1: [type, description]
- Output 2: [type, description]

**Methodology**:

[Explanation in natural language]

**Formulas**:
```
Formula 1 = ...
Formula 2 = ...
```

**Data transformations**:
1. [Transformation 1]
2. [Transformation 2]

**Validations**:
- Validation 1: [criteria]
- Validation 2: [criteria]

**Interpretation**:
- If result > X: [interpretation]
- If result < Y: [interpretation]

**Concrete example**:

Input:
- Commodity: Corn
- Year current: 2023
- Year previous: 2022

Processing:
- Fetch 2023 production: 15.3B bu
- Fetch 2022 production: 13.7B bu
- Calculate: (15.3 - 13.7) / 13.7 = +11.7%

Output:
```json
{
  "commodity": "CORN",
  "year_current": 2023,
  "year_previous": 2022,
  "production_current": 15.3,
  "production_previous": 13.7,
  "change_absolute": 1.6,
  "change_percent": 11.7,
  "interpretation": "significant_increase"
}
```

Response to user:
"Corn production grew 11.7% in 2023 vs 2022 (15.3B bu vs 13.7B bu)."
```

### Step 5: Specify Methodologies

For quantitative analyses, detail methodology:

**Example: YoY Decomposition**

```markdown
### Growth Decomposition

**Objective**: Understand how much of production growth comes from:
- Planted area increase (extensive)
- Productivity/yield increase (intensive)

**Mathematics**:

Production = Area × Yield

Δ Production = Δ Area × Yield(t-1) + Area(t-1) × Δ Yield + Δ Area × Δ Yield

Interaction term usually small, so approximation:

Δ Production ≈ Δ Area × Yield(t-1) + Area(t-1) × Δ Yield

**Percentage contributions**:

Contrib_Area = (Δ Area% / Δ Production%) × 100
Contrib_Yield = (Δ Yield% / Δ Production%) × 100

**Interpretation**:

- Contrib_Area > 60%: **Extensive growth**
  → Area expansion is main driver
  → Agricultural frontier expanding

- Contrib_Yield > 60%: **Intensive growth**
  → Technology improvement is main driver
  → Productivity/ha increasing

- Both ~50%: **Balanced growth**

**Validation**:

Check: Production(t) ≈ Area(t) × Yield(t) (margin 1%)
Check: Contrib_Area + Contrib_Yield ≈ 100% (margin 5%)

**Example**:

Soybeans 2023 vs 2022:
- Δ Production: +12.4%
- Δ Area: +6.1%
- Δ Yield: +7.6%

Contrib_Area = (6.1 / 12.4) × 100 = 49%
Contrib_Yield = (7.6 / 12.4) × 100 = 61%

**Interpretation**: Intensive growth (61% from yield).
Technology and management improving.
```

### Step 6: Document Analyses

Save all specifications in `references/analysis-methods.md` of the agent.

## Phase 2 Checklist

- [ ] 15+ typical questions listed
- [ ] Questions grouped by analysis type
- [ ] 4-6 analyses prioritized (with scoring)
- [ ] Each analysis specified (objective, inputs, outputs, methodology)
- [ ] Methodologies detailed with formulas
- [ ] Validations defined
- [ ] Interpretations specified
- [ ] Concrete examples included
