# Intent Analyzer Tools v1.0

**Version:** 1.0
**Purpose:** Development and testing tools for multi-intent detection system
**Target:** Validate intent detection with 95%+ accuracy

---

## 🛠️ **Intent Analysis Toolkit**

### **Core Tools**

1. **Intent Parser Validator** - Test intent parsing accuracy
2. **Intent Combination Analyzer** - Analyze intent compatibility
3. **Natural Language Intent Simulator** - Test complex queries
4. **Performance Benchmark Suite** - Measure detection performance

---

## 🔍 **Intent Parser Validator**

### **Usage**

```bash
# Basic intent parsing test
./intent-parser-validator.sh <skill-config> <test-query>

# Batch testing with query file
./intent-parser-validator.sh <skill-config> --batch <queries.txt>

# Full validation suite
./intent-parser-validator.sh <skill-config> --full-suite
```

### **Implementation**

```bash
#!/bin/bash
# intent-parser-validator.sh

validate_intent_parsing() {
    local skill_config="$1"
    local query="$2"

    echo "🔍 Analyzing query: \"$query\""

    # Extract intents using Python implementation
    python3 << EOF
import json
import sys
sys.path.append('..')

# Load skill configuration
with open('$skill_config', 'r') as f:
    config = json.load(f)

# Import intent parser (simplified implementation)
def parse_intent_simple(query):
    """Simplified intent parsing for validation"""

    # Primary intent detection
    primary_patterns = {
        'analyze': ['analyze', 'examine', 'evaluate', 'study'],
        'create': ['create', 'build', 'make', 'generate'],
        'compare': ['compare', 'versus', 'vs', 'ranking'],
        'monitor': ['monitor', 'track', 'watch', 'alert'],
        'transform': ['convert', 'transform', 'change', 'turn']
    }

    # Secondary intent detection
    secondary_patterns = {
        'and_visualize': ['show', 'chart', 'graph', 'visualize'],
        'and_save': ['save', 'export', 'download', 'store'],
        'and_explain': ['explain', 'clarify', 'describe', 'detail']
    }

    query_lower = query.lower()

    # Find primary intent
    primary_intent = None
    for intent, keywords in primary_patterns.items():
        if any(keyword in query_lower for keyword in keywords):
            primary_intent = intent
            break

    # Find secondary intents
    secondary_intents = []
    for intent, keywords in secondary_patterns.items():
        if any(keyword in query_lower for keyword in keywords):
            secondary_intents.append(intent)

    return {
        'primary_intent': primary_intent,
        'secondary_intents': secondary_intents,
        'confidence': 0.8 if primary_intent else 0.0,
        'complexity': 'high' if len(secondary_intents) > 1 else 'medium' if secondary_intents else 'low'
    }

# Parse the query
result = parse_intent_simple('$query')

print("Intent Analysis Results:")
print("=" * 30)
print(f"Primary Intent: {result['primary_intent']}")
print(f"Secondary Intents: {', '.join(result['secondary_intents'])}")
print(f"Confidence: {result['confidence']:.2f}")
print(f"Complexity: {result['complexity']}")

# Validate against skill capabilities
capabilities = config.get('capabilities', {})
supported_primary = capabilities.get('primary_intents', [])
supported_secondary = capabilities.get('secondary_intents', [])

validation_issues = []
if result['primary_intent'] not in supported_primary:
    validation_issues.append(f"Primary intent '{result['primary_intent']}' not supported")

for sec_intent in result['secondary_intents']:
    if sec_intent not in supported_secondary:
        validation_issues.append(f"Secondary intent '{sec_intent}' not supported")

if validation_issues:
    print("Validation Issues:")
    for issue in validation_issues:
        print(f"  - {issue}")
else:
    print("✅ All intents supported by skill")

EOF
}
```

---

## 🔄 **Intent Combination Analyzer**

### **Purpose**

Analyze compatibility and execution order of intent combinations.

### **Implementation**

