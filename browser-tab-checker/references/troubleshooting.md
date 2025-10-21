# Browser Tab Checker - Troubleshooting Guide

This guide covers common issues and solutions when using the Browser Tab Checker tool.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Chrome/Chromium Issues](#chromechromium-issues)
3. [Firefox Issues](#firefox-issues)
4. [General Issues](#general-issues)
5. [Claude Code Integration Issues](#claude-code-integration-issues)

---

## Installation Issues

### ModuleNotFoundError: No module named 'lz4'

**Error Message:**
```
ModuleNotFoundError: No module named 'lz4'
```

**Cause:** The required Python packages are not installed.

**Solution:**
```bash
cd browser-tab-checker
pip install -r requirements.txt
```

**Alternative (install directly):**
```bash
pip install lz4
```

### Permission Denied When Running Scripts

**Error Message:**
```
Permission denied: ./scripts/browser_tabs.py
```

**Solution:**
```bash
# Make scripts executable
chmod +x scripts/*.py

# Or run with python explicitly
python scripts/browser_tabs.py
```

---

## Chrome/Chromium Issues

### Chrome DevTools Protocol Port Not Found

**Error Message:**
```
Error: Chrome DevTools Protocol port not found. Is Chrome running with --remote-debugging-port?
```

**Cause:** Chrome is not running with remote debugging enabled.

**Solution:**

**Option 1: Start Chrome with debugging (temporary)**
```bash
google-chrome --remote-debugging-port=9222
```

**Option 2: Create an alias (permanent)**

Add to `~/.bashrc` or `~/.zshrc`:
```bash
alias chrome-debug='google-chrome --remote-debugging-port=9222'
```

Then run:
```bash
source ~/.bashrc  # or ~/.zshrc
chrome-debug
```

**Option 3: Modify Chrome launcher**

Edit `~/.local/share/applications/google-chrome.desktop`:
```ini
[Desktop Entry]
Exec=/usr/bin/google-chrome --remote-debugging-port=9222 %U
```

**Security Warning:** Only use `--remote-debugging-port` on localhost. Never expose this port to the network.

### Failed to Connect to Chrome at localhost:9222

**Error Message:**
```
Error: Failed to connect to Chrome at localhost:9222
```

**Possible Causes:**
1. Chrome is not running
2. Chrome is running on a different port
3. Firewall is blocking the connection
4. Chrome didn't start debugging server

**Solutions:**

**Check if Chrome is listening on the port:**
```bash
netstat -tuln | grep 9222
# or
ss -tuln | grep 9222
```

**Try different ports:**
```bash
# Check ports 9222, 9223, 9224
for port in 9222 9223 9224; do
    curl -s http://localhost:$port/json | head -n 1
done
```

**Restart Chrome with debugging:**
```bash
# Close all Chrome instances
killall chrome

# Start with debugging
google-chrome --remote-debugging-port=9222
```

### Chrome Shows No Tabs (Count is 0)

**Possible Causes:**
1. Chrome is running but no tabs are open
2. Only background pages/extensions are open
3. You're checking the wrong Chrome instance

**Solutions:**

**Verify manually:**
```bash
curl http://localhost:9222/json | python -m json.tool
```

Look for entries with `"type": "page"`.

**Check all possible ports:**
```bash
python scripts/browser_tabs.py --browser chrome -v
```

### Using Chrome in Headless Mode

**Issue:** Headless Chrome might not expose tabs the same way.

**Solution:** Use regular Chrome or Chromium for tab counting. Headless mode is not recommended for this use case.

---

## Firefox Issues

### No Firefox Profiles Found

**Error Message:**
```
Error: No Firefox profiles found
```

**Possible Causes:**
1. Firefox is not installed
2. Firefox has never been run (no profile created)
3. Firefox is installed in a non-standard location
4. Using Firefox Flatpak

**Solutions:**

**Verify Firefox installation:**
```bash
which firefox
firefox --version
```

**Check profile locations:**
```bash
ls -la ~/.mozilla/firefox/
ls -la ~/.var/app/org.mozilla.firefox/.mozilla/firefox/  # Flatpak
```

**Create a profile if needed:**
```bash
firefox -CreateProfile "default"
```

**For Flatpak Firefox:**

The tool should automatically check Flatpak locations. If it doesn't work, check:
```bash
flatpak list | grep firefox
```

### Could Not Read Firefox Session Files

**Error Message:**
```
Error: Could not read Firefox session files. Is Firefox running?
```

**Possible Causes:**
1. Firefox is not running (and no recent session saved)
2. Session files are corrupted
3. Permission issues
4. Session files don't exist

**Solutions:**

**Start Firefox:**
```bash
firefox &
# Wait a few seconds, then run the checker
python scripts/browser_tabs.py --browser firefox
```

**Check session files manually:**
```bash
# Find your profile
cd ~/.mozilla/firefox/

# List profiles
ls -d *.default* *.default-release*

# Check for session files
cd YOUR_PROFILE_NAME
ls -la sessionstore*
ls -la sessionstore-backups/
```

**Check file permissions:**
```bash
# Session files should be readable
ls -l sessionstore.jsonlz4
# If not readable:
chmod 644 sessionstore.jsonlz4
```

**Backup and recovery:**

If session files are corrupted, Firefox keeps backups:
```bash
cd ~/.mozilla/firefox/YOUR_PROFILE/sessionstore-backups/
ls -la
# Try recovery files:
# - recovery.jsonlz4
# - previous.jsonlz4
# - upgrade.jsonlz4
```

### Firefox Tab Count Seems Wrong

**Possible Causes:**
1. Multiple Firefox profiles are open
2. Private browsing windows (not saved in session)
3. Session restore disabled

**Solutions:**

**Check for multiple profiles:**
```bash
ps aux | grep firefox
```

**Enable session restore:**

In Firefox:
1. Go to `about:preferences`
2. Search for "session"
3. Enable "Restore previous session"

**Note:** Private browsing tabs are not saved to session files and won't be counted.

### LZ4 Decompression Errors

**Error Message:**
```
Error during LZ4 decompression
```

**Cause:** Session file format is not recognized or corrupted.

**Solutions:**

**Update lz4 package:**
```bash
pip install --upgrade lz4
```

**Try with a different session file:**
```bash
cd ~/.mozilla/firefox/YOUR_PROFILE/sessionstore-backups/
# Check different backup files
```

**Create a fresh session:**
```bash
# Close Firefox completely
killall firefox

# Remove session files (Firefox will create new ones)
mv sessionstore.jsonlz4 sessionstore.jsonlz4.bak

# Start Firefox and open some tabs
firefox &

# Wait a few seconds, then check
python scripts/browser_tabs.py --browser firefox
```

---

## General Issues

### No Tabs Found (Total Count is 0)

**Possible Causes:**
1. No browsers are running
2. Browsers are running but not configured correctly
3. Browser versions not supported

**Solutions:**

**Check running browsers:**
```bash
ps aux | grep -E "(chrome|firefox)" | grep -v grep
```

**Test each browser individually:**
```bash
python scripts/check_chrome_tabs.py
python scripts/check_firefox_tabs.py
```

**Verify browser configurations:**
- Chrome: Check remote debugging is enabled
- Firefox: Check session files exist

### Import Error for Browser Scripts

**Error Message:**
```
ModuleNotFoundError: No module named 'check_chrome_tabs'
```

**Cause:** Scripts are not in the Python path.

**Solution:**

**Run from the scripts directory:**
```bash
cd browser-tab-checker/scripts
python browser_tabs.py
```

**Or add to Python path:**
```bash
cd browser-tab-checker
PYTHONPATH=scripts python scripts/browser_tabs.py
```

### JSON Output is Malformed

**Issue:** JSON output doesn't parse correctly.

**Solution:**

Ensure you're using the `--json` flag:
```bash
python scripts/browser_tabs.py --json | python -m json.tool
```

**Redirect to file:**
```bash
python scripts/browser_tabs.py --json > tabs.json
cat tabs.json | python -m json.tool
```

---

## Claude Code Integration Issues

### Skill Not Found After Installation

**Issue:** `/plugin list` doesn't show browser-tab-checker.

**Solutions:**

**Verify marketplace.json exists:**
```bash
cat browser-tab-checker/.claude-plugin/marketplace.json
```

**Reinstall the skill:**
```bash
/plugin marketplace remove browser-tab-checker
/plugin marketplace add ./browser-tab-checker
```

**Check Claude Code plugin directory:**
```bash
ls -la ~/.claude/plugins/
```

### Skill Doesn't Activate Automatically

**Issue:** Asking about tabs doesn't trigger the skill.

**Possible Causes:**
1. Skill description keywords don't match query
2. Another skill is taking precedence
3. Skill is not properly installed

**Solutions:**

**Be explicit in your query:**
```
"Use the browser-tab-checker skill to count my tabs"
"Check browser tabs"
"How many browser tabs are open?"
```

**Verify skill is enabled:**
```bash
/plugin list
```

**Check skill description:**
```bash
cat browser-tab-checker/.claude-plugin/marketplace.json
```

### Python Dependencies Not Found in Claude Code

**Issue:** Skill runs but fails due to missing dependencies.

**Solution:**

Install dependencies in the correct Python environment:
```bash
# Find which Python Claude Code uses
which python3

# Install dependencies
pip3 install -r browser-tab-checker/requirements.txt

# Or use absolute path
/usr/bin/python3 -m pip install -r browser-tab-checker/requirements.txt
```

---

## Platform-Specific Issues

### Linux-Specific

**Wayland vs X11:**

Some browser features might behave differently on Wayland. If issues persist, try running on X11:
```bash
# Force X11
export GDK_BACKEND=x11
google-chrome --remote-debugging-port=9222
```

**Snap/Flatpak Browsers:**

Snap and Flatpak browsers have isolated filesystems. The tool includes support for Flatpak Firefox, but Snap browsers might require additional configuration.

---

## Debugging Tips

### Enable Verbose Output

Get more details about what's happening:
```bash
python scripts/browser_tabs.py -v
```

### Test Individual Components

**Test Chrome connection:**
```bash
curl http://localhost:9222/json
```

**Test Firefox session files:**
```bash
python3 -c "
import pathlib
firefox_dir = pathlib.Path.home() / '.mozilla' / 'firefox'
print('Firefox directory:', firefox_dir)
print('Exists:', firefox_dir.exists())
if firefox_dir.exists():
    profiles = [d for d in firefox_dir.iterdir() if d.is_dir()]
    print('Profiles:', profiles)
"
```

### Check Python Version

```bash
python --version
# Should be 3.8 or higher
```

### Check Network Connectivity (Chrome)

```bash
# Test if localhost resolves correctly
ping -c 1 localhost

# Test if port is accessible
telnet localhost 9222
# or
nc -zv localhost 9222
```

---

## Getting Help

If you're still experiencing issues:

1. **Collect information:**
   ```bash
   # System info
   uname -a
   python --version

   # Browser info
   google-chrome --version
   firefox --version

   # Script output
   python scripts/browser_tabs.py -v 2>&1 | tee debug.log
   ```

2. **Check logs:**
   - Chrome logs: Check `~/.config/google-chrome/`
   - Firefox logs: Check `about:support` in Firefox

3. **Create an issue:**
   - Include the collected information
   - Describe what you expected vs what happened
   - Include any error messages

---

## Quick Reference

### Common Commands

```bash
# Simple check
python scripts/browser_tabs.py

# Detailed view
python scripts/browser_tabs.py -v

# JSON output
python scripts/browser_tabs.py --json

# Check specific browser
python scripts/browser_tabs.py --browser chrome
python scripts/browser_tabs.py --browser firefox

# Start Chrome with debugging
google-chrome --remote-debugging-port=9222

# Check Chrome debugging is working
curl http://localhost:9222/json
```

### Important File Locations

- **Chrome session:** `~/.config/google-chrome/`
- **Firefox profiles:** `~/.mozilla/firefox/`
- **Firefox Flatpak:** `~/.var/app/org.mozilla.firefox/.mozilla/firefox/`
- **Session files:** `sessionstore.jsonlz4`, `sessionstore.js`
- **Session backups:** `sessionstore-backups/`

### Environment Variables

```bash
# Force X11 (if using Wayland)
export GDK_BACKEND=x11

# Custom Chrome debugging port
export CHROME_DEBUG_PORT=9222
```

---

**Last Updated:** 2025-10-21
**Version:** 1.0.0
