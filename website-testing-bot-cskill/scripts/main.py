"""
Website Testing Bot - Main Orchestrator

Coordinates all testing modules to perform comprehensive website analysis
and generate detailed reports suitable for agent handoff.
"""

import asyncio
import json
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from .crawlers.site_crawler import SiteCrawler, CrawlResult
from .crawlers.page_parser import PageParser
from .crawlers.resource_collector import ResourceCollector

from .testers.element_tester import ElementTester, ElementTestResult
from .testers.performance_tester import PerformanceTester, PerformanceReport
from .testers.security_tester import SecurityTester, SecurityReport
from .testers.accessibility_tester import AccessibilityTester, AccessibilityReport
from .testers.functionality_tester import FunctionalityTester, FunctionalityReport

from .analyzers.uniqueness_analyzer import UniquenessAnalyzer, UniquenessReport
from .analyzers.commercial_analyzer import CommercialAnalyzer, CommercialReport
from .analyzers.readiness_analyzer import ReadinessAnalyzer, ReadinessReport

from .reporters.report_generator import ReportGenerator, TestReport
from .reporters.agent_handoff_generator import AgentHandoffGenerator, HandoffDocument
from .reporters.grade_calculator import GradeCalculator

from .utils.http_client import HTTPClient
from .utils.validators import validate_url, validate_config


@dataclass
class TestConfig:
    """Configuration for website testing."""
    # Crawling options
    max_depth: int = 10
    max_pages: int = 500
    respect_robots_txt: bool = True
    follow_external_links: bool = False
    crawl_delay: float = 0.5

    # Performance options
    load_test_requests: int = 50
    concurrent_requests: int = 10

    # Security options
    run_security_tests: bool = True

    # Accessibility options
    wcag_level: str = "AA"

    # Output options
    output_format: str = "json"
    generate_handoff: bool = True

    # Timeout
    timeout: int = 30


@dataclass
class WebsiteTestReport:
    """Complete website test report."""
    url: str
    generated_at: str
    test_duration_seconds: float

    # Grades
    commercial_grade: str
    commercial_score: int
    uniqueness_score: int
    uniqueness_rating: str
    readiness_status: str

    # Capacity
    max_concurrent_users: int
    recommended_max_users: int

    # Counts
    total_pages: int
    total_issues: int
    critical_issues: int
    high_issues: int

    # Detailed reports
    summary: Dict[str, Any]
    crawl_summary: Dict[str, Any]
    performance_summary: Dict[str, Any]
    security_summary: Dict[str, Any]
    accessibility_summary: Dict[str, Any]
    uniqueness_summary: Dict[str, Any]

    # All issues
    all_issues: List[Dict[str, Any]]

    # Agent handoff
    agent_handoff: Dict[str, Any]

    # Recommendations
    recommendations: List[Dict[str, Any]]


