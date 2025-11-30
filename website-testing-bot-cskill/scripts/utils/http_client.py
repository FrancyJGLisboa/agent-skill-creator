"""
HTTP client with retry logic and response handling.

Provides robust HTTP request capabilities with exponential backoff,
timeout handling, and comprehensive response processing.
"""

import time
import asyncio
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from urllib.parse import urlparse
import ssl
import socket

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from .constants import (
    DEFAULT_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY_BASE,
    DEFAULT_USER_AGENT,
    HTTP_SUCCESS_CODES,
    HTTP_ERROR_CODES
)


@dataclass
class HTTPResponse:
    """Standardized HTTP response object."""
    url: str
    status_code: int
    headers: Dict[str, str]
    content: bytes
    text: str
    elapsed_ms: float
    redirects: List[str] = field(default_factory=list)
    error: Optional[str] = None
    ssl_info: Optional[Dict[str, Any]] = None

    @property
    def is_success(self) -> bool:
        """Check if response indicates success."""
        return self.status_code in HTTP_SUCCESS_CODES

    @property
    def is_error(self) -> bool:
        """Check if response indicates an error."""
        return self.status_code in HTTP_ERROR_CODES

    @property
    def is_redirect(self) -> bool:
        """Check if response is a redirect."""
        return self.status_code in {301, 302, 303, 307, 308}

    @property
    def content_type(self) -> Optional[str]:
        """Get the content type from headers."""
        return self.headers.get('content-type', '').split(';')[0].strip()

    @property
    def content_length(self) -> int:
        """Get content length in bytes."""
        return len(self.content) if self.content else 0


