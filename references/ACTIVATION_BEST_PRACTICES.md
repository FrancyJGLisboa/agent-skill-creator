# Activation Best Practices

**Version:** 1.0
**Purpose:** Proven strategies and practical guidance for creating skills with reliable activation

---

## Overview

This guide compiles best practices, lessons learned, and proven strategies for implementing the 3-Layer Activation System. Follow these guidelines to achieve 95%+ activation reliability consistently.

### Target Audience

- **Skill Creators**: Building new skills with robust activation
- **Advanced Users**: Optimizing existing skills
- **Teams**: Establishing activation standards

### Success Criteria

✅ **95%+ activation reliability** across diverse user queries
✅ **Zero false positives** (no incorrect activations)
✅ **Natural language support** (users don't need special phrases)
✅ **Maintainable** (easy to update and extend)

---

## 🎯 Golden Rules

### Rule #1: Always Use All 3 Layers

**Don't:**
```json
{
  "plugins": [{
    "description": "Stock analysis tool"
  }]
}
```
❌ Only Layer 3 (description) = ~70% reliability

**Do:**
```json
{
  "activation": {
    "keywords": ["analyze stock", "RSI indicator", ...],
    "patterns": ["(?i)(analyze)\\s+.*\\s+stock", ...]
  },
  "plugins": [{
    "description": "Comprehensive stock analysis tool with RSI, MACD..."
  }]
}
```
✅ All 3 layers = 95%+ reliability

---

### Rule #2: Keywords Must Be Complete Phrases

**Don't:**
```json
"keywords": [
  "create",        // ❌ Too generic
  "agent",         // ❌ Too broad
  "stock"          // ❌ Single word
]
```

**Do:**
```json
"keywords": [
  "create an agent for",     // ✅ Complete phrase
  "analyze stock",           // ✅ Verb + entity
  "technical analysis for"   // ✅ Specific context
]
```

**Why?** Single words match everything, causing false positives.

---

### Rule #3: Patterns Must Include Action Verbs

**Don't:**
```json
"patterns": [
  "(?i)(stock|stocks?)"              // ❌ No action
]
```

**Do:**
```json
"patterns": [
  "(?i)(analyze|analysis)\\s+.*\\s+stock"  // ✅ Verb + entity
]
```

**Why?** Passive patterns activate on mentions, not intentions.

---

### Rule #4: Description Must Be Rich, Not Generic

**Don't:**
```
"Stock analysis tool"
```
❌ 3 keywords, too vague

**Do:**
```
"Comprehensive technical analysis tool for stocks and ETFs. Analyzes price movements,
volume patterns, and momentum indicators including RSI (Relative Strength Index),
MACD (Moving Average Convergence Divergence), Bollinger Bands, moving averages,
and chart patterns. Generates buy and sell signals based on technical indicators."
```
✅ 60+ keywords, specific capabilities

---

### Rule #5: Define Negative Scope

**Don't:**
```json
{
  // No when_not_to_use section
}
```

**Do:**
```json
"usage": {
  "when_not_to_use": [
    "User asks for fundamental analysis (P/E ratios, earnings)",
    "User wants news or sentiment analysis",
    "User asks general questions about how markets work"
  ]
}
```

**Why?** Prevents false positives and helps users understand boundaries.

---

## 📋 Layer-by-Layer Best Practices

### Layer 1: Keywords

#### ✅ Do's

1. **Use complete phrases (2+ words)**
   ```json
   "analyze stock"        // Good
   "create an agent for"  // Good
   "RSI indicator"        // Good
   ```

2. **Cover all major capabilities**
   - 3-5 keywords per capability
   - Action keywords: "create", "analyze", "compare"
   - Domain keywords: "stock", "RSI", "MACD"
   - Workflow keywords: "automate workflow", "daily I have to"

3. **Include domain-specific terms**
   ```json
   "RSI indicator"
   "MACD crossover"
   "Bollinger Bands"
   ```

4. **Use natural variations**
   ```json
   "analyze stock"
   "stock analysis"
   ```

#### ❌ Don'ts

1. **No single words**
   ```json
   "stock"     // ❌ Too broad
   "analysis"  // ❌ Too generic
   ```

2. **No overly generic phrases**
   ```json
   "data analysis"  // ❌ Every skill does analysis
   "help me"        // ❌ Too vague
   ```

3. **No redundancy**
   ```json
   "analyze stock"
   "analyze stocks"     // ❌ Covered by pattern
   "stock analyzer"     // ❌ Slight variation
   ```

4. **Don't exceed 20 keywords**
   - More keywords = diluted effectiveness
   - Focus on quality, not quantity

---

### Layer 2: Patterns

#### ✅ Do's

1. **Always start with (?i) for case-insensitivity**
   ```regex
   (?i)(analyze|analysis)\s+.*\s+stock
   ```

2. **Include action verb groups**
   ```regex
   (create|build|develop|make)    // Synonyms
   (analyze|analysis|examine)     // Variations
   ```

3. **Allow flexible word order**
   ```regex
   (?i)(analyze)\\s+.*\\s+(stock)
   ```
   Matches: "analyze AAPL stock", "analyze this stock's performance"

4. **Use optional groups for articles**
   ```regex
   (an?\\s+)?agent
   ```
   Matches: "an agent", "a agent", "agent"

5. **Combine verb + entity + context**
   ```regex
   (?i)(create|build)\\s+(an?\\s+)?agent\\s+(for|to|that)
   ```

#### ❌ Don'ts

1. **No single-word patterns**
   ```regex
   (?i)(stock)  // ❌ Matches everything
   ```

2. **No overly specific patterns**
   ```regex
   (?i)analyze AAPL stock using RSI  // ❌ Too narrow
   ```

3. **Don't forget to escape special regex characters**
   ```regex
   (?i)interface{}      // ❌ Invalid
   (?i)interface\\{\\}  // ✅ Correct
   ```

4. **Don't create conflicting patterns**
   ```json
   "patterns": [
     "(?i)(create)\\s+.*\\s+agent",
     "(?i)(create)\\s+(an?\\s+)?agent"  // ❌ Redundant
   ]
   ```

#### Pattern Categories (Use 1-2 from each)

**Action + Object:**
```regex
(?i)(create|build)\\s+(an?\\s+)?agent\\s+for
```

**Domain-Specific:**
```regex
(?i)(analyze|analysis)\\s+.*\\s+(stock|ticker)
```

**Workflow:**
```regex
(?i)(every day|daily)\\s+(I|we)\\s+(have to|need)
```

**Transformation:**
```regex
(?i)(turn|convert)\\s+.*\\s+into\\s+(an?\\s+)?agent
```

**Comparison:**
```regex
(?i)(compare|rank)\\s+.*\\s+stocks?
```

---

### Layer 3: Description

#### ✅ Do's

1. **Start with primary use case**
   ```
   "Comprehensive technical analysis tool for stocks and ETFs..."
   ```

2. **Include all Layer 1 keywords naturally**
   ```
   "...analyzes price movements... RSI (Relative Strength Index)...
   MACD (Moving Average Convergence Divergence)... Bollinger Bands..."
   ```

3. **Use full names for acronyms (first mention)**
   ```
   "RSI (Relative Strength Index)"  ✅
   "RSI"                             ❌ (first mention)
   ```

4. **Mention target user persona**
   ```
   "...Perfect for traders needing technical analysis..."
   ```

5. **Include specific capabilities**
   ```
   "Generates buy and sell signals based on technical indicators"
   ```

6. **Add synonyms and variations**
   ```
   "analyzes", "monitors", "tracks", "evaluates", "assesses"
   ```

#### ❌ Don'ts

1. **No keyword stuffing**
   ```
   "Stock stock stocks analyze analysis analyzer technical..."  // ❌
   ```

2. **No vague descriptions**
   ```
   "A tool for data analysis"  // ❌ Too generic
   ```

3. **No missing domain context**
   ```
   "Calculates indicators"  // ❌ What kind?
   ```

4. **Don't exceed 500 characters**
   - Claude has limits on description processing
   - Focus on quality keywords, not length

---

## 🧪 Testing Best Practices

### Test Query Design

#### ✅ Do's

1. **Create diverse test queries**
   ```json
   "test_queries": [
     "Analyze AAPL stock using RSI",           // Direct keyword
     "What's the technical analysis for MSFT?", // Pattern
     "Show me chart patterns for AMD",          // Description
     "Compare AAPL vs GOOGL momentum"           // Natural variation
   ]
   ```

2. **Cover all capabilities**
   - At least 2 queries per major capability
   - Mix of direct and natural language
   - Edge cases and variations

3. **Document expected activation layer**
   ```json
   "test_queries": [
     "Analyze stock AAPL  // Layer 1: keyword 'analyze stock'"
   ]
   ```

4. **Include negative tests**
   ```json
   "negative_tests": [
     "What's the P/E ratio of AAPL?  // Should NOT activate"
   ]
   ```

#### ❌ Don'ts

1. **No duplicate or near-duplicate queries**
   ```json
   "Analyze AAPL stock"
   "Analyze AAPL stock price"  // ❌ Too similar
   ```

2. **No overly similar queries**
   - Test different phrasings, not same query repeatedly

3. **Don't skip negative tests**
   - False positives are worse than false negatives

---

### Testing Process

**Phase 1: Layer Testing**
```bash
# Test each layer independently
1. Test all keywords (expect 100% success)
2. Test all patterns (expect 100% success)
3. Test description with edge cases (expect 90%+ success)
```

**Phase 2: Integration Testing**
```bash
# Test complete system
1. Test all test_queries (expect 95%+ success)
2. Test negative queries (expect 0% activation)
3. Document any failures
```

**Phase 3: Iteration**
```bash
# Fix and retest
1. Analyze failures
2. Update keywords/patterns/description
3. Retest
4. Repeat until 95%+ success
```

---

## 🎯 Common Patterns by Domain

### Financial/Stock Analysis

**Keywords:**
```json
[
  "analyze stock",
  "technical analysis for",
  "RSI indicator",
  "MACD indicator",
  "buy signal for",
  "compare stocks"
]
```

**Patterns:**
```json
[
  "(?i)(analyze|analysis)\\s+.*\\s+(stock|ticker)",
  "(?i)(RSI|MACD|Bollinger)\\s+(for|of|indicator)",
  "(?i)(buy|sell)\\s+signal\\s+for"
]
```

---

### Data Extraction/Processing

**Keywords:**
```json
[
  "extract from PDF",
  "parse article",
  "convert PDF to",
  "extract text from"
]
```

**Patterns:**
```json
[
  "(?i)(extract|parse|get)\\s+.*\\s+from\\s+(pdf|article|web)",
  "(?i)(convert|transform)\\s+pdf\\s+to"
]
```

---

### Workflow Automation

**Keywords:**
```json
[
  "automate workflow",
  "create an agent for",
  "every day I have to",
  "turn process into agent"
]
```

**Patterns:**
```json
[
  "(?i)(create|build)\\s+(an?\\s+)?agent\\s+for",
  "(?i)(automate|automation)\\s+(workflow|process)",
  "(?i)(every day|daily)\\s+I\\s+(have to|need)"
]
```

---

### Data Analysis/Comparison

**Keywords:**
```json
[
  "compare data",
  "rank by",
  "top states by",
  "analyze trend"
]
```

**Patterns:**
```json
[
  "(?i)(compare|rank)\\s+.*\\s+(by|using|with)",
  "(?i)(top|best)\\s+\\d*\\s+(states|countries|items)",
  "(?i)(analyze|analysis)\\s+.*\\s+(trend|pattern)"
]
```

---

## 🚫 Common Mistakes & Fixes

### Mistake #1: Keywords Too Generic

**Problem:**
```json
"keywords": ["data", "analysis", "create"]
```

**Impact:** False positives - activates for everything

**Fix:**
```json
"keywords": [
  "analyze stock data",
  "technical analysis",
  "create an agent for"
]
```

---

### Mistake #2: Patterns Too Broad

**Problem:**
```regex
(?i)(data|information)
```

**Impact:** Matches every query with "data"

**Fix:**
```regex
(?i)(analyze|process)\\s+.*\\s+(stock|market)\\s+(data|information)
```

---

### Mistake #3: Missing Action Verbs

**Problem:**
```json
"keywords": ["stock market", "financial data"]
```

**Impact:** No clear user intent, passive activation

**Fix:**
```json
"keywords": [
  "analyze stock market",
  "process financial data",
  "monitor stock performance"
]
```

---

### Mistake #4: Insufficient Test Coverage

**Problem:**
```json
"test_queries": [
  "Analyze AAPL",
  "Analyze MSFT"
]
```

**Impact:** Only tests one pattern, misses variations

**Fix:**
```json
"test_queries": [
  "Analyze AAPL stock using RSI",          // Keyword test
  "What's the technical analysis for MSFT?", // Pattern test
  "Show me chart patterns for AMD",          // Description test
  "Compare AAPL vs GOOGL momentum",          // Combination test
  "Is there a buy signal for NVDA?",        // Signal test
  ...10+ total covering all capabilities
]
```

---

### Mistake #5: No Negative Scope

**Problem:**
```json
{
  // No when_not_to_use section
}
```

**Impact:** False positives, user confusion

**Fix:**
```json
"usage": {
  "when_not_to_use": [
    "User asks for fundamental analysis",
    "User wants news/sentiment analysis",
    "User asks how markets work (education)"
  ]
}
```

---

## ✅ Pre-Deployment Checklist

### Layer 1: Keywords
- [ ] 10-15 complete keyword phrases defined
- [ ] All keywords are 2+ words
- [ ] No overly generic keywords
- [ ] Keywords cover all major capabilities
- [ ] 3+ keywords per capability

### Layer 2: Patterns
- [ ] 5-7 regex patterns defined
- [ ] All patterns start with (?i)
- [ ] All patterns include action verb + entity
- [ ] Patterns tested with regex tester
- [ ] No patterns too broad or too narrow

### Layer 3: Description
- [ ] 300-500 character description
- [ ] 60+ unique keywords included
- [ ] All Layer 1 keywords mentioned naturally
- [ ] Primary use case stated first
- [ ] Target user persona mentioned

### Usage Section
- [ ] 5+ when_to_use cases documented
- [ ] 3+ when_not_to_use cases documented
- [ ] Example query provided
- [ ] Counter-examples documented

### Testing
- [ ] 10+ test queries covering all layers
- [ ] Queries tested in Claude Code
- [ ] Negative queries tested (no false positives)
- [ ] Overall success rate 95%+
- [ ] Failures documented and fixed

### Documentation
- [ ] README includes activation section
- [ ] 10+ activation phrase examples
- [ ] Troubleshooting section included
- [ ] Tips for reliable activation provided

---

## 🎓 Learning from Examples

### Excellent Example: stock-analyzer-cskill

**What makes it excellent:**

✅ **Complete keyword coverage (15 keywords)**
```json
"keywords": [
  "analyze stock",           // Primary action
  "technical analysis for",  // Domain-specific
  "RSI indicator",          // Specific feature 1
  "MACD indicator",         // Specific feature 2
  "Bollinger Bands",        // Specific feature 3
  "buy signal for",         // Use case 1
  "compare stocks",         // Use case 2
  ...
]
```

✅ **Well-crafted patterns (7 patterns)**
```json
"patterns": [
  "(?i)(analyze|analysis)\\s+.*\\s+(stock|ticker)",        // General
  "(?i)(technical|chart)\\s+analysis\\s+(for|of)",        // Specific
  "(?i)(RSI|MACD|Bollinger)\\s+(for|of|indicator)",      // Features
  "(?i)(buy|sell)\\s+signal\\s+for",                      // Signals
  ...
]
```

✅ **Rich description (80+ keywords)**
```
"Comprehensive technical analysis tool for stocks and ETFs.
Analyzes price movements, volume patterns, and momentum indicators
including RSI (Relative Strength Index), MACD (Moving Average
Convergence Divergence), Bollinger Bands..."
```

✅ **Complete testing (12 positive + 7 negative queries)**

✅ **Clear boundaries (when_not_to_use section)**

**Result:** 98% activation reliability

**Location:** `references/examples/stock-analyzer-cskill/`

---

## 📚 Additional Resources

### Documentation
- **Complete Guide**: `phase4-detection.md`
- **Pattern Library**: `activation-patterns-guide.md`
- **Testing Guide**: `activation-testing-guide.md`
- **Quality Checklist**: `activation-quality-checklist.md`

### Templates
- **Marketplace Template**: `templates/marketplace-robust-template.json`
- **README Template**: `templates/README-activation-template.md`

### Examples
- **Complete Example**: `examples/stock-analyzer-cskill/`

---

## 🔄 Continuous Improvement

### Monitor Activation Performance

**Track metrics:**
- Activation success rate (target: 95%+)
- False positive rate (target: 0%)
- False negative rate (target: <5%)
- User feedback on activation issues

### Iterate Based on Feedback

**When to update:**
1. False negatives: Add keywords/patterns for missed queries
2. False positives: Narrow patterns, enhance when_not_to_use
3. New capabilities: Update all 3 layers
4. User confusion: Improve documentation

### Version Your Activation System

```json
{
  "metadata": {
    "version": "1.1.0",
    "activation_version": "3.0",
    "last_activation_update": "2025-10-23"
  }
}
```

---

## 🎯 Quick Reference

### Minimum Requirements
- **Keywords**: 10+ complete phrases
- **Patterns**: 5+ regex with verbs + entities
- **Description**: 300+ chars, 60+ keywords
- **Usage**: 5+ when_to_use, 3+ when_not_to_use
- **Testing**: 10+ test queries, 95%+ success rate

### Target Goals
- **Keywords**: 12-15 phrases
- **Patterns**: 7 patterns
- **Description**: 400+ chars, 80+ keywords
- **Testing**: 15+ test queries, 98%+ success rate
- **False Positives**: 0%

### Quality Grades
- **A (Excellent)**: 95%+ success, 0% false positives
- **B (Good)**: 90-94% success, <1% false positives
- **C (Acceptable)**: 85-89% success, <2% false positives
- **F (Needs Work)**: <85% success or >2% false positives

**Only Grade A skills should be deployed to production.**

---

**Version:** 1.0
**Last Updated:** 2025-10-23
**Maintained By:** Agent-Skill-Creator Team