class WebsiteTestingBot:
    """
    Comprehensive website testing bot.

    Performs exhaustive testing of all website elements and generates
    detailed reports with explicit fix instructions for agent handoff.
    """

    def __init__(self, config: Optional[TestConfig] = None):
        """
        Initialize the website testing bot.

        Args:
            config: Optional test configuration
        """
        self.config = config or TestConfig()
        self.http_client = HTTPClient(timeout=self.config.timeout)

        # Initialize testers
        self.crawler = SiteCrawler(
            max_depth=self.config.max_depth,
            max_pages=self.config.max_pages,
            respect_robots=self.config.respect_robots_txt,
            crawl_delay=self.config.crawl_delay,
            concurrent_requests=self.config.concurrent_requests
        )
        self.element_tester = ElementTester(self.http_client)
        self.performance_tester = PerformanceTester(
            self.http_client,
            load_test_requests=self.config.load_test_requests,
            concurrent_requests=self.config.concurrent_requests
        )
        self.security_tester = SecurityTester(self.http_client)
        self.accessibility_tester = AccessibilityTester(self.config.wcag_level)
        self.functionality_tester = FunctionalityTester()

        # Initialize analyzers
        self.uniqueness_analyzer = UniquenessAnalyzer()
        self.commercial_analyzer = CommercialAnalyzer()
        self.readiness_analyzer = ReadinessAnalyzer()

        # Initialize reporters
        self.report_generator = ReportGenerator()
        self.handoff_generator = AgentHandoffGenerator()
        self.grade_calculator = GradeCalculator()

    async def test_website(
        self,
        url: str,
        competitor_urls: Optional[List[str]] = None
    ) -> WebsiteTestReport:
        """
        Run comprehensive website test.

        Args:
            url: The website URL to test
            competitor_urls: Optional URLs for uniqueness comparison

        Returns:
            WebsiteTestReport with all grades, scores, and issues
        """
        start_time = datetime.now()

        # Validate URL
        is_valid, normalized_url, errors = validate_url(url)
        if not is_valid:
            raise ValueError(f"Invalid URL: {', '.join(errors)}")

        url = normalized_url
        print(f"Starting comprehensive test of {url}")

        # Phase 1: Crawl the website
        print("Phase 1: Crawling website...")
        crawl_result = await self.crawler.crawl_async(url)
        print(f"  - Found {crawl_result.total_pages} pages, {crawl_result.total_resources} resources")

        # Phase 2: Fetch main page for detailed analysis
        print("Phase 2: Fetching main page...")
        response = await self.http_client.get_async(url)
        html_content = response.text

        # Phase 3: Test all elements
        print("Phase 3: Testing elements...")
        element_results = await self._test_all_elements(crawl_result, url)
        print(f"  - Tested {len(element_results)} elements")

        # Phase 4: Performance testing
        print("Phase 4: Performance testing...")
        performance_report = await self.performance_tester.test_performance(url)
        print(f"  - Performance grade: {performance_report.grade}")

        # Phase 5: Security testing
        print("Phase 5: Security testing...")
        security_report = await self.security_tester.test_security(url)
        print(f"  - Security grade: {security_report.grade}")

        # Phase 6: Accessibility testing
        print("Phase 6: Accessibility testing...")
        accessibility_report = self.accessibility_tester.test_accessibility(url, html_content)
        print(f"  - Accessibility score: {accessibility_report.score}")

        # Phase 7: Uniqueness analysis
        print("Phase 7: Analyzing uniqueness...")
        uniqueness_report = self.uniqueness_analyzer.analyze_uniqueness(
            url, html_content, '', competitor_urls
        )
        print(f"  - Uniqueness score: {uniqueness_report.score} ({uniqueness_report.rating})")

        # Phase 8: Commercial readiness analysis
        print("Phase 8: Analyzing commercial readiness...")
        commercial_report = self.commercial_analyzer.analyze_commercial_readiness(
            url,
            performance_data=asdict(performance_report) if performance_report else {},
            security_data=asdict(security_report) if security_report else {},
            accessibility_data=asdict(accessibility_report) if accessibility_report else {},
            test_results={
                'pages': crawl_result.pages,
                'broken_links': crawl_result.broken_links,
                'issues': self._collect_all_issues(element_results)
            }
        )
        print(f"  - Commercial grade: {commercial_report.grade}")

        # Phase 9: Overall readiness assessment
        print("Phase 9: Assessing readiness...")
        all_issues = self._compile_all_issues(
            element_results,
            performance_report,
            security_report,
            accessibility_report,
            commercial_report
        )

        readiness_report = self.readiness_analyzer.analyze_readiness(
            url,
            all_issues,
            {
                'pages': crawl_result.pages,
                'broken_links': crawl_result.broken_links,
                'performance': asdict(performance_report) if performance_report else {},
                'security': asdict(security_report) if security_report else {},
                'accessibility': asdict(accessibility_report) if accessibility_report else {}
            },
            asdict(commercial_report) if commercial_report else {},
            asdict(uniqueness_report) if uniqueness_report else {}
        )
        print(f"  - Readiness status: {readiness_report.status}")

        # Phase 10: Generate reports
        print("Phase 10: Generating reports...")

        # Generate agent handoff
        handoff_doc = self.handoff_generator.generate_handoff(
            url,
            all_issues,
            {
                'commercial_readiness': {
                    'grade': commercial_report.grade,
                    'score': commercial_report.score
                },
                'uniqueness': {
                    'score': uniqueness_report.score,
                    'rating': uniqueness_report.rating
                },
                'readiness_status': {
                    'status': readiness_report.status
                },
                'performance': {
                    'grade': performance_report.grade,
                    'score': performance_report.score
                },
                'security': {
                    'grade': security_report.grade,
                    'score': security_report.score
                },
                'accessibility': {
                    'grade': accessibility_report.grade,
                    'score': accessibility_report.score
                }
            },
            readiness_report
        )

        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()

        # Count issues by severity
        critical_count = len([i for i in all_issues if i.get('severity') == 'critical'])
        high_count = len([i for i in all_issues if i.get('severity') == 'high'])

        # Build final report
        report = WebsiteTestReport(
            url=url,
            generated_at=datetime.now().isoformat(),
            test_duration_seconds=duration,

            commercial_grade=commercial_report.grade,
            commercial_score=commercial_report.score,
            uniqueness_score=uniqueness_report.score,
            uniqueness_rating=uniqueness_report.rating,
            readiness_status=readiness_report.status,

            max_concurrent_users=commercial_report.max_concurrent_users,
            recommended_max_users=commercial_report.recommended_max_users,

            total_pages=crawl_result.total_pages,
            total_issues=len(all_issues),
            critical_issues=critical_count,
            high_issues=high_count,

            summary={
                'recommendation': self._get_recommendation(
                    readiness_report.status,
                    commercial_report.grade,
                    critical_count
                ),
                'readiness_description': readiness_report.status_description,
                'commercial_description': commercial_report.grade_description,
                'uniqueness_description': uniqueness_report.rating_description
            },

            crawl_summary={
                'total_pages': crawl_result.total_pages,
                'total_resources': crawl_result.total_resources,
                'broken_links': len(crawl_result.broken_links),
                'external_links': len(crawl_result.external_links),
                'crawl_duration': crawl_result.crawl_duration_seconds
            },

            performance_summary={
                'grade': performance_report.grade,
                'score': performance_report.score,
                'capacity': {
                    'max_users': performance_report.capacity_estimate.max_concurrent_users,
                    'bottleneck': performance_report.capacity_estimate.bottleneck
                }
            },

            security_summary={
                'grade': security_report.grade,
                'score': security_report.score,
                'ssl_valid': security_report.ssl_info.valid,
                'issues_count': len(security_report.all_issues)
            },

            accessibility_summary={
                'grade': accessibility_report.grade,
                'score': accessibility_report.score,
                'wcag_level': accessibility_report.wcag_level_tested,
                'issues_count': len(accessibility_report.issues)
            },

            uniqueness_summary={
                'score': uniqueness_report.score,
                'rating': uniqueness_report.rating,
                'templates_detected': [
                    {'name': t.name, 'confidence': t.confidence}
                    for t in uniqueness_report.templates_detected[:3]
                ],
                'customization_level': uniqueness_report.customization_level
            },

            all_issues=all_issues,

            agent_handoff=asdict(handoff_doc),

            recommendations=self._generate_top_recommendations(
                all_issues,
                readiness_report,
                commercial_report
            )
        )

        print(f"\nTest complete in {duration:.1f} seconds")
        print(f"Results: {readiness_report.status} | Commercial: {commercial_report.grade} | Uniqueness: {uniqueness_report.score}")

        return report

    async def _test_all_elements(
        self,
        crawl_result: CrawlResult,
        base_url: str
    ) -> List[ElementTestResult]:
        """Test all discovered elements."""
        results = []

        # Test buttons
        for button in crawl_result.all_buttons[:50]:  # Limit for performance
            result = self.element_tester.test_button(button, button.get('source_page', base_url))
            results.append(result)

        # Test links
        for link in crawl_result.all_links[:100]:
            result = self.element_tester.test_link(link, link.get('source_page', base_url))
            results.append(result)

        # Test images
        for image in crawl_result.all_images[:50]:
            result = self.element_tester.test_image(image, image.get('source_page', base_url))
            results.append(result)

        # Test forms
        for form in crawl_result.all_forms[:20]:
            result = self.element_tester.test_form(form, form.get('source_page', base_url))
            results.append(result)

        # Test menus
        for menu in crawl_result.all_menus[:10]:
            result = self.element_tester.test_menu(menu, menu.get('source_page', base_url))
            results.append(result)

        return results

    def _collect_all_issues(
        self,
        element_results: List[ElementTestResult]
    ) -> List[Dict[str, Any]]:
        """Collect all issues from element tests."""
        issues = []
        for result in element_results:
            for issue in result.issues:
                issues.append(asdict(issue))
        return issues

    def _compile_all_issues(
        self,
        element_results: List[ElementTestResult],
        performance_report: PerformanceReport,
        security_report: SecurityReport,
        accessibility_report: AccessibilityReport,
        commercial_report: CommercialReport
    ) -> List[Dict[str, Any]]:
        """Compile all issues from all sources."""
        all_issues = []
        issue_id = 1

        # Element issues
        for result in element_results:
            for issue in result.issues:
                all_issues.append({
                    'id': issue_id,
                    'source': 'element_test',
                    'severity': issue.severity,
                    'category': issue.category,
                    'element_type': issue.element_type,
                    'description': issue.description,
                    'fix_instruction': issue.fix_instruction,
                    'location': issue.location,
                    'wcag_reference': issue.wcag_reference
                })
                issue_id += 1

        # Performance issues
        for issue in performance_report.issues:
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
        for issue in security_report.all_issues:
            all_issues.append({
                'id': issue_id,
                'source': 'security_test',
                'severity': issue.severity,
                'category': 'security',
                'element_type': '',
                'description': issue.description,
                'fix_instruction': issue.fix_instruction,
                'location': {},
                'wcag_reference': None
            })
            issue_id += 1

        # Accessibility issues
        for issue in accessibility_report.issues:
            all_issues.append({
                'id': issue_id,
                'source': 'accessibility_test',
                'severity': issue.severity,
                'category': 'accessibility',
                'element_type': '',
                'description': issue.description,
                'fix_instruction': issue.fix_instruction,
                'location': {'element_selector': issue.element_selector},
                'wcag_reference': issue.wcag_criterion
            })
            issue_id += 1

        # Commercial issues
        for issue in commercial_report.issues:
            all_issues.append({
                'id': issue_id,
                'source': 'commercial_analysis',
                'severity': issue.get('severity', 'medium'),
                'category': 'commercial',
                'element_type': '',
                'description': issue.get('description', ''),
                'fix_instruction': issue.get('fix_instruction', ''),
                'location': {},
                'wcag_reference': None
            })
            issue_id += 1

        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
        all_issues.sort(key=lambda x: severity_order.get(x['severity'], 5))

        return all_issues

    def _get_recommendation(
        self,
        status: str,
        grade: str,
        critical_count: int
    ) -> str:
        """Get overall recommendation."""
        if status == 'UNDER_CONSTRUCTION' or critical_count > 0:
            return "DO NOT LAUNCH - Critical issues must be resolved"
        elif status == 'NEEDS_POLISHING':
            return "SOFT LAUNCH ONLY - Address issues before full launch"
        elif grade in ['D', 'F']:
            return "LIMITED LAUNCH - Scaling concerns prevent high traffic"
        elif grade in ['C', 'C+']:
            return "PROCEED WITH CAUTION - Monitor closely"
        else:
            return "READY FOR LAUNCH - All systems go"

    def _generate_top_recommendations(
        self,
        all_issues: List[Dict[str, Any]],
        readiness_report: ReadinessReport,
        commercial_report: CommercialReport
    ) -> List[Dict[str, Any]]:
        """Generate top recommendations."""
        recommendations = []

        # Add next steps from readiness report
        for i, step in enumerate(readiness_report.next_steps[:5]):
            recommendations.append({
                'priority': i + 1,
                'category': 'launch_preparation',
                'recommendation': step
            })

        # Add infrastructure recommendations
        for rec in commercial_report.infrastructure_recommendations[:3]:
            recommendations.append({
                'priority': len(recommendations) + 1,
                'category': 'infrastructure',
                'recommendation': rec.get('title', '') + ': ' + rec.get('description', '')
            })

        return recommendations


