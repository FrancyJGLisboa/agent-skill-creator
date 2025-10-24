# Analysis Methodology Reference

## Content Analysis Pipeline

1. **Text Combination**: Aggregate all text from sections, headings, and code context
2. **Tokenization**: Split into sentences and words
3. **Pattern Matching**: Apply regex patterns for algorithms, architectures
4. **Domain Classification**: Score content against domain vocabularies
5. **Complexity Assessment**: Evaluate based on length, technical terms, structure

## Domain Classification

### Methodology
- **Keyword Frequency**: Count occurrences of domain-specific terms
- **TF-IDF Scoring**: Weight terms by importance
- **Threshold**: Minimum 3 keyword matches for confident classification
- **Default**: "general_programming" if no strong match

### Domain Vocabularies
Each domain has 10-15 characteristic keywords that indicate its presence.

## Algorithm Detection

### Multi-Strategy Approach

1. **Explicit Detection**
   - Look for "Algorithm X:" patterns
   - Find numbered procedural steps
   - Extract complexity notation (O(...))

2. **Pseudocode Recognition**
   - Detect keywords: BEGIN, END, FOR, WHILE, IF
   - Identify indented structure
   - Check for procedural language

3. **Code Analysis**
   - Count control flow structures (loops, conditionals)
   - Identify function definitions
   - Look for mathematical operations

## Architecture Detection

### Pattern Matching
- Maintain database of known patterns
- Search for pattern names in text
- Extract surrounding context

### Relationship Extraction
- Identify verbs connecting components: "uses", "calls", "extends"
- Map component interactions
- Build dependency graph

## Complexity Assessment

### Scoring Factors
- **Content Length**: >10,000 chars = +2, >5,000 = +1
- **Section Count**: >10 sections = +2, >5 = +1
- **Code Blocks**: >5 blocks = +2, >2 = +1
- **Technical Terms**: +1 for each of: algorithm, optimization, architecture, distributed, concurrent

### Classification
- Score >= 6: Complex
- Score >= 3: Moderate
- Score < 3: Simple

## Confidence Calculation

### Base Confidence
Start at 0.5 (50%)

### Adjustments
- +0.2 if algorithms detected
- +0.1 if architectures detected
- +0.2 if domain classified (not general)
- Cap at 1.0 (100%)

### Interpretation
- > 0.7: High confidence
- 0.5-0.7: Medium confidence
- < 0.5: Low confidence
