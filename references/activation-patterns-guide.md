# Activation Patterns Guide

**Version:** 1.0
**Purpose:** Library of proven regex patterns for skill activation

---

## Overview

This guide provides reusable regex patterns for Layer 2 (Patterns) of the 3-Layer Activation System. All patterns are tested and production-ready.

### Pattern Structure

```regex
(?i)                          → Case insensitive flag
(verb|synonyms)               → Action verb group
\s+                           → Required whitespace
(optional\s+)?                → Optional modifiers
(entity|object)               → Target entity
\s+(connector)                → Context connector
```

---

## 📚 Pattern Library by Category

### 1. Creation Patterns

#### Pattern 1.1: Agent/Skill Creation
```regex
(?i)(create|build|develop|make|generate|design)\s+(an?\s+)?(agent|skill|workflow)\s+(for|to|that)
```

**Matches:**
- "create an agent for"
- "build a skill to"
- "develop agent that"
- "make a workflow for"
- "generate skill to"

**Use For:** Skills that create agents, automation, or workflows

---

#### Pattern 1.2: Custom Solution Creation
```regex
(?i)(create|build)\s+a?\s+custom\s+(solution|tool|automation|system)\s+(for|to)
```

**Matches:**
- "create a custom solution for"
- "build custom tool to"
- "create custom automation for"

**Use For:** Custom development skills

---

### 2. Automation Patterns

#### Pattern 2.1: Direct Automation Request
```regex
(?i)(automate|automation|streamline)\s+(this\s+)?(workflow|process|task|job|repetitive)
```

**Matches:**
- "automate this workflow"
- "automation process"
- "streamline task"
- "automate repetitive job"

**Use For:** Workflow automation skills

---

#### Pattern 2.2: Repetitive Task Pattern
```regex
(?i)(every day|daily|repeatedly|constantly|regularly)\s+(I|we)\s+(have to|need to|do|must)
```

**Matches:**
- "every day I have to"
- "daily we need to"
- "repeatedly I do"
- "regularly we must"

**Use For:** Repetitive workflow detection

---

#### Pattern 2.3: Need Automation
```regex
(?i)need\s+to\s+automate\s+.*
```

**Matches:**
- "need to automate this process"
- "need to automate data entry"
- "need to automate reporting"
- "need to automate this codebase"

**Use For:** Explicit automation needs

---

### 3. Transformation Patterns

#### Pattern 3.1: Convert/Transform
```regex
(?i)(turn|convert|transform|change)\s+(this\s+)?(process|workflow|task|data)\s+into\s+(an?\s+)?(agent|automation|system)
```

**Matches:**
- "turn this process into an agent"
- "turn this codebase into an agent"
- "convert workflow to automation"
- "convert workflow in this repo/codebase into automation"
- "transform task into system"
- "transform this codebase tasks into system"

**Use For:** Process transformation skills

---

#### Pattern 3.2: From X to Y
```regex
(?i)(from|convert)\s+([A-Za-z]+)\s+(to|into)\s+([A-Za-z]+)
```

**Matches:**
- "from PDF to text"
- "convert CSV to JSON"
- "from article to code"
- "from repository to code"
- "from codebasee to code"
- "from github repo to code"

**Use For:** Format conversion, data transformation

---

### 4. Analysis Patterns

#### Pattern 4.1: General Analysis
```regex
(?i)(analyze|analysis|examine|study)\s+.*\s+(data|information|metrics|performance|results)
```

**Matches:**
- "analyze sales data"
- "analysis of performance metrics"
- "examine customer information"

**Use For:** Data analysis skills

---

#### Pattern 4.2: Domain-Specific Analysis
```regex
(?i)(analyze|analysis|monitor|track)\s+.*\s+(stock|crop|customer|user|product)s?
```

**Matches:**
- "analyze stock performance"
- "monitor crop conditions"
- "track customer behavior"
- "track prices"
- "monitor weather"

**Use For:** Domain-specific analytics

---

#### Pattern 4.3: Technical Analysis
```regex
(?i)(technical|chart)\s+(analysis|indicators?)\s+(for|of|on)
```

**Matches:**
- "technical analysis for AAPL"
- "chart indicators of SPY"
- "technical analysis on stocks"

