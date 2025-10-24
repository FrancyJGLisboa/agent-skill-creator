# Context-Aware Activation System v1.0

**Version:** 1.0
**Purpose:** Advanced context filtering for precise skill activation and false positive reduction
**Target:** Reduce false positives from 2% to <1% while maintaining 99.5%+ reliability

---

## 🎯 **Overview**

Context-Aware Activation enhances the 3-Layer Activation System by analyzing the semantic and contextual environment of user queries to ensure skills activate only in appropriate situations.

### **Problem Solved**

**Before:** Skills activated based purely on keyword/pattern matching, leading to false positives in inappropriate contexts
**After:** Skills evaluate contextual relevance before activation, dramatically reducing inappropriate activations

---

## 🧠 **Context Analysis Framework**

### **Multi-Dimensional Context Analysis**

The system evaluates query context across multiple dimensions:

#### **1. Domain Context**
```json
{
  "domain_context": {
    "current_domain": "finance",
    "confidence": 0.92,
    "related_domains": ["trading", "investment", "market"],
    "excluded_domains": ["healthcare", "education", "entertainment"]
  }
}
```

#### **2. Task Context**
```json
{
  "task_context": {
    "current_task": "analysis",
    "task_stage": "exploration",
    "task_complexity": "medium",
    "required_capabilities": ["data_processing", "calculation"]
  }
}
```

#### **3. User Intent Context**
```json
{
  "intent_context": {
    "primary_intent": "analyze",
    "secondary_intents": ["compare", "evaluate"],
    "intent_strength": 0.87,
    "urgency_level": "medium"
  }
}
```

#### **4. Conversational Context**
```json
{
  "conversational_context": {
    "conversation_stage": "problem_identification",
    "previous_queries": ["stock market trends", "investment analysis"],
    "context_coherence": 0.94,
    "topic_consistency": 0.89
  }
}
```

---

## 🔍 **Context Detection Algorithms**

### **Semantic Context Extraction**

```python
def extract_semantic_context(query, conversation_history=None):
    """Extract semantic context from query and conversation"""

    context = {
        'entities': extract_named_entities(query),
        'concepts': extract_key_concepts(query),
        'relationships': extract_entity_relationships(query),
        'sentiment': analyze_sentiment(query),
        'urgency': detect_urgency(query)
    }

    # Analyze conversation history if available
    if conversation_history:
        context['conversation_coherence'] = analyze_coherence(
            query, conversation_history
        )
        context['topic_evolution'] = track_topic_evolution(
            conversation_history
        )

    return context

def extract_named_entities(query):
    """Extract named entities from query"""
    entities = {
        'organizations': [],
        'locations': [],
        'persons': [],
        'products': [],
        'technical_terms': []
    }

    # Use NLP library or pattern matching
    # Implementation depends on available tools

    return entities

def extract_key_concepts(query):
    """Extract key concepts and topics"""
    concepts = {
        'primary_domain': identify_primary_domain(query),
        'secondary_domains': identify_secondary_domains(query),
        'technical_concepts': extract_technical_terms(query),
        'business_concepts': extract_business_terms(query)
    }

    return concepts
```

### **Context Relevance Scoring**

