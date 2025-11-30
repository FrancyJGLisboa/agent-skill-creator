"""
Page parser for detailed element extraction and analysis.

Provides deep parsing of individual pages for testing purposes.
"""

from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
import re

from ..utils.html_parser import HTMLParser, DOMElement, ParsedForm, ParsedLink, ParsedImage


@dataclass
class ParsedPage:
    """Complete parsed representation of a web page."""
    url: str
    title: Optional[str]
    language: Optional[str]
    meta_tags: Dict[str, str]
    headings: List[DOMElement]
    links: List[ParsedLink]
    images: List[ParsedImage]
    forms: List[ParsedForm]
    buttons: List[DOMElement]
    menus: List[DOMElement]
    scripts: List[Dict[str, Any]]
    stylesheets: List[Dict[str, Any]]
    iframes: List[Dict[str, Any]]
    videos: List[Dict[str, Any]]
    interactive_elements: List[DOMElement]
    aria_elements: List[DOMElement]
    landmark_regions: List[DOMElement]
    skip_links: List[DOMElement]
    focus_order: List[DOMElement]


class PageParser:
    """
    Deep page parser for comprehensive element extraction.

    Extracts all elements needed for thorough testing.
    """

    def __init__(self, html: str, url: str):
        """
        Initialize page parser.

        Args:
            html: HTML content to parse
            url: URL of the page (for resolving relative links)
        """
        self.html = html
        self.url = url
        self._parser = HTMLParser(html, url)

    def parse(self) -> ParsedPage:
        """
        Perform complete page parsing.

        Returns:
            ParsedPage with all extracted elements
        """
        return ParsedPage(
            url=self.url,
            title=self._parser.get_title(),
            language=self._parser.get_language(),
            meta_tags=self._parser.get_meta_tags(),
            headings=self._parser.get_headings(),
            links=self._parser.get_all_links(),
            images=self._parser.get_all_images(),
            forms=self._parser.get_all_forms(),
            buttons=self._parser.get_all_buttons(),
            menus=self._parser.get_all_menus(),
            scripts=self._parser.get_scripts(),
            stylesheets=self._parser.get_stylesheets(),
            iframes=self._get_iframes(),
            videos=self._get_videos(),
            interactive_elements=self._get_interactive_elements(),
            aria_elements=self._get_aria_elements(),
            landmark_regions=self._get_landmark_regions(),
            skip_links=self._get_skip_links(),
            focus_order=self._get_focus_order()
        )

    def _get_iframes(self) -> List[Dict[str, Any]]:
        """Extract all iframe elements."""
        iframes = []

        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(self.html, 'html.parser')

            for iframe in soup.find_all('iframe'):
                iframes.append({
                    'src': iframe.get('src', ''),
                    'title': iframe.get('title'),
                    'width': iframe.get('width'),
                    'height': iframe.get('height'),
                    'sandbox': iframe.get('sandbox'),
                    'loading': iframe.get('loading'),
                    'allow': iframe.get('allow'),
                    'has_title': bool(iframe.get('title'))
                })
        except ImportError:
            # Fallback regex extraction
            pattern = r'<iframe[^>]+src=["\']([^"\']+)["\'][^>]*>'
            for match in re.finditer(pattern, self.html, re.I):
                iframes.append({
                    'src': match.group(1),
                    'title': None,
                    'has_title': False
                })

        return iframes

    def _get_videos(self) -> List[Dict[str, Any]]:
        """Extract all video elements."""
        videos = []

        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(self.html, 'html.parser')

            # HTML5 video elements
            for video in soup.find_all('video'):
                sources = []
                for source in video.find_all('source'):
                    sources.append({
                        'src': source.get('src'),
                        'type': source.get('type')
                    })

                tracks = []
                for track in video.find_all('track'):
                    tracks.append({
                        'kind': track.get('kind'),
                        'src': track.get('src'),
                        'srclang': track.get('srclang'),
                        'label': track.get('label')
                    })

                videos.append({
                    'type': 'html5',
                    'src': video.get('src'),
                    'sources': sources,
                    'tracks': tracks,
                    'has_captions': any(t.get('kind') == 'captions' for t in tracks),
                    'poster': video.get('poster'),
                    'controls': video.has_attr('controls'),
                    'autoplay': video.has_attr('autoplay'),
                    'muted': video.has_attr('muted')
                })

            # YouTube embeds
            for iframe in soup.find_all('iframe'):
                src = iframe.get('src', '')
                if 'youtube.com' in src or 'youtu.be' in src:
                    videos.append({
                        'type': 'youtube',
                        'src': src,
                        'title': iframe.get('title')
                    })

            # Vimeo embeds
            for iframe in soup.find_all('iframe'):
                src = iframe.get('src', '')
                if 'vimeo.com' in src:
                    videos.append({
                        'type': 'vimeo',
                        'src': src,
                        'title': iframe.get('title')
                    })

        except ImportError:
            pass

        return videos

    def _get_interactive_elements(self) -> List[DOMElement]:
        """Extract interactive elements (accordions, tabs, sliders, etc.)."""
        elements = []

        try:
            from bs4 import BeautifulSoup, Tag
            soup = BeautifulSoup(self.html, 'html.parser')

            # Common interactive patterns
            interactive_patterns = [
                # Accordions
                {'class': re.compile(r'accordion|collapse|expandable', re.I)},
                {'role': 'tablist'},
                {'role': 'tab'},
                {'role': 'tabpanel'},

                # Sliders/Carousels
                {'class': re.compile(r'carousel|slider|swiper|slick', re.I)},
                {'role': 'slider'},

                # Modals
                {'class': re.compile(r'modal|dialog|popup|overlay', re.I)},
                {'role': 'dialog'},
                {'role': 'alertdialog'},

                # Dropdowns
                {'class': re.compile(r'dropdown|select|combobox', re.I)},
                {'role': 'listbox'},
                {'role': 'combobox'},
                {'role': 'menu'},
                {'role': 'menubar'},

                # Tooltips
                {'class': re.compile(r'tooltip|popover', re.I)},
                {'role': 'tooltip'},

                # Progress/Loading
                {'role': 'progressbar'},
                {'class': re.compile(r'progress|loading|spinner', re.I)},

                # Toggles
                {'role': 'switch'},
                {'class': re.compile(r'toggle|switch', re.I)}
            ]

            for pattern in interactive_patterns:
                for elem in soup.find_all(attrs=pattern):
                    if isinstance(elem, Tag):
                        elements.append(self._tag_to_dom_element(elem))

        except ImportError:
            pass

        return elements

    def _get_aria_elements(self) -> List[DOMElement]:
        """Extract elements with ARIA attributes."""
        elements = []

        try:
            from bs4 import BeautifulSoup, Tag
            soup = BeautifulSoup(self.html, 'html.parser')

            # Find all elements with aria-* attributes
            for elem in soup.find_all(True):
                if isinstance(elem, Tag):
                    aria_attrs = {k: v for k, v in elem.attrs.items()
                                if k.startswith('aria-') or k == 'role'}
                    if aria_attrs:
                        elements.append(self._tag_to_dom_element(elem))

        except ImportError:
            pass

        return elements

    def _get_landmark_regions(self) -> List[DOMElement]:
        """Extract ARIA landmark regions."""
        elements = []

        try:
            from bs4 import BeautifulSoup, Tag
            soup = BeautifulSoup(self.html, 'html.parser')

            # HTML5 landmark elements
            landmark_tags = ['header', 'nav', 'main', 'aside', 'footer', 'section', 'article']
            for tag in landmark_tags:
                for elem in soup.find_all(tag):
                    elements.append(self._tag_to_dom_element(elem))

            # ARIA landmark roles
            landmark_roles = [
                'banner', 'navigation', 'main', 'complementary',
                'contentinfo', 'region', 'search', 'form'
            ]
            for role in landmark_roles:
                for elem in soup.find_all(attrs={'role': role}):
                    if isinstance(elem, Tag):
                        elements.append(self._tag_to_dom_element(elem))

        except ImportError:
            pass

        return elements

    def _get_skip_links(self) -> List[DOMElement]:
        """Extract skip navigation links."""
        elements = []

        try:
            from bs4 import BeautifulSoup, Tag
            soup = BeautifulSoup(self.html, 'html.parser')

            # Common skip link patterns
            skip_patterns = [
                {'class': re.compile(r'skip|bypass|jump', re.I)},
                {'id': re.compile(r'skip|bypass|jump', re.I)}
            ]

            for pattern in skip_patterns:
                for elem in soup.find_all('a', attrs=pattern):
                    if isinstance(elem, Tag):
                        href = elem.get('href', '')
                        if href.startswith('#'):
                            elements.append(self._tag_to_dom_element(elem))

            # Also check for links that go to #main, #content, etc.
            for a in soup.find_all('a', href=re.compile(r'^#(main|content|maincontent)', re.I)):
                if isinstance(a, Tag):
                    elements.append(self._tag_to_dom_element(a))

        except ImportError:
            pass

        return elements

    def _get_focus_order(self) -> List[DOMElement]:
        """Extract elements in tab/focus order."""
        elements = []

        try:
            from bs4 import BeautifulSoup, Tag
            soup = BeautifulSoup(self.html, 'html.parser')

            # Naturally focusable elements
            focusable_tags = ['a', 'button', 'input', 'select', 'textarea']

            # Get all focusable elements
            focusable = []
            for tag in focusable_tags:
                for elem in soup.find_all(tag):
                    if isinstance(elem, Tag):
                        tabindex = elem.get('tabindex', '0')
                        try:
                            ti = int(tabindex)
                        except (ValueError, TypeError):
                            ti = 0

                        # Skip tabindex=-1 (not in tab order)
                        if ti >= 0:
                            focusable.append((ti, elem))

            # Also get elements with explicit tabindex
            for elem in soup.find_all(attrs={'tabindex': True}):
                if isinstance(elem, Tag) and elem.name not in focusable_tags:
                    tabindex = elem.get('tabindex', '0')
                    try:
                        ti = int(tabindex)
                    except (ValueError, TypeError):
                        ti = 0

                    if ti >= 0:
                        focusable.append((ti, elem))

            # Sort by tabindex (positive first, then 0s in DOM order)
            positive = [(ti, e) for ti, e in focusable if ti > 0]
            zero = [(ti, e) for ti, e in focusable if ti == 0]

            positive.sort(key=lambda x: x[0])
            sorted_elements = positive + zero

            for _, elem in sorted_elements:
                elements.append(self._tag_to_dom_element(elem))

        except ImportError:
            pass

        return elements

    def _tag_to_dom_element(self, tag) -> DOMElement:
        """Convert a BeautifulSoup tag to DOMElement."""
        from bs4 import Tag

        if not isinstance(tag, Tag):
            return None

        return DOMElement(
            tag=tag.name,
            attributes=dict(tag.attrs) if tag.attrs else {},
            text=tag.get_text(strip=True)[:100],  # Limit text length
            inner_html=tag.decode_contents()[:500] if hasattr(tag, 'decode_contents') else '',
            outer_html=str(tag)[:1000],
            css_selector=self._get_css_selector(tag),
            xpath=self._get_xpath(tag),
            line_number=tag.sourceline if hasattr(tag, 'sourceline') else 0,
            parent_tag=tag.parent.name if tag.parent else None,
            children_count=len([c for c in tag.children if isinstance(c, Tag)]),
            classes=tag.get('class', []),
            element_id=tag.get('id')
        )

    def _get_css_selector(self, element) -> str:
        """Generate a CSS selector for an element."""
        from bs4 import Tag

        parts = []
        current = element

        while current and isinstance(current, Tag) and current.name:
            selector = current.name

            if current.get('id'):
                selector += f"#{current.get('id')}"
                parts.insert(0, selector)
                break

            classes = current.get('class', [])
            if classes:
                selector += '.' + '.'.join(classes[:2])

            parts.insert(0, selector)
            current = current.parent

        return ' > '.join(parts[-5:])  # Limit depth

    def _get_xpath(self, element) -> str:
        """Generate an XPath for an element."""
        from bs4 import Tag

        parts = []
        current = element

        while current and isinstance(current, Tag) and current.name:
            xpath_part = current.name

            if current.get('id'):
                xpath_part = f"{current.name}[@id='{current.get('id')}']"
                parts.insert(0, xpath_part)
                break

            parts.insert(0, xpath_part)
            current = current.parent

        return '//' + '/'.join(parts[-5:]) if parts else ''

    def get_heading_hierarchy(self) -> Dict[str, Any]:
        """
        Analyze heading hierarchy for accessibility.

        Returns:
            Dictionary with heading structure analysis
        """
        headings = self._parser.get_headings()

        hierarchy = {
            'headings': [],
            'issues': [],
            'has_h1': False,
            'h1_count': 0,
            'proper_hierarchy': True
        }

        last_level = 0

        for h in headings:
            level = int(h.tag[1])  # h1 -> 1, h2 -> 2, etc.

            hierarchy['headings'].append({
                'level': level,
                'text': h.text[:100],
                'id': h.element_id
            })

            if level == 1:
                hierarchy['has_h1'] = True
                hierarchy['h1_count'] += 1

            # Check for skipped levels
            if last_level > 0 and level > last_level + 1:
                hierarchy['proper_hierarchy'] = False
                hierarchy['issues'].append(
                    f"Heading level skipped: h{last_level} to h{level}"
                )

            last_level = level

        if hierarchy['h1_count'] == 0:
            hierarchy['issues'].append("No h1 heading found")
        elif hierarchy['h1_count'] > 1:
            hierarchy['issues'].append(f"Multiple h1 headings found ({hierarchy['h1_count']})")

        return hierarchy
