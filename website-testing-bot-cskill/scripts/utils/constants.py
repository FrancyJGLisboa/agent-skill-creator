"""
Constants and configuration values for the Website Testing Bot.

This module contains all constant values, thresholds, and configuration
defaults used throughout the testing system.
"""

from typing import Dict, List, Any

# =============================================================================
# SEVERITY LEVELS
# =============================================================================

SEVERITY_CRITICAL = "critical"  # Blocks launch, must fix immediately
SEVERITY_HIGH = "high"          # Should fix before launch
SEVERITY_MEDIUM = "medium"      # Should fix, but not blocking
SEVERITY_LOW = "low"            # Nice to fix, minor improvement
SEVERITY_INFO = "info"          # Informational, no action required

SEVERITY_ORDER = {
    SEVERITY_CRITICAL: 0,
    SEVERITY_HIGH: 1,
    SEVERITY_MEDIUM: 2,
    SEVERITY_LOW: 3,
    SEVERITY_INFO: 4
}

# =============================================================================
# READINESS STATUS
# =============================================================================

READINESS_READY = "READY"
READINESS_NEEDS_POLISHING = "NEEDS_POLISHING"
READINESS_UNDER_CONSTRUCTION = "UNDER_CONSTRUCTION"

READINESS_CRITERIA = {
    READINESS_READY: {
        "max_critical_issues": 0,
        "max_high_issues": 0,
        "min_accessibility_score": 80,
        "min_security_grade": "B",
        "min_performance_grade": "B",
        "broken_links_allowed": 0
    },
    READINESS_NEEDS_POLISHING: {
        "max_critical_issues": 0,
        "max_high_issues": 5,
        "min_accessibility_score": 60,
        "min_security_grade": "C",
        "min_performance_grade": "C",
        "broken_links_allowed": 5
    },
    READINESS_UNDER_CONSTRUCTION: {
        "max_critical_issues": float('inf'),
        "max_high_issues": float('inf'),
        "min_accessibility_score": 0,
        "min_security_grade": "F",
        "min_performance_grade": "F",
        "broken_links_allowed": float('inf')
    }
}

# =============================================================================
# COMMERCIAL READINESS GRADES
# =============================================================================

COMMERCIAL_GRADES = {
    "A+": {"min_score": 95, "max_users": 100000, "max_response_ms": 100},
    "A": {"min_score": 90, "max_users": 50000, "max_response_ms": 200},
    "B+": {"min_score": 85, "max_users": 25000, "max_response_ms": 500},
    "B": {"min_score": 80, "max_users": 10000, "max_response_ms": 1000},
    "C+": {"min_score": 70, "max_users": 5000, "max_response_ms": 2000},
    "C": {"min_score": 60, "max_users": 1000, "max_response_ms": 3000},
    "D": {"min_score": 40, "max_users": 500, "max_response_ms": 5000},
    "F": {"min_score": 0, "max_users": 100, "max_response_ms": float('inf')}
}

COMMERCIAL_GRADE_DESCRIPTIONS = {
    "A+": "Enterprise-ready: 100k+ concurrent users, <100ms response, zero critical issues",
    "A": "Production-ready: 50k-100k users, <200ms response, no critical issues",
    "B+": "Near-ready: 25k-50k users, <500ms response, minor issues only",
    "B": "Viable: 10k-25k users, <1s response, some issues to address",
    "C+": "Developing: 5k-10k users, acceptable performance, notable issues",
    "C": "Early stage: 1k-5k users, performance concerns, multiple issues",
    "D": "Not ready: <1k users, significant performance issues, many problems",
    "F": "Critical: Fundamental issues preventing commercial use"
}

# =============================================================================
# UNIQUENESS SCORING
# =============================================================================

UNIQUENESS_THRESHOLDS = {
    "highly_original": {"min": 90, "max": 100, "label": "Highly Original"},
    "distinctive": {"min": 75, "max": 89, "label": "Distinctive"},
    "moderate": {"min": 50, "max": 74, "label": "Moderate"},
    "generic": {"min": 25, "max": 49, "label": "Generic"},
    "template_clone": {"min": 0, "max": 24, "label": "Template Clone"}
}

UNIQUENESS_WEIGHTS = {
    "visual_design": 0.25,
    "layout_structure": 0.20,
    "functionality": 0.20,
    "content_presentation": 0.15,
    "interactive_elements": 0.10,
    "brand_identity": 0.10
}

# =============================================================================
# WCAG GUIDELINES
# =============================================================================