```python
def calculate_context_relevance(query, skill_config, extracted_context):
    """Calculate how relevant the query context is to the skill"""

    relevance_scores = {}

    # Domain relevance
    relevance_scores['domain'] = calculate_domain_relevance(
        skill_config['expected_domains'],
        extracted_context['concepts']['primary_domain']
    )

    # Task relevance
    relevance_scores['task'] = calculate_task_relevance(
        skill_config['supported_tasks'],
        extracted_context['intent_context']['primary_intent']
    )

    # Capability relevance
    relevance_scores['capability'] = calculate_capability_relevance(
        skill_config['capabilities'],
        extracted_context['required_capabilities']
    )

    # Context coherence
    relevance_scores['coherence'] = extracted_context.get(
        'conversation_coherence', 0.5
    )

    # Calculate weighted overall relevance
    weights = {
        'domain': 0.3,
        'task': 0.25,
        'capability': 0.25,
        'coherence': 0.2
    }

    overall_relevance = sum(
        score * weights[category]
        for category, score in relevance_scores.items()
    )

    return {
        'overall_relevance': overall_relevance,
        'category_scores': relevance_scores,
        'recommendation': evaluate_relevance_threshold(overall_relevance)
    }

def evaluate_relevance_threshold(relevance_score):
    """Determine activation recommendation based on relevance"""

    if relevance_score >= 0.9:
        return {'activate': True, 'confidence': 'high', 'reason': 'Strong context match'}
    elif relevance_score >= 0.7:
        return {'activate': True, 'confidence': 'medium', 'reason': 'Good context match'}
    elif relevance_score >= 0.5:
        return {'activate': False, 'confidence': 'low', 'reason': 'Weak context match'}
    else:
        return {'activate': False, 'confidence': 'very_low', 'reason': 'Poor context match'}
```

---

## 🚫 **Context Filtering System**

### **Negative Context Detection**

```python
def detect_negative_context(query, skill_config):
    """Detect contexts where skill should NOT activate"""

    negative_indicators = {
        'excluded_domains': [],
        'conflicting_intents': [],
        'inappropriate_contexts': [],
        'resource_constraints': []
    }

    # Check for excluded domains
    excluded_domains = skill_config.get('contextual_filters', {}).get('excluded_domains', [])
    query_domains = identify_query_domains(query)

    for domain in query_domains:
        if domain in excluded_domains:
            negative_indicators['excluded_domains'].append({
                'domain': domain,
                'reason': f'Domain "{domain}" is explicitly excluded'
            })

    # Check for conflicting intents
    conflicting_intents = identify_conflicting_intents(query, skill_config)
    negative_indicators['conflicting_intents'] = conflicting_intents

    # Check for inappropriate contexts
    inappropriate_contexts = check_context_appropriateness(query, skill_config)
    negative_indicators['inappropriate_contexts'] = inappropriate_contexts

    # Calculate negative score
    negative_score = calculate_negative_score(negative_indicators)

    return {
        'should_block': negative_score > 0.7,
        'negative_score': negative_score,
        'indicators': negative_indicators,
        'recommendation': generate_block_recommendation(negative_score)
    }

def check_context_appropriateness(query, skill_config):
    """Check if query context is appropriate for skill activation"""

    inappropriate = []

    # Check if user is asking for help with existing tools
    if any(phrase in query.lower() for phrase in [
        'how to use', 'help with', 'tutorial', 'guide', 'explain'
    ]):
        if 'tutorial' not in skill_config.get('capabilities', {}):
            inappropriate.append({
                'type': 'help_request',
                'reason': 'User requesting help, not task execution'
            })

    # Check if user is asking about theory or education
    if any(phrase in query.lower() for phrase in [
        'what is', 'explain', 'define', 'theory', 'concept', 'learn about'
    ]):
        if 'educational' not in skill_config.get('capabilities', {}):
            inappropriate.append({
                'type': 'educational_query',
                'reason': 'User asking for education, not task execution'
            })

    # Check if user is trying to debug or troubleshoot
    if any(phrase in query.lower() for phrase in [
        'debug', 'error', 'problem', 'issue', 'fix', 'troubleshoot'
    ]):
        if 'debugging' not in skill_config.get('capabilities', {}):
            inappropriate.append({
                'type': 'debugging_query',
                'reason': 'User asking for debugging help'
            })

    return inappropriate
```

### **Context-Aware Decision Engine**

