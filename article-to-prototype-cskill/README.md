# Article-to-Prototype Skill

**Version:** 1.0.0
**Type:** Claude Skill
**Architecture:** Simple Skill

Autonomously extracts technical content from articles (PDF, web, markdown, notebooks) and generates functional prototypes/POCs in the appropriate programming language.

---

## Overview

The Article-to-Prototype Skill bridges the gap between technical documentation and working code. It automates the time-consuming process of translating algorithms, architectures, and methodologies from written content into executable prototypes.

### Key Features

- **Multi-Format Extraction**: PDF, web pages, Jupyter notebooks, markdown
- **Intelligent Analysis**: Detects algorithms, architectures, dependencies, and domain
- **Language Selection**: Automatically chooses optimal programming language
- **Multi-Language Generation**: Python, JavaScript/TypeScript, Rust, Go, Julia
- **Production Quality**: Complete projects with tests, dependencies, and documentation
- **Source Attribution**: Maintains links to original articles

---

## Installation

### Prerequisites

- Python 3.8 or higher
- Claude Code CLI

### Install Dependencies

```bash
cd article-to-prototype-cskill
pip install -r requirements.txt
```

### Required Python Packages

```
PyPDF2>=3.0.0
pdfplumber>=0.10.0
requests>=2.31.0
beautifulsoup4>=4.12.0
trafilatura>=1.6.0
nbformat>=5.9.0
mistune>=3.0.0
```

---

## Usage

### In Claude Code

The skill activates automatically when you use phrases like:

```
"Extract algorithm from paper.pdf and implement in Python"
"Create prototype from https://example.com/tutorial"
"Implement the code described in notebook.ipynb"
"Parse this article and build a working version"
```

### Command Line

```bash
# Basic usage
python scripts/main.py path/to/article.pdf

# Specify output directory
python scripts/main.py article.pdf -o ./my-prototype

# Specify target language
python scripts/main.py article.pdf -l rust

# Verbose output
python scripts/main.py article.pdf -v
```

---

## Examples

### Example 1: PDF Algorithm Paper

**Input:**
```bash
python scripts/main.py papers/dijkstra.pdf
```

**Output:**
```
article-to-prototype-cskill/output/
├── src/
│   ├── main.py          # Dijkstra implementation
│   └── graph.py         # Graph data structure
├── tests/
│   └── test_main.py     # Unit tests
├── requirements.txt
├── README.md
└── .gitignore
```

### Example 2: Web Tutorial

**Input:**
```bash
python scripts/main.py https://realpython.com/python-REST-api -l python
```

**Output:**
```
output/
├── src/
│   ├── main.py          # REST API server
│   └── routes.py        # API endpoints
├── requirements.txt     # flask, requests
├── README.md
└── .gitignore
```

### Example 3: Jupyter Notebook

**Input:**
```bash
python scripts/main.py ml-tutorial.ipynb
```

**Output:**
```
output/
├── src/
│   ├── model.py         # ML model
│   ├── preprocessing.py # Data preprocessing
│   └── training.py      # Training loop
├── requirements.txt     # numpy, pandas, sklearn
├── tests/
└── README.md
```

---

## Supported Formats

### PDF Documents
- Academic papers
- Technical reports
- Books and chapters
- Presentations

### Web Content
- Blog posts
- Documentation sites
- Tutorials
- GitHub READMEs

### Jupyter Notebooks
- Code and markdown cells
- Cell outputs
- Metadata and dependencies

### Markdown Files
- Standard markdown
- YAML front matter
- Code fences
- GFM (GitHub Flavored Markdown)

---

## Supported Languages

| Language | Use Cases | Generated Files |
|----------|-----------|-----------------|
| **Python** | ML, data science, scripting | main.py, requirements.txt, tests |
| **JavaScript** | Web apps, Node.js | index.js, package.json |
| **TypeScript** | Type-safe web apps | index.ts, tsconfig.json, package.json |
| **Rust** | Systems, performance | main.rs, Cargo.toml |
| **Go** | Microservices, CLIs | main.go, go.mod |
| **Julia** | Scientific computing | main.jl, Project.toml |

---

## How It Works

### Pipeline Overview

```
Input → Extraction → Analysis → Language Selection → Generation → Output
```

### 1. Extraction Phase
- Detects input format (PDF, URL, notebook, markdown)
- Applies specialized extractor
- Preserves structure, code blocks, and metadata

