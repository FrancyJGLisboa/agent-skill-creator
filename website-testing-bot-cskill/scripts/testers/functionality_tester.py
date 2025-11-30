"""
Functionality tester for interactive element validation.

Tests dynamic functionality like modals, dropdowns, carousels, etc.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class FunctionalityIssue:
    """A functionality issue found during testing."""
    severity: str
    category: str
    element_type: str
    description: str
    fix_instruction: str
    element_selector: str


@dataclass
class FunctionalityReport:
    """Complete functionality testing report."""
    url: str
    interactive_elements: List[Dict[str, Any]]
    issues: List[FunctionalityIssue]
    tests_run: int
    tests_passed: int
    coverage: Dict[str, int]


class FunctionalityTester:
    """
    Tests interactive functionality of website elements.

    Note: Full functionality testing requires browser automation (Selenium/Playwright).
    This provides static analysis and structure validation.
    """

    def __init__(self):
        """Initialize functionality tester."""
        pass

    def test_functionality(
        self,
        url: str,
        html: str,
        interactive_elements: List[Dict[str, Any]]
    ) -> FunctionalityReport:
        """
        Test interactive element functionality.

        Args:
            url: URL being tested
            html: HTML content
            interactive_elements: List of interactive elements from parser

        Returns:
            FunctionalityReport with findings
        """
        issues = []
        tests_run = 0
        tests_passed = 0

        # Test modals
        modal_issues = self._test_modals(html)
        issues.extend(modal_issues)
        tests_run += 3
        tests_passed += 3 - len(modal_issues)

        # Test dropdowns
        dropdown_issues = self._test_dropdowns(html)
        issues.extend(dropdown_issues)
        tests_run += 3
        tests_passed += 3 - len(dropdown_issues)

        # Test carousels/sliders
        carousel_issues = self._test_carousels(html)
        issues.extend(carousel_issues)
        tests_run += 2
        tests_passed += 2 - len(carousel_issues)

        # Test tabs
        tab_issues = self._test_tabs(html)
        issues.extend(tab_issues)
        tests_run += 2
        tests_passed += 2 - len(tab_issues)

        # Test accordions
        accordion_issues = self._test_accordions(html)
        issues.extend(accordion_issues)
        tests_run += 2
        tests_passed += 2 - len(accordion_issues)

        coverage = {
            'modals': self._count_elements(html, 'modal'),
            'dropdowns': self._count_elements(html, 'dropdown'),
            'carousels': self._count_elements(html, 'carousel|slider|swiper'),
            'tabs': self._count_elements(html, 'tab'),
            'accordions': self._count_elements(html, 'accordion|collapse')
        }

        return FunctionalityReport(
            url=url,
            interactive_elements=interactive_elements,
            issues=issues,
            tests_run=tests_run,
            tests_passed=tests_passed,
            coverage=coverage
        )

    def _test_modals(self, html: str) -> List[FunctionalityIssue]:
        """Test modal dialog structure."""
        import re
        issues = []

        # Find modals
        modals = re.findall(r'<[^>]*(modal|dialog)[^>]*>.*?</[^>]+>', html, re.I | re.S)

        for modal in modals[:5]:  # Test first 5
            modal_lower = modal.lower()

            # Check for close button
            if 'close' not in modal_lower and 'dismiss' not in modal_lower:
                issues.append(FunctionalityIssue(
                    severity='medium',
                    category='functionality',
                    element_type='modal',
                    description='Modal may be missing close button',
                    fix_instruction=(
                        "Add a close button to the modal. "
                        "Include: <button type='button' aria-label='Close' class='close'>×</button>. "
                        "Also ensure clicking outside modal or pressing Escape closes it."
                    ),
                    element_selector=''
                ))
                break

            # Check for proper role
            if 'role="dialog"' not in modal_lower and 'role="alertdialog"' not in modal_lower:
                issues.append(FunctionalityIssue(
                    severity='medium',
                    category='accessibility',
                    element_type='modal',
                    description='Modal missing role="dialog" attribute',
                    fix_instruction=(
                        "Add role='dialog' to modal container. "
                        "Also add aria-modal='true' and aria-labelledby pointing to modal title. "
                        "This announces the modal correctly to screen readers."
                    ),
                    element_selector=''
                ))
                break

        return issues

    def _test_dropdowns(self, html: str) -> List[FunctionalityIssue]:
        """Test dropdown menu structure."""
        import re
        issues = []

        # Find dropdowns
        dropdowns = re.findall(r'<[^>]*(dropdown)[^>]*>', html, re.I)

        if dropdowns:
            # Check for aria-expanded
            if 'aria-expanded' not in html.lower():
                issues.append(FunctionalityIssue(
                    severity='medium',
                    category='accessibility',
                    element_type='dropdown',
                    description='Dropdown missing aria-expanded attribute',
                    fix_instruction=(
                        "Add aria-expanded to dropdown triggers. "
                        "Set aria-expanded='false' by default, toggle to 'true' when open. "
                        "Also add aria-haspopup='menu' to the trigger."
                    ),
                    element_selector=''
                ))

            # Check for keyboard accessibility
            if 'keydown' not in html.lower() and 'keyup' not in html.lower():
                issues.append(FunctionalityIssue(
                    severity='low',
                    category='functionality',
                    element_type='dropdown',
                    description='Dropdown may not have keyboard support',
                    fix_instruction=(
                        "Ensure dropdown is keyboard accessible. "
                        "Arrow keys should navigate options, Enter/Space should select, "
                        "Escape should close. Add keyboard event listeners."
                    ),
                    element_selector=''
                ))

        return issues

    def _test_carousels(self, html: str) -> List[FunctionalityIssue]:
        """Test carousel/slider structure."""
        import re
        issues = []

        carousel_patterns = ['carousel', 'slider', 'swiper', 'slideshow']
        has_carousel = any(p in html.lower() for p in carousel_patterns)

        if has_carousel:
            # Check for navigation
            if 'prev' not in html.lower() and 'next' not in html.lower():
                issues.append(FunctionalityIssue(
                    severity='medium',
                    category='functionality',
                    element_type='carousel',
                    description='Carousel may be missing navigation controls',
                    fix_instruction=(
                        "Add previous/next navigation buttons to carousel. "
                        "Include: <button aria-label='Previous slide'>←</button> "
                        "<button aria-label='Next slide'>→</button>. "
                        "Also consider adding slide indicator dots."
                    ),
                    element_selector=''
                ))

            # Check for pause control
            if 'autoplay' in html.lower() and 'pause' not in html.lower():
                issues.append(FunctionalityIssue(
                    severity='medium',
                    category='accessibility',
                    element_type='carousel',
                    description='Autoplay carousel should have pause control',
                    fix_instruction=(
                        "Add pause/play button for autoplay carousels. "
                        "Users with motion sensitivity need to stop animations. "
                        "WCAG 2.2.2 requires pause mechanism for auto-updating content."
                    ),
                    element_selector=''
                ))

        return issues

    def _test_tabs(self, html: str) -> List[FunctionalityIssue]:
        """Test tab panel structure."""
        import re
        issues = []

        has_tabs = 'role="tab"' in html.lower() or 'tablist' in html.lower()

        if has_tabs:
            # Check for tabpanel
            if 'role="tabpanel"' not in html.lower() and 'tabpanel' not in html.lower():
                issues.append(FunctionalityIssue(
                    severity='medium',
                    category='accessibility',
                    element_type='tabs',
                    description='Tab panels missing role="tabpanel"',
                    fix_instruction=(
                        "Add proper tab panel ARIA structure. "
                        "Tabs: role='tablist' containing role='tab' elements. "
                        "Panels: role='tabpanel' with aria-labelledby pointing to tab."
                    ),
                    element_selector=''
                ))

            # Check for aria-selected
            if 'aria-selected' not in html.lower():
                issues.append(FunctionalityIssue(
                    severity='medium',
                    category='accessibility',
                    element_type='tabs',
                    description='Tabs missing aria-selected attribute',
                    fix_instruction=(
                        "Add aria-selected to tab elements. "
                        "Set aria-selected='true' on active tab, 'false' on others. "
                        "Update dynamically when user selects different tab."
                    ),
                    element_selector=''
                ))

        return issues

    def _test_accordions(self, html: str) -> List[FunctionalityIssue]:
        """Test accordion structure."""
        import re
        issues = []

        accordion_patterns = ['accordion', 'collapse', 'expandable']
        has_accordion = any(p in html.lower() for p in accordion_patterns)

        if has_accordion:
            # Check for aria-expanded
            if 'aria-expanded' not in html.lower():
                issues.append(FunctionalityIssue(
                    severity='medium',
                    category='accessibility',
                    element_type='accordion',
                    description='Accordion headers missing aria-expanded',
                    fix_instruction=(
                        "Add aria-expanded to accordion triggers. "
                        "Set aria-expanded='false' when collapsed, 'true' when expanded. "
                        "Also use aria-controls to associate with content panel."
                    ),
                    element_selector=''
                ))

            # Check for button semantics
            if re.search(r'<div[^>]*(accordion|collapse)[^>]*onclick', html, re.I):
                issues.append(FunctionalityIssue(
                    severity='medium',
                    category='accessibility',
                    element_type='accordion',
                    description='Accordion uses div instead of button for trigger',
                    fix_instruction=(
                        "Use <button> for accordion headers, not <div>. "
                        "Buttons are keyboard accessible by default. "
                        "If div must be used, add role='button' and tabindex='0'."
                    ),
                    element_selector=''
                ))

        return issues

    def _count_elements(self, html: str, pattern: str) -> int:
        """Count elements matching pattern."""
        import re
        return len(re.findall(pattern, html, re.I))
