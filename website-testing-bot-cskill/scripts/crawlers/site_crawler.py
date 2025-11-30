"""
Site crawler for comprehensive website discovery.

Performs exhaustive crawling to map all pages, resources, and elements.
"""

import asyncio
import time
from typing import Optional, List, Dict, Any, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, urljoin
import re

from ..utils.http_client import HTTPClient, HTTPResponse
from ..utils.html_parser import HTMLParser
from ..utils.validators import URLValidator
from ..utils.constants import (
    DEFAULT_MAX_DEPTH,
    DEFAULT_MAX_PAGES,
    DEFAULT_CRAWL_DELAY,
    SKIP_EXTENSIONS,
    SKIP_URL_PATTERNS
)


@dataclass
class PageInfo:
    """Information about a crawled page."""
    url: str
    title: Optional[str]
    status_code: int
    load_time_ms: float
    content_type: str
    content_length: int
    depth: int
    links_found: int
    images_found: int
    forms_found: int
    scripts_found: int
    stylesheets_found: int
    error: Optional[str] = None
    redirected_from: Optional[str] = None
    redirected_to: Optional[str] = None


@dataclass
class CrawlResult:
    """Complete result of a site crawl."""
    base_url: str
    pages: List[PageInfo]
    all_links: List[Dict[str, Any]]
    all_images: List[Dict[str, Any]]
    all_forms: List[Dict[str, Any]]
    all_scripts: List[Dict[str, Any]]
    all_stylesheets: List[Dict[str, Any]]
    all_buttons: List[Dict[str, Any]]
    all_menus: List[Dict[str, Any]]
    broken_links: List[Dict[str, Any]]
    external_links: List[Dict[str, Any]]
    orphaned_pages: List[str]
    sitemap_found: bool
    robots_txt: Optional[str]
    crawl_duration_seconds: float
    total_pages: int
    total_resources: int
    max_depth_reached: int
    errors: List[Dict[str, Any]] = field(default_factory=list)


