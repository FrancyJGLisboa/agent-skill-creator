"""
Performance tester for website load and speed analysis.

Measures Core Web Vitals, resource loading, and capacity estimation.
"""

import time
import asyncio
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor

from ..utils.http_client import HTTPClient
from ..utils.constants import (
    SEVERITY_CRITICAL,
    SEVERITY_HIGH,
    SEVERITY_MEDIUM,
    SEVERITY_LOW,
    PERFORMANCE_THRESHOLDS,
    COMMERCIAL_GRADES
)


@dataclass
class PerformanceMetric:
    """A single performance metric measurement."""
    name: str
    value: float
    unit: str
    status: str  # good, needs_improvement, poor
    threshold_good: float
    threshold_poor: float


@dataclass
class CapacityEstimate:
    """Estimated capacity for concurrent users."""
    max_concurrent_users: int
    recommended_concurrent_users: int
    bottleneck: str
    confidence: str  # high, medium, low
    methodology: str
    factors: Dict[str, Any]


@dataclass
class PerformanceReport:
    """Complete performance testing report."""
    url: str
    test_duration_seconds: float
    metrics: List[PerformanceMetric]
    core_web_vitals: Dict[str, PerformanceMetric]
    resource_analysis: Dict[str, Any]
    capacity_estimate: CapacityEstimate
    issues: List[Dict[str, Any]]
    grade: str
    score: int
    recommendations: List[Dict[str, Any]]


