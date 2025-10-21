---
name: browser-tab-checker
description: Checks and counts the number of open browser tabs. Use this skill when the user asks about browser tabs, tab count, open tabs, or how many tabs they have open. Activates with phrases like "how many tabs", "count tabs", "check tabs", "browser tabs", "open tabs". Works with Chrome, Chromium, and Firefox browsers on Linux systems.
---

# Browser Tab Checker Skill

This skill provides the ability to check and count open browser tabs across multiple browsers on Linux systems.

## When to Use This Skill

Claude should automatically activate this skill when the user:

✅ **Asks about browser tabs**
- "How many tabs do I have open?"
- "Check my browser tabs"
- "Count my tabs"
- "How many browser tabs are open?"

✅ **Asks about specific browsers**
- "How many Chrome tabs do I have?"
- "Check my Firefox tabs"
- "Count tabs in Chrome"

✅ **Asks for detailed tab information**
- "What tabs are open?"
- "List my open tabs"
- "Show me my browser tabs"
- "What tabs do I have open in Firefox?"

## Overview

The Browser Tab Checker skill allows Claude Code to:

1. **Count tabs** across Chrome, Chromium, and Firefox
2. **Show details** of each open tab (title and URL)
3. **Filter by browser** to check specific browsers
4. **Multiple output formats** (simple, detailed, JSON)

## How It Works

### Chrome/Chromium Detection

Uses the Chrome DevTools Protocol (CDP):
- Connects to Chrome's debugging port (default: 9222)
- Queries for list of open pages
- Filters to count only actual tabs (not extensions)

**Requirements:**
- Chrome must be started with `--remote-debugging-port=9222`

### Firefox Detection

Reads Firefox session files:
- Locates Firefox profile directories
- Reads session files (handles LZ4 compression)
- Parses session data to count tabs

**Requirements:**
- Firefox must be running or have recent session files

## Usage Examples

### Example 1: Simple Tab Count

**User:** "How many browser tabs do I have open?"

**Claude Response:**
```
I'll check your browser tabs.

Browser Tab Count
==================================================
Chrome               12 tabs
Firefox               8 tabs
--------------------------------------------------
Total                20 tabs

You have 20 tabs open across Chrome and Firefox.
```

### Example 2: Detailed Tab Information

**User:** "Show me what tabs are open in Chrome"

**Claude Response:**
```
I'll show you the details of your Chrome tabs.

Chrome Tabs (12 total):
======================================================================

  [1]
      Title: GitHub - anthropics/claude-code
      URL:   https://github.com/anthropics/claude-code

  [2]
      Title: Python Documentation
      URL:   https://docs.python.org/3/

  [3]
      Title: Stack Overflow
      URL:   https://stackoverflow.com/

...
```

### Example 3: Specific Browser

**User:** "How many Firefox tabs are open?"

**Claude Response:**
```
I'll check your Firefox tabs.

Firefox tabs open: 8

You have 8 tabs open in Firefox.
```

## Workflow

When this skill is activated, Claude should:

1. **Determine the request type:**
   - Simple count vs detailed information
   - All browsers vs specific browser
   - Output format preference

2. **Execute the appropriate script:**
   - For simple count: `python browser_tabs.py`
   - For detailed info: `python browser_tabs.py -v`
   - For specific browser: `python browser_tabs.py --browser chrome|firefox`
   - For JSON: `python browser_tabs.py --json`

3. **Parse and present results:**
   - Extract tab counts and details
   - Format in a user-friendly way
   - Provide context and interpretation

4. **Handle errors gracefully:**
   - If Chrome not accessible: Explain need for `--remote-debugging-port`
   - If Firefox not found: Explain profile requirements
   - If no browsers: Inform user no browsers are currently running

## Commands

### Basic Commands

**Check all browsers (simple):**
```bash
cd /home/user/agent-skill-creator/browser-tab-checker/scripts
python browser_tabs.py
```

