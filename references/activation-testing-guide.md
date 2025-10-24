# Activation Testing Guide

**Version:** 1.0
**Purpose:** Comprehensive guide for testing skill activation reliability

---

## Overview

This guide provides procedures, templates, and checklists for testing the 3-Layer Activation System to ensure skills activate correctly and reliably.

### Testing Philosophy

**Goal:** 95%+ activation reliability

**Approach:** Test each layer independently, then integration

**Metrics:**
- **True Positives:** Valid queries that correctly activate
- **True Negatives:** Invalid queries that correctly don't activate
- **False Positives:** Invalid queries that incorrectly activate
- **False Negatives:** Valid queries that fail to activate

**Target:** Zero false positives, <5% false negatives

---

## 🧪 Testing Methodology

### Phase 1: Layer 1 Testing (Keywords)

#### Objective
Verify that exact keyword phrases activate the skill.

#### Procedure

**Step 1:** List all keywords from marketplace.json

**Step 2:** Create test query for each keyword

**Step 3:** Test each query manually

**Step 4:** Document results

#### Template

```markdown
## Layer 1: Keywords Testing

**Keyword 1:** "create an agent for"

Test Queries:
1. "create an agent for processing invoices"
   - ✅ Activated
   - Via: Keyword match

2. "I want to create an agent for data analysis"
   - ✅ Activated
   - Via: Keyword match

3. "Create An Agent For automation"  // Case variation
   - ✅ Activated
   - Via: Keyword match (case-insensitive)

**Keyword 2:** "automate workflow"
...
```

#### Pass Criteria
- [ ] 100% of keyword test queries activate
- [ ] Case-insensitive matching works
- [ ] Embedded keywords activate (keyword within longer query)

---

### Phase 2: Layer 2 Testing (Patterns)

#### Objective
Verify that regex patterns capture expected variations.

#### Procedure

**Step 1:** List all patterns from marketplace.json

**Step 2:** Create 5+ test queries per pattern

**Step 3:** Test pattern matching (can use regex tester)

**Step 4:** Test in Claude Code

**Step 5:** Document results

#### Template

```markdown
## Layer 2: Patterns Testing

**Pattern 1:** `(?i)(create|build)\s+(an?\s+)?agent\s+for`

Designed to Match:
- Verbs: create, build
- Optional article: a, an
- Entity: agent
- Connector: for

Test Queries:
1. "create an agent for automation"
   - ✅ Matches pattern
   - ✅ Activated in Claude Code

2. "build a agent for processing"
   - ✅ Matches pattern
   - ✅ Activated

3. "create agent for data"  // No article
   - ✅ Matches pattern
   - ✅ Activated

4. "Build Agent For Tasks"  // Different case
   - ✅ Matches pattern
   - ✅ Activated

5. "I want to create an agent for reporting"  // Embedded
   - ✅ Matches pattern
   - ✅ Activated

Should NOT Match:
6. "agent creation guide"
   - ❌ No action verb
   - ❌ Correctly did not activate

7. "create something for automation"
   - ❌ No "agent" keyword
   - ❌ Correctly did not activate
```

#### Pass Criteria
- [ ] 100% of positive test queries match pattern
- [ ] 100% of positive queries activate in Claude Code
- [ ] 0% of negative queries match pattern
- [ ] Pattern is flexible (captures variations)
- [ ] Pattern is specific (no false positives)

---

### Phase 3: Layer 3 Testing (Description + NLU)

#### Objective
Verify that description helps Claude understand intent for edge cases.

#### Procedure

**Step 1:** Create queries that DON'T match keywords/patterns

**Step 2:** Verify these still activate via description understanding

**Step 3:** Document which queries activate

#### Template

```markdown
## Layer 3: Description + NLU Testing

**Queries that don't match Keywords or Patterns:**

1. "I keep doing this task manually, can you help automate it?"
   - ❌ No keyword match
   - ❌ No pattern match
   - ✅ Should activate via description understanding
   - Result: {activated/did not activate}

2. "This process is repetitive and takes hours daily"
   - ❌ No keyword match
   - ❌ No pattern match
   - ✅ Should activate (describes repetitive workflow)
   - Result: {activated/did not activate}

3. "Help me build something to handle this workflow"
   - ❌ No exact keyword
   - ⚠️ Might match pattern
   - ✅ Should activate
   - Result: {activated/did not activate}
```

#### Pass Criteria
- [ ] Edge case queries activate when appropriate
- [ ] Natural language variations work
- [ ] Description provides fallback coverage

---

### Phase 4: Integration Testing

#### Objective
Test complete system with real-world query variations.

#### Procedure

**Step 1:** Create 10+ realistic query variations per capability

**Step 2:** Test all queries in actual Claude Code environment

**Step 3:** Track activation success rate

**Step 4:** Identify gaps

#### Template

