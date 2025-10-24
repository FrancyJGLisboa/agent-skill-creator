# Activation Test Automation Framework v1.0

**Version:** 1.0
**Purpose:** Automated testing system for skill activation reliability
**Target:** 99.5% activation reliability with <1% false positives

---

## 🎯 **Overview**

This framework provides automated tools to test, validate, and monitor skill activation reliability across the 3-Layer Activation System (Keywords, Patterns, Description + NLU).

### **Problem Solved**

**Before:** Manual testing was time-consuming, inconsistent, and missed edge cases
**After:** Automated testing provides consistent validation, comprehensive coverage, and continuous monitoring

---

## 🛠️ **Core Components**

### **1. Activation Test Suite Generator**
Automatically generates comprehensive test cases for any skill based on its marketplace.json configuration.

### **2. Regex Pattern Validator**
Validates regex patterns against test cases and identifies potential issues.

### **3. Coverage Analyzer**
Calculates activation coverage and identifies gaps in keyword/pattern combinations.

### **4. Continuous Monitor**
Monitors skill activation in real-time and tracks performance metrics.

---

## 📁 **Framework Structure**

```
references/tools/activation-tester/
├── core/
│   ├── test-generator.md          # Test case generation logic
│   ├── pattern-validator.md       # Regex validation tools
│   ├── coverage-analyzer.md       # Coverage calculation
│   └── performance-monitor.md     # Continuous monitoring
├── scripts/
│   ├── run-full-test-suite.sh     # Complete automation script
│   ├── quick-validation.sh        # Fast validation checks
│   ├── regression-test.sh         # Regression testing
│   └── performance-benchmark.sh   # Performance testing
├── templates/
│   ├── test-report-template.md    # Standardized reporting
│   ├── coverage-report-template.md # Coverage analysis
│   └── performance-dashboard.md   # Metrics visualization
└── examples/
    ├── stock-analyzer-test-suite.md # Example test suite
    └── agent-creator-test-suite.md  # Example reference test
```

---

## 🧪 **Test Generation System**

### **Keyword Test Generation**

For each keyword in marketplace.json, the system generates:

```bash
generate_keyword_tests() {
    local keyword="$1"
    local skill_context="$2"

    # 1. Exact match test
    echo "Test: \"${keyword}\""

    # 2. Embedded in sentence
    echo "Test: \"I need to ${keyword} for my project\""

    # 3. Case variations
    echo "Test: \"$(echo ${keyword} | tr '[:lower:]' '[:upper:]')\""

    # 4. Natural language variations
    echo "Test: \"Can you help me ${keyword}?\""

    # 5. Context-specific variations
    echo "Test: \"${keyword} in ${skill_context}\""
}
```

### **Pattern Test Generation**

For each regex pattern, generate comprehensive test cases:

```bash
generate_pattern_tests() {
    local pattern="$1"
    local description="$2"

    # Extract pattern components
    local verbs=$(extract_verbs "$pattern")
    local entities=$(extract_entities "$pattern")
    local contexts=$(extract_contexts "$pattern")

    # Generate positive test cases
    for verb in $verbs; do
        for entity in $entities; do
            echo "Test: \"${verb} ${entity}\""
            echo "Test: \"I want to ${verb} ${entity} now\""
            echo "Test: \"Can you ${verb} ${entity} for me?\""
        done
    done

    # Generate negative test cases
    generate_negative_cases "$pattern"
}
```

### **Integration Test Generation**

Creates realistic user queries combining multiple elements:

```bash
generate_integration_tests() {
    local capabilities=("$@")

    for capability in "${capabilities[@]}"; do
        # Natural language variations
        echo "Test: \"How can I ${capability}?\""
        echo "Test: \"I need help with ${capability}\""
        echo "Test: \"Can you ${capability} for me?\""

        # Workflow context
        echo "Test: \"Every day I have to ${capability}\""
        echo "Test: \"I want to automate ${capability}\""

        # Complex queries
        echo "Test: \"${capability} and show me results\""
        echo "Test: \"Help me understand ${capability} better\""
    done
}
```

---

## 🔍 **Pattern Validation System**

### **Regex Pattern Analyzer**

Validates regex patterns for common issues:

```python
def analyze_pattern(pattern):
    """Analyze regex pattern for potential issues"""
    issues = []
    suggestions = []

    # Check for common regex problems
    if pattern.count('*') > 2:
        issues.append("Too many wildcards - may cause false positives")

    if not re.search(r'\(\?\:i\)', pattern):
        suggestions.append("Add case-insensitive flag: (?i)")

    if pattern.startswith('.*') and pattern.endswith('.*'):
        issues.append("Pattern too broad - may match anything")

    # Calculate pattern specificity
    specificity = calculate_specificity(pattern)

    return {
        'issues': issues,
        'suggestions': suggestions,
        'specificity': specificity,
        'risk_level': assess_risk(pattern)
    }
```

### **Pattern Coverage Test**

Tests pattern against comprehensive query variations:

