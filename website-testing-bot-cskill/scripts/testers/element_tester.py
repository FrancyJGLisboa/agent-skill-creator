"""
Element tester for comprehensive validation of website elements.

Tests buttons, links, images, forms, and menus for functionality and quality.
"""

import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from urllib.parse import urlparse

from ..utils.http_client import HTTPClient
from ..utils.constants import (
    SEVERITY_CRITICAL,
    SEVERITY_HIGH,
    SEVERITY_MEDIUM,
    SEVERITY_LOW,
    SEVERITY_INFO
)


@dataclass
class Issue:
    """Represents a testing issue found."""
    severity: str
    category: str
    element_type: str
    description: str
    fix_instruction: str
    location: Dict[str, Any]
    wcag_reference: Optional[str] = None
    related_issues: List[str] = field(default_factory=list)


@dataclass
class ElementTestResult:
    """Result of element testing."""
    element_type: str
    element_id: str
    location: Dict[str, Any]
    tests_run: int
    tests_passed: int
    tests_failed: int
    issues: List[Issue]
    details: Dict[str, Any]


class ElementTester:
    """
    Comprehensive element tester for website validation.

    Tests every interactive and static element for functionality,
    accessibility, and user experience.
    """

    def __init__(self, http_client: Optional[HTTPClient] = None):
        """
        Initialize element tester.

        Args:
            http_client: HTTP client for resource checking
        """
        self.http_client = http_client or HTTPClient()
        self._issues: List[Issue] = []
        self._results: List[ElementTestResult] = []

    def test_button(
        self,
        button_data: Dict[str, Any],
        page_url: str
    ) -> ElementTestResult:
        """
        Test a button element comprehensively.

        Args:
            button_data: Button element data from parser
            page_url: URL of the page containing the button

        Returns:
            ElementTestResult with all test outcomes
        """
        issues = []
        tests_run = 0
        tests_passed = 0

        tag = button_data.get('tag', 'button')
        attributes = button_data.get('attributes', {})
        text = button_data.get('text', '')
        classes = button_data.get('classes', [])

        location = {
            'page_url': page_url,
            'css_selector': button_data.get('css_selector', ''),
            'xpath': button_data.get('xpath', ''),
            'line_number': button_data.get('line_number', 0)
        }

        # Test 1: Button has accessible text
        tests_run += 1
        if text.strip() or attributes.get('aria-label') or attributes.get('aria-labelledby'):
            tests_passed += 1
        else:
            issues.append(Issue(
                severity=SEVERITY_HIGH,
                category='accessibility',
                element_type='button',
                description='Button has no accessible text content',
                fix_instruction=(
                    f"Add visible text content inside the button, or add an aria-label attribute. "
                    f"For example: <button aria-label='Submit form'>Submit</button>. "
                    f"If using an icon button, ensure aria-label describes the action."
                ),
                location=location,
                wcag_reference='4.1.2 Name, Role, Value (Level A)'
            ))

        # Test 2: Button has proper type attribute (for button elements)
        tests_run += 1
        if tag == 'button':
            btn_type = attributes.get('type')
            if btn_type in ['button', 'submit', 'reset']:
                tests_passed += 1
            else:
                issues.append(Issue(
                    severity=SEVERITY_LOW,
                    category='best_practice',
                    element_type='button',
                    description='Button missing explicit type attribute',
                    fix_instruction=(
                        f"Add type attribute to button. Without it, buttons default to type='submit' "
                        f"which may cause unintended form submissions. Add: type='button' if it's a "
                        f"generic button, type='submit' if it submits a form, or type='reset' to reset forms."
                    ),
                    location=location
                ))
        else:
            tests_passed += 1  # Input buttons have implicit type

        # Test 3: Button is not disabled without indication
        tests_run += 1
        is_disabled = attributes.get('disabled') is not None or 'disabled' in str(classes)
        has_disabled_aria = attributes.get('aria-disabled') == 'true'

        if is_disabled or has_disabled_aria:
            # Check if visually indicated (has disabled class)
            if 'disabled' in str(classes).lower() or is_disabled:
                tests_passed += 1
            else:
                issues.append(Issue(
                    severity=SEVERITY_MEDIUM,
                    category='ux',
                    element_type='button',
                    description='Disabled button may not be visually distinct',
                    fix_instruction=(
                        f"Add visual styling for disabled state. Add a CSS class like 'disabled' and "
                        f"style it: .disabled {{ opacity: 0.5; cursor: not-allowed; }}. "
                        f"Ensure the disabled state is communicated both visually and programmatically."
                    ),
                    location=location
                ))
        else:
            tests_passed += 1

        # Test 4: Button has focus styles (check for outline:none antipattern)
        tests_run += 1
        # We can't check CSS directly, but we can flag potential issues
        if 'no-focus' in str(classes).lower() or 'outline-none' in str(classes).lower():
            issues.append(Issue(
                severity=SEVERITY_HIGH,
                category='accessibility',
                element_type='button',
                description='Button may have focus outline removed',
                fix_instruction=(
                    f"Do not remove focus outlines without providing an alternative focus indicator. "
                    f"If outline:none is used in CSS, add a custom focus style like: "
                    f"button:focus {{ box-shadow: 0 0 0 3px rgba(0,102,204,0.5); }}. "
                    f"Focus visibility is essential for keyboard users."
                ),
                location=location,
                wcag_reference='2.4.7 Focus Visible (Level AA)'
            ))
        else:
            tests_passed += 1

        # Test 5: Icon-only buttons have aria-label
        tests_run += 1
        text_content = text.strip()
        has_icon_class = any(icon in str(classes).lower() for icon in ['icon', 'fa-', 'material-', 'bi-'])

        if has_icon_class and not text_content:
            if attributes.get('aria-label') or attributes.get('aria-labelledby') or attributes.get('title'):
                tests_passed += 1
            else:
                issues.append(Issue(
                    severity=SEVERITY_HIGH,
                    category='accessibility',
                    element_type='button',
                    description='Icon button has no accessible label',
                    fix_instruction=(
                        f"Icon-only buttons must have an accessible name. Add aria-label with a "
                        f"description of the button's action. For example: "
                        f"<button aria-label='Close dialog'><i class='icon-close'></i></button>. "
                        f"The aria-label should describe what the button does, not what it looks like."
                    ),
                    location=location,
                    wcag_reference='4.1.2 Name, Role, Value (Level A)'
                ))
        else:
            tests_passed += 1

        # Test 6: Link-styled buttons use proper semantics
        tests_run += 1
        if tag == 'a' and button_data.get('attributes', {}).get('role') == 'button':
            href = attributes.get('href', '')
            if not href or href == '#' or href.startswith('javascript:'):
                issues.append(Issue(
                    severity=SEVERITY_MEDIUM,
                    category='semantics',
                    element_type='button',
                    description='Link styled as button should be a <button> element',
                    fix_instruction=(
                        f"If this element triggers an action (not navigation), use a <button> element "
                        f"instead of an <a> with role='button'. Links are for navigation, buttons are "
                        f"for actions. Change: <a href='#' role='button'>Click</a> to: "
                        f"<button type='button'>Click</button>. Style with CSS to match appearance."
                    ),
                    location=location
                ))
            else:
                tests_passed += 1
        else:
            tests_passed += 1

        return ElementTestResult(
            element_type='button',
            element_id=attributes.get('id', f"button_{location['line_number']}"),
            location=location,
            tests_run=tests_run,
            tests_passed=tests_passed,
            tests_failed=tests_run - tests_passed,
            issues=issues,
            details={
                'tag': tag,
                'text': text[:100],
                'type': attributes.get('type'),
                'classes': classes
            }
        )

    def test_link(
        self,
        link_data: Dict[str, Any],
        page_url: str
    ) -> ElementTestResult:
        """
        Test a link element comprehensively.

        Args:
            link_data: Link element data from parser
            page_url: URL of the page containing the link

        Returns:
            ElementTestResult with all test outcomes
        """
        issues = []
        tests_run = 0
        tests_passed = 0

        href = link_data.get('href', '')
        text = link_data.get('text', '')
        target = link_data.get('target', '')
        rel = link_data.get('rel', '')
        is_external = link_data.get('is_external', False)

        location = {
            'page_url': page_url,
            'css_selector': link_data.get('css_selector', ''),
            'line_number': link_data.get('line_number', 0)
        }

        # Test 1: Link has href
        tests_run += 1
        if href and href != '#':
            tests_passed += 1
        else:
            issues.append(Issue(
                severity=SEVERITY_MEDIUM,
                category='functionality',
                element_type='link',
                description='Link has empty or placeholder href',
                fix_instruction=(
                    f"Replace href='#' with the actual destination URL. If this link triggers "
                    f"JavaScript behavior and doesn't navigate, consider using a <button> element "
                    f"instead. If it's a placeholder link during development, add the real URL. "
                    f"Links with href='#' cause the page to jump to top when clicked."
                ),
                location=location
            ))

        # Test 2: Link has descriptive text
        tests_run += 1
        generic_texts = ['click here', 'read more', 'learn more', 'here', 'link', 'more']
        text_lower = text.lower().strip()

        if text_lower and text_lower not in generic_texts:
            tests_passed += 1
        else:
            issues.append(Issue(
                severity=SEVERITY_MEDIUM,
                category='accessibility',
                element_type='link',
                description=f"Link text '{text}' is not descriptive",
                fix_instruction=(
                    f"Replace generic link text with descriptive text that indicates the destination. "
                    f"Instead of 'Click here' or 'Read more', use text like 'Read our privacy policy' "
                    f"or 'View product specifications'. Screen reader users often navigate by links, "
                    f"and descriptive text helps them understand where each link goes."
                ),
                location=location,
                wcag_reference='2.4.4 Link Purpose (In Context) (Level A)'
            ))

        # Test 3: External links have proper rel attribute
        tests_run += 1
        if is_external and target == '_blank':
            if 'noopener' in str(rel) or 'noreferrer' in str(rel):
                tests_passed += 1
            else:
                issues.append(Issue(
                    severity=SEVERITY_HIGH,
                    category='security',
                    element_type='link',
                    description='External link with target="_blank" missing rel="noopener"',
                    fix_instruction=(
                        f"Add rel='noopener noreferrer' to all external links that open in new tabs. "
                        f"Without this, the new page can access your page via window.opener and "
                        f"potentially redirect it (tabnabbing attack). Change to: "
                        f"<a href='{href}' target='_blank' rel='noopener noreferrer'>{text}</a>"
                    ),
                    location=location
                ))
        else:
            tests_passed += 1

        # Test 4: Link is not broken (if we have status code)
        tests_run += 1
        status_code = link_data.get('status_code', 200)
        if status_code and status_code >= 400:
            issues.append(Issue(
                severity=SEVERITY_CRITICAL,
                category='broken_link',
                element_type='link',
                description=f"Link returns HTTP {status_code} error",
                fix_instruction=(
                    f"The link to '{href}' is broken (HTTP {status_code}). "
                    f"Options to fix: 1) Update the href to the correct URL if the page moved, "
                    f"2) Remove the link if the destination no longer exists, "
                    f"3) Create the missing page if it should exist. "
                    f"Test by visiting the URL directly in a browser."
                ),
                location=location
            ))
        else:
            tests_passed += 1

        # Test 5: New tab links indicate they open in new tab
        tests_run += 1
        if target == '_blank':
            # Check if text indicates new tab/window
            new_tab_indicators = ['new tab', 'new window', 'opens in', 'external']
            has_indicator = any(ind in text.lower() for ind in new_tab_indicators)

            if has_indicator or link_data.get('attributes', {}).get('aria-label'):
                tests_passed += 1
            else:
                issues.append(Issue(
                    severity=SEVERITY_LOW,
                    category='ux',
                    element_type='link',
                    description='Link opens in new tab without indication',
                    fix_instruction=(
                        f"Indicate to users that this link opens in a new tab. Options: "
                        f"1) Add '(opens in new tab)' to the link text, "
                        f"2) Add an icon with aria-label='opens in new tab', "
                        f"3) Add title='Opens in new tab' attribute. "
                        f"This helps users who may be disoriented by unexpected new tabs."
                    ),
                    location=location
                ))
        else:
            tests_passed += 1

        # Test 6: Mailto links have valid email
        tests_run += 1
        if href.startswith('mailto:'):
            email = href.replace('mailto:', '').split('?')[0]
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if re.match(email_pattern, email):
                tests_passed += 1
            else:
                issues.append(Issue(
                    severity=SEVERITY_MEDIUM,
                    category='functionality',
                    element_type='link',
                    description=f"Mailto link has invalid email format: {email}",
                    fix_instruction=(
                        f"Correct the email address in the mailto link. Current value '{email}' "
                        f"doesn't appear to be a valid email format. Ensure the format is: "
                        f"mailto:username@domain.com. If additional parameters are needed, "
                        f"use: mailto:email@example.com?subject=Hello&body=Message"
                    ),
                    location=location
                ))
        else:
            tests_passed += 1

        return ElementTestResult(
            element_type='link',
            element_id=f"link_{href[:50]}",
            location=location,
            tests_run=tests_run,
            tests_passed=tests_passed,
            tests_failed=tests_run - tests_passed,
            issues=issues,
            details={
                'href': href,
                'text': text[:100],
                'target': target,
                'rel': rel,
                'is_external': is_external
            }
        )

    def test_image(
        self,
        image_data: Dict[str, Any],
        page_url: str
    ) -> ElementTestResult:
        """
        Test an image element comprehensively.

        Args:
            image_data: Image element data from parser
            page_url: URL of the page containing the image

        Returns:
            ElementTestResult with all test outcomes
        """
        issues = []
        tests_run = 0
        tests_passed = 0

        src = image_data.get('src', '')
        alt = image_data.get('alt')
        width = image_data.get('width')
        height = image_data.get('height')
        srcset = image_data.get('srcset')
        loading = image_data.get('loading')

        location = {
            'page_url': page_url,
            'css_selector': image_data.get('css_selector', ''),
            'line_number': image_data.get('line_number', 0)
        }

        # Test 1: Image has alt attribute
        tests_run += 1
        if alt is not None:  # Empty string is valid for decorative images
            tests_passed += 1
        else:
            issues.append(Issue(
                severity=SEVERITY_HIGH,
                category='accessibility',
                element_type='image',
                description='Image missing alt attribute',
                fix_instruction=(
                    f"Add alt attribute to the image. If the image conveys information, "
                    f"describe it: alt='Photo of product in use'. If decorative, use empty alt: alt=''. "
                    f"NEVER omit the alt attribute entirely. For this image at {src}, determine if it's: "
                    f"1) Informative: describe the content, 2) Decorative: use alt='', "
                    f"3) Functional (button/link): describe the action."
                ),
                location=location,
                wcag_reference='1.1.1 Non-text Content (Level A)'
            ))

        # Test 2: Alt text is meaningful (not filename or generic)
        tests_run += 1
        if alt:
            bad_patterns = [
                r'^image\d*$', r'^img\d*$', r'^photo\d*$', r'^picture\d*$',
                r'\.jpg$', r'\.png$', r'\.gif$', r'\.webp$',
                r'^DSC\d+', r'^IMG_\d+', r'^untitled',
                r'^banner$', r'^header$', r'^logo$'
            ]
            is_bad = any(re.match(pat, alt, re.I) for pat in bad_patterns)

            if not is_bad:
                tests_passed += 1
            else:
                issues.append(Issue(
                    severity=SEVERITY_MEDIUM,
                    category='accessibility',
                    element_type='image',
                    description=f"Alt text '{alt}' is not descriptive",
                    fix_instruction=(
                        f"Replace the generic alt text with a meaningful description. "
                        f"Current: alt='{alt}'. Instead of filenames or generic words, describe "
                        f"what the image shows: who/what is in it, what action is happening, "
                        f"or what information it conveys. Example: 'Customer service representative "
                        f"helping a client at the front desk'."
                    ),
                    location=location,
                    wcag_reference='1.1.1 Non-text Content (Level A)'
                ))
        else:
            tests_passed += 1  # Empty alt is valid for decorative

        # Test 3: Image has dimensions (prevents layout shift)
        tests_run += 1
        if width and height:
            tests_passed += 1
        else:
            issues.append(Issue(
                severity=SEVERITY_MEDIUM,
                category='performance',
                element_type='image',
                description='Image missing width and/or height attributes',
                fix_instruction=(
                    f"Add width and height attributes to prevent Cumulative Layout Shift (CLS). "
                    f"Example: <img src='{src}' width='800' height='600' alt='...'/>. "
                    f"This allows the browser to reserve space before the image loads. "
                    f"Get dimensions from image properties or use CSS aspect-ratio instead."
                ),
                location=location
            ))

        # Test 4: Image loads successfully
        tests_run += 1
        status_code = image_data.get('status_code', 200)
        if status_code and status_code >= 400:
            issues.append(Issue(
                severity=SEVERITY_CRITICAL,
                category='broken_image',
                element_type='image',
                description=f"Image returns HTTP {status_code} - broken/missing",
                fix_instruction=(
                    f"The image at '{src}' is not loading (HTTP {status_code}). "
                    f"Fix options: 1) Verify the image file exists at this path, "
                    f"2) Check for typos in the filename, 3) Ensure the file was uploaded, "
                    f"4) Check file permissions on the server. "
                    f"Test by opening {src} directly in browser."
                ),
                location=location
            ))
        else:
            tests_passed += 1

        # Test 5: Image is optimized (if file size available)
        tests_run += 1
        file_size = image_data.get('file_size', 0)
        if file_size > 500000:  # > 500KB
            size_kb = file_size / 1024
            issues.append(Issue(
                severity=SEVERITY_HIGH,
                category='performance',
                element_type='image',
                description=f"Image is {size_kb:.0f}KB - too large for web",
                fix_instruction=(
                    f"Optimize this image to reduce file size. Current: {size_kb:.0f}KB, "
                    f"Target: <200KB. Steps: 1) Resize to actual display dimensions "
                    f"(don't serve 4000px image for 400px display), "
                    f"2) Compress with quality 80-85%, 3) Convert to WebP format. "
                    f"Tools: Squoosh (web), ImageOptim (Mac), or command: "
                    f"'cwebp -q 85 {src} -o output.webp'"
                ),
                location=location
            ))
        else:
            tests_passed += 1

        # Test 6: Responsive images use srcset
        tests_run += 1
        is_large_image = (width and int(width) > 600) or 'hero' in src.lower() or 'banner' in src.lower()
        if is_large_image and not srcset:
            issues.append(Issue(
                severity=SEVERITY_LOW,
                category='performance',
                element_type='image',
                description='Large image should use srcset for responsive loading',
                fix_instruction=(
                    f"Add srcset attribute for responsive images to serve appropriate sizes. "
                    f"Example: <img src='image-800.jpg' "
                    f"srcset='image-400.jpg 400w, image-800.jpg 800w, image-1200.jpg 1200w' "
                    f"sizes='(max-width: 600px) 400px, (max-width: 1200px) 800px, 1200px' "
                    f"alt='...'/>. This saves bandwidth on mobile devices."
                ),
                location=location
            ))
        else:
            tests_passed += 1

        # Test 7: Below-fold images use lazy loading
        tests_run += 1
        is_above_fold = image_data.get('is_above_fold', True)  # Assume above fold if unknown
        if not is_above_fold and loading != 'lazy':
            issues.append(Issue(
                severity=SEVERITY_LOW,
                category='performance',
                element_type='image',
                description='Below-fold image should use lazy loading',
                fix_instruction=(
                    f"Add loading='lazy' to images below the fold. "
                    f"Change to: <img src='{src}' loading='lazy' alt='...'/>. "
                    f"This defers loading until the image is near the viewport, "
                    f"improving initial page load time. Do NOT add to above-fold images."
                ),
                location=location
            ))
        else:
            tests_passed += 1

        return ElementTestResult(
            element_type='image',
            element_id=f"img_{src[:50]}",
            location=location,
            tests_run=tests_run,
            tests_passed=tests_passed,
            tests_failed=tests_run - tests_passed,
            issues=issues,
            details={
                'src': src,
                'alt': alt,
                'width': width,
                'height': height,
                'has_srcset': bool(srcset),
                'loading': loading
            }
        )

    def test_form(
        self,
        form_data: Dict[str, Any],
        page_url: str
    ) -> ElementTestResult:
        """
        Test a form element comprehensively.

        Args:
            form_data: Form element data from parser
            page_url: URL of the page containing the form

        Returns:
            ElementTestResult with all test outcomes
        """
        issues = []
        tests_run = 0
        tests_passed = 0

        action = form_data.get('action', '')
        method = form_data.get('method', 'GET')
        form_id = form_data.get('id', '')
        fields = form_data.get('fields', [])

        location = {
            'page_url': page_url,
            'css_selector': form_data.get('css_selector', ''),
            'line_number': form_data.get('line_number', 0)
        }

        # Test 1: Form has action attribute
        tests_run += 1
        if action:
            tests_passed += 1
        else:
            issues.append(Issue(
                severity=SEVERITY_MEDIUM,
                category='functionality',
                element_type='form',
                description='Form missing action attribute',
                fix_instruction=(
                    f"Add action attribute to specify where form data is submitted. "
                    f"Example: <form action='/api/submit' method='POST'>. "
                    f"Without an action, the form submits to the current page URL, "
                    f"which may not be the intended behavior."
                ),
                location=location
            ))

        # Test 2: Sensitive forms use POST method
        tests_run += 1
        has_password = any(f.get('type') == 'password' for f in fields)
        has_sensitive = any(f.get('type') in ['password', 'email', 'tel', 'credit-card'] for f in fields)

        if has_sensitive and method.upper() == 'GET':
            issues.append(Issue(
                severity=SEVERITY_CRITICAL,
                category='security',
                element_type='form',
                description='Form with sensitive data should use POST method',
                fix_instruction=(
                    f"Change form method from GET to POST. GET requests expose data in URLs "
                    f"and browser history. Change: <form method='GET'> to <form method='POST'>. "
                    f"This is critical for forms containing passwords, emails, or payment info."
                ),
                location=location
            ))
        else:
            tests_passed += 1

        # Test 3: Form has submit button
        tests_run += 1
        has_submit = any(f.get('type') in ['submit', 'button'] for f in fields) or form_data.get('submit_button')
        if has_submit:
            tests_passed += 1
        else:
            issues.append(Issue(
                severity=SEVERITY_MEDIUM,
                category='functionality',
                element_type='form',
                description='Form missing submit button',
                fix_instruction=(
                    f"Add a submit button to the form. Users need a clear way to submit. "
                    f"Add: <button type='submit'>Submit</button> or "
                    f"<input type='submit' value='Submit'/>. "
                    f"Ensure the button text describes the action (e.g., 'Send Message', 'Sign Up')."
                ),
                location=location
            ))

        # Test 4: All fields have labels
        tests_run += 1
        fields_without_labels = [f for f in fields if not f.get('label') and f.get('type') not in ['hidden', 'submit', 'button']]
        if not fields_without_labels:
            tests_passed += 1
        else:
            field_names = [f.get('name', 'unknown') for f in fields_without_labels[:3]]
            issues.append(Issue(
                severity=SEVERITY_HIGH,
                category='accessibility',
                element_type='form',
                description=f"Form fields missing labels: {', '.join(field_names)}",
                fix_instruction=(
                    f"Add <label> elements for each form field. For field '{field_names[0]}': "
                    f"<label for='{field_names[0]}'>Field Label</label>"
                    f"<input id='{field_names[0]}' name='{field_names[0]}'/>. "
                    f"Labels help all users, especially screen reader users, understand what to enter."
                ),
                location=location,
                wcag_reference='3.3.2 Labels or Instructions (Level A)'
            ))

        # Test 5: Required fields are marked
        tests_run += 1
        required_fields = [f for f in fields if f.get('required')]
        if not required_fields or all(f.get('aria-required') or f.get('required') for f in required_fields):
            tests_passed += 1
        else:
            issues.append(Issue(
                severity=SEVERITY_MEDIUM,
                category='accessibility',
                element_type='form',
                description='Required fields not properly indicated',
                fix_instruction=(
                    f"Mark required fields with both visual and programmatic indicators. "
                    f"Add: required attribute AND visual indicator (asterisk with explanation). "
                    f"Example: <label>Email *<input type='email' required/></label> "
                    f"with note: '* indicates required field'. "
                    f"Don't rely solely on color to indicate required status."
                ),
                location=location,
                wcag_reference='3.3.2 Labels or Instructions (Level A)'
            ))

        # Test 6: Form submits over HTTPS
        tests_run += 1
        if action.startswith('http://') and has_sensitive:
            issues.append(Issue(
                severity=SEVERITY_CRITICAL,
                category='security',
                element_type='form',
                description='Form with sensitive data submits over HTTP (not secure)',
                fix_instruction=(
                    f"Change form action from HTTP to HTTPS. "
                    f"Current: action='{action}'. "
                    f"Change to: action='{action.replace('http://', 'https://')}'. "
                    f"HTTP transmits data in plain text. HTTPS encrypts the transmission."
                ),
                location=location
            ))
        else:
            tests_passed += 1

        # Test 7: Email fields have correct type
        tests_run += 1
        email_fields = [f for f in fields if 'email' in f.get('name', '').lower()]
        wrong_type_email = [f for f in email_fields if f.get('type') not in ['email', 'hidden']]
        if not wrong_type_email:
            tests_passed += 1
        else:
            issues.append(Issue(
                severity=SEVERITY_LOW,
                category='ux',
                element_type='form',
                description='Email field should use type="email"',
                fix_instruction=(
                    f"Change email input type from 'text' to 'email'. "
                    f"This enables browser validation, mobile keyboard optimization, "
                    f"and autofill. Change: <input type='text' name='email'/> to "
                    f"<input type='email' name='email'/>."
                ),
                location=location
            ))

        # Test 8: Phone fields have correct type
        tests_run += 1
        phone_fields = [f for f in fields if any(p in f.get('name', '').lower() for p in ['phone', 'tel', 'mobile'])]
        wrong_type_phone = [f for f in phone_fields if f.get('type') not in ['tel', 'hidden']]
        if not wrong_type_phone:
            tests_passed += 1
        else:
            issues.append(Issue(
                severity=SEVERITY_LOW,
                category='ux',
                element_type='form',
                description='Phone field should use type="tel"',
                fix_instruction=(
                    f"Change phone input type from 'text' to 'tel'. "
                    f"This shows numeric keyboard on mobile devices. "
                    f"Change: <input type='text' name='phone'/> to "
                    f"<input type='tel' name='phone'/>."
                ),
                location=location
            ))

        return ElementTestResult(
            element_type='form',
            element_id=form_id or f"form_{location['line_number']}",
            location=location,
            tests_run=tests_run,
            tests_passed=tests_passed,
            tests_failed=tests_run - tests_passed,
            issues=issues,
            details={
                'action': action,
                'method': method,
                'field_count': len(fields),
                'has_submit': has_submit,
                'has_password': has_password
            }
        )

    def test_menu(
        self,
        menu_data: Dict[str, Any],
        page_url: str
    ) -> ElementTestResult:
        """
        Test a navigation menu element comprehensively.

        Args:
            menu_data: Menu element data from parser
            page_url: URL of the page containing the menu

        Returns:
            ElementTestResult with all test outcomes
        """
        issues = []
        tests_run = 0
        tests_passed = 0

        tag = menu_data.get('tag', 'nav')
        element_id = menu_data.get('id')
        classes = menu_data.get('classes', [])
        attributes = menu_data.get('attributes', {})
        children_count = menu_data.get('children_count', 0)

        location = {
            'page_url': page_url,
            'css_selector': menu_data.get('css_selector', ''),
            'xpath': menu_data.get('xpath', ''),
            'line_number': menu_data.get('line_number', 0)
        }

        # Test 1: Menu uses semantic nav element
        tests_run += 1
        if tag == 'nav' or attributes.get('role') == 'navigation':
            tests_passed += 1
        else:
            issues.append(Issue(
                severity=SEVERITY_MEDIUM,
                category='semantics',
                element_type='menu',
                description='Navigation menu should use <nav> element',
                fix_instruction=(
                    f"Wrap navigation menu in a <nav> element for proper semantics. "
                    f"Change: <div class='menu'>...</div> to <nav class='menu'>...</nav>. "
                    f"Or add role='navigation' if <nav> cannot be used. "
                    f"This helps assistive technologies identify navigation regions."
                ),
                location=location,
                wcag_reference='1.3.1 Info and Relationships (Level A)'
            ))

        # Test 2: Menu has accessible label (if multiple navs)
        tests_run += 1
        has_label = attributes.get('aria-label') or attributes.get('aria-labelledby')
        if tag == 'nav' and not has_label:
            issues.append(Issue(
                severity=SEVERITY_LOW,
                category='accessibility',
                element_type='menu',
                description='Navigation should have aria-label',
                fix_instruction=(
                    f"Add aria-label to distinguish this navigation from others. "
                    f"Example: <nav aria-label='Main navigation'>...</nav> or "
                    f"<nav aria-label='Footer links'>...</nav>. "
                    f"This is especially important when page has multiple nav regions."
                ),
                location=location,
                wcag_reference='2.4.1 Bypass Blocks (Level A)'
            ))
        else:
            tests_passed += 1

        # Test 3: Menu uses list structure
        tests_run += 1
        # We would check if children include ul/ol
        has_list_class = any(c in str(classes).lower() for c in ['menu', 'nav', 'navigation'])
        if has_list_class or children_count > 0:
            tests_passed += 1
        else:
            issues.append(Issue(
                severity=SEVERITY_LOW,
                category='semantics',
                element_type='menu',
                description='Menu should use list structure (ul/ol)',
                fix_instruction=(
                    f"Structure menu items in a list. Example: "
                    f"<nav><ul><li><a href='/'>Home</a></li><li><a href='/about'>About</a></li></ul></nav>. "
                    f"Lists provide structure that assistive technologies can convey to users, "
                    f"such as the number of items in the menu."
                ),
                location=location
            ))

        # Test 4: Current page indicated
        tests_run += 1
        has_current = 'current' in str(classes).lower() or 'active' in str(classes).lower()
        if has_current:
            tests_passed += 1
        else:
            issues.append(Issue(
                severity=SEVERITY_LOW,
                category='accessibility',
                element_type='menu',
                description='Current page should be indicated in menu',
                fix_instruction=(
                    f"Indicate the current page in navigation. "
                    f"Add aria-current='page' to current page link: "
                    f"<a href='/about' aria-current='page'>About</a>. "
                    f"Also add visual styling: .nav-link[aria-current='page'] {{ font-weight: bold; }}."
                ),
                location=location,
                wcag_reference='2.4.4 Link Purpose (In Context) (Level A)'
            ))

        # Test 5: Dropdown menus have proper ARIA
        tests_run += 1
        has_dropdown_class = any(d in str(classes).lower() for d in ['dropdown', 'submenu', 'has-children'])
        if not has_dropdown_class:
            tests_passed += 1  # Not a dropdown, pass
        else:
            has_aria_expanded = attributes.get('aria-expanded') is not None
            has_aria_haspopup = attributes.get('aria-haspopup') is not None

            if has_aria_expanded or has_aria_haspopup:
                tests_passed += 1
            else:
                issues.append(Issue(
                    severity=SEVERITY_MEDIUM,
                    category='accessibility',
                    element_type='menu',
                    description='Dropdown menu missing ARIA attributes',
                    fix_instruction=(
                        f"Add ARIA attributes for dropdown accessibility. "
                        f"On the trigger: aria-expanded='false' (toggle with JS), aria-haspopup='menu'. "
                        f"Example: <button aria-expanded='false' aria-haspopup='menu'>Products</button>. "
                        f"Update aria-expanded to 'true' when dropdown is open."
                    ),
                    location=location,
                    wcag_reference='4.1.2 Name, Role, Value (Level A)'
                ))

        return ElementTestResult(
            element_type='menu',
            element_id=element_id or f"nav_{location['line_number']}",
            location=location,
            tests_run=tests_run,
            tests_passed=tests_passed,
            tests_failed=tests_run - tests_passed,
            issues=issues,
            details={
                'tag': tag,
                'has_label': bool(attributes.get('aria-label')),
                'children_count': children_count,
                'classes': classes
            }
        )

    def get_all_issues(self) -> List[Issue]:
        """Get all issues found during testing."""
        return self._issues

    def get_summary(self) -> Dict[str, Any]:
        """Get testing summary."""
        all_issues = []
        total_tests = 0
        total_passed = 0

        for result in self._results:
            all_issues.extend(result.issues)
            total_tests += result.tests_run
            total_passed += result.tests_passed

        issues_by_severity = {}
        for issue in all_issues:
            issues_by_severity[issue.severity] = issues_by_severity.get(issue.severity, 0) + 1

        return {
            'total_tests': total_tests,
            'tests_passed': total_passed,
            'tests_failed': total_tests - total_passed,
            'pass_rate': (total_passed / total_tests * 100) if total_tests > 0 else 0,
            'total_issues': len(all_issues),
            'issues_by_severity': issues_by_severity,
            'elements_tested': len(self._results)
        }
