# Browser Tab Checker

A Python tool to check and count open browser tabs across multiple browsers (Chrome, Chromium, Firefox) on Linux systems.

## Features

- **Multi-browser support**: Chrome, Chromium, and Firefox
- **Simple CLI interface**: Easy to use command-line tool
- **Detailed information**: Get titles and URLs of all open tabs
- **Multiple output formats**: Text, detailed, or JSON
- **Claude Code integration**: Can be used as a skill in Claude Code

## Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Steps

1. Clone or download this repository
2. Navigate to the browser-tab-checker directory:
   ```bash
   cd browser-tab-checker
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Make scripts executable (optional):
   ```bash
   chmod +x scripts/*.py
   ```

## Usage

### Basic Usage

Check tabs in all browsers:
```bash
python scripts/browser_tabs.py
```

Output:
```
Browser Tab Count
==================================================
Chrome               12 tabs
Firefox               8 tabs
--------------------------------------------------
Total                20 tabs
```

### Detailed View

Get detailed information about each tab:
```bash
python scripts/browser_tabs.py -v
```

Or:
```bash
python scripts/browser_tabs.py --verbose
```

### JSON Output

Get results in JSON format:
```bash
python scripts/browser_tabs.py --json
```

### Check Specific Browser

Check only Chrome:
```bash
python scripts/browser_tabs.py --browser chrome
```

Check only Firefox:
```bash
python scripts/browser_tabs.py --browser firefox
```

### Individual Browser Scripts

You can also run browser-specific scripts:

**Chrome/Chromium:**
```bash
python scripts/check_chrome_tabs.py
python scripts/check_chrome_tabs.py -v  # Verbose mode
```

**Firefox:**
```bash
python scripts/check_firefox_tabs.py
python scripts/check_firefox_tabs.py -v  # Verbose mode
```

## Browser-Specific Requirements

### Chrome/Chromium

Chrome must be started with remote debugging enabled:

```bash
# Regular Chrome
google-chrome --remote-debugging-port=9222

# Chromium
chromium --remote-debugging-port=9222
```

You can make this permanent by adding it to your Chrome launcher or creating an alias:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias chrome-debug='google-chrome --remote-debugging-port=9222'
```

**Security Note**: Only enable remote debugging on localhost and when needed. Don't expose the debugging port to the network.

### Firefox

Firefox tab counting works by reading the session files. No special configuration is needed. The tool will:

1. Automatically find your Firefox profile(s)
2. Read the session files (handles both compressed and uncompressed formats)
3. Count tabs across all windows

**Note**: Firefox must be running or have been recently closed for session files to be available.

## Claude Code Integration

### Installation as Claude Code Skill

From the parent directory:
```bash
/plugin marketplace add ./browser-tab-checker
```

### Usage in Claude Code

Once installed, you can ask Claude:
- "How many browser tabs do I have open?"
- "Check my browser tabs"
- "Count my open tabs"
- "What tabs are open in Chrome?"

Claude will automatically use this skill to check and report your tab count.

## How It Works

### Chrome/Chromium Detection

The tool uses the Chrome DevTools Protocol (CDP) to communicate with Chrome:

1. Connects to Chrome's debugging port (default: 9222)
2. Queries the `/json` endpoint for list of pages
3. Filters to count only actual page tabs (excludes extensions, background pages)

### Firefox Detection

The tool reads Firefox's session files:

1. Locates Firefox profile directories (`~/.mozilla/firefox/`)
2. Reads session files (`sessionstore.jsonlz4` or `sessionstore.js`)
3. Handles LZ4 compression (newer Firefox versions)
4. Parses session data to count tabs across all windows

## Troubleshooting

### Chrome Shows "Error: Chrome DevTools Protocol port not found"

**Solution**: Start Chrome with remote debugging enabled:
```bash
google-chrome --remote-debugging-port=9222
```

### Firefox Shows "No Firefox profiles found"

**Possible causes**:
- Firefox is not installed
- Firefox profile is in a non-standard location
- Using Firefox Flatpak (check `~/.var/app/org.mozilla.firefox/`)

**Solution**: Ensure Firefox is installed and has been run at least once to create a profile.

### Firefox Shows "Could not read Firefox session files"

**Possible causes**:
- Firefox is not running
- Session files are corrupted
- Permission issues

**Solution**:
- Ensure Firefox is running or was recently running
- Check file permissions in the Firefox profile directory
- Try restarting Firefox

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'lz4'`

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

## Architecture

```
browser-tab-checker/
├── .claude-plugin/
│   └── marketplace.json          # Claude Code plugin configuration
├── scripts/
│   ├── browser_tabs.py           # Main unified interface
│   ├── check_chrome_tabs.py      # Chrome/Chromium tab counter
│   └── check_firefox_tabs.py     # Firefox tab counter
├── references/
│   └── troubleshooting.md        # Detailed troubleshooting guide
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Supported Browsers

| Browser | Linux | Method | Notes |
|---------|-------|--------|-------|
| Chrome | ✅ | CDP | Requires `--remote-debugging-port` |
| Chromium | ✅ | CDP | Requires `--remote-debugging-port` |
| Firefox | ✅ | Session files | Handles LZ4 compression |
| Brave | 🔄 | CDP | Same as Chrome (planned) |
| Edge | 🔄 | CDP | Same as Chrome (planned) |

Legend: ✅ Fully supported | 🔄 Planned | ❌ Not supported

## Examples

### Example 1: Quick Check

```bash
$ python scripts/browser_tabs.py

Browser Tab Count
==================================================
Chrome               15 tabs
Firefox               7 tabs
--------------------------------------------------
Total                22 tabs
```

### Example 2: Detailed Information

```bash
$ python scripts/browser_tabs.py -v

Chrome Tabs (15 total):
======================================================================

  [1]
      Title: GitHub - anthropics/claude-code: Official CLI for Claude
      URL:   https://github.com/anthropics/claude-code

  [2]
      Title: Python Documentation
      URL:   https://docs.python.org/3/

  [3]
      Title: Stack Overflow - Python Questions
      URL:   https://stackoverflow.com/questions/tagged/python

...
```

### Example 3: JSON Output

```bash
$ python scripts/browser_tabs.py --json

{
  "chrome": {
    "count": 15,
    "error": null
  },
  "firefox": {
    "count": 7,
    "error": null
  }
}
```

### Example 4: Check Only Chrome

```bash
$ python scripts/browser_tabs.py --browser chrome

Browser Tab Count
==================================================
Chrome               15 tabs
--------------------------------------------------
Total                15 tabs
```

## Security Considerations

1. **Chrome Remote Debugging**: Only enable on localhost, never expose to network
2. **Session Files**: The tool reads Firefox session files but doesn't modify them
3. **Sensitive Data**: Tab titles and URLs may contain sensitive information - be careful with verbose output

## Performance

- **Chrome**: Very fast (<0.5s) - uses HTTP API
- **Firefox**: Fast (~1s) - reads local files
- **Multiple Profiles**: Checks all profiles sequentially

## Contributing

Contributions are welcome! Areas for improvement:

- [ ] Add support for Brave browser
- [ ] Add support for Edge browser
- [ ] Add Windows support
- [ ] Add macOS support
- [ ] Add tab grouping/organization features
- [ ] Add filtering options (by domain, title, etc.)

## License

Apache 2.0

## Credits

Created as part of the agent-skill-creator project.

## Version History

- **1.0.0** (2025-10-21): Initial release
  - Chrome/Chromium support via CDP
  - Firefox support via session files
  - CLI interface with multiple output formats
  - Claude Code integration