```markdown
## Integration Testing

**Capability:** Agent Creation

**Test Queries:**

| # | Query | Expected | Actual | Layer | Status |
|---|-------|----------|--------|-------|--------|
| 1 | "create an agent for PDFs" | Activate | Activated | Keyword | ✅ |
| 2 | "build automation for emails" | Activate | Activated | Pattern | ✅ |
| 3 | "daily I process invoices manually" | Activate | Activated | Desc | ✅ |
| 4 | "make agent for data entry" | Activate | Activated | Pattern | ✅ |
| 5 | "automate my workflow for reports" | Activate | Activated | Keyword | ✅ |
| 6 | "I need help with automation" | Activate | NOT activated | - | ❌ |
| 7 | "turn this into automated process" | Activate | Activated | Pattern | ✅ |
| 8 | "create skill for stock analysis" | Activate | Activated | Keyword | ✅ |
| 9 | "repeatedly doing this task" | Activate | Activated | Desc | ✅ |
| 10 | "can you help automate this?" | Activate | Activated | Desc | ✅ |

**Results:**
- Total queries: 10
- Activated correctly: 9
- Failed to activate: 1 (Query #6)
- Success rate: 90%

**Issues:**
- Query #6 too generic, needs more specific keywords
```

#### Pass Criteria
- [ ] 95%+ success rate
- [ ] All capability variations covered
- [ ] Realistic query phrasings tested
- [ ] Edge cases documented

---

### Phase 5: Negative Testing (False Positives)

#### Objective
Ensure skill does NOT activate for out-of-scope queries.

#### Procedure

**Step 1:** List out-of-scope use cases (when_not_to_use)

**Step 2:** Create queries for each

**Step 3:** Verify skill does NOT activate

**Step 4:** Document any false positives

#### Template

```markdown
## Negative Testing

**Out of Scope:** General programming questions

Test Queries (Should NOT Activate):
1. "How do I write a for loop in Python?"
   - Result: Did not activate ✅

2. "What's the difference between list and tuple?"
   - Result: Did not activate ✅

3. "Help me debug this code"
   - Result: Did not activate ✅

**Out of Scope:** Using existing skills

Test Queries (Should NOT Activate):
4. "Run the invoice processor skill"
   - Result: Did not activate ✅

5. "Show me existing agents"
   - Result: Did not activate ✅

**Results:**
- Total negative queries: 5
- Correctly did not activate: 5
- False positives: 0
- Success rate: 100%
```

#### Pass Criteria
- [ ] 100% of out-of-scope queries do NOT activate
- [ ] Zero false positives
- [ ] when_not_to_use cases covered

---

## 📋 Complete Testing Checklist

### Pre-Testing Setup
- [ ] marketplace.json has activation section
- [ ] Keywords defined (10-15)
- [ ] Patterns defined (5-7)
- [ ] Description includes keywords
- [ ] when_to_use / when_not_to_use defined
- [ ] test_queries array populated

### Layer 1: Keywords
- [ ] All keywords tested individually
- [ ] Case-insensitive matching verified
- [ ] Embedded keywords work
- [ ] 100% activation rate

### Layer 2: Patterns
- [ ] Each pattern tested with 5+ queries
- [ ] Pattern matches verified (regex tester)
- [ ] Claude Code activation verified
- [ ] No false positives
- [ ] Flexible enough for variations

### Layer 3: Description
- [ ] Edge cases tested
- [ ] Natural language variations work
- [ ] Fallback coverage confirmed

### Integration
- [ ] 10+ realistic queries per capability tested
- [ ] 95%+ success rate achieved
- [ ] All capabilities covered
- [ ] Results documented

### Negative Testing
- [ ] Out-of-scope queries tested
- [ ] Zero false positives
- [ ] when_not_to_use cases verified

### Documentation
- [ ] Test results documented
- [ ] Issues logged
- [ ] Recommendations made
- [ ] marketplace.json updated if needed

---

## 📊 Test Report Template

