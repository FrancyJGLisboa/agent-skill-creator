# Activation Quality Checklist

**Version:** 1.0
**Purpose:** Ensure high-quality activation system for all created skills

---

## Overview

Use this checklist during Phase 4 (Detection) to ensure the skill has robust, reliable activation. **All items must be checked before proceeding to Phase 5.**

**Target:** 95%+ activation reliability with zero false positives

---

## ✅ Layer 1: Keywords Quality

### Quantity
- [ ] **Minimum 10 keywords defined**
- [ ] **Maximum 20 keywords** (more can dilute effectiveness)
- [ ] At least 3 categories covered (action, workflow, domain)

### Quality
- [ ] **All keywords are complete phrases** (not single words)
- [ ] No keywords shorter than 2 words
- [ ] **No overly generic keywords** (e.g., "data", "analysis" alone)
- [ ] Each keyword is unique and non-redundant

### Coverage
- [ ] Keywords cover main capability: {{capability-1}}
- [ ] Keywords cover secondary capability: {{capability-2}}
- [ ] Keywords cover tertiary capability: {{capability-3}}
- [ ] **At least 3 keywords per major capability**

### Specificity
- [ ] Keywords include action verbs (create, analyze, extract)
- [ ] Keywords include domain entities (agent, stock, crop)
- [ ] Keywords include context modifiers when appropriate

### Examples
- [ ] ✅ Good: "create an agent for"
- [ ] ✅ Good: "stock technical analysis"
- [ ] ✅ Good: "harvest progress data"
- [ ] ❌ Bad: "create" (single word)
- [ ] ❌ Bad: "data analysis" (too generic)
- [ ] ❌ Bad: "help me" (too vague)

---

## ✅ Layer 2: Patterns Quality

### Quantity
- [ ] **Minimum 5 patterns defined**
- [ ] **Maximum 10 patterns** (more can create conflicts)
- [ ] At least 3 pattern types covered (action, transformation, query)

### Structure
- [ ] **All patterns start with (?i)** for case-insensitivity
- [ ] All patterns include action verb group
- [ ] Patterns allow for flexible word order where appropriate
- [ ] **No patterns match single words only**

### Specificity vs Flexibility
- [ ] Patterns are specific enough (avoid false positives)
- [ ] Patterns are flexible enough (capture variations)
- [ ] Patterns require both verb AND entity/context
- [ ] **Tested each pattern independently**

### Quality Checks
- [ ] **Pattern 1: Action + Object pattern exists**
  - Example: `(?i)(create|build)\s+(an?\s+)?agent\s+for`
- [ ] **Pattern 2: Domain-specific pattern exists**
  - Example: `(?i)(analyze|monitor)\s+.*\s+(stock|crop)`
- [ ] **Pattern 3: Workflow pattern exists** (if applicable)
  - Example: `(?i)(every day|daily)\s+I\s+(have to|need)`
- [ ] **Pattern 4: Transformation pattern exists** (if applicable)
  - Example: `(?i)(convert|transform)\s+.*\s+into`
- [ ] Pattern 5-7: Additional patterns cover edge cases

### Testing
- [ ] **Each pattern tested with 5+ positive examples**
- [ ] Each pattern tested with 2+ negative examples
- [ ] No pattern has >20% false positive rate
- [ ] Combined patterns achieve >80% coverage

---

## ✅ Layer 3: Description Quality

### Content Requirements
- [ ] **60+ unique keywords included in description**
- [ ] All major capabilities explicitly mentioned
- [ ] **Each capability has synonyms** in parentheses
- [ ] Technology/API/data source names included
- [ ] 3-5 example use cases mentioned

### Structure
- [ ] Description starts with primary use case
- [ ] **"Activates for queries about:"** section included
- [ ] **"Does NOT activate for:"** section included
- [ ] Length is 300-500 characters (comprehensive but not excessive)

### Keyword Integration
- [ ] All Layer 1 keywords appear in description
- [ ] Domain-specific terms well-represented
- [ ] Action verbs prominently featured
- [ ] Geographic/temporal qualifiers included (if relevant)

### Clarity
- [ ] Description is readable and natural
- [ ] No keyword stuffing (keywords flow naturally)
- [ ] Technical terms explained where necessary
- [ ] **User can understand when to use skill**

---

## ✅ Usage Section Quality

### when_to_use
- [ ] **Minimum 5 use cases listed**
- [ ] Use cases are specific and actionable
- [ ] Use cases cover all major capabilities
- [ ] Use cases use natural language

### when_not_to_use
- [ ] **Minimum 3 counter-cases listed**
- [ ] Counter-cases prevent common false positives
- [ ] Counter-cases clearly distinguish from similar skills
- [ ] Each counter-case explains WHY not to use

### Example
- [ ] **Concrete example query provided**
- [ ] Example demonstrates typical usage
- [ ] Example would actually activate the skill

---

## ✅ Test Queries Quality

### Quantity
- [ ] **Minimum 10 test queries defined**
- [ ] At least 2 queries per major capability
- [ ] Mix of query types (direct, natural, edge cases)

### Coverage
- [ ] Tests cover Layer 1 (keywords)
- [ ] Tests cover Layer 2 (patterns)
- [ ] Tests cover Layer 3 (description/NLU)
- [ ] Tests cover all capabilities
- [ ] Tests include edge cases

