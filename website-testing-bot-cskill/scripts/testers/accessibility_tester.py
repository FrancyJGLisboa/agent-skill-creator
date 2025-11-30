"""
Accessibility tester for WCAG compliance checking.

Tests for accessibility violations and provides remediation guidance.
"""

import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from ..utils.html_parser import HTMLParser
from ..utils.constants import (
    SEVERITY_CRITICAL,
    SEVERITY_HIGH,
    SEVERITY_MEDIUM,
    SEVERITY_LOW,
    WCAG_GUIDELINES,
    CONTRAST_RATIOS
)


@dataclass
class AccessibilityIssue:
    """An accessibility issue found during testing."""
    severity: str
    wcag_criterion: str
    wcag_level: str
    title: str
    description: str
    fix_instruction: str
    element_selector: str
    element_html: str
    impact: str


@dataclass
class AccessibilityReport:
    """Complete accessibility testing report."""
    url: str
    wcag_level_tested: str
    issues: List[AccessibilityIssue]
    issues_by_principle: Dict[str, int]
    issues_by_level: Dict[str, int]
    score: int
    grade: str
    passes: List[Dict[str, Any]]
    summary: Dict[str, Any]


class AccessibilityTester:
    """
    WCAG accessibility compliance tester.

    Tests for Level A and AA accessibility requirements.
    """

    def __init__(self, wcag_level: str = 'AA'):
        """
        Initialize accessibility tester.

        Args:
            wcag_level: WCAG conformance level to test ('A', 'AA', or 'AAA')
        """
        self.wcag_level = wcag_level

    def test_accessibility(self, url: str, html: str) -> AccessibilityReport:
        """
        Run comprehensive accessibility tests.

        Args:
            url: URL being tested
            html: HTML content to test

        Returns:
            AccessibilityReport with all findings
        """
        parser = HTMLParser(html, url)
        issues = []
        passes = []

        # Run all tests
        issues.extend(self._test_images(parser))
        issues.extend(self._test_links(parser))
        issues.extend(self._test_forms(parser))
        issues.extend(self._test_headings(parser))
        issues.extend(self._test_language(parser))
        issues.extend(self._test_landmarks(parser))
        issues.extend(self._test_tables(html))
        issues.extend(self._test_focus(html))
        issues.extend(self._test_contrast(html))
        issues.extend(self._test_aria(html))

        # Group issues
        issues_by_principle = self._group_by_principle(issues)
        issues_by_level = self._group_by_level(issues)

        # Calculate score
        score = self._calculate_score(issues)
        grade = self._score_to_grade(score)

        # Generate summary
        summary = {
            'total_issues': len(issues),
            'critical_issues': len([i for i in issues if i.severity == SEVERITY_CRITICAL]),
            'high_issues': len([i for i in issues if i.severity == SEVERITY_HIGH]),
            'medium_issues': len([i for i in issues if i.severity == SEVERITY_MEDIUM]),
            'low_issues': len([i for i in issues if i.severity == SEVERITY_LOW]),
            'level_a_issues': issues_by_level.get('A', 0),
            'level_aa_issues': issues_by_level.get('AA', 0)
        }

        return AccessibilityReport(
            url=url,
            wcag_level_tested=self.wcag_level,
            issues=issues,
            issues_by_principle=issues_by_principle,
            issues_by_level=issues_by_level,
            score=score,
            grade=grade,
            passes=passes,
            summary=summary
        )

    def _test_images(self, parser: HTMLParser) -> List[AccessibilityIssue]:
        """Test images for accessibility."""
        issues = []
        images = parser.get_all_images()

        for img in images:
            # Test: Images must have alt attribute
            if img.alt is None:
                issues.append(AccessibilityIssue(
                    severity=SEVERITY_HIGH,
                    wcag_criterion='1.1.1',
                    wcag_level='A',
                    title='Image missing alt attribute',
                    description='Image does not have an alt attribute',
                    fix_instruction=(
                        f"Add alt attribute to image. If informative, describe the content: "
                        f"<img src='{img.src}' alt='Description of image content'/>. "
                        f"If decorative, use empty alt: <img src='{img.src}' alt=''/>. "
                        f"Never omit the alt attribute entirely."
                    ),
                    element_selector=img.css_selector,
                    element_html=f"<img src='{img.src}'/>",
                    impact='Screen reader users cannot understand the image content'
                ))

            # Test: Alt text should not be filename
            elif img.alt:
                bad_patterns = [
                    r'^IMG_\d+', r'^DSC_?\d+', r'^image\d*$', r'^photo\d*$',
                    r'\.jpg$', r'\.png$', r'\.gif$', r'\.webp$'
                ]
                if any(re.match(p, img.alt, re.I) for p in bad_patterns):
                    issues.append(AccessibilityIssue(
                        severity=SEVERITY_MEDIUM,
                        wcag_criterion='1.1.1',
                        wcag_level='A',
                        title='Alt text appears to be filename',
                        description=f"Alt text '{img.alt}' appears to be a filename, not description",
                        fix_instruction=(
                            f"Replace filename with descriptive text. Instead of '{img.alt}', "
                            f"describe what the image shows: who/what is in it, what's happening, "
                            f"or what information it conveys."
                        ),
                        element_selector=img.css_selector,
                        element_html=f"<img src='{img.src}' alt='{img.alt}'/>",
                        impact='Screen reader will read meaningless filename'
                    ))

        return issues

    def _test_links(self, parser: HTMLParser) -> List[AccessibilityIssue]:
        """Test links for accessibility."""
        issues = []
        links = parser.get_all_links()

        generic_texts = ['click here', 'here', 'link', 'read more', 'learn more', 'more', 'click']

        for link in links:
            # Test: Links must have discernible text
            if not link.text.strip():
                issues.append(AccessibilityIssue(
                    severity=SEVERITY_HIGH,
                    wcag_criterion='2.4.4',
                    wcag_level='A',
                    title='Link has no text',
                    description='Link element has no visible or accessible text',
                    fix_instruction=(
                        f"Add text content or aria-label to link. Example: "
                        f"<a href='{link.href}'>Descriptive link text</a> or "
                        f"<a href='{link.href}' aria-label='Description'><img .../></a> for image links."
                    ),
                    element_selector=link.css_selector,
                    element_html=f"<a href='{link.href}'></a>",
                    impact='Screen reader users cannot determine link purpose'
                ))

            # Test: Link text should be descriptive
            elif link.text.lower().strip() in generic_texts:
                issues.append(AccessibilityIssue(
                    severity=SEVERITY_MEDIUM,
                    wcag_criterion='2.4.4',
                    wcag_level='A',
                    title='Link text is not descriptive',
                    description=f"Link text '{link.text}' doesn't describe destination",
                    fix_instruction=(
                        f"Replace '{link.text}' with text describing the destination. "
                        f"Instead of 'Click here', use 'View our pricing plans'. "
                        f"Instead of 'Read more', use 'Read more about product features'."
                    ),
                    element_selector=link.css_selector,
                    element_html=f"<a href='{link.href}'>{link.text}</a>",
                    impact='Link purpose unclear out of context'
                ))

        return issues

    def _test_forms(self, parser: HTMLParser) -> List[AccessibilityIssue]:
        """Test forms for accessibility."""
        issues = []
        forms = parser.get_all_forms()

        for form in forms:
            for field in form.fields:
                # Skip hidden and button fields
                if field.get('type') in ['hidden', 'submit', 'button', 'reset']:
                    continue

                # Test: Form inputs must have labels
                if not field.get('label'):
                    issues.append(AccessibilityIssue(
                        severity=SEVERITY_HIGH,
                        wcag_criterion='3.3.2',
                        wcag_level='A',
                        title='Form input missing label',
                        description=f"Input '{field.get('name')}' has no associated label",
                        fix_instruction=(
                            f"Add label element for input. Method 1 (explicit): "
                            f"<label for='{field.get('id') or field.get('name')}'>Label Text</label>"
                            f"<input id='{field.get('id') or field.get('name')}' .../> "
                            f"Method 2 (implicit): <label>Label Text <input .../></label>. "
                            f"Labels help all users and expand click target."
                        ),
                        element_selector=field.get('css_selector', ''),
                        element_html=f"<input name='{field.get('name')}' type='{field.get('type')}'/>",
                        impact='Screen reader users cannot identify field purpose'
                    ))

                # Test: Required fields should be indicated
                if field.get('required') and not field.get('aria-required'):
                    issues.append(AccessibilityIssue(
                        severity=SEVERITY_LOW,
                        wcag_criterion='3.3.2',
                        wcag_level='A',
                        title='Required field not clearly indicated',
                        description=f"Required field '{field.get('name')}' may not be clearly marked",
                        fix_instruction=(
                            f"Mark required fields visually and programmatically. "
                            f"Add: aria-required='true' and visual indicator like asterisk (*). "
                            f"Include legend: '* indicates required field'. "
                            f"Don't rely on color alone."
                        ),
                        element_selector=field.get('css_selector', ''),
                        element_html=f"<input name='{field.get('name')}' required/>",
                        impact='Users may not know field is required until error'
                    ))

        return issues

    def _test_headings(self, parser: HTMLParser) -> List[AccessibilityIssue]:
        """Test heading structure for accessibility."""
        issues = []
        headings = parser.get_headings()

        # Check for h1
        h1_count = len([h for h in headings if h.tag == 'h1'])
        if h1_count == 0:
            issues.append(AccessibilityIssue(
                severity=SEVERITY_MEDIUM,
                wcag_criterion='1.3.1',
                wcag_level='A',
                title='Page missing h1 heading',
                description='No h1 heading found on page',
                fix_instruction=(
                    f"Add an h1 heading that describes the page content. "
                    f"Every page should have exactly one h1. "
                    f"Example: <h1>Product Catalog</h1>. "
                    f"The h1 should be the primary topic of the page."
                ),
                element_selector='',
                element_html='',
                impact='Screen reader users cannot quickly identify page topic'
            ))
        elif h1_count > 1:
            issues.append(AccessibilityIssue(
                severity=SEVERITY_LOW,
                wcag_criterion='1.3.1',
                wcag_level='A',
                title='Multiple h1 headings',
                description=f'Page has {h1_count} h1 headings (should have 1)',
                fix_instruction=(
                    f"Reduce to one h1 per page. The h1 should be the main page title. "
                    f"Demote additional h1s to h2 or appropriate level. "
                    f"Multiple h1s can confuse document outline."
                ),
                element_selector='',
                element_html='',
                impact='Document structure unclear'
            ))

        # Check heading hierarchy
        last_level = 0
        for h in headings:
            level = int(h.tag[1])
            if last_level > 0 and level > last_level + 1:
                issues.append(AccessibilityIssue(
                    severity=SEVERITY_MEDIUM,
                    wcag_criterion='1.3.1',
                    wcag_level='A',
                    title='Heading level skipped',
                    description=f'Jumped from h{last_level} to h{level}',
                    fix_instruction=(
                        f"Don't skip heading levels. After h{last_level}, use h{last_level + 1}, "
                        f"not h{level}. Heading levels should increase by one. "
                        f"Correct hierarchy: h1 > h2 > h3, not h1 > h3."
                    ),
                    element_selector=h.css_selector,
                    element_html=f"<{h.tag}>{h.text[:50]}</{h.tag}>",
                    impact='Document outline broken for assistive tech'
                ))
            last_level = level

        return issues

    def _test_language(self, parser: HTMLParser) -> List[AccessibilityIssue]:
        """Test language declaration."""
        issues = []

        lang = parser.get_language()
        if not lang:
            issues.append(AccessibilityIssue(
                severity=SEVERITY_HIGH,
                wcag_criterion='3.1.1',
                wcag_level='A',
                title='Page language not specified',
                description='HTML element missing lang attribute',
                fix_instruction=(
                    f"Add lang attribute to html element: <html lang='en'>. "
                    f"Use correct language code: 'en' for English, 'es' for Spanish, "
                    f"'fr' for French, etc. This enables screen readers to use correct pronunciation."
                ),
                element_selector='html',
                element_html='<html>',
                impact='Screen readers may use wrong pronunciation'
            ))

        return issues

    def _test_landmarks(self, parser: HTMLParser) -> List[AccessibilityIssue]:
        """Test landmark regions."""
        issues = []
        html = parser.html

        # Check for main landmark
        if '<main' not in html.lower() and 'role="main"' not in html.lower():
            issues.append(AccessibilityIssue(
                severity=SEVERITY_MEDIUM,
                wcag_criterion='2.4.1',
                wcag_level='A',
                title='Missing main landmark',
                description='No <main> element or role="main" found',
                fix_instruction=(
                    f"Wrap primary content in <main> element: "
                    f"<main>...page content...</main>. "
                    f"This allows screen reader users to skip to main content. "
                    f"There should be one main landmark per page."
                ),
                element_selector='',
                element_html='',
                impact='Screen reader users cannot skip to main content'
            ))

        # Check for skip link
        skip_patterns = ['skip', 'jump', '#main', '#content']
        has_skip = any(p in html.lower() for p in skip_patterns)
        if not has_skip:
            issues.append(AccessibilityIssue(
                severity=SEVERITY_MEDIUM,
                wcag_criterion='2.4.1',
                wcag_level='A',
                title='Missing skip navigation link',
                description='No skip link to bypass repeated content',
                fix_instruction=(
                    f"Add skip link at start of page: "
                    f"<a href='#main-content' class='skip-link'>Skip to main content</a>. "
                    f"Style to be visible on focus: "
                    f".skip-link {{ position: absolute; left: -9999px; }} "
                    f".skip-link:focus {{ left: 0; }}. "
                    f"Add id to main content: <main id='main-content'>."
                ),
                element_selector='',
                element_html='',
                impact='Keyboard users must tab through all navigation'
            ))

        return issues

    def _test_tables(self, html: str) -> List[AccessibilityIssue]:
        """Test tables for accessibility."""
        issues = []

        # Find data tables (exclude layout tables)
        tables = re.findall(r'<table[^>]*>.*?</table>', html, re.I | re.S)

        for table in tables:
            # Check for table headers
            if '<th' not in table.lower():
                if re.search(r'<td[^>]*>.*?\d+.*?</td>', table):  # Likely data table
                    issues.append(AccessibilityIssue(
                        severity=SEVERITY_HIGH,
                        wcag_criterion='1.3.1',
                        wcag_level='A',
                        title='Data table missing headers',
                        description='Table appears to contain data but has no <th> elements',
                        fix_instruction=(
                            f"Add <th> elements for header cells. "
                            f"For column headers: <thead><tr><th>Header</th>...</tr></thead>. "
                            f"Add scope attribute: <th scope='col'>Column Header</th> or "
                            f"<th scope='row'>Row Header</th>. "
                            f"This associates data cells with headers."
                        ),
                        element_selector='',
                        element_html=table[:200] + '...',
                        impact='Screen readers cannot associate data with headers'
                    ))

            # Check for caption
            if '<caption' not in table.lower() and 'aria-label' not in table.lower():
                issues.append(AccessibilityIssue(
                    severity=SEVERITY_LOW,
                    wcag_criterion='1.3.1',
                    wcag_level='A',
                    title='Table missing caption',
                    description='Table has no caption or accessible name',
                    fix_instruction=(
                        f"Add caption to describe table: "
                        f"<table><caption>Monthly Sales Data</caption>...</table>. "
                        f"Or use aria-label: <table aria-label='Monthly Sales Data'>. "
                        f"Caption helps users understand table purpose."
                    ),
                    element_selector='',
                    element_html=table[:200] + '...',
                    impact='Users may not understand table purpose'
                ))

        return issues

    def _test_focus(self, html: str) -> List[AccessibilityIssue]:
        """Test focus handling."""
        issues = []

        # Check for outline:none antipattern
        if 'outline:' in html and ('none' in html or '0' in html):
            issues.append(AccessibilityIssue(
                severity=SEVERITY_HIGH,
                wcag_criterion='2.4.7',
                wcag_level='AA',
                title='Focus outline may be removed',
                description='CSS may remove focus indicators (outline: none)',
                fix_instruction=(
                    f"Never remove focus outline without replacement. "
                    f"Instead of removing: :focus {{ outline: none; }} "
                    f"Add custom style: :focus {{ outline: 2px solid #0066cc; outline-offset: 2px; }} "
                    f"or use :focus-visible for better UX."
                ),
                element_selector='',
                element_html='',
                impact='Keyboard users cannot see current focus position'
            ))

        # Check for positive tabindex (bad practice)
        positive_tabindex = re.findall(r'tabindex=["\']([1-9]\d*)["\']', html)
        if positive_tabindex:
            issues.append(AccessibilityIssue(
                severity=SEVERITY_MEDIUM,
                wcag_criterion='2.4.3',
                wcag_level='A',
                title='Positive tabindex values used',
                description=f'Found tabindex values > 0: {", ".join(set(positive_tabindex))}',
                fix_instruction=(
                    f"Replace positive tabindex with 0 or remove entirely. "
                    f"Positive tabindex disrupts natural tab order. "
                    f"Use DOM order for focus order. "
                    f"tabindex='0' makes element focusable in natural order, "
                    f"tabindex='-1' removes from tab order but allows programmatic focus."
                ),
                element_selector='',
                element_html='',
                impact='Tab order may not match visual order'
            ))

        return issues

    def _test_contrast(self, html: str) -> List[AccessibilityIssue]:
        """Test color contrast (limited without CSS parsing)."""
        issues = []

        # Look for inline styles with potential contrast issues
        low_contrast_patterns = [
            (r'color:\s*#[cdef]{3}\b', 'Light gray on light'),
            (r'color:\s*#[cdef]{6}\b', 'Light gray on light'),
            (r'color:\s*lightgr[ae]y', 'Light gray'),
        ]

        for pattern, desc in low_contrast_patterns:
            if re.search(pattern, html, re.I):
                issues.append(AccessibilityIssue(
                    severity=SEVERITY_MEDIUM,
                    wcag_criterion='1.4.3',
                    wcag_level='AA',
                    title='Potential contrast issue detected',
                    description=f'{desc} color may have insufficient contrast',
                    fix_instruction=(
                        f"Ensure text has minimum 4.5:1 contrast ratio. "
                        f"Use WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/. "
                        f"For normal text: 4.5:1 minimum, for large text (18pt+): 3:1 minimum. "
                        f"Common fix: darken text or lighten background."
                    ),
                    element_selector='',
                    element_html='',
                    impact='Users with low vision may not read text'
                ))
                break

        return issues

    def _test_aria(self, html: str) -> List[AccessibilityIssue]:
        """Test ARIA usage."""
        issues = []

        # Check for aria-hidden on focusable elements
        if re.search(r'aria-hidden=["\']true["\'][^>]*(button|input|select|a\s|href)', html, re.I):
            issues.append(AccessibilityIssue(
                severity=SEVERITY_HIGH,
                wcag_criterion='4.1.2',
                wcag_level='A',
                title='Focusable element hidden from screen readers',
                description='aria-hidden="true" on interactive element',
                fix_instruction=(
                    f"Don't use aria-hidden='true' on focusable elements. "
                    f"Either remove aria-hidden, or add tabindex='-1' to remove from tab order. "
                    f"Hidden interactive elements create confusing experience."
                ),
                element_selector='',
                element_html='',
                impact='Keyboard users can focus element screen readers ignore'
            ))

        # Check for role without necessary attributes
        role_requirements = {
            'slider': ['aria-valuenow', 'aria-valuemin', 'aria-valuemax'],
            'progressbar': ['aria-valuenow'],
            'checkbox': ['aria-checked'],
            'switch': ['aria-checked'],
            'combobox': ['aria-expanded'],
        }

        for role, required_attrs in role_requirements.items():
            pattern = f'role=["\']?{role}["\']?[^>]*>'
            matches = re.findall(pattern, html, re.I)
            for match in matches:
                missing = [attr for attr in required_attrs if attr not in match.lower()]
                if missing:
                    issues.append(AccessibilityIssue(
                        severity=SEVERITY_HIGH,
                        wcag_criterion='4.1.2',
                        wcag_level='A',
                        title=f'Role "{role}" missing required attributes',
                        description=f'Missing: {", ".join(missing)}',
                        fix_instruction=(
                            f"Add required ARIA attributes for role='{role}': "
                            f"{', '.join(missing)}. "
                            f"Example: <div role='{role}' {' '.join(f\"{a}='value'\" for a in missing)}>. "
                            f"These attributes provide necessary state information."
                        ),
                        element_selector='',
                        element_html=match,
                        impact='Assistive tech cannot convey element state'
                    ))

        return issues

    def _group_by_principle(self, issues: List[AccessibilityIssue]) -> Dict[str, int]:
        """Group issues by WCAG principle."""
        principles = {
            '1': 'perceivable',
            '2': 'operable',
            '3': 'understandable',
            '4': 'robust'
        }

        counts = {p: 0 for p in principles.values()}

        for issue in issues:
            principle_num = issue.wcag_criterion.split('.')[0]
            principle_name = principles.get(principle_num, 'unknown')
            counts[principle_name] += 1

        return counts

    def _group_by_level(self, issues: List[AccessibilityIssue]) -> Dict[str, int]:
        """Group issues by WCAG level."""
        counts = {'A': 0, 'AA': 0, 'AAA': 0}

        for issue in issues:
            if issue.wcag_level in counts:
                counts[issue.wcag_level] += 1

        return counts

    def _calculate_score(self, issues: List[AccessibilityIssue]) -> int:
        """Calculate accessibility score."""
        score = 100

        severity_deductions = {
            SEVERITY_CRITICAL: 20,
            SEVERITY_HIGH: 12,
            SEVERITY_MEDIUM: 6,
            SEVERITY_LOW: 2
        }

        for issue in issues:
            score -= severity_deductions.get(issue.severity, 5)

        return max(0, min(100, score))

    def _score_to_grade(self, score: int) -> str:
        """Convert score to letter grade."""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
