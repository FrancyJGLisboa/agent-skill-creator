"""
Security tester for vulnerability scanning and risk assessment.

Checks SSL/TLS, security headers, and common vulnerabilities.
"""

import re
import ssl
import socket
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from urllib.parse import urlparse
from datetime import datetime

from ..utils.http_client import HTTPClient
from ..utils.constants import (
    SEVERITY_CRITICAL,
    SEVERITY_HIGH,
    SEVERITY_MEDIUM,
    SEVERITY_LOW,
    SECURITY_HEADERS
)


@dataclass
class SecurityIssue:
    """A security issue found during testing."""
    severity: str
    category: str
    title: str
    description: str
    fix_instruction: str
    reference: Optional[str] = None


@dataclass
class SSLInfo:
    """SSL/TLS certificate information."""
    valid: bool
    issuer: str
    subject: str
    expires: str
    days_until_expiry: int
    protocol_version: str
    cipher_suite: str
    certificate_chain_valid: bool
    issues: List[SecurityIssue] = field(default_factory=list)


@dataclass
class SecurityReport:
    """Complete security testing report."""
    url: str
    ssl_info: SSLInfo
    security_headers: Dict[str, Any]
    vulnerabilities: List[SecurityIssue]
    cookies: List[Dict[str, Any]]
    grade: str
    score: int
    all_issues: List[SecurityIssue]
    recommendations: List[Dict[str, Any]]


