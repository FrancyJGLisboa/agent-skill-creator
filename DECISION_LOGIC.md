# Agent Creator: Decision Logic and Architecture Selection

## 🎯 **Purpose**

This document explains the decision-making process used by the Agent Creator meta-skill to determine the appropriate architecture for Claude Skills.

## 📋 **Decision Framework**

### **Phase 1: Requirements Analysis**

During user input analysis, the Agent Creator evaluates:

#### **Complexity Indicators**
- **Number of distinct objectives**: How many different goals?
- **Workflow complexity**: Linear vs branching vs parallel
- **Data sources**: Single vs multiple API/data sources
- **Output formats**: Simple vs complex report generation
- **Integration needs**: Standalone vs interconnected systems

#### **Domain Complexity Assessment**
- **Single domain** (e.g., PDF processing) → Simple Skill likely
- **Multi-domain** (e.g., finance + reporting + optimization) → Complex Suite likely
- **Specialized expertise required** (technical, financial, legal) → Component separation beneficial

### **Phase 2: Architecture Decision Tree**

```
START: Analyze User Request
    ↓
┌─ Single, clear objective?
│   ├─ Yes → Continue Simple Skill Path
│   └─ No → Continue Complex Suite Path
    ↓
Simple Skill Path:
├─ Single data source?
│   ├─ Yes → Simple Skill confirmed
│   └─ No → Consider Hybrid architecture
├─ Linear workflow?
│   ├─ Yes → Simple Skill confirmed
│   └─ No → Consider breaking into components
└─ <1000 lines estimated code?
    ├─ Yes → Simple Skill confirmed
    └─ No → Recommend Complex Suite

Complex Suite Path:
├─ Multiple related workflows?
│   ├─ Yes → Complex Suite confirmed
│   └─ No → Consider Simple + Extensions
├─ Team maintenance expected?
│   ├─ Yes → Complex Suite confirmed
│   └─ No → Consider advanced Simple Skill
└─ Domain expertise specialization needed?
    ├─ Yes → Complex Suite confirmed
    └─ No → Consider Hybrid approach
```

### **Phase 3: Specific Decision Rules**

#### **Simple Skill Criteria**
✅ **Use Simple Skill when:**
- Single primary objective
- One or two related sub-tasks
- Linear workflow (A → B → C)
- Single domain expertise
- <1000 lines total code expected
- One developer can maintain
- Development time: <2 weeks

**Examples:**
- "Create PDF text extractor"
- "Automate CSV data cleaning"
- "Generate weekly status reports"
- "Convert images to web format"

#### **Complex Skill Suite Criteria**
✅ **Use Complex Suite when:**
- Multiple distinct objectives
- Parallel or branching workflows
- Multiple domain expertise areas
- >2000 lines total code expected
- Team maintenance anticipated
- Development time: >2 weeks
- Component reusability valuable

**Examples:**
- "Complete financial analysis platform"
- "E-commerce automation system"
- "Research workflow automation"
- "Business intelligence suite"

#### **Hybrid Architecture Criteria**
✅ **Use Hybrid when:**
- Core objective with optional extensions
- Configurable component selection
- Main workflow with specialized sub-tasks
- 1000-2000 lines code expected
- Central orchestration important

**Examples:**
- "Document processor with OCR and classification"
- "Data analysis with optional reporting components"
- "API client with multiple integration options"

### **Phase 4: Implementation Decision**

#### **Simple Skill Implementation**
```python
# Decision confirmed: Create Simple Skill
architecture = "simple"
base_name = generate_descriptive_name(requirements)
skill_name = f"{base_name}-cskill"  # Apply naming convention
files_to_create = [
    "SKILL.md",
    "scripts/ (if needed)",
    "references/ (if needed)",
    "assets/ (if needed)"
]
marketplace_json = False  # Single skill doesn't need manifest
```

#### **Complex Suite Implementation**
```python
# Decision confirmed: Create Complex Skill Suite
architecture = "complex_suite"
base_name = generate_descriptive_name(requirements)
suite_name = f"{base_name}-cskill"  # Apply naming convention
components = identify_components(requirements)
component_names = [f"{comp}-cskill" for comp in components]
files_to_create = [
    ".claude-plugin/marketplace.json",
    f"{component}/SKILL.md" for component in component_names,
    "shared/utils/",
    "shared/config/"
]
marketplace_json = True  # Suite needs organization manifest
```

#### **Hybrid Implementation**
```python
# Decision confirmed: Create Hybrid Architecture
architecture = "hybrid"
base_name = generate_descriptive_name(requirements)
skill_name = f"{base_name}-cskill"  # Apply naming convention
main_skill = "primary_skill.md"
optional_components = identify_optional_components(requirements)
component_names = [f"{comp}-cskill" for comp in optional_components]
files_to_create = [
    "SKILL.md",  # Main orchestrator
    "scripts/components/",  # Optional sub-components
    "config/component_selection.json"
]
```

