"""
Input validation utilities for the Website Testing Bot.

Provides URL validation, configuration validation, and input sanitization.
"""

import re
from typing import Optional, Tuple, List, Any, Dict
from urllib.parse import urlparse, urljoin
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a validation check."""
    is_valid: bool
    normalized_value: Any
    errors: List[str]
    warnings: List[str]


class URLValidator:
    """Validates and normalizes URLs for testing."""

    # Valid URL schemes for web testing
    VALID_SCHEMES = {'http', 'https'}

    # Patterns that indicate potentially dangerous or invalid URLs
    DANGEROUS_PATTERNS = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'file:',
    ]

    # Pattern for valid domain names
    DOMAIN_PATTERN = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*'
        r'[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
    )

    # Pattern for valid IP addresses
    IP_PATTERN = re.compile(
        r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    )

    @classmethod
    def validate(cls, url: str) -> ValidationResult:
        """
        Validate a URL for website testing.

        Args:
            url: The URL string to validate

        Returns:
            ValidationResult with validation status and any errors
        """
        errors = []
        warnings = []
        normalized_url = url.strip()

        # Check for empty URL
        if not normalized_url:
            return ValidationResult(
                is_valid=False,
                normalized_value=None,
                errors=["URL cannot be empty"],
                warnings=[]
            )

        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, normalized_url, re.IGNORECASE):
                return ValidationResult(
                    is_valid=False,
                    normalized_value=None,
                    errors=[f"URL contains dangerous pattern: {pattern}"],
                    warnings=[]
                )

        # Add scheme if missing
        if not normalized_url.startswith(('http://', 'https://')):
            normalized_url = 'https://' + normalized_url
            warnings.append("Added 'https://' scheme to URL")

        # Parse the URL
        try:
            parsed = urlparse(normalized_url)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                normalized_value=None,
                errors=[f"Failed to parse URL: {str(e)}"],
                warnings=[]
            )

        # Validate scheme
        if parsed.scheme.lower() not in cls.VALID_SCHEMES:
            errors.append(f"Invalid URL scheme: {parsed.scheme}. Must be http or https")

        # Validate domain/host
        if not parsed.netloc:
            errors.append("URL must have a domain/host")
        else:
            host = parsed.netloc.split(':')[0]  # Remove port if present

            # Check if it's a valid domain or IP
            if not cls.DOMAIN_PATTERN.match(host) and not cls.IP_PATTERN.match(host):
                if host != 'localhost':
                    errors.append(f"Invalid domain format: {host}")

            # Warn about localhost
            if host == 'localhost' or host.startswith('127.') or host.startswith('192.168.'):
                warnings.append("URL points to local/private network address")

        # Normalize the URL
        if not errors:
            # Ensure trailing slash for root URLs
            if not parsed.path:
                normalized_url = normalized_url + '/'

            # Remove duplicate slashes in path
            if parsed.path:
                clean_path = re.sub(r'/+', '/', parsed.path)
                normalized_url = f"{parsed.scheme}://{parsed.netloc}{clean_path}"
                if parsed.query:
                    normalized_url += f"?{parsed.query}"
                if parsed.fragment:
                    normalized_url += f"#{parsed.fragment}"

        return ValidationResult(
            is_valid=len(errors) == 0,
            normalized_value=normalized_url if not errors else None,
            errors=errors,
            warnings=warnings
        )

    @classmethod
    def is_same_domain(cls, url1: str, url2: str) -> bool:
        """Check if two URLs belong to the same domain."""
        try:
            domain1 = urlparse(url1).netloc.lower()
            domain2 = urlparse(url2).netloc.lower()
            return domain1 == domain2
        except Exception:
            return False

    @classmethod
    def resolve_relative(cls, base_url: str, relative_url: str) -> str:
        """Resolve a relative URL against a base URL."""
        return urljoin(base_url, relative_url)

    @classmethod
    def get_domain(cls, url: str) -> Optional[str]:
        """Extract the domain from a URL."""
        try:
            return urlparse(url).netloc.lower()
        except Exception:
            return None

    @classmethod
    def is_internal_link(cls, base_url: str, link_url: str) -> bool:
        """Check if a link is internal to the base URL's domain."""
        base_domain = cls.get_domain(base_url)
        link_domain = cls.get_domain(link_url)

        if not link_domain:
            return True  # Relative URLs are internal

        return base_domain == link_domain


