# Website Testing Bot - Ultimate Commercial Readiness Assessment Tool

## Executive Summary

The Website Testing Bot is a comprehensive, exhaustive website quality assurance system designed to be the definitive "sign-off" tool for commercial website launches. This skill performs deep analysis of every element, functionality, and aspect of a website, producing detailed reports with explicit fix instructions suitable for handoff to another agent or developer who has zero prior knowledge of the site.

**Core Mission**: Provide the ultimate pre-launch validation that answers three critical questions:
1. **Can this website handle commercial-scale usage?** (Commercial Readiness Grade)
2. **Is this website unique and professional, not a cookie-cutter template?** (Uniqueness Score)
3. **Is this website ready to launch, or what specific work remains?** (Readiness Status)

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Testing Modules](#testing-modules)
3. [Grading Systems](#grading-systems)
4. [Agent Handoff Protocol](#agent-handoff-protocol)
5. [Technical Implementation](#technical-implementation)
6. [Usage Guide](#usage-guide)
7. [Output Formats](#output-formats)
8. [Error Handling](#error-handling)
9. [Performance Optimization](#performance-optimization)
10. [Security Considerations](#security-considerations)

---

## Architecture Overview

### System Design Philosophy

The Website Testing Bot follows a **Crawl → Test → Analyze → Grade → Report** pipeline architecture. This ensures systematic coverage of every website element while maintaining clear separation of concerns between discovery, validation, assessment, and reporting phases.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        WEBSITE TESTING BOT                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐               │
│  │   CRAWLER    │───▶│   TESTERS    │───▶│  ANALYZERS   │               │
│  │              │    │              │    │              │               │
│  │ - Site Map   │    │ - Elements   │    │ - Uniqueness │               │
│  │ - Pages      │    │ - Performance│    │ - Commercial │               │
│  │ - Resources  │    │ - Security   │    │ - Readiness  │               │
│  │ - Assets     │    │ - A11y       │    │              │               │
│  └──────────────┘    └──────────────┘    └──────────────┘               │
│          │                   │                   │                       │
│          └───────────────────┴───────────────────┘                       │
│                              │                                           │
│                              ▼                                           │
│                    ┌──────────────────┐                                  │
│                    │  REPORT GENERATOR │                                 │
│                    │                   │                                 │
│                    │ - Grading         │                                 │
│                    │ - Issue Lists     │                                 │
│                    │ - Fix Instructions│                                 │
│                    │ - Agent Handoff   │                                 │
│                    └──────────────────┘                                  │
│                              │                                           │
│                              ▼                                           │
│                    ┌──────────────────┐                                  │
│                    │   FINAL OUTPUT   │                                  │
│                    │                   │                                 │
│                    │ - JSON Report     │                                 │
│                    │ - Handoff Doc     │                                 │
│                    │ - Grades & Scores │                                 │
│                    └──────────────────┘                                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
website-testing-bot-cskill/
├── .claude-plugin/
│   └── marketplace.json          # Activation configuration (4-layer system)
├── SKILL.md                      # This documentation file
├── scripts/
│   ├── __init__.py               # Package initialization
│   ├── main.py                   # Main orchestrator
│   ├── crawlers/
│   │   ├── __init__.py
│   │   ├── site_crawler.py       # Full site discovery crawler
│   │   ├── page_parser.py        # Individual page parsing
│   │   └── resource_collector.py # Asset and resource collection
│   ├── testers/
│   │   ├── __init__.py
│   │   ├── element_tester.py     # Button, link, image, form testing
│   │   ├── performance_tester.py # Load and speed testing
│   │   ├── security_tester.py    # Vulnerability scanning
│   │   ├── accessibility_tester.py # WCAG compliance testing
│   │   └── functionality_tester.py # Interactive element testing
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── uniqueness_analyzer.py    # Template detection, originality scoring
│   │   ├── commercial_analyzer.py    # Scale capacity, load estimation
│   │   └── readiness_analyzer.py     # Overall launch readiness
│   ├── reporters/
│   │   ├── __init__.py
│   │   ├── report_generator.py       # Main report creation
│   │   ├── agent_handoff_generator.py # Zero-assumption fix instructions
│   │   └── grade_calculator.py       # Scoring and grading logic
│   └── utils/
│       ├── __init__.py
│       ├── http_client.py            # Request handling with retries
│       ├── html_parser.py            # DOM manipulation utilities
│       ├── validators.py             # Input validation
│       └── constants.py              # Configuration constants
├── templates/
│   ├── report_template.json          # Report structure template
│   └── handoff_template.md           # Agent handoff document template
├── references/
│   ├── wcag_guidelines.md            # Accessibility reference
│   ├── security_checklist.md         # Security testing reference
│   └── performance_metrics.md        # Performance benchmarks
└── requirements.txt                  # Python dependencies
```

---

## Testing Modules

### 1. Site Crawler Module

The crawler module performs exhaustive discovery of all website content, creating a complete map of pages, resources, and interactive elements.

#### Capabilities

**Page Discovery**:
- Follows all internal links recursively up to configurable depth (default: 10 levels)
- Respects robots.txt directives while noting excluded content
- Identifies orphaned pages (pages not linked from anywhere)
- Maps URL structure and hierarchy
- Detects redirect chains and loops

**Resource Collection**:
- Catalogs all images with dimensions, file sizes, and formats
- Lists all CSS files with load order and file sizes
- Inventories all JavaScript files with execution order
- Identifies all fonts (local and external)
- Detects all external API calls and third-party integrations
- Maps all video and audio resources

**Element Inventory**:
- Counts and catalogs all buttons (by type: submit, button, link-styled)
- Lists all forms with their fields and validation rules
- Maps all navigation menus (header, footer, sidebar, mobile)
- Identifies all modals, popups, and overlays
- Catalogs all tooltips and hover states
- Lists all interactive elements (sliders, carousels, accordions, tabs)

#### Output Format

```json
{
  "crawl_summary": {
    "total_pages": 47,
    "total_resources": 234,
    "total_elements": 1893,
    "crawl_time_seconds": 45.2,
    "max_depth_reached": 6
  },
  "pages": [
    {
      "url": "https://example.com/about",
      "title": "About Us - Example Company",
      "status_code": 200,
      "load_time_ms": 342,
      "links_found": 23,
      "images_found": 8,
      "forms_found": 1,
      "depth_level": 1
    }
  ],
  "resources": {
    "images": [...],
    "stylesheets": [...],
    "scripts": [...],
    "fonts": [...],
    "media": [...]
  },
  "elements": {
    "buttons": [...],
    "links": [...],
    "forms": [...],
    "menus": [...],
    "interactive": [...]
  }
}
```

### 2. Element Tester Module

The element tester validates every interactive and static element on the website, ensuring proper functionality and user experience.

#### Button Testing

For every button found on the site:

**Functional Tests**:
- Click functionality (does the button respond to clicks?)
- Keyboard accessibility (can it be activated via Enter/Space?)
- Disabled state handling (is disabled state visually clear?)
- Loading state behavior (does it show loading feedback?)
- Form submission handling (for submit buttons)
- Navigation behavior (for link-styled buttons)

**Visual Tests**:
- Hover state exists and is visible
- Focus state exists and is visible (keyboard navigation)
- Active/pressed state feedback
- Disabled state visual differentiation
- Consistent sizing with other buttons
- Text contrast against background

**Output per Button**:
```json
{
  "element_id": "btn_submit_contact",
  "location": {
    "page_url": "https://example.com/contact",
    "css_selector": "#contact-form button[type='submit']",
    "xpath": "//form[@id='contact-form']//button[@type='submit']",
    "line_in_source": 247
  },
  "tests_passed": 11,
  "tests_failed": 2,
  "issues": [
    {
      "severity": "high",
      "type": "accessibility",
      "description": "Button has no visible focus state when navigated to via keyboard",
      "fix_instruction": "Add CSS focus state: #contact-form button[type='submit']:focus { outline: 2px solid #0066cc; outline-offset: 2px; }",
      "wcag_reference": "2.4.7 Focus Visible (Level AA)"
    },
    {
      "severity": "medium",
      "type": "ux",
      "description": "No loading feedback when form is submitting",
      "fix_instruction": "Add loading state: 1) Add spinner icon inside button, 2) Add disabled attribute during submission, 3) Change button text to 'Sending...' during submission"
    }
  ]
}
```

#### Link Testing

For every link (anchor element) on the site:

**Validation Tests**:
- URL is valid and properly formatted
- Destination exists (not 404)
- No redirect loops
- External links have appropriate rel attributes
- Mailto links have valid email format
- Tel links have valid phone format
- Download links point to existing files

**Behavior Tests**:
- Opens in correct target (same window vs new tab)
- Anchor links scroll to correct position
- Hash links navigate to correct section
- Query parameters are properly encoded

**Security Tests**:
- External links have rel="noopener noreferrer" when target="_blank"
- No links to suspicious domains
- No mixed content (HTTP links on HTTPS page)

**Output per Link**:
```json
{
  "element_id": "link_45",
  "href": "https://example.com/products/widget-deluxe",
  "text": "Widget Deluxe",
  "location": {
    "page_url": "https://example.com/products",
    "css_selector": ".product-grid .product-card:nth-child(3) a.product-link",
    "line_in_source": 189
  },
  "status": "broken",
  "http_status": 404,
  "issues": [
    {
      "severity": "critical",
      "type": "broken_link",
      "description": "Link destination returns 404 Not Found",
      "fix_instruction": "The page at '/products/widget-deluxe' does not exist. Either: 1) Create the page at this URL, OR 2) Update the href to point to the correct URL, OR 3) Remove this link if the product no longer exists. The link is located in the file that generates the product grid - look for the product card template and ensure the URL generation logic includes the correct slug."
    }
  ]
}
```

#### Image Testing

For every image on the site:

**Loading Tests**:
- Image URL returns 200 OK
- Image loads within acceptable time (<2 seconds)
- Image format is web-optimized (WebP, optimized JPEG/PNG)
- Image dimensions are appropriate for container
- Responsive images have srcset defined

**Optimization Tests**:
- File size is reasonable for dimensions
- Modern format alternatives provided (WebP)
- Lazy loading implemented for below-fold images
- Width and height attributes set (prevents layout shift)

**Accessibility Tests**:
- Alt text is present
- Alt text is descriptive (not "image" or filename)
- Decorative images have empty alt=""
- Complex images have long description
- SVGs have appropriate title/description

**Output per Image**:
```json
{
  "element_id": "img_hero_banner",
  "src": "/images/hero-banner.jpg",
  "location": {
    "page_url": "https://example.com/",
    "css_selector": ".hero-section img",
    "line_in_source": 67
  },
  "dimensions": {
    "natural": "3840x2160",
    "displayed": "1920x1080"
  },
  "file_size_kb": 2847,
  "format": "jpeg",
  "issues": [
    {
      "severity": "high",
      "type": "performance",
      "description": "Image file size is 2.8MB which is extremely large for web use",
      "fix_instruction": "Optimize this image: 1) Resize to maximum display size (1920x1080 based on CSS), 2) Compress using lossy compression (quality 80-85%), 3) Convert to WebP format with JPEG fallback, 4) Use responsive images with srcset. Target file size should be under 200KB. Command: 'cwebp -q 85 hero-banner.jpg -o hero-banner.webp' or use online tool like squoosh.app"
    },
    {
      "severity": "medium",
      "type": "accessibility",
      "description": "Alt text is generic: 'banner image'",
      "fix_instruction": "Replace alt text with descriptive content. Current: alt='banner image'. Suggested: alt='Professional team collaborating in modern office space - Example Company'. The alt text should describe what the image shows and convey the same information a sighted user would receive."
    },
    {
      "severity": "medium",
      "type": "performance",
      "description": "Missing width and height attributes causing layout shift",
      "fix_instruction": "Add explicit dimensions to prevent Cumulative Layout Shift (CLS). Add: width='1920' height='1080' to the img tag. This allows the browser to reserve space before the image loads."
    }
  ]
}
```

#### Form Testing

For every form on the site:

**Structure Tests**:
- All fields have associated labels
- Labels are properly connected via for/id
- Required fields are marked
- Field types are appropriate (email for email, tel for phone, etc.)
- Submit button exists and is properly configured

**Validation Tests**:
- Required field validation works
- Email format validation works
- Phone number validation works
- Password strength requirements clear
- Error messages are clear and helpful
- Success feedback is provided

**Functionality Tests**:
- Form submits successfully
- Form data reaches server
- Response handling works
- Error responses are handled gracefully
- Timeout handling implemented

**Accessibility Tests**:
- Form is keyboard navigable
- Error messages are announced to screen readers
- Focus moves logically through fields
- Invalid fields are clearly identified

**Security Tests**:
- CSRF token present
- Form submits over HTTPS
- Sensitive fields have autocomplete off where appropriate
- Password fields are masked

**Output per Form**:
```json
{
  "form_id": "contact-form",
  "action": "/api/contact",
  "method": "POST",
  "location": {
    "page_url": "https://example.com/contact",
    "css_selector": "#contact-form",
    "line_in_source": 156
  },
  "fields": [
    {
      "name": "email",
      "type": "email",
      "required": true,
      "has_label": true,
      "issues": []
    },
    {
      "name": "message",
      "type": "textarea",
      "required": true,
      "has_label": false,
      "issues": [
        {
          "severity": "high",
          "type": "accessibility",
          "description": "Textarea field 'message' has no associated label",
          "fix_instruction": "Add a label element for this textarea. Add: <label for='message'>Your Message</label> before the textarea, and add id='message' to the textarea element. The label provides context for screen reader users and improves click target for all users."
        }
      ]
    }
  ],
  "submission_test": {
    "status": "failed",
    "error": "Server returned 500 Internal Server Error",
    "issues": [
      {
        "severity": "critical",
        "type": "functionality",
        "description": "Form submission fails with 500 error",
        "fix_instruction": "The form endpoint '/api/contact' is returning a server error. Debug steps: 1) Check server logs for the specific error message, 2) Verify the endpoint handler exists and is properly configured, 3) Ensure database connection is working if form saves to database, 4) Check that all required server-side validation is passing, 5) Verify email service configuration if form sends emails. This is a backend issue requiring server-side debugging."
      }
    ]
  }
}
```

#### Menu Testing

For every navigation menu:

**Structure Tests**:
- Menu has proper semantic structure (nav, ul, li)
- Active page is indicated
- Dropdown menus are properly nested
- Mobile menu exists and functions

**Functionality Tests**:
- All menu links work
- Dropdowns open on hover/click
- Dropdowns close appropriately
- Mobile menu toggle works
- Mobile menu closes on link click

**Accessibility Tests**:
- Menu is keyboard navigable
- Dropdown menus accessible via keyboard
- Current page indicated to screen readers
- Skip navigation link present
- ARIA attributes correct for dropdowns

### 3. Performance Tester Module

Comprehensive performance analysis to estimate commercial capacity.

#### Page Load Metrics

**Core Web Vitals**:
- **LCP (Largest Contentful Paint)**: Target < 2.5s
- **FID (First Input Delay)**: Target < 100ms
- **CLS (Cumulative Layout Shift)**: Target < 0.1

**Additional Metrics**:
- **TTFB (Time to First Byte)**: Server response time
- **FCP (First Contentful Paint)**: First visible content
- **TTI (Time to Interactive)**: Page becomes usable
- **Total Blocking Time**: Main thread blocking
- **Speed Index**: Visual loading progress

#### Resource Analysis

**File Size Analysis**:
- Total page weight (target < 3MB)
- JavaScript bundle size (target < 500KB)
- CSS file size (target < 200KB)
- Image optimization score
- Font loading impact

**Request Analysis**:
- Total HTTP requests (target < 50)
- Third-party request count
- Request waterfall optimization
- Render-blocking resource identification
- Cache effectiveness

#### Load Capacity Estimation

The system estimates maximum concurrent users through:

**Server Response Analysis**:
- Baseline response time measurement
- Response time under simulated load
- Error rate tracking
- Resource utilization patterns

**Capacity Calculation**:
```
Estimated Max Users = (Server Capacity / Avg Request Size) × (1 / Avg Requests Per User) × Concurrency Factor
```

**Output**:
```json
{
  "performance_summary": {
    "overall_grade": "B+",
    "core_web_vitals": {
      "lcp_ms": 2100,
      "lcp_status": "good",
      "fid_ms": 45,
      "fid_status": "good",
      "cls_score": 0.15,
      "cls_status": "needs_improvement"
    },
    "capacity_estimate": {
      "max_concurrent_users": 15000,
      "recommended_concurrent_users": 10000,
      "bottleneck": "Database query optimization needed",
      "scaling_recommendation": "Consider implementing read replicas for database"
    }
  },
  "issues": [
    {
      "severity": "high",
      "type": "performance",
      "metric": "CLS",
      "description": "Cumulative Layout Shift of 0.15 exceeds 0.1 threshold",
      "fix_instruction": "Layout shift is caused by: 1) Images without dimensions on lines 67, 145, 289 - add width and height attributes, 2) Dynamic ad container at line 234 - reserve space with min-height, 3) Font loading causing text reflow - add font-display: swap to @font-face rules in /css/fonts.css"
    }
  ]
}
```

### 4. Security Tester Module

Security vulnerability scanning focused on common web vulnerabilities.

#### SSL/TLS Analysis

- Certificate validity and expiration
- Certificate chain completeness
- Protocol version (TLS 1.2+)
- Cipher suite strength
- HSTS header presence

#### Header Security

- Content-Security-Policy analysis
- X-Frame-Options presence
- X-Content-Type-Options
- X-XSS-Protection
- Referrer-Policy
- Permissions-Policy

#### Vulnerability Scanning

**XSS Detection**:
- Reflected XSS testing on URL parameters
- DOM-based XSS pattern detection
- Stored XSS indicator detection

**Injection Testing**:
- SQL injection pattern testing
- Command injection detection
- Header injection testing

**Authentication Testing**:
- Session cookie security
- Secure flag presence
- HttpOnly flag presence
- SameSite attribute

**Output**:
```json
{
  "security_summary": {
    "overall_grade": "B",
    "ssl_grade": "A",
    "header_grade": "C",
    "vulnerability_grade": "B+"
  },
  "issues": [
    {
      "severity": "high",
      "type": "security",
      "category": "headers",
      "description": "Content-Security-Policy header is missing",
      "fix_instruction": "Add Content-Security-Policy header to prevent XSS attacks. Add to server configuration or .htaccess: Header set Content-Security-Policy \"default-src 'self'; script-src 'self' https://trusted-cdn.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https://fonts.gstatic.com\". Adjust the policy based on your actual resource sources."
    },
    {
      "severity": "medium",
      "type": "security",
      "category": "cookies",
      "description": "Session cookie missing SameSite attribute",
      "fix_instruction": "Update session cookie configuration to include SameSite=Strict or SameSite=Lax. In Express.js: app.use(session({ cookie: { sameSite: 'strict' } })). In PHP: session_set_cookie_params(['samesite' => 'Strict']). This prevents CSRF attacks."
    }
  ]
}
```

### 5. Accessibility Tester Module

WCAG 2.1 AA compliance testing for accessibility.

#### Automated Checks

**Perceivable**:
- Image alt text presence and quality
- Video captions/transcripts
- Audio descriptions
- Color contrast ratios
- Text resizing capability
- Content reflow

**Operable**:
- Keyboard accessibility
- Focus visibility
- Skip links
- Page titles
- Focus order
- Link purpose clarity

**Understandable**:
- Language declaration
- Consistent navigation
- Error identification
- Labels and instructions

**Robust**:
- Valid HTML
- ARIA usage
- Name, role, value

**Output**:
```json
{
  "accessibility_summary": {
    "overall_score": 76,
    "wcag_level": "Partial AA",
    "issues_by_principle": {
      "perceivable": 8,
      "operable": 12,
      "understandable": 3,
      "robust": 5
    }
  },
  "issues": [
    {
      "severity": "high",
      "type": "accessibility",
      "wcag_criterion": "1.4.3 Contrast (Minimum)",
      "wcag_level": "AA",
      "description": "Text has insufficient color contrast ratio of 3.2:1 (minimum required is 4.5:1)",
      "location": {
        "page_url": "https://example.com/",
        "css_selector": ".hero-section .subtitle",
        "line_in_source": 78
      },
      "fix_instruction": "Change text color from #888888 to #595959 (or darker) to achieve 4.5:1 contrast ratio against the #ffffff background. Alternatively, darken the background. Use a contrast checker tool to verify: https://webaim.org/resources/contrastchecker/. Current: text #888888 on background #ffffff = 3.2:1. Required: minimum 4.5:1 for normal text, 3:1 for large text (18pt+ or 14pt bold)."
    }
  ]
}
```

---

## Grading Systems

### Commercial Readiness Grade (A+ to F)

This grade answers: **"Can this website handle commercial-scale usage?"**

#### Grade Definitions

| Grade | User Capacity | Response Time | Critical Issues | Description |
|-------|---------------|---------------|-----------------|-------------|
| A+ | 100k+ | <100ms | 0 | Enterprise-ready, exceptional performance |
| A | 50k-100k | <200ms | 0 | Production-ready, excellent performance |
| B+ | 25k-50k | <500ms | 0 | Near-ready, good performance |
| B | 10k-25k | <1s | 0 | Viable, acceptable performance |
| C+ | 5k-10k | <2s | 0-2 minor | Developing, needs optimization |
| C | 1k-5k | <3s | 0-5 minor | Early stage, significant optimization needed |
| D | <1k | >3s | Any | Not ready, major issues |
| F | N/A | N/A | Critical | Fundamental issues preventing use |

#### Scoring Formula

```
Commercial Score = (
  (Capacity Score × 0.25) +
  (Performance Score × 0.20) +
  (Error Rate Score × 0.15) +
  (Security Score × 0.15) +
  (Accessibility Score × 0.10) +
  (Mobile Score × 0.10) +
  (SEO Score × 0.05)
)
```

### Uniqueness Rating (1-100)

This score answers: **"Is this website unique or a cookie-cutter template?"**

#### Scoring Thresholds

| Score | Rating | Description |
|-------|--------|-------------|
| 90-100 | Highly Original | Custom design, unique functionality, strong brand identity |
| 75-89 | Distinctive | Customized template with significant modifications |
| 50-74 | Moderate | Recognizable template base with some customization |
| 25-49 | Generic | Minimal template customization, common patterns |
| 1-24 | Template Clone | Nearly unmodified template, no unique identity |

#### Evaluation Criteria

The uniqueness analyzer examines:

1. **Visual Design Originality (25%)**
   - Color scheme uniqueness
   - Typography choices
   - Layout composition
   - Visual hierarchy

2. **Layout Structure (20%)**
   - Grid system customization
   - Section arrangement
   - Spacing patterns
   - Responsive breakpoints

3. **Functionality Innovation (20%)**
   - Custom interactive elements
   - Unique user flows
   - Novel features
   - Animation originality

4. **Content Presentation (15%)**
   - Content structure
   - Media usage
   - Storytelling approach
   - Information architecture

5. **Interactive Element Creativity (10%)**
   - Navigation patterns
   - Form designs
   - Button styles
   - Micro-interactions

6. **Brand Identity Integration (10%)**
   - Logo integration
   - Brand color usage
   - Voice consistency
   - Visual cohesion

### Readiness Status

This status answers: **"Is this website ready to launch?"**

#### Status Definitions

**READY** ✅
- Zero critical issues
- All pages load successfully
- All forms functional
- No broken links
- Accessibility score > 80%
- Security scan clean
- Performance grade B or higher

**NEEDS POLISHING** ⚠️
- No critical issues
- Minor functional problems present
- Some broken links acceptable
- Accessibility score > 60%
- No high-severity security issues
- Performance grade C or higher

**UNDER CONSTRUCTION** 🚧
- Critical issues present
- Major functional failures
- Significant broken functionality
- Accessibility score < 60%
- Security vulnerabilities found
- Performance grade D or lower

---

## Agent Handoff Protocol

The most critical feature of this tool is generating reports that another AI agent or developer can use to fix all identified issues **without any prior knowledge of the website**.

### Handoff Document Requirements

Every issue in the handoff document MUST include:

1. **Exact Location**
   - Page URL
   - CSS selector
   - XPath
   - Line number in source
   - File path (if determinable)

2. **Clear Problem Description**
   - What is wrong
   - Why it is wrong
   - What standard/best practice it violates

3. **Explicit Fix Instructions**
   - Step-by-step instructions
   - Code snippets to add/modify
   - Tool commands if applicable
   - No assumed knowledge

4. **Verification Steps**
   - How to verify the fix worked
   - What to test after fixing
   - Expected outcome

5. **Priority and Dependencies**
   - Severity level
   - Whether other fixes depend on this
   - Recommended fix order

### Example Handoff Entry

```markdown
## Issue #17: Broken Product Image

### Location
- **Page**: https://example.com/products/widget-pro
- **Element**: Product main image
- **CSS Selector**: `.product-detail .product-image img`
- **Line in HTML**: 145

### Problem
The product image fails to load, returning a 404 error. The image URL `/images/products/widget-pro-main.jpg` does not exist on the server. This results in a broken image icon being displayed to users, which damages credibility and prevents users from seeing the product.

### Fix Instructions

**Step 1**: Check if the image exists in a different location
```bash
find /var/www/html/images -name "*widget-pro*"
```

**Step 2**: If the image exists elsewhere, update the src attribute:
```html
<!-- Current (broken) -->
<img src="/images/products/widget-pro-main.jpg" alt="Widget Pro">

<!-- Fix Option A: If file is in different folder -->
<img src="/images/products/catalog/widget-pro-main.jpg" alt="Widget Pro">

<!-- Fix Option B: If filename is different -->
<img src="/images/products/widget-pro.jpg" alt="Widget Pro">
```

**Step 3**: If the image does not exist, you need to:
1. Obtain the product image from the product manager/designer
2. Resize to appropriate dimensions (recommended: 800x800px)
3. Optimize for web (compress to <100KB)
4. Upload to `/images/products/widget-pro-main.jpg`

**Step 4**: After fixing, verify by:
1. Clear browser cache
2. Navigate to https://example.com/products/widget-pro
3. Confirm image displays correctly
4. Check Network tab shows 200 status for image

### Priority
- **Severity**: HIGH
- **Impact**: User cannot see product, likely to abandon
- **Dependencies**: None - can be fixed independently
- **Estimated Effort**: 5-15 minutes depending on image availability
```

---

## Technical Implementation

### Main Orchestrator (main.py)

The main orchestrator coordinates all testing modules and generates the final report.

```python
# Entry point function signature
async def run_website_test(
    url: str,
    test_config: Optional[TestConfig] = None,
    competitor_urls: Optional[List[str]] = None
) -> WebsiteTestReport:
    """
    Run comprehensive website test.

    Args:
        url: The website URL to test
        test_config: Optional configuration for test parameters
        competitor_urls: Optional URLs for uniqueness comparison

    Returns:
        WebsiteTestReport with all grades, scores, and issues
    """
```

### Error Handling Strategy

All modules implement robust error handling:

1. **Network Errors**: Retry with exponential backoff (3 attempts)
2. **Timeout Errors**: Configurable timeout with graceful degradation
3. **Parse Errors**: Log and continue, mark element as "untestable"
4. **Rate Limiting**: Respect server limits, implement delays
5. **Authentication Walls**: Detect and report as limitation

### Configuration Options

```python
@dataclass
class TestConfig:
    """Configuration for website testing."""

    # Crawling options
    max_depth: int = 10
    max_pages: int = 500
    respect_robots_txt: bool = True
    follow_external_links: bool = False

    # Performance options
    load_test_concurrent_users: int = 100
    load_test_duration_seconds: int = 60

    # Security options
    run_active_security_tests: bool = False  # Passive only by default

    # Accessibility options
    wcag_level: str = "AA"  # "A", "AA", or "AAA"

    # Output options
    include_screenshots: bool = True
    output_format: str = "json"  # "json", "markdown", "html"
```

---

## Usage Guide

### Basic Usage

```
Test my website at https://example.com for commercial readiness
```

### Advanced Usage

```
Perform a comprehensive audit of https://example.com including:
- Full element testing (all buttons, links, images, forms, menus)
- Performance benchmarking with load capacity estimation
- Security vulnerability scan
- WCAG AA accessibility compliance check
- Uniqueness score compared to these competitors: https://competitor1.com, https://competitor2.com

Generate a detailed agent handoff report with explicit fix instructions assuming the fixing agent has zero knowledge of the site. Include all three grades:
1. Commercial readiness grade
2. Uniqueness score
3. Overall readiness status
```

### Interpreting Results

The final report includes:

1. **Executive Summary**: Quick overview of all grades
2. **Detailed Test Results**: Every test performed with pass/fail
3. **Issue List**: All problems found, sorted by severity
4. **Agent Handoff Document**: Fix instructions for each issue
5. **Recommendations**: Prioritized list of improvements
6. **Verification Checklist**: How to confirm all fixes

---

## Output Formats

### JSON Report Structure

```json
{
  "report_metadata": {
    "generated_at": "2025-11-30T10:30:00Z",
    "tool_version": "1.0.0",
    "test_duration_seconds": 342
  },
  "grades": {
    "commercial_readiness": {
      "grade": "B+",
      "score": 82,
      "max_concurrent_users": 35000,
      "bottlenecks": ["Database queries", "Image optimization"]
    },
    "uniqueness": {
      "score": 67,
      "rating": "Moderate",
      "template_detected": "Bootstrap-based custom",
      "differentiation_suggestions": [...]
    },
    "readiness_status": {
      "status": "NEEDS_POLISHING",
      "blocking_issues": 0,
      "critical_issues": 2,
      "total_issues": 47
    }
  },
  "test_results": {
    "elements": {...},
    "performance": {...},
    "security": {...},
    "accessibility": {...}
  },
  "issues": [...],
  "agent_handoff": {
    "fix_instructions": [...],
    "priority_order": [...],
    "dependencies": [...],
    "verification_steps": [...]
  }
}
```

---

## Security Considerations

### Testing Ethics

This tool performs **authorized testing only**. Users must:
- Own the website or have explicit permission to test
- Not use results for malicious purposes
- Respect rate limits and server resources

### Data Handling

- No sensitive data is stored permanently
- Credentials are never logged
- Test results are local only
- No data sent to external services

---

## Performance Optimization

### Efficient Crawling

- Parallel page fetching (configurable concurrency)
- Intelligent caching of resources
- Incremental testing support
- Resume capability for large sites

### Resource Management

- Memory-efficient processing
- Streaming for large responses
- Connection pooling
- Request deduplication

---

## Appendix: WCAG 2.1 Quick Reference

| Criterion | Level | Description |
|-----------|-------|-------------|
| 1.1.1 | A | Non-text content has text alternative |
| 1.4.3 | AA | Contrast ratio at least 4.5:1 |
| 2.1.1 | A | All functionality keyboard accessible |
| 2.4.4 | A | Link purpose clear from text |
| 2.4.7 | AA | Focus visible |
| 3.1.1 | A | Language of page specified |
| 4.1.2 | A | Name, role, value available |

---

## Version History

- **1.0.0** (2025-11-30): Initial release with full testing suite

---

*This skill is part of the Agent Skill Creator ecosystem. For questions or improvements, refer to the main documentation.*