```markdown
# Activation Test Report

**Skill Name:** {skill-name}
**Version:** {version}
**Test Date:** {date}
**Tested By:** {name}
**Environment:** Claude Code {version}

---

## Executive Summary

- **Overall Success Rate:** {X}%
- **Total Queries Tested:** {N}
- **True Positives:** {N}
- **True Negatives:** {N}
- **False Positives:** {N}
- **False Negatives:** {N}

---

## Layer 1: Keywords Testing

**Keywords Tested:** {count}
**Success Rate:** {X}%

### Results
| Keyword | Test Queries | Passed | Failed |
|---------|--------------|--------|--------|
| {keyword-1} | {N} | {N} | {N} |
| {keyword-2} | {N} | {N} | {N} |

**Issues:**
- {issue-1}
- {issue-2}

---

## Layer 2: Patterns Testing

**Patterns Tested:** {count}
**Success Rate:** {X}%

### Results
| Pattern | Test Queries | Passed | Failed |
|---------|--------------|--------|--------|
| {pattern-1} | {N} | {N} | {N} |
| {pattern-2} | {N} | {N} | {N} |

**Issues:**
- {issue-1}
- {issue-2}

---

## Layer 3: Description Testing

**Edge Cases Tested:** {count}
**Success Rate:** {X}%

**Results:**
- Activated via description: {N}
- Failed to activate: {N}

---

## Integration Testing

**Total Test Queries:** {count}
**Success Rate:** {X}%

**Breakdown by Capability:**
| Capability | Queries | Success | Rate |
|------------|---------|---------|------|
| {cap-1} | {N} | {N} | {X}% |
| {cap-2} | {N} | {N} | {X}% |

---

## Negative Testing

**Out-of-Scope Queries:** {count}
**False Positives:** {N}
**Success Rate:** {X}%

---

## Issues & Recommendations

### Critical Issues
1. {issue-description}
   - Impact: {high/medium/low}
   - Recommendation: {action}

### Minor Issues
1. {issue-description}
   - Impact: {low}
   - Recommendation: {action}

### Recommendations
1. {recommendation-1}
2. {recommendation-2}

---

## Conclusion

{Summary of test results and next steps}

**Status:** {PASS / NEEDS WORK / FAIL}

---

**Appendix A:** Full Test Query List
**Appendix B:** Failed Query Analysis
**Appendix C:** Updated marketplace.json (if changes needed)
```

---

## 🔄 Iterative Testing Process

### Step 1: Initial Test
- Run complete test suite
- Document results
- Identify failures

### Step 2: Analysis
- Analyze failed queries
- Determine root cause
- Plan fixes

### Step 3: Fix
- Update keywords/patterns/description
- Document changes

### Step 4: Retest
- Test only failed queries
- Verify fixes work
- Ensure no regressions

### Step 5: Full Regression Test
- Run complete test suite again
- Verify 95%+ success rate
- Document final results

---

## 🎯 Sample Test Suite

### Example: Agent Creation Skill

```markdown
## Test Suite: Agent Creation Skill

### Layer 1 Tests (Keywords)

**Keyword:** "create an agent for"
- ✅ "create an agent for processing PDFs"
- ✅ "I want to create an agent for automation"
- ✅ "Create An Agent For daily tasks"

**Keyword:** "automate workflow"
- ✅ "automate workflow for invoices"
- ✅ "need to automate workflow"
- ✅ "Automate Workflow handling"

[... more keywords]

### Layer 2 Tests (Patterns)

**Pattern:** `(?i)(create|build)\s+(an?\s+)?agent`
- ✅ "create an agent for X"
- ✅ "build a agent for Y"
- ✅ "create agent for Z"
- ✅ "Build Agent for tasks"
- ❌ "agent creation guide" (should not match)

[... more patterns]

### Integration Tests

**Capability:** Agent Creation
1. ✅ "create an agent for processing CSVs"
2. ✅ "build automation for email handling"
3. ✅ "automate this workflow: download, process, upload"
4. ✅ "every day I have to categorize files manually"
5. ✅ "turn this process into an automated agent"
6. ✅ "I need a skill for data extraction"
7. ✅ "daily workflow automation needed"
8. ✅ "repeatedly doing manual data entry"
9. ✅ "develop an agent to monitor APIs"
10. ✅ "make something to handle invoices automatically"

**Success Rate:** 10/10 = 100%

### Negative Tests

**Should NOT Activate:**
1. ✅ "How do I use an existing agent?" (did not activate)
2. ✅ "Explain what agents are" (did not activate)
3. ✅ "Debug this code" (did not activate)
4. ✅ "Write a Python function" (did not activate)
5. ✅ "Run the invoice agent" (did not activate)

**Success Rate:** 5/5 = 100%
```

---

## 📚 Additional Resources

- `phase4-detection.md` - Detection methodology
- `activation-patterns-guide.md` - Pattern library
- `activation-quality-checklist.md` - Quality standards
- `ACTIVATION_BEST_PRACTICES.md` - Best practices

---

## 🔧 Troubleshooting

### Issue: Low Success Rate (<90%)

**Diagnosis:**
1. Review failed queries
2. Check if keywords/patterns too narrow
3. Verify description includes key concepts

**Solution:**
1. Add more keyword variations
2. Broaden patterns slightly
3. Enhance description with synonyms

### Issue: False Positives

**Diagnosis:**
1. Review activated queries
2. Check if patterns too broad
3. Verify keywords not too generic

**Solution:**
1. Narrow patterns (add context requirements)
2. Use complete phrases for keywords
3. Add negative scope to description

### Issue: Inconsistent Activation

**Diagnosis:**
1. Test same query multiple times
2. Check for Claude Code updates
3. Verify marketplace.json structure

**Solution:**
1. Use all 3 layers (keywords + patterns + description)
2. Increase keyword/pattern coverage
3. Validate JSON syntax

---

**Version:** 1.0
**Last Updated:** 2025-10-23
**Maintained By:** Agent-Skill-Creator Team