**Use For:** Financial/technical analysis skills

---

### 5. Comparison Patterns

#### Pattern 5.1: Direct Comparison
```regex
(?i)(compare|comparison)\s+.*\s+(vs|versus|against|with|to)
```

**Matches:**
- "compare AAPL vs MSFT"
- "comparison of stocks against benchmark"
- "compare performance with last year"

**Use For:** Comparison and benchmarking skills

---

#### Pattern 5.2: Year-over-Year
```regex
(?i)(this year|this week|this month|this quarter|today|current)\s+(vs|versus|against|compared to)\s+(last year|last week|last month|last quarter|last day|previous|prior)
```

**Matches:**
- "this year vs last year"
- "current versus previous year"
- "this year compared to prior year"
- "this week vs last week"
- "current versus previous week"
- "this quarter compared to prior quarter"

**Use For:** Temporal comparison skills

---

### 6. Ranking & Sorting Patterns

#### Pattern 6.1: Top N Pattern
```regex
(?i)(top|best|leading|biggest|highest)\s+(\d+)?\s*(states|countries|stocks|products|customers)?
```

**Matches:**
- "top 10 states"
- "best performing stocks"
- "leading products"
- "biggest countries"

**Use For:** Ranking and leaderboard skills

---

#### Pattern 6.2: Ranking Request
```regex
(?i)(rank|ranking|sort|list)\s+.*\s+(by|based on)\s+(.*?)
```

**Matches:**
- "rank states by production"
- "ranking based on performance"
- "sort stocks by volatility"

**Use For:** Sorting and organization skills

---

### 7. Extraction Patterns

#### Pattern 7.1: Extract From Source
```regex
(?i)(extract|parse|get|retrieve)\s+.*\s+(from)\s+(pdf|article|web|url|file|document|page)
```

**Matches:**
- "extract text from PDF"
- "parse data from article"
- "get information from web page"

**Use For:** Data extraction skills

---

#### Pattern 7.2: Implementation From Source
```regex
(?i)(implement|build|create|generate)\s+(.*?)\s+(from)\s+(article|paper|documentation|tutorial)
```

**Matches:**
- "implement algorithm from paper"
- "create code from tutorial"
- "generate prototype from article"

**Use For:** Code generation from documentation

---

### 8. Reporting Patterns

#### Pattern 8.1: Generate Report
```regex
(?i)(generate|create|produce|build)\s+(an?\s+)?(report|dashboard|summary|overview)\s+(for|about|on)
```

**Matches:**
- "generate a report for sales"
- "create dashboard about performance"
- "produce summary on metrics"

**Use For:** Reporting and visualization skills

---

#### Pattern 8.2: Report Request
```regex
(?i)(show|give|provide)\s+me\s+(an?\s+)?(report|summary|overview|dashboard)
```

**Matches:**
- "show me a report"
- "give me summary"
- "provide overview"

**Use For:** Data presentation skills

---

### 9. Monitoring Patterns

#### Pattern 9.1: Monitor/Track
```regex
(?i)(monitor|track|watch|observe)\s+.*\s+(for|about)\s+(changes|updates|alerts|notifications)
```

**Matches:**
- "monitor stocks for changes"
- "track repositories for updates"
- "watch prices for alerts"

**Use For:** Monitoring and alerting skills

---

#### Pattern 9.2: Notification Request
```regex
(?i)(notify|alert|inform)\s+me\s+(when|if|about)
```

**Matches:**
- "notify me when price drops"
- "alert me if error occurs"
- "inform me about changes"

**Use For:** Notification systems

---

### 10. Search & Query Patterns

#### Pattern 10.1: What/How Questions
```regex
(?i)(what|how|which|where)\s+(is|are|was|were)\s+.*\s+(of|for|in)
```

**Matches:**
- "what is production of corn"
- "how are conditions for soybeans"
- "which stocks are best"

**Use For:** Query and search skills

---

#### Pattern 10.2: Data Request
```regex
(?i)(show|get|fetch|retrieve|find)\s+.*\s+(data|information|stats|metrics)
```

**Matches:**
- "show me crop data"
- "get stock information"
- "fetch performance metrics"

**Use For:** Data retrieval skills

---

