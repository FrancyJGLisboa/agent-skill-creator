"""
Web Extractor

Fetches and extracts content from web pages and online documentation.
Removes boilerplate, extracts code blocks, and preserves article structure.
"""

import logging
import re
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from urllib.parse import urlparse, urljoin
from dataclasses import dataclass

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

try:
    import trafilatura
    HAS_TRAFILATURA = True
except ImportError:
    HAS_TRAFILATURA = False

from .pdf_extractor import ExtractedContent, Section, CodeBlock

logger = logging.getLogger(__name__)


class WebExtractionError(Exception):
    """Raised when web extraction fails"""
    pass


class WebExtractor:
    """Extracts content from web pages with boilerplate removal"""

    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        user_agent: Optional[str] = None
    ):
        """
        Initialize web extractor.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            user_agent: Custom user agent string
        """
        if not HAS_REQUESTS:
            raise ImportError("requests library not installed. Install with: pip install requests")

        if not HAS_BS4 and not HAS_TRAFILATURA:
            raise ImportError(
                "Neither BeautifulSoup4 nor trafilatura is installed. "
                "Install with: pip install beautifulsoup4 trafilatura"
            )

        self.timeout = timeout
        self.max_retries = max_retries
        self.user_agent = user_agent or (
            "Mozilla/5.0 (compatible; Article-to-Prototype/1.0)"
        )

        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})

    def extract(self, url: str) -> ExtractedContent:
        """
        Extract content from a web page.

        Args:
            url: URL to fetch and extract

        Returns:
            ExtractedContent object with structured data

        Raises:
            WebExtractionError: If fetching or parsing fails
        """
        logger.info(f"Extracting content from URL: {url}")

        # Validate URL
        if not self._is_valid_url(url):
            raise WebExtractionError(f"Invalid URL: {url}")

        # Fetch HTML content
        html = self._fetch_html(url)

        # Extract content using best available method
        if HAS_TRAFILATURA:
            try:
                return self._extract_with_trafilatura(html, url)
            except Exception as e:
                logger.warning(f"trafilatura extraction failed: {e}, trying BeautifulSoup")
                if HAS_BS4:
                    return self._extract_with_beautifulsoup(html, url)
                raise

        if HAS_BS4:
            return self._extract_with_beautifulsoup(html, url)

        raise WebExtractionError("No web extraction library available")

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme in ['http', 'https'], result.netloc])
        except Exception:
            return False

    def _fetch_html(self, url: str) -> str:
        """
        Fetch HTML content with retries.

        Args:
            url: URL to fetch

        Returns:
            HTML content as string

        Raises:
            WebExtractionError: If fetching fails
        """
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(f"Fetching URL (attempt {attempt}/{self.max_retries})")
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()

                # Check content type
                content_type = response.headers.get('Content-Type', '').lower()
                if 'text/html' not in content_type and 'text/plain' not in content_type:
                    logger.warning(f"Unexpected content type: {content_type}")

                logger.info(f"Successfully fetched {len(response.text)} characters")
                return response.text

            except requests.exceptions.Timeout as e:
                last_error = e
                logger.warning(f"Request timeout on attempt {attempt}")
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)  # Exponential backoff

            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code
                if status_code == 404:
                    raise WebExtractionError(f"Page not found (404): {url}")
                elif status_code == 403:
                    raise WebExtractionError(f"Access forbidden (403): {url}")
                elif status_code >= 500:
                    last_error = e
                    logger.warning(f"Server error {status_code} on attempt {attempt}")
                    if attempt < self.max_retries:
                        time.sleep(2 ** attempt)
                else:
                    raise WebExtractionError(f"HTTP error {status_code}: {url}")

            except requests.exceptions.RequestException as e:
                last_error = e
                logger.warning(f"Request failed on attempt {attempt}: {e}")
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)

        raise WebExtractionError(f"Failed to fetch URL after {self.max_retries} attempts: {last_error}")

    def _extract_with_trafilatura(self, html: str, url: str) -> ExtractedContent:
        """Extract using trafilatura (preferred for main content)"""
        logger.debug("Using trafilatura for extraction")

        # Extract main content
        main_text = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
            favor_precision=True
        )

        if not main_text:
            raise WebExtractionError("trafilatura failed to extract content")

        # Extract metadata
        metadata = trafilatura.extract_metadata(html)
        metadata_dict = {}
        if metadata:
            metadata_dict = {
                'title': metadata.title or '',
                'author': metadata.author or '',
                'date': metadata.date or '',
                'description': metadata.description or '',
                'sitename': metadata.sitename or '',
                'url': url,
            }

        # Also use BeautifulSoup for code blocks if available
        code_blocks = []
        if HAS_BS4:
            soup = BeautifulSoup(html, 'html.parser')
            code_blocks = self._extract_code_blocks_bs4(soup)

        # Extract sections from main text
        sections = self._parse_text_into_sections(main_text)

        # Get title
        title = metadata_dict.get('title', 'Untitled Article')

        return ExtractedContent(
            title=title,
            sections=sections,
            code_blocks=code_blocks,
            metadata=metadata_dict,
            source_url=url,
            extraction_date=datetime.now(),
            raw_text=main_text
        )

    def _extract_with_beautifulsoup(self, html: str, url: str) -> ExtractedContent:
        """Extract using BeautifulSoup (fallback method)"""
        logger.debug("Using BeautifulSoup for extraction")

        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()

        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else 'Untitled Article'

        # Try to find main content area
        main_content = (
            soup.find('main') or
            soup.find('article') or
            soup.find('div', class_=re.compile(r'content|article|post', re.I)) or
            soup.find('body')
        )

        if not main_content:
            raise WebExtractionError("Could not find main content area")

        # Extract text
        text = main_content.get_text(separator='\n', strip=True)

        # Extract metadata from meta tags
        metadata = self._extract_metadata_bs4(soup)
        metadata['url'] = url

        # Extract sections
        sections = self._extract_sections_bs4(main_content)

        # Extract code blocks
        code_blocks = self._extract_code_blocks_bs4(main_content)

        return ExtractedContent(
            title=title,
            sections=sections,
            code_blocks=code_blocks,
            metadata=metadata,
            source_url=url,
            extraction_date=datetime.now(),
            raw_text=text
        )

    def _extract_metadata_bs4(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract metadata from HTML meta tags"""
        metadata = {}

        # Try Open Graph tags
        og_title = soup.find('meta', property='og:title')
        if og_title:
            metadata['title'] = og_title.get('content', '')

        og_description = soup.find('meta', property='og:description')
        if og_description:
            metadata['description'] = og_description.get('content', '')

        og_author = soup.find('meta', property='og:author')
        if og_author:
            metadata['author'] = og_author.get('content', '')

        # Try standard meta tags
        if 'description' not in metadata:
            description = soup.find('meta', attrs={'name': 'description'})
            if description:
                metadata['description'] = description.get('content', '')

        if 'author' not in metadata:
            author = soup.find('meta', attrs={'name': 'author'})
            if author:
                metadata['author'] = author.get('content', '')

        return metadata

    def _extract_sections_bs4(self, content: BeautifulSoup) -> List[Section]:
        """Extract sections based on heading tags"""
        sections = []
        current_section = None
        current_content = []

        for element in content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'pre']):
            if element.name.startswith('h'):
                # Save previous section
                if current_section:
                    current_section.content = '\n'.join(current_content).strip()
                    sections.append(current_section)

                # Start new section
                level = int(element.name[1])
                current_section = Section(
                    heading=element.get_text().strip(),
                    level=level,
                    content='',
                    line_number=0,
                    subsections=[]
                )
                current_content = []
            elif current_section:
                text = element.get_text().strip()
                if text:
                    current_content.append(text)

        # Save last section
        if current_section:
            current_section.content = '\n'.join(current_content).strip()
            sections.append(current_section)

        logger.info(f"Extracted {len(sections)} sections")
        return sections

    def _extract_code_blocks_bs4(self, content: BeautifulSoup) -> List[CodeBlock]:
        """Extract code blocks from HTML"""
        code_blocks = []

        # Find all code blocks (pre, code tags)
        for i, code_element in enumerate(content.find_all(['pre', 'code'])):
            code_text = code_element.get_text().strip()

            if not code_text or len(code_text) < 10:
                continue

            # Try to detect language from class
            language = None
            classes = code_element.get('class', [])
            for cls in classes:
                if cls.startswith('language-'):
                    language = cls.replace('language-', '')
                    break
                elif cls.startswith('lang-'):
                    language = cls.replace('lang-', '')
                    break

            # Get context (surrounding text)
            context = ''
            prev_sibling = code_element.find_previous_sibling(['p', 'h1', 'h2', 'h3', 'h4'])
            if prev_sibling:
                context = prev_sibling.get_text().strip()[:100]

            code_blocks.append(CodeBlock(
                language=language,
                code=code_text,
                line_number=i,
                context=context
            ))

        logger.info(f"Extracted {len(code_blocks)} code blocks")
        return code_blocks

    def _parse_text_into_sections(self, text: str) -> List[Section]:
        """Parse plain text into sections based on structure"""
        sections = []
        lines = text.split('\n')

        heading_pattern = re.compile(r'^#+\s+(.+)$|^([A-Z][A-Za-z\s]+)$')
        current_section = None
        current_content = []

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Check if line is a heading
            match = heading_pattern.match(stripped)
            if match and len(stripped) > 3 and len(stripped) < 100:
                # Save previous section
                if current_section:
                    current_section.content = '\n'.join(current_content).strip()
                    sections.append(current_section)

                # Start new section
                heading = match.group(1) or match.group(2)
                level = 1 if stripped.startswith('#') else 2
                current_section = Section(
                    heading=heading,
                    level=level,
                    content='',
                    line_number=i,
                    subsections=[]
                )
                current_content = []
            elif current_section:
                if stripped:
                    current_content.append(line)

        # Save last section
        if current_section:
            current_section.content = '\n'.join(current_content).strip()
            sections.append(current_section)

        return sections

    def extract_code_blocks(self, url: str) -> List[CodeBlock]:
        """
        Extract only code blocks from a web page.

        Args:
            url: URL to fetch

        Returns:
            List of CodeBlock objects
        """
        logger.info(f"Extracting code blocks from: {url}")
        content = self.extract(url)
        return content.code_blocks

    def crawl_documentation(
        self,
        base_url: str,
        max_pages: int = 10,
        follow_pattern: Optional[str] = None
    ) -> List[ExtractedContent]:
        """
        Crawl multi-page documentation.

        Args:
            base_url: Starting URL
            max_pages: Maximum number of pages to crawl
            follow_pattern: Regex pattern for URLs to follow (optional)

        Returns:
            List of ExtractedContent objects

        Note: This is a basic implementation. For production use,
        consider using a proper crawler like Scrapy.
        """
        logger.info(f"Starting documentation crawl from: {base_url}")
        logger.warning("Crawling is experimental and may be slow")

        visited = set()
        to_visit = [base_url]
        results = []

        pattern = re.compile(follow_pattern) if follow_pattern else None

        while to_visit and len(results) < max_pages:
            url = to_visit.pop(0)

            if url in visited:
                continue

            visited.add(url)

            try:
                content = self.extract(url)
                results.append(content)
                logger.info(f"Crawled {len(results)}/{max_pages}: {url}")

                # Find links to follow (basic implementation)
                if pattern and HAS_BS4:
                    html = self._fetch_html(url)
                    soup = BeautifulSoup(html, 'html.parser')

                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        absolute_url = urljoin(url, href)

                        if absolute_url not in visited and pattern.match(absolute_url):
                            to_visit.append(absolute_url)

                # Rate limiting
                time.sleep(1)

            except Exception as e:
                logger.error(f"Failed to crawl {url}: {e}")
                continue

        logger.info(f"Crawling complete. Extracted {len(results)} pages")
        return results