```python
def analyze_intent_combination(primary_intent, secondary_intents, skill_config):
    """Analyze intent combination compatibility and execution plan"""

    # Get supported combinations from skill config
    supported_combinations = skill_config.get('intent_hierarchy', {}).get('intent_combinations', {})

    # Check for exact combination match
    combination_key = f"{primary_intent}_and_{'_and_'.join(secondary_intents)}"

    if combination_key in supported_combinations:
        return {
            'supported': True,
            'combination_type': 'predefined',
            'execution_plan': supported_combinations[combination_key],
            'confidence': 0.95
        }

    # Check for partial matches
    for sec_intent in secondary_intents:
        partial_key = f"{primary_intent}_and_{sec_intent}"
        if partial_key in supported_combinations:
            return {
                'supported': True,
                'combination_type': 'partial_match',
                'execution_plan': supported_combinations[partial_key],
                'additional_intents': [i for i in secondary_intents if i != sec_intent],
                'confidence': 0.8
            }

    # Check if individual intents are supported
    capabilities = skill_config.get('capabilities', {})
    primary_supported = primary_intent in capabilities.get('primary_intents', [])
    secondary_supported = all(intent in capabilities.get('secondary_intents', []) for intent in secondary_intents)

    if primary_supported and secondary_supported:
        return {
            'supported': True,
            'combination_type': 'dynamic',
            'execution_plan': generate_dynamic_execution_plan(primary_intent, secondary_intents),
            'confidence': 0.7
        }

    return {
        'supported': False,
        'reason': 'One or more intents not supported',
        'fallback_intent': primary_intent if primary_supported else None
    }

def generate_dynamic_execution_plan(primary_intent, secondary_intents):
    """Generate execution plan for non-predefined combinations"""

    plan = {
        'steps': [
            {
                'step': 1,
                'intent': primary_intent,
                'action': f'execute_{primary_intent}',
                'dependencies': []
            }
        ],
        'parallel_steps': []
    }

    # Add secondary intents
    for i, intent in enumerate(secondary_intents):
        if can_execute_parallel(primary_intent, intent):
            plan['parallel_steps'].append({
                'step': f'parallel_{i}',
                'intent': intent,
                'action': f'execute_{intent}',
                'dependencies': ['step_1']
            })
        else:
            plan['steps'].append({
                'step': len(plan['steps']) + 1,
                'intent': intent,
                'action': f'execute_{intent}',
                'dependencies': [f'step_{len(plan["steps"])}']
            })

    return plan

def can_execute_parallel(primary_intent, secondary_intent):
    """Determine if intents can be executed in parallel"""

    parallel_pairs = {
        'analyze': ['and_visualize', 'and_save'],
        'compare': ['and_visualize', 'and_explain'],
        'monitor': ['and_alert', 'and_save']
    }

    return secondary_intent in parallel_pairs.get(primary_intent, [])
```

---

## 🗣️ **Natural Language Intent Simulator**

### **Purpose**

Generate and test natural language variations of intent combinations.

### **Implementation**