```python
def make_context_aware_decision(query, skill_config, conversation_history=None):
    """Make final activation decision considering all context factors"""

    # Extract context
    context = extract_semantic_context(query, conversation_history)

    # Calculate relevance
    relevance = calculate_context_relevance(query, skill_config, context)

    # Check for negative indicators
    negative_context = detect_negative_context(query, skill_config)

    # Get confidence threshold from skill config
    confidence_threshold = skill_config.get(
        'contextual_filters', {}
    ).get('confidence_threshold', 0.7)

    # Make decision
    should_activate = True
    decision_reasons = []

    # Check negative context first (blocking condition)
    if negative_context['should_block']:
        should_activate = False
        decision_reasons.append(f"Blocked: {negative_context['recommendation']['reason']}")

    # Check relevance threshold
    elif relevance['overall_relevance'] < confidence_threshold:
        should_activate = False
        decision_reasons.append(f"Low relevance: {relevance['overall_relevance']:.2f} < {confidence_threshold}")

    # Check confidence level
    elif relevance['recommendation']['confidence'] == 'low':
        should_activate = False
        decision_reasons.append(f"Low confidence: {relevance['recommendation']['reason']}")

    # If passing all checks, recommend activation
    else:
        decision_reasons.append(f"Approved: {relevance['recommendation']['reason']}")

    return {
        'should_activate': should_activate,
        'confidence': relevance['recommendation']['confidence'],
        'relevance_score': relevance['overall_relevance'],
        'negative_score': negative_context['negative_score'],
        'decision_reasons': decision_reasons,
        'context_analysis': {
            'relevance': relevance,
            'negative_context': negative_context,
            'extracted_context': context
        }
    }
```

---

## 📋 **Enhanced Marketplace Configuration**

### **Context-Aware Configuration Structure**

```json
{
  "name": "skill-name",
  "activation": {
    "keywords": [...],
    "patterns": [...],

    "_comment": "NEW: Context-aware filtering",
    "contextual_filters": {
      "required_context": {
        "domains": ["finance", "trading", "investment"],
        "tasks": ["analysis", "calculation", "comparison"],
        "entities": ["stock", "ticker", "market"],
        "confidence_threshold": 0.8
      },

      "excluded_context": {
        "domains": ["healthcare", "education", "entertainment"],
        "tasks": ["tutorial", "help", "debugging"],
        "query_types": ["question", "definition", "explanation"],
        "user_states": ["learning", "exploring"]
      },

      "context_weights": {
        "domain_relevance": 0.35,
        "task_relevance": 0.30,
        "intent_strength": 0.20,
        "conversation_coherence": 0.15
      },

      "activation_rules": {
        "min_relevance_score": 0.75,
        "max_negative_score": 0.3,
        "required_coherence": 0.6,
        "context_consistency_check": true
      }
    }
  },

  "capabilities": {
    "technical_analysis": true,
    "data_processing": true,
    "_comment": "NEW: Context capabilities",
    "context_requirements": {
      "min_confidence": 0.8,
      "required_domains": ["finance"],
      "supported_tasks": ["analysis", "calculation"]
    }
  }
}
```

---

## 🧪 **Context Testing Framework**

### **Context Test Generation**