### 2. Analysis Phase
- **Algorithm Detection**: Identifies algorithms, pseudocode, and procedures
- **Architecture Recognition**: Finds design patterns and system architectures
- **Domain Classification**: Categorizes content (ML, web dev, systems, etc.)
- **Dependency Extraction**: Discovers required libraries and tools

### 3. Language Selection
Selection priority:
1. Explicit user hint (`-l python`)
2. Detected from code blocks
3. Domain best practices (ML → Python, Web → TypeScript)
4. Dependency analysis
5. Default to Python

### 4. Generation Phase
Creates complete project:
- Main implementation with algorithms
- Dependency manifest
- Test suite structure
- Comprehensive README
- .gitignore

---

## Configuration

### Environment Variables

```bash
# Optional: Custom cache directory
export ARTICLE_PROTOTYPE_CACHE_DIR=~/.article-to-prototype

# Optional: Default output language
export ARTICLE_PROTOTYPE_DEFAULT_LANG=python
```

### Custom Prompts

Edit `assets/prompts/analysis_prompt.txt` to customize analysis behavior.

---

## Quality Standards

Every generated prototype includes:

- ✅ **No Placeholders**: Fully implemented functions
- ✅ **Type Safety**: Type hints, annotations, or strong typing
- ✅ **Error Handling**: Try/catch, Result types, error returns
- ✅ **Logging**: Structured logging throughout
- ✅ **Documentation**: Docstrings and README
- ✅ **Tests**: Basic test suite structure
- ✅ **Source Attribution**: Links to original article

---

## Troubleshooting

### PDF Extraction Issues

**Problem:** "No text extracted from PDF"

**Solutions:**
- PDF may be scanned (image-based) - try OCR preprocessing
- Try alternative URL if article is available online
- Check if PDF is corrupted

### Web Extraction Issues

**Problem:** "Failed to fetch URL"

**Solutions:**
- Check internet connection
- Verify URL is accessible
- Some sites may block automated access
- Try downloading HTML and processing locally

### Dependency Issues

**Problem:** "Import error for pdfplumber"

**Solution:**
```bash
pip install --upgrade -r requirements.txt
```

---

## Performance

### Typical Processing Times

| Operation | Duration |
|-----------|----------|
| PDF extraction (20 pages) | 3-5 seconds |
| Web page extraction | 2-4 seconds |
| Content analysis | 5-10 seconds |
| Code generation (Python) | 10-15 seconds |
| **Total (end-to-end)** | **30-45 seconds** |

### Optimization Tips

- Use local files instead of URLs when possible
- Cache is enabled by default (24-hour TTL)
- Run with `-v` flag to see detailed progress

---

## Advanced Usage

### Batch Processing

```python
from scripts.main import ArticleToPrototype

orchestrator = ArticleToPrototype()

articles = [
    "paper1.pdf",
    "paper2.pdf",
    "https://example.com/tutorial"
]

for article in articles:
    result = orchestrator.process(
        source=article,
        output_dir=f"./output_{i}"
    )
    print(f"Generated: {result['output_dir']}")
```

### Custom Analysis

```python
from scripts.analyzers.content_analyzer import ContentAnalyzer
from scripts.extractors.pdf_extractor import PDFExtractor

# Extract
extractor = PDFExtractor()
content = extractor.extract("article.pdf")

# Custom analysis
analyzer = ContentAnalyzer()
analysis = analyzer.analyze(content)

# Access results
print(f"Domain: {analysis.domain}")
print(f"Algorithms: {len(analysis.algorithms)}")
for algo in analysis.algorithms:
    print(f"  - {algo.name}: {algo.description}")
```

---

## Contributing

This skill is part of the Agent-Skill-Creator ecosystem. To contribute:

1. Test the skill with various article types
2. Report issues with specific examples
3. Suggest new features or languages
4. Submit extraction pattern improvements

---

## License

MIT License - See LICENSE file for details

---

## Acknowledgments

- Created by Agent-Skill-Creator v2.1
- Extraction libraries: PyPDF2, pdfplumber, trafilatura, BeautifulSoup
- Follows Agent-Skill-Creator quality standards

---

## Version History

### v1.0.0 (2025-10-23)
- Initial release
- Multi-format extraction (PDF, web, notebooks, markdown)
- Multi-language generation (Python, JS/TS, Rust, Go, Julia)
- Intelligent analysis and language selection
- Production-quality code generation

---

**Generated by:** Agent-Skill-Creator v2.1
**Last Updated:** 2025-10-23
**Documentation:** See SKILL.md for comprehensive details
