# Extraction Patterns Reference

This document describes extraction patterns for different content formats.

## PDF Extraction Patterns

### Academic Papers
- **Title**: Usually in first 20 lines, larger font
- **Abstract**: Labeled section, typically after title
- **Sections**: Numbered or titled (Introduction, Methods, Results, Conclusion)
- **Algorithms**: Indented, numbered steps, or "Algorithm X:" headers
- **Code**: Monospace font, background shading
- **References**: Last section, bibliographic format

### Technical Reports
- Similar to academic papers but may include:
- Executive summary at start
- Appendices with detailed data
- Diagrams and flowcharts (text descriptions)

## Web Content Patterns

### Blog Posts
- **Main Content**: Usually in `<article>` or `<main>` tags
- **Code Blocks**: `<pre><code>` tags with language classes
- **Headings**: `<h1>` through `<h6>` for structure
- **Metadata**: `<meta>` tags and Open Graph properties

### Documentation Sites
- **Navigation**: Sidebar or header navigation (filter out)
- **Content Area**: Main documentation content
- **Code Examples**: Syntax-highlighted blocks
- **API Specs**: Structured format with endpoints

## Jupyter Notebook Patterns

### Cell Types
- **Markdown Cells**: Explanatory text, headings, images
- **Code Cells**: Executable Python (or other language) code
- **Raw Cells**: Unformatted text (rare)

### Content Organization
- Title usually in first markdown cell (# heading)
- Imports typically in first code cell
- Alternating explanations (markdown) and code
- Outputs follow code cells

## Markdown Patterns

### YAML Front Matter
```yaml
---
title: Document Title
author: Author Name
date: 2025-01-01
---
```

### Structure
- **Headings**: # through ###### for hierarchy
- **Code Fences**: ```language notation
- **Lists**: Numbered (1. 2. 3.) or bulleted (- * +)
- **Links**: [text](url) format
- **Inline Code**: `backticks`

## Algorithm Detection Patterns

### Explicit Algorithms
```
Algorithm 1: Quick Sort
1. Choose pivot element
2. Partition array
3. Recursively sort partitions
```

### Pseudocode
```
PROCEDURE Dijkstra(Graph, source):
    FOR each vertex v in Graph:
        distance[v] := infinity
        previous[v] := undefined
    distance[source] := 0
    ...
```

### Inline Descriptions
"The algorithm works by first sorting the input array,
then performing a binary search..."

## Architecture Detection Patterns

### Explicit Mentions
- "The system uses a microservices architecture..."
- "We implement the MVC pattern..."
- "This follows an event-driven approach..."

### Component Descriptions
- "The frontend communicates with the backend via REST API"
- "Services are orchestrated using Kubernetes"
- "Data flows through an ETL pipeline"

## Dependency Detection Patterns

### Import Statements
- Python: `import numpy`, `from pandas import DataFrame`
- JavaScript: `const express = require('express')`
- Java: `import java.util.List;`

### Installation Commands
- `pip install tensorflow`
- `npm install react`
- `cargo add tokio`

### Inline Mentions
- "This implementation uses TensorFlow for training"
- "Built with React and Express"
- "Requires Python 3.8+"