```bash
test_pattern_coverage() {
    local pattern="$1"
    local test_queries=("$@")
    local matches=0
    local total=${#test_queries[@]}

    for query in "${test_queries[@]}"; do
        if [[ $query =~ $pattern ]]; then
            ((matches++))
            echo "✅ Match: '$query'"
        else
            echo "❌ No match: '$query'"
        fi
    done

    local coverage=$((matches * 100 / total))
    echo "Pattern coverage: ${coverage}%"

    if [[ $coverage -lt 80 ]]; then
        echo "⚠️  Low coverage - consider expanding pattern"
    fi
}
```

---

## 📊 **Coverage Analysis System**

### **Multi-Layer Coverage Calculator**

Calculates coverage across all three activation layers:

```python
def calculate_activation_coverage(skill_config):
    """Calculate comprehensive activation coverage"""

    keywords = skill_config['activation']['keywords']
    patterns = skill_config['activation']['patterns']
    description = skill_config['metadata']['description']

    # Layer 1: Keyword coverage
    keyword_coverage = {
        'total_keywords': len(keywords),
        'categories': categorize_keywords(keywords),
        'synonym_coverage': calculate_synonym_coverage(keywords),
        'natural_language_coverage': calculate_nl_coverage(keywords)
    }

    # Layer 2: Pattern coverage
    pattern_coverage = {
        'total_patterns': len(patterns),
        'pattern_types': categorize_patterns(patterns),
        'regex_complexity': calculate_pattern_complexity(patterns),
        'overlap_analysis': analyze_pattern_overlap(patterns)
    }

    # Layer 3: Description coverage
    description_coverage = {
        'keyword_density': calculate_keyword_density(description, keywords),
        'semantic_richness': analyze_semantic_content(description),
        'concept_coverage': extract_concepts(description)
    }

    # Overall coverage score
    overall_score = calculate_overall_coverage(
        keyword_coverage, pattern_coverage, description_coverage
    )

    return {
        'overall_score': overall_score,
        'keyword_coverage': keyword_coverage,
        'pattern_coverage': pattern_coverage,
        'description_coverage': description_coverage,
        'recommendations': generate_recommendations(overall_score)
    }
```

### **Gap Identification**

Identifies gaps in activation coverage:

```python
def identify_activation_gaps(skill_config, test_results):
    """Identify gaps in activation coverage"""

    gaps = []

    # Analyze failed test queries
    failed_queries = [q for q in test_results if not q['activated']]

    # Categorize failures
    failure_categories = categorize_failures(failed_queries)

    # Identify missing keyword categories
    missing_categories = find_missing_keyword_categories(
        skill_config['activation']['keywords'],
        failure_categories
    )

    # Identify pattern weaknesses
    pattern_gaps = find_pattern_gaps(
        skill_config['activation']['patterns'],
        failed_queries
    )

    # Generate specific recommendations
    for category in missing_categories:
        gaps.append({
            'type': 'missing_keyword_category',
            'category': category,
            'suggestion': f"Add 5-10 keywords from {category} category"
        })

    for gap in pattern_gaps:
        gaps.append({
            'type': 'pattern_gap',
            'gap_type': gap['type'],
            'suggestion': gap['suggestion']
        })

    return gaps
```

---

## 🚀 **Automation Scripts**

### **Full Test Suite Runner**

```bash
#!/bin/bash
# run-full-test-suite.sh

run_full_test_suite() {
    local skill_path="$1"
    local output_dir="$2"

    echo "🧪 Running Full Activation Test Suite"
    echo "Skill: $skill_path"
    echo "Output: $output_dir"

    # 1. Parse skill configuration
    echo "📋 Parsing skill configuration..."
    parse_skill_config "$skill_path"

    # 2. Generate test cases
    echo "🎲 Generating test cases..."
    generate_all_test_cases "$skill_path"

    # 3. Run keyword tests
    echo "🔑 Testing keyword activation..."
    run_keyword_tests "$skill_path"

    # 4. Run pattern tests
    echo "🔍 Testing pattern matching..."
    run_pattern_tests "$skill_path"

    # 5. Run integration tests
    echo "🔗 Testing integration scenarios..."
    run_integration_tests "$skill_path"

    # 6. Run negative tests
    echo "🚫 Testing false positives..."
    run_negative_tests "$skill_path"

    # 7. Calculate coverage
    echo "📊 Calculating coverage..."
    calculate_coverage "$skill_path"

    # 8. Generate report
    echo "📄 Generating test report..."
    generate_test_report "$skill_path" "$output_dir"

    echo "✅ Test suite completed!"
    echo "📁 Report available at: $output_dir/activation-test-report.html"
}
```

### **Quick Validation Script**