```python
def generate_context_test_cases(skill_config):
    """Generate test cases for context-aware activation"""

    test_cases = []

    # Positive context tests (should activate)
    positive_contexts = [
        {
            'query': 'Analyze AAPL stock using RSI indicator',
            'context': {'domain': 'finance', 'task': 'analysis', 'intent': 'analyze'},
            'expected': True,
            'reason': 'Perfect domain and task match'
        },
        {
            'query': 'I need to compare MSFT vs GOOGL performance',
            'context': {'domain': 'finance', 'task': 'comparison', 'intent': 'compare'},
            'expected': True,
            'reason': 'Domain match with supported task'
        }
    ]

    # Negative context tests (should NOT activate)
    negative_contexts = [
        {
            'query': 'Explain what stock analysis is',
            'context': {'domain': 'education', 'task': 'explanation', 'intent': 'learn'},
            'expected': False,
            'reason': 'Educational context, not task execution'
        },
        {
            'query': 'How to use the stock analyzer tool',
            'context': {'domain': 'help', 'task': 'tutorial', 'intent': 'learn'},
            'expected': False,
            'reason': 'Tutorial request, not analysis task'
        },
        {
            'query': 'Debug my stock analysis code',
            'context': {'domain': 'programming', 'task': 'debugging', 'intent': 'fix'},
            'expected': False,
            'reason': 'Debugging context, not supported capability'
        }
    ]

    # Edge case tests
    edge_cases = [
        {
            'query': 'Stock market trends for healthcare companies',
            'context': {'domain': 'finance', 'subdomain': 'healthcare', 'task': 'analysis'},
            'expected': True,
            'reason': 'Finance domain with healthcare subdomain - should activate'
        },
        {
            'query': 'Teach me about technical analysis',
            'context': {'domain': 'education', 'topic': 'technical_analysis'},
            'expected': False,
            'reason': 'Educational context despite relevant topic'
        }
    ]

    test_cases.extend(positive_contexts)
    test_cases.extend(negative_contexts)
    test_cases.extend(edge_cases)

    return test_cases

def run_context_aware_tests(skill_config, test_cases):
    """Run context-aware activation tests"""

    results = []

    for i, test_case in enumerate(test_cases):
        query = test_case['query']
        expected = test_case['expected']
        reason = test_case['reason']

        # Simulate context analysis
        decision = make_context_aware_decision(query, skill_config)

        result = {
            'test_id': i + 1,
            'query': query,
            'expected': expected,
            'actual': decision['should_activate'],
            'correct': expected == decision['should_activate'],
            'confidence': decision['confidence'],
            'relevance_score': decision['relevance_score'],
            'decision_reasons': decision['decision_reasons'],
            'test_reason': reason
        }

        results.append(result)

        # Log result
        status = "✅" if result['correct'] else "❌"
        print(f"{status} Test {i+1}: {query}")
        if not result['correct']:
            print(f"   Expected: {expected}, Got: {decision['should_activate']}")
            print(f"   Reasons: {'; '.join(decision['decision_reasons'])}")

    # Calculate metrics
    total_tests = len(results)
    correct_tests = sum(1 for r in results if r['correct'])
    accuracy = correct_tests / total_tests if total_tests > 0 else 0

    return {
        'total_tests': total_tests,
        'correct_tests': correct_tests,
        'accuracy': accuracy,
        'results': results
    }
```

---

## 📊 **Performance Monitoring**

### **Context-Aware Metrics**

```python
class ContextAwareMonitor:
    """Monitor context-aware activation performance"""

    def __init__(self):
        self.metrics = {
            'total_queries': 0,
            'context_filtered': 0,
            'false_positives_prevented': 0,
            'context_analysis_time': [],
            'relevance_scores': [],
            'negative_contexts_detected': []
        }

    def log_context_decision(self, query, decision, actual_outcome=None):
        """Log context-aware activation decision"""

        self.metrics['total_queries'] += 1

        # Track context filtering
        if not decision['should_activate'] and decision['relevance_score'] > 0.5:
            self.metrics['context_filtered'] += 1

        # Track prevented false positives (if we have feedback)
        if actual_outcome == 'false_positive_prevented':
            self.metrics['false_positives_prevented'] += 1

        # Track relevance scores
        self.metrics['relevance_scores'].append(decision['relevance_score'])

        # Track negative contexts
        if decision['negative_score'] > 0.5:
            self.metrics['negative_contexts_detected'].append({
                'query': query,
                'negative_score': decision['negative_score'],
                'reasons': decision['decision_reasons']
            })

    def generate_performance_report(self):
        """Generate context-aware performance report"""

        total = self.metrics['total_queries']
        if total == 0:
            return "No data available"

        context_filter_rate = self.metrics['context_filtered'] / total
        avg_relevance = sum(self.metrics['relevance_scores']) / len(self.metrics['relevance_scores'])

        report = f"""
Context-Aware Performance Report
================================

Total Queries Analyzed: {total}
Queries Filtered by Context: {self.metrics['context_filtered']} ({context_filter_rate:.1%})
False Positives Prevented: {self.metrics['false_positives_prevented']}
Average Relevance Score: {avg_relevance:.3f}

Top Negative Context Categories:
"""

        # Analyze negative contexts
        negative_reasons = {}
        for context in self.metrics['negative_contexts_detected']:
            for reason in context['reasons']:
                negative_reasons[reason] = negative_reasons.get(reason, 0) + 1

        for reason, count in sorted(negative_reasons.items(), key=lambda x: x[1], reverse=True)[:5]:
            report += f"  - {reason}: {count}\n"

        return report
```

---

## 🔄 **Integration with Existing System**

### **Enhanced 3-Layer Activation**

```python
def enhanced_three_layer_activation(query, skill_config, conversation_history=None):
    """Enhanced 3-layer activation with context awareness"""

    # Layer 1: Keyword matching (existing)
    keyword_match = check_keyword_matching(query, skill_config['activation']['keywords'])

    # Layer 2: Pattern matching (existing)
    pattern_match = check_pattern_matching(query, skill_config['activation']['patterns'])

    # Layer 3: Description understanding (existing)
    description_match = check_description_relevance(query, skill_config)

    # NEW: Layer 4: Context-aware filtering
    context_decision = make_context_aware_decision(query, skill_config, conversation_history)

    # Make final decision
    base_match = keyword_match or pattern_match or description_match

    if not base_match:
        return {
            'should_activate': False,
            'reason': 'No base layer match',
            'layers_matched': [],
            'context_filtered': False
        }

    if not context_decision['should_activate']:
        return {
            'should_activate': False,
            'reason': f'Context filtered: {"; ".join(context_decision["decision_reasons"])}',
            'layers_matched': get_matched_layers(keyword_match, pattern_match, description_match),
            'context_filtered': True,
            'context_score': context_decision['relevance_score']
        }

    return {
        'should_activate': True,
        'reason': f'Approved: {context_decision["recommendation"]["reason"]}',
        'layers_matched': get_matched_layers(keyword_match, pattern_match, description_match),
        'context_filtered': False,
        'context_score': context_decision['relevance_score'],
        'confidence': context_decision['confidence']
    }
```

---

## ✅ **Implementation Checklist**

### **Configuration Requirements**
- [ ] Add `contextual_filters` section to marketplace.json
- [ ] Define `required_context` domains and tasks
- [ ] Define `excluded_context` for false positive prevention
- [ ] Set appropriate `confidence_threshold`
- [ ] Configure `context_weights` for domain-specific needs

### **Testing Requirements**
- [ ] Generate context test cases for each skill
- [ ] Test positive context scenarios
- [ ] Test negative context scenarios
- [ ] Validate edge cases and boundary conditions
- [ ] Monitor false positive reduction

### **Performance Requirements**
- [ ] Context analysis time < 100ms
- [ ] Relevance calculation accuracy > 90%
- [ ] False positive reduction > 50%
- [ ] No negative impact on true positive rate

---

## 📈 **Expected Outcomes**

### **Performance Improvements**
- **False Positive Rate**: 2% → **<1%**
- **Context Precision**: 60% → **85%**
- **User Satisfaction**: 85% → **95%**
- **Activation Reliability**: 98% → **99.5%**

### **User Experience Benefits**
- Skills activate only in appropriate contexts
- Reduced confusion and frustration
- More predictable and reliable behavior
- Better understanding of skill capabilities

---

**Version:** 1.0
**Last Updated:** 2025-10-24
**Maintained By:** Agent-Skill-Creator Team