**Check all browsers (detailed):**
```bash
cd /home/user/agent-skill-creator/browser-tab-checker/scripts
python browser_tabs.py -v
```

**Check specific browser:**
```bash
cd /home/user/agent-skill-creator/browser-tab-checker/scripts
python browser_tabs.py --browser chrome
python browser_tabs.py --browser firefox
```

**JSON output:**
```bash
cd /home/user/agent-skill-creator/browser-tab-checker/scripts
python browser_tabs.py --json
```

### Individual Browser Scripts

**Chrome only:**
```bash
cd /home/user/agent-skill-creator/browser-tab-checker/scripts
python check_chrome_tabs.py
python check_chrome_tabs.py -v  # Verbose
```

**Firefox only:**
```bash
cd /home/user/agent-skill-creator/browser-tab-checker/scripts
python check_firefox_tabs.py
python check_firefox_tabs.py -v  # Verbose
```

## Error Handling

### Chrome Not Accessible

**Error:** "Chrome DevTools Protocol port not found"

**Claude Response:**
```
Chrome is not currently accessible for tab counting. To enable tab checking for Chrome,
you need to start Chrome with remote debugging enabled:

google-chrome --remote-debugging-port=9222

Or create an alias:
alias chrome-debug='google-chrome --remote-debugging-port=9222'

Note: Only enable this on localhost for security reasons.
```

### Firefox Not Found

**Error:** "No Firefox profiles found"

**Claude Response:**
```
Firefox profiles were not found on your system. This could mean:
1. Firefox is not installed
2. Firefox has never been run (no profile created)
3. Firefox is installed in a non-standard location

If Firefox is installed, try running it once to create a profile.
```

### No Session Files

**Error:** "Could not read Firefox session files"

**Claude Response:**
```
Firefox session files could not be read. This usually means:
1. Firefox is not currently running
2. Firefox was recently closed and session hasn't been saved

Try starting Firefox and then checking again.
```

## Response Templates

### Successful Count

```
I checked your browser tabs:

{Browser} has {count} tabs open
{Browser} has {count} tabs open

Total: {total} tabs across all browsers
```

### Detailed Listing

```
Here are your open tabs in {Browser}:

Window 1:
  1. {Title}
     {URL}
  2. {Title}
     {URL}
...

You have {count} tabs total in {Browser}.
```

### Error Response

```
I attempted to check your browser tabs, but {browser} is not currently accessible.

{Helpful explanation and instructions}

Would you like me to:
- Provide instructions to enable browser tab checking?
- Check a different browser?
- Help with something else?
```

## Browser Setup Instructions

### Chrome/Chromium Setup

To enable tab checking for Chrome:

**Temporary (current session):**
```bash
google-chrome --remote-debugging-port=9222
```

**Permanent (alias method):**
```bash
# Add to ~/.bashrc or ~/.zshrc
alias chrome-debug='google-chrome --remote-debugging-port=9222'

# Then use
chrome-debug
```

**Permanent (desktop launcher):**
Edit `~/.local/share/applications/google-chrome.desktop`:
```ini
Exec=/usr/bin/google-chrome --remote-debugging-port=9222 %U
```

**Security Note:** Only enable remote debugging on localhost. Never expose the debugging port to the network.

### Firefox Setup

Firefox requires no special setup. The tool automatically:
1. Finds Firefox profile directories
2. Reads session files
3. Handles compression (LZ4)
4. Counts tabs across all windows

Just make sure Firefox is running or was recently running.

## Technical Details

### Architecture

```
browser-tab-checker/
├── scripts/
│   ├── browser_tabs.py           # Main unified interface
│   ├── check_chrome_tabs.py      # Chrome/Chromium counter
│   └── check_firefox_tabs.py     # Firefox counter
├── .claude-plugin/
│   └── marketplace.json          # Plugin configuration
├── references/
│   └── troubleshooting.md        # Detailed troubleshooting
└── README.md                      # Documentation
```

### Dependencies

