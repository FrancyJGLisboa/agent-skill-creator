#!/usr/bin/env python3
"""
Browser Tab Checker - Unified Interface

This script provides a unified interface to count and display tabs
from all supported browsers (Chrome, Firefox, Chromium, etc.)
"""

import sys
import argparse
from typing import Dict, List, Tuple, Optional

# Import individual browser counters
from check_chrome_tabs import ChromeTabCounter
from check_firefox_tabs import FirefoxTabCounter


class BrowserTabChecker:
    """Unified browser tab checker for all supported browsers."""

    def __init__(self):
        """Initialize browser tab checker."""
        self.chrome_counter = ChromeTabCounter()
        self.firefox_counter = FirefoxTabCounter()

    def check_all_browsers(self) -> Dict[str, Dict]:
        """
        Check tabs in all supported browsers.

        Returns:
            Dictionary with browser results:
            {
                'chrome': {'count': int, 'error': str|None},
                'firefox': {'count': int, 'error': str|None},
                ...
            }
        """
        results = {}

        # Check Chrome/Chromium
        chrome_count, chrome_error = self.chrome_counter.count_tabs()
        results['chrome'] = {
            'count': chrome_count,
            'error': chrome_error
        }

        # Check Firefox
        firefox_count, firefox_error = self.firefox_counter.count_tabs()
        results['firefox'] = {
            'count': firefox_count,
            'error': firefox_error
        }

        return results

    def get_total_tabs(self) -> Tuple[int, List[str]]:
        """
        Get total number of tabs across all browsers.

        Returns:
            Tuple of (total count, list of browsers with tabs)
        """
        results = self.check_all_browsers()
        total = 0
        browsers_with_tabs = []

        for browser, data in results.items():
            if data['count'] is not None and data['count'] > 0:
                total += data['count']
                browsers_with_tabs.append(browser)

        return total, browsers_with_tabs

    def get_detailed_info(self) -> Dict[str, Dict]:
        """
        Get detailed information about tabs in all browsers.

        Returns:
            Dictionary with detailed browser tab information
        """
        details = {}

        # Chrome details
        chrome_tabs, chrome_error = self.chrome_counter.get_tab_info()
        details['chrome'] = {
            'tabs': chrome_tabs,
            'error': chrome_error
        }

        # Firefox details
        firefox_tabs, firefox_error = self.firefox_counter.get_tab_info()
        details['firefox'] = {
            'tabs': firefox_tabs,
            'error': firefox_error
        }

        return details


def format_output_simple(results: Dict[str, Dict]) -> str:
    """
    Format results in simple text format.

    Args:
        results: Browser results dictionary

    Returns:
        Formatted string
    """
    lines = []
    total = 0

    lines.append("Browser Tab Count")
    lines.append("=" * 50)

    for browser, data in sorted(results.items()):
        if data['count'] is not None:
            lines.append(f"{browser.capitalize():15} {data['count']:>5} tabs")
            total += data['count']
        else:
            lines.append(f"{browser.capitalize():15} {'N/A':>5} (not running or inaccessible)")

    lines.append("-" * 50)
    lines.append(f"{'Total':15} {total:>5} tabs")

    return "\n".join(lines)


def format_output_detailed(details: Dict[str, Dict]) -> str:
    """
    Format detailed tab information.

    Args:
        details: Detailed browser information

    Returns:
        Formatted string
    """
    lines = []

    for browser, data in sorted(details.items()):
        if data['tabs']:
            lines.append(f"\n{browser.capitalize()} Tabs ({len(data['tabs'])} total):")
            lines.append("=" * 70)

            for i, tab in enumerate(data['tabs'], 1):
                # Handle different tab info formats
                if 'window' in tab:  # Firefox format
                    lines.append(f"\n  [{i}] Window {tab.get('window', '?')}, Tab {tab.get('tab_number', '?')}")
                else:  # Chrome format
                    lines.append(f"\n  [{i}]")

                title = tab.get('title', 'Untitled')
                url = tab.get('url', '')

                # Truncate long titles
                if len(title) > 60:
                    title = title[:57] + "..."

                lines.append(f"      Title: {title}")
                lines.append(f"      URL:   {url}")

        elif data['error']:
            lines.append(f"\n{browser.capitalize()}: {data['error']}")

    return "\n".join(lines)


def format_output_json(results: Dict[str, Dict]) -> str:
    """
    Format results in JSON format.

    Args:
        results: Browser results dictionary

    Returns:
        JSON string
    """
    import json
    return json.dumps(results, indent=2)


def main():
    """Main function for CLI usage."""
    parser = argparse.ArgumentParser(
        description='Check and count browser tabs across all browsers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Show simple tab count
  %(prog)s -v                 # Show detailed tab information
  %(prog)s --json             # Output in JSON format
  %(prog)s --browser chrome   # Check only Chrome
        """
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed information about each tab'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )

    parser.add_argument(
        '--browser',
        choices=['chrome', 'firefox', 'all'],
        default='all',
        help='Which browser to check (default: all)'
    )

    args = parser.parse_args()

    # Initialize checker
    checker = BrowserTabChecker()

    # Get results
    if args.verbose:
        details = checker.get_detailed_info()

        # Filter by browser if specified
        if args.browser != 'all':
            details = {args.browser: details[args.browser]}

        if args.json:
            print(format_output_json(details))
        else:
            print(format_output_detailed(details))
    else:
        results = checker.check_all_browsers()

        # Filter by browser if specified
        if args.browser != 'all':
            results = {args.browser: results[args.browser]}

        if args.json:
            print(format_output_json(results))
        else:
            print(format_output_simple(results))

    # Exit with appropriate code
    total, browsers = checker.get_total_tabs()
    if total == 0:
        sys.exit(1)  # No tabs found


if __name__ == "__main__":
    main()