### Quality
- [ ] Queries use natural language
- [ ] Queries are realistic user requests
- [ ] Queries vary in phrasing and structure
- [ ] **Each query documented with expected activation layer**

### Negative Tests
- [ ] **Minimum 3 negative test cases** (should NOT activate)
- [ ] Negative cases test counter-examples from when_not_to_use
- [ ] Negative cases documented separately

---

## ✅ Integration & Conflicts

### Conflict Check
- [ ] **Reviewed other existing skills in ecosystem**
- [ ] No keyword conflicts with other skills
- [ ] Patterns don't overlap significantly with other skills
- [ ] Clear differentiation from similar skills

### Priority
- [ ] Activation priority is appropriate
- [ ] More specific skills have higher priority if needed
- [ ] Domain-specific skills prioritized over general skills

---

## ✅ Documentation

### In marketplace.json
- [ ] **activation section complete**
- [ ] **usage section complete**
- [ ] **test_queries array populated**
- [ ] All JSON is valid (no syntax errors)

### In SKILL.md
- [ ] Keywords section included
- [ ] Activation examples (positive and negative)
- [ ] Use cases clearly documented

### In README.md
- [ ] **Activation section included** (see template)
- [ ] 10+ activation phrase examples
- [ ] Counter-examples documented
- [ ] Activation tips provided

---

## ✅ Testing Validation

### Layer Testing
- [ ] **Layer 1 (Keywords) tested individually**
  - Pass rate: ___% (target: 100%)
- [ ] **Layer 2 (Patterns) tested individually**
  - Pass rate: ___% (target: 100%)
- [ ] **Layer 3 (Description) tested with edge cases**
  - Pass rate: ___% (target: 90%+)

### Integration Testing
- [ ] **All test_queries tested in Claude Code**
  - Pass rate: ___% (target: 95%+)
- [ ] Negative tests verified (no false positives)
  - Pass rate: ___% (target: 100%)

### Results
- [ ] **Overall success rate: ____%** (target: >=95%)
- [ ] **False positive rate: ____%** (target: 0%)
- [ ] **False negative rate: ____%** (target: <5%)

---

## ✅ Final Verification

### Pre-Deployment
- [ ] All above checklists completed
- [ ] Test report documented
- [ ] Issues identified and fixed
- [ ] **Activation success rate >= 95%**

### Documentation Complete
- [ ] marketplace.json reviewed and validated
- [ ] SKILL.md includes activation section
- [ ] README.md includes activation examples
- [ ] TESTING.md created (if complex skill)

### Sign-Off
- [ ] Creator reviewed activation system
- [ ] Test results satisfactory
- [ ] Ready for Phase 5 (Implementation)

---

## 📊 Scoring System

### Minimum Requirements

| Layer | Minimum Score | Target Score |
|-------|---------------|--------------|
| Keywords (Layer 1) | 10 keywords | 12-15 keywords |
| Patterns (Layer 2) | 5 patterns | 7 patterns |
| Description (Layer 3) | 300 chars, 60+ keywords | 400 chars, 80+ keywords |
| Test Queries | 10 queries | 15+ queries |
| Success Rate | 90% | 95%+ |

### Grading

**A (Excellent):** 95%+ success rate, all requirements met
**B (Good):** 90-94% success rate, most requirements met
**C (Acceptable):** 85-89% success rate, minimum requirements met
**F (Needs Work):** <85% success rate, requirements not met

**Only Grade A skills should proceed to implementation.**

---

## 🚨 Common Issues Checklist

### Issue: Low Activation Rate (<90%)

**Check:**
- [ ] Are keywords too specific/narrow?
- [ ] Are patterns too restrictive?
- [ ] Is description missing key concepts?
- [ ] Are test queries realistic?

### Issue: False Positives

**Check:**
- [ ] Are keywords too generic?
- [ ] Are patterns too broad?
- [ ] Is description unclear about scope?
- [ ] Are when_not_to_use cases defined?

### Issue: Inconsistent Activation

**Check:**
- [ ] Are all 3 layers properly configured?
- [ ] Is JSON syntax valid?
- [ ] Are patterns properly escaped?
- [ ] Has testing been thorough?

---

## 📝 Quick Reference

### Minimum Requirements Summary

**Must Have:**
- ✅ 10+ keywords (complete phrases)
- ✅ 5+ patterns (with verbs + entities)
- ✅ 300+ char description (60+ keywords)
- ✅ 5+ when_to_use cases
- ✅ 3+ when_not_to_use cases
- ✅ 10+ test queries
- ✅ 95%+ success rate

**Should Have:**
- ⭐ 15 keywords
- ⭐ 7 patterns
- ⭐ 400+ char description (80+ keywords)
- ⭐ 15+ test queries
- ⭐ 98%+ success rate
- ⭐ Zero false positives

---

## 📚 Additional Resources

- `phase4-detection.md` - Complete detection methodology
- `activation-patterns-guide.md` - Pattern library
- `activation-testing-guide.md` - Testing procedures
- `marketplace-robust-template.json` - Template with placeholders
- `README-activation-template.md` - README template

---

**Status:** ___ (In Progress / Complete)
**Reviewer:** ___
**Date:** ___
**Success Rate:** ___%
**Grade:** ___ (A / B / C / F)

---

**Version:** 1.0
**Last Updated:** 2025-10-23
**Maintained By:** Agent-Skill-Creator Team