class HTTPClient:
    """
    Robust HTTP client with retry logic and comprehensive response handling.

    Supports both synchronous (requests) and asynchronous (aiohttp) modes.
    """

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
        user_agent: str = DEFAULT_USER_AGENT,
        follow_redirects: bool = True,
        verify_ssl: bool = True
    ):
        """
        Initialize HTTP client.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            user_agent: User agent string for requests
            follow_redirects: Whether to follow redirects
            verify_ssl: Whether to verify SSL certificates
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.user_agent = user_agent
        self.follow_redirects = follow_redirects
        self.verify_ssl = verify_ssl

        self._session = None
        self._async_session = None

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default request headers."""
        return {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None
    ) -> HTTPResponse:
        """
        Perform a synchronous GET request with retry logic.

        Args:
            url: URL to request
            headers: Optional additional headers
            params: Optional query parameters

        Returns:
            HTTPResponse object
        """
        if not REQUESTS_AVAILABLE:
            return HTTPResponse(
                url=url,
                status_code=0,
                headers={},
                content=b'',
                text='',
                elapsed_ms=0,
                error="requests library not installed"
            )

        request_headers = self._get_default_headers()
        if headers:
            request_headers.update(headers)

        last_error = None
        redirects = []

        for attempt in range(self.max_retries):
            try:
                start_time = time.time()

                response = requests.get(
                    url,
                    headers=request_headers,
                    params=params,
                    timeout=self.timeout,
                    allow_redirects=self.follow_redirects,
                    verify=self.verify_ssl
                )

                elapsed_ms = (time.time() - start_time) * 1000

                # Collect redirect history
                if response.history:
                    redirects = [r.url for r in response.history]

                # Get SSL info if HTTPS
                ssl_info = None
                if url.startswith('https://'):
                    ssl_info = self._get_ssl_info(url)

                return HTTPResponse(
                    url=response.url,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    content=response.content,
                    text=response.text,
                    elapsed_ms=elapsed_ms,
                    redirects=redirects,
                    ssl_info=ssl_info
                )

            except requests.exceptions.Timeout:
                last_error = f"Request timed out after {self.timeout}s"
            except requests.exceptions.SSLError as e:
                last_error = f"SSL error: {str(e)}"
                # Don't retry SSL errors
                break
            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error: {str(e)}"
            except requests.exceptions.RequestException as e:
                last_error = f"Request error: {str(e)}"

            # Exponential backoff before retry
            if attempt < self.max_retries - 1:
                delay = RETRY_DELAY_BASE ** (attempt + 1)
                time.sleep(delay)

        return HTTPResponse(
            url=url,
            status_code=0,
            headers={},
            content=b'',
            text='',
            elapsed_ms=0,
            error=last_error
        )

    async def get_async(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None
    ) -> HTTPResponse:
        """
        Perform an asynchronous GET request with retry logic.

        Args:
            url: URL to request
            headers: Optional additional headers
            params: Optional query parameters

        Returns:
            HTTPResponse object
        """
        if not AIOHTTP_AVAILABLE:
            return HTTPResponse(
                url=url,
                status_code=0,
                headers={},
                content=b'',
                text='',
                elapsed_ms=0,
                error="aiohttp library not installed"
            )

        request_headers = self._get_default_headers()
        if headers:
            request_headers.update(headers)

        last_error = None
        redirects = []

        ssl_context = None if self.verify_ssl else False

        for attempt in range(self.max_retries):
            try:
                start_time = time.time()

                timeout = aiohttp.ClientTimeout(total=self.timeout)

                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(
                        url,
                        headers=request_headers,
                        params=params,
                        allow_redirects=self.follow_redirects,
                        ssl=ssl_context
                    ) as response:
                        elapsed_ms = (time.time() - start_time) * 1000
                        content = await response.read()
                        text = await response.text(errors='replace')

                        # Collect redirect history
                        if response.history:
                            redirects = [str(r.url) for r in response.history]

                        return HTTPResponse(
                            url=str(response.url),
                            status_code=response.status,
                            headers=dict(response.headers),
                            content=content,
                            text=text,
                            elapsed_ms=elapsed_ms,
                            redirects=redirects
                        )

            except asyncio.TimeoutError:
                last_error = f"Request timed out after {self.timeout}s"
            except aiohttp.ClientSSLError as e:
                last_error = f"SSL error: {str(e)}"
                break  # Don't retry SSL errors
            except aiohttp.ClientError as e:
                last_error = f"Client error: {str(e)}"
            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"

            # Exponential backoff before retry
            if attempt < self.max_retries - 1:
                delay = RETRY_DELAY_BASE ** (attempt + 1)
                await asyncio.sleep(delay)

        return HTTPResponse(
            url=url,
            status_code=0,
            headers={},
            content=b'',
            text='',
            elapsed_ms=0,
            error=last_error
        )

    def head(self, url: str) -> HTTPResponse:
        """
        Perform a HEAD request to check URL status without downloading body.

        Args:
            url: URL to check

        Returns:
            HTTPResponse object (content will be empty)
        """
        if not REQUESTS_AVAILABLE:
            return HTTPResponse(
                url=url,
                status_code=0,
                headers={},
                content=b'',
                text='',
                elapsed_ms=0,
                error="requests library not installed"
            )

        try:
            start_time = time.time()

            response = requests.head(
                url,
                headers=self._get_default_headers(),
                timeout=self.timeout,
                allow_redirects=self.follow_redirects,
                verify=self.verify_ssl
            )

            elapsed_ms = (time.time() - start_time) * 1000

            return HTTPResponse(
                url=response.url,
                status_code=response.status_code,
                headers=dict(response.headers),
                content=b'',
                text='',
                elapsed_ms=elapsed_ms
            )

        except Exception as e:
            return HTTPResponse(
                url=url,
                status_code=0,
                headers={},
                content=b'',
                text='',
                elapsed_ms=0,
                error=str(e)
            )

    def _get_ssl_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get SSL certificate information for a URL.

        Args:
            url: HTTPS URL to check

        Returns:
            Dictionary with SSL info or None
        """
        try:
            parsed = urlparse(url)
            hostname = parsed.netloc.split(':')[0]
            port = int(parsed.netloc.split(':')[1]) if ':' in parsed.netloc else 443

            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    version = ssock.version()

                    return {
                        'subject': dict(x[0] for x in cert.get('subject', [])),
                        'issuer': dict(x[0] for x in cert.get('issuer', [])),
                        'version': version,
                        'cipher': cipher[0] if cipher else None,
                        'not_before': cert.get('notBefore'),
                        'not_after': cert.get('notAfter'),
                        'serial_number': cert.get('serialNumber')
                    }
        except Exception:
            return None

    async def batch_get_async(
        self,
        urls: List[str],
        concurrency: int = 10
    ) -> List[HTTPResponse]:
        """
        Perform multiple async GET requests with concurrency limit.

        Args:
            urls: List of URLs to request
            concurrency: Maximum concurrent requests

        Returns:
            List of HTTPResponse objects
        """
        semaphore = asyncio.Semaphore(concurrency)

        async def limited_get(url: str) -> HTTPResponse:
            async with semaphore:
                return await self.get_async(url)

        tasks = [limited_get(url) for url in urls]
        return await asyncio.gather(*tasks)

    def check_url_status(self, url: str) -> Tuple[int, Optional[str]]:
        """
        Quick URL status check returning just status code and error.

        Args:
            url: URL to check

        Returns:
            Tuple of (status_code, error_message)
        """
        response = self.head(url)
        return (response.status_code, response.error)