class SecurityTester:
    """
    Security vulnerability scanner for websites.

    Tests SSL/TLS, security headers, cookies, and common web vulnerabilities.
    """

    def __init__(self, http_client: Optional[HTTPClient] = None):
        """
        Initialize security tester.

        Args:
            http_client: HTTP client for requests
        """
        self.http_client = http_client or HTTPClient()

    async def test_security(self, url: str) -> SecurityReport:
        """
        Run comprehensive security tests.

        Args:
            url: URL to test

        Returns:
            SecurityReport with all findings
        """
        all_issues = []

        # Test SSL/TLS
        ssl_info = self._test_ssl(url)
        all_issues.extend(ssl_info.issues)

        # Get response for header/cookie analysis
        response = await self.http_client.get_async(url)

        # Test security headers
        header_results = self._test_security_headers(response.headers)
        all_issues.extend(header_results['issues'])

        # Test cookies
        cookie_results = self._test_cookies(response.headers)
        all_issues.extend(cookie_results['issues'])

        # Test for common vulnerabilities
        vuln_results = await self._test_vulnerabilities(url, response.text)
        all_issues.extend(vuln_results)

        # Calculate score and grade
        score = self._calculate_security_score(all_issues, ssl_info)
        grade = self._score_to_grade(score)

        # Generate recommendations
        recommendations = self._generate_recommendations(all_issues)

        return SecurityReport(
            url=url,
            ssl_info=ssl_info,
            security_headers=header_results,
            vulnerabilities=vuln_results,
            cookies=cookie_results['cookies'],
            grade=grade,
            score=score,
            all_issues=all_issues,
            recommendations=recommendations
        )

    def _test_ssl(self, url: str) -> SSLInfo:
        """Test SSL/TLS configuration."""
        issues = []

        parsed = urlparse(url)

        # Check if HTTPS
        if parsed.scheme != 'https':
            issues.append(SecurityIssue(
                severity=SEVERITY_CRITICAL,
                category='ssl',
                title='Site not using HTTPS',
                description='The website is not using HTTPS encryption',
                fix_instruction=(
                    f"Enable HTTPS on the server. Steps: "
                    f"1) Obtain SSL certificate (free from Let's Encrypt), "
                    f"2) Install certificate on web server, "
                    f"3) Configure server to use HTTPS, "
                    f"4) Redirect all HTTP traffic to HTTPS. "
                    f"Command for Let's Encrypt: 'certbot --apache' or 'certbot --nginx'"
                ),
                reference='https://letsencrypt.org/getting-started/'
            ))
            return SSLInfo(
                valid=False,
                issuer='N/A',
                subject='N/A',
                expires='N/A',
                days_until_expiry=0,
                protocol_version='N/A',
                cipher_suite='N/A',
                certificate_chain_valid=False,
                issues=issues
            )

        hostname = parsed.netloc.split(':')[0]
        port = int(parsed.netloc.split(':')[1]) if ':' in parsed.netloc else 443

        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    version = ssock.version()

                    # Parse certificate info
                    issuer = dict(x[0] for x in cert.get('issuer', []))
                    subject = dict(x[0] for x in cert.get('subject', []))
                    not_after = cert.get('notAfter', '')

                    # Calculate days until expiry
                    try:
                        expiry_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                        days_until_expiry = (expiry_date - datetime.now()).days
                    except Exception:
                        days_until_expiry = -1

                    # Check for issues
                    if days_until_expiry < 30:
                        issues.append(SecurityIssue(
                            severity=SEVERITY_HIGH if days_until_expiry < 7 else SEVERITY_MEDIUM,
                            category='ssl',
                            title='SSL certificate expiring soon',
                            description=f'Certificate expires in {days_until_expiry} days',
                            fix_instruction=(
                                f"Renew SSL certificate before expiration. "
                                f"For Let's Encrypt: 'certbot renew'. "
                                f"Set up automatic renewal: 'crontab -e' and add: "
                                f"'0 0 1 * * certbot renew --quiet'"
                            )
                        ))

                    if version in ['TLSv1', 'TLSv1.0', 'SSLv3', 'SSLv2']:
                        issues.append(SecurityIssue(
                            severity=SEVERITY_HIGH,
                            category='ssl',
                            title='Outdated TLS version',
                            description=f'Server uses {version} which is deprecated',
                            fix_instruction=(
                                f"Upgrade to TLS 1.2 or TLS 1.3. "
                                f"For Apache: 'SSLProtocol -all +TLSv1.2 +TLSv1.3'. "
                                f"For Nginx: 'ssl_protocols TLSv1.2 TLSv1.3;'"
                            )
                        ))

                    return SSLInfo(
                        valid=True,
                        issuer=issuer.get('organizationName', 'Unknown'),
                        subject=subject.get('commonName', hostname),
                        expires=not_after,
                        days_until_expiry=days_until_expiry,
                        protocol_version=version,
                        cipher_suite=cipher[0] if cipher else 'Unknown',
                        certificate_chain_valid=True,
                        issues=issues
                    )

        except ssl.SSLError as e:
            issues.append(SecurityIssue(
                severity=SEVERITY_CRITICAL,
                category='ssl',
                title='SSL certificate error',
                description=str(e),
                fix_instruction=(
                    f"Fix SSL certificate issue. Common causes: "
                    f"1) Certificate not trusted - get from recognized CA, "
                    f"2) Certificate expired - renew it, "
                    f"3) Hostname mismatch - ensure certificate matches domain, "
                    f"4) Incomplete chain - include intermediate certificates"
                )
            ))
        except Exception as e:
            issues.append(SecurityIssue(
                severity=SEVERITY_HIGH,
                category='ssl',
                title='SSL connection failed',
                description=str(e),
                fix_instruction='Check server SSL configuration and certificate'
            ))

        return SSLInfo(
            valid=False,
            issuer='Unknown',
            subject='Unknown',
            expires='Unknown',
            days_until_expiry=-1,
            protocol_version='Unknown',
            cipher_suite='Unknown',
            certificate_chain_valid=False,
            issues=issues
        )

    def _test_security_headers(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Test security headers."""
        issues = []
        header_status = {}

        for header_name, config in SECURITY_HEADERS.items():
            header_value = headers.get(header_name.lower()) or headers.get(header_name)

            if header_value:
                header_status[header_name] = {
                    'present': True,
                    'value': header_value
                }
            else:
                header_status[header_name] = {
                    'present': False,
                    'value': None
                }

                issues.append(SecurityIssue(
                    severity=config['severity'],
                    category='headers',
                    title=f'Missing {header_name} header',
                    description=config['description'],
                    fix_instruction=self._get_header_fix(header_name, config)
                ))

        return {
            'headers': header_status,
            'issues': issues
        }

    def _get_header_fix(self, header_name: str, config: Dict[str, Any]) -> str:
        """Get fix instruction for missing security header."""
        fixes = {
            'Strict-Transport-Security': (
                f"Add HSTS header. For Apache: "
                f"'Header always set Strict-Transport-Security \"max-age=31536000; includeSubDomains\"'. "
                f"For Nginx: 'add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;'. "
                f"This forces browsers to use HTTPS for future visits."
            ),
            'Content-Security-Policy': (
                f"Add CSP header to prevent XSS. Start with report-only mode: "
                f"'Content-Security-Policy-Report-Only: default-src 'self'; script-src 'self'; "
                f"style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;'. "
                f"Monitor for violations, then enforce. This blocks inline scripts and external resources."
            ),
            'X-Frame-Options': (
                f"Add X-Frame-Options to prevent clickjacking. "
                f"'Header always set X-Frame-Options \"SAMEORIGIN\"' for Apache, "
                f"'add_header X-Frame-Options \"SAMEORIGIN\" always;' for Nginx. "
                f"Use 'DENY' to completely block framing."
            ),
            'X-Content-Type-Options': (
                f"Add X-Content-Type-Options to prevent MIME sniffing. "
                f"'Header always set X-Content-Type-Options \"nosniff\"' for Apache, "
                f"'add_header X-Content-Type-Options \"nosniff\" always;' for Nginx."
            ),
            'X-XSS-Protection': (
                f"Add X-XSS-Protection header. "
                f"'Header always set X-XSS-Protection \"1; mode=block\"' for Apache, "
                f"'add_header X-XSS-Protection \"1; mode=block\" always;' for Nginx. "
                f"Note: This is legacy, CSP is preferred for modern browsers."
            ),
            'Referrer-Policy': (
                f"Add Referrer-Policy to control referrer information. "
                f"'Header always set Referrer-Policy \"strict-origin-when-cross-origin\"' for Apache, "
                f"'add_header Referrer-Policy \"strict-origin-when-cross-origin\" always;' for Nginx."
            ),
            'Permissions-Policy': (
                f"Add Permissions-Policy to control browser features. "
                f"'Header always set Permissions-Policy \"geolocation=(), microphone=(), camera=()\"' for Apache. "
                f"This disables sensitive APIs unless explicitly allowed."
            )
        }
        return fixes.get(header_name, f"Add {header_name}: {config['recommended']}")

    def _test_cookies(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Test cookie security."""
        issues = []
        cookies = []

        set_cookie_headers = []
        for key, value in headers.items():
            if key.lower() == 'set-cookie':
                set_cookie_headers.append(value)

        for cookie_str in set_cookie_headers:
            cookie_data = self._parse_cookie(cookie_str)
            cookies.append(cookie_data)

            # Check for security issues
            if cookie_data.get('is_session'):
                if not cookie_data.get('secure'):
                    issues.append(SecurityIssue(
                        severity=SEVERITY_HIGH,
                        category='cookies',
                        title=f"Session cookie '{cookie_data['name']}' missing Secure flag",
                        description='Session cookie can be sent over unencrypted HTTP',
                        fix_instruction=(
                            f"Add Secure flag to session cookies. "
                            f"Set-Cookie: {cookie_data['name']}=value; Secure; HttpOnly; SameSite=Strict. "
                            f"In code: cookie.setSecure(true) or equivalent for your framework."
                        )
                    ))

                if not cookie_data.get('httponly'):
                    issues.append(SecurityIssue(
                        severity=SEVERITY_HIGH,
                        category='cookies',
                        title=f"Session cookie '{cookie_data['name']}' missing HttpOnly flag",
                        description='Session cookie accessible via JavaScript (XSS risk)',
                        fix_instruction=(
                            f"Add HttpOnly flag to prevent JavaScript access. "
                            f"Set-Cookie: {cookie_data['name']}=value; HttpOnly; Secure; SameSite=Strict. "
                            f"This prevents cookie theft via XSS attacks."
                        )
                    ))

                if not cookie_data.get('samesite'):
                    issues.append(SecurityIssue(
                        severity=SEVERITY_MEDIUM,
                        category='cookies',
                        title=f"Session cookie '{cookie_data['name']}' missing SameSite attribute",
                        description='Cookie may be vulnerable to CSRF attacks',
                        fix_instruction=(
                            f"Add SameSite attribute for CSRF protection. "
                            f"Set-Cookie: {cookie_data['name']}=value; SameSite=Strict. "
                            f"Use 'Strict' for high security, 'Lax' for better compatibility."
                        )
                    ))

        return {
            'cookies': cookies,
            'issues': issues
        }

    def _parse_cookie(self, cookie_str: str) -> Dict[str, Any]:
        """Parse a Set-Cookie header value."""
        parts = cookie_str.split(';')
        name_value = parts[0].strip()

        name = name_value.split('=')[0] if '=' in name_value else name_value
        value = name_value.split('=', 1)[1] if '=' in name_value else ''

        cookie_lower = cookie_str.lower()

        # Detect if session cookie
        session_indicators = ['session', 'sess', 'sid', 'token', 'auth', 'jwt']
        is_session = any(ind in name.lower() for ind in session_indicators)

        return {
            'name': name,
            'value': value[:20] + '...' if len(value) > 20 else value,
            'secure': 'secure' in cookie_lower,
            'httponly': 'httponly' in cookie_lower,
            'samesite': 'samesite' in cookie_lower,
            'is_session': is_session
        }

    async def _test_vulnerabilities(self, url: str, html: str) -> List[SecurityIssue]:
        """Test for common vulnerabilities."""
        issues = []

        # Check for mixed content
        if url.startswith('https://'):
            http_resources = re.findall(r'(src|href)=["\']http://[^"\']+["\']', html, re.I)
            if http_resources:
                issues.append(SecurityIssue(
                    severity=SEVERITY_HIGH,
                    category='mixed_content',
                    title='Mixed content detected',
                    description=f'HTTPS page loads {len(http_resources)} resources over HTTP',
                    fix_instruction=(
                        f"Change all HTTP resource URLs to HTTPS. "
                        f"Find and replace: src='http://' with src='https://'. "
                        f"Or use protocol-relative URLs: src='//example.com/'. "
                        f"Mixed content can be blocked by browsers and exposes data."
                    )
                ))

        # Check for inline event handlers (potential XSS vector)
        inline_handlers = re.findall(r'on\w+\s*=\s*["\'][^"\']+["\']', html, re.I)
        if len(inline_handlers) > 10:
            issues.append(SecurityIssue(
                severity=SEVERITY_LOW,
                category='xss_risk',
                title='Many inline event handlers detected',
                description=f'{len(inline_handlers)} inline event handlers found',
                fix_instruction=(
                    f"Move inline event handlers to external JavaScript. "
                    f"Instead of: <button onclick='doThing()'> "
                    f"Use: element.addEventListener('click', doThing). "
                    f"This enables CSP and improves security."
                )
            ))

        # Check for potentially dangerous patterns
        if 'eval(' in html or 'innerHTML' in html:
            issues.append(SecurityIssue(
                severity=SEVERITY_MEDIUM,
                category='xss_risk',
                title='Potentially dangerous JavaScript patterns',
                description='eval() or innerHTML usage detected in page',
                fix_instruction=(
                    f"Avoid eval() and innerHTML with user input. "
                    f"Replace innerHTML with textContent for text, "
                    f"or use DOM methods like createElement. "
                    f"Replace eval with JSON.parse for data parsing."
                )
            ))

        # Check for exposed credentials/secrets
        secret_patterns = [
            (r'api[_-]?key\s*[:=]\s*["\'][^"\']{10,}["\']', 'API key'),
            (r'password\s*[:=]\s*["\'][^"\']+["\']', 'password'),
            (r'secret\s*[:=]\s*["\'][^"\']{10,}["\']', 'secret'),
            (r'aws[_-]?access[_-]?key', 'AWS key'),
        ]

        for pattern, name in secret_patterns:
            if re.search(pattern, html, re.I):
                issues.append(SecurityIssue(
                    severity=SEVERITY_CRITICAL,
                    category='exposed_secrets',
                    title=f'Possible {name} exposed in HTML',
                    description=f'Pattern matching {name} found in page source',
                    fix_instruction=(
                        f"Remove {name} from client-side code immediately. "
                        f"Store secrets server-side only. Use environment variables "
                        f"for configuration. Rotate any exposed credentials. "
                        f"Consider the credential compromised."
                    )
                ))

        # Check for forms without CSRF token
        forms = re.findall(r'<form[^>]*method=["\']post["\'][^>]*>.*?</form>', html, re.I | re.S)
        for form in forms:
            if 'csrf' not in form.lower() and '_token' not in form.lower():
                issues.append(SecurityIssue(
                    severity=SEVERITY_MEDIUM,
                    category='csrf',
                    title='Form may be missing CSRF protection',
                    description='POST form without visible CSRF token',
                    fix_instruction=(
                        f"Add CSRF token to all POST forms. "
                        f"Generate token server-side and include as hidden field: "
                        f"<input type='hidden' name='csrf_token' value='...'/>. "
                        f"Validate token on form submission. Most frameworks have built-in support."
                    )
                ))

        return issues

    def _calculate_security_score(
        self,
        issues: List[SecurityIssue],
        ssl_info: SSLInfo
    ) -> int:
        """Calculate overall security score."""
        score = 100

        # Deduct for issues
        severity_deductions = {
            SEVERITY_CRITICAL: 25,
            SEVERITY_HIGH: 15,
            SEVERITY_MEDIUM: 8,
            SEVERITY_LOW: 3
        }

        for issue in issues:
            score -= severity_deductions.get(issue.severity, 5)

        # Bonus for valid HTTPS
        if ssl_info.valid:
            score = min(100, score + 5)

        return max(0, min(100, score))

    def _score_to_grade(self, score: int) -> str:
        """Convert score to letter grade."""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'

    def _generate_recommendations(
        self,
        issues: List[SecurityIssue]
    ) -> List[Dict[str, Any]]:
        """Generate security recommendations."""
        recommendations = []

        # Group issues by category
        categories = {}
        for issue in issues:
            if issue.category not in categories:
                categories[issue.category] = []
            categories[issue.category].append(issue)

        # Generate category-level recommendations
        if 'ssl' in categories:
            recommendations.append({
                'priority': 'critical',
                'category': 'SSL/TLS',
                'title': 'Fix SSL/TLS configuration',
                'description': (
                    f"Found {len(categories['ssl'])} SSL-related issues. "
                    f"Ensure valid HTTPS with TLS 1.2+, proper certificate chain, "
                    f"and certificate not expiring soon."
                )
            })

        if 'headers' in categories:
            recommendations.append({
                'priority': 'high',
                'category': 'Security Headers',
                'title': 'Implement security headers',
                'description': (
                    f"Missing {len(categories['headers'])} security headers. "
                    f"Add CSP, HSTS, and other headers to protect against common attacks."
                )
            })

        return recommendations
