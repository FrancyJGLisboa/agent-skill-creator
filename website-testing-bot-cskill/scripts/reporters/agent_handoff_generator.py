"""
Agent handoff generator for creating fix instruction documents.

Generates comprehensive documents for AI agents or developers
to fix identified issues with zero assumptions.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class HandoffDocument:
    """Complete agent handoff document."""
    document_id: str
    generated_at: str
    target_url: str
    summary: Dict[str, Any]
    priority_fixes: List[Dict[str, Any]]
    all_fixes: List[Dict[str, Any]]
    verification_steps: List[Dict[str, Any]]
    rollback_instructions: Dict[str, Any]
    success_criteria: Dict[str, Any]


class AgentHandoffGenerator:
    """
    Generates comprehensive handoff documents for fixing agents.

    Creates detailed, zero-assumption fix instructions that any
    AI agent or developer can follow to resolve issues.
    """

    def __init__(self):
        """Initialize handoff generator."""
        pass

    def generate_handoff(
        self,
        url: str,
        all_issues: List[Dict[str, Any]],
        grades: Dict[str, Any],
        readiness_data: Any
    ) -> HandoffDocument:
        """
        Generate agent handoff document.

        Args:
            url: Target URL
            all_issues: All issues to fix
            grades: Current grades
            readiness_data: Readiness assessment data

        Returns:
            HandoffDocument with all fix instructions
        """
        document_id = f"handoff_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        generated_at = datetime.now().isoformat()

        # Generate summary
        summary = self._generate_summary(all_issues, grades, readiness_data)

        # Generate priority fixes (critical and high)
        priority_fixes = self._generate_priority_fixes(all_issues)

        # Generate all fixes with detailed instructions
        all_fixes = self._generate_all_fixes(all_issues)

        # Generate verification steps
        verification_steps = self._generate_verification_steps(all_issues)

        # Generate rollback instructions
        rollback_instructions = self._generate_rollback_instructions()

        # Define success criteria
        success_criteria = self._define_success_criteria(grades, readiness_data)

        return HandoffDocument(
            document_id=document_id,
            generated_at=generated_at,
            target_url=url,
            summary=summary,
            priority_fixes=priority_fixes,
            all_fixes=all_fixes,
            verification_steps=verification_steps,
            rollback_instructions=rollback_instructions,
            success_criteria=success_criteria
        )

    def _generate_summary(
        self,
        all_issues: List[Dict[str, Any]],
        grades: Dict[str, Any],
        readiness_data: Any
    ) -> Dict[str, Any]:
        """Generate summary for the fixing agent."""
        critical_count = len([i for i in all_issues if i.get('severity') == 'critical'])
        high_count = len([i for i in all_issues if i.get('severity') == 'high'])
        medium_count = len([i for i in all_issues if i.get('severity') == 'medium'])
        low_count = len([i for i in all_issues if i.get('severity') == 'low'])

        return {
            'instructions_for_agent': (
                "YOU ARE RECEIVING THIS DOCUMENT TO FIX A WEBSITE. "
                "This document contains all identified issues and explicit fix instructions. "
                "DO NOT make assumptions about the codebase - each fix includes specific "
                "file locations, code changes, and verification steps. "
                "Work through fixes in the order provided (priority first). "
                "After each fix, run the verification step before proceeding. "
                "If you encounter errors not covered here, document them for review."
            ),
            'total_issues': len(all_issues),
            'by_severity': {
                'critical': critical_count,
                'high': high_count,
                'medium': medium_count,
                'low': low_count
            },
            'current_status': grades.get('readiness_status', {}).get('status', 'UNKNOWN'),
            'target_status': 'READY',
            'current_commercial_grade': grades.get('commercial_readiness', {}).get('grade', 'N/A'),
            'estimated_work': self._estimate_work(all_issues),
            'priority_order': (
                "1. Critical issues (security vulnerabilities, broken core functionality)\n"
                "2. High-severity issues (accessibility, major UX problems)\n"
                "3. Medium-severity issues (optimization, best practices)\n"
                "4. Low-severity issues (polish, minor improvements)"
            )
        }

    def _estimate_work(self, all_issues: List[Dict[str, Any]]) -> str:
        """Estimate work required."""
        critical = len([i for i in all_issues if i.get('severity') == 'critical'])
        high = len([i for i in all_issues if i.get('severity') == 'high'])

        if critical > 5 or (critical + high) > 20:
            return "Significant work required - 1-2 weeks estimated"
        elif critical > 0 or (critical + high) > 10:
            return "Moderate work required - 3-5 days estimated"
        elif high > 0:
            return "Light work required - 1-2 days estimated"
        else:
            return "Minor polish - less than 1 day estimated"

    def _generate_priority_fixes(
        self,
        all_issues: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate priority fix list (critical and high only)."""
        priority_issues = [i for i in all_issues
                         if i.get('severity') in ['critical', 'high']]

        fixes = []
        for i, issue in enumerate(priority_issues, 1):
            fixes.append(self._create_fix_entry(issue, i, is_priority=True))

        return fixes

    def _generate_all_fixes(
        self,
        all_issues: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate complete fix list with detailed instructions."""
        fixes = []
        for i, issue in enumerate(all_issues, 1):
            fixes.append(self._create_fix_entry(issue, i, is_priority=False))
        return fixes

    def _create_fix_entry(
        self,
        issue: Dict[str, Any],
        fix_number: int,
        is_priority: bool
    ) -> Dict[str, Any]:
        """Create a detailed fix entry."""
        location = issue.get('location', {})

        return {
            'fix_number': fix_number,
            'issue_id': issue.get('id'),
            'severity': issue.get('severity', 'medium'),
            'category': issue.get('category', 'unknown'),
            'is_priority': is_priority,

            'problem': {
                'description': issue.get('description', ''),
                'impact': self._get_impact_description(issue),
                'affected_element': issue.get('element_type', ''),
            },

            'location': {
                'page_url': location.get('page_url', 'Unknown'),
                'css_selector': location.get('css_selector', 'Unknown'),
                'xpath': location.get('xpath', ''),
                'line_number': location.get('line_number', 'Unknown'),
                'additional_context': self._get_location_context(issue)
            },

            'fix_instructions': {
                'summary': issue.get('fix_instruction', 'No specific fix instruction provided'),
                'steps': self._expand_fix_steps(issue),
                'code_changes': self._generate_code_changes(issue),
                'tools_needed': self._identify_tools_needed(issue),
                'estimated_time': self._estimate_fix_time(issue)
            },

            'verification': {
                'how_to_verify': self._get_verification_steps(issue),
                'expected_result': self._get_expected_result(issue),
                'common_mistakes': self._get_common_mistakes(issue)
            },

            'dependencies': {
                'depends_on': self._get_dependencies(issue),
                'blocks': self._get_blocked_by(issue)
            },

            'wcag_reference': issue.get('wcag_reference')
        }

    def _get_impact_description(self, issue: Dict[str, Any]) -> str:
        """Get impact description for an issue."""
        category = issue.get('category', '')
        severity = issue.get('severity', '')

        impacts = {
            ('critical', 'security'): "Users and data at risk. Site may be compromised.",
            ('critical', 'functionality'): "Core functionality broken. Users cannot complete key tasks.",
            ('critical', 'broken_link'): "Important navigation broken. Users cannot find content.",
            ('high', 'accessibility'): "Users with disabilities cannot use this feature.",
            ('high', 'security'): "Potential security vulnerability that should be fixed.",
            ('high', 'performance'): "Significantly impacts user experience and SEO.",
            ('medium', 'accessibility'): "Impacts some users' ability to use the site.",
            ('medium', 'ux'): "Degrades user experience but doesn't block functionality.",
            ('low', 'best_practice'): "Minor improvement for code quality or performance."
        }

        return impacts.get((severity, category),
                          f"Impacts {category} at {severity} level")

    def _get_location_context(self, issue: Dict[str, Any]) -> str:
        """Get additional location context."""
        element_type = issue.get('element_type', '')
        location = issue.get('location', {})

        if element_type == 'button':
            return "Look for button elements, including <button>, <input type='submit'>, and elements with role='button'"
        elif element_type == 'link':
            return "Look for anchor (<a>) elements"
        elif element_type == 'image':
            return "Look for <img> elements and CSS background images"
        elif element_type == 'form':
            return "Look for <form> elements and their child inputs"
        elif element_type == 'menu':
            return "Look for <nav> elements or elements with navigation-related classes"

        return f"Located at {location.get('css_selector', 'specified location')}"

    def _expand_fix_steps(self, issue: Dict[str, Any]) -> List[str]:
        """Expand fix instruction into discrete steps."""
        instruction = issue.get('fix_instruction', '')
        steps = []

        # Parse instruction for numbered steps
        if '1)' in instruction or '1.' in instruction:
            import re
            pattern = r'(?:\d+[\)\.]\s*)([^0-9\)\.]+?)(?=\d+[\)\.']|$)'
            matches = re.findall(pattern, instruction)
            steps = [m.strip() for m in matches if m.strip()]

        if not steps:
            # Create generic steps based on category
            category = issue.get('category', '')

            if category == 'accessibility':
                steps = [
                    "Locate the element using the provided selector",
                    "Identify the accessibility issue",
                    "Apply the fix as described",
                    "Test with keyboard navigation",
                    "Test with screen reader if available"
                ]
            elif category == 'security':
                steps = [
                    "Identify the security configuration",
                    "Apply the security fix",
                    "Verify fix doesn't break functionality",
                    "Test security headers/settings"
                ]
            elif category == 'performance':
                steps = [
                    "Measure current performance",
                    "Apply optimization",
                    "Measure performance again",
                    "Verify improvement"
                ]
            else:
                steps = [instruction] if instruction else ["Apply fix as described"]

        return steps

    def _generate_code_changes(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code change suggestions."""
        category = issue.get('category', '')
        element_type = issue.get('element_type', '')

        # Provide code examples based on issue type
        if 'alt' in issue.get('description', '').lower():
            return {
                'before': '<img src="image.jpg">',
                'after': '<img src="image.jpg" alt="Descriptive text about the image">',
                'language': 'html'
            }
        elif 'label' in issue.get('description', '').lower():
            return {
                'before': '<input type="text" name="email">',
                'after': '<label for="email">Email Address</label>\n<input type="text" id="email" name="email">',
                'language': 'html'
            }
        elif 'https' in issue.get('description', '').lower():
            return {
                'before': 'http://example.com/resource',
                'after': 'https://example.com/resource',
                'language': 'text'
            }

        return {
            'note': 'Refer to fix_instruction for specific code changes',
            'language': 'text'
        }

    def _identify_tools_needed(self, issue: Dict[str, Any]) -> List[str]:
        """Identify tools needed for the fix."""
        tools = []
        category = issue.get('category', '')
        description = issue.get('description', '').lower()

        if category == 'accessibility':
            tools.append("Browser DevTools for element inspection")
            tools.append("axe DevTools or similar for verification")

        if category == 'performance':
            tools.append("Browser DevTools Network tab")
            tools.append("Lighthouse or WebPageTest")

        if category == 'security':
            tools.append("Browser DevTools Security tab")
            tools.append("SSL checker tool")

        if 'image' in description:
            tools.append("Image optimization tool (squoosh.app, ImageOptim)")

        if not tools:
            tools.append("Text editor or IDE")
            tools.append("Browser for verification")

        return tools

    def _estimate_fix_time(self, issue: Dict[str, Any]) -> str:
        """Estimate time to fix."""
        severity = issue.get('severity', '')
        category = issue.get('category', '')

        if severity == 'critical':
            return "30-60 minutes (verify carefully)"
        elif severity == 'high':
            return "15-30 minutes"
        elif category in ['accessibility', 'security']:
            return "10-20 minutes"
        else:
            return "5-15 minutes"

    def _get_verification_steps(self, issue: Dict[str, Any]) -> List[str]:
        """Get verification steps for a fix."""
        category = issue.get('category', '')
        element_type = issue.get('element_type', '')

        if category == 'accessibility':
            return [
                "Navigate to the page containing the element",
                "Inspect the element to verify changes applied",
                "Test keyboard navigation (Tab key)",
                "Run accessibility checker (axe DevTools)",
                "Verify issue no longer appears"
            ]
        elif category == 'security':
            return [
                "Clear browser cache",
                "Navigate to the page",
                "Open DevTools Security tab",
                "Verify security warnings resolved",
                "Check response headers if applicable"
            ]
        elif category == 'performance':
            return [
                "Clear browser cache",
                "Open DevTools Network tab",
                "Reload the page",
                "Verify metrics improved",
                "Run Lighthouse audit"
            ]
        elif element_type == 'link':
            return [
                "Navigate to the page with the link",
                "Click the link",
                "Verify it navigates to correct destination",
                "Check for 200 status in Network tab"
            ]
        elif element_type == 'image':
            return [
                "Navigate to the page with the image",
                "Verify image displays correctly",
                "Check alt text in DevTools",
                "Verify image loads (no 404)"
            ]
        elif element_type == 'form':
            return [
                "Navigate to the form",
                "Fill out all fields",
                "Submit the form",
                "Verify successful submission",
                "Check for proper validation"
            ]

        return [
            "Apply the fix",
            "Test the affected functionality",
            "Verify the issue is resolved"
        ]

    def _get_expected_result(self, issue: Dict[str, Any]) -> str:
        """Get expected result after fix."""
        category = issue.get('category', '')

        if 'broken' in issue.get('description', '').lower():
            return "Resource loads successfully with 200 status code"
        elif category == 'accessibility':
            return "Element passes accessibility checks, no warnings in DevTools"
        elif category == 'security':
            return "No security warnings, proper headers present"
        elif category == 'performance':
            return "Improved metrics, faster load times"

        return "Issue no longer present when tested"

    def _get_common_mistakes(self, issue: Dict[str, Any]) -> List[str]:
        """Get common mistakes to avoid."""
        category = issue.get('category', '')

        if category == 'accessibility':
            return [
                "Don't use generic alt text like 'image' or 'photo'",
                "Don't hide elements with visibility while keeping in DOM",
                "Don't forget to test with keyboard"
            ]
        elif category == 'security':
            return [
                "Don't disable security features to 'fix' the warning",
                "Don't expose credentials in client-side code",
                "Don't forget to test functionality after security changes"
            ]
        elif category == 'performance':
            return [
                "Don't sacrifice functionality for performance",
                "Don't remove content that users need",
                "Don't forget to test on slow connections"
            ]

        return [
            "Don't skip verification after fixing",
            "Don't make changes beyond what's specified"
        ]

    def _get_dependencies(self, issue: Dict[str, Any]) -> List[str]:
        """Get issues this fix depends on."""
        # In a real implementation, this would analyze issue relationships
        return []

    def _get_blocked_by(self, issue: Dict[str, Any]) -> List[str]:
        """Get issues blocked by this fix."""
        return []

    def _generate_verification_steps(
        self,
        all_issues: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate overall verification steps."""
        return [
            {
                'step': 1,
                'title': 'Run full site crawl',
                'description': 'After all fixes, crawl the site to verify no broken links remain',
                'tool': 'Site crawler or link checker'
            },
            {
                'step': 2,
                'title': 'Run accessibility audit',
                'description': 'Run axe DevTools or similar on main pages',
                'tool': 'axe DevTools, WAVE, or Lighthouse'
            },
            {
                'step': 3,
                'title': 'Run security scan',
                'description': 'Verify security headers and HTTPS configuration',
                'tool': 'Security Headers (securityheaders.com)'
            },
            {
                'step': 4,
                'title': 'Run performance audit',
                'description': 'Run Lighthouse and verify Core Web Vitals',
                'tool': 'Lighthouse, WebPageTest'
            },
            {
                'step': 5,
                'title': 'Test main user flows',
                'description': 'Manually test key user journeys (forms, navigation, etc.)',
                'tool': 'Manual testing'
            }
        ]

    def _generate_rollback_instructions(self) -> Dict[str, Any]:
        """Generate rollback instructions."""
        return {
            'general_advice': (
                "Before making changes, ensure you have version control (git) "
                "or backups in place. If a fix causes issues:"
            ),
            'steps': [
                "Revert the specific change using git: git checkout -- <file>",
                "If committed, use: git revert <commit-hash>",
                "For database changes, restore from backup",
                "Document what went wrong for future reference"
            ],
            'emergency_contact': (
                "If critical functionality breaks and you cannot resolve, "
                "document the issue and escalate to the project maintainer."
            )
        }

    def _define_success_criteria(
        self,
        grades: Dict[str, Any],
        readiness_data: Any
    ) -> Dict[str, Any]:
        """Define success criteria for the fixes."""
        return {
            'primary_goal': "Achieve READY status for commercial launch",
            'criteria': [
                {
                    'criterion': 'Zero Critical Issues',
                    'description': 'All critical issues resolved',
                    'current': grades.get('readiness_status', {}).get('status', 'UNKNOWN') != 'UNDER_CONSTRUCTION',
                    'required': True
                },
                {
                    'criterion': 'Security Clean',
                    'description': 'No high-severity security issues',
                    'current': grades.get('security', {}).get('grade', 'F') in ['A', 'B'],
                    'required': True
                },
                {
                    'criterion': 'Performance Acceptable',
                    'description': 'Performance grade B or higher',
                    'current': grades.get('performance', {}).get('grade', 'F') in ['A+', 'A', 'B+', 'B'],
                    'required': True
                },
                {
                    'criterion': 'Accessibility Compliant',
                    'description': 'Accessibility score 80% or higher',
                    'current': grades.get('accessibility', {}).get('score', 0) >= 80,
                    'required': True
                },
                {
                    'criterion': 'All Links Working',
                    'description': 'No broken links on the site',
                    'current': False,  # Determined by test
                    'required': True
                },
                {
                    'criterion': 'Forms Functional',
                    'description': 'All forms submit successfully',
                    'current': False,  # Determined by test
                    'required': True
                }
            ],
            'secondary_goals': [
                "Improve commercial readiness grade to B or higher",
                "Increase uniqueness score above 50",
                "Resolve all high-severity issues"
            ]
        }

    def to_markdown(self, document: HandoffDocument) -> str:
        """Convert handoff document to markdown format."""
        md = []

        md.append(f"# Website Fix Handoff Document")
        md.append(f"\n**Document ID:** {document.document_id}")
        md.append(f"\n**Generated:** {document.generated_at}")
        md.append(f"\n**Target URL:** {document.target_url}")

        md.append("\n\n---\n")
        md.append("## INSTRUCTIONS FOR FIXING AGENT\n")
        md.append(document.summary['instructions_for_agent'])

        md.append("\n\n## Summary\n")
        md.append(f"- **Total Issues:** {document.summary['total_issues']}")
        md.append(f"- **Critical:** {document.summary['by_severity']['critical']}")
        md.append(f"- **High:** {document.summary['by_severity']['high']}")
        md.append(f"- **Medium:** {document.summary['by_severity']['medium']}")
        md.append(f"- **Low:** {document.summary['by_severity']['low']}")
        md.append(f"- **Current Status:** {document.summary['current_status']}")
        md.append(f"- **Estimated Work:** {document.summary['estimated_work']}")

        md.append("\n\n## Priority Fixes (Do These First)\n")
        for fix in document.priority_fixes:
            md.append(f"\n### Fix #{fix['fix_number']}: {fix['problem']['description'][:100]}")
            md.append(f"\n**Severity:** {fix['severity'].upper()}")
            md.append(f"\n**Location:** {fix['location']['css_selector']}")
            md.append(f"\n\n**Fix Instructions:**\n{fix['fix_instructions']['summary']}")
            md.append(f"\n\n**Steps:**")
            for step in fix['fix_instructions']['steps']:
                md.append(f"\n- {step}")
            md.append(f"\n\n**Verify:** {fix['verification']['expected_result']}")
            md.append("\n\n---")

        md.append("\n\n## Success Criteria\n")
        for criterion in document.success_criteria['criteria']:
            status = "✅" if criterion['current'] else "❌"
            md.append(f"\n{status} {criterion['criterion']}: {criterion['description']}")

        return "\n".join(md)