## 🎯 Pattern Combinations

### Combo 1: Analysis + Domain
```regex
(?i)(analyze|analysis)\s+.*\s+(stock|crop|customer|product)s?\s+(using|with|via)
```

**Example:** "analyze stocks using RSI"

---

### Combo 2: Extract + Implement
```regex
(?i)(extract|parse)\s+.*\s+and\s+(implement|build|create)
```

**Example:** "extract algorithm and implement in Python"

---

### Combo 3: Monitor + Report
```regex
(?i)(monitor|track)\s+.*\s+and\s+(generate|create|send)\s+(report|alert)
```

**Example:** "monitor prices and generate alerts"

---

## 🚫 Anti-Patterns (Avoid These)

### Anti-Pattern 1: Too Broad
```regex
❌ (?i)(data)
❌ (?i)(analysis)
❌ (?i)(create)
```
**Problem:** Matches everything, high false positive rate

---

### Anti-Pattern 2: No Action Verb
```regex
❌ (?i)(stock|stocks?)
❌ (?i)(pdf|document)
```
**Problem:** Passive, no user intent

---

### Anti-Pattern 3: Overly Specific
```regex
❌ (?i)analyze AAPL stock using RSI indicator
```
**Problem:** Too narrow, misses variations

---

## ✅ Pattern Quality Checklist

For each pattern, verify:

- [ ] Includes action verb(s)
- [ ] Includes target entity/object
- [ ] Case insensitive (`(?i)`)
- [ ] Flexible (captures variations)
- [ ] Not too broad (false positives)
- [ ] Not too narrow (false negatives)
- [ ] Tested with 5+ example queries
- [ ] Documented with match examples

---

## 🧪 Pattern Testing Template

```markdown
### Pattern: {pattern-name}

**Regex:**
```regex
{regex-pattern}
```

**Should Match:**
✅ "{example-1}"
✅ "{example-2}"
✅ "{example-3}"

**Should NOT Match:**
❌ "{counter-example-1}"
❌ "{counter-example-2}"

**Test Results:**
- Tested: {date}
- Pass rate: {X/Y}
- Issues: {none/list}
```

---

## 📖 Usage Examples

### Example 1: Stock Analysis Skill

**Selected Patterns:**
```json
"patterns": [
  "(?i)(analyze|analysis)\\s+.*\\s+(stock|stocks?|ticker)s?",
  "(?i)(technical|chart)\\s+(analysis|indicators?)\\s+(for|of)",
  "(?i)(buy|sell)\\s+(signal|recommendation)\\s+(for|using)",
  "(?i)(compare|rank)\\s+.*\\s+stocks?\\s+(using|by)"
]
```

### Example 2: PDF Extraction Skill

**Selected Patterns:**
```json
"patterns": [
  "(?i)(extract|parse|get)\\s+.*\\s+(from)\\s+(pdf|document)",
  "(?i)(convert|transform)\\s+pdf\\s+(to|into)",
  "(?i)(read|process)\\s+.*\\s+pdf"
]
```

### Example 3: Agent Creation Skill

**Selected Patterns:**
```json
"patterns": [
  "(?i)(create|build)\\s+(an?\\s+)?(agent|skill)\\s+for",
  "(?i)(automate|automation)\\s+(workflow|process)",
  "(?i)(every day|daily)\\s+I\\s+(have to|need to)",
  "(?i)turn\\s+.*\\s+into\\s+(an?\\s+)?agent"
]
```

---

## 🔄 Pattern Maintenance

### When to Update Patterns

1. **False Negatives:** Valid queries not matching
2. **False Positives:** Invalid queries matching
3. **New Use Cases:** Skill capabilities expanded
4. **User Feedback:** Reported activation issues

### Update Process

1. Identify issue (false negative/positive)
2. Analyze query pattern
3. Update or add pattern
4. Test with 10+ variations
5. Document changes
6. Update marketplace.json

---

## 📚 Additional Resources

- See `phase4-detection.md` for complete detection guide
- See `activation-testing-guide.md` for testing procedures
- See `ACTIVATION_BEST_PRACTICES.md` for best practices

---

**Version:** 1.0
**Last Updated:** 2025-10-23
**Maintained By:** Agent-Skill-Creator Team
