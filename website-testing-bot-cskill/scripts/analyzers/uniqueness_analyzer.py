"""
Uniqueness analyzer for template detection and originality scoring.

Detects cookie-cutter templates and scores design originality.
"""

import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from ..utils.constants import (
    KNOWN_TEMPLATE_FINGERPRINTS,
    UNIQUENESS_THRESHOLDS,
    UNIQUENESS_WEIGHTS
)


@dataclass
class TemplateMatch:
    """Information about a detected template."""
    name: str
    confidence: float
    indicators_found: List[str]
    category: str  # framework, cms, builder, theme


@dataclass
class UniquenessReport:
    """Complete uniqueness analysis report."""
    url: str
    score: int
    rating: str
    rating_description: str
    templates_detected: List[TemplateMatch]
    breakdown: Dict[str, int]
    customization_level: str
    issues: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    competitor_comparison: Optional[Dict[str, Any]] = None


class UniquenessAnalyzer:
    """
    Analyzes website uniqueness and template detection.

    Scores originality across visual design, layout, functionality,
    and brand identity to determine if site is cookie-cutter or custom.
    """

    def __init__(self):
        """Initialize uniqueness analyzer."""
        self._template_fingerprints = KNOWN_TEMPLATE_FINGERPRINTS

    def analyze_uniqueness(
        self,
        url: str,
        html: str,
        css_content: str = '',
        competitor_urls: List[str] = None
    ) -> UniquenessReport:
        """
        Analyze website uniqueness.

        Args:
            url: URL being analyzed
            html: HTML content
            css_content: CSS content (if available)
            competitor_urls: Optional competitor URLs for comparison

        Returns:
            UniquenessReport with score and analysis
        """
        issues = []
        recommendations = []

        # Detect templates/frameworks
        templates_detected = self._detect_templates(html, css_content)

        # Score each category
        breakdown = {
            'visual_design': self._score_visual_design(html, css_content, templates_detected),
            'layout_structure': self._score_layout_structure(html),
            'functionality': self._score_functionality(html),
            'content_presentation': self._score_content_presentation(html),
            'interactive_elements': self._score_interactive_elements(html),
            'brand_identity': self._score_brand_identity(html)
        }

        # Calculate weighted total score
        total_score = sum(
            breakdown[key] * UNIQUENESS_WEIGHTS[key]
            for key in breakdown
        )
        score = int(total_score)

        # Determine rating
        rating, rating_description = self._get_rating(score)

        # Determine customization level
        customization_level = self._determine_customization_level(templates_detected, score)

        # Generate issues
        if templates_detected:
            for template in templates_detected:
                if template.confidence > 0.7:
                    issues.append({
                        'severity': 'medium' if template.confidence < 0.9 else 'high',
                        'category': 'template_detection',
                        'description': f"Detected {template.name} ({template.category}) with {template.confidence*100:.0f}% confidence",
                        'indicators': template.indicators_found,
                        'fix_instruction': self._get_template_fix(template)
                    })

        if score < 50:
            issues.append({
                'severity': 'high',
                'category': 'uniqueness',
                'description': f"Uniqueness score of {score} indicates generic/template-like design",
                'fix_instruction': (
                    "To increase uniqueness: 1) Customize color scheme beyond template defaults, "
                    "2) Add custom illustrations or photography, 3) Create unique layout sections, "
                    "4) Develop custom interactive elements, 5) Establish distinct typography hierarchy."
                )
            })

        # Generate recommendations
        recommendations.extend(self._generate_recommendations(breakdown, templates_detected))

        return UniquenessReport(
            url=url,
            score=score,
            rating=rating,
            rating_description=rating_description,
            templates_detected=templates_detected,
            breakdown=breakdown,
            customization_level=customization_level,
            issues=issues,
            recommendations=recommendations,
            competitor_comparison=None
        )

    def _detect_templates(self, html: str, css_content: str) -> List[TemplateMatch]:
        """Detect known templates and frameworks."""
        detected = []
        html_lower = html.lower()
        css_lower = css_content.lower() if css_content else ''

        for template_name, fingerprint in self._template_fingerprints.items():
            indicators_found = []
            total_indicators = 0
            matched_indicators = 0

            # Check CSS classes
            if 'css_classes' in fingerprint:
                total_indicators += len(fingerprint['css_classes'])
                for cls in fingerprint['css_classes']:
                    if cls.lower() in html_lower or cls.lower() in css_lower:
                        indicators_found.append(f"CSS class: {cls}")
                        matched_indicators += 1

            # Check meta generators
            if 'meta_generators' in fingerprint:
                total_indicators += len(fingerprint['meta_generators'])
                for gen in fingerprint['meta_generators']:
                    if gen.lower() in html_lower:
                        indicators_found.append(f"Meta generator: {gen}")
                        matched_indicators += 1

            # Check paths
            if 'paths' in fingerprint:
                total_indicators += len(fingerprint['paths'])
                for path in fingerprint['paths']:
                    if path.lower() in html_lower:
                        indicators_found.append(f"Path: {path}")
                        matched_indicators += 1

            # Check domains
            if 'domains' in fingerprint:
                total_indicators += len(fingerprint['domains'])
                for domain in fingerprint['domains']:
                    if domain.lower() in html_lower:
                        indicators_found.append(f"Domain: {domain}")
                        matched_indicators += 1

            # Check CSS files
            if 'css_files' in fingerprint:
                total_indicators += len(fingerprint['css_files'])
                for css_file in fingerprint['css_files']:
                    if css_file.lower() in html_lower:
                        indicators_found.append(f"CSS file: {css_file}")
                        matched_indicators += 1

            # Calculate confidence
            if total_indicators > 0:
                confidence = matched_indicators / total_indicators
                if confidence > 0.3:  # At least 30% match
                    category = self._categorize_template(template_name)
                    detected.append(TemplateMatch(
                        name=template_name,
                        confidence=confidence,
                        indicators_found=indicators_found,
                        category=category
                    ))

        # Sort by confidence
        detected.sort(key=lambda x: x.confidence, reverse=True)
        return detected

    def _categorize_template(self, template_name: str) -> str:
        """Categorize template type."""
        frameworks = ['bootstrap', 'tailwind', 'foundation', 'material_ui']
        cms = ['wordpress', 'drupal', 'joomla']
        builders = ['wix', 'squarespace', 'shopify', 'webflow']

        if template_name in frameworks:
            return 'framework'
        elif template_name in cms:
            return 'cms'
        elif template_name in builders:
            return 'website_builder'
        else:
            return 'theme'

    def _score_visual_design(
        self,
        html: str,
        css_content: str,
        templates: List[TemplateMatch]
    ) -> int:
        """Score visual design originality (0-100)."""
        score = 100

        # Deduct for template usage
        if templates:
            highest_confidence = templates[0].confidence if templates else 0
            if highest_confidence > 0.8:
                score -= 30
            elif highest_confidence > 0.5:
                score -= 15

        # Check for custom styling indicators
        html_lower = html.lower()

        # Custom animations
        if '@keyframes' in css_content.lower() if css_content else False:
            score += 5
        elif 'animation' not in html_lower:
            score -= 5

        # CSS variables (modern custom styling)
        if '--' in html_lower or (css_content and '--' in css_content):
            score += 10

        # Custom fonts
        google_fonts = re.findall(r'fonts\.googleapis\.com/css[^"\']*', html)
        if len(google_fonts) > 0:
            score += 5

        # Inline styles (often indicate customization)
        inline_styles = len(re.findall(r'style="[^"]{20,}"', html))
        if inline_styles > 10:
            score += 5

        return max(0, min(100, score))

    def _score_layout_structure(self, html: str) -> int:
        """Score layout structure uniqueness (0-100)."""
        score = 70  # Start at baseline

        html_lower = html.lower()

        # Check for grid usage
        if 'display: grid' in html_lower or 'display:grid' in html_lower:
            score += 10

        # Check for flexbox
        if 'display: flex' in html_lower or 'display:flex' in html_lower:
            score += 5

        # Check for unique section patterns
        sections = re.findall(r'<section[^>]*class="([^"]+)"', html)
        unique_classes = set()
        for section_classes in sections:
            unique_classes.update(section_classes.split())

        # More unique class names = more customization
        if len(unique_classes) > 20:
            score += 15
        elif len(unique_classes) > 10:
            score += 10
        elif len(unique_classes) > 5:
            score += 5

        # Standard template patterns reduce score
        template_layouts = ['container', 'row', 'col-', 'grid-x', 'cell']
        template_matches = sum(1 for t in template_layouts if t in html_lower)
        if template_matches > 3:
            score -= 15

        return max(0, min(100, score))

    def _score_functionality(self, html: str) -> int:
        """Score functionality innovation (0-100)."""
        score = 60  # Start at baseline

        html_lower = html.lower()

        # Custom web components
        if re.search(r'<[a-z]+-[a-z]+', html):
            score += 20

        # Custom JavaScript
        if 'customelements.define' in html_lower:
            score += 15

        # Interactive features
        interactive_features = [
            'drag', 'drop', 'resize', 'scroll-behavior',
            'intersection', 'mutationobserver', 'webgl', 'canvas'
        ]
        for feature in interactive_features:
            if feature in html_lower:
                score += 5

        # Standard jQuery plugins reduce score
        common_plugins = [
            'jquery.min.js', 'slick.min.js', 'owl.carousel',
            'lightbox', 'fancybox', 'isotope'
        ]
        for plugin in common_plugins:
            if plugin in html_lower:
                score -= 5

        return max(0, min(100, score))

    def _score_content_presentation(self, html: str) -> int:
        """Score content presentation uniqueness (0-100)."""
        score = 70  # Start at baseline

        html_lower = html.lower()

        # Check for custom content structures
        if 'data-' in html_lower:
            data_attrs = re.findall(r'data-([a-z-]+)', html_lower)
            unique_attrs = set(data_attrs)
            if len(unique_attrs) > 10:
                score += 15
            elif len(unique_attrs) > 5:
                score += 10

        # Schema.org markup (shows attention to detail)
        if 'schema.org' in html_lower or 'itemtype' in html_lower:
            score += 10

        # Microdata
        if 'itemscope' in html_lower:
            score += 5

        # Rich media embedding
        media_types = ['video', 'audio', 'canvas', 'svg']
        for media in media_types:
            if f'<{media}' in html_lower:
                score += 5

        return max(0, min(100, score))

    def _score_interactive_elements(self, html: str) -> int:
        """Score interactive element creativity (0-100)."""
        score = 60  # Start at baseline

        html_lower = html.lower()

        # Custom form styling
        if 'appearance: none' in html_lower or 'appearance:none' in html_lower:
            score += 10

        # Custom animations on interactions
        if ':hover' in html_lower or ':focus' in html_lower:
            score += 5

        # Custom cursor
        if 'cursor:' in html_lower and 'pointer' not in html_lower.split('cursor:')[1][:50]:
            score += 5

        # Transitions
        if 'transition' in html_lower:
            score += 5

        # Transform effects
        if 'transform' in html_lower:
            score += 5

        # Standard UI component libraries reduce score
        ui_libs = ['bootstrap', 'material', 'ant-design', 'chakra']
        for lib in ui_libs:
            if lib in html_lower:
                score -= 10
                break

        return max(0, min(100, score))

    def _score_brand_identity(self, html: str) -> int:
        """Score brand identity integration (0-100)."""
        score = 50  # Start at baseline

        html_lower = html.lower()

        # Custom favicon
        if 'favicon' in html_lower or 'icon' in html_lower:
            if '.ico' in html_lower or '.png' in html_lower or '.svg' in html_lower:
                score += 10

        # OG/Twitter meta tags (shows brand awareness)
        if 'og:' in html_lower or 'twitter:' in html_lower:
            score += 10

        # Custom fonts (not system fonts)
        if 'font-face' in html_lower or 'fonts.google' in html_lower:
            score += 10

        # Logo
        if 'logo' in html_lower:
            score += 10

        # Brand colors (check for non-standard colors)
        colors = re.findall(r'#[0-9a-f]{6}', html_lower)
        unique_colors = set(colors)
        if len(unique_colors) > 5:
            score += 15
        elif len(unique_colors) > 3:
            score += 10

        return max(0, min(100, score))

    def _get_rating(self, score: int) -> tuple:
        """Get rating label and description."""
        for key, threshold in UNIQUENESS_THRESHOLDS.items():
            if threshold['min'] <= score <= threshold['max']:
                descriptions = {
                    'highly_original': "Custom design, unique functionality, strong brand identity",
                    'distinctive': "Customized template with significant modifications",
                    'moderate': "Recognizable template base with some customization",
                    'generic': "Minimal template customization, common patterns",
                    'template_clone': "Nearly unmodified template, no unique identity"
                }
                return threshold['label'], descriptions.get(key, '')
        return "Unknown", ""

    def _determine_customization_level(
        self,
        templates: List[TemplateMatch],
        score: int
    ) -> str:
        """Determine customization level description."""
        if not templates or (templates and templates[0].confidence < 0.3):
            if score > 80:
                return "Fully Custom - No template detected, highly original design"
            else:
                return "Custom with Common Patterns - Original but uses familiar design patterns"

        highest = templates[0]
        if highest.confidence > 0.8:
            if score > 50:
                return f"Customized {highest.name} - Template base with notable modifications"
            else:
                return f"Standard {highest.name} - Minimal customization from template"
        elif highest.confidence > 0.5:
            return f"Modified {highest.name} - Significant departures from template"
        else:
            return "Hybrid - Uses framework components with custom implementation"

    def _get_template_fix(self, template: TemplateMatch) -> str:
        """Get fix instruction for template detection."""
        fixes = {
            'framework': (
                f"Using {template.name} framework is fine, but customize heavily: "
                f"1) Create custom color variables, 2) Override default component styles, "
                f"3) Add unique animations, 4) Use custom typography, "
                f"5) Create unique layout patterns beyond grid defaults."
            ),
            'cms': (
                f"{template.name} detected. To improve uniqueness: "
                f"1) Use a custom theme or heavily modify existing theme, "
                f"2) Add custom page templates, 3) Implement unique headers/footers, "
                f"4) Customize forms and interactive elements, 5) Remove template watermarks."
            ),
            'website_builder': (
                f"{template.name} builder detected with {template.confidence*100:.0f}% confidence. "
                f"Builder sites often look similar. To differentiate: "
                f"1) Use custom code blocks for unique sections, "
                f"2) Upload custom graphics instead of stock photos, "
                f"3) Create unique page layouts, 4) Customize all typography, "
                f"5) Consider migrating to custom development for full control."
            ),
            'theme': (
                f"Theme/template detected. Customize by: "
                f"1) Changing all default colors, 2) Replacing stock imagery, "
                f"3) Modifying layout structure, 4) Adding custom sections, "
                f"5) Removing or replacing template widgets."
            )
        }
        return fixes.get(template.category, "Customize the template to increase uniqueness.")

    def _generate_recommendations(
        self,
        breakdown: Dict[str, int],
        templates: List[TemplateMatch]
    ) -> List[Dict[str, Any]]:
        """Generate uniqueness improvement recommendations."""
        recommendations = []

        # Find lowest scoring areas
        sorted_areas = sorted(breakdown.items(), key=lambda x: x[1])

        for area, score in sorted_areas[:3]:  # Top 3 weakest areas
            if score < 70:
                recommendations.append({
                    'priority': 'high' if score < 50 else 'medium',
                    'category': area,
                    'current_score': score,
                    'title': f'Improve {area.replace("_", " ").title()}',
                    'description': self._get_area_recommendation(area, score)
                })

        return recommendations

    def _get_area_recommendation(self, area: str, score: int) -> str:
        """Get specific recommendation for an area."""
        recommendations = {
            'visual_design': (
                "Enhance visual design: Create custom color palette, "
                "use unique typography combinations, add custom illustrations "
                "or photography, implement distinctive hover/focus states."
            ),
            'layout_structure': (
                "Improve layout uniqueness: Create asymmetric layouts, "
                "use CSS Grid for complex arrangements, design unique section "
                "transitions, break from standard 12-column patterns."
            ),
            'functionality': (
                "Add unique functionality: Implement custom animations, "
                "create interactive data visualizations, add micro-interactions, "
                "develop unique navigation patterns or scroll effects."
            ),
            'content_presentation': (
                "Enhance content presentation: Use custom content cards, "
                "implement unique list styles, add structured data, "
                "create distinctive media presentation."
            ),
            'interactive_elements': (
                "Customize interactions: Design unique button styles, "
                "create custom form elements, add distinctive transitions, "
                "implement creative loading states."
            ),
            'brand_identity': (
                "Strengthen brand identity: Develop consistent color usage, "
                "implement custom typography, add branded icons, "
                "ensure logo integration throughout."
            )
        }
        return recommendations.get(area, "Customize this area to improve uniqueness.")
