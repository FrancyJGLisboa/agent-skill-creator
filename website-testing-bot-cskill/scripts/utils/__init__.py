"""Utility modules for common functionality."""

from .http_client import HTTPClient, HTTPResponse
from .html_parser import HTMLParser, DOMElement
from .validators import URLValidator, validate_url, validate_config
from .constants import (
    SEVERITY_CRITICAL,
    SEVERITY_HIGH,
    SEVERITY_MEDIUM,
    SEVERITY_LOW,
    SEVERITY_INFO,
    READINESS_READY,
    READINESS_NEEDS_POLISHING,
    READINESS_UNDER_CONSTRUCTION,
    WCAG_GUIDELINES,
    SECURITY_HEADERS,
    DEFAULT_TIMEOUT,
    MAX_RETRIES
)

__all__ = [
    "HTTPClient",
    "HTTPResponse",
    "HTMLParser",
    "DOMElement",
    "URLValidator",
    "validate_url",
    "validate_config",
    "SEVERITY_CRITICAL",
    "SEVERITY_HIGH",
    "SEVERITY_MEDIUM",
    "SEVERITY_LOW",
    "SEVERITY_INFO",
    "READINESS_READY",
    "READINESS_NEEDS_POLISHING",
    "READINESS_UNDER_CONSTRUCTION",
    "WCAG_GUIDELINES",
    "SECURITY_HEADERS",
    "DEFAULT_TIMEOUT",
    "MAX_RETRIES"
]
