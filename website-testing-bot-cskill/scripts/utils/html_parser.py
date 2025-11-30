"""
HTML parsing utilities for element extraction and analysis.

Provides DOM traversal, element finding, and attribute extraction.
"""

import re
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from html.parser import HTMLParser as BaseHTMLParser
from urllib.parse import urljoin

try:
    from bs4 import BeautifulSoup, Tag
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


@dataclass
class DOMElement:
    """Represents a DOM element with its properties."""
    tag: str
    attributes: Dict[str, str]
    text: str
    inner_html: str
    outer_html: str
    css_selector: str
    xpath: str
    line_number: int
    parent_tag: Optional[str] = None
    children_count: int = 0
    classes: List[str] = field(default_factory=list)
    element_id: Optional[str] = None

    @property
    def has_id(self) -> bool:
        return bool(self.element_id)

    @property
    def has_classes(self) -> bool:
        return len(self.classes) > 0


@dataclass
class ParsedForm:
    """Represents a parsed HTML form."""
    action: str
    method: str
    element_id: Optional[str]
    css_selector: str
    fields: List[Dict[str, Any]]
    submit_button: Optional[DOMElement]
    line_number: int


@dataclass
class ParsedLink:
    """Represents a parsed anchor link."""
    href: str
    text: str
    title: Optional[str]
    target: Optional[str]
    rel: Optional[str]
    css_selector: str
    line_number: int
    is_external: bool = False
    is_mailto: bool = False
    is_tel: bool = False
    is_anchor: bool = False


@dataclass
class ParsedImage:
    """Represents a parsed image element."""
    src: str
    alt: Optional[str]
    width: Optional[str]
    height: Optional[str]
    srcset: Optional[str]
    loading: Optional[str]
    css_selector: str
    line_number: int


