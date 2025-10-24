"""
PDF Extractor

Extracts text, structure, and metadata from PDF documents using multiple strategies.
Preserves code blocks, section structure, and handles various PDF formats.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

logger = logging.getLogger(__name__)


class PDFExtractionError(Exception):
    """Raised when PDF extraction fails"""
    pass


@dataclass
class Section:
    """Represents a document section"""
    heading: str
    level: int
    content: str
    line_number: int
    subsections: List['Section']


@dataclass
class CodeBlock:
    """Represents a code block"""
    language: Optional[str]
    code: str
    line_number: Optional[int]
    context: str


@dataclass
class ExtractedContent:
    """Structured extracted content"""
    title: str
    sections: List[Section]
    code_blocks: List[CodeBlock]
    metadata: Dict[str, Any]
    source_url: Optional[str]
    extraction_date: datetime
    raw_text: str


class PDFExtractor:
    """Extracts content from PDF files with structure preservation"""

    def __init__(self):
        """Initialize PDF extractor"""
        if not HAS_PDFPLUMBER and not HAS_PYPDF2:
            raise ImportError(
                "Neither pdfplumber nor PyPDF2 is installed. "
                "Install with: pip install pdfplumber PyPDF2"
            )

        self.heading_patterns = [
            re.compile(r'^(\d+\.)+\s+[A-Z]'),  # 1.1 Title
            re.compile(r'^[A-Z][A-Z\s]+$'),     # ALL CAPS TITLE
            re.compile(r'^Abstract\s*$', re.IGNORECASE),
            re.compile(r'^Introduction\s*$', re.IGNORECASE),
            re.compile(r'^Conclusion\s*$', re.IGNORECASE),
            re.compile(r'^References\s*$', re.IGNORECASE),
        ]

        self.code_indicators = [
            'algorithm', 'procedure', 'function', 'def ', 'class ',
            'import ', 'for(', 'while(', 'if(', '{', '}', ';'
        ]

    def extract(self, pdf_path: str) -> ExtractedContent:
        """
        Extract content from a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            ExtractedContent object with structured data

        Raises:
            PDFExtractionError: If extraction fails
            FileNotFoundError: If PDF file doesn't exist
        """
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if not path.suffix.lower() == '.pdf':
            raise PDFExtractionError(f"Not a PDF file: {pdf_path}")

        logger.info(f"Extracting content from PDF: {pdf_path}")

        # Try pdfplumber first (better layout analysis)
        if HAS_PDFPLUMBER:
            try:
                return self._extract_with_pdfplumber(pdf_path)
            except Exception as e:
                logger.warning(f"pdfplumber extraction failed: {e}, trying PyPDF2")
                if HAS_PYPDF2:
                    return self._extract_with_pypdf2(pdf_path)
                raise

        # Fallback to PyPDF2
        if HAS_PYPDF2:
            return self._extract_with_pypdf2(pdf_path)

        raise PDFExtractionError("No PDF library available for extraction")

    def _extract_with_pdfplumber(self, pdf_path: str) -> ExtractedContent:
        """Extract using pdfplumber (preferred method)"""
        logger.debug("Using pdfplumber for extraction")

        text_content = []
        metadata = {}

        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Extract metadata
                if pdf.metadata:
                    metadata = {
                        'title': pdf.metadata.get('Title', ''),
                        'author': pdf.metadata.get('Author', ''),
                        'subject': pdf.metadata.get('Subject', ''),
                        'creator': pdf.metadata.get('Creator', ''),
                        'producer': pdf.metadata.get('Producer', ''),
                        'creation_date': pdf.metadata.get('CreationDate', ''),
                    }

                # Extract text from all pages
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        text = page.extract_text()
                        if text:
                            text_content.append(f"\n--- Page {page_num} ---\n{text}")
                            logger.debug(f"Extracted {len(text)} chars from page {page_num}")
                    except Exception as e:
                        logger.warning(f"Failed to extract page {page_num}: {e}")
                        continue

        except Exception as e:
            raise PDFExtractionError(f"pdfplumber extraction failed: {e}")

        if not text_content:
            raise PDFExtractionError("No text content extracted from PDF")

        raw_text = '\n'.join(text_content)
        logger.info(f"Extracted {len(raw_text)} characters from PDF")

        # Process extracted text
        return self._process_extracted_text(raw_text, metadata, pdf_path)

    def _extract_with_pypdf2(self, pdf_path: str) -> ExtractedContent:
        """Extract using PyPDF2 (fallback method)"""
        logger.debug("Using PyPDF2 for extraction")

        text_content = []
        metadata = {}

        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)

                # Extract metadata
                if reader.metadata:
                    metadata = {
                        'title': reader.metadata.get('/Title', ''),
                        'author': reader.metadata.get('/Author', ''),
                        'subject': reader.metadata.get('/Subject', ''),
                        'creator': reader.metadata.get('/Creator', ''),
                        'producer': reader.metadata.get('/Producer', ''),
                    }

                # Extract text from all pages
                for page_num, page in enumerate(reader.pages, 1):
                    try:
                        text = page.extract_text()
                        if text:
                            text_content.append(f"\n--- Page {page_num} ---\n{text}")
                            logger.debug(f"Extracted {len(text)} chars from page {page_num}")
                    except Exception as e:
                        logger.warning(f"Failed to extract page {page_num}: {e}")
                        continue

        except Exception as e:
            raise PDFExtractionError(f"PyPDF2 extraction failed: {e}")

        if not text_content:
            raise PDFExtractionError("No text content extracted from PDF")

        raw_text = '\n'.join(text_content)
        logger.info(f"Extracted {len(raw_text)} characters from PDF")

        # Process extracted text
        return self._process_extracted_text(raw_text, metadata, pdf_path)

    def _process_extracted_text(
        self,
        raw_text: str,
        metadata: Dict[str, Any],
        pdf_path: str
    ) -> ExtractedContent:
        """Process raw extracted text into structured content"""

        # Extract title
        title = self._extract_title(raw_text, metadata)

        # Extract sections
        sections = self._extract_sections(raw_text)

        # Extract code blocks
        code_blocks = self._extract_code_blocks(raw_text)

        # Build metadata
        full_metadata = {
            **metadata,
            'file_name': Path(pdf_path).name,
            'file_path': pdf_path,
            'num_sections': len(sections),
            'num_code_blocks': len(code_blocks),
        }

        return ExtractedContent(
            title=title,
            sections=sections,
            code_blocks=code_blocks,
            metadata=full_metadata,
            source_url=None,
            extraction_date=datetime.now(),
            raw_text=raw_text
        )

    def _extract_title(self, text: str, metadata: Dict[str, Any]) -> str:
        """Extract document title"""
        # First, try metadata
        if metadata.get('title'):
            title = metadata['title'].strip()
            if title and title.lower() != 'untitled':
                logger.debug(f"Using title from metadata: {title}")
                return title

        # Try to find title in first few lines
        lines = text.split('\n')
        for i, line in enumerate(lines[:20]):  # Check first 20 lines
            line = line.strip()
            if len(line) > 10 and len(line) < 200:
                # Likely a title if it's not too short or too long
                if not line.startswith('---'):  # Skip page markers
                    logger.debug(f"Using title from content: {line}")
                    return line

        # Fallback
        return "Untitled Document"

    def _extract_sections(self, text: str) -> List[Section]:
        """Extract document sections with headings"""
        sections = []
        lines = text.split('\n')
        current_section = None
        current_content = []

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Check if line is a heading
            is_heading, level = self._is_heading(stripped)

            if is_heading:
                # Save previous section if exists
                if current_section:
                    current_section.content = '\n'.join(current_content).strip()
                    sections.append(current_section)

                # Start new section
                current_section = Section(
                    heading=stripped,
                    level=level,
                    content='',
                    line_number=i,
                    subsections=[]
                )
                current_content = []
            elif current_section:
                # Add content to current section
                current_content.append(line)

        # Save last section
        if current_section:
            current_section.content = '\n'.join(current_content).strip()
            sections.append(current_section)

        logger.info(f"Extracted {len(sections)} sections")
        return sections

    def _is_heading(self, line: str) -> Tuple[bool, int]:
        """
        Determine if a line is a heading and its level.

        Returns:
            Tuple of (is_heading, level)
        """
        if not line or len(line) < 3:
            return False, 0

        # Check against heading patterns
        for pattern in self.heading_patterns:
            if pattern.match(line):
                # Determine level based on numbering
                if line[0].isdigit():
                    level = line.split()[0].count('.') + 1
                else:
                    level = 1
                return True, level

        # Check for short uppercase lines (potential headings)
        if line.isupper() and 3 < len(line) < 50 and ' ' in line:
            return True, 1

        return False, 0

    def _extract_code_blocks(self, text: str) -> List[CodeBlock]:
        """Extract code blocks from text"""
        code_blocks = []
        lines = text.split('\n')

        in_code_block = False
        current_code = []
        code_start_line = 0
        context = ''

        for i, line in enumerate(lines):
            # Check if line looks like code
            is_code = self._is_code_line(line)

            if is_code and not in_code_block:
                # Start of code block
                in_code_block = True
                code_start_line = i
                current_code = [line]
                # Capture context (previous line)
                if i > 0:
                    context = lines[i - 1].strip()
            elif is_code and in_code_block:
                # Continue code block
                current_code.append(line)
            elif not is_code and in_code_block:
                # End of code block
                if len(current_code) > 2:  # Minimum 3 lines for a code block
                    code_blocks.append(CodeBlock(
                        language=self._detect_language('\n'.join(current_code)),
                        code='\n'.join(current_code),
                        line_number=code_start_line,
                        context=context
                    ))
                in_code_block = False
                current_code = []
                context = ''

        # Save last code block if exists
        if in_code_block and len(current_code) > 2:
            code_blocks.append(CodeBlock(
                language=self._detect_language('\n'.join(current_code)),
                code='\n'.join(current_code),
                line_number=code_start_line,
                context=context
            ))

        logger.info(f"Extracted {len(code_blocks)} code blocks")
        return code_blocks

    def _is_code_line(self, line: str) -> bool:
        """Check if a line looks like code"""
        stripped = line.strip()

        # Empty lines don't indicate code
        if not stripped:
            return False

        # Check for code indicators
        for indicator in self.code_indicators:
            if indicator in stripped.lower():
                return True

        # Check for indentation (common in code)
        if line.startswith('    ') or line.startswith('\t'):
            return True

        # Check for common code patterns
        if re.search(r'[=\+\-\*\/]{2,}', stripped):  # Multiple operators
            return True
        if re.search(r'[\(\)\{\}\[\];]', stripped):  # Brackets and semicolons
            return True
        if re.search(r'^\s*\d+[\.\)]\s+', stripped):  # Numbered steps (algorithm)
            return True

        return False

    def _detect_language(self, code: str) -> Optional[str]:
        """Detect programming language from code"""
        code_lower = code.lower()

        language_indicators = {
            'python': ['def ', 'import ', 'from ', 'print(', '__init__', 'self.'],
            'javascript': ['function ', 'const ', 'let ', 'var ', '=>', 'console.'],
            'java': ['public class', 'private ', 'void ', 'System.out'],
            'c++': ['#include', 'cout', 'std::', 'namespace'],
            'c': ['#include', 'printf', 'int main'],
            'rust': ['fn ', 'let mut', 'impl ', 'pub '],
            'go': ['func ', 'package ', 'import (', ':='],
            'pseudocode': ['algorithm', 'procedure', 'begin', 'end', 'step '],
        }

        scores = {lang: 0 for lang in language_indicators}

        for lang, indicators in language_indicators.items():
            for indicator in indicators:
                if indicator in code_lower:
                    scores[lang] += 1

        # Return language with highest score
        max_score = max(scores.values())
        if max_score > 0:
            detected = max(scores, key=scores.get)
            logger.debug(f"Detected language: {detected} (score: {max_score})")
            return detected

        return None

    def extract_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract only metadata from PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary of metadata
        """
        logger.debug(f"Extracting metadata from: {pdf_path}")

        if HAS_PDFPLUMBER:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    if pdf.metadata:
                        return dict(pdf.metadata)
            except Exception as e:
                logger.warning(f"pdfplumber metadata extraction failed: {e}")

        if HAS_PYPDF2:
            try:
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    if reader.metadata:
                        return {k.replace('/', ''): v for k, v in reader.metadata.items()}
            except Exception as e:
                logger.warning(f"PyPDF2 metadata extraction failed: {e}")

        return {}
