"""
Markdown Extractor

Parses markdown files and extracts structure and content.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    import mistune
    HAS_MISTUNE = True
except ImportError:
    HAS_MISTUNE = False

from .pdf_extractor import ExtractedContent, Section, CodeBlock

logger = logging.getLogger(__name__)


class MarkdownExtractionError(Exception):
    """Raised when markdown extraction fails"""
    pass


class MarkdownExtractor:
    """Extracts content from markdown files"""

    def __init__(self):
        """Initialize markdown extractor"""
        self.code_fence_pattern = re.compile(
            r'```(\w+)?\n(.*?)\n```',
            re.DOTALL
        )
        self.heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)

    def extract(self, markdown_path: str) -> ExtractedContent:
        """
        Extract content from a markdown file.

        Args:
            markdown_path: Path to the .md file

        Returns:
            ExtractedContent object with structured content

        Raises:
            MarkdownExtractionError: If parsing fails
        """
        path = Path(markdown_path)
        if not path.exists():
            raise FileNotFoundError(f"Markdown file not found: {markdown_path}")

        logger.info(f"Extracting markdown: {markdown_path}")

        try:
            with open(markdown_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise MarkdownExtractionError(f"Failed to read markdown: {e}")

        # Extract YAML front matter if present
        front_matter, content = self._extract_front_matter(content)

        # Extract title
        title = self._extract_title(content, front_matter)

        # Extract code blocks
        code_blocks = self.extract_code_blocks(content)

        # Extract sections
        sections = self._extract_sections(content)

        # Build metadata
        metadata = {
            'file_name': path.name,
            'file_path': str(path),
            'num_sections': len(sections),
            'num_code_blocks': len(code_blocks),
            **front_matter
        }

        logger.info(f"Extracted {len(sections)} sections and {len(code_blocks)} code blocks")

        return ExtractedContent(
            title=title,
            sections=sections,
            code_blocks=code_blocks,
            metadata=metadata,
            source_url=None,
            extraction_date=datetime.now(),
            raw_text=content
        )

    def _extract_front_matter(self, content: str) -> tuple[Dict[str, Any], str]:
        """Extract YAML front matter from markdown"""
        front_matter = {}

        # Check for YAML front matter (--- ... ---)
        if content.startswith('---\n'):
            try:
                end_index = content.index('\n---\n', 4)
                yaml_content = content[4:end_index]
                content = content[end_index + 5:]

                # Simple YAML parsing (key: value pairs)
                for line in yaml_content.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        front_matter[key.strip()] = value.strip()

                logger.debug(f"Extracted front matter: {front_matter}")

            except ValueError:
                # No closing ---, treat as regular content
                pass

        return front_matter, content

    def _extract_title(self, content: str, front_matter: Dict[str, Any]) -> str:
        """Extract title from markdown"""
        # Try front matter first
        if 'title' in front_matter:
            return front_matter['title']

        # Look for first # heading
        match = self.heading_pattern.search(content)
        if match:
            return match.group(2).strip()

        return "Untitled Document"

    def _extract_sections(self, content: str) -> List[Section]:
        """Extract sections based on headings"""
        sections = []

        # Find all headings
        headings = list(self.heading_pattern.finditer(content))

        for i, match in enumerate(headings):
            heading_level = len(match.group(1))
            heading_text = match.group(2).strip()
            start_pos = match.end()

            # Find content until next heading or end
            if i + 1 < len(headings):
                end_pos = headings[i + 1].start()
            else:
                end_pos = len(content)

            section_content = content[start_pos:end_pos].strip()

            # Remove code blocks from section content for cleaner reading
            section_content_clean = self.code_fence_pattern.sub(
                '[code block]',
                section_content
            )

            sections.append(Section(
                heading=heading_text,
                level=heading_level,
                content=section_content_clean,
                line_number=content[:start_pos].count('\n'),
                subsections=[]
            ))

        logger.debug(f"Found {len(sections)} sections")
        return sections

    def extract_code_blocks(self, content: str) -> List[CodeBlock]:
        """
        Extract code blocks from markdown.

        Args:
            content: Markdown content string

        Returns:
            List of CodeBlock objects
        """
        code_blocks = []

        # Find all code fences
        for i, match in enumerate(self.code_fence_pattern.finditer(content)):
            language = match.group(1)  # Language annotation
            code = match.group(2).strip()

            # Get context (text before code block)
            context_start = max(0, match.start() - 200)
            context_text = content[context_start:match.start()]
            # Get last line as context
            context = context_text.split('\n')[-1].strip() if context_text else ''

            code_blocks.append(CodeBlock(
                language=language,
                code=code,
                line_number=content[:match.start()].count('\n'),
                context=context
            ))

        logger.debug(f"Found {len(code_blocks)} code blocks")
        return code_blocks