class HTMLParser:
    """
    Comprehensive HTML parser for extracting elements and analyzing structure.

    Uses BeautifulSoup when available, falls back to basic parsing otherwise.
    """

    def __init__(self, html: str, base_url: str = ''):
        """
        Initialize parser with HTML content.

        Args:
            html: HTML string to parse
            base_url: Base URL for resolving relative links
        """
        self.html = html
        self.base_url = base_url
        self._soup = None
        self._line_map = {}

        if BS4_AVAILABLE:
            self._soup = BeautifulSoup(html, 'html.parser')
            self._build_line_map()

    def _build_line_map(self) -> None:
        """Build a map of element positions to line numbers."""
        lines = self.html.split('\n')
        current_pos = 0

        for line_num, line in enumerate(lines, 1):
            for i, char in enumerate(line):
                self._line_map[current_pos + i] = line_num
            current_pos += len(line) + 1  # +1 for newline

    def _get_line_number(self, element) -> int:
        """Get the line number for a BeautifulSoup element."""
        if hasattr(element, 'sourceline'):
            return element.sourceline or 0
        return 0

    def _get_css_selector(self, element) -> str:
        """Generate a CSS selector for an element."""
        if not BS4_AVAILABLE or not isinstance(element, Tag):
            return ''

        parts = []
        current = element

        while current and current.name:
            selector = current.name

            # Add ID if present
            if current.get('id'):
                selector += f"#{current.get('id')}"
                parts.insert(0, selector)
                break

            # Add classes if present
            classes = current.get('class', [])
            if classes:
                selector += '.' + '.'.join(classes[:2])  # Limit to first 2 classes

            # Add nth-child if needed for uniqueness
            if current.parent:
                siblings = [s for s in current.parent.children
                           if isinstance(s, Tag) and s.name == current.name]
                if len(siblings) > 1:
                    index = siblings.index(current) + 1
                    selector += f":nth-child({index})"

            parts.insert(0, selector)
            current = current.parent

        return ' > '.join(parts)

    def _get_xpath(self, element) -> str:
        """Generate an XPath for an element."""
        if not BS4_AVAILABLE or not isinstance(element, Tag):
            return ''

        parts = []
        current = element

        while current and current.name:
            xpath_part = current.name

            # Add ID predicate if present
            if current.get('id'):
                xpath_part = f"{current.name}[@id='{current.get('id')}']"
                parts.insert(0, xpath_part)
                break

            # Add position predicate
            if current.parent:
                siblings = [s for s in current.parent.children
                           if isinstance(s, Tag) and s.name == current.name]
                if len(siblings) > 1:
                    index = siblings.index(current) + 1
                    xpath_part += f"[{index}]"

            parts.insert(0, xpath_part)
            current = current.parent

        return '//' + '/'.join(parts) if parts else ''

    def _resolve_url(self, url: str) -> str:
        """Resolve a relative URL to absolute."""
        if not url or url.startswith(('http://', 'https://', 'data:', 'javascript:')):
            return url
        return urljoin(self.base_url, url)

    def get_all_links(self) -> List[ParsedLink]:
        """
        Extract all anchor links from the HTML.

        Returns:
            List of ParsedLink objects
        """
        if not BS4_AVAILABLE:
            return self._fallback_get_links()

        links = []
        for a in self._soup.find_all('a', href=True):
            href = a.get('href', '')
            resolved_href = self._resolve_url(href)

            link = ParsedLink(
                href=resolved_href,
                text=a.get_text(strip=True),
                title=a.get('title'),
                target=a.get('target'),
                rel=a.get('rel', [None])[0] if a.get('rel') else None,
                css_selector=self._get_css_selector(a),
                line_number=self._get_line_number(a),
                is_external=not self._is_internal_url(resolved_href),
                is_mailto=href.startswith('mailto:'),
                is_tel=href.startswith('tel:'),
                is_anchor=href.startswith('#')
            )
            links.append(link)

        return links

    def get_all_images(self) -> List[ParsedImage]:
        """
        Extract all images from the HTML.

        Returns:
            List of ParsedImage objects
        """
        if not BS4_AVAILABLE:
            return self._fallback_get_images()

        images = []
        for img in self._soup.find_all('img'):
            src = img.get('src', '')
            resolved_src = self._resolve_url(src)

            image = ParsedImage(
                src=resolved_src,
                alt=img.get('alt'),
                width=img.get('width'),
                height=img.get('height'),
                srcset=img.get('srcset'),
                loading=img.get('loading'),
                css_selector=self._get_css_selector(img),
                line_number=self._get_line_number(img)
            )
            images.append(image)

        return images

    def get_all_buttons(self) -> List[DOMElement]:
        """
        Extract all buttons from the HTML.

        Returns:
            List of DOMElement objects for buttons
        """
        if not BS4_AVAILABLE:
            return []

        buttons = []

        # <button> elements
        for btn in self._soup.find_all('button'):
            buttons.append(self._element_to_dom(btn))

        # <input type="submit|button|reset">
        for inp in self._soup.find_all('input', type=re.compile(r'submit|button|reset', re.I)):
            buttons.append(self._element_to_dom(inp))

        # Elements with role="button"
        for elem in self._soup.find_all(attrs={'role': 'button'}):
            if elem.name not in ['button', 'input']:
                buttons.append(self._element_to_dom(elem))

        return buttons

    def get_all_forms(self) -> List[ParsedForm]:
        """
        Extract all forms from the HTML.

        Returns:
            List of ParsedForm objects
        """
        if not BS4_AVAILABLE:
            return []

        forms = []

        for form in self._soup.find_all('form'):
            fields = []

            # Get all input fields
            for inp in form.find_all(['input', 'textarea', 'select']):
                field = {
                    'tag': inp.name,
                    'type': inp.get('type', 'text') if inp.name == 'input' else inp.name,
                    'name': inp.get('name'),
                    'id': inp.get('id'),
                    'required': inp.has_attr('required'),
                    'placeholder': inp.get('placeholder'),
                    'label': self._find_label_for(inp),
                    'css_selector': self._get_css_selector(inp)
                }
                fields.append(field)

            # Find submit button
            submit_btn = form.find(['button', 'input'],
                                   type=re.compile(r'submit', re.I))

            parsed_form = ParsedForm(
                action=self._resolve_url(form.get('action', '')),
                method=form.get('method', 'GET').upper(),
                element_id=form.get('id'),
                css_selector=self._get_css_selector(form),
                fields=fields,
                submit_button=self._element_to_dom(submit_btn) if submit_btn else None,
                line_number=self._get_line_number(form)
            )
            forms.append(parsed_form)

        return forms

    def get_all_menus(self) -> List[DOMElement]:
        """
        Extract all navigation menus from the HTML.

        Returns:
            List of DOMElement objects for nav elements
        """
        if not BS4_AVAILABLE:
            return []

        menus = []

        # <nav> elements
        for nav in self._soup.find_all('nav'):
            menus.append(self._element_to_dom(nav))

        # Elements with role="navigation"
        for elem in self._soup.find_all(attrs={'role': 'navigation'}):
            if elem.name != 'nav':
                menus.append(self._element_to_dom(elem))

        # Common menu class patterns
        menu_patterns = ['menu', 'nav', 'navigation', 'navbar', 'header-menu']
        for pattern in menu_patterns:
            for elem in self._soup.find_all(class_=re.compile(pattern, re.I)):
                if elem not in [m for m in menus]:
                    dom = self._element_to_dom(elem)
                    if dom not in menus:
                        menus.append(dom)

        return menus

    def get_headings(self) -> List[DOMElement]:
        """
        Extract all heading elements (h1-h6).

        Returns:
            List of DOMElement objects for headings
        """
        if not BS4_AVAILABLE:
            return []

        headings = []
        for h in self._soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            headings.append(self._element_to_dom(h))
        return headings

    def get_meta_tags(self) -> Dict[str, str]:
        """
        Extract all meta tags.

        Returns:
            Dictionary of meta tag name/property to content
        """
        if not BS4_AVAILABLE:
            return {}

        meta = {}
        for tag in self._soup.find_all('meta'):
            name = tag.get('name') or tag.get('property') or tag.get('http-equiv')
            content = tag.get('content')
            if name and content:
                meta[name] = content

        return meta

    def get_title(self) -> Optional[str]:
        """Get the page title."""
        if not BS4_AVAILABLE:
            match = re.search(r'<title[^>]*>([^<]+)</title>', self.html, re.I)
            return match.group(1).strip() if match else None

        title = self._soup.find('title')
        return title.get_text(strip=True) if title else None

    def get_language(self) -> Optional[str]:
        """Get the page language from html lang attribute."""
        if not BS4_AVAILABLE:
            match = re.search(r'<html[^>]+lang=["\']([^"\']+)["\']', self.html, re.I)
            return match.group(1) if match else None

        html = self._soup.find('html')
        return html.get('lang') if html else None

    def get_scripts(self) -> List[Dict[str, Any]]:
        """
        Extract all script references.

        Returns:
            List of dictionaries with script info
        """
        if not BS4_AVAILABLE:
            return []

        scripts = []
        for script in self._soup.find_all('script'):
            scripts.append({
                'src': self._resolve_url(script.get('src', '')),
                'type': script.get('type'),
                'async': script.has_attr('async'),
                'defer': script.has_attr('defer'),
                'inline': not script.get('src'),
                'line_number': self._get_line_number(script)
            })
        return scripts

    def get_stylesheets(self) -> List[Dict[str, Any]]:
        """
        Extract all stylesheet references.

        Returns:
            List of dictionaries with stylesheet info
        """
        if not BS4_AVAILABLE:
            return []

        stylesheets = []

        # <link rel="stylesheet">
        for link in self._soup.find_all('link', rel='stylesheet'):
            stylesheets.append({
                'href': self._resolve_url(link.get('href', '')),
                'media': link.get('media'),
                'line_number': self._get_line_number(link)
            })

        # <style> tags
        for style in self._soup.find_all('style'):
            stylesheets.append({
                'href': None,
                'inline': True,
                'content_length': len(style.get_text()),
                'line_number': self._get_line_number(style)
            })

        return stylesheets

    def _element_to_dom(self, element) -> DOMElement:
        """Convert a BeautifulSoup element to DOMElement."""
        if not element:
            return None

        return DOMElement(
            tag=element.name,
            attributes=dict(element.attrs) if element.attrs else {},
            text=element.get_text(strip=True),
            inner_html=element.decode_contents() if hasattr(element, 'decode_contents') else '',
            outer_html=str(element),
            css_selector=self._get_css_selector(element),
            xpath=self._get_xpath(element),
            line_number=self._get_line_number(element),
            parent_tag=element.parent.name if element.parent else None,
            children_count=len([c for c in element.children if isinstance(c, Tag)]),
            classes=element.get('class', []),
            element_id=element.get('id')
        )

    def _find_label_for(self, element) -> Optional[str]:
        """Find the label text for a form element."""
        if not BS4_AVAILABLE:
            return None

        elem_id = element.get('id')
        if elem_id:
            label = self._soup.find('label', attrs={'for': elem_id})
            if label:
                return label.get_text(strip=True)

        # Check for wrapping label
        parent = element.find_parent('label')
        if parent:
            return parent.get_text(strip=True)

        return None

    def _is_internal_url(self, url: str) -> bool:
        """Check if URL is internal to base_url."""
        if not url or url.startswith('#'):
            return True
        if url.startswith(('mailto:', 'tel:', 'javascript:')):
            return False
        if not self.base_url:
            return True

        from urllib.parse import urlparse
        base_domain = urlparse(self.base_url).netloc.lower()
        url_domain = urlparse(url).netloc.lower()

        return not url_domain or url_domain == base_domain

    def _fallback_get_links(self) -> List[ParsedLink]:
        """Fallback link extraction without BeautifulSoup."""
        links = []
        pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>'

        for match in re.finditer(pattern, self.html, re.I):
            href = match.group(1)
            text = match.group(2).strip()

            links.append(ParsedLink(
                href=self._resolve_url(href),
                text=text,
                title=None,
                target=None,
                rel=None,
                css_selector='',
                line_number=0,
                is_external=not self._is_internal_url(href),
                is_mailto=href.startswith('mailto:'),
                is_tel=href.startswith('tel:'),
                is_anchor=href.startswith('#')
            ))

        return links

    def _fallback_get_images(self) -> List[ParsedImage]:
        """Fallback image extraction without BeautifulSoup."""
        images = []
        pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'

        for match in re.finditer(pattern, self.html, re.I):
            src = match.group(1)
            full_tag = match.group(0)

            # Try to extract alt
            alt_match = re.search(r'alt=["\']([^"\']*)["\']', full_tag, re.I)
            alt = alt_match.group(1) if alt_match else None

            images.append(ParsedImage(
                src=self._resolve_url(src),
                alt=alt,
                width=None,
                height=None,
                srcset=None,
                loading=None,
                css_selector='',
                line_number=0
            ))

        return images
