"""
Notebook Extractor

Parses Jupyter notebooks and extracts code, markdown, and outputs.
"""

import logging
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    import nbformat
    HAS_NBFORMAT = True
except ImportError:
    HAS_NBFORMAT = False

from .pdf_extractor import ExtractedContent, Section, CodeBlock

logger = logging.getLogger(__name__)


class NotebookExtractionError(Exception):
    """Raised when notebook extraction fails"""
    pass


class NotebookExtractor:
    """Extracts content from Jupyter notebooks"""

    def __init__(self):
        """Initialize notebook extractor"""
        if not HAS_NBFORMAT:
            raise ImportError("nbformat not installed. Install with: pip install nbformat")

    def extract(self, notebook_path: str) -> ExtractedContent:
        """
        Extract content from a Jupyter notebook.

        Args:
            notebook_path: Path to the .ipynb file

        Returns:
            ExtractedContent object with cells and outputs

        Raises:
            NotebookExtractionError: If parsing fails
        """
        path = Path(notebook_path)
        if not path.exists():
            raise FileNotFoundError(f"Notebook not found: {notebook_path}")

        if not path.suffix.lower() == '.ipynb':
            raise NotebookExtractionError(f"Not a notebook file: {notebook_path}")

        logger.info(f"Extracting notebook: {notebook_path}")

        try:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
        except Exception as e:
            raise NotebookExtractionError(f"Failed to read notebook: {e}")

        # Extract title from metadata or first markdown cell
        title = self._extract_title(nb)

        # Extract sections from markdown cells
        sections = []
        code_blocks = []
        raw_text_parts = []

        for i, cell in enumerate(nb.cells):
            if cell.cell_type == 'markdown':
                section = self._process_markdown_cell(cell, i)
                if section:
                    sections.append(section)
                    raw_text_parts.append(f"## {section.heading}\n{section.content}")

            elif cell.cell_type == 'code':
                code_block = self._process_code_cell(cell, i)
                if code_block:
                    code_blocks.append(code_block)
                    raw_text_parts.append(f"```python\n{code_block.code}\n```")

        # Extract metadata
        metadata = self._extract_metadata(nb, notebook_path)

        # Extract dependencies from code cells
        dependencies = self.extract_dependencies(notebook_path)
        metadata['dependencies'] = dependencies

        raw_text = '\n\n'.join(raw_text_parts)

        logger.info(f"Extracted {len(sections)} sections and {len(code_blocks)} code blocks")

        return ExtractedContent(
            title=title,
            sections=sections,
            code_blocks=code_blocks,
            metadata=metadata,
            source_url=None,
            extraction_date=datetime.now(),
            raw_text=raw_text
        )

    def _extract_title(self, nb: Any) -> str:
        """Extract title from notebook"""
        # Try metadata first
        if hasattr(nb, 'metadata') and 'title' in nb.metadata:
            return nb.metadata['title']

        # Look for title in first markdown cell
        for cell in nb.cells:
            if cell.cell_type == 'markdown':
                lines = cell.source.split('\n')
                for line in lines:
                    if line.startswith('#'):
                        title = line.lstrip('#').strip()
                        if title:
                            return title

        return "Untitled Notebook"

    def _process_markdown_cell(self, cell: Any, cell_num: int) -> Optional[Section]:
        """Process markdown cell into a section"""
        content = cell.source.strip()

        if not content:
            return None

        # Check if starts with heading
        lines = content.split('\n')
        if lines[0].startswith('#'):
            heading_line = lines[0]
            level = len(heading_line) - len(heading_line.lstrip('#'))
            heading = heading_line.lstrip('#').strip()
            body = '\n'.join(lines[1:]).strip()

            return Section(
                heading=heading,
                level=level,
                content=body,
                line_number=cell_num,
                subsections=[]
            )

        # If no heading, create generic section
        return Section(
            heading=f"Cell {cell_num}",
            level=3,
            content=content,
            line_number=cell_num,
            subsections=[]
        )

    def _process_code_cell(self, cell: Any, cell_num: int) -> Optional[CodeBlock]:
        """Process code cell into a code block"""
        code = cell.source.strip()

        if not code:
            return None

        # Extract language from cell metadata
        language = 'python'  # Default for Jupyter
        if hasattr(cell, 'metadata') and 'language' in cell.metadata:
            language = cell.metadata['language']

        # Get output as context
        context = ''
        if hasattr(cell, 'outputs') and cell.outputs:
            output_texts = []
            for output in cell.outputs[:3]:  # First 3 outputs
                if hasattr(output, 'text'):
                    output_texts.append(str(output.text)[:100])
                elif hasattr(output, 'data') and 'text/plain' in output.data:
                    output_texts.append(str(output.data['text/plain'])[:100])

            if output_texts:
                context = ' | '.join(output_texts)

        return CodeBlock(
            language=language,
            code=code,
            line_number=cell_num,
            context=context
        )

    def _extract_metadata(self, nb: Any, notebook_path: str) -> Dict[str, Any]:
        """Extract notebook metadata"""
        metadata = {
            'file_name': Path(notebook_path).name,
            'file_path': notebook_path,
            'num_cells': len(nb.cells) if hasattr(nb, 'cells') else 0,
        }

        # Extract kernel info
        if hasattr(nb, 'metadata'):
            if 'kernelspec' in nb.metadata:
                kernel = nb.metadata['kernelspec']
                metadata['kernel_name'] = kernel.get('name', 'unknown')
                metadata['kernel_display_name'] = kernel.get('display_name', 'unknown')

            if 'language_info' in nb.metadata:
                lang_info = nb.metadata['language_info']
                metadata['language'] = lang_info.get('name', 'unknown')
                metadata['language_version'] = lang_info.get('version', 'unknown')

        return metadata

    def extract_code_cells(self, notebook_path: str) -> List[CodeBlock]:
        """Extract only code cells"""
        content = self.extract(notebook_path)
        return content.code_blocks

    def extract_dependencies(self, notebook_path: str) -> List[str]:
        """
        Extract imported libraries and dependencies.

        Args:
            notebook_path: Path to notebook

        Returns:
            List of dependency names
        """
        try:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
        except Exception as e:
            logger.error(f"Failed to read notebook for dependencies: {e}")
            return []

        dependencies = set()
        import_pattern = re.compile(
            r'^\s*(?:from\s+(\S+)\s+)?import\s+(\S+)',
            re.MULTILINE
        )

        for cell in nb.cells:
            if cell.cell_type == 'code':
                matches = import_pattern.findall(cell.source)
                for match in matches:
                    # match[0] is 'from X', match[1] is 'import Y'
                    dep = match[0] if match[0] else match[1]
                    # Get root package name
                    root_dep = dep.split('.')[0]
                    dependencies.add(root_dep)

        logger.debug(f"Extracted dependencies: {dependencies}")
        return sorted(list(dependencies))