#### **Naming Convention Logic**
```python
def generate_descriptive_name(user_requirements):
    """Generate descriptive base name from user requirements"""
    # Extract key concepts from user input
    concepts = extract_concepts(user_requirements)

    # Create descriptive base name
    if len(concepts) == 1:
        base_name = concepts[0]
    elif len(concepts) <= 3:
        base_name = "-".join(concepts)
    else:
        base_name = "-".join(concepts[:3]) + "-suite"

    # Ensure valid filename format
    base_name = sanitize_filename(base_name)
    return base_name

def apply_cskill_convention(base_name):
    """Apply -cskill naming convention"""
    if not base_name.endswith("-cskill"):
        return f"{base_name}-cskill"
    return base_name

# Examples of naming logic:
# "extract text from PDF" → "pdf-text-extractor-cskill"
# "financial analysis with reporting" → "financial-analysis-suite-cskill"
# "clean CSV data" → "csv-data-cleaner-cskill"
```

## 🎯 **Decision Documentation**

### **DECISIONS.md Template**

Every created skill includes a `DECISIONS.md` file documenting:

```markdown
# Architecture Decisions

## Requirements Analysis
- **Primary Objectives**: [List main goals]
- **Complexity Indicators**: [Number of objectives, workflows, data sources]
- **Domain Assessment**: [Single vs multi-domain]

## Architecture Selection
- **Chosen Architecture**: [Simple Skill / Complex Suite / Hybrid]
- **Key Decision Factors**: [Why this architecture was selected]
- **Alternatives Considered**: [Other options and why rejected]

## Implementation Rationale
- **Component Breakdown**: [How functionality is organized]
- **Integration Strategy**: [How components work together]
- **Maintenance Considerations**: [Long-term maintenance approach]

## Future Evolution
- **Growth Path**: [How to evolve from simple to complex if needed]
- **Extension Points**: [Where functionality can be added]
- **Migration Strategy**: [How to change architectures if requirements change]
```

## 🔄 **Learning and Improvement**

### **Decision Quality Tracking**
The Agent Creator tracks:
- **User satisfaction** with architectural choices
- **Maintenance requirements** for each pattern
- **Evolution patterns** (simple → complex transitions)
- **Success metrics** by architecture type

### **Pattern Recognition**
Over time, the system learns:
- **Common complexity indicators** for specific domains
- **Optimal component boundaries** for multi-domain problems
- **User preference patterns** for different architectures
- **Evolution triggers** that signal need for architecture change

### **Feedback Integration**
User feedback improves future decisions:
- **Architecture mismatch** reports
- **Maintenance difficulty** feedback
- **Feature request patterns**
- **User success stories**

## 📊 **Examples of Decision Logic in Action**

### **Example 1: PDF Text Extractor Request**
**User Input:** "Create a skill to extract text from PDF documents"

**Analysis:**
- Single objective: PDF text extraction ✓
- Linear workflow: PDF → Extract → Clean ✓
- Single domain: Document processing ✓
- Estimated code: ~500 lines ✓
- Single developer maintenance ✓

**Decision:** Simple Skill
**Implementation:** `pdf-extractor/SKILL.md` with optional scripts folder

### **Example 2: Financial Analysis Platform Request**
**User Input:** "Build a complete financial analysis system with data acquisition, technical analysis, portfolio optimization, and reporting"

**Analysis:**
- Multiple objectives: 4 distinct capabilities ✗
- Complex workflows: Data → Analysis → Optimization → Reporting ✗
- Multi-domain: Data engineering, finance, reporting ✗
- Estimated code: ~5000 lines ✗
- Team maintenance likely ✗

**Decision:** Complex Skill Suite
**Implementation:** 4 component skills with marketplace.json

### **Example 3: Document Processor Request**
**User Input:** "Create a document processor that can extract text, classify documents, and optionally generate summaries"

**Analysis:**
- Core objective: Document processing ✓
- Optional components: Classification, summarization ✓
- Configurable workflow: Base + extensions ✓
- Estimated code: ~1500 lines ✓
- Central orchestration important ✓

**Decision:** Hybrid Architecture
**Implementation:** Main skill with optional component scripts

## ✅ **Quality Assurance**

### **Decision Validation**
Before finalizing architecture choice:
1. **Requirements completeness check**
2. **Complexity assessment verification**
3. **Maintenance feasibility analysis**
4. **User communication and confirmation**

### **Architecture Review**
Post-creation validation:
1. **Component boundary effectiveness**
2. **Integration success**
3. **Maintainability assessment**
4. **User satisfaction measurement**

This decision logic ensures that every created skill has the appropriate architecture for its requirements, maximizing effectiveness and minimizing maintenance overhead.