async def run_website_test(
    url: str,
    config: Optional[TestConfig] = None,
    competitor_urls: Optional[List[str]] = None
) -> WebsiteTestReport:
    """
    Run comprehensive website test.

    This is the main entry point for running tests.

    Args:
        url: The website URL to test
        config: Optional test configuration
        competitor_urls: Optional URLs for uniqueness comparison

    Returns:
        WebsiteTestReport with all grades, scores, and issues
    """
    bot = WebsiteTestingBot(config)
    return await bot.test_website(url, competitor_urls)


def run_test_sync(
    url: str,
    config: Optional[TestConfig] = None,
    competitor_urls: Optional[List[str]] = None
) -> WebsiteTestReport:
    """
    Synchronous wrapper for running website tests.

    Args:
        url: The website URL to test
        config: Optional test configuration
        competitor_urls: Optional URLs for uniqueness comparison

    Returns:
        WebsiteTestReport with all grades, scores, and issues
    """
    return asyncio.run(run_website_test(url, config, competitor_urls))


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python main.py <url>")
        sys.exit(1)

    test_url = sys.argv[1]
    print(f"Testing website: {test_url}")

    report = run_test_sync(test_url)

    print("\n" + "=" * 60)
    print("WEBSITE TEST RESULTS")
    print("=" * 60)
    print(f"\nURL: {report.url}")
    print(f"Test Duration: {report.test_duration_seconds:.1f} seconds")
    print(f"\n--- GRADES ---")
    print(f"Commercial Readiness: {report.commercial_grade} ({report.commercial_score}/100)")
    print(f"Uniqueness: {report.uniqueness_score}/100 ({report.uniqueness_rating})")
    print(f"Readiness Status: {report.readiness_status}")
    print(f"\n--- CAPACITY ---")
    print(f"Max Concurrent Users: {report.max_concurrent_users:,}")
    print(f"Recommended Max: {report.recommended_max_users:,}")
    print(f"\n--- ISSUES ---")
    print(f"Total Issues: {report.total_issues}")
    print(f"Critical: {report.critical_issues}")
    print(f"High: {report.high_issues}")
    print(f"\n--- RECOMMENDATION ---")
    print(report.summary['recommendation'])