WCAG_GUIDELINES = {
    "1.1.1": {
        "name": "Non-text Content",
        "level": "A",
        "description": "All non-text content has a text alternative"
    },
    "1.3.1": {
        "name": "Info and Relationships",
        "level": "A",
        "description": "Information and relationships conveyed through presentation are programmatically determinable"
    },
    "1.4.1": {
        "name": "Use of Color",
        "level": "A",
        "description": "Color is not the only visual means of conveying information"
    },
    "1.4.3": {
        "name": "Contrast (Minimum)",
        "level": "AA",
        "description": "Text has a contrast ratio of at least 4.5:1"
    },
    "1.4.4": {
        "name": "Resize Text",
        "level": "AA",
        "description": "Text can be resized up to 200% without loss of functionality"
    },
    "1.4.10": {
        "name": "Reflow",
        "level": "AA",
        "description": "Content reflows without horizontal scrolling at 320px width"
    },
    "1.4.11": {
        "name": "Non-text Contrast",
        "level": "AA",
        "description": "UI components have 3:1 contrast against adjacent colors"
    },
    "2.1.1": {
        "name": "Keyboard",
        "level": "A",
        "description": "All functionality is operable via keyboard"
    },
    "2.1.2": {
        "name": "No Keyboard Trap",
        "level": "A",
        "description": "Keyboard focus can be moved away using only keyboard"
    },
    "2.4.1": {
        "name": "Bypass Blocks",
        "level": "A",
        "description": "A mechanism exists to bypass repeated content"
    },
    "2.4.2": {
        "name": "Page Titled",
        "level": "A",
        "description": "Pages have titles that describe topic or purpose"
    },
    "2.4.3": {
        "name": "Focus Order",
        "level": "A",
        "description": "Focus order preserves meaning and operability"
    },
    "2.4.4": {
        "name": "Link Purpose (In Context)",
        "level": "A",
        "description": "Link purpose can be determined from link text or context"
    },
    "2.4.6": {
        "name": "Headings and Labels",
        "level": "AA",
        "description": "Headings and labels describe topic or purpose"
    },
    "2.4.7": {
        "name": "Focus Visible",
        "level": "AA",
        "description": "Keyboard focus indicator is visible"
    },
    "3.1.1": {
        "name": "Language of Page",
        "level": "A",
        "description": "Default language of page is programmatically determinable"
    },
    "3.2.1": {
        "name": "On Focus",
        "level": "A",
        "description": "Focus does not cause unexpected context change"
    },
    "3.2.2": {
        "name": "On Input",
        "level": "A",
        "description": "Input does not cause unexpected context change"
    },
    "3.3.1": {
        "name": "Error Identification",
        "level": "A",
        "description": "Input errors are identified and described in text"
    },
    "3.3.2": {
        "name": "Labels or Instructions",
        "level": "A",
        "description": "Labels or instructions provided for user input"
    },
    "4.1.1": {
        "name": "Parsing",
        "level": "A",
        "description": "Elements have complete start/end tags, no duplicates"
    },
    "4.1.2": {
        "name": "Name, Role, Value",
        "level": "A",
        "description": "UI components have accessible name and role"
    }
}

# =============================================================================
# SECURITY HEADERS
# =============================================================================

SECURITY_HEADERS = {
    "Strict-Transport-Security": {
        "severity": SEVERITY_HIGH,
        "description": "HSTS header enforces HTTPS connections",
        "recommended": "max-age=31536000; includeSubDomains"
    },
    "Content-Security-Policy": {
        "severity": SEVERITY_HIGH,
        "description": "CSP prevents XSS and injection attacks",
        "recommended": "default-src 'self'; script-src 'self'"
    },
    "X-Frame-Options": {
        "severity": SEVERITY_MEDIUM,
        "description": "Prevents clickjacking attacks",
        "recommended": "DENY or SAMEORIGIN"
    },
    "X-Content-Type-Options": {
        "severity": SEVERITY_MEDIUM,
        "description": "Prevents MIME type sniffing",
        "recommended": "nosniff"
    },
    "X-XSS-Protection": {
        "severity": SEVERITY_LOW,
        "description": "Legacy XSS filter (deprecated but still useful)",
        "recommended": "1; mode=block"
    },
    "Referrer-Policy": {
        "severity": SEVERITY_LOW,
        "description": "Controls referrer information sent with requests",
        "recommended": "strict-origin-when-cross-origin"
    },
    "Permissions-Policy": {
        "severity": SEVERITY_LOW,
        "description": "Controls browser features and APIs",
        "recommended": "geolocation=(), microphone=(), camera=()"
    }
}

# =============================================================================
# PERFORMANCE THRESHOLDS
# =============================================================================

PERFORMANCE_THRESHOLDS = {
    "lcp": {  # Largest Contentful Paint
        "good": 2500,      # ms
        "needs_improvement": 4000,
        "poor": float('inf')
    },
    "fid": {  # First Input Delay
        "good": 100,       # ms
        "needs_improvement": 300,
        "poor": float('inf')
    },
    "cls": {  # Cumulative Layout Shift
        "good": 0.1,
        "needs_improvement": 0.25,
        "poor": float('inf')
    },
    "ttfb": {  # Time to First Byte
        "good": 200,       # ms
        "needs_improvement": 500,
        "poor": float('inf')
    },
    "fcp": {  # First Contentful Paint
        "good": 1800,      # ms
        "needs_improvement": 3000,
        "poor": float('inf')
    },
    "tti": {  # Time to Interactive
        "good": 3800,      # ms
        "needs_improvement": 7300,
        "poor": float('inf')
    },
    "page_weight": {  # Total page size
        "good": 1500000,   # bytes (1.5MB)
        "needs_improvement": 3000000,  # 3MB
        "poor": float('inf')
    },
    "request_count": {
        "good": 30,
        "needs_improvement": 50,
        "poor": float('inf')
    }
}

