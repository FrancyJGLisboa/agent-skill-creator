"""
Commercial readiness analyzer for capacity and scaling assessment.

Evaluates production readiness and estimates commercial capacity.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from ..utils.constants import (
    COMMERCIAL_GRADES,
    COMMERCIAL_GRADE_DESCRIPTIONS,
    SEVERITY_CRITICAL,
    SEVERITY_HIGH,
    SEVERITY_MEDIUM
)


@dataclass
class ScalingFactor:
    """A factor affecting scaling capacity."""
    name: str
    impact: str  # positive, negative, neutral
    weight: float
    description: str
    recommendation: str


@dataclass
class CommercialReport:
    """Complete commercial readiness report."""
    url: str
    grade: str
    grade_description: str
    score: int
    max_concurrent_users: int
    recommended_max_users: int
    bottlenecks: List[str]
    scaling_factors: List[ScalingFactor]
    infrastructure_recommendations: List[Dict[str, Any]]
    cost_estimates: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    issues: List[Dict[str, Any]]


class CommercialAnalyzer:
    """
    Analyzes commercial readiness and scaling capacity.

    Evaluates performance, reliability, and infrastructure
    to estimate production deployment readiness.
    """

    def __init__(self):
        """Initialize commercial analyzer."""
        pass

    def analyze_commercial_readiness(
        self,
        url: str,
        performance_data: Dict[str, Any],
        security_data: Dict[str, Any],
        accessibility_data: Dict[str, Any],
        test_results: Dict[str, Any]
    ) -> CommercialReport:
        """
        Analyze commercial readiness.

        Args:
            url: URL being analyzed
            performance_data: Performance test results
            security_data: Security test results
            accessibility_data: Accessibility test results
            test_results: Overall test results

        Returns:
            CommercialReport with grade and analysis
        """
        issues = []

        # Calculate component scores
        performance_score = self._calculate_performance_score(performance_data)
        security_score = self._calculate_security_score(security_data)
        accessibility_score = self._calculate_accessibility_score(accessibility_data)
        functionality_score = self._calculate_functionality_score(test_results)

        # Calculate weighted total
        weights = {
            'performance': 0.30,
            'security': 0.25,
            'functionality': 0.25,
            'accessibility': 0.10,
            'seo': 0.05,
            'mobile': 0.05
        }

        total_score = (
            performance_score * weights['performance'] +
            security_score * weights['security'] +
            functionality_score * weights['functionality'] +
            accessibility_score * weights['accessibility'] +
            80 * weights['seo'] +  # Default SEO score
            80 * weights['mobile']  # Default mobile score
        )

        score = int(total_score)

        # Determine grade
        grade = self._score_to_grade(score)
        grade_description = COMMERCIAL_GRADE_DESCRIPTIONS.get(grade, "")

        # Estimate capacity
        capacity_estimate = self._estimate_capacity(performance_data, score)
        max_users = capacity_estimate['max_users']
        recommended_max = capacity_estimate['recommended_max']

        # Identify bottlenecks
        bottlenecks = self._identify_bottlenecks(
            performance_data, security_data, test_results
        )

        # Analyze scaling factors
        scaling_factors = self._analyze_scaling_factors(
            performance_data, test_results
        )

        # Generate infrastructure recommendations
        infrastructure_recs = self._generate_infrastructure_recommendations(
            max_users, bottlenecks, performance_data
        )

        # Estimate costs
        cost_estimates = self._estimate_costs(max_users, infrastructure_recs)

        # Assess risks
        risk_assessment = self._assess_risks(
            security_data, performance_data, functionality_score
        )

        # Generate issues
        issues.extend(self._generate_commercial_issues(
            score, grade, bottlenecks, risk_assessment
        ))

        return CommercialReport(
            url=url,
            grade=grade,
            grade_description=grade_description,
            score=score,
            max_concurrent_users=max_users,
            recommended_max_users=recommended_max,
            bottlenecks=bottlenecks,
            scaling_factors=scaling_factors,
            infrastructure_recommendations=infrastructure_recs,
            cost_estimates=cost_estimates,
            risk_assessment=risk_assessment,
            issues=issues
        )

    def _calculate_performance_score(self, data: Dict[str, Any]) -> int:
        """Calculate performance component score."""
        if not data:
            return 50

        score = 100

        # Check Core Web Vitals
        vitals = data.get('core_web_vitals', {})
        for vital_name, vital_data in vitals.items():
            if hasattr(vital_data, 'status'):
                if vital_data.status == 'poor':
                    score -= 20
                elif vital_data.status == 'needs_improvement':
                    score -= 10

        # Check capacity estimate
        capacity = data.get('capacity_estimate', {})
        if hasattr(capacity, 'max_concurrent_users'):
            max_users = capacity.max_concurrent_users
            if max_users < 1000:
                score -= 20
            elif max_users < 5000:
                score -= 10

        return max(0, min(100, score))

    def _calculate_security_score(self, data: Dict[str, Any]) -> int:
        """Calculate security component score."""
        if not data:
            return 50

        score = 100

        # Check SSL
        ssl_info = data.get('ssl_info', {})
        if hasattr(ssl_info, 'valid') and not ssl_info.valid:
            score -= 30

        # Count issues by severity
        issues = data.get('all_issues', [])
        for issue in issues:
            if hasattr(issue, 'severity'):
                if issue.severity == SEVERITY_CRITICAL:
                    score -= 20
                elif issue.severity == SEVERITY_HIGH:
                    score -= 10
                elif issue.severity == SEVERITY_MEDIUM:
                    score -= 5

        return max(0, min(100, score))

    def _calculate_accessibility_score(self, data: Dict[str, Any]) -> int:
        """Calculate accessibility component score."""
        if not data:
            return 50

        if hasattr(data, 'score'):
            return data.score
        return data.get('score', 50)

    def _calculate_functionality_score(self, data: Dict[str, Any]) -> int:
        """Calculate functionality component score."""
        if not data:
            return 70

        score = 100

        # Count broken links
        broken_links = data.get('broken_links', [])
        if len(broken_links) > 10:
            score -= 20
        elif len(broken_links) > 5:
            score -= 10
        elif len(broken_links) > 0:
            score -= 5

        # Count form issues
        form_issues = [i for i in data.get('issues', [])
                      if 'form' in str(i).lower()]
        score -= len(form_issues) * 5

        return max(0, min(100, score))

    def _score_to_grade(self, score: int) -> str:
        """Convert score to letter grade."""
        for grade, config in sorted(COMMERCIAL_GRADES.items(),
                                    key=lambda x: x[1]['min_score'],
                                    reverse=True):
            if score >= config['min_score']:
                return grade
        return 'F'

    def _estimate_capacity(
        self,
        performance_data: Dict[str, Any],
        score: int
    ) -> Dict[str, int]:
        """Estimate user capacity based on performance data."""
        base_capacity = 1000

        # Get from performance data if available
        if performance_data:
            capacity = performance_data.get('capacity_estimate', {})
            if hasattr(capacity, 'max_concurrent_users'):
                base_capacity = capacity.max_concurrent_users

        # Adjust based on score
        score_multiplier = score / 100
        adjusted_capacity = int(base_capacity * score_multiplier)

        # Safety margin for recommended
        recommended = int(adjusted_capacity * 0.7)

        return {
            'max_users': adjusted_capacity,
            'recommended_max': recommended
        }

    def _identify_bottlenecks(
        self,
        performance_data: Dict[str, Any],
        security_data: Dict[str, Any],
        test_results: Dict[str, Any]
    ) -> List[str]:
        """Identify system bottlenecks."""
        bottlenecks = []

        # Performance bottlenecks
        if performance_data:
            vitals = performance_data.get('core_web_vitals', {})
            for vital_name, vital_data in vitals.items():
                if hasattr(vital_data, 'status') and vital_data.status == 'poor':
                    bottlenecks.append(f"Performance: {vital_data.name}")

            resources = performance_data.get('resource_analysis', {})
            if resources.get('resource_counts', {}).get('total_requests', 0) > 100:
                bottlenecks.append("Too many HTTP requests per page")

        # Security bottlenecks
        if security_data:
            ssl_info = security_data.get('ssl_info', {})
            if hasattr(ssl_info, 'valid') and not ssl_info.valid:
                bottlenecks.append("SSL/HTTPS not properly configured")

        # Functionality bottlenecks
        if test_results:
            broken = test_results.get('broken_links', [])
            if len(broken) > 5:
                bottlenecks.append(f"{len(broken)} broken links")

        if not bottlenecks:
            bottlenecks.append("No significant bottlenecks detected")

        return bottlenecks

    def _analyze_scaling_factors(
        self,
        performance_data: Dict[str, Any],
        test_results: Dict[str, Any]
    ) -> List[ScalingFactor]:
        """Analyze factors affecting scaling."""
        factors = []

        # Static vs dynamic content
        factors.append(ScalingFactor(
            name="Content Type",
            impact="positive" if not test_results.get('has_database_forms', False) else "neutral",
            weight=0.2,
            description="Static content scales better than dynamic",
            recommendation="Use CDN for static assets, cache dynamic content"
        ))

        # Resource optimization
        if performance_data:
            resources = performance_data.get('resource_analysis', {})
            compression = resources.get('compression', {})

            if compression.get('gzip_enabled'):
                factors.append(ScalingFactor(
                    name="Compression",
                    impact="positive",
                    weight=0.15,
                    description="GZIP compression enabled",
                    recommendation="Consider adding Brotli compression for better compression"
                ))
            else:
                factors.append(ScalingFactor(
                    name="Compression",
                    impact="negative",
                    weight=0.15,
                    description="No compression detected",
                    recommendation="Enable GZIP compression to reduce bandwidth"
                ))

            caching = resources.get('caching', {})
            if caching.get('cache_control'):
                factors.append(ScalingFactor(
                    name="Caching",
                    impact="positive",
                    weight=0.2,
                    description="Cache headers configured",
                    recommendation="Ensure long cache times for static assets"
                ))
            else:
                factors.append(ScalingFactor(
                    name="Caching",
                    impact="negative",
                    weight=0.2,
                    description="No cache headers detected",
                    recommendation="Add Cache-Control headers for all resources"
                ))

        # Third-party dependencies
        factors.append(ScalingFactor(
            name="External Dependencies",
            impact="neutral",
            weight=0.1,
            description="Third-party services affect reliability",
            recommendation="Minimize third-party dependencies or use fallbacks"
        ))

        return factors

    def _generate_infrastructure_recommendations(
        self,
        max_users: int,
        bottlenecks: List[str],
        performance_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate infrastructure recommendations."""
        recommendations = []

        # CDN recommendation
        recommendations.append({
            'priority': 'high',
            'category': 'cdn',
            'title': 'Use Content Delivery Network',
            'description': (
                f"For {max_users} users, deploy behind a CDN like Cloudflare, "
                f"AWS CloudFront, or Fastly. CDN reduces server load by 60-80% "
                f"for static content and improves global performance."
            ),
            'estimated_impact': '+50% capacity, -40% latency'
        })

        # Caching layer
        if max_users > 5000:
            recommendations.append({
                'priority': 'high',
                'category': 'caching',
                'title': 'Implement caching layer',
                'description': (
                    f"Add Redis or Memcached for application caching. "
                    f"Implement page caching with Varnish or Nginx FastCGI cache. "
                    f"Cache database queries to reduce load."
                ),
                'estimated_impact': '+100% capacity, -60% database load'
            })

        # Load balancing
        if max_users > 10000:
            recommendations.append({
                'priority': 'high',
                'category': 'scaling',
                'title': 'Configure load balancing',
                'description': (
                    f"Deploy multiple server instances behind a load balancer. "
                    f"Use AWS ALB, Google Cloud Load Balancer, or HAProxy. "
                    f"Enable health checks and automatic failover."
                ),
                'estimated_impact': '+200% capacity, improved reliability'
            })

        # Database optimization
        if any('database' in b.lower() for b in bottlenecks):
            recommendations.append({
                'priority': 'high',
                'category': 'database',
                'title': 'Optimize database',
                'description': (
                    f"Add read replicas for database scaling. "
                    f"Implement connection pooling. "
                    f"Review and optimize slow queries. "
                    f"Consider managed database service for automatic scaling."
                ),
                'estimated_impact': '+150% database capacity'
            })

        # Auto-scaling
        if max_users > 25000:
            recommendations.append({
                'priority': 'medium',
                'category': 'scaling',
                'title': 'Implement auto-scaling',
                'description': (
                    f"Configure auto-scaling groups to handle traffic spikes. "
                    f"Set scaling policies based on CPU, memory, and request rate. "
                    f"Test scaling behavior under load."
                ),
                'estimated_impact': 'Handles 10x traffic spikes automatically'
            })

        return recommendations

    def _estimate_costs(
        self,
        max_users: int,
        infrastructure_recs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Estimate infrastructure costs."""
        # Base monthly costs (rough estimates)
        base_hosting = 50 if max_users < 5000 else 200 if max_users < 25000 else 500
        cdn_cost = 20 if max_users < 10000 else 100 if max_users < 50000 else 300
        database_cost = 50 if max_users < 10000 else 200 if max_users < 50000 else 500

        total_monthly = base_hosting + cdn_cost + database_cost

        return {
            'estimated_monthly_usd': total_monthly,
            'breakdown': {
                'hosting': base_hosting,
                'cdn': cdn_cost,
                'database': database_cost
            },
            'cost_per_1000_users': total_monthly / (max_users / 1000) if max_users > 0 else 0,
            'note': (
                f"Estimates based on {max_users} concurrent users. "
                f"Actual costs vary by provider, region, and usage patterns."
            )
        }

    def _assess_risks(
        self,
        security_data: Dict[str, Any],
        performance_data: Dict[str, Any],
        functionality_score: int
    ) -> Dict[str, Any]:
        """Assess deployment risks."""
        risks = {
            'high': [],
            'medium': [],
            'low': []
        }

        # Security risks
        if security_data:
            ssl_info = security_data.get('ssl_info', {})
            if hasattr(ssl_info, 'valid') and not ssl_info.valid:
                risks['high'].append({
                    'category': 'security',
                    'description': 'Invalid or missing SSL certificate',
                    'mitigation': 'Install valid SSL certificate before launch'
                })

            critical_issues = [i for i in security_data.get('all_issues', [])
                             if hasattr(i, 'severity') and i.severity == SEVERITY_CRITICAL]
            if critical_issues:
                risks['high'].append({
                    'category': 'security',
                    'description': f'{len(critical_issues)} critical security issues',
                    'mitigation': 'Address all critical security issues'
                })

        # Performance risks
        if performance_data:
            vitals = performance_data.get('core_web_vitals', {})
            poor_vitals = [v for v in vitals.values()
                         if hasattr(v, 'status') and v.status == 'poor']
            if poor_vitals:
                risks['medium'].append({
                    'category': 'performance',
                    'description': f'{len(poor_vitals)} Core Web Vitals in poor range',
                    'mitigation': 'Optimize performance before high traffic'
                })

        # Functionality risks
        if functionality_score < 70:
            risks['medium'].append({
                'category': 'functionality',
                'description': 'Below-average functionality score',
                'mitigation': 'Fix broken elements and form issues'
            })

        overall_risk = 'high' if risks['high'] else 'medium' if risks['medium'] else 'low'

        return {
            'overall_risk_level': overall_risk,
            'risks': risks,
            'risk_count': sum(len(r) for r in risks.values())
        }

    def _generate_commercial_issues(
        self,
        score: int,
        grade: str,
        bottlenecks: List[str],
        risk_assessment: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate commercial readiness issues."""
        issues = []

        if grade in ['D', 'F']:
            issues.append({
                'severity': SEVERITY_CRITICAL,
                'category': 'commercial_readiness',
                'description': f'Commercial readiness grade {grade} is not acceptable for production',
                'fix_instruction': (
                    f"Site is not ready for commercial launch. "
                    f"Address all critical and high-severity issues first. "
                    f"Current bottlenecks: {', '.join(bottlenecks)}. "
                    f"Target grade B or higher before launch."
                )
            })
        elif grade in ['C', 'C+']:
            issues.append({
                'severity': SEVERITY_HIGH,
                'category': 'commercial_readiness',
                'description': f'Commercial readiness grade {grade} indicates significant issues',
                'fix_instruction': (
                    f"Site can handle limited commercial use but has concerns. "
                    f"Improve performance and fix identified issues. "
                    f"Consider soft launch with limited users first."
                )
            })

        for risk in risk_assessment.get('risks', {}).get('high', []):
            issues.append({
                'severity': SEVERITY_CRITICAL,
                'category': 'risk',
                'description': f"High risk: {risk['description']}",
                'fix_instruction': risk['mitigation']
            })

        return issues