```bash
#!/bin/bash
# quick-validation.sh

quick_validation() {
    local skill_path="$1"

    echo "⚡ Quick Activation Validation"

    # Fast JSON validation
    if ! python3 -m json.tool "$skill_path/marketplace.json" > /dev/null 2>&1; then
        echo "❌ Invalid JSON in marketplace.json"
        return 1
    fi

    # Check required fields
    check_required_fields "$skill_path"

    # Validate regex patterns
    validate_patterns "$skill_path"

    # Quick keyword count check
    keyword_count=$(jq '.activation.keywords | length' "$skill_path/marketplace.json")
    if [[ $keyword_count -lt 20 ]]; then
        echo "⚠️  Low keyword count: $keyword_count (recommend 50+)"
    fi

    # Pattern count check
    pattern_count=$(jq '.activation.patterns | length' "$skill_path/marketplace.json")
    if [[ $pattern_count -lt 8 ]]; then
        echo "⚠️  Low pattern count: $pattern_count (recommend 10+)"
    fi

    echo "✅ Quick validation completed"
}
```

---

## 📈 **Performance Monitoring**

### **Real-time Activation Monitor**

```python
class ActivationMonitor:
    """Monitor skill activation performance in real-time"""

    def __init__(self, skill_name):
        self.skill_name = skill_name
        self.activation_log = []
        self.performance_metrics = {
            'total_activations': 0,
            'successful_activations': 0,
            'failed_activations': 0,
            'average_response_time': 0,
            'activation_by_layer': {
                'keywords': 0,
                'patterns': 0,
                'description': 0
            }
        }

    def log_activation(self, query, activated, layer, response_time):
        """Log activation attempt"""
        self.activation_log.append({
            'timestamp': datetime.now(),
            'query': query,
            'activated': activated,
            'layer': layer,
            'response_time': response_time
        })

        self.update_metrics(activated, layer, response_time)

    def calculate_reliability_score(self):
        """Calculate current reliability score"""
        if self.performance_metrics['total_activations'] == 0:
            return 0.0

        success_rate = (
            self.performance_metrics['successful_activations'] /
            self.performance_metrics['total_activations']
        )

        return success_rate

    def generate_alerts(self):
        """Generate performance alerts"""
        alerts = []

        reliability = self.calculate_reliability_score()
        if reliability < 0.95:
            alerts.append({
                'type': 'low_reliability',
                'message': f'Reliability dropped to {reliability:.2%}',
                'severity': 'high'
            })

        avg_response_time = self.performance_metrics['average_response_time']
        if avg_response_time > 5.0:
            alerts.append({
                'type': 'slow_response',
                'message': f'Average response time: {avg_response_time:.2f}s',
                'severity': 'medium'
            })

        return alerts
```

---

## 📋 **Usage Examples**

### **Example 1: Testing Stock Analyzer Skill**

```bash
# Run full test suite
./run-full-test-suite.sh \
    /path/to/stock-analyzer-cskill \
    /output/test-results

# Quick validation
./quick-validation.sh /path/to/stock-analyzer-cskill

# Monitor performance
./performance-benchmark.sh stock-analyzer-cskill
```

### **Example 2: Integration with Development Workflow**

```yaml
# .github/workflows/activation-testing.yml
name: Activation Testing

on: [push, pull_request]

jobs:
  test-activation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Activation Tests
        run: |
          ./references/tools/activation-tester/scripts/run-full-test-suite.sh \
            ./references/examples/stock-analyzer-cskill \
            ./test-results
      - name: Upload Test Results
        uses: actions/upload-artifact@v2
        with:
          name: activation-test-results
          path: ./test-results/
```

---

## ✅ **Quality Standards**

### **Test Coverage Requirements**
- [ ] 100% keyword coverage testing
- [ ] 95%+ pattern coverage validation
- [ ] All capability variations tested
- [ ] Edge cases documented and tested
- [ ] Negative testing for false positives

### **Performance Benchmarks**
- [ ] Activation reliability: 99.5%+
- [ ] False positive rate: <1%
- [ ] Test execution time: <30 seconds
- [ ] Memory usage: <100MB
- [ ] Response time: <2 seconds average

### **Reporting Standards**
- [ ] Automated test report generation
- [ ] Performance metrics dashboard
- [ ] Historical trend analysis
- [ ] Actionable recommendations
- [ ] Integration with CI/CD pipeline

---

## 🔄 **Continuous Improvement**

### **Feedback Loop Integration**
1. **Collect** activation data from real usage
2. **Analyze** performance metrics and failure patterns
3. **Identify** optimization opportunities
4. **Implement** improvements to keywords/patterns
5. **Validate** improvements with automated testing
6. **Deploy** updated configurations

### **A/B Testing Framework**
- Test different keyword combinations
- Compare pattern performance
- Validate description effectiveness
- Measure user satisfaction impact

---

## 📚 **Additional Resources**

- `../activation-testing-guide.md` - Manual testing procedures
- `../activation-patterns-guide.md` - Pattern library
- `../phase4-detection.md` - Detection methodology
- `../synonym-expansion-system.md` - Keyword expansion

---

**Version:** 1.0
**Last Updated:** 2025-10-24
**Maintained By:** Agent-Skill-Creator Team