def validate_url(url: str) -> Tuple[bool, str, List[str]]:
    """
    Simple URL validation function.

    Args:
        url: URL to validate

    Returns:
        Tuple of (is_valid, normalized_url, errors)
    """
    result = URLValidator.validate(url)
    return (result.is_valid, result.normalized_value or url, result.errors)


def validate_config(config: Dict[str, Any]) -> ValidationResult:
    """
    Validate a test configuration dictionary.

    Args:
        config: Configuration dictionary to validate

    Returns:
        ValidationResult with validation status and any errors
    """
    errors = []
    warnings = []
    normalized = config.copy()

    # Validate max_depth
    if 'max_depth' in config:
        if not isinstance(config['max_depth'], int) or config['max_depth'] < 1:
            errors.append("max_depth must be a positive integer")
        elif config['max_depth'] > 20:
            warnings.append("max_depth > 20 may result in very long crawl times")
            normalized['max_depth'] = min(config['max_depth'], 50)

    # Validate max_pages
    if 'max_pages' in config:
        if not isinstance(config['max_pages'], int) or config['max_pages'] < 1:
            errors.append("max_pages must be a positive integer")
        elif config['max_pages'] > 10000:
            warnings.append("max_pages > 10000 may result in very long test times")

    # Validate timeout
    if 'timeout' in config:
        if not isinstance(config['timeout'], (int, float)) or config['timeout'] < 1:
            errors.append("timeout must be a positive number")
        elif config['timeout'] > 300:
            warnings.append("timeout > 300 seconds is unusually long")

    # Validate WCAG level
    if 'wcag_level' in config:
        valid_levels = {'A', 'AA', 'AAA'}
        if config['wcag_level'].upper() not in valid_levels:
            errors.append(f"wcag_level must be one of: {valid_levels}")
        else:
            normalized['wcag_level'] = config['wcag_level'].upper()

    # Validate concurrent users for load testing
    if 'load_test_concurrent_users' in config:
        if not isinstance(config['load_test_concurrent_users'], int):
            errors.append("load_test_concurrent_users must be an integer")
        elif config['load_test_concurrent_users'] > 1000:
            warnings.append("Testing with >1000 concurrent users requires significant resources")

    return ValidationResult(
        is_valid=len(errors) == 0,
        normalized_value=normalized,
        errors=errors,
        warnings=warnings
    )


def sanitize_selector(selector: str) -> str:
    """
    Sanitize a CSS selector string.

    Args:
        selector: CSS selector to sanitize

    Returns:
        Sanitized selector string
    """
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '\\', '\n', '\r', '\t']
    result = selector
    for char in dangerous_chars:
        result = result.replace(char, '')
    return result.strip()


def validate_email(email: str) -> bool:
    """
    Validate an email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    email_pattern = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    return bool(email_pattern.match(email))


def validate_phone(phone: str) -> bool:
    """
    Validate a phone number format (basic validation).

    Args:
        phone: Phone number to validate

    Returns:
        True if appears valid, False otherwise
    """
    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\.\(\)]+', '', phone)
    # Check if remaining is digits with optional leading +
    return bool(re.match(r'^\+?\d{7,15}$', cleaned))


def is_valid_html_id(id_str: str) -> bool:
    """
    Check if a string is a valid HTML ID attribute.

    Args:
        id_str: String to check

    Returns:
        True if valid HTML ID, False otherwise
    """
    if not id_str:
        return False
    # HTML5 IDs can contain any characters except spaces
    # Must have at least one character
    return ' ' not in id_str and len(id_str) > 0


def is_valid_css_class(class_str: str) -> bool:
    """
    Check if a string is a valid CSS class name.

    Args:
        class_str: String to check

    Returns:
        True if valid CSS class, False otherwise
    """
    if not class_str:
        return False
    # CSS class names can't start with a digit
    # Can contain letters, digits, hyphens, underscores
    return bool(re.match(r'^[a-zA-Z_-][a-zA-Z0-9_-]*$', class_str))
