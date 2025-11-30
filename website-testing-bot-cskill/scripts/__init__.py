"""
Website Testing Bot - Ultimate Commercial Readiness Assessment Tool

A comprehensive website testing system that performs exhaustive analysis
of every site element, providing detailed reports suitable for agent handoff.
"""

__version__ = "1.0.0"
__author__ = "Agent Skill Creator"

from .main import WebsiteTestingBot, run_website_test, TestConfig, WebsiteTestReport

__all__ = [
    "WebsiteTestingBot",
    "run_website_test",
    "TestConfig",
    "WebsiteTestReport"
]
