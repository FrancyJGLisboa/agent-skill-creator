# Claude LLM Protocols Guide: Complete Skill Creation System

**Version:** 1.0
**Purpose:** Comprehensive guide for Claude LLM to follow during skill creation via Agent-Skill-Creator
**Target:** Ensure consistent, high-quality skill creation following all defined protocols

---

## 🎯 **Overview**

This guide defines the complete set of protocols that Claude LLM must follow when creating skills through the Agent-Skill-Creator system. The protocols ensure autonomy, quality, and consistency while integrating advanced capabilities like context-aware activation and multi-intent detection.

### **Protocol Hierarchy**

```
Autonomous Creation Protocol (Master Protocol)
├── Phase 1: Discovery Protocol
├── Phase 2: Design Protocol
├── Phase 3: Architecture Protocol
├── Phase 4: Detection Protocol (Enhanced with Fase 1)
├── Phase 5: Implementation Protocol
├── Phase 6: Testing Protocol
└── AgentDB Learning Protocol
```

---

## 🤖 **Autonomous Creation Protocol (Master Protocol)**

### **When to Apply**
Always. This is the master protocol that governs all skill creation activities.

### **Core Principles**

#### **🔓 Autonomy Rules**
- ✅ **Claude DECIDES** which API to use (doesn't ask user)
- ✅ **Claude DEFINES** which analyses to perform (based on value)
- ✅ **Claude STRUCTURES** optimally (best practices)
- ✅ **Claude IMPLEMENTS** complete code (no placeholders)
- ✅ **Claude LEARNS** from experience (AgentDB integration)

#### **⭐ Quality Standards**
- ✅ Production-ready code (no TODOs)
- ✅ Useful documentation (not "see docs")
- ✅ Real configs (no placeholders)
- ✅ Robust error handling
- ✅ Intelligence validated with mathematical proofs

#### **📦 Completeness Requirements**
- ✅ Complete SKILL.md (5000+ words)
- ✅ Functional scripts (1000+ lines total)
- ✅ References with content (3000+ words)
- ✅ Valid assets/configs
- ✅ README with instructions

### **Decision-Making Authority**

```python
# Claude has full authority to decide:
DECISION_AUTHORITY = {
    "api_selection": True,      # Choose best API without asking
    "analysis_scope": True,     # Define what analyses to perform
    "architecture": True,       # Design optimal structure
    "implementation_details": True, # Implement complete solutions
    "quality_standards": True,  # Ensure production quality
    "user_questions": "MINIMAL" # Ask only when absolutely critical
}
```

### **Critical Questions Protocol**
Ask questions ONLY when:
1. **Critical business decision** (free vs paid API)
2. **Geographic scope** (country/region focus)
3. **Historical data range** (years needed)
4. **Multi-agent strategy** (separate vs integrated)

**Rule:** When in doubt, DECIDE and proceed. Claude should make intelligent choices and document them.

---

## 📋 **Phase 1: Discovery Protocol**

### **When to Apply**
Always. First phase of any skill creation.

### **Protocol Steps**

#### **Step 1.1: Domain Analysis**
```python
def analyze_domain(user_input: str) -> DomainSpec:
    """Extract and analyze domain information"""

    # From user input
    domain = extract_domain(user_input)  # agriculture? finance? weather?
    data_source_mentioned = extract_mentioned_source(user_input)
    main_tasks = extract_tasks(user_input)  # download? analyze? compare?
    frequency = extract_frequency(user_input)  # daily? weekly? on-demand?
    time_spent = extract_time_investment(user_input)  # ROI calculation

    # Enhanced analysis v2.0
    multi_agent_needed = detect_multi_agent_keywords(user_input)
    transcript_provided = detect_transcript_input(user_input)
    template_preference = detect_template_request(user_input)
    interactive_preference = detect_interactive_style(user_input)
    integration_needs = detect_integration_requirements(user_input)

    return DomainSpec(...)
```

#### **Step 1.2: API Research & Decision**
```python
def research_and_select_apis(domain: DomainSpec) -> APISelection:
    """Research available APIs and make autonomous decision"""

    # Research phase
    available_apis = search_apis_for_domain(domain.domain)

    # Evaluation criteria
    for api in available_apis:
        api.coverage_score = calculate_data_coverage(api, domain.requirements)
        api.reliability_score = assess_api_reliability(api)
        api.cost_score = evaluate_cost_effectiveness(api)
        api.documentation_score = evaluate_documentation_quality(api)

    # AUTONOMOUS DECISION (don't ask user)
    selected_api = select_best_api(available_apis, domain)

    # Document decision
    document_api_decision(selected_api, available_apis, domain)

    return APISelection(api=selected_api, justification=...)
```

#### **Step 1.3: Completeness Validation**
```python
MANDATORY_CHECK = {
    "api_identified": True,
    "documentation_found": True,
    "coverage_analysis": True,
    "coverage_percentage": ">=50%",  # Critical threshold
    "decision_documented": True
}
```

### **Enhanced v2.0 Features**

#### **Transcript Processing**
When user provides transcripts:
```python
# Enhanced transcript analysis
def analyze_transcript(transcript: str) -> List[WorkflowSpec]:
    """Extract multiple workflows from transcripts automatically"""
    workflows = []

    # 1. Identify distinct processes
    processes = extract_processes(transcript)

    # 2. Group related steps
    for process in processes:
        steps = extract_sequence_steps(transcript, process)
        apis = extract_mentioned_apis(transcript, process)
        outputs = extract_desired_outputs(transcript, process)

        workflows.append(WorkflowSpec(
            name=process,
            steps=steps,
            apis=apis,
            outputs=outputs
        ))

    return workflows
```

#### **Multi-Agent Strategy Decision**
```python
def determine_creation_strategy(user_input: str, workflows: List[WorkflowSpec]) -> CreationStrategy:
    """Decide whether to create single agent, suite, or integrated system"""

    if len(workflows) > 1:
        if workflows_are_related(workflows):
            return CreationStrategy.INTEGRATED_SUITE
        else:
            return CreationStrategy.MULTI_AGENT_SUITE
    else:
        return CreationStrategy.SINGLE_AGENT
```

---

## 🎨 **Phase 2: Design Protocol**

### **When to Apply**
After API selection is complete.

### **Protocol Steps**

#### **Step 2.1: Use Case Analysis**
```python
def define_use_cases(domain: DomainSpec, api: APISelection) -> UseCaseSpec:
    """Think about use cases and define analyses based on value"""

    # Core analyses (4-6 required)
    core_analyses = [
        f"{domain.lower()}_trend_analysis",
        f"{domain.lower()}_comparative_analysis",
        f"{domain.lower()}_ranking_analysis",
        f"{domain.lower()}_performance_analysis"
    ]

    # Domain-specific analyses
    domain_analyses = generate_domain_specific_analyses(domain, api)

    # Mandatory comprehensive report
    comprehensive_report = f"comprehensive_{domain.lower()}_report"

    return UseCaseSpec(
        core_analyses=core_analyses,
        domain_analyses=domain_analyses,
        comprehensive_report=comprehensive_report
    )
```

#### **Step 2.2: Analysis Methodology**
```python
def define_methodologies(use_cases: UseCaseSpec) -> MethodologySpec:
    """Specify methodologies for each analysis"""

    methodologies = {}

    for analysis in use_cases.all_analyses:
        methodologies[analysis] = {
            "data_requirements": define_data_requirements(analysis),
            "statistical_methods": select_statistical_methods(analysis),
            "visualization_needs": determine_visualization_needs(analysis),
            "output_format": define_output_format(analysis)
        }

    return MethodologySpec(methodologies=methodologies)
```

#### **Step 2.3: Value Proposition**
```python
def calculate_value_proposition(domain: DomainSpec, analyses: UseCaseSpec) -> ValueSpec:
    """Calculate ROI and value proposition"""

    current_manual_time = domain.time_spent_hours * 52  # Annual
    automated_time = 0.5  # Estimated automated time per task
    time_saved_annual = (current_manual_time - automated_time) * 52

    roi_calculation = {
        "time_before": current_manual_time,
        "time_after": automated_time,
        "time_saved": time_saved_annual,
        "value_proposition": f"Save {time_saved_annual:.1f} hours annually"
    }

    return ValueSpec(roi=roi_calculation)
```

---

## 🏗️ **Phase 3: Architecture Protocol**

### **When to Apply**
After design specifications are complete.

### **Protocol Steps**

#### **Step 3.1: Modular Architecture Design**
```python
def design_architecture(use_cases: UseCaseSpec, api: APISelection) -> ArchitectureSpec:
    """Structure optimally following best practices"""

    # MANDATORY structure
    required_structure = {
        "main_scripts": [
            f"{api.name.lower()}_client.py",
            f"{domain.lower()}_analyzer.py",
            f"{domain.lower()}_comparator.py",
            f"comprehensive_{domain.lower()}_report.py"
        ],
        "utils": {
            "helpers.py": "MANDATORY - temporal context and common utilities",
            "validators/": "MANDATORY - 4 validators minimum"
        },
        "tests/": "MANDATORY - comprehensive test suite",
        "references/": "MANDATORY - documentation and guides"
    }

    return ArchitectureSpec(structure=required_structure)
```

#### **Step 3.2: Modular Parser Architecture (MANDATORY)**
```python
# Rule: If API returns N data types → create N specific parsers
def create_modular_parsers(api_data_types: List[str]) -> ParserSpec:
    """Create one parser per data type - MANDATORY"""

    parsers = {}
    for data_type in api_data_types:
        parser_name = f"parse_{data_type.lower()}"
        parsers[parser_name] = {
            "function_signature": f"def {parser_name}(data: dict) -> pd.DataFrame:",
            "validation_rules": generate_validation_rules(data_type),
            "error_handling": create_error_handling(data_type)
        }

    return ParserSpec(parsers=parsers)
```

#### **Step 3.3: Validation System (MANDATORY)**
```python
def create_validation_system(domain: str, data_types: List[str]) -> ValidationSpec:
    """Create comprehensive validation system - MANDATORY"""

    # MANDATORY: 4 validators minimum
    validators = {
        f"validate_{domain.lower()}_data": create_domain_validator(),
        f"validate_{domain.lower()}_entity": create_entity_validator(),
        f"validate_{domain.lower()}_temporal": create_temporal_validator(),
        f"validate_{domain.lower()}_completeness": create_completeness_validator()
    }

    # Additional validators per data type
    for data_type in data_types:
        validators[f"validate_{data_type.lower()}"] = create_type_validator(data_type)

    return ValidationSpec(validators=validators)
```

#### **Step 3.4: Helper Functions (MANDATORY)**
```python
# MANDATORY: utils/helpers.py with temporal context
def create_helpers_module() -> HelperSpec:
    """Create helper functions module - MANDATORY"""

    helpers = {
        # Temporal context functions
        "get_current_year": "lambda: datetime.now().year",
        "get_seasonal_context": "determine_current_season()",
        "get_time_period_description": "generate_time_description()",

        # Common utilities
        "safe_float_conversion": "convert_to_float_safely()",
        "format_currency": "format_as_currency()",
        "calculate_growth_rate": "compute_growth_rate()",
        "handle_missing_data": "process_missing_values()"
    }

    return HelperSpec(functions=helpers)
```

---

## 🎯 **Phase 4: Detection Protocol (Enhanced with Fase 1)**

### **When to Apply**
After architecture is designed.

### **Enhanced 4-Layer Detection System**

```python
def create_detection_system(domain: str, capabilities: List[str]) -> DetectionSpec:
    """Create 4-layer detection with Fase 1 enhancements"""

    # Layer 1: Keywords (Expanded 50-80 keywords)
    keyword_spec = {
        "total_target": "50-80 keywords",
        "categories": {
            "core_capabilities": "10-15 keywords",
            "synonym_variations": "10-15 keywords",
            "direct_variations": "8-12 keywords",
            "domain_specific": "5-8 keywords",
            "natural_language": "5-10 keywords"
        }
    }

    # Layer 2: Patterns (10-15 patterns)
    pattern_spec = {
        "total_target": "10-15 patterns",
        "enhanced_patterns": [
            "data_extraction_patterns",
            "processing_patterns",
            "workflow_automation_patterns",
            "technical_operations_patterns",
            "natural_language_patterns"
        ]
    }

    # Layer 3: Description + NLU
    description_spec = {
        "minimum_length": "300-500 characters",
        "keyword_density": "include 60+ unique keywords",
        "semantic_richness": "comprehensive concept coverage"
    }

    # Layer 4: Context-Aware Filtering (Fase 1 enhancement)
    context_spec = {
        "required_context": {
            "domains": [domain, get_related_domains(domain)],
            "tasks": capabilities,
            "confidence_threshold": 0.8
        },
        "excluded_context": {
            "domains": get_excluded_domains(domain),
            "tasks": ["tutorial", "help", "debugging"],
            "query_types": ["question", "definition"]
        },
        "context_weights": {
            "domain_relevance": 0.35,
            "task_relevance": 0.30,
            "intent_strength": 0.20,
            "conversation_coherence": 0.15
        }
    }

    # Multi-Intent Detection (Fase 1 enhancement)
    intent_spec = {
        "primary_intents": get_primary_intents(domain),
        "secondary_intents": get_secondary_intents(capabilities),
        "contextual_intents": get_contextual_intents(),
        "intent_combinations": generate_supported_combinations()
    }

    return DetectionSpec(
        keywords=keyword_spec,
        patterns=pattern_spec,
        description=description_spec,
        context=context_spec,
        intents=intent_spec
    )
```

### **Keywords Generation Protocol**

```python
def generate_expanded_keywords(domain: str, capabilities: List[str]) -> KeywordSpec:
    """Generate 50-80 expanded keywords using Fase 1 system"""

    # Use synonym expansion system
    base_keywords = generate_base_keywords(domain, capabilities)
    expanded_keywords = expand_with_synonyms(base_keywords, domain)

    # Category organization
    categorized_keywords = {
        "core_capabilities": extract_core_capabilities(expanded_keywords),
        "synonym_variations": extract_synonyms(expanded_keywords),
        "direct_variations": generate_direct_variations(base_keywords),
        "domain_specific": generate_domain_specific(domain),
        "natural_language": generate_natural_variations(base_keywords)
    }

    return KeywordSpec(
        total=len(expanded_keywords),
        categories=categorized_keywords,
        minimum_target=50  # Target: 50-80 keywords
    )
```

### **Pattern Generation Protocol**

```python
def generate_enhanced_patterns(domain: str, keywords: KeywordSpec) -> PatternSpec:
    """Generate 10-15 enhanced patterns using Fase 1 system"""

    # Use activation patterns guide
    base_patterns = generate_base_patterns(domain)
    enhanced_patterns = enhance_patterns_with_synonyms(base_patterns)

    # Pattern categories
    pattern_categories = {
        "data_extraction": create_data_extraction_patterns(domain),
        "processing_workflow": create_processing_patterns(domain),
        "technical_operations": create_technical_patterns(domain),
        "natural_language": create_conversational_patterns(domain)
    }

    return PatternSpec(
        patterns=enhanced_patterns,
        categories=pattern_categories,
        minimum_target=10  # Target: 10-15 patterns
    )
```

---

## ⚙️ **Phase 5: Implementation Protocol**

### **When to Apply**
After detection system is designed.

### **Critical Implementation Order (MANDATORY)**

#### **Step 5.1: Create marketplace.json IMMEDIATELY**
```python
# STEP 0.1: Create basic structure
def create_marketplace_json_first(domain: str, description: str) -> bool:
    """Create marketplace.json BEFORE any other files - MANDATORY"""

    marketplace_template = {
        "name": f"{domain.lower()}-skill-name",
        "owner": {"name": "Agent Creator", "email": "noreply@example.com"},
        "metadata": {
            "description": description,  # Will be synchronized later
            "version": "1.0.0",
            "created": datetime.now().strftime("%Y-%m-%d"),
            "language": "en-US"
        },
        "plugins": [{
            "name": f"{domain.lower()}-plugin",
            "description": description,  # MUST match SKILL.md description
            "source": "./",
            "strict": false,
            "skills": ["./"]
        }],
        "activation": {
            "keywords": [],  # Will be populated in Phase 4
            "patterns": []   # Will be populated in Phase 4
        },
        "capabilities": {},
        "usage": {
            "example": "",
            "when_to_use": [],
            "when_not_to_use": []
        },
        "test_queries": []
    }

    # Create file immediately
    with open('.claude-plugin/marketplace.json', 'w') as f:
        json.dump(marketplace_template, f, indent=2)

    return True
```

#### **Step 5.2: Validate marketplace.json**
```python
def validate_marketplace_json() -> ValidationResult:
    """Validate marketplace.json immediately after creation - MANDATORY"""

    validation_checks = {
        "syntax_valid": validate_json_syntax('.claude-plugin/marketplace.json'),
        "required_fields": check_required_fields('.claude-plugin/marketplace.json'),
        "structure_valid": validate_marketplace_structure('.claude-plugin/marketplace.json')
    }

    if not all(validation_checks.values()):
        raise ValidationError("marketplace.json validation failed - FIX BEFORE CONTINUING")

    return ValidationResult(passed=True, checks=validation_checks)
```

#### **Step 5.3: Create SKILL.md with Frontmatter**
```python
def create_skill_md(domain: str, description: str, detection_spec: DetectionSpec) -> bool:
    """Create SKILL.md with proper frontmatter - MANDATORY"""

    frontmatter = f"""---
name: {domain.lower()}-skill-name
description: {description}
---

# {domain.title()} Skill

[... rest of SKILL.md content ...]
"""

    with open('SKILL.md', 'w') as f:
        f.write(frontmatter)

    return True
```

#### **Step 5.4: CRITICAL Synchronization Check**
```python
def synchronize_descriptions() -> bool:
    """MANDATORY: SKILL.md description MUST EQUAL marketplace.json description"""

    skill_description = extract_frontmatter_description('SKILL.md')
    marketplace_description = extract_marketplace_description('.claude-plugin/marketplace.json')

    if skill_description != marketplace_description:
        # Fix marketplace.json to match SKILL.md
        update_marketplace_description('.claude-plugin/marketplace.json', skill_description)

        print("🔧 FIXED: Synchronized SKILL.md description with marketplace.json")

    return True
```

#### **Step 5.5: Implementation Order (MANDATORY)**
```python
# Implementation sequence
IMPLEMENTATION_ORDER = {
    1: "utils/helpers.py (MANDATORY)",
    2: "utils/validators/ (MANDATORY - 4 validators minimum)",
    3: "Modular parsers (1 per data type - MANDATORY)",
    4: "Main analysis scripts",
    5: "comprehensive_{domain}_report() (MANDATORY)",
    6: "tests/ directory",
    7: "README.md and documentation"
}
```

### **Code Implementation Standards**

#### **No Placeholders Rule**
```python
# ❌ FORBIDDEN - No placeholders or TODOs
def analyze_data(data):
    # TODO: implement analysis
    pass

# ✅ REQUIRED - Complete implementation
def analyze_data(data: pd.DataFrame) -> Dict[str, Any]:
    """Analyze domain data with comprehensive metrics"""

    if data.empty:
        raise ValueError("Data cannot be empty")

    # Complete implementation with error handling
    try:
        analysis_results = {
            "trend_analysis": calculate_trends(data),
            "performance_metrics": calculate_performance(data),
            "statistical_summary": generate_statistics(data)
        }
        return analysis_results
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise AnalysisError(f"Unable to analyze data: {e}")
```

#### **Documentation Standards**
```python
# ✅ REQUIRED: Complete docstrings
def calculate_growth_rate(values: List[float]) -> float:
    """
    Calculate compound annual growth rate (CAGR) for a series of values.

    Args:
        values: List of numeric values in chronological order

    Returns:
        Compound annual growth rate as decimal (0.15 = 15%)

    Raises:
        ValueError: If less than 2 values or contains non-numeric data

    Example:
        >>> calculate_growth_rate([100, 115, 132.25])
        0.15  # 15% CAGR
    """
    # Implementation...
```

---

## 🧪 **Phase 6: Testing Protocol**

### **When to Apply**
After implementation is complete.

### **Mandatory Test Requirements**

#### **Step 6.1: Test Suite Structure**
```python
MANDATORY_TEST_STRUCTURE = {
    "tests/": {
        "test_integration.py": "≥5 end-to-end tests - MANDATORY",
        "test_parse.py": "1 test per parser - MANDATORY",
        "test_analyze.py": "1 test per analysis function - MANDATORY",
        "test_helpers.py": "≥3 tests - MANDATORY",
        "test_validation.py": "≥5 tests - MANDATORY"
    },
    "total_minimum_tests": 25,  # Absolute minimum
    "all_tests_must_pass": True  # No exceptions
}
```

#### **Step 6.2: Integration Tests (MANDATORY)**
```python
def create_integration_tests() -> List[TestSpec]:
    """Create ≥5 end-to-end integration tests - MANDATORY"""

    integration_tests = [
        {
            "name": "test_full_workflow_integration",
            "description": "Test complete workflow from API to report",
            "steps": [
                "test_api_connection",
                "test_data_parsing",
                "test_analysis_execution",
                "test_report_generation"
            ]
        },
        {
            "name": "test_error_handling_integration",
            "description": "Test error handling throughout system",
            "steps": [
                "test_api_failure_handling",
                "test_invalid_data_handling",
                "test_missing_data_handling"
            ]
        }
        # ... 3+ more integration tests
    ]

    return integration_tests
```

#### **Step 6.3: Test Execution & Validation**
```python
def execute_all_tests() -> TestResult:
    """Execute ALL tests and ensure they pass - MANDATORY"""

    test_results = {}

    # Execute each test file
    for test_file in MANDATORY_TEST_STRUCTURE["tests/"]:
        test_results[test_file] = execute_test_file(f"tests/{test_file}")

    # Validate all tests pass
    failed_tests = [test for test, result in test_results.items() if not result.passed]

    if failed_tests:
        raise TestError(f"FAILED TESTS: {failed_tests} - FIX BEFORE DELIVERY")

    print("✅ ALL TESTS PASSED - Ready for delivery")
    return TestResult(passed=True, results=test_results)
```

---

## 🧠 **AgentDB Learning Protocol**

### **When to Apply**
After successful skill creation and testing.

### **Automatic Episode Storage**
```python
def store_creation_episode(user_input: str, creation_result: CreationResult) -> str:
    """Store successful creation episode for future learning - AUTOMATIC"""

    try:
        bridge = get_real_agentdb_bridge()

        episode = Episode(
            session_id=f"agent-creation-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            task=user_input,
            input=f"Domain: {creation_result.domain}, API: {creation_result.api}",
            output=f"Created: {creation_result.agent_name}/ with {creation_result.file_count} files",
            critique=f"Success: {'✅ High quality' if creation_result.all_tests_passed else '⚠️ Needs refinement'}",
            reward=0.9 if creation_result.all_tests_passed else 0.7,
            success=creation_result.all_tests_passed,
            latency_ms=creation_result.creation_time_seconds * 1000,
            tokens_used=creation_result.estimated_tokens,
            tags=[creation_result.domain, creation_result.api, creation_result.architecture_type],
            metadata={
                "agent_name": creation_result.agent_name,
                "domain": creation_result.domain,
                "api": creation_result.api,
                "complexity": creation_result.complexity,
                "files_created": creation_result.file_count,
                "validation_passed": creation_result.all_tests_passed
            }
        )

        episode_id = bridge.store_episode(episode)
        print(f"🧠 Episode stored for learning: #{episode_id}")

        # Create skill if successful
        if creation_result.all_tests_passed and bridge.is_available:
            skill = Skill(
                name=f"{creation_result.domain}_agent_template",
                description=f"Proven template for {creation_result.domain} agents",
                code=f"API: {creation_result.api}, Structure: {creation_result.architecture}",
                success_rate=1.0,
                uses=1,
                avg_reward=0.9,
                metadata={"domain": creation_result.domain, "api": creation_result.api}
            )

            skill_id = bridge.create_skill(skill)
            print(f"🎯 Skill created: #{skill_id}")

        return episode_id

    except Exception as e:
        # AgentDB failure should not break agent creation
        print("🔄 AgentDB learning unavailable - agent creation completed successfully")
        return None
```

### **Learning Progress Integration**
```python
def provide_learning_feedback(episode_count: int, success_rate: float) -> str:
    """Provide subtle feedback about learning progress"""

    if episode_count == 1:
        return "🎉 First agent created successfully!"
    elif episode_count == 10:
        return "⚡ Agent creation optimized based on 10 successful patterns"
    elif episode_count >= 30:
        return "🌟 I've learned your preferences - future creations will be optimized"

    return ""
```

---

## 🚨 **Critical Protocol Violations & Prevention**

### **Common Violations to Avoid**

#### **❌ Forbidden Actions**
```python
FORBIDDEN_ACTIONS = {
    "asking_user_questions": "Except for critical business decisions",
    "creating_placeholders": "No TODOs or pass statements",
    "skipping_validations": "All validations must pass",
    "ignoring_mandatory_structure": "Required files/dirs must be created",
    "poor_documentation": "Must include complete docstrings and comments",
    "failing_tests": "All tests must pass before delivery"
}
```

#### **⚠️ Quality Gates**
```python
QUALITY_GATES = {
    "pre_implementation": [
        "marketplace.json created and validated",
        "SKILL.md created with frontmatter",
        "descriptions synchronized"
    ],
    "post_implementation": [
        "all mandatory files created",
        "no placeholders or TODOs",
        "complete error handling",
        "comprehensive documentation"
    ],
    "pre_delivery": [
        "all tests created (≥25)",
        "all tests pass",
        "marketplace test command successful",
        "AgentDB episode stored"
    ]
}
```

### **Delivery Validation Protocol**
```python
def final_delivery_validation() -> ValidationResult:
    """Final MANDATORY validation before delivery"""

    validation_steps = [
        ("marketplace_syntax", validate_marketplace_syntax),
        ("description_sync", validate_description_synchronization),
        ("import_validation", validate_all_imports),
        ("placeholder_check", check_no_placeholders),
        ("test_execution", execute_all_tests),
        ("marketplace_installation", test_marketplace_installation)
    ]

    results = {}
    for step_name, validation_func in validation_steps:
        try:
            results[step_name] = validation_func()
        except Exception as e:
            results[step_name] = ValidationResult(passed=False, error=str(e))

    failed_steps = [step for step, result in results.items() if not result.passed]

    if failed_steps:
        raise ValidationError(f"DELIVERY BLOCKED - Failed validations: {failed_steps}")

    return ValidationResult(passed=True, validations=results)
```

---

## 📋 **Complete Protocol Checklist**

### **Pre-Creation Validation**
- [ ] User request triggers skill creation protocol
- [ ] Agent-Skill-Cursor activates correctly
- [ ] Initial domain analysis complete

### **Phase 1: Discovery**
- [ ] Domain identified and analyzed
- [ ] API researched and selected (with justification)
- [ ] API completeness analysis completed (≥50% coverage)
- [ ] Multi-agent/transcript analysis if applicable
- [ ] Creation strategy determined

### **Phase 2: Design**
- [ ] Use cases defined (4-6 analyses + comprehensive report)
- [ ] Methodologies specified for each analysis
- [ ] Value proposition and ROI calculated
- [ ] Design decisions documented

### **Phase 3: Architecture**
- [ ] Modular architecture designed
- [ ] Parser architecture planned (1 per data type)
- [ ] Validation system planned (4+ validators)
- [ ] Helper functions specified
- [ ] File structure finalized

### **Phase 4: Detection (Enhanced)**
- [ ] 50-80 keywords generated across 5 categories
- [ ] 10-15 enhanced patterns created
- [ ] Context-aware filters configured
- [ ] Multi-intent detection configured
- [ ] marketplace.json activation section populated

### **Phase 5: Implementation**
- [ ] marketplace.json created FIRST and validated
- [ ] SKILL.md created with synchronized description
- [ ] utils/helpers.py implemented (MANDATORY)
- [ ] utils/validators/ implemented (4+ validators)
- [ ] Modular parsers implemented (1 per data type)
- [ ] Main analysis scripts implemented
- [ ] comprehensive_{domain}_report() implemented (MANDATORY)
- [ ] No placeholders or TODOs anywhere
- [ ] Complete error handling throughout
- [ ] Comprehensive documentation written

### **Phase 6: Testing**
- [ ] tests/ directory created
- [ ] ≥25 tests implemented across all categories
- [ ] ALL tests pass
- [ ] Integration tests successful
- [ ] Marketplace installation test successful

### **Final Delivery**
- [ ] Final validation passed
- [ ] AgentDB episode stored
- [ ] Learning feedback provided if applicable
- [ ] Ready for user delivery

---

## 🎯 **Protocol Success Metrics**

### **Quality Indicators**
- **Activation Reliability**: ≥99.5%
- **False Positive Rate**: <1%
- **Code Coverage**: ≥90%
- **Test Pass Rate**: 100%
- **Documentation Completeness**: 100%
- **User Satisfaction**: ≥95%

### **Learning Indicators**
- **Episodes Stored**: 100% of successful creations
- **Pattern Recognition**: Improves with each creation
- **Decision Quality**: Enhanced by AgentDB learning
- **Template Success Rate**: Tracked and optimized

---

**Version:** 1.0
**Last Updated:** 2025-10-24
**Maintained By:** Agent-Skill-Creator Team