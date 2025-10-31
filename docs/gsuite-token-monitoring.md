# GSuite MCP Token Monitoring System

**Created:** 2025-10-15
**Status:** ✅ Ready to Deploy

---

## Overview

Automated monitoring system for GSuite MCP OAuth tokens to prevent authentication failures due to expired refresh tokens. The system checks token expiry every 6 hours and sends macOS notifications when re-authentication is needed.

---

## Components

### 1. Token Check Script
**Location**: `/Users/gavinslater/projects/life/scripts/check-gsuite-token.py`

**Features**:
- Checks OAuth token expiry status
- Warns when token expires in less than 2 days
- Sends macOS notifications (optional)
- Exit codes for automation (0=OK, 1=Warning, 2=Expired)

**Usage**:
```bash
# Check status and display in terminal
python3 ~/projects/life/scripts/check-gsuite-token.py

# Check and send notification if expiring soon
python3 ~/projects/life/scripts/check-gsuite-token.py --notify

# Quiet mode (only notifications, no terminal output)
python3 ~/projects/life/scripts/check-gsuite-token.py --notify --quiet
```

### 2. LaunchAgent Configuration
**Location**: `/Users/gavinslater/Library/LaunchAgents/com.gavinslater.gsuite-token-monitor.plist`

**Schedule**: Every 6 hours (21600 seconds)

**Behavior**:
- Runs automatically in the background
- Sends notifications when token is expiring soon
- Logs output to: `~/Library/Logs/gsuite-token-monitor.log`

---

## Installation & Setup

### Step 1: Verify Script Works

Test the monitoring script manually:

```bash
# Test the script
python3 ~/projects/life/scripts/check-gsuite-token.py

# Test with notification
python3 ~/projects/life/scripts/check-gsuite-token.py --notify
```

Expected output:
- ✅ Green checkmark: Token is valid
- 🟡 Yellow warning: Token expiring soon (< 2 days)
- 🔴 Red alert: Token expired

### Step 2: Load LaunchAgent

Enable automatic monitoring:

```bash
# Load the LaunchAgent (starts monitoring)
launchctl load ~/Library/LaunchAgents/com.gavinslater.gsuite-token-monitor.plist

# Verify it's loaded
launchctl list | grep gsuite-token-monitor
```

Expected output: You should see `com.gavinslater.gsuite-token-monitor` in the list.

### Step 3: Verify Logs

Check that logging is working:

```bash
# View the log file
tail -f ~/Library/Logs/gsuite-token-monitor.log
```

The log will be empty until the first scheduled run (or you can trigger it manually - see below).

---

## Management Commands

### Check Service Status

```bash
# List the service
launchctl list | grep gsuite-token-monitor

# View recent log entries
tail -20 ~/Library/Logs/gsuite-token-monitor.log
```

### Manual Trigger (Test)

Trigger a check immediately without waiting for the schedule:

```bash
# Trigger the service now
launchctl start com.gavinslater.gsuite-token-monitor

# View the result
tail -5 ~/Library/Logs/gsuite-token-monitor.log
```

### Stop/Start Monitoring

```bash
# Stop monitoring (unload)
launchctl unload ~/Library/LaunchAgents/com.gavinslater.gsuite-token-monitor.plist

# Start monitoring (load)
launchctl load ~/Library/LaunchAgents/com.gavinslater.gsuite-token-monitor.plist

# Restart monitoring (reload)
launchctl unload ~/Library/LaunchAgents/com.gavinslater.gsuite-token-monitor.plist
launchctl load ~/Library/LaunchAgents/com.gavinslater.gsuite-token-monitor.plist
```

### Update Configuration

If you modify the plist file:

```bash
# Reload the configuration
launchctl unload ~/Library/LaunchAgents/com.gavinslater.gsuite-token-monitor.plist
launchctl load ~/Library/LaunchAgents/com.gavinslater.gsuite-token-monitor.plist
```

---

## Notification Behavior

### When Token is Valid
- ✅ No notification sent
- Script runs silently in background
- Logged to file for reference

### When Token Expires in < 2 Days
- 🟡 Notification: "GSuite Token Expiring Soon"
- Message includes time remaining
- Sound alert: "Glass"
- Appears in macOS Notification Center

### When Token is Expired
- 🔴 Notification: "GSuite Token Expired"
- Urgent message about lost email access
- Sound alert: "Glass"
- Appears in macOS Notification Center

---

## Re-authentication Process

When you receive a notification that the token is expiring:

### Option 1: Quick Re-authentication

```bash
cd ~/mcp-gsuite-test
uvx mcp-gsuite --gauth-file ./credentials/.gauth.json
```

This will:
1. Open your browser
2. Prompt for Google sign-in (gavin.n.slater@gmail.com)
3. Request permission grants
4. Save new tokens automatically
5. Reset the 7-day expiry timer