# =============================================================================
# HTTP CONFIGURATION
# =============================================================================

DEFAULT_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_DELAY_BASE = 2  # seconds, exponential backoff

DEFAULT_USER_AGENT = (
    "WebsiteTestingBot/1.0 "
    "(Compatible; Website Quality Assessment Tool; "
    "+https://github.com/agent-skill-creator)"
)

HTTP_SUCCESS_CODES = {200, 201, 202, 204, 301, 302, 303, 304, 307, 308}
HTTP_ERROR_CODES = {400, 401, 403, 404, 405, 408, 429, 500, 502, 503, 504}

# =============================================================================
# CRAWLING CONFIGURATION
# =============================================================================

DEFAULT_MAX_DEPTH = 10
DEFAULT_MAX_PAGES = 500
DEFAULT_CRAWL_DELAY = 0.5  # seconds between requests

SKIP_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.zip', '.rar', '.tar', '.gz', '.7z',
    '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv',
    '.exe', '.dmg', '.pkg', '.deb', '.rpm'
}

SKIP_URL_PATTERNS = [
    r'mailto:',
    r'tel:',
    r'javascript:',
    r'#$',
    r'\?.*logout',
    r'\?.*signout',
    r'/wp-admin/',
    r'/administrator/',
    r'/admin/'
]

# =============================================================================
# TEMPLATE FINGERPRINTS (for uniqueness detection)
# =============================================================================

KNOWN_TEMPLATE_FINGERPRINTS = {
    "bootstrap": {
        "css_classes": ["container", "row", "col-", "btn-primary", "navbar-expand"],
        "meta_generators": ["Bootstrap"],
        "css_files": ["bootstrap.min.css", "bootstrap.css"]
    },
    "wordpress": {
        "css_classes": ["wp-block", "entry-content", "wp-caption"],
        "meta_generators": ["WordPress"],
        "paths": ["/wp-content/", "/wp-includes/"]
    },
    "squarespace": {
        "css_classes": ["sqs-block", "sqs-layout"],
        "meta_generators": ["Squarespace"],
        "domains": ["squarespace.com", "sqsp.net"]
    },
    "wix": {
        "css_classes": ["comp-", "_1EZhW"],
        "meta_generators": ["Wix.com"],
        "domains": ["wix.com", "wixsite.com"]
    },
    "shopify": {
        "css_classes": ["shopify-section", "product-card"],
        "meta_generators": ["Shopify"],
        "paths": ["/cdn.shopify.com/"]
    },
    "tailwind": {
        "css_classes": ["flex", "grid", "px-", "py-", "bg-", "text-"],
        "css_files": ["tailwind.min.css", "tailwind.css"]
    },
    "material_ui": {
        "css_classes": ["MuiButton", "MuiPaper", "MuiTypography"],
        "css_files": ["material-ui"]
    },
    "foundation": {
        "css_classes": ["grid-x", "cell", "button-group"],
        "css_files": ["foundation.min.css"]
    }
}

# =============================================================================
# ISSUE CATEGORIES
# =============================================================================

ISSUE_CATEGORIES = {
    "broken_link": "Broken or dead link",
    "broken_image": "Missing or broken image",
    "broken_resource": "Missing CSS, JS, or other resource",
    "form_error": "Form functionality issue",
    "button_error": "Button functionality issue",
    "menu_error": "Navigation/menu issue",
    "accessibility": "Accessibility violation",
    "security": "Security vulnerability",
    "performance": "Performance issue",
    "seo": "SEO problem",
    "mobile": "Mobile responsiveness issue",
    "content": "Content quality issue",
    "ux": "User experience problem"
}

# =============================================================================
# COLOR CONTRAST REQUIREMENTS
# =============================================================================

CONTRAST_RATIOS = {
    "normal_text_aa": 4.5,      # WCAG AA for normal text
    "large_text_aa": 3.0,       # WCAG AA for large text (18pt+ or 14pt bold)
    "normal_text_aaa": 7.0,     # WCAG AAA for normal text
    "large_text_aaa": 4.5,      # WCAG AAA for large text
    "ui_components": 3.0,       # WCAG 2.1 for UI components
    "graphical_objects": 3.0    # WCAG 2.1 for graphical objects
}

# Large text definition: 18pt (24px) regular or 14pt (18.67px) bold
LARGE_TEXT_SIZE_PX = 24
LARGE_TEXT_BOLD_SIZE_PX = 18.67

# =============================================================================
# REPORT CONFIGURATION
# =============================================================================

REPORT_SECTIONS = [
    "executive_summary",
    "grades",
    "element_tests",
    "performance_tests",
    "security_tests",
    "accessibility_tests",
    "uniqueness_analysis",
    "issues_list",
    "agent_handoff",
    "recommendations"
]

MAX_ISSUES_PER_CATEGORY = 100  # Limit issues per category in report
