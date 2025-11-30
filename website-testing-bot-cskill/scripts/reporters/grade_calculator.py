"""
Grade calculator for computing overall grades and scores.

Calculates weighted grades from multiple test categories.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from ..utils.constants import (
    COMMERCIAL_GRADES,
    COMMERCIAL_GRADE_DESCRIPTIONS,
    UNIQUENESS_THRESHOLDS
)


@dataclass
class GradeResult:
    """Result of grade calculation."""
    grade: str
    score: int
    description: str
    breakdown: Dict[str, int]
    strengths: List[str]
    weaknesses: List[str]


class GradeCalculator:
    """
    Calculates grades and scores for website testing.

    Combines multiple category scores into overall grades.
    """

    # Weight configuration for different scoring contexts
    COMMERCIAL_WEIGHTS = {
        'performance': 0.25,
        'security': 0.25,
        'functionality': 0.20,
        'accessibility': 0.10,
        'mobile': 0.10,
        'seo': 0.10
    }

    OVERALL_WEIGHTS = {
        'commercial': 0.40,
        'uniqueness': 0.25,
        'functionality': 0.20,
        'accessibility': 0.15
    }

    def __init__(self):
        """Initialize grade calculator."""
        pass

    def calculate_commercial_grade(
        self,
        performance_score: int,
        security_score: int,
        functionality_score: int,
        accessibility_score: int,
        mobile_score: int = 70,
        seo_score: int = 70
    ) -> GradeResult:
        """
        Calculate commercial readiness grade.

        Args:
            performance_score: Performance test score (0-100)
            security_score: Security test score (0-100)
            functionality_score: Functionality test score (0-100)
            accessibility_score: Accessibility test score (0-100)
            mobile_score: Mobile responsiveness score (0-100)
            seo_score: SEO score (0-100)

        Returns:
            GradeResult with commercial grade
        """
        breakdown = {
            'performance': performance_score,
            'security': security_score,
            'functionality': functionality_score,
            'accessibility': accessibility_score,
            'mobile': mobile_score,
            'seo': seo_score
        }

        # Calculate weighted score
        total_score = sum(
            breakdown[key] * self.COMMERCIAL_WEIGHTS[key]
            for key in breakdown
        )
        score = int(total_score)

        # Determine grade
        grade = self._score_to_commercial_grade(score)
        description = COMMERCIAL_GRADE_DESCRIPTIONS.get(grade, "")

        # Identify strengths and weaknesses
        strengths = [k for k, v in breakdown.items() if v >= 80]
        weaknesses = [k for k, v in breakdown.items() if v < 60]

        return GradeResult(
            grade=grade,
            score=score,
            description=description,
            breakdown=breakdown,
            strengths=strengths,
            weaknesses=weaknesses
        )

    def calculate_uniqueness_score(
        self,
        visual_design: int,
        layout_structure: int,
        functionality: int,
        content_presentation: int,
        interactive_elements: int,
        brand_identity: int
    ) -> GradeResult:
        """
        Calculate uniqueness score.

        Args:
            visual_design: Visual design originality (0-100)
            layout_structure: Layout structure uniqueness (0-100)
            functionality: Functionality innovation (0-100)
            content_presentation: Content presentation style (0-100)
            interactive_elements: Interactive element creativity (0-100)
            brand_identity: Brand identity integration (0-100)

        Returns:
            GradeResult with uniqueness score
        """
        breakdown = {
            'visual_design': visual_design,
            'layout_structure': layout_structure,
            'functionality': functionality,
            'content_presentation': content_presentation,
            'interactive_elements': interactive_elements,
            'brand_identity': brand_identity
        }

        weights = {
            'visual_design': 0.25,
            'layout_structure': 0.20,
            'functionality': 0.20,
            'content_presentation': 0.15,
            'interactive_elements': 0.10,
            'brand_identity': 0.10
        }

        # Calculate weighted score
        total_score = sum(
            breakdown[key] * weights[key]
            for key in breakdown
        )
        score = int(total_score)

        # Determine rating
        rating, description = self._score_to_uniqueness_rating(score)

        # Identify strengths and weaknesses
        strengths = [k for k, v in breakdown.items() if v >= 70]
        weaknesses = [k for k, v in breakdown.items() if v < 50]

        return GradeResult(
            grade=rating,
            score=score,
            description=description,
            breakdown=breakdown,
            strengths=strengths,
            weaknesses=weaknesses
        )

    def calculate_overall_score(
        self,
        commercial_score: int,
        uniqueness_score: int,
        functionality_score: int,
        accessibility_score: int
    ) -> int:
        """
        Calculate overall website quality score.

        Args:
            commercial_score: Commercial readiness score (0-100)
            uniqueness_score: Uniqueness score (0-100)
            functionality_score: Functionality score (0-100)
            accessibility_score: Accessibility score (0-100)

        Returns:
            Overall score (0-100)
        """
        scores = {
            'commercial': commercial_score,
            'uniqueness': uniqueness_score,
            'functionality': functionality_score,
            'accessibility': accessibility_score
        }

        total = sum(
            scores[key] * self.OVERALL_WEIGHTS[key]
            for key in scores
        )

        return int(total)

    def calculate_test_pass_rate(
        self,
        tests_run: int,
        tests_passed: int
    ) -> Dict[str, Any]:
        """
        Calculate test pass rate and status.

        Args:
            tests_run: Total tests executed
            tests_passed: Number of tests passed

        Returns:
            Dictionary with pass rate and status
        """
        if tests_run == 0:
            return {
                'pass_rate': 0,
                'status': 'no_tests',
                'description': 'No tests executed'
            }

        pass_rate = (tests_passed / tests_run) * 100

        if pass_rate >= 95:
            status = 'excellent'
            description = 'Excellent test results'
        elif pass_rate >= 85:
            status = 'good'
            description = 'Good test results with minor issues'
        elif pass_rate >= 70:
            status = 'acceptable'
            description = 'Acceptable but needs improvement'
        elif pass_rate >= 50:
            status = 'poor'
            description = 'Poor results, significant issues'
        else:
            status = 'critical'
            description = 'Critical issues, major work needed'

        return {
            'pass_rate': round(pass_rate, 1),
            'tests_run': tests_run,
            'tests_passed': tests_passed,
            'tests_failed': tests_run - tests_passed,
            'status': status,
            'description': description
        }

    def _score_to_commercial_grade(self, score: int) -> str:
        """Convert score to commercial grade."""
        for grade, config in sorted(COMMERCIAL_GRADES.items(),
                                    key=lambda x: x[1]['min_score'],
                                    reverse=True):
            if score >= config['min_score']:
                return grade
        return 'F'

    def _score_to_uniqueness_rating(self, score: int) -> tuple:
        """Convert score to uniqueness rating."""
        for key, threshold in UNIQUENESS_THRESHOLDS.items():
            if threshold['min'] <= score <= threshold['max']:
                descriptions = {
                    'highly_original': "Custom design, unique functionality, strong brand identity",
                    'distinctive': "Customized template with significant modifications",
                    'moderate': "Recognizable template base with some customization",
                    'generic': "Minimal template customization, common patterns",
                    'template_clone': "Nearly unmodified template, no unique identity"
                }
                return threshold['label'], descriptions.get(key, '')
        return "Unknown", ""

    def estimate_capacity_from_grade(self, grade: str) -> Dict[str, int]:
        """
        Estimate user capacity from commercial grade.

        Args:
            grade: Commercial grade (A+ to F)

        Returns:
            Dictionary with capacity estimates
        """
        config = COMMERCIAL_GRADES.get(grade, COMMERCIAL_GRADES['F'])

        return {
            'max_concurrent_users': config['max_users'],
            'recommended_concurrent_users': int(config['max_users'] * 0.7),
            'max_response_time_ms': config['max_response_ms']
        }

    def get_grade_requirements(self, target_grade: str) -> Dict[str, Any]:
        """
        Get requirements to achieve a target grade.

        Args:
            target_grade: Target grade to achieve

        Returns:
            Dictionary with requirements
        """
        config = COMMERCIAL_GRADES.get(target_grade)
        if not config:
            return {}

        return {
            'minimum_score': config['min_score'],
            'description': COMMERCIAL_GRADE_DESCRIPTIONS.get(target_grade, ''),
            'requirements': [
                f"Overall score must be {config['min_score']}% or higher",
                f"Response time must be under {config['max_response_ms']}ms",
                "No critical security issues",
                "All core functionality working",
                "Accessibility score 80%+ for Grade B and above"
            ],
            'typical_capacity': f"Supports approximately {config['max_users']:,} concurrent users"
        }

    def compare_grades(
        self,
        current_grade: str,
        target_grade: str
    ) -> Dict[str, Any]:
        """
        Compare current grade to target and identify gap.

        Args:
            current_grade: Current grade
            target_grade: Target grade

        Returns:
            Dictionary with comparison and improvement needed
        """
        current_config = COMMERCIAL_GRADES.get(current_grade, COMMERCIAL_GRADES['F'])
        target_config = COMMERCIAL_GRADES.get(target_grade, COMMERCIAL_GRADES['A'])

        score_gap = target_config['min_score'] - current_config['min_score']

        if score_gap <= 0:
            return {
                'status': 'achieved',
                'message': f"Current grade {current_grade} meets or exceeds target {target_grade}"
            }

        return {
            'status': 'improvement_needed',
            'current_grade': current_grade,
            'target_grade': target_grade,
            'score_gap': score_gap,
            'capacity_gap': target_config['max_users'] - current_config['max_users'],
            'improvements_needed': self._get_improvement_suggestions(score_gap),
            'estimated_effort': self._estimate_improvement_effort(score_gap)
        }

    def _get_improvement_suggestions(self, score_gap: int) -> List[str]:
        """Get suggestions for improving score."""
        suggestions = []

        if score_gap >= 30:
            suggestions.extend([
                "Major performance optimization required",
                "Significant security hardening needed",
                "Address all critical and high-severity issues"
            ])
        elif score_gap >= 15:
            suggestions.extend([
                "Optimize Core Web Vitals",
                "Implement security best practices",
                "Fix high-priority accessibility issues"
            ])
        else:
            suggestions.extend([
                "Fine-tune performance",
                "Address remaining medium-priority issues",
                "Polish user experience"
            ])

        return suggestions

    def _estimate_improvement_effort(self, score_gap: int) -> str:
        """Estimate effort to close score gap."""
        if score_gap >= 30:
            return "2-4 weeks of focused development"
        elif score_gap >= 15:
            return "1-2 weeks of development"
        elif score_gap >= 5:
            return "3-5 days of development"
        else:
            return "1-2 days of polish"
