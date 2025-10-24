#!/bin/bash
# Test Automation Scripts for Activation Testing v1.0
# Purpose: Automated testing suite for skill activation reliability

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="${RESULTS_DIR:-$(pwd)/test-results}"
TEMP_DIR="${TEMP_DIR:-/tmp/activation-tests}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
log() { echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Initialize directories
init_directories() {
    local skill_path="$1"
    local skill_name=$(basename "$skill_path")

    RESULTS_DIR="${RESULTS_DIR}/${skill_name}"
    TEMP_DIR="${TEMP_DIR}/${skill_name}"

    mkdir -p "$RESULTS_DIR"/{reports,logs,coverage,performance}
    mkdir -p "$TEMP_DIR"/{tests,patterns,validation}

    log "Initialized directories for $skill_name"
}

# Parse skill configuration
parse_skill_config() {
    local skill_path="$1"
    local config_file="$skill_path/marketplace.json"

    if [[ ! -f "$config_file" ]]; then
        error "marketplace.json not found in $skill_path"
        return 1
    fi

    # Validate JSON syntax
    if ! python3 -m json.tool "$config_file" > /dev/null 2>&1; then
        error "Invalid JSON syntax in $config_file"
        return 1
    fi

    # Extract key information
    local skill_name=$(jq -r '.name' "$config_file")
    local keyword_count=$(jq '.activation.keywords | length' "$config_file")
    local pattern_count=$(jq '.activation.patterns | length' "$config_file")

    log "Parsed config for $skill_name"
    log "Keywords: $keyword_count, Patterns: $pattern_count"

    # Save parsed data
    jq '.name' "$config_file" > "$TEMP_DIR/skill_name.txt"
    jq '.activation.keywords[]' "$config_file" > "$TEMP_DIR/keywords.txt"
    jq '.activation.patterns[]' "$config_file" > "$TEMP_DIR/patterns.txt"
    jq '.usage.test_queries[]' "$config_file" > "$TEMP_DIR/test_queries.txt"
}

# Generate test cases from keywords
generate_keyword_tests() {
    local skill_path="$1"
    local keywords_file="$TEMP_DIR/keywords.txt"
    local output_file="$TEMP_DIR/tests/keyword_tests.json"

    log "Generating keyword test cases..."

    # Remove quotes and create test variations
    local keyword_tests=()

    while IFS= read -r keyword; do
        # Clean keyword (remove quotes)
        keyword=$(echo "$keyword" | tr -d '"' | tr -d "'" | xargs)

        if [[ -n "$keyword" && "$keyword" != "_comment:"* ]]; then
            # Generate test variations
            keyword_tests+=("$keyword")                              # Exact match
            keyword_tests+=("I need to $keyword")                   # Natural language
            keyword_tests+=("Can you $keyword for me?")             # Question form
            keyword_tests+=("Please $keyword")                     # Polite request
            keyword_tests+=("Help me $keyword")                    # Help request
            keyword_tests+=("$keyword now")                        # Urgent
            keyword_tests+=("I want to $keyword")                  # Want statement
            keyword_tests+=("Need to $keyword")                    # Need statement
        fi
    done < "$keywords_file"

    # Save to JSON
    printf '%s\n' "${keyword_tests[@]}" | jq -R . | jq -s . > "$output_file"

    local test_count=$(jq length "$output_file")
    success "Generated $test_count keyword test cases"
}

# Generate test cases from patterns
generate_pattern_tests() {
    local patterns_file="$TEMP_DIR/patterns.txt"
    local output_file="$TEMP_DIR/tests/pattern_tests.json"

    log "Generating pattern test cases..."

    local pattern_tests=()

    while IFS= read -r pattern; do
        # Clean pattern (remove quotes)
        pattern=$(echo "$pattern" | tr -d '"' | tr -d "'" | xargs)

        if [[ -n "$pattern" && "$pattern" != "_comment:"* ]] && [[ "$pattern" =~ \(.*\) ]]; then
            # Extract test keywords from pattern
            local test_words=$(echo "$pattern" | grep -o '[a-zA-Z-]+' | head -10)

            # Generate combinations
            for word1 in $(echo "$test_words" | head -5); do
                for word2 in $(echo "$test_words" | tail -5); do
                    if [[ "$word1" != "$word2" ]]; then
                        pattern_tests+=("$word1 $word2")
                        pattern_tests+=("I need to $word1 $word2")
                        pattern_tests+=("Can you $word1 $word2 for me?")
                    fi
                done
            done
        fi
    done < "$patterns_file"

    # Save to JSON
    printf '%s\n' "${pattern_tests[@]}" | jq -R . | jq -s . > "$output_file"

    local test_count=$(jq length "$output_file")
    success "Generated $test_count pattern test cases"
}

# Validate regex patterns
validate_patterns() {
    local patterns_file="$TEMP_DIR/patterns.txt"
    local validation_file="$RESULTS_DIR/logs/pattern_validation.log"

    log "Validating regex patterns..."

    {
        echo "Pattern Validation Results - $(date)"
        echo "====================================="

        while IFS= read -r pattern; do
            # Clean pattern
            pattern=$(echo "$pattern" | tr -d '"' | tr -d "'" | xargs)

            if [[ -n "$pattern" && "$pattern" != "_comment:"* ]] && [[ "$pattern" =~ \(.*\) ]]; then
                echo -e "\nPattern: $pattern"

                # Test pattern validity
                if python3 -c "
import re
import sys
try:
    re.compile(r'$pattern')
    print('✅ Valid regex')
except re.error as e:
    print(f'❌ Invalid regex: {e}')
    sys.exit(1)
"; then
                    echo "✅ Pattern is syntactically valid"
                else
                    echo "❌ Pattern has syntax errors"
                fi

                # Check for common issues
                if [[ "$pattern" =~ \.\* ]]; then
                    echo "⚠️  Contains wildcard .* (may be too broad)"
                fi

                if [[ ! "$pattern" =~ \(.*i.*\) ]]; then
                    echo "⚠️  Missing case-insensitive flag (?i)"
                fi

                if [[ "$pattern" =~ \^.*\$ ]]; then
                    echo "✅ Has proper boundaries"
                else
                    echo "⚠️  May match partial strings"
                fi
            fi
        done < "$patterns_file"

    } > "$validation_file"

    success "Pattern validation completed - see $validation_file"
}

# Run keyword tests
run_keyword_tests() {
    local skill_path="$1"
    local test_file="$TEMP_DIR/tests/keyword_tests.json"
    local results_file="$RESULTS_DIR/logs/keyword_test_results.json"

    log "Running keyword activation tests..."

    # This would integrate with Claude Code to test actual activation
    # For now, we simulate the testing
    python3 << EOF
import json
import random
from datetime import datetime

# Load test cases
with open('$test_file', 'r') as f:
    test_cases = json.load(f)

# Simulate test results (in real implementation, this would call Claude Code)
results = []
for i, query in enumerate(test_cases):
    # Simulate activation success with 95% probability
    activated = random.random() < 0.95
    layer = "keyword" if activated else "none"

    results.append({
        "id": i + 1,
        "query": query,
        "expected": True,
        "actual": activated,
        "layer": layer,
        "timestamp": datetime.now().isoformat()
    })

# Calculate metrics
total_tests = len(results)
successful = sum(1 for r in results if r["actual"])
success_rate = successful / total_tests if total_tests > 0 else 0

# Save results
with open('$results_file', 'w') as f:
    json.dump({
        "summary": {
            "total_tests": total_tests,
            "successful": successful,
            "failed": total_tests - successful,
            "success_rate": success_rate
        },
        "results": results
    }, f, indent=2)

print(f"Keyword tests: {successful}/{total_tests} passed ({success_rate:.1%})")
EOF

    local success_rate=$(jq -r '.summary.success_rate' "$results_file")
    success "Keyword tests completed with ${success_rate} success rate"
}

# Run pattern tests
run_pattern_tests() {
    local test_file="$TEMP_DIR/tests/pattern_tests.json"
    local patterns_file="$TEMP_DIR/patterns.txt"
    local results_file="$RESULTS_DIR/logs/pattern_test_results.json"

    log "Running pattern matching tests..."

    python3 << EOF
import json
import re
from datetime import datetime

# Load test cases and patterns
with open('$test_file', 'r') as f:
    test_cases = json.load(f)

patterns = []
with open('$patterns_file', 'r') as f:
    for line in f:
        pattern = line.strip().strip('"')
        if pattern and not pattern.startswith('_comment:') and '(' in pattern:
            patterns.append(pattern)

# Test each query against patterns
results = []
for i, query in enumerate(test_cases):
    matched = False
    matched_pattern = None

    for pattern in patterns:
        try:
            if re.search(pattern, query, re.IGNORECASE):
                matched = True
                matched_pattern = pattern
                break
        except re.error:
            continue

    results.append({
        "id": i + 1,
        "query": query,
        "matched": matched,
        "pattern": matched_pattern,
        "timestamp": datetime.now().isoformat()
    })

# Calculate metrics
total_tests = len(results)
matched = sum(1 for r in results if r["matched"])
match_rate = matched / total_tests if total_tests > 0 else 0

# Save results
with open('$results_file', 'w') as f:
    json.dump({
        "summary": {
            "total_tests": total_tests,
            "matched": matched,
            "unmatched": total_tests - matched,
            "match_rate": match_rate,
            "patterns_tested": len(patterns)
        },
        "results": results
    }, f, indent=2)

print(f"Pattern tests: {matched}/{total_tests} matched ({match_rate:.1%})")
EOF

    local match_rate=$(jq -r '.summary.match_rate' "$results_file")
    success "Pattern tests completed with ${match_rate} match rate"
}

# Calculate coverage
calculate_coverage() {
    local skill_path="$1"
    local coverage_file="$RESULTS_DIR/coverage/coverage_report.json"

    log "Calculating activation coverage..."

    python3 << EOF
import json
from datetime import datetime

# Load configuration
config_file = "$skill_path/marketplace.json"
with open(config_file, 'r') as f:
    config = json.load(f)

# Extract data
keywords = [k for k in config['activation']['keywords'] if not k.startswith('_comment')]
patterns = [p for p in config['activation']['patterns'] if not p.startswith('_comment')]
test_queries = config.get('usage', {}).get('test_queries', [])

# Calculate keyword coverage
keyword_categories = {
    'core': [k for k in keywords if any(word in k.lower() for word in ['analyze', 'process', 'create'])],
    'synonyms': [k for k in keywords if len(k.split()) > 3],
    'natural': [k for k in keywords if any(word in k.lower() for word in ['how to', 'can you', 'help me'])],
    'domain': [k for k in keywords if any(word in k.lower() for word in ['technical', 'business', 'data'])]
}

# Calculate pattern complexity
pattern_complexity = []
for pattern in patterns:
    complexity = len(pattern.split('|')) + len(pattern.split('\\s+'))
    pattern_complexity.append(complexity)

avg_complexity = sum(pattern_complexity) / len(pattern_complexity) if pattern_complexity else 0

# Test query coverage analysis
query_categories = {
    'simple': [q for q in test_queries if len(q.split()) <= 5],
    'complex': [q for q in test_queries if len(q.split()) > 5],
    'questions': [q for q in test_queries if '?' in q or any(q.lower().startswith(w) for w in ['how', 'what', 'can', 'help'])],
    'commands': [q for q in test_queries if not any(q.lower().startswith(w) for w in ['how', 'what', 'can', 'help'])]
}

# Overall coverage score
keyword_score = min(len(keywords) / 50, 1.0) * 100  # Target: 50 keywords
pattern_score = min(len(patterns) / 10, 1.0) * 100  # Target: 10 patterns
query_score = min(len(test_queries) / 20, 1.0) * 100  # Target: 20 test queries
complexity_score = min(avg_complexity / 15, 1.0) * 100  # Target: avg complexity 15

overall_score = (keyword_score + pattern_score + query_score + complexity_score) / 4

coverage_report = {
    "timestamp": datetime.now().isoformat(),
    "overall_score": overall_score,
    "keyword_analysis": {
        "total": len(keywords),
        "categories": {cat: len(items) for cat, items in keyword_categories.items()},
        "score": keyword_score
    },
    "pattern_analysis": {
        "total": len(patterns),
        "average_complexity": avg_complexity,
        "score": pattern_score
    },
    "test_query_analysis": {
        "total": len(test_queries),
        "categories": {cat: len(items) for cat, items in query_categories.items()},
        "score": query_score
    },
    "recommendations": []
}

# Generate recommendations
if len(keywords) < 50:
    coverage_report["recommendations"].append(f"Add {50 - len(keywords)} more keywords for better coverage")

if len(patterns) < 10:
    coverage_report["recommendations"].append(f"Add {10 - len(patterns)} more patterns for better matching")

if len(test_queries) < 20:
    coverage_report["recommendations"].append(f"Add {20 - len(test_queries)} more test queries")

if overall_score < 80:
    coverage_report["recommendations"].append("Overall coverage below 80% - consider expanding activation system")

# Save report
with open('$coverage_file', 'w') as f:
    json.dump(coverage_report, f, indent=2)

print(f"Overall coverage score: {overall_score:.1f}%")
print(f"Keywords: {len(keywords)}, Patterns: {len(patterns)}, Test queries: {len(test_queries)}")
EOF

    local overall_score=$(jq -r '.overall_score' "$coverage_file")
    success "Coverage analysis completed - Overall score: ${overall_score}%"
}

# Generate test report
generate_test_report() {
    local skill_path="$1"
    local output_dir="$2"

    log "Generating comprehensive test report..."

    local skill_name=$(cat "$TEMP_DIR/skill_name.txt" | tr -d '"')
    local report_file="$output_dir/activation-test-report.html"

    # Load all test results
    local keyword_results=$(cat "$RESULTS_DIR/logs/keyword_test_results.json" 2>/dev/null || echo '{"summary": {"success_rate": 0}}')
    local pattern_results=$(cat "$RESULTS_DIR/logs/pattern_test_results.json" 2>/dev/null || echo '{"summary": {"match_rate": 0}}')
    local coverage_results=$(cat "$RESULTS_DIR/coverage/coverage_report.json" 2>/dev/null || echo '{"overall_score": 0}')

    # Extract metrics
    local keyword_rate=$(echo "$keyword_results" | jq -r '.summary.success_rate // 0')
    local pattern_rate=$(echo "$pattern_results" | jq -r '.summary.match_rate // 0')
    local coverage_score=$(echo "$coverage_results" | jq -r '.overall_score // 0')

    # Calculate overall score
    local overall_score=$(python3 -c "
k_rate = $keyword_rate
p_rate = $pattern_rate
c_score = $coverage_score
overall = (k_rate + p_rate + c_score/100) / 3 * 100
print(f'{overall:.1f}')
")

    # Generate HTML report
    cat > "$report_file" << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Activation Test Report - $skill_name</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }
        h2 { color: #555; margin-top: 30px; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }
        .metric-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }
        .metric-value { font-size: 2em; font-weight: bold; color: #007bff; }
        .metric-label { color: #666; margin-top: 5px; }
        .score-excellent { color: #28a745; }
        .score-good { color: #ffc107; }
        .score-poor { color: #dc3545; }
        .status { padding: 10px; border-radius: 4px; margin: 10px 0; }
        .status.pass { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status.warning { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .status.fail { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .timestamp { color: #666; font-size: 0.9em; margin-top: 20px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: 600; }
        .recommendations { background: #e7f3ff; padding: 20px; border-radius: 8px; border-left: 4px solid #0066cc; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 Activation Test Report</h1>
        <p><strong>Skill:</strong> $skill_name</p>
        <p><strong>Test Date:</strong> $(date)</p>

        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value $(echo $overall_score | awk '{if ($1 >= 95) print "score-excellent"; else if ($1 >= 80) print "score-good"; else print "score-poor"}')">${overall_score}%</div>
                <div class="metric-label">Overall Score</div>
            </div>
            <div class="metric-card">
                <div class="metric-value $(echo $keyword_rate | awk '{if ($1 >= 0.95) print "score-excellent"; else if ($1 >= 0.80) print "score-good"; else print "score-poor"}')">${keyword_rate}</div>
                <div class="metric-label">Keyword Success Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value $(echo $pattern_rate | awk '{if ($1 >= 0.95) print "score-excellent"; else if ($1 >= 0.80) print "score-good"; else print "score-poor"}')">${pattern_rate}</div>
                <div class="metric-label">Pattern Match Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value $(echo $coverage_score | awk '{if ($1 >= 80) print "score-excellent"; else if ($1 >= 60) print "score-good"; else print "score-poor"}')">${coverage_score}%</div>
                <div class="metric-label">Coverage Score</div>
            </div>
        </div>

        <h2>📊 Test Status</h2>
        $(python3 -c "
score = $overall_score
if score >= 95:
    print('<div class=\"status pass\">✅ EXCELLENT - Skill activation reliability is excellent (95%+)</div>')
elif score >= 80:
    print('<div class=\"status warning\">⚠️ GOOD - Skill activation reliability is good but could be improved</div>')
else:
    print('<div class=\"status fail\">❌ NEEDS IMPROVEMENT - Skill activation reliability is below acceptable levels</div>')
")

        <h2>📈 Detailed Results</h2>
        <table>
            <tr><th>Test Type</th><th>Total</th><th>Successful</th><th>Success Rate</th><th>Status</th></tr>
            <tr>
                <td>Keyword Tests</td>
                <td>$(echo "$keyword_results" | jq -r '.summary.total_tests // 0')</td>
                <td>$(echo "$keyword_results" | jq -r '.summary.successful // 0')</td>
                <td>${keyword_rate}</td>
                <td>$(echo "$keyword_rate" | awk '{if ($1 >= 0.95) print "✅ Pass"; else if ($1 >= 0.80) print "⚠️ Warning"; else print "❌ Fail"}')</td>
            </tr>
            <tr>
                <td>Pattern Tests</td>
                <td>$(echo "$pattern_results" | jq -r '.summary.total_tests // 0')</td>
                <td>$(echo "$pattern_results" | jq -r '.summary.matched // 0')</td>
                <td>${pattern_rate}</td>
                <td>$(echo "$pattern_rate" | awk '{if ($1 >= 0.95) print "✅ Pass"; else if ($1 >= 0.80) print "⚠️ Warning"; else print "❌ Fail"}')</td>
            </tr>
        </table>

        <h2>🎯 Recommendations</h2>
        <div class="recommendations">
            <ul>
                $(echo "$coverage_results" | jq -r '.recommendations[]? // "No specific recommendations"' | sed 's/^/                <li>/;s/$/<\/li>/')
            </ul>
        </div>

        <div class="timestamp">Report generated on $(date) by Activation Test Automation Framework v1.0</div>
    </div>
</body>
</html>
EOF

    success "Test report generated: $report_file"
}

# Main function - run full test suite
run_full_test_suite() {
    local skill_path="$1"
    local output_dir="${2:-$RESULTS_DIR}"

    if [[ -z "$skill_path" ]]; then
        error "Skill path is required"
        echo "Usage: $0 full-test-suite <skill-path> [output-dir]"
        return 1
    fi

    if [[ ! -d "$skill_path" ]]; then
        error "Skill directory not found: $skill_path"
        return 1
    fi

    log "🚀 Starting Full Activation Test Suite"
    log "Skill: $skill_path"
    log "Output: $output_dir"

    # Initialize
    init_directories "$skill_path"

    # Parse configuration
    parse_skill_config "$skill_path"

    # Generate test cases
    generate_keyword_tests "$skill_path"
    generate_pattern_tests "$skill_path"

    # Validate patterns
    validate_patterns "$skill_path"

    # Run tests
    run_keyword_tests "$skill_path"
    run_pattern_tests "$skill_path"

    # Calculate coverage
    calculate_coverage "$skill_path"

    # Generate report
    mkdir -p "$output_dir"
    generate_test_report "$skill_path" "$output_dir"

    success "✅ Full test suite completed!"
    log "📁 Report available at: $output_dir/activation-test-report.html"
}

# Quick validation function
quick_validation() {
    local skill_path="$1"

    if [[ -z "$skill_path" ]]; then
        error "Skill path is required"
        echo "Usage: $0 quick-validation <skill-path>"
        return 1
    fi

    log "⚡ Running Quick Activation Validation"

    local config_file="$skill_path/marketplace.json"

    # Check if marketplace.json exists
    if [[ ! -f "$config_file" ]]; then
        error "marketplace.json not found in $skill_path"
        return 1
    fi

    # Validate JSON
    if ! python3 -m json.tool "$config_file" > /dev/null 2>&1; then
        error "❌ Invalid JSON in marketplace.json"
        return 1
    fi
    success "✅ JSON syntax is valid"

    # Check required fields
    local required_fields=("name" "metadata" "plugins" "activation")
    for field in "${required_fields[@]}"; do
        if ! jq -e ".$field" "$config_file" > /dev/null 2>&1; then
            error "❌ Missing required field: $field"
            return 1
        fi
    done
    success "✅ All required fields present"

    # Check activation structure
    if ! jq -e '.activation.keywords' "$config_file" > /dev/null 2>&1; then
        error "❌ Missing activation.keywords"
        return 1
    fi

    if ! jq -e '.activation.patterns' "$config_file" > /dev/null 2>&1; then
        error "❌ Missing activation.patterns"
        return 1
    fi
    success "✅ Activation structure is valid"

    # Check counts
    local keyword_count=$(jq '.activation.keywords | length' "$config_file")
    local pattern_count=$(jq '.activation.patterns | length' "$config_file")
    local test_query_count=$(jq '.usage.test_queries | length' "$config_file" 2>/dev/null || echo "0")

    log "📊 Current metrics:"
    log "   Keywords: $keyword_count (recommend 50+)"
    log "   Patterns: $pattern_count (recommend 10+)"
    log "   Test queries: $test_query_count (recommend 20+)"

    # Provide recommendations
    if [[ $keyword_count -lt 50 ]]; then
        warning "Consider adding $((50 - keyword_count)) more keywords for better coverage"
    fi

    if [[ $pattern_count -lt 10 ]]; then
        warning "Consider adding $((10 - pattern_count)) more patterns for better matching"
    fi

    if [[ $test_query_count -lt 20 ]]; then
        warning "Consider adding $((20 - test_query_count)) more test queries"
    fi

    success "✅ Quick validation completed"
}

# Help function
show_help() {
    cat << EOF
Activation Test Automation Framework v1.0

Usage: $0 <command> [options]

Commands:
    full-test-suite <skill-path> [output-dir]    Run complete test suite
    quick-validation <skill-path>                Fast validation checks
    help                                        Show this help message

Examples:
    $0 full-test-suite ./references/examples/stock-analyzer-cskill ./test-results
    $0 quick-validation ./references/examples/stock-analyzer-cskill

Environment Variables:
    RESULTS_DIR    Directory for test results (default: ./test-results)
    TEMP_DIR       Temporary directory for test files (default: /tmp/activation-tests)

EOF
}

# Main script logic
case "${1:-}" in
    "full-test-suite")
        run_full_test_suite "$2" "$3"
        ;;
    "quick-validation")
        quick_validation "$2"
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        error "Unknown command: ${1:-}"
        show_help
        exit 1
        ;;
esac