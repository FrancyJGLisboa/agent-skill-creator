---
name: pdf-text-extractor-cskill
description: Simple skill for extracting text from PDF documents with basic cleaning and formatting options. Created by Agent-Skill-Creator.
---

# PDF Text Extractor

This skill extracts text content from PDF documents and provides basic formatting options.

## When to Use This Skill

Use this skill when you need to:
- Extract text from PDF files
- Clean up extracted text (remove artifacts)
- Format extracted text for different use cases
- Process single or multiple PDFs

## Capabilities

### PDF Processing
- Extract text from PDF files
- Handle encrypted PDFs (with password)
- Process multiple pages
- Maintain basic text structure

### Text Cleaning
- Remove line breaks within paragraphs
- Fix common PDF artifacts
- Preserve important formatting
- Clean up special characters

### Output Formats
- Plain text (.txt)
- Markdown (.md)
- JSON with metadata

## Usage Examples

**Basic extraction:**
"Extract text from document.pdf"

**With cleaning:**
"Extract and clean text from report.pdf, remove line breaks"

**Multiple files:**
"Extract text from all PDFs in the reports/ folder"

**With output format:**
"Extract text from invoice.pdf and save as markdown"

## Scripts Available

- `scripts/extract_pdf.py` - Main extraction functionality
- `scripts/clean_text.py` - Text cleaning utilities
- `scripts/batch_process.py` - Process multiple files

## References

- `examples/sample_output.txt` - Example of cleaned output
- `pdf-formats.md` - Supported PDF formats and limitations

## Limitations

- Scanned PDFs require OCR (not included)
- Complex layouts may need manual adjustment
- Embedded images not extracted

## Installation Requirements

```bash
pip install PyPDF2 python-docx
```

This is a **Simple Skill** example - focused on one primary capability with minimal complexity.