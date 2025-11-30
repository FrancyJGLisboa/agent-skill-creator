"""
Report generator for comprehensive test reports.

Generates structured reports from all test results.
"""

import json
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class TestReport:
    """Complete website test report."""
    report_id: str
    generated_at: str
    url: str
    grades: Dict[str, Any]
    summary: Dict[str, Any]
    element_tests: Dict[str, Any]
    performance_tests: Dict[str, Any]
    security_tests: Dict[str, Any]
    accessibility_tests: Dict[str, Any]
    uniqueness_analysis: Dict[str, Any]
    commercial_analysis: Dict[str, Any]
    readiness_assessment: Dict[str, Any]
    all_issues: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    agent_handoff: Dict[str, Any]


class ReportGenerator:
    """
    Generates comprehensive test reports.

    Aggregates all test results into structured reports.
    """

    def __init__(self):
        """Initialize report generator."""
        pass

    def generate_report(
        self,
        url: str,
        crawl_result: Any,
        element_results: List[Any],
        performance_report: Any,
        security_report: Any,
        accessibility_report: Any,
        uniqueness_report: Any,
        commercial_report: Any,
        readiness_report: Any
    ) -> TestReport:
        """
        Generate comprehensive test report.

        Args:
            url: Tested URL
            crawl_result: Crawl results
            element_results: Element test results
            performance_report: Performance test report
            security_report: Security test report
            accessibility_report: Accessibility test report
            uniqueness_report: Uniqueness analysis report
            commercial_report: Commercial readiness report
            readiness_report: Overall readiness report

        Returns:
            TestReport with all data
        """
        report_id = f"wtr_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        generated_at = datetime.now().isoformat()

        # Compile grades
        grades = self._compile_grades(
            commercial_report, uniqueness_report, readiness_report,
            performance_report, security_report, accessibility_report
        )

        # Generate summary
        summary = self._generate_summary(
            crawl_result, element_results, grades
        )

        # Compile all issues
        all_issues = self._compile_all_issues(
            element_results, performance_report, security_report,
            accessibility_report, commercial_report, readiness_report
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            all_issues, performance_report, security_report,
            commercial_report, readiness_report
        )

        # Generate agent handoff
        agent_handoff = self._generate_agent_handoff(
            all_issues, grades, readiness_report
        )

        return TestReport(
            report_id=report_id,
            generated_at=generated_at,
            url=url,
            grades=grades,
            summary=summary,
            element_tests=self._format_element_tests(element_results),
            performance_tests=self._format_performance(performance_report),
            security_tests=self._format_security(security_report),
            accessibility_tests=self._format_accessibility(accessibility_report),
            uniqueness_analysis=self._format_uniqueness(uniqueness_report),
            commercial_analysis=self._format_commercial(commercial_report),
            readiness_assessment=self._format_readiness(readiness_report),
            all_issues=all_issues,
            recommendations=recommendations,
            agent_handoff=agent_handoff
        )

    def _compile_grades(
        self,
        commercial: Any,
        uniqueness: Any,
        readiness: Any,
        performance: Any,
        security: Any,
        accessibility: Any
    ) -> Dict[str, Any]:
        """Compile all grades into summary."""
        return {
            'commercial_readiness': {
                'grade': getattr(commercial, 'grade', 'N/A') if commercial else 'N/A',
                'score': getattr(commercial, 'score', 0) if commercial else 0,
                'max_users': getattr(commercial, 'max_concurrent_users', 0) if commercial else 0,
                'description': getattr(commercial, 'grade_description', '') if commercial else ''
            },
            'uniqueness': {
                'score': getattr(uniqueness, 'score', 0) if uniqueness else 0,
                'rating': getattr(uniqueness, 'rating', 'N/A') if uniqueness else 'N/A',
                'description': getattr(uniqueness, 'rating_description', '') if uniqueness else ''
            },
            'readiness_status': {
                'status': getattr(readiness, 'status', 'UNKNOWN') if readiness else 'UNKNOWN',
                'description': getattr(readiness, 'status_description', '') if readiness else ''
            },
            'performance': {
                'grade': getattr(performance, 'grade', 'N/A') if performance else 'N/A',
                'score': getattr(performance, 'score', 0) if performance else 0
            },
            'security': {
                'grade': getattr(security, 'grade', 'N/A') if security else 'N/A',
                'score': getattr(security, 'score', 0) if security else 0
            },
            'accessibility': {
                'grade': getattr(accessibility, 'grade', 'N/A') if accessibility else 'N/A',
                'score': getattr(accessibility, 'score', 0) if accessibility else 0
            }
        }

    def _generate_summary(
        self,
        crawl_result: Any,
        element_results: List[Any],
        grades: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate executive summary."""
        total_issues = 0
        critical_issues = 0
        high_issues = 0

        for result in element_results:
            if hasattr(result, 'issues'):
                total_issues += len(result.issues)
                for issue in result.issues:
                    if hasattr(issue, 'severity'):
                        if issue.severity == 'critical':
                            critical_issues += 1
                        elif issue.severity == 'high':
                            high_issues += 1

        return {
            'total_pages': getattr(crawl_result, 'total_pages', 0) if crawl_result else 0,
            'total_resources': getattr(crawl_result, 'total_resources', 0) if crawl_result else 0,
            'total_issues': total_issues,
            'critical_issues': critical_issues,
            'high_issues': high_issues,
            'commercial_grade': grades['commercial_readiness']['grade'],
            'uniqueness_score': grades['uniqueness']['score'],
            'readiness_status': grades['readiness_status']['status'],
            'recommendation': self._get_overall_recommendation(grades, critical_issues)
        }

    def _get_overall_recommendation(
        self,
        grades: Dict[str, Any],
        critical_issues: int
    ) -> str:
        """Get overall recommendation."""
        status = grades['readiness_status']['status']
        commercial_grade = grades['commercial_readiness']['grade']

        if status == 'UNDER_CONSTRUCTION' or critical_issues > 0:
            return "DO NOT LAUNCH - Critical issues must be resolved first"
        elif status == 'NEEDS_POLISHING':
            return "SOFT LAUNCH ONLY - Address issues before full commercial launch"
        elif commercial_grade in ['D', 'F']:
            return "LIMITED LAUNCH - Scaling concerns prevent high-traffic deployment"
        elif commercial_grade in ['C', 'C+']:
            return "PROCEED WITH CAUTION - Monitor closely, prepare for scaling"
        else:
            return "READY FOR LAUNCH - All systems go for commercial deployment"

    def _compile_all_issues(
        self,
        element_results: List[Any],
        performance: Any,
        security: Any,
        accessibility: Any,
        commercial: Any,
        readiness: Any
    ) -> List[Dict[str, Any]]:
        """Compile all issues from all sources."""
        all_issues = []
        issue_id = 1

        # Element issues
        for result in element_results:
            if hasattr(result, 'issues'):
                for issue in result.issues:
                    all_issues.append({
                        'id': issue_id,
                        'source': 'element_test',
                        'severity': getattr(issue, 'severity', 'medium'),
                        'category': getattr(issue, 'category', 'unknown'),
                        'element_type': getattr(issue, 'element_type', ''),
                        'description': getattr(issue, 'description', ''),
                        'fix_instruction': getattr(issue, 'fix_instruction', ''),
                        'location': getattr(issue, 'location', {}),
                        'wcag_reference': getattr(issue, 'wcag_reference', None)
                    })
                    issue_id += 1

        # Performance issues
        if performance and hasattr(performance, 'issues'):
            for issue in performance.issues:
                all_issues.append({
                    'id': issue_id,
                    'source': 'performance_test',
                    'severity': issue.get('severity', 'medium'),
                    'category': 'performance',
                    'element_type': '',
                    'description': issue.get('description', ''),
                    'fix_instruction': issue.get('fix_instruction', ''),
                    'location': {},
                    'wcag_reference': None
                })
                issue_id += 1

        # Security issues
        if security and hasattr(security, 'all_issues'):
            for issue in security.all_issues:
                all_issues.append({
                    'id': issue_id,
                    'source': 'security_test',
                    'severity': getattr(issue, 'severity', 'medium'),
                    'category': 'security',
                    'element_type': '',
                    'description': getattr(issue, 'description', ''),
                    'fix_instruction': getattr(issue, 'fix_instruction', ''),
                    'location': {},
                    'wcag_reference': None
                })
                issue_id += 1

        # Accessibility issues
        if accessibility and hasattr(accessibility, 'issues'):
            for issue in accessibility.issues:
                all_issues.append({
                    'id': issue_id,
                    'source': 'accessibility_test',
                    'severity': getattr(issue, 'severity', 'medium'),
                    'category': 'accessibility',
                    'element_type': '',
                    'description': getattr(issue, 'description', ''),
                    'fix_instruction': getattr(issue, 'fix_instruction', ''),
                    'location': {
                        'element_selector': getattr(issue, 'element_selector', '')
                    },
                    'wcag_reference': getattr(issue, 'wcag_criterion', None)
                })
                issue_id += 1

        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
        all_issues.sort(key=lambda x: severity_order.get(x['severity'], 5))

        return all_issues

    def _generate_recommendations(
        self,
        all_issues: List[Dict[str, Any]],
        performance: Any,
        security: Any,
        commercial: Any,
        readiness: Any
    ) -> List[Dict[str, Any]]:
        """Generate prioritized recommendations."""
        recommendations = []

        # Add recommendations from each report
        if performance and hasattr(performance, 'recommendations'):
            for rec in performance.recommendations:
                recommendations.append({
                    'source': 'performance',
                    **rec
                })

        if commercial and hasattr(commercial, 'infrastructure_recommendations'):
            for rec in commercial.infrastructure_recommendations:
                recommendations.append({
                    'source': 'infrastructure',
                    **rec
                })

        if readiness and hasattr(readiness, 'next_steps'):
            for i, step in enumerate(readiness.next_steps):
                recommendations.append({
                    'source': 'readiness',
                    'priority': 'high' if i < 3 else 'medium',
                    'category': 'launch_preparation',
                    'title': step,
                    'description': step
                })

        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        recommendations.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 4))

        return recommendations

    def _generate_agent_handoff(
        self,
        all_issues: List[Dict[str, Any]],
        grades: Dict[str, Any],
        readiness: Any
    ) -> Dict[str, Any]:
        """Generate agent handoff document."""
        return {
            'summary': {
                'total_issues_to_fix': len(all_issues),
                'critical_count': len([i for i in all_issues if i['severity'] == 'critical']),
                'high_count': len([i for i in all_issues if i['severity'] == 'high']),
                'current_status': grades['readiness_status']['status'],
                'target_status': 'READY',
                'commercial_grade': grades['commercial_readiness']['grade']
            },
            'fix_order': self._generate_fix_order(all_issues),
            'issues': all_issues,
            'checklist': getattr(readiness, 'checklist', {}) if readiness else {},
            'instructions': (
                "IMPORTANT: This handoff document is for an AI agent or developer "
                "to fix all identified issues. Each issue includes explicit fix instructions. "
                "Do NOT make assumptions - follow instructions exactly. "
                "After fixing each issue, verify using the provided test criteria. "
                "Work through issues in the order specified in 'fix_order'."
            )
        }

    def _generate_fix_order(self, all_issues: List[Dict[str, Any]]) -> List[int]:
        """Generate recommended order for fixing issues."""
        # Group by severity and category
        critical = [i['id'] for i in all_issues if i['severity'] == 'critical']
        security_high = [i['id'] for i in all_issues
                        if i['severity'] == 'high' and i['category'] == 'security']
        functionality_high = [i['id'] for i in all_issues
                            if i['severity'] == 'high' and i['category'] in ['functionality', 'broken_link', 'broken_image']]
        other_high = [i['id'] for i in all_issues
                     if i['severity'] == 'high' and i['id'] not in security_high + functionality_high]
        medium = [i['id'] for i in all_issues if i['severity'] == 'medium']
        low = [i['id'] for i in all_issues if i['severity'] == 'low']

        return critical + security_high + functionality_high + other_high + medium + low

    def _format_element_tests(self, results: List[Any]) -> Dict[str, Any]:
        """Format element test results."""
        total_tests = 0
        total_passed = 0
        by_element_type = {}

        for result in results:
            if hasattr(result, 'tests_run'):
                total_tests += result.tests_run
                total_passed += result.tests_passed

                element_type = getattr(result, 'element_type', 'unknown')
                if element_type not in by_element_type:
                    by_element_type[element_type] = {'tested': 0, 'passed': 0, 'issues': 0}

                by_element_type[element_type]['tested'] += 1
                by_element_type[element_type]['passed'] += 1 if result.tests_failed == 0 else 0
                by_element_type[element_type]['issues'] += len(result.issues) if hasattr(result, 'issues') else 0

        return {
            'total_tests': total_tests,
            'tests_passed': total_passed,
            'pass_rate': (total_passed / total_tests * 100) if total_tests > 0 else 0,
            'by_element_type': by_element_type
        }

    def _format_performance(self, report: Any) -> Dict[str, Any]:
        """Format performance report."""
        if not report:
            return {}

        return {
            'grade': getattr(report, 'grade', 'N/A'),
            'score': getattr(report, 'score', 0),
            'core_web_vitals': self._format_web_vitals(report),
            'capacity_estimate': self._format_capacity(report),
            'issue_count': len(getattr(report, 'issues', []))
        }

    def _format_web_vitals(self, report: Any) -> Dict[str, Any]:
        """Format Core Web Vitals."""
        if not report or not hasattr(report, 'core_web_vitals'):
            return {}

        vitals = {}
        for key, metric in report.core_web_vitals.items():
            vitals[key] = {
                'value': getattr(metric, 'value', 0),
                'unit': getattr(metric, 'unit', ''),
                'status': getattr(metric, 'status', 'unknown')
            }
        return vitals

    def _format_capacity(self, report: Any) -> Dict[str, Any]:
        """Format capacity estimate."""
        if not report or not hasattr(report, 'capacity_estimate'):
            return {}

        cap = report.capacity_estimate
        return {
            'max_users': getattr(cap, 'max_concurrent_users', 0),
            'recommended_users': getattr(cap, 'recommended_concurrent_users', 0),
            'bottleneck': getattr(cap, 'bottleneck', ''),
            'confidence': getattr(cap, 'confidence', 'low')
        }

    def _format_security(self, report: Any) -> Dict[str, Any]:
        """Format security report."""
        if not report:
            return {}

        return {
            'grade': getattr(report, 'grade', 'N/A'),
            'score': getattr(report, 'score', 0),
            'ssl_valid': getattr(report.ssl_info, 'valid', False) if hasattr(report, 'ssl_info') else False,
            'issue_count': len(getattr(report, 'all_issues', []))
        }

    def _format_accessibility(self, report: Any) -> Dict[str, Any]:
        """Format accessibility report."""
        if not report:
            return {}

        return {
            'grade': getattr(report, 'grade', 'N/A'),
            'score': getattr(report, 'score', 0),
            'wcag_level': getattr(report, 'wcag_level_tested', 'AA'),
            'issue_count': len(getattr(report, 'issues', [])),
            'issues_by_principle': getattr(report, 'issues_by_principle', {})
        }

    def _format_uniqueness(self, report: Any) -> Dict[str, Any]:
        """Format uniqueness report."""
        if not report:
            return {}

        return {
            'score': getattr(report, 'score', 0),
            'rating': getattr(report, 'rating', 'N/A'),
            'description': getattr(report, 'rating_description', ''),
            'templates_detected': [
                {
                    'name': t.name,
                    'confidence': t.confidence,
                    'category': t.category
                }
                for t in getattr(report, 'templates_detected', [])
            ],
            'customization_level': getattr(report, 'customization_level', ''),
            'breakdown': getattr(report, 'breakdown', {})
        }

    def _format_commercial(self, report: Any) -> Dict[str, Any]:
        """Format commercial report."""
        if not report:
            return {}

        return {
            'grade': getattr(report, 'grade', 'N/A'),
            'score': getattr(report, 'score', 0),
            'max_users': getattr(report, 'max_concurrent_users', 0),
            'recommended_max': getattr(report, 'recommended_max_users', 0),
            'bottlenecks': getattr(report, 'bottlenecks', []),
            'cost_estimates': getattr(report, 'cost_estimates', {}),
            'risk_level': report.risk_assessment.get('overall_risk_level', 'unknown') if hasattr(report, 'risk_assessment') else 'unknown'
        }

    def _format_readiness(self, report: Any) -> Dict[str, Any]:
        """Format readiness report."""
        if not report:
            return {}

        return {
            'status': getattr(report, 'status', 'UNKNOWN'),
            'description': getattr(report, 'status_description', ''),
            'blocking_issues': len(getattr(report, 'blocking_issues', [])),
            'warnings': len(getattr(report, 'warnings', [])),
            'checklist': getattr(report, 'checklist', {}),
            'estimated_effort': getattr(report, 'estimated_effort_to_ready', 'Unknown'),
            'next_steps': getattr(report, 'next_steps', [])
        }

    def to_json(self, report: TestReport) -> str:
        """Convert report to JSON string."""
        return json.dumps(asdict(report), indent=2, default=str)

    def to_dict(self, report: TestReport) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return asdict(report)
