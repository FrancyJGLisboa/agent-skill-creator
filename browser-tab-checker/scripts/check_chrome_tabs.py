#!/usr/bin/env python3
"""
Chrome/Chromium Tab Counter

This script counts the number of open tabs in Chrome/Chromium browsers
using the Chrome DevTools Protocol (CDP).
"""

import json
import urllib.request
import urllib.error
import socket
from typing import Dict, List, Optional, Tuple


class ChromeTabCounter:
    """Counter for Chrome/Chromium browser tabs."""

    DEFAULT_PORTS = [9222, 9223, 9224]  # Common Chrome DevTools Protocol ports

    def __init__(self, host: str = "localhost", port: Optional[int] = None):
        """
        Initialize Chrome tab counter.

        Args:
            host: Hostname where Chrome is running (default: localhost)
            port: CDP port number (default: auto-detect)
        """
        self.host = host
        self.port = port

    def _check_port(self, port: int, timeout: float = 0.5) -> bool:
        """
        Check if a port is open.

        Args:
            port: Port number to check
            timeout: Connection timeout in seconds

        Returns:
            True if port is open, False otherwise
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            result = sock.connect_ex((self.host, port))
            sock.close()
            return result == 0
        except socket.error:
            return False

    def _find_chrome_port(self) -> Optional[int]:
        """
        Auto-detect Chrome DevTools Protocol port.

        Returns:
            Port number if found, None otherwise
        """
        for port in self.DEFAULT_PORTS:
            if self._check_port(port):
                return port
        return None

    def _fetch_json(self, url: str) -> Optional[Dict]:
        """
        Fetch JSON from URL.

        Args:
            url: URL to fetch

        Returns:
            Parsed JSON data or None on error
        """
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                data = response.read().decode('utf-8')
                return json.loads(data)
        except (urllib.error.URLError, json.JSONDecodeError, socket.timeout):
            return None

    def get_tabs(self) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """
        Get list of open tabs.

        Returns:
            Tuple of (tabs list, error message)
            - On success: (list of tab dicts, None)
            - On failure: (None, error message)
        """
        # Determine port
        port = self.port if self.port else self._find_chrome_port()

        if not port:
            return None, "Chrome DevTools Protocol port not found. Is Chrome running with --remote-debugging-port?"

        # Fetch tabs
        url = f"http://{self.host}:{port}/json"
        data = self._fetch_json(url)

        if data is None:
            return None, f"Failed to connect to Chrome at {self.host}:{port}"

        # Filter for actual page tabs (exclude background pages, extensions, etc.)
        tabs = [item for item in data if item.get('type') == 'page']

        return tabs, None

    def count_tabs(self) -> Tuple[Optional[int], Optional[str]]:
        """
        Count the number of open tabs.

        Returns:
            Tuple of (tab count, error message)
            - On success: (number, None)
            - On failure: (None, error message)
        """
        tabs, error = self.get_tabs()

        if error:
            return None, error

        return len(tabs), None

    def get_tab_info(self) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """
        Get detailed information about open tabs.

        Returns:
            Tuple of (tab info list, error message)
            Each tab info dict contains: title, url, id
        """
        tabs, error = self.get_tabs()

        if error:
            return None, error

        tab_info = []
        for tab in tabs:
            tab_info.append({
                'title': tab.get('title', 'Untitled'),
                'url': tab.get('url', ''),
                'id': tab.get('id', '')
            })

        return tab_info, None


def main():
    """Main function for CLI usage."""
    import sys

    counter = ChromeTabCounter()

    # Get tab count
    count, error = counter.count_tabs()

    if error:
        print(f"Error: {error}", file=sys.stderr)
        print("\nTo enable Chrome DevTools Protocol:", file=sys.stderr)
        print("  Linux: google-chrome --remote-debugging-port=9222", file=sys.stderr)
        print("  Or: chromium --remote-debugging-port=9222", file=sys.stderr)
        sys.exit(1)

    print(f"Chrome/Chromium tabs open: {count}")

    # Get detailed info if requested
    if len(sys.argv) > 1 and sys.argv[1] in ['-v', '--verbose']:
        tab_info, _ = counter.get_tab_info()
        if tab_info:
            print("\nTab details:")
            for i, tab in enumerate(tab_info, 1):
                print(f"  {i}. {tab['title']}")
                print(f"     {tab['url']}")


if __name__ == "__main__":
    main()