class PerformanceTester:
    """
    Comprehensive performance tester for websites.

    Measures load times, Core Web Vitals, and estimates scaling capacity.
    """

    def __init__(
        self,
        http_client: Optional[HTTPClient] = None,
        load_test_requests: int = 50,
        concurrent_requests: int = 10
    ):
        """
        Initialize performance tester.

        Args:
            http_client: HTTP client for requests
            load_test_requests: Number of requests for load testing
            concurrent_requests: Concurrent requests for load testing
        """
        self.http_client = http_client or HTTPClient()
        self.load_test_requests = load_test_requests
        self.concurrent_requests = concurrent_requests

    async def test_performance(
        self,
        url: str,
        pages: List[Dict[str, Any]] = None
    ) -> PerformanceReport:
        """
        Run comprehensive performance tests.

        Args:
            url: Base URL to test
            pages: List of crawled pages with timing data

        Returns:
            PerformanceReport with all metrics and analysis
        """
        start_time = time.time()
        issues = []
        recommendations = []

        # Collect page load metrics
        page_metrics = await self._measure_page_load(url)

        # Analyze resources
        response = await self.http_client.get_async(url)
        resource_analysis = self._analyze_resources(response)

        # Calculate Core Web Vitals (simulated from available data)
        core_web_vitals = self._calculate_web_vitals(page_metrics, resource_analysis)

        # Run load test
        load_results = await self._run_load_test(url)

        # Estimate capacity
        capacity = self._estimate_capacity(page_metrics, load_results, resource_analysis)

        # Generate issues from metrics
        issues.extend(self._generate_performance_issues(core_web_vitals, resource_analysis))

        # Generate recommendations
        recommendations.extend(self._generate_recommendations(core_web_vitals, resource_analysis, capacity))

        # Calculate overall score and grade
        score = self._calculate_performance_score(core_web_vitals, resource_analysis)
        grade = self._score_to_grade(score)

        test_duration = time.time() - start_time

        return PerformanceReport(
            url=url,
            test_duration_seconds=test_duration,
            metrics=[page_metrics],
            core_web_vitals=core_web_vitals,
            resource_analysis=resource_analysis,
            capacity_estimate=capacity,
            issues=issues,
            grade=grade,
            score=score,
            recommendations=recommendations
        )

    async def _measure_page_load(self, url: str) -> PerformanceMetric:
        """Measure page load timing."""
        response = await self.http_client.get_async(url)

        ttfb = response.elapsed_ms * 0.3  # Estimate TTFB as portion of total time
        total_time = response.elapsed_ms

        status = 'good' if total_time < 2000 else 'needs_improvement' if total_time < 4000 else 'poor'

        return PerformanceMetric(
            name='page_load_time',
            value=total_time,
            unit='ms',
            status=status,
            threshold_good=2000,
            threshold_poor=4000
        )

    def _analyze_resources(self, response) -> Dict[str, Any]:
        """Analyze page resources from response."""
        content = response.text
        content_length = response.content_length

        # Count resources from HTML
        import re

        scripts = len(re.findall(r'<script[^>]*src=', content, re.I))
        inline_scripts = len(re.findall(r'<script[^>]*>(?!.*src=)', content, re.I))
        stylesheets = len(re.findall(r'<link[^>]*rel=["\']stylesheet["\']', content, re.I))
        inline_styles = len(re.findall(r'<style[^>]*>', content, re.I))
        images = len(re.findall(r'<img[^>]*src=', content, re.I))
        fonts = len(re.findall(r'@font-face|\.woff|\.woff2|\.ttf', content, re.I))

        # Estimate sizes
        html_size = len(content.encode('utf-8'))

        return {
            'html_size_bytes': html_size,
            'total_size_bytes': content_length,
            'resource_counts': {
                'external_scripts': scripts,
                'inline_scripts': inline_scripts,
                'external_stylesheets': stylesheets,
                'inline_styles': inline_styles,
                'images': images,
                'fonts': fonts,
                'total_requests': scripts + stylesheets + images + 1
            },
            'compression': {
                'gzip_enabled': 'gzip' in response.headers.get('content-encoding', ''),
                'br_enabled': 'br' in response.headers.get('content-encoding', '')
            },
            'caching': {
                'cache_control': response.headers.get('cache-control'),
                'etag': response.headers.get('etag') is not None,
                'expires': response.headers.get('expires')
            }
        }

    def _calculate_web_vitals(
        self,
        page_metric: PerformanceMetric,
        resource_analysis: Dict[str, Any]
    ) -> Dict[str, PerformanceMetric]:
        """Calculate Core Web Vitals estimates."""
        # These are estimates based on available data
        # Real measurements would require browser-level instrumentation

        total_load = page_metric.value
        resource_count = resource_analysis['resource_counts']['total_requests']
        html_size = resource_analysis['html_size_bytes']

        # Estimate LCP (Largest Contentful Paint)
        # Based on page load time and resource count
        lcp_estimate = total_load * 0.8 + (resource_count * 20)
        lcp_status = self._get_status(lcp_estimate, PERFORMANCE_THRESHOLDS['lcp'])

        # Estimate FID (First Input Delay)
        # Based on JavaScript count
        script_count = resource_analysis['resource_counts']['external_scripts']
        fid_estimate = min(50 + (script_count * 15), 500)
        fid_status = self._get_status(fid_estimate, PERFORMANCE_THRESHOLDS['fid'])

        # Estimate CLS (Cumulative Layout Shift)
        # Based on images without dimensions (we estimate)
        image_count = resource_analysis['resource_counts']['images']
        cls_estimate = min(image_count * 0.02, 0.3)
        cls_status = self._get_status(cls_estimate, PERFORMANCE_THRESHOLDS['cls'])

        # Calculate TTFB
        ttfb_estimate = total_load * 0.25
        ttfb_status = self._get_status(ttfb_estimate, PERFORMANCE_THRESHOLDS['ttfb'])

        # Calculate FCP
        fcp_estimate = total_load * 0.5
        fcp_status = self._get_status(fcp_estimate, PERFORMANCE_THRESHOLDS['fcp'])

        return {
            'lcp': PerformanceMetric(
                name='Largest Contentful Paint',
                value=lcp_estimate,
                unit='ms',
                status=lcp_status,
                threshold_good=PERFORMANCE_THRESHOLDS['lcp']['good'],
                threshold_poor=PERFORMANCE_THRESHOLDS['lcp']['needs_improvement']
            ),
            'fid': PerformanceMetric(
                name='First Input Delay',
                value=fid_estimate,
                unit='ms',
                status=fid_status,
                threshold_good=PERFORMANCE_THRESHOLDS['fid']['good'],
                threshold_poor=PERFORMANCE_THRESHOLDS['fid']['needs_improvement']
            ),
            'cls': PerformanceMetric(
                name='Cumulative Layout Shift',
                value=cls_estimate,
                unit='score',
                status=cls_status,
                threshold_good=PERFORMANCE_THRESHOLDS['cls']['good'],
                threshold_poor=PERFORMANCE_THRESHOLDS['cls']['needs_improvement']
            ),
            'ttfb': PerformanceMetric(
                name='Time to First Byte',
                value=ttfb_estimate,
                unit='ms',
                status=ttfb_status,
                threshold_good=PERFORMANCE_THRESHOLDS['ttfb']['good'],
                threshold_poor=PERFORMANCE_THRESHOLDS['ttfb']['needs_improvement']
            ),
            'fcp': PerformanceMetric(
                name='First Contentful Paint',
                value=fcp_estimate,
                unit='ms',
                status=fcp_status,
                threshold_good=PERFORMANCE_THRESHOLDS['fcp']['good'],
                threshold_poor=PERFORMANCE_THRESHOLDS['fcp']['needs_improvement']
            )
        }

    def _get_status(self, value: float, thresholds: Dict[str, float]) -> str:
        """Determine status based on threshold."""
        if value <= thresholds['good']:
            return 'good'
        elif value <= thresholds['needs_improvement']:
            return 'needs_improvement'
        else:
            return 'poor'

    async def _run_load_test(self, url: str) -> Dict[str, Any]:
        """Run simple load test to estimate capacity."""
        response_times = []
        errors = 0

        # Sequential baseline
        for _ in range(5):
            response = await self.http_client.get_async(url)
            if response.error:
                errors += 1
            else:
                response_times.append(response.elapsed_ms)
            await asyncio.sleep(0.1)

        baseline_avg = sum(response_times) / len(response_times) if response_times else 1000

        # Concurrent load test
        concurrent_times = []
        concurrent_errors = 0

        async def make_request():
            response = await self.http_client.get_async(url)
            return response

        tasks = [make_request() for _ in range(self.concurrent_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                concurrent_errors += 1
            elif result.error:
                concurrent_errors += 1
            else:
                concurrent_times.append(result.elapsed_ms)

        concurrent_avg = sum(concurrent_times) / len(concurrent_times) if concurrent_times else 5000

        return {
            'baseline_response_ms': baseline_avg,
            'concurrent_response_ms': concurrent_avg,
            'baseline_errors': errors,
            'concurrent_errors': concurrent_errors,
            'degradation_factor': concurrent_avg / baseline_avg if baseline_avg > 0 else 10,
            'concurrent_requests_tested': self.concurrent_requests
        }

    def _estimate_capacity(
        self,
        page_metric: PerformanceMetric,
        load_results: Dict[str, Any],
        resource_analysis: Dict[str, Any]
    ) -> CapacityEstimate:
        """Estimate maximum concurrent user capacity."""
        baseline_ms = load_results['baseline_response_ms']
        degradation = load_results['degradation_factor']
        concurrent_tested = load_results['concurrent_requests_tested']

        # Estimate based on degradation factor
        # If degradation is low, server can handle more
        if degradation < 1.5:
            capacity_multiplier = 100
            confidence = 'medium'
            bottleneck = 'No significant bottleneck detected'
        elif degradation < 2.0:
            capacity_multiplier = 50
            confidence = 'medium'
            bottleneck = 'Moderate server strain under concurrent load'
        elif degradation < 3.0:
            capacity_multiplier = 25
            confidence = 'low'
            bottleneck = 'Server response degrades significantly under load'
        else:
            capacity_multiplier = 10
            confidence = 'low'
            bottleneck = 'Server struggles with concurrent requests'

        max_users = concurrent_tested * capacity_multiplier
        recommended_users = int(max_users * 0.7)  # 70% of max for safety

        # Adjust based on resource analysis
        request_count = resource_analysis['resource_counts']['total_requests']
        if request_count > 50:
            max_users = int(max_users * 0.8)
            recommended_users = int(recommended_users * 0.8)
            bottleneck = f'{bottleneck}; High request count ({request_count}) per page load'

        return CapacityEstimate(
            max_concurrent_users=max_users,
            recommended_concurrent_users=recommended_users,
            bottleneck=bottleneck,
            confidence=confidence,
            methodology='Response time degradation under synthetic load',
            factors={
                'baseline_response_ms': baseline_ms,
                'degradation_factor': degradation,
                'requests_per_page': request_count,
                'concurrent_tested': concurrent_tested
            }
        )

    def _generate_performance_issues(
        self,
        web_vitals: Dict[str, PerformanceMetric],
        resource_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate issues from performance metrics."""
        issues = []

        # Check Core Web Vitals
        for key, metric in web_vitals.items():
            if metric.status == 'poor':
                issues.append({
                    'severity': SEVERITY_HIGH,
                    'category': 'performance',
                    'metric': metric.name,
                    'description': f'{metric.name} of {metric.value:.0f}{metric.unit} is poor (threshold: {metric.threshold_poor}{metric.unit})',
                    'fix_instruction': self._get_metric_fix(key, metric)
                })
            elif metric.status == 'needs_improvement':
                issues.append({
                    'severity': SEVERITY_MEDIUM,
                    'category': 'performance',
                    'metric': metric.name,
                    'description': f'{metric.name} of {metric.value:.0f}{metric.unit} needs improvement (target: {metric.threshold_good}{metric.unit})',
                    'fix_instruction': self._get_metric_fix(key, metric)
                })

        # Check resource counts
        resources = resource_analysis['resource_counts']
        if resources['total_requests'] > 50:
            issues.append({
                'severity': SEVERITY_MEDIUM,
                'category': 'performance',
                'metric': 'request_count',
                'description': f"Page makes {resources['total_requests']} HTTP requests (target: <50)",
                'fix_instruction': (
                    f"Reduce HTTP requests by: 1) Bundling JavaScript files into fewer files, "
                    f"2) Bundling CSS files, 3) Using CSS sprites for icons, "
                    f"4) Lazy loading below-fold images, 5) Removing unused resources."
                )
            })

        # Check compression
        if not resource_analysis['compression']['gzip_enabled']:
            issues.append({
                'severity': SEVERITY_HIGH,
                'category': 'performance',
                'metric': 'compression',
                'description': 'GZIP compression not enabled',
                'fix_instruction': (
                    f"Enable GZIP compression on the server. For Apache, add to .htaccess: "
                    f"'AddOutputFilterByType DEFLATE text/html text/css application/javascript'. "
                    f"For Nginx: 'gzip on; gzip_types text/html text/css application/javascript;'. "
                    f"This typically reduces transfer size by 70-90%."
                )
            })

        # Check caching
        if not resource_analysis['caching']['cache_control']:
            issues.append({
                'severity': SEVERITY_MEDIUM,
                'category': 'performance',
                'metric': 'caching',
                'description': 'Cache-Control header not set',
                'fix_instruction': (
                    f"Add Cache-Control headers for static resources. "
                    f"For Apache: 'Header set Cache-Control \"max-age=31536000, public\"' for static assets. "
                    f"For dynamic content: 'Cache-Control: no-cache, must-revalidate'. "
                    f"This allows browsers to cache resources and reduces repeat requests."
                )
            })

        return issues

    def _get_metric_fix(self, key: str, metric: PerformanceMetric) -> str:
        """Get fix instruction for a specific metric."""
        fixes = {
            'lcp': (
                f"To improve LCP ({metric.value:.0f}ms -> <{metric.threshold_good}ms): "
                f"1) Optimize the largest visible element (usually hero image or heading), "
                f"2) Preload critical resources: <link rel='preload' as='image' href='hero.jpg'>, "
                f"3) Use a CDN for faster delivery, "
                f"4) Reduce server response time (TTFB), "
                f"5) Remove render-blocking JavaScript."
            ),
            'fid': (
                f"To improve FID ({metric.value:.0f}ms -> <{metric.threshold_good}ms): "
                f"1) Break up long JavaScript tasks into smaller chunks, "
                f"2) Use web workers for heavy computation, "
                f"3) Defer non-critical JavaScript, "
                f"4) Remove unused JavaScript, "
                f"5) Minimize polyfills for modern browsers."
            ),
            'cls': (
                f"To improve CLS ({metric.value:.2f} -> <{metric.threshold_good}): "
                f"1) Add width and height attributes to all images, "
                f"2) Reserve space for ads and embeds, "
                f"3) Avoid inserting content above existing content, "
                f"4) Use transform animations instead of layout-triggering properties, "
                f"5) Preload fonts to avoid FOUT."
            ),
            'ttfb': (
                f"To improve TTFB ({metric.value:.0f}ms -> <{metric.threshold_good}ms): "
                f"1) Use a CDN, "
                f"2) Optimize server-side code, "
                f"3) Implement server-side caching, "
                f"4) Upgrade server hardware/hosting, "
                f"5) Use database query optimization."
            ),
            'fcp': (
                f"To improve FCP ({metric.value:.0f}ms -> <{metric.threshold_good}ms): "
                f"1) Eliminate render-blocking resources, "
                f"2) Inline critical CSS, "
                f"3) Preload key requests, "
                f"4) Reduce server response time, "
                f"5) Avoid multiple page redirects."
            )
        }
        return fixes.get(key, 'Optimize resources to improve this metric.')

    def _generate_recommendations(
        self,
        web_vitals: Dict[str, PerformanceMetric],
        resource_analysis: Dict[str, Any],
        capacity: CapacityEstimate
    ) -> List[Dict[str, Any]]:
        """Generate performance improvement recommendations."""
        recommendations = []

        # Add general recommendations based on analysis
        if capacity.max_concurrent_users < 5000:
            recommendations.append({
                'priority': 'high',
                'category': 'scaling',
                'title': 'Improve server capacity',
                'description': (
                    f"Current estimated capacity: {capacity.max_concurrent_users} users. "
                    f"Consider: implementing caching layer (Redis/Varnish), "
                    f"using a load balancer, scaling horizontally with multiple servers, "
                    f"or using serverless functions for API endpoints."
                )
            })

        if not resource_analysis['compression']['br_enabled']:
            recommendations.append({
                'priority': 'medium',
                'category': 'optimization',
                'title': 'Enable Brotli compression',
                'description': (
                    f"Brotli compression provides 15-25% better compression than gzip. "
                    f"Enable with: 'brotli on;' in Nginx or similar for other servers."
                )
            })

        return recommendations

    def _calculate_performance_score(
        self,
        web_vitals: Dict[str, PerformanceMetric],
        resource_analysis: Dict[str, Any]
    ) -> int:
        """Calculate overall performance score (0-100)."""
        score = 100

        # Deduct for poor vitals
        for metric in web_vitals.values():
            if metric.status == 'poor':
                score -= 20
            elif metric.status == 'needs_improvement':
                score -= 10

        # Deduct for resource issues
        resources = resource_analysis['resource_counts']
        if resources['total_requests'] > 100:
            score -= 15
        elif resources['total_requests'] > 50:
            score -= 5

        if not resource_analysis['compression']['gzip_enabled']:
            score -= 10

        return max(0, min(100, score))

    def _score_to_grade(self, score: int) -> str:
        """Convert score to letter grade."""
        if score >= 95:
            return 'A+'
        elif score >= 90:
            return 'A'
        elif score >= 85:
            return 'B+'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C+'
        elif score >= 60:
            return 'C'
        elif score >= 40:
            return 'D'
        else:
            return 'F'
