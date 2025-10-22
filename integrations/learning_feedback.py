#!/usr/bin/env python3
"""
Learning Feedback System - Subtle Progress Indicators

Provides subtle, non-intrusive feedback about agent learning progress.
Users see natural improvement without being overwhelmed with technical details.

All feedback is designed to feel like "smart magic" rather than "system notifications".
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from agentdb_bridge import get_agentdb_bridge
from validation_system import get_validation_system

logger = logging.getLogger(__name__)

@dataclass
class LearningMilestone:
    """Represents a learning milestone achieved by an agent"""
    milestone_type: str
    description: str
    impact: str  # How this benefits the user
    confidence: float
    timestamp: datetime

class LearningFeedbackSystem:
    """
    Provides subtle feedback about agent learning progress.

    All feedback is designed to feel natural and helpful,
    not technical or overwhelming.
    """

    def __init__(self):
        self.agentdb_bridge = get_agentdb_bridge()
        self.validation_system = get_validation_system()
        self.feedback_history = []
        self.user_patterns = {}
        self.milestones_achieved = []

    def analyze_agent_usage(self, agent_name: str, user_input: str, execution_time: float,
                          success: bool, result_quality: float) -> Optional[str]:
        """
        Analyze agent usage and provide subtle feedback if appropriate.
        Returns feedback message or None if no feedback needed.
        """
        try:
            # Track user patterns
            self._track_user_pattern(agent_name, user_input, execution_time)

            # Check for learning milestones
            milestone = self._check_for_milestone(agent_name, execution_time, success, result_quality)
            if milestone:
                self.milestones_achieved.append(milestone)
                return self._format_milestone_feedback(milestone)

            # Check for improvement indicators
            improvement = self._detect_improvement(agent_name, execution_time, result_quality)
            if improvement:
                return self._format_improvement_feedback(improvement)

            # Check for pattern recognition
            pattern_feedback = self._generate_pattern_feedback(agent_name, user_input)
            if pattern_feedback:
                return pattern_feedback

        except Exception as e:
            logger.debug(f"Failed to analyze agent usage: {e}")

        return None

    def _track_user_pattern(self, agent_name: str, user_input: str, execution_time: float):
        """Track user interaction patterns"""
        if agent_name not in self.user_patterns:
            self.user_patterns[agent_name] = {
                "queries": [],
                "times": [],
                "successes": [],
                "execution_times": [],
                "first_interaction": datetime.now()
            }

        pattern = self.user_patterns[agent_name]
        pattern["queries"].append(user_input)
        pattern["times"].append(execution_time)
        pattern["successes"].append(success)
        pattern["execution_times"].append(execution_time)

        # Keep only last 100 interactions
        for key in ["queries", "times", "successes", "execution_times"]:
            if len(pattern[key]) > 100:
                pattern[key] = pattern[key][-100:]

    def _check_for_milestone(self, agent_name: str, execution_time: float,
                           success: bool, result_quality: float) -> Optional[LearningMilestone]:
        """Check if user achieved a learning milestone"""
        pattern = self.user_patterns.get(agent_name, {})

        # Milestone 1: First successful execution
        if len(pattern.get("successes", [])) == 1 and success:
            return LearningMilestone(
                milestone_type="first_success",
                description="First successful execution",
                impact=f"Agent {agent_name} is now active and learning",
                confidence=0.9,
                timestamp=datetime.now()
            )

        # Milestone 2: Consistency (10 successful uses)
        success_count = len([s for s in pattern.get("successes", []) if s])
        if success_count == 10:
            return LearningMilestone(
                milestone_type="consistency",
                description="10 successful executions",
                impact=f"Agent {agent_name} is reliable and consistent",
                confidence=0.85,
                timestamp=datetime.now()
            )

        # Milestone 3: Speed improvement (20% faster than average)
        if len(pattern.get("execution_times", [])) >= 10:
            recent_times = pattern["execution_times"][-5:]
            early_times = pattern["execution_times"][:5]
            recent_avg = sum(recent_times) / len(recent_times)
            early_avg = sum(early_times) / len(early_times)

            if early_avg > 0 and recent_avg < early_avg * 0.8:  # 20% improvement
                return LearningMilestone(
                    milestone_type="speed_improvement",
                    description="20% faster execution speed",
                    impact=f"Agent {agent_name} has optimized and become faster",
                    confidence=0.8,
                    timestamp=datetime.now()
                )

        # Milestone 4: Long-term relationship (30 days)
        if pattern.get("first_interaction"):
            days_since_first = (datetime.now() - pattern["first_interaction"]).days
            if days_since_first >= 30:
                return LearningMilestone(
                    milestone_type="long_term_usage",
                    description="30 days of consistent usage",
                    impact=f"Agent {agent_name} has learned your preferences over time",
                    confidence=0.95,
                    timestamp=datetime.now()
                )

        return None

    def _detect_improvement(self, agent_name: str, execution_time: float,
                           result_quality: float) -> Optional[Dict[str, Any]]:
        """Detect if agent shows improvement signs"""
        pattern = self.user_patterns.get(agent_name, {})

        if len(pattern.get("execution_times", [])) < 5:
            return None

        recent_times = pattern["execution_times"][-3:]
        avg_recent = sum(recent_times) / len(recent_times)

        # Check speed improvement
        if avg_recent < 2.0:  # Fast execution
            return {
                "type": "speed",
                "message": f"⚡ Agent is responding quickly",
                "detail": f"Average time: {avg_recent:.1f}s"
            }

        # Check quality improvement
        if result_quality > 0.9:
            return {
                "type": "quality",
                "message": f"✨ High quality results detected",
                "detail": f"Result quality: {result_quality:.1%}"
            }

        return None

    def _generate_pattern_feedback(self, agent_name: str, user_input: str) -> Optional[str]:
        """Generate feedback based on user interaction patterns"""
        pattern = self.user_patterns.get(agent_name, {})

        if len(pattern.get("queries", [])) < 5:
            return None

        queries = pattern["queries"]

        # Check for time-based patterns
        hour = datetime.now().hour
        weekday = datetime.now().weekday()

        # Morning patterns
        if 6 <= hour <= 9 and len([q for q in queries[-5:] if "morning" in q.lower() or "today" in q.lower()]) >= 3:
            return f"🌅 Good morning! {agent_name} is ready for your daily analysis"

        # Friday patterns
        if weekday == 4 and len([q for q in queries[-10:] if "week" in q.lower() or "friday" in q.lower()]) >= 2:
            return f"📊 {agent_name} is preparing your weekly summary"

        # End of month patterns
        day_of_month = datetime.now().day
        if day_of_month >= 28 and len([q for q in queries[-10:] if "month" in q.lower()]) >= 2:
            return f"📈 {agent_name} is ready for your monthly reports"

        return None

    def _format_milestone_feedback(self, milestone: LearningMilestone) -> str:
        """Format milestone feedback to feel natural and encouraging"""
        messages = {
            "first_success": [
                f"🎉 Congratulations! {milestone.description}",
                f"🎉 Agent is now active and ready to assist you!"
            ],
            "consistency": [
                f"🎯 Excellent! {milestone.description}",
                f"🎯 Your agent has proven its reliability"
            ],
            "speed_improvement": [
                f"⚡ Amazing! {milestone.description}",
                f"⚡ Your agent is getting much faster with experience"
            ],
            "long_term_usage": [
                f"🌟 Fantastic! {milestone.description}",
                f"🌟 Your agent has learned your preferences and patterns"
            ]
        }

        message_set = messages.get(milestone.milestone_type, ["✨ Milestone achieved!"])
        return message_set[0] if message_set else f"✨ {milestone.description}"

    def _format_improvement_feedback(self, improvement: Dict[str, Any]) -> str:
        """Format improvement feedback to feel helpful but not overwhelming"""
        if improvement["type"] == "speed":
            return f"{improvement['message']} ({improvement['detail']})"
        elif improvement["type"] == "quality":
            return f"{improvement['message']} ({improvement['detail']})"
        else:
            return improvement["message"]

    def get_learning_summary(self, agent_name: str) -> Dict[str, Any]:
        """Get comprehensive learning summary for an agent"""
        try:
            # Get AgentDB learning summary
            agentdb_summary = self.agentdb_bridge.get_learning_summary(agent_name)

            # Get validation summary
            validation_summary = self.validation_system.get_validation_summary()

            # Get user patterns
            pattern = self.user_patterns.get(agent_name, {})

            # Calculate user statistics
            total_queries = len(pattern.get("queries", []))
            success_rate = (sum(pattern.get("successes", [])) / len(pattern.get("successes", [False])) * 100) if pattern.get("successes") else 0
            avg_time = sum(pattern.get("execution_times", [])) / len(pattern.get("execution_times", [1])) if pattern.get("execution_times") else 0

            # Get milestones
            milestones = [m for m in self.milestones_achieved if m.description and agent_name.lower() in m.description.lower()]

            return {
                "agent_name": agent_name,
                "agentdb_learning": agentdb_summary,
                "validation_performance": validation_summary,
                "user_statistics": {
                    "total_queries": total_queries,
                    "success_rate": success_rate,
                    "average_time": avg_time,
                    "first_interaction": pattern.get("first_interaction"),
                    "last_interaction": datetime.now() if pattern else None
                },
                "milestones_achieved": [
                    {
                        "type": m.milestone_type,
                        "description": m.description,
                        "impact": m.impact,
                        "confidence": m.confidence,
                        "timestamp": m.timestamp.isoformat()
                    }
                    for m in milestones
                ],
                "learning_progress": self._calculate_progress_score(agent_name)
            }

        except Exception as e:
            logger.error(f"Failed to get learning summary: {e}")
            return {"error": str(e)}

    def _calculate_progress_score(self, agent_name: str) -> float:
        """Calculate overall learning progress score"""
        score = 0.0

        # AgentDB contributions (40%)
        try:
            agentdb_summary = self.agentdb_bridge.get_learning_summary(agent_name)
            if agentdb_summary and agentdb_summary.get("total_sessions", 0) > 0:
                score += min(0.4, agentdb_summary["success_rate"] * 0.4)
        except:
            pass

        # User engagement (30%)
        pattern = self.user_patterns.get(agent_name, {})
        if pattern.get("successes"):
            engagement_rate = sum(pattern["successes"]) / len(pattern["successes"])
            score += min(0.3, engagement_rate * 0.3)

        # Milestones (20%)
        milestone_score = min(len(self.milestones_achieved) / 4, 0.2)  # Max 4 milestones
        score += milestone_score

        # Consistency (10%)
        if len(pattern.get("successes", [])) >= 10:
            consistency = sum(pattern["successes"][-10:]) / 10
            score += min(0.1, consistency * 0.1)

        return min(score, 1.0)

    def suggest_personalization(self, agent_name: str) -> Optional[str]:
        """
        Suggest personalization based on learned patterns.
        Returns subtle suggestion or None.
        """
        try:
            pattern = self.user_patterns.get(agent_name, {})

            # Check if user always asks for similar things
            recent_queries = pattern.get("queries", [])[-10:]

            # Look for common themes
            themes = {}
            for query in recent_queries:
                words = query.lower().split()
                for word in words:
                    if len(word) > 3:  # Ignore short words
                        themes[word] = themes.get(word, 0) + 1

            # Find most common theme
            if themes:
                top_theme = max(themes, key=themes.get)
                if themes[top_theme] >= 3:  # Appears in 3+ recent queries
                    return f"🎯 I notice you often ask about {top_theme}. Consider creating a specialized agent for this."

        except Exception as e:
            logger.debug(f"Failed to suggest personalization: {e}")

        return None

# Global feedback system (invisible to users)
_learning_feedback_system = None

def get_learning_feedback_system() -> LearningFeedbackSystem:
    """Get the global learning feedback system instance"""
    global _learning_feedback_system
    if _learning_feedback_system is None:
        _learning_feedback_system = LearningFeedbackSystem()
    return _learning_feedback_system

def analyze_agent_execution(agent_name: str, user_input: str, execution_time: float,
                             success: bool, result_quality: float) -> Optional[str]:
    """
    Analyze agent execution and provide learning feedback.
    Called automatically after each agent execution.
    """
    system = get_learning_feedback_system()
    return system.analyze_agent_usage(agent_name, user_input, execution_time, success, result_quality)

def get_agent_learning_summary(agent_name: str) -> Dict[str, Any]:
    """
    Get comprehensive learning summary for an agent.
    Used internally for progress tracking.
    """
    system = get_learning_feedback_system()
    return system.get_learning_summary(agent_name)

def suggest_agent_personalization(agent_name: str) -> Optional[str]:
    """
    Suggest personalization based on learned patterns.
    Used when appropriate to enhance user experience.
    """
    system = get_learning_feedback_system()
    return system.suggest_personalization(agent_name)

# Auto-initialize when module is imported
get_learning_feedback_system()