```python
class NaturalLanguageIntentSimulator:
    """Generate natural language variations for intent testing"""

    def __init__(self):
        self.templates = {
            'single_intent': [
                "I need to {intent} {entity}",
                "Can you {intent} {entity}?",
                "Please {intent} {entity}",
                "Help me {intent} {entity}",
                "{intent} {entity} for me"
            ],
            'double_intent': [
                "I need to {intent1} {entity} and {intent2} the results",
                "Can you {intent1} {entity} and also {intent2}?",
                "Please {intent1} {entity} and {intent2} everything",
                "Help me {intent1} {entity} and {intent2} the output",
                "{intent1} {entity} and then {intent2}"
            ],
            'triple_intent': [
                "I need to {intent1} {entity}, {intent2} the results, and {intent3}",
                "Can you {intent1} {entity}, {intent2} it, and {intent3} everything?",
                "Please {intent1} {entity}, {intent2} the analysis, and {intent3}",
                "Help me {intent1} {entity}, {intent2} the data, and {intent3} the results"
            ]
        }

        self.intent_variations = {
            'analyze': ['analyze', 'examine', 'evaluate', 'study', 'review', 'assess'],
            'create': ['create', 'build', 'make', 'generate', 'develop', 'design'],
            'compare': ['compare', 'comparison', 'versus', 'vs', 'rank', 'rating'],
            'monitor': ['monitor', 'track', 'watch', 'observe', 'follow', 'keep an eye on'],
            'transform': ['convert', 'transform', 'change', 'turn', 'format', 'structure']
        }

        self.secondary_variations = {
            'and_visualize': ['show me', 'visualize', 'create a chart', 'graph', 'display'],
            'and_save': ['save', 'export', 'download', 'store', 'keep', 'record'],
            'and_explain': ['explain', 'describe', 'detail', 'clarify', 'break down']
        }

        self.entities = {
            'finance': ['AAPL stock', 'MSFT shares', 'market data', 'portfolio performance', 'stock prices'],
            'general': ['this data', 'the information', 'these results', 'the output', 'everything']
        }

    def generate_variations(self, primary_intent, secondary_intents=[], domain='finance'):
        """Generate natural language variations for intent combinations"""

        variations = []
        entity_list = self.entities[domain]

        # Single intent variations
        if not secondary_intents:
            for template in self.templates['single_intent']:
                for primary_verb in self.intent_variations.get(primary_intent, [primary_intent]):
                    for entity in entity_list[:3]:  # Limit to avoid too many variations
                        query = template.format(intent=primary_verb, entity=entity)
                        variations.append({
                            'query': query,
                            'expected_intents': {
                                'primary': primary_intent,
                                'secondary': [],
                                'contextual': []
                            },
                            'complexity': 'low'
                        })

        # Double intent variations
        elif len(secondary_intents) == 1:
            secondary_intent = secondary_intents[0]
            for template in self.templates['double_intent']:
                for primary_verb in self.intent_variations.get(primary_intent, [primary_intent]):
                    for secondary_verb in self.secondary_variations.get(secondary_intent, [secondary_intent.replace('and_', '')]):
                        for entity in entity_list[:2]:
                            query = template.format(
                                intent1=primary_verb,
                                intent2=secondary_verb,
                                entity=entity
                            )
                            variations.append({
                                'query': query,
                                'expected_intents': {
                                    'primary': primary_intent,
                                    'secondary': [secondary_intent],
                                    'contextual': []
                                },
                                'complexity': 'medium'
                            })

        # Triple intent variations
        elif len(secondary_intents) >= 2:
            for template in self.templates['triple_intent']:
                for primary_verb in self.intent_variations.get(primary_intent, [primary_intent]):
                    for entity in entity_list[:2]:
                        secondary_verbs = [
                            self.secondary_variations.get(intent, [intent.replace('and_', '')])[0]
                            for intent in secondary_intents[:2]
                        ]
                        query = template.format(
                            intent1=primary_verb,
                            intent2=secondary_verbs[0],
                            intent3=secondary_verbs[1],
                            entity=entity
                        )
                        variations.append({
                            'query': query,
                            'expected_intents': {
                                'primary': primary_intent,
                                'secondary': secondary_intents[:2],
                                'contextual': []
                            },
                            'complexity': 'high'
                        })

        return variations

    def generate_test_suite(self, skill_config, num_variations=10):
        """Generate complete test suite for a skill"""

        test_suite = []

        # Get supported intents from skill config
        capabilities = skill_config.get('capabilities', {})
        primary_intents = capabilities.get('primary_intents', [])
        secondary_intents = capabilities.get('secondary_intents', [])

        # Generate single intent tests
        for primary in primary_intents[:3]:  # Limit to avoid too many tests
            variations = self.generate_variations(primary, [], 'finance')
            test_suite.extend(variations[:num_variations])

        # Generate double intent tests
        for primary in primary_intents[:2]:
            for secondary in secondary_intents[:2]:
                variations = self.generate_variations([primary], [secondary], 'finance')
                test_suite.extend(variations[:num_variations//2])

        # Generate triple intent tests
        for primary in primary_intents[:1]:
            combinations = []
            for i, sec1 in enumerate(secondary_intents[:2]):
                for sec2 in secondary_intents[i+1:i+2]:
                    combinations.append([sec1, sec2])

            for combo in combinations:
                variations = self.generate_variations(primary, combo, 'finance')
                test_suite.extend(variations[:num_variations//4])

        return test_suite
```