class SiteCrawler:
    """
    Comprehensive site crawler for website testing.

    Discovers all pages, resources, and elements through recursive crawling.
    """

    def __init__(
        self,
        max_depth: int = DEFAULT_MAX_DEPTH,
        max_pages: int = DEFAULT_MAX_PAGES,
        crawl_delay: float = DEFAULT_CRAWL_DELAY,
        respect_robots: bool = True,
        follow_external: bool = False,
        timeout: int = 30,
        concurrent_requests: int = 10
    ):
        """
        Initialize the site crawler.

        Args:
            max_depth: Maximum link depth to crawl
            max_pages: Maximum number of pages to crawl
            crawl_delay: Delay between requests in seconds
            respect_robots: Whether to respect robots.txt
            follow_external: Whether to follow external links
            timeout: Request timeout in seconds
            concurrent_requests: Maximum concurrent requests
        """
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.crawl_delay = crawl_delay
        self.respect_robots = respect_robots
        self.follow_external = follow_external
        self.timeout = timeout
        self.concurrent_requests = concurrent_requests

        self.http_client = HTTPClient(timeout=timeout)
        self._visited: Set[str] = set()
        self._queued: Set[str] = set()
        self._robots_rules: Dict[str, List[str]] = {}
        self._pages: List[PageInfo] = []
        self._all_links: List[Dict[str, Any]] = []
        self._all_images: List[Dict[str, Any]] = []
        self._all_forms: List[Dict[str, Any]] = []
        self._all_scripts: List[Dict[str, Any]] = []
        self._all_stylesheets: List[Dict[str, Any]] = []
        self._all_buttons: List[Dict[str, Any]] = []
        self._all_menus: List[Dict[str, Any]] = []
        self._broken_links: List[Dict[str, Any]] = []
        self._external_links: List[Dict[str, Any]] = []
        self._link_sources: Dict[str, List[str]] = {}  # Track where links came from
        self._errors: List[Dict[str, Any]] = []

    def crawl(self, url: str) -> CrawlResult:
        """
        Perform synchronous crawl of a website.

        Args:
            url: Starting URL to crawl

        Returns:
            CrawlResult with all discovered content
        """
        return asyncio.run(self.crawl_async(url))

    async def crawl_async(self, url: str) -> CrawlResult:
        """
        Perform asynchronous crawl of a website.

        Args:
            url: Starting URL to crawl

        Returns:
            CrawlResult with all discovered content
        """
        start_time = time.time()

        # Validate and normalize URL
        validation = URLValidator.validate(url)
        if not validation.is_valid:
            return CrawlResult(
                base_url=url,
                pages=[],
                all_links=[],
                all_images=[],
                all_forms=[],
                all_scripts=[],
                all_stylesheets=[],
                all_buttons=[],
                all_menus=[],
                broken_links=[],
                external_links=[],
                orphaned_pages=[],
                sitemap_found=False,
                robots_txt=None,
                crawl_duration_seconds=0,
                total_pages=0,
                total_resources=0,
                max_depth_reached=0,
                errors=[{"type": "validation", "message": "; ".join(validation.errors)}]
            )

        base_url = validation.normalized_value
        self._base_domain = urlparse(base_url).netloc.lower()

        # Fetch robots.txt if respecting it
        robots_txt = None
        if self.respect_robots:
            robots_txt = await self._fetch_robots_txt(base_url)

        # Check for sitemap
        sitemap_found = await self._check_sitemap(base_url)

        # Start crawling from the base URL
        await self._crawl_page(base_url, depth=0)

        # Process queue with concurrency control
        semaphore = asyncio.Semaphore(self.concurrent_requests)

        while self._queued and len(self._visited) < self.max_pages:
            # Get batch of URLs to process
            batch = list(self._queued)[:self.concurrent_requests]
            for url in batch:
                self._queued.discard(url)

            # Process batch concurrently
            tasks = [self._crawl_with_semaphore(semaphore, url) for url in batch]
            await asyncio.gather(*tasks)

            # Respect crawl delay
            if self.crawl_delay > 0:
                await asyncio.sleep(self.crawl_delay)

        # Identify broken links
        await self._check_broken_links()

        # Identify orphaned pages
        orphaned = self._find_orphaned_pages()

        # Calculate max depth reached
        max_depth = max([p.depth for p in self._pages], default=0)

        crawl_duration = time.time() - start_time

        return CrawlResult(
            base_url=base_url,
            pages=self._pages,
            all_links=self._all_links,
            all_images=self._all_images,
            all_forms=self._all_forms,
            all_scripts=self._all_scripts,
            all_stylesheets=self._all_stylesheets,
            all_buttons=self._all_buttons,
            all_menus=self._all_menus,
            broken_links=self._broken_links,
            external_links=self._external_links,
            orphaned_pages=orphaned,
            sitemap_found=sitemap_found,
            robots_txt=robots_txt,
            crawl_duration_seconds=crawl_duration,
            total_pages=len(self._pages),
            total_resources=len(self._all_images) + len(self._all_scripts) + len(self._all_stylesheets),
            max_depth_reached=max_depth,
            errors=self._errors
        )

    async def _crawl_with_semaphore(self, semaphore: asyncio.Semaphore, url: str) -> None:
        """Crawl a page with semaphore for concurrency control."""
        async with semaphore:
            depth = self._get_depth_for_url(url)
            await self._crawl_page(url, depth)

    async def _crawl_page(self, url: str, depth: int) -> None:
        """
        Crawl a single page and extract all elements.

        Args:
            url: URL to crawl
            depth: Current depth level
        """
        # Skip if already visited or depth exceeded
        if url in self._visited or depth > self.max_depth:
            return

        # Skip if max pages reached
        if len(self._visited) >= self.max_pages:
            return

        # Check robots.txt
        if self.respect_robots and not self._is_allowed_by_robots(url):
            return

        # Skip non-crawlable URLs
        if self._should_skip_url(url):
            return

        self._visited.add(url)

        # Fetch the page
        response = await self.http_client.get_async(url)

        if response.error:
            self._errors.append({
                "url": url,
                "type": "fetch_error",
                "message": response.error
            })
            self._pages.append(PageInfo(
                url=url,
                title=None,
                status_code=0,
                load_time_ms=response.elapsed_ms,
                content_type="",
                content_length=0,
                depth=depth,
                links_found=0,
                images_found=0,
                forms_found=0,
                scripts_found=0,
                stylesheets_found=0,
                error=response.error
            ))
            return

        # Skip non-HTML responses
        content_type = response.content_type
        if content_type and 'text/html' not in content_type:
            return

        # Parse the page
        parser = HTMLParser(response.text, url)

        # Extract all elements
        links = parser.get_all_links()
        images = parser.get_all_images()
        forms = parser.get_all_forms()
        scripts = parser.get_scripts()
        stylesheets = parser.get_stylesheets()
        buttons = parser.get_all_buttons()
        menus = parser.get_all_menus()

        # Store page info
        page_info = PageInfo(
            url=url,
            title=parser.get_title(),
            status_code=response.status_code,
            load_time_ms=response.elapsed_ms,
            content_type=content_type,
            content_length=response.content_length,
            depth=depth,
            links_found=len(links),
            images_found=len(images),
            forms_found=len(forms),
            scripts_found=len(scripts),
            stylesheets_found=len(stylesheets),
            redirected_from=response.redirects[0] if response.redirects else None,
            redirected_to=response.url if response.url != url else None
        )
        self._pages.append(page_info)

        # Process and store links
        for link in links:
            link_data = {
                "href": link.href,
                "text": link.text,
                "source_page": url,
                "css_selector": link.css_selector,
                "line_number": link.line_number,
                "is_external": link.is_external,
                "is_mailto": link.is_mailto,
                "is_tel": link.is_tel,
                "is_anchor": link.is_anchor,
                "target": link.target,
                "rel": link.rel
            }
            self._all_links.append(link_data)

            # Track link sources for orphan detection
            if link.href not in self._link_sources:
                self._link_sources[link.href] = []
            self._link_sources[link.href].append(url)

            # Queue internal links for crawling
            if not link.is_external and not link.is_mailto and not link.is_tel:
                if link.href and not link.is_anchor:
                    self._queue_url(link.href, depth + 1)

            # Track external links
            if link.is_external:
                self._external_links.append(link_data)

        # Process and store images
        for img in images:
            self._all_images.append({
                "src": img.src,
                "alt": img.alt,
                "width": img.width,
                "height": img.height,
                "srcset": img.srcset,
                "loading": img.loading,
                "source_page": url,
                "css_selector": img.css_selector,
                "line_number": img.line_number
            })

        # Process and store forms
        for form in forms:
            self._all_forms.append({
                "action": form.action,
                "method": form.method,
                "id": form.element_id,
                "fields": form.fields,
                "source_page": url,
                "css_selector": form.css_selector,
                "line_number": form.line_number
            })

        # Process and store scripts
        for script in scripts:
            self._all_scripts.append({
                **script,
                "source_page": url
            })

        # Process and store stylesheets
        for stylesheet in stylesheets:
            self._all_stylesheets.append({
                **stylesheet,
                "source_page": url
            })

        # Process and store buttons
        for button in buttons:
            self._all_buttons.append({
                "tag": button.tag,
                "text": button.text,
                "id": button.element_id,
                "classes": button.classes,
                "source_page": url,
                "css_selector": button.css_selector,
                "xpath": button.xpath,
                "line_number": button.line_number,
                "attributes": button.attributes
            })

        # Process and store menus
        for menu in menus:
            self._all_menus.append({
                "tag": menu.tag,
                "id": menu.element_id,
                "classes": menu.classes,
                "source_page": url,
                "css_selector": menu.css_selector,
                "xpath": menu.xpath,
                "line_number": menu.line_number,
                "children_count": menu.children_count
            })

    def _queue_url(self, url: str, depth: int) -> None:
        """Add URL to crawl queue if not already visited/queued."""
        # Normalize URL
        url = url.split('#')[0]  # Remove fragment
        url = url.rstrip('/')  # Normalize trailing slash

        if url and url not in self._visited and url not in self._queued:
            if self._is_same_domain(url):
                self._queued.add(url)
                self._url_depths[url] = depth

    def _get_depth_for_url(self, url: str) -> int:
        """Get the stored depth for a URL."""
        return getattr(self, '_url_depths', {}).get(url, 0)

    def _is_same_domain(self, url: str) -> bool:
        """Check if URL belongs to the same domain."""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower() == self._base_domain
        except Exception:
            return False

    def _should_skip_url(self, url: str) -> bool:
        """Check if URL should be skipped."""
        # Skip binary/non-HTML extensions
        parsed = urlparse(url)
        path = parsed.path.lower()

        for ext in SKIP_EXTENSIONS:
            if path.endswith(ext):
                return True

        # Skip URLs matching skip patterns
        for pattern in SKIP_URL_PATTERNS:
            if re.search(pattern, url, re.I):
                return True

        return False

    async def _fetch_robots_txt(self, base_url: str) -> Optional[str]:
        """Fetch and parse robots.txt."""
        parsed = urlparse(base_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

        response = await self.http_client.get_async(robots_url)

        if response.is_success:
            self._parse_robots_txt(response.text)
            return response.text

        return None

    def _parse_robots_txt(self, content: str) -> None:
        """Parse robots.txt content."""
        disallowed = []
        current_agent = None

        for line in content.split('\n'):
            line = line.strip().lower()

            if line.startswith('user-agent:'):
                agent = line.split(':', 1)[1].strip()
                current_agent = agent

            elif line.startswith('disallow:') and current_agent in ['*', 'websitetestingbot']:
                path = line.split(':', 1)[1].strip()
                if path:
                    disallowed.append(path)

        self._robots_rules['disallowed'] = disallowed

    def _is_allowed_by_robots(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt."""
        if not self._robots_rules.get('disallowed'):
            return True

        parsed = urlparse(url)
        path = parsed.path

        for disallowed in self._robots_rules['disallowed']:
            if path.startswith(disallowed):
                return False

        return True

    async def _check_sitemap(self, base_url: str) -> bool:
        """Check if sitemap.xml exists."""
        parsed = urlparse(base_url)
        sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"

        response = await self.http_client.get_async(sitemap_url)
        return response.is_success

    async def _check_broken_links(self) -> None:
        """Check all internal links for broken status."""
        # Get unique internal link hrefs that weren't crawled as pages
        checked_urls = {p.url for p in self._pages}
        links_to_check = set()

        for link in self._all_links:
            href = link['href']
            if href and not link['is_external'] and not link['is_mailto'] and not link['is_tel']:
                if href not in checked_urls and not href.startswith('#'):
                    links_to_check.add(href)

        # Check each link
        semaphore = asyncio.Semaphore(self.concurrent_requests)

        async def check_link(url: str) -> None:
            async with semaphore:
                status, error = self.http_client.check_url_status(url)
                if error or status >= 400:
                    # Find all occurrences of this link
                    for link in self._all_links:
                        if link['href'] == url:
                            self._broken_links.append({
                                **link,
                                "status_code": status,
                                "error": error
                            })

        tasks = [check_link(url) for url in list(links_to_check)[:100]]  # Limit to 100
        await asyncio.gather(*tasks)

    def _find_orphaned_pages(self) -> List[str]:
        """Find pages that aren't linked from anywhere."""
        orphaned = []
        linked_urls = set(self._link_sources.keys())

        for page in self._pages:
            # Skip the homepage
            if page.depth == 0:
                continue

            if page.url not in linked_urls:
                orphaned.append(page.url)

        return orphaned

    # Initialize url depths tracking
    _url_depths: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize instance variables."""
        self._url_depths = {}
