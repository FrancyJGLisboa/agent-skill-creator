---
name: article-to-prototype
description: Extract technical content from articles, papers, tutorials, and documentation to generate functional code prototypes. Use when user says extract from paper, implement from article, create prototype from documentation, convert tutorial to code, or turn paper into implementation. Reads PDFs, web pages, Jupyter notebooks, and markdown, then generates complete projects with tests, dependencies, and documentation in the appropriate language.
---
# Article-to-Prototype Skill

Extract technical content from diverse sources and generate functional prototypes in the most appropriate programming language.

## When to Use

Activate when the user:
- Asks to implement code from a paper, article, blog post, or tutorial
- Wants to extract algorithms from documentation and create working code
- Says "extract from paper", "implement from article", "prototype from docs"
- Provides a PDF, URL, notebook, or markdown file and wants code generated

## Pipeline

```
Input → Format Detection → Content Extraction → Semantic Analysis → Language Selection → Code Generation → Output
```

### Step 1: Format Detection & Extraction

Detect input format and extract structured content:

| Format | Extractor | Key capabilities |
|--------|-----------|-----------------|
| PDF | pdfplumber (fallback: PyPDF2) | Section structure, equations as LaTeX, code blocks via font heuristics |
| Web | trafilatura (fallback: BeautifulSoup) | Main content extraction, code block detection, metadata |
| Notebook | nbformat | Code cells with ordering, imports, outputs, kernel metadata |
| Markdown | mistune | CommonMark/GFM, YAML frontmatter, fenced code blocks |

**Checkpoint**: Verify extraction produced meaningful content (>100 chars of text or at least 1 code block). If extraction fails, try fallback extractor. If both fail, ask user for alternative source.

### Step 2: Semantic Analysis

Analyze extracted content to identify:
- **Algorithms**: Pseudocode, numbered steps, complexity annotations (O(n) notation)
- **Architecture patterns**: Design patterns, system architectures, data flow patterns
- **Dependencies**: Import statements, library mentions, version specifications
- **Domain**: Classify via keyword density (ML, web, systems, data science, scientific, DevOps)

**Checkpoint**: Verify at least one algorithm or architecture pattern was detected. If analysis confidence is low (<0.5), ask user to confirm the domain and intended output before proceeding.

### Step 3: Language Selection

```
Priority 1: Explicit language mention in article → use it
Priority 2: Domain match → ML/data=Python, web=TypeScript, systems=Rust/Go, scientific=Julia/Python
Priority 3: Dependency analysis → score languages by library availability
Default: Python
```

### Step 4: Code Generation

Generate a complete project with:
- **Source code**: Fully implemented functions (no placeholders/TODOs), type hints, error handling, logging
- **Tests**: Unit tests covering core logic, edge cases, and example usage
- **Dependencies**: requirements.txt / package.json / Cargo.toml with pinned versions
- **README**: Installation, usage examples, source attribution linking back to original article
- **Config**: .gitignore, license, environment variable templates

Output structure follows language conventions (e.g., `src/`, `tests/`, `docs/`).

**Checkpoint**: Verify all generated files have valid syntax. Run `python -m py_compile` for Python, `tsc --noEmit` for TypeScript. If syntax errors found, fix and regenerate.

## Quality Checklist

Before outputting any prototype, verify:
- [ ] All functions fully implemented (no TODOs or placeholders)
- [ ] Type annotations present (Python type hints, TypeScript types, etc.)
- [ ] Error handling for all external operations
- [ ] Unit tests with >80% core logic coverage
- [ ] README with installation, usage, and source attribution
- [ ] Dependencies listed with version pins

## Example

**Input**: User provides a PDF paper describing Dijkstra's shortest path algorithm.

**Extraction** (Step 1):
```python
import pdfplumber
with pdfplumber.open("dijkstra_paper.pdf") as pdf:
    text = "\n".join(page.extract_text() for page in pdf.pages)
```

**Analysis** (Step 2): Detects graph algorithm, O((V+E) log V) complexity, Python domain.

**Output** (Step 4):
```
dijkstra-implementation/
├── src/dijkstra.py       # Fully implemented with type hints
├── src/graph.py           # Graph data structure
├── tests/test_dijkstra.py # Unit tests with sample graphs
├── requirements.txt       # pytest
├── README.md             # Links back to original paper
└── LICENSE
```

## Error Handling

- PDF corruption → try alternative library, then partial extraction
- Web timeout → retry with exponential backoff (3 attempts)
- Low analysis confidence → ask user to confirm domain/language before generating
- No algorithms detected → generate general-purpose scaffold and inform user

## Extension

Add new format extractors or language generators by implementing the respective interface and registering in the format/language maps. See `references/` for extraction patterns, analysis methodology, and generation rules.