---

## 📊 **Performance Benchmark Suite**

### **Benchmark Metrics**

1. **Intent Detection Accuracy** - % of correctly identified intents
2. **Processing Speed** - Time taken to parse intents
3. **Complexity Handling** - Success rate by complexity level
4. **Natural Language Understanding** - Success with varied phrasing

### **Implementation**

```python
class IntentBenchmarkSuite:
    """Performance benchmarking for intent detection"""

    def __init__(self):
        self.results = {
            'accuracy_by_complexity': {'low': [], 'medium': [], 'high': [], 'very_high': []},
            'processing_times': [],
            'intent_accuracy': {'primary': [], 'secondary': [], 'contextual': []},
            'natural_language_success': []
        }

    def run_benchmark(self, skill_config, test_cases):
        """Run complete benchmark suite"""

        print("🚀 Starting Intent Detection Benchmark")
        print(f"Test cases: {len(test_cases)}")

        for i, test_case in enumerate(test_cases):
            query = test_case['query']
            expected = test_case['expected_intents']
            complexity = test_case['complexity']

            # Measure processing time
            start_time = time.time()

            # Parse intents (using simplified implementation)
            detected = self.parse_intents(query, skill_config)

            end_time = time.time()
            processing_time = end_time - start_time

            # Calculate accuracy
            primary_correct = detected['primary_intent'] == expected['primary']
            secondary_correct = set(detected.get('secondary_intents', [])) == set(expected['secondary'])
            contextual_correct = set(detected.get('contextual_intents', [])) == set(expected['contextual'])

            overall_accuracy = primary_correct and secondary_correct and contextual_correct

            # Store results
            self.results['accuracy_by_complexity'][complexity].append(overall_accuracy)
            self.results['processing_times'].append(processing_time)
            self.results['intent_accuracy']['primary'].append(primary_correct)
            self.results['intent_accuracy']['secondary'].append(secondary_correct)
            self.results['intent_accuracy']['contextual'].append(contextual_correct)

            # Check if natural language (non-obvious phrasing)
            is_natural_language = self.is_natural_language(query, expected)
            if is_natural_language:
                self.results['natural_language_success'].append(overall_accuracy)

            # Progress indicator
            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{len(test_cases)} test cases...")

        return self.generate_benchmark_report()

    def parse_intents(self, query, skill_config):
        """Simplified intent parsing for benchmarking"""

        # This would use the actual intent parsing implementation
        # For now, simplified version for demonstration

        query_lower = query.lower()

        # Primary intent detection
        primary_patterns = {
            'analyze': ['analyze', 'examine', 'evaluate', 'study'],
            'create': ['create', 'build', 'make', 'generate'],
            'compare': ['compare', 'versus', 'vs', 'ranking'],
            'monitor': ['monitor', 'track', 'watch', 'alert']
        }

        primary_intent = None
        for intent, keywords in primary_patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                primary_intent = intent
                break

        # Secondary intent detection
        secondary_patterns = {
            'and_visualize': ['show', 'chart', 'graph', 'visualize'],
            'and_save': ['save', 'export', 'download', 'store'],
            'and_explain': ['explain', 'clarify', 'describe', 'detail']
        }

        secondary_intents = []
        for intent, keywords in secondary_patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                secondary_intents.append(intent)

        return {
            'primary_intent': primary_intent,
            'secondary_intents': secondary_intents,
            'contextual_intents': [],
            'confidence': 0.8 if primary_intent else 0.0
        }

    def is_natural_language(self, query, expected_intents):
        """Check if query uses natural language vs. direct commands"""

        natural_indicators = [
            'i need to', 'can you', 'help me', 'please', 'would like',
            'interested in', 'thinking about', 'wondering if'
        ]

        direct_indicators = [
            'analyze', 'create', 'compare', 'monitor',
            'show', 'save', 'explain'
        ]

        query_lower = query.lower()

        natural_score = sum(1 for indicator in natural_indicators if indicator in query_lower)
        direct_score = sum(1 for indicator in direct_indicators if indicator in query_lower)

        return natural_score > direct_score

    def generate_benchmark_report(self):
        """Generate comprehensive benchmark report"""

        total_tests = sum(len(accuracies) for accuracies in self.results['accuracy_by_complexity'].values())

        if total_tests == 0:
            return "No test results available"

        # Calculate accuracy by complexity
        accuracy_by_complexity = {}
        for complexity, accuracies in self.results['accuracy_by_complexity'].items():
            if accuracies:
                accuracy_by_complexity[complexity] = sum(accuracies) / len(accuracies)
            else:
                accuracy_by_complexity[complexity] = 0.0

        # Calculate overall metrics
        avg_processing_time = sum(self.results['processing_times']) / len(self.results['processing_times'])
        primary_intent_accuracy = sum(self.results['intent_accuracy']['primary']) / len(self.results['intent_accuracy']['primary'])
        secondary_intent_accuracy = sum(self.results['intent_accuracy']['secondary']) / len(self.results['intent_accuracy']['secondary'])

        # Calculate natural language success rate
        nl_success_rate = 0.0
        if self.results['natural_language_success']:
            nl_success_rate = sum(self.results['natural_language_success']) / len(self.results['natural_language_success'])

        report = f"""
Intent Detection Benchmark Report
=================================

Overall Performance:
- Total Tests: {total_tests}
- Average Processing Time: {avg_processing_time:.3f}s

Accuracy by Complexity:
"""
        for complexity, accuracy in accuracy_by_complexity.items():
            test_count = len(self.results['accuracy_by_complexity'][complexity])
            report += f"- {complexity.capitalize()}: {accuracy:.1%} ({test_count} tests)\n"

        report += f"""
Intent Detection Accuracy:
- Primary Intent: {primary_intent_accuracy:.1%}
- Secondary Intent: {secondary_intent_accuracy:.1%}
- Natural Language Queries: {nl_success_rate:.1%}

Performance Assessment:
"""

        # Performance assessment
        overall_accuracy = sum(accuracy_by_complexity.values()) / len(accuracy_by_complexity)

        if overall_accuracy >= 0.95:
            report += "✅ EXCELLENT - Intent detection performance is outstanding\n"
        elif overall_accuracy >= 0.85:
            report += "✅ GOOD - Intent detection performance is solid\n"
        elif overall_accuracy >= 0.70:
            report += "⚠️ ACCEPTABLE - Intent detection needs some improvement\n"
        else:
            report += "❌ NEEDS IMPROVEMENT - Intent detection requires significant work\n"

        if avg_processing_time <= 0.1:
            report += "✅ Processing speed is excellent\n"
        elif avg_processing_time <= 0.2:
            report += "✅ Processing speed is good\n"
        else:
            report += "⚠️ Processing speed could be improved\n"

        return report
```

