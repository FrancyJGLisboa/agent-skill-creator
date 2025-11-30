"""
Readiness analyzer for overall launch status determination.

Determines if site is Under Construction, Needs Polishing, or Ready.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from ..utils.constants import (
    READINESS_READY,
    READINESS_NEEDS_POLISHING,
    READINESS_UNDER_CONSTRUCTION,
    READINESS_CRITERIA,
    SEVERITY_CRITICAL,
    SEVERITY_HIGH,
    SEVERITY_MEDIUM
)


@dataclass
class ReadinessCriterion:
    """A criterion for readiness evaluation."""
    name: str
    status: str  # pass, fail, warning
    current_value: Any
    required_value: Any
    description: str
    fix_instruction: str


@dataclass
class ReadinessReport:
    """Complete readiness assessment report."""
    url: str
    status: str  # READY, NEEDS_POLISHING, UNDER_CONSTRUCTION
    status_description: str
    criteria_results: List[ReadinessCriterion]
    blocking_issues: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    checklist: Dict[str, bool]
    next_steps: List[str]
    estimated_effort_to_ready: str


class ReadinessAnalyzer:
    """
    Analyzes overall website launch readiness.

    Determines status based on critical issues, functionality,
    security, accessibility, and performance criteria.
    """

    def __init__(self):
        """Initialize readiness analyzer."""
        pass

    def analyze_readiness(
        self,
        url: str,
        all_issues: List[Dict[str, Any]],
        test_results: Dict[str, Any],
        commercial_data: Dict[str, Any],
        uniqueness_data: Dict[str, Any]
    ) -> ReadinessReport:
        """
        Analyze overall readiness.

        Args:
            url: URL being analyzed
            all_issues: All issues from all testers
            test_results: Aggregated test results
            commercial_data: Commercial readiness data
            uniqueness_data: Uniqueness analysis data

        Returns:
            ReadinessReport with status and criteria
        """
        criteria_results = []
        blocking_issues = []
        warnings = []

        # Evaluate each criterion
        criteria_results.extend(self._evaluate_critical_issues(all_issues))
        criteria_results.extend(self._evaluate_functionality(test_results))
        criteria_results.extend(self._evaluate_security(test_results, all_issues))
        criteria_results.extend(self._evaluate_accessibility(test_results, all_issues))
        criteria_results.extend(self._evaluate_performance(test_results, commercial_data))

        # Collect blocking issues
        for criterion in criteria_results:
            if criterion.status == 'fail':
                blocking_issues.append({
                    'criterion': criterion.name,
                    'description': criterion.description,
                    'fix_instruction': criterion.fix_instruction
                })
            elif criterion.status == 'warning':
                warnings.append({
                    'criterion': criterion.name,
                    'description': criterion.description,
                    'fix_instruction': criterion.fix_instruction
                })

        # Determine status
        status = self._determine_status(criteria_results, blocking_issues)
        status_description = self._get_status_description(status)

        # Generate checklist
        checklist = self._generate_checklist(criteria_results, test_results)

        # Generate next steps
        next_steps = self._generate_next_steps(status, blocking_issues, warnings)

        # Estimate effort
        effort_estimate = self._estimate_effort(blocking_issues, warnings)

        return ReadinessReport(
            url=url,
            status=status,
            status_description=status_description,
            criteria_results=criteria_results,
            blocking_issues=blocking_issues,
            warnings=warnings,
            checklist=checklist,
            next_steps=next_steps,
            estimated_effort_to_ready=effort_estimate
        )

    def _evaluate_critical_issues(
        self,
        all_issues: List[Dict[str, Any]]
    ) -> List[ReadinessCriterion]:
        """Evaluate critical issue criterion."""
        criteria = []

        critical_count = sum(1 for i in all_issues
                           if i.get('severity') == SEVERITY_CRITICAL or
                           (hasattr(i, 'severity') and i.severity == SEVERITY_CRITICAL))

        high_count = sum(1 for i in all_issues
                        if i.get('severity') == SEVERITY_HIGH or
                        (hasattr(i, 'severity') and i.severity == SEVERITY_HIGH))

        # Critical issues criterion
        status = 'pass' if critical_count == 0 else 'fail'
        criteria.append(ReadinessCriterion(
            name="No Critical Issues",
            status=status,
            current_value=critical_count,
            required_value=0,
            description=f"Found {critical_count} critical issues" if critical_count > 0 else "No critical issues",
            fix_instruction=(
                f"Must fix all {critical_count} critical issues before launch. "
                f"Critical issues include: security vulnerabilities, broken core functionality, "
                f"missing HTTPS, exposed credentials. See detailed issue list for specifics."
            ) if critical_count > 0 else "No action needed"
        ))

        # High severity issues criterion
        status = 'pass' if high_count == 0 else 'warning' if high_count <= 5 else 'fail'
        criteria.append(ReadinessCriterion(
            name="High Severity Issues",
            status=status,
            current_value=high_count,
            required_value=0,
            description=f"Found {high_count} high-severity issues",
            fix_instruction=(
                f"Address {high_count} high-severity issues. While not blocking, these "
                f"significantly impact user experience. Prioritize fixing before launch "
                f"or schedule for immediate post-launch attention."
            ) if high_count > 0 else "No action needed"
        ))

        return criteria

    def _evaluate_functionality(
        self,
        test_results: Dict[str, Any]
    ) -> List[ReadinessCriterion]:
        """Evaluate functionality criteria."""
        criteria = []

        # Broken links
        broken_links = test_results.get('broken_links', [])
        broken_count = len(broken_links)

        status = 'pass' if broken_count == 0 else 'warning' if broken_count <= 5 else 'fail'
        criteria.append(ReadinessCriterion(
            name="No Broken Links",
            status=status,
            current_value=broken_count,
            required_value=0,
            description=f"Found {broken_count} broken links",
            fix_instruction=(
                f"Fix {broken_count} broken links. Broken links damage credibility and SEO. "
                f"Either update URLs, remove links, or create missing pages. "
                f"Use redirect for moved content."
            ) if broken_count > 0 else "All links functional"
        ))

        # Forms functional
        form_issues = [i for i in test_results.get('issues', [])
                      if 'form' in str(i).lower() and
                      (i.get('severity') in [SEVERITY_CRITICAL, SEVERITY_HIGH])]
        form_issue_count = len(form_issues)

        status = 'pass' if form_issue_count == 0 else 'fail'
        criteria.append(ReadinessCriterion(
            name="Forms Functional",
            status=status,
            current_value=form_issue_count,
            required_value=0,
            description=f"{form_issue_count} form issues found" if form_issue_count > 0 else "All forms working",
            fix_instruction=(
                f"Fix {form_issue_count} form issues. Forms are critical for user interaction. "
                f"Issues include: missing labels, broken submission, validation errors. "
                f"Test each form end-to-end after fixes."
            ) if form_issue_count > 0 else "No action needed"
        ))

        # Pages load
        pages = test_results.get('pages', [])
        failed_pages = [p for p in pages
                       if (hasattr(p, 'status_code') and p.status_code >= 400) or
                       (hasattr(p, 'error') and p.error)]
        failed_count = len(failed_pages)

        status = 'pass' if failed_count == 0 else 'fail'
        criteria.append(ReadinessCriterion(
            name="All Pages Load",
            status=status,
            current_value=failed_count,
            required_value=0,
            description=f"{failed_count} pages failed to load" if failed_count > 0 else "All pages load successfully",
            fix_instruction=(
                f"Fix {failed_count} pages that fail to load. Check for: "
                f"server errors (500), missing pages (404), redirect loops. "
                f"Each failed page needs individual diagnosis."
            ) if failed_count > 0 else "No action needed"
        ))

        return criteria

    def _evaluate_security(
        self,
        test_results: Dict[str, Any],
        all_issues: List[Dict[str, Any]]
    ) -> List[ReadinessCriterion]:
        """Evaluate security criteria."""
        criteria = []

        # HTTPS
        security_data = test_results.get('security', {})
        ssl_valid = True
        if security_data:
            ssl_info = security_data.get('ssl_info', {})
            if hasattr(ssl_info, 'valid'):
                ssl_valid = ssl_info.valid

        status = 'pass' if ssl_valid else 'fail'
        criteria.append(ReadinessCriterion(
            name="HTTPS Enabled",
            status=status,
            current_value=ssl_valid,
            required_value=True,
            description="HTTPS properly configured" if ssl_valid else "HTTPS not configured or invalid",
            fix_instruction=(
                f"Enable HTTPS immediately. Install SSL certificate from Let's Encrypt (free) "
                f"or your hosting provider. HTTPS is mandatory for commercial sites - "
                f"browsers flag non-HTTPS as insecure."
            ) if not ssl_valid else "No action needed"
        ))

        # No high severity security issues
        security_issues = [i for i in all_issues
                         if i.get('category') == 'security' or
                         (hasattr(i, 'category') and i.category == 'security')]
        high_security = [i for i in security_issues
                        if i.get('severity') in [SEVERITY_CRITICAL, SEVERITY_HIGH] or
                        (hasattr(i, 'severity') and i.severity in [SEVERITY_CRITICAL, SEVERITY_HIGH])]

        status = 'pass' if len(high_security) == 0 else 'fail'
        criteria.append(ReadinessCriterion(
            name="No High Security Risks",
            status=status,
            current_value=len(high_security),
            required_value=0,
            description=f"{len(high_security)} high security risks" if high_security else "No high security risks",
            fix_instruction=(
                f"Address {len(high_security)} security issues before launch. "
                f"Security vulnerabilities expose users and business to risk. "
                f"Includes: missing headers, exposed data, XSS risks."
            ) if high_security else "No action needed"
        ))

        return criteria

    def _evaluate_accessibility(
        self,
        test_results: Dict[str, Any],
        all_issues: List[Dict[str, Any]]
    ) -> List[ReadinessCriterion]:
        """Evaluate accessibility criteria."""
        criteria = []

        # Accessibility score
        a11y_data = test_results.get('accessibility', {})
        a11y_score = 0
        if a11y_data:
            if hasattr(a11y_data, 'score'):
                a11y_score = a11y_data.score
            else:
                a11y_score = a11y_data.get('score', 0)

        if a11y_score >= 80:
            status = 'pass'
        elif a11y_score >= 60:
            status = 'warning'
        else:
            status = 'fail'

        criteria.append(ReadinessCriterion(
            name="Accessibility Score > 80%",
            status=status,
            current_value=a11y_score,
            required_value=80,
            description=f"Accessibility score: {a11y_score}%",
            fix_instruction=(
                f"Improve accessibility score from {a11y_score}% to 80%+. "
                f"Priority fixes: add alt text to images, ensure form labels, "
                f"fix color contrast, add skip links, ensure keyboard navigation."
            ) if a11y_score < 80 else "No action needed"
        ))

        return criteria

    def _evaluate_performance(
        self,
        test_results: Dict[str, Any],
        commercial_data: Dict[str, Any]
    ) -> List[ReadinessCriterion]:
        """Evaluate performance criteria."""
        criteria = []

        # Performance grade
        perf_data = test_results.get('performance', {})
        perf_grade = 'C'
        if perf_data:
            if hasattr(perf_data, 'grade'):
                perf_grade = perf_data.grade
            else:
                perf_grade = perf_data.get('grade', 'C')

        if perf_grade in ['A+', 'A', 'B+', 'B']:
            status = 'pass'
        elif perf_grade in ['C+', 'C']:
            status = 'warning'
        else:
            status = 'fail'

        criteria.append(ReadinessCriterion(
            name="Performance Grade B or Higher",
            status=status,
            current_value=perf_grade,
            required_value='B',
            description=f"Performance grade: {perf_grade}",
            fix_instruction=(
                f"Improve performance from {perf_grade} to B or higher. "
                f"Optimize images, enable compression, minimize JavaScript, "
                f"implement caching, use CDN for static assets."
            ) if status != 'pass' else "No action needed"
        ))

        return criteria

    def _determine_status(
        self,
        criteria_results: List[ReadinessCriterion],
        blocking_issues: List[Dict[str, Any]]
    ) -> str:
        """Determine overall status from criteria."""
        failed_criteria = [c for c in criteria_results if c.status == 'fail']
        warning_criteria = [c for c in criteria_results if c.status == 'warning']

        # Critical failures
        critical_failures = ['No Critical Issues', 'HTTPS Enabled', 'No High Security Risks']
        has_critical_failure = any(c.name in critical_failures and c.status == 'fail'
                                   for c in criteria_results)

        if has_critical_failure or len(failed_criteria) >= 3:
            return READINESS_UNDER_CONSTRUCTION

        if len(failed_criteria) > 0 or len(warning_criteria) >= 3:
            return READINESS_NEEDS_POLISHING

        return READINESS_READY

    def _get_status_description(self, status: str) -> str:
        """Get description for status."""
        descriptions = {
            READINESS_READY: (
                "Website is ready for commercial launch. "
                "All critical tests pass, no blocking issues, "
                "approved for production deployment."
            ),
            READINESS_NEEDS_POLISHING: (
                "Website is functional but has issues requiring attention before launch. "
                "No critical blockers, but quality improvements needed. "
                "Consider soft launch or limited release while addressing issues."
            ),
            READINESS_UNDER_CONSTRUCTION: (
                "Website has significant issues preventing commercial use. "
                "Critical problems must be resolved before launch. "
                "Not recommended for production deployment."
            )
        }
        return descriptions.get(status, "Unknown status")

    def _generate_checklist(
        self,
        criteria_results: List[ReadinessCriterion],
        test_results: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Generate launch checklist."""
        return {
            'https_enabled': any(c.name == 'HTTPS Enabled' and c.status == 'pass'
                                for c in criteria_results),
            'no_critical_issues': any(c.name == 'No Critical Issues' and c.status == 'pass'
                                      for c in criteria_results),
            'no_broken_links': any(c.name == 'No Broken Links' and c.status == 'pass'
                                   for c in criteria_results),
            'forms_functional': any(c.name == 'Forms Functional' and c.status == 'pass'
                                    for c in criteria_results),
            'all_pages_load': any(c.name == 'All Pages Load' and c.status == 'pass'
                                  for c in criteria_results),
            'security_clean': any(c.name == 'No High Security Risks' and c.status == 'pass'
                                  for c in criteria_results),
            'accessibility_compliant': any(c.name == 'Accessibility Score > 80%' and c.status == 'pass'
                                           for c in criteria_results),
            'performance_acceptable': any(c.name == 'Performance Grade B or Higher' and c.status == 'pass'
                                          for c in criteria_results)
        }

    def _generate_next_steps(
        self,
        status: str,
        blocking_issues: List[Dict[str, Any]],
        warnings: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate prioritized next steps."""
        steps = []

        if status == READINESS_UNDER_CONSTRUCTION:
            steps.append("STOP: Do not launch until critical issues resolved")
            for issue in blocking_issues[:5]:
                steps.append(f"FIX: {issue['criterion']} - {issue['description']}")

        elif status == READINESS_NEEDS_POLISHING:
            steps.append("Address blocking issues before full launch")
            for issue in blocking_issues[:3]:
                steps.append(f"Priority: {issue['criterion']}")
            steps.append("Consider soft launch to limited audience")

        else:  # READY
            steps.append("Proceed with launch")
            steps.append("Set up monitoring and error tracking")
            steps.append("Prepare for traffic scaling")
            if warnings:
                steps.append("Schedule post-launch improvements for warnings")

        return steps

    def _estimate_effort(
        self,
        blocking_issues: List[Dict[str, Any]],
        warnings: List[Dict[str, Any]]
    ) -> str:
        """Estimate effort to reach Ready status."""
        if not blocking_issues and not warnings:
            return "Ready now - no additional effort needed"

        total_issues = len(blocking_issues) + len(warnings)

        if total_issues <= 5:
            return "1-2 days of focused work"
        elif total_issues <= 15:
            return "3-5 days of development work"
        elif total_issues <= 30:
            return "1-2 weeks of development work"
        else:
            return "2-4 weeks of significant development effort"