### Option 2: Test First, Then Re-authenticate

```bash
# Check current status
python3 ~/projects/life/scripts/check-gsuite-token.py

# If expiring soon, re-authenticate
cd ~/mcp-gsuite-test && uvx mcp-gsuite --gauth-file ./credentials/.gauth.json
```

---

## Configuration Options

### Change Check Frequency

Edit the plist file and modify `StartInterval` (in seconds):

```xml
<key>StartInterval</key>
<integer>21600</integer>  <!-- 6 hours = 21600 seconds -->
```

Recommended intervals:
- **21600** (6 hours) - Default, good balance
- **43200** (12 hours) - Less frequent, still safe
- **86400** (24 hours) - Daily check, minimal overhead
- **3600** (1 hour) - Aggressive monitoring (not recommended)

### Change Warning Threshold

Edit the script and modify `WARNING_DAYS`:

```python
WARNING_DAYS = 2  # Warn when token expires in less than 2 days
```

Recommended values:
- **2 days** - Default, good advance warning
- **1 day** - Less advance notice
- **3 days** - Maximum advance warning

### Disable Notifications

To check tokens without notifications, modify the plist:

```xml
<key>ProgramArguments</key>
<array>
    <string>/usr/bin/python3</string>
    <string>/Users/gavinslater/projects/life/scripts/check-gsuite-token.py</string>
    <!-- Remove the --notify flag -->
</array>
```

---

## Troubleshooting

### Issue: LaunchAgent not running

**Check if loaded**:
```bash
launchctl list | grep gsuite-token-monitor
```

**If not listed**:
```bash
launchctl load ~/Library/LaunchAgents/com.gavinslater.gsuite-token-monitor.plist
```

### Issue: No notifications appearing

**Test manually**:
```bash
python3 ~/projects/life/scripts/check-gsuite-token.py --notify
```

**Check macOS notification settings**:
1. System Settings → Notifications
2. Find "Script Editor" or "Python"
3. Ensure notifications are allowed

### Issue: Script errors in log

**View errors**:
```bash
cat ~/Library/Logs/gsuite-token-monitor.log
```

**Common issues**:
- Token file not found → Check path in script
- Python not found → Check shebang line in script
- Permission denied → Check script is executable: `chmod +x ~/projects/life/scripts/check-gsuite-token.py`

### Issue: Token file path wrong

If you move the token files, update the script:

```python
# Edit this line in check-gsuite-token.py
TOKEN_FILE = Path.home() / "mcp-gsuite-test/credentials/.oauth2.gavin.n.slater@gmail.com.json"
```

---

## Monitoring Dashboard

### Quick Status Check

Create an alias in your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
alias gsuite-token='python3 ~/projects/life/scripts/check-gsuite-token.py'
```

Then simply run:
```bash
gsuite-token
```

### Check Service Health

```bash
# One-liner to check everything
echo "=== LaunchAgent Status ===" && \
launchctl list | grep gsuite-token-monitor && \
echo -e "\n=== Recent Logs ===" && \
tail -5 ~/Library/Logs/gsuite-token-monitor.log
```

---

## Integration with Other Systems

### Add to Daily Journal

You can call the script from your daily journal slash command:

```bash
python3 ~/projects/life/scripts/check-gsuite-token.py --quiet
```

### Add to Weekly Review

Include token status check in your GTD weekly review routine.

### Email Alert (Advanced)

Modify the script to send email alerts instead of notifications (requires SMTP setup).

---

## File Locations Reference

| Component | Location |
|-----------|----------|
| **Monitoring Script** | `/Users/gavinslater/projects/life/scripts/check-gsuite-token.py` |
| **LaunchAgent Config** | `/Users/gavinslater/Library/LaunchAgents/com.gavinslater.gsuite-token-monitor.plist` |
| **Log File** | `/Users/gavinslater/Library/Logs/gsuite-token-monitor.log` |
| **Token File** | `/Users/gavinslater/mcp-gsuite-test/credentials/.oauth2.gavin.n.slater@gmail.com.json` |

---

## Security Notes

- ✅ Script runs with your user permissions (not root)
- ✅ Token file permissions remain unchanged
- ✅ Script only reads token file (no modifications)
- ✅ Notifications contain no sensitive data
- ✅ Logs contain no credentials (only status messages)

---

## Maintenance

### After System Updates

macOS updates may reset LaunchAgents. After updates:

```bash
# Reload the service
launchctl load ~/Library/LaunchAgents/com.gavinslater.gsuite-token-monitor.plist
```

### Log Rotation

The log file grows over time. Rotate it occasionally:

```bash
# Archive old logs
mv ~/Library/Logs/gsuite-token-monitor.log ~/Library/Logs/gsuite-token-monitor.log.old

# Service will create new log automatically
```

---

**End of Documentation**

*This monitoring system ensures you never lose GSuite MCP access due to expired tokens.*
