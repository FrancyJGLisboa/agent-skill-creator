"""
Resource collector for cataloging all website assets.

Collects and categorizes images, scripts, stylesheets, fonts, and media.
"""

import re
from typing import Optional, List, Dict, Any, Set
from dataclasses import dataclass, field
from urllib.parse import urlparse, urljoin

from ..utils.http_client import HTTPClient


@dataclass
class ResourceInfo:
    """Information about a collected resource."""
    url: str
    type: str  # image, script, stylesheet, font, media, other
    source_page: str
    status_code: int = 0
    file_size: int = 0
    content_type: Optional[str] = None
    load_time_ms: float = 0
    error: Optional[str] = None
    is_external: bool = False
    is_inline: bool = False
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceInventory:
    """Complete inventory of all website resources."""
    images: List[ResourceInfo]
    scripts: List[ResourceInfo]
    stylesheets: List[ResourceInfo]
    fonts: List[ResourceInfo]
    media: List[ResourceInfo]
    other: List[ResourceInfo]
    total_count: int
    total_size_bytes: int
    external_count: int
    broken_count: int
    by_domain: Dict[str, int]
    by_type: Dict[str, int]


class ResourceCollector:
    """
    Collector for all website resources.

    Catalogs every asset loaded by the website including images,
    scripts, stylesheets, fonts, and media files.
    """

    # Resource type mappings
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.ico', '.bmp', '.avif'}
    SCRIPT_EXTENSIONS = {'.js', '.mjs'}
    STYLE_EXTENSIONS = {'.css'}
    FONT_EXTENSIONS = {'.woff', '.woff2', '.ttf', '.otf', '.eot'}
    MEDIA_EXTENSIONS = {'.mp4', '.webm', '.ogg', '.mp3', '.wav', '.m4a'}

    MIME_TYPE_MAP = {
        'image': ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml', 'image/x-icon'],
        'script': ['application/javascript', 'text/javascript', 'application/x-javascript'],
        'stylesheet': ['text/css'],
        'font': ['font/woff', 'font/woff2', 'font/ttf', 'font/otf', 'application/font-woff'],
        'media': ['video/mp4', 'video/webm', 'audio/mpeg', 'audio/ogg', 'audio/wav']
    }

    def __init__(self, base_url: str, http_client: Optional[HTTPClient] = None):
        """
        Initialize resource collector.

        Args:
            base_url: Base URL for resolving relative paths
            http_client: HTTP client for resource checking
        """
        self.base_url = base_url
        self.http_client = http_client or HTTPClient()
        self._base_domain = urlparse(base_url).netloc.lower()
        self._collected: Dict[str, ResourceInfo] = {}

    def collect_from_page(
        self,
        page_url: str,
        images: List[Dict[str, Any]],
        scripts: List[Dict[str, Any]],
        stylesheets: List[Dict[str, Any]]
    ) -> None:
        """
        Collect resources from parsed page data.

        Args:
            page_url: URL of the source page
            images: List of image data from parser
            scripts: List of script data from parser
            stylesheets: List of stylesheet data from parser
        """
        # Process images
        for img in images:
            src = img.get('src', '')
            if src and not src.startswith('data:'):
                url = self._resolve_url(src, page_url)
                self._add_resource(url, 'image', page_url, img)

        # Process scripts
        for script in scripts:
            src = script.get('src', '')
            if src:
                url = self._resolve_url(src, page_url)
                self._add_resource(url, 'script', page_url, script)
            elif script.get('inline'):
                # Track inline scripts
                self._add_inline_resource('script', page_url, script)

        # Process stylesheets
        for style in stylesheets:
            href = style.get('href', '')
            if href:
                url = self._resolve_url(href, page_url)
                self._add_resource(url, 'stylesheet', page_url, style)
            elif style.get('inline'):
                self._add_inline_resource('stylesheet', page_url, style)

    def collect_from_css(self, css_url: str, css_content: str, page_url: str) -> None:
        """
        Extract resources referenced in CSS content.

        Args:
            css_url: URL of the CSS file
            css_content: CSS content to parse
            page_url: URL of the page that referenced the CSS
        """
        # Extract url() references
        url_pattern = r'url\(["\']?([^"\')\s]+)["\']?\)'

        for match in re.finditer(url_pattern, css_content, re.I):
            url = match.group(1)

            # Skip data URIs
            if url.startswith('data:'):
                continue

            # Resolve relative to CSS file location
            resolved = self._resolve_url(url, css_url)
            resource_type = self._detect_type_from_url(resolved)

            self._add_resource(resolved, resource_type, page_url, {
                'referenced_from': css_url,
                'in_css': True
            })

        # Extract @font-face src
        font_face_pattern = r'@font-face\s*\{[^}]*src:\s*([^;]+)'

        for match in re.finditer(font_face_pattern, css_content, re.I):
            src_value = match.group(1)

            # Extract URLs from src value
            for url_match in re.finditer(url_pattern, src_value):
                url = url_match.group(1)
                if not url.startswith('data:'):
                    resolved = self._resolve_url(url, css_url)
                    self._add_resource(resolved, 'font', page_url, {
                        'referenced_from': css_url,
                        'font_face': True
                    })

    def _add_resource(
        self,
        url: str,
        resource_type: str,
        source_page: str,
        attributes: Dict[str, Any]
    ) -> None:
        """Add a resource to the collection."""
        # Normalize URL
        url = url.split('#')[0]  # Remove fragment
        url = url.split('?')[0]  # Remove query string for deduplication

        if not url:
            return

        # Update existing or add new
        if url in self._collected:
            # Just update source pages if already collected
            return

        is_external = not self._is_same_domain(url)

        self._collected[url] = ResourceInfo(
            url=url,
            type=resource_type,
            source_page=source_page,
            is_external=is_external,
            is_inline=False,
            attributes=attributes
        )

    def _add_inline_resource(
        self,
        resource_type: str,
        source_page: str,
        attributes: Dict[str, Any]
    ) -> None:
        """Track inline resources (inline scripts/styles)."""
        # Generate a unique key for inline resources
        key = f"inline_{resource_type}_{source_page}_{len(self._collected)}"

        self._collected[key] = ResourceInfo(
            url=key,
            type=resource_type,
            source_page=source_page,
            is_external=False,
            is_inline=True,
            attributes=attributes
        )

    def _resolve_url(self, url: str, base: str) -> str:
        """Resolve a relative URL against a base."""
        if url.startswith(('http://', 'https://', '//')):
            if url.startswith('//'):
                return 'https:' + url
            return url
        return urljoin(base, url)

    def _is_same_domain(self, url: str) -> bool:
        """Check if URL belongs to the same domain."""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower() == self._base_domain
        except Exception:
            return False

    def _detect_type_from_url(self, url: str) -> str:
        """Detect resource type from URL extension."""
        parsed = urlparse(url)
        path = parsed.path.lower()

        for ext in self.IMAGE_EXTENSIONS:
            if path.endswith(ext):
                return 'image'

        for ext in self.SCRIPT_EXTENSIONS:
            if path.endswith(ext):
                return 'script'

        for ext in self.STYLE_EXTENSIONS:
            if path.endswith(ext):
                return 'stylesheet'

        for ext in self.FONT_EXTENSIONS:
            if path.endswith(ext):
                return 'font'

        for ext in self.MEDIA_EXTENSIONS:
            if path.endswith(ext):
                return 'media'

        return 'other'

    async def verify_resources(self, sample_size: int = 100) -> None:
        """
        Verify resources exist and collect size/timing data.

        Args:
            sample_size: Maximum number of resources to verify
        """
        resources_to_check = [r for r in self._collected.values() if not r.is_inline][:sample_size]

        for resource in resources_to_check:
            response = await self.http_client.get_async(resource.url)

            resource.status_code = response.status_code
            resource.file_size = response.content_length
            resource.content_type = response.content_type
            resource.load_time_ms = response.elapsed_ms
            resource.error = response.error

    def get_inventory(self) -> ResourceInventory:
        """
        Get complete resource inventory.

        Returns:
            ResourceInventory with all collected resources
        """
        images = []
        scripts = []
        stylesheets = []
        fonts = []
        media = []
        other = []

        total_size = 0
        external_count = 0
        broken_count = 0
        by_domain: Dict[str, int] = {}
        by_type: Dict[str, int] = {}

        for resource in self._collected.values():
            # Categorize by type
            if resource.type == 'image':
                images.append(resource)
            elif resource.type == 'script':
                scripts.append(resource)
            elif resource.type == 'stylesheet':
                stylesheets.append(resource)
            elif resource.type == 'font':
                fonts.append(resource)
            elif resource.type == 'media':
                media.append(resource)
            else:
                other.append(resource)

            # Track totals
            total_size += resource.file_size or 0

            if resource.is_external:
                external_count += 1

            if resource.error or resource.status_code >= 400:
                broken_count += 1

            # Track by domain
            try:
                domain = urlparse(resource.url).netloc
                by_domain[domain] = by_domain.get(domain, 0) + 1
            except Exception:
                pass

            # Track by type
            by_type[resource.type] = by_type.get(resource.type, 0) + 1

        return ResourceInventory(
            images=images,
            scripts=scripts,
            stylesheets=stylesheets,
            fonts=fonts,
            media=media,
            other=other,
            total_count=len(self._collected),
            total_size_bytes=total_size,
            external_count=external_count,
            broken_count=broken_count,
            by_domain=by_domain,
            by_type=by_type
        )

    def get_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """
        Generate resource optimization suggestions.

        Returns:
            List of optimization suggestions
        """
        suggestions = []
        inventory = self.get_inventory()

        # Check for large images
        large_images = [img for img in inventory.images if img.file_size > 500000]  # > 500KB
        if large_images:
            suggestions.append({
                'type': 'image_optimization',
                'severity': 'high',
                'message': f'{len(large_images)} images are over 500KB and should be optimized',
                'resources': [img.url for img in large_images[:5]]
            })

        # Check for too many scripts
        if len(inventory.scripts) > 20:
            suggestions.append({
                'type': 'script_bundling',
                'severity': 'medium',
                'message': f'{len(inventory.scripts)} JavaScript files detected - consider bundling',
                'count': len(inventory.scripts)
            })

        # Check for too many stylesheets
        if len(inventory.stylesheets) > 10:
            suggestions.append({
                'type': 'css_bundling',
                'severity': 'medium',
                'message': f'{len(inventory.stylesheets)} CSS files detected - consider bundling',
                'count': len(inventory.stylesheets)
            })

        # Check for external dependencies
        if inventory.external_count > 20:
            suggestions.append({
                'type': 'external_dependencies',
                'severity': 'low',
                'message': f'{inventory.external_count} external resources - may impact reliability',
                'count': inventory.external_count
            })

        # Check for broken resources
        if inventory.broken_count > 0:
            suggestions.append({
                'type': 'broken_resources',
                'severity': 'high',
                'message': f'{inventory.broken_count} broken/missing resources detected',
                'count': inventory.broken_count
            })

        # Check total page weight
        total_mb = inventory.total_size_bytes / (1024 * 1024)
        if total_mb > 3:
            suggestions.append({
                'type': 'page_weight',
                'severity': 'high',
                'message': f'Total resource size is {total_mb:.1f}MB - target is under 3MB',
                'size_mb': total_mb
            })

        return suggestions
