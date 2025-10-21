#!/usr/bin/env python3
"""
Firefox Tab Counter

This script counts the number of open tabs in Firefox browser
by reading the sessionstore files or using the Remote Debugging Protocol.
"""

import json
import os
import glob
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import lz4.block


class FirefoxTabCounter:
    """Counter for Firefox browser tabs."""

    def __init__(self):
        """Initialize Firefox tab counter."""
        self.profile_paths = self._find_firefox_profiles()

    def _find_firefox_profiles(self) -> List[Path]:
        """
        Find Firefox profile directories.

        Returns:
            List of profile directory paths
        """
        profiles = []

        # Common Firefox profile locations on Linux
        home = Path.home()
        firefox_dirs = [
            home / ".mozilla" / "firefox",
            home / ".var" / "app" / "org.mozilla.firefox" / ".mozilla" / "firefox",  # Flatpak
        ]

        for firefox_dir in firefox_dirs:
            if firefox_dir.exists():
                # Find all profile directories (they end with .default or .default-release)
                for profile_dir in firefox_dir.iterdir():
                    if profile_dir.is_dir() and not profile_dir.name.startswith('.'):
                        profiles.append(profile_dir)

        return profiles

    def _decompress_lz4(self, file_path: Path) -> Optional[bytes]:
        """
        Decompress LZ4-compressed Firefox session file.

        Args:
            file_path: Path to compressed file

        Returns:
            Decompressed data or None on error
        """
        try:
            with open(file_path, 'rb') as f:
                # Skip the "mozLz40\0" header (8 bytes)
                f.read(8)
                compressed_data = f.read()
                return lz4.block.decompress(compressed_data)
        except Exception:
            return None

    def _read_session_file(self, file_path: Path) -> Optional[Dict]:
        """
        Read Firefox session file.

        Args:
            file_path: Path to session file

        Returns:
            Parsed session data or None on error
        """
        try:
            # Try reading as JSON first (older Firefox versions)
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass

        # Try decompressing as LZ4 (newer Firefox versions)
        decompressed = self._decompress_lz4(file_path)
        if decompressed:
            try:
                return json.loads(decompressed.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass

        return None

    def _count_tabs_in_session(self, session_data: Dict) -> int:
        """
        Count tabs in session data.

        Args:
            session_data: Parsed session data

        Returns:
            Number of tabs
        """
        count = 0

        # Navigate the session data structure
        windows = session_data.get('windows', [])

        for window in windows:
            tabs = window.get('tabs', [])
            count += len(tabs)

        return count

    def _get_tabs_info_from_session(self, session_data: Dict) -> List[Dict]:
        """
        Extract tab information from session data.

        Args:
            session_data: Parsed session data

        Returns:
            List of tab info dicts
        """
        tabs_info = []

        windows = session_data.get('windows', [])

        for window_idx, window in enumerate(windows, 1):
            tabs = window.get('tabs', [])

            for tab_idx, tab in enumerate(tabs, 1):
                entries = tab.get('entries', [])
                if entries:
                    # Get the current entry
                    current_index = tab.get('index', 1) - 1
                    if 0 <= current_index < len(entries):
                        entry = entries[current_index]
                        tabs_info.append({
                            'window': window_idx,
                            'title': entry.get('title', 'Untitled'),
                            'url': entry.get('url', ''),
                            'tab_number': tab_idx
                        })

        return tabs_info

    def count_tabs(self) -> Tuple[Optional[int], Optional[str]]:
        """
        Count the number of open tabs in all Firefox profiles.

        Returns:
            Tuple of (tab count, error message)
            - On success: (number, None)
            - On failure: (None, error message)
        """
        if not self.profile_paths:
            return None, "No Firefox profiles found"

        total_tabs = 0
        found_session = False

        for profile_path in self.profile_paths:
            # Try different session file names
            session_files = [
                profile_path / "sessionstore.jsonlz4",
                profile_path / "sessionstore-backups" / "recovery.jsonlz4",
                profile_path / "sessionstore.js",
                profile_path / "sessionstore-backups" / "recovery.js",
            ]

            for session_file in session_files:
                if session_file.exists():
                    session_data = self._read_session_file(session_file)
                    if session_data:
                        tabs = self._count_tabs_in_session(session_data)
                        total_tabs += tabs
                        found_session = True
                        break

        if not found_session:
            return None, "Could not read Firefox session files. Is Firefox running?"

        return total_tabs, None

    def get_tab_info(self) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """
        Get detailed information about open tabs.

        Returns:
            Tuple of (tab info list, error message)
            Each tab info dict contains: window, tab_number, title, url
        """
        if not self.profile_paths:
            return None, "No Firefox profiles found"

        all_tabs = []
        found_session = False

        for profile_path in self.profile_paths:
            session_files = [
                profile_path / "sessionstore.jsonlz4",
                profile_path / "sessionstore-backups" / "recovery.jsonlz4",
                profile_path / "sessionstore.js",
                profile_path / "sessionstore-backups" / "recovery.js",
            ]

            for session_file in session_files:
                if session_file.exists():
                    session_data = self._read_session_file(session_file)
                    if session_data:
                        tabs = self._get_tabs_info_from_session(session_data)
                        all_tabs.extend(tabs)
                        found_session = True
                        break

        if not found_session:
            return None, "Could not read Firefox session files. Is Firefox running?"

        return all_tabs, None


def main():
    """Main function for CLI usage."""
    import sys

    counter = FirefoxTabCounter()

    # Get tab count
    count, error = counter.count_tabs()

    if error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    print(f"Firefox tabs open: {count}")

    # Get detailed info if requested
    if len(sys.argv) > 1 and sys.argv[1] in ['-v', '--verbose']:
        tab_info, _ = counter.get_tab_info()
        if tab_info:
            print("\nTab details:")
            current_window = 0
            for tab in tab_info:
                if tab['window'] != current_window:
                    current_window = tab['window']
                    print(f"\n  Window {current_window}:")
                print(f"    {tab['tab_number']}. {tab['title']}")
                print(f"       {tab['url']}")


if __name__ == "__main__":
    main()