---

## ✅ **Usage Examples**

### **Example 1: Basic Intent Analysis**

```bash
# Test single intent
./intent-parser-validator.sh ./marketplace.json "Analyze AAPL stock"

# Test multiple intents
./intent-parser-validator.sh ./marketplace.json "Analyze AAPL stock and show me a chart"

# Batch testing
echo -e "Analyze AAPL stock\nCompare MSFT vs GOOGL\nMonitor my portfolio" > queries.txt
./intent-parser-validator.sh ./marketplace.json --batch queries.txt
```

### **Example 2: Natural Language Generation**

```python
# Generate test variations
simulator = NaturalLanguageIntentSimulator()
variations = simulator.generate_variations('analyze', ['and_visualize'], 'finance')

for variation in variations[:5]:
    print(f"Query: {variation['query']}")
    print(f"Expected: {variation['expected_intents']}")
    print()
```

### **Example 3: Performance Benchmarking**

```python
# Generate test suite
simulator = NaturalLanguageIntentSimulator()
test_suite = simulator.generate_test_suite(skill_config, num_variations=20)

# Run benchmarks
benchmark = IntentBenchmarkSuite()
report = benchmark.run_benchmark(skill_config, test_suite)
print(report)
```

---

**Version:** 1.0
**Last Updated:** 2025-10-24
**Maintained By:** Agent-Skill-Creator Team