- **Python 3.8+**
- **lz4** (for Firefox session file decompression)

All dependencies are installed via:
```bash
pip install -r browser-tab-checker/requirements.txt
```

### Supported Browsers

| Browser | Status | Method |
|---------|--------|--------|
| Chrome | ✅ Supported | Chrome DevTools Protocol |
| Chromium | ✅ Supported | Chrome DevTools Protocol |
| Firefox | ✅ Supported | Session file reading |
| Brave | 🔄 Planned | Chrome DevTools Protocol |
| Edge | 🔄 Planned | Chrome DevTools Protocol |

## Privacy and Security

### Data Handled

The tool reads:
- Tab titles
- Tab URLs
- Tab counts

**Important:** Tab information may contain sensitive data (passwords in URLs, private information in titles). Handle with care.

### Security Considerations

1. **Chrome Remote Debugging:**
   - Only enable on localhost (127.0.0.1)
   - Never expose port 9222 to the network
   - Disable when not needed

2. **Firefox Session Files:**
   - Read-only access (no modifications)
   - Files contain full browsing history
   - Located in user's home directory

3. **Output:**
   - Verbose mode shows full URLs and titles
   - Be careful sharing this information
   - Use simple mode for privacy

## Troubleshooting

For detailed troubleshooting, refer to:
```bash
cat /home/user/agent-skill-creator/browser-tab-checker/references/troubleshooting.md
```

Common issues:
- Chrome not accessible → Start with `--remote-debugging-port=9222`
- Firefox profiles not found → Ensure Firefox is installed and has been run
- Session files not readable → Start Firefox and wait a few seconds
- Module not found → Install dependencies with `pip install -r requirements.txt`

## Performance

- **Chrome:** Very fast (<0.5s) - Uses HTTP API
- **Firefox:** Fast (~1s) - Reads local files
- **Multiple browsers:** Sequential checking

## Limitations

1. **Linux only** (currently)
2. **Chrome requires special startup flag**
3. **Firefox private tabs not counted** (not in session files)
4. **Incognito tabs not counted** (not in session files)
5. **Browser must be running** (or recently closed for Firefox)

## Future Enhancements

Potential improvements:
- [ ] Windows support
- [ ] macOS support
- [ ] Brave browser support
- [ ] Edge browser support
- [ ] Tab filtering (by domain, title)
- [ ] Tab organization features
- [ ] Tab statistics and analytics

## Keywords for Activation

This skill should activate when detecting:

**Question words:**
- "How many"
- "Count"
- "Check"
- "Show"
- "List"
- "What"

**Combined with:**
- "tabs"
- "browser tabs"
- "open tabs"
- "Chrome tabs"
- "Firefox tabs"
- "browser windows"

**Example phrases:**
- "How many tabs do I have open?"
- "Count my browser tabs"
- "Check tabs in Chrome"
- "Show me open tabs"
- "List Firefox tabs"
- "What tabs are open?"
- "How many Chrome tabs?"
- "Count tabs"

## Integration with Other Skills

This skill can complement:
- **Productivity tracking** - Monitor tab overload
- **Browser automation** - Identify what's currently open
- **System monitoring** - Track browser resource usage
- **Session management** - Understand current browsing context

## Best Practices

When using this skill, Claude should:

1. **Be conversational:** Present results in a friendly, natural way
2. **Provide context:** Explain what the numbers mean
3. **Offer insights:** Comment on tab counts (e.g., "That's quite a few tabs!")
4. **Handle errors gracefully:** Provide helpful setup instructions
5. **Respect privacy:** Be mindful of sensitive information in tab details
6. **Suggest actions:** Offer to help close tabs, organize, etc.

## Version

- **Version:** 1.0.0
- **Created:** 2025-10-21
- **Last Updated:** 2025-10-21
- **Platform:** Linux
- **Python:** 3.8+

## License

Apache 2.0

## Credits

Created as part of the agent-skill-creator project.
