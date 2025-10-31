# GSuite MCP Server Setup Guide

**Last Updated:** 2025-10-15
**Author:** Gavin Slater
**Status:** ✅ Production - Active and Working

---

## 📋 Overview

The GSuite MCP server (`mcp-gsuite`) provides Gmail and Google Calendar integration for both **Claude Desktop** and **Claude Code**. This document serves as the definitive reference for the current production setup.

### Current Status
- ✅ **Working**: Successfully retrieving emails and calendar events
- ✅ **Configured**: Single source of truth in `/mcp-gsuite-test/`
- ✅ **Secured**: Credentials protected via `.gitignore`
- ✅ **Integrated**: Seamlessly shared between Claude Desktop and Claude Code

---

## 🏗️ Architecture Overview

### MCP Server
- **Package**: `mcp-gsuite` (Python-based)
- **Installation**: Managed via `uvx` (uv package manager)
- **Protocol**: Model Context Protocol (MCP)

### Integration Points
1. **Claude Desktop** (macOS app) - Primary configuration
2. **Claude Code** (VS Code extension) - Inherits Desktop configuration
3. **Email Management Agent** - Specialized sub-agent using Gmail MCP tools

### How Configuration Sharing Works
- Claude Code **does NOT** have its own MCP configuration file
- Claude Code **inherits** all MCP servers from Claude Desktop's configuration
- Both applications use the **same** `claude_desktop_config.json` file
- Configuration changes apply to both applications simultaneously

---

## 📁 Configuration Files

### 1. MCP Server Configuration

**Location**: `/Users/gavinslater/Library/Application Support/Claude/claude_desktop_config.json`

**MCP Gsuite Section**:
```json
{
  "mcpServers": {
    "mcp-gsuite": {
      "command": "uvx",
      "args": [
        "mcp-gsuite",
        "--gauth-file",
        "/Users/gavinslater/mcp-gsuite-test/credentials/.gauth.json",
        "--oauth2-dir",
        "/Users/gavinslater/mcp-gsuite-test/credentials",
        "--credentials-dir",
        "/Users/gavinslater/mcp-gsuite-test/credentials",
        "--accounts-file",
        "/Users/gavinslater/mcp-gsuite-test/.accounts.json"
      ]
    }
  }
}
```

**Note**: This configuration file also contains other MCP servers (filesystem, obsidian, github, etc.)

---

### 2. Authentication Files

**Base Directory**: `/Users/gavinslater/mcp-gsuite-test/`

#### File Structure
```
/Users/gavinslater/mcp-gsuite-test/
├── .accounts.json                                      # Account configuration
└── credentials/
    ├── .gauth.json                                     # OAuth client credentials
    └── .oauth2.gavin.n.slater@gmail.com.json          # Access/refresh tokens
```

#### `.accounts.json`
**Purpose**: Defines which Google accounts to access
**Location**: `/Users/gavinslater/mcp-gsuite-test/.accounts.json`

```json
{
  "accounts": [
    {
      "email": "gavin.n.slater@gmail.com",
      "account_type": "personal",
      "extra_info": "Contains personal email and Calendar"
    }
  ]
}
```

#### `.gauth.json`
**Purpose**: OAuth client credentials from Google Cloud Console
**Location**: `/Users/gavinslater/mcp-gsuite-test/credentials/.gauth.json`

```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["http://localhost:4100/code"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  }
}
```

**Client Type**: `installed` (desktop application)

#### `.oauth2.gavin.n.slater@gmail.com.json`
**Purpose**: OAuth access and refresh tokens
**Location**: `/Users/gavinslater/mcp-gsuite-test/credentials/.oauth2.gavin.n.slater@gmail.com.json`

```json
{
  "access_token": "ya29...[token]",
  "expires_in": 3599,
  "refresh_token": "1//03AT1q...[token]",
  "scope": "https://www.googleapis.com/auth/calendar.readonly https://www.googleapis.com/auth/gmail.readonly",
  "token_type": "Bearer",
  "refresh_token_expires_in": 604799,
  "token_expiry": "2025-10-15T11:36:38.717906Z"
}
```

**Granted Permissions**:
- ✅ `gmail.readonly` - Read Gmail messages
- ✅ `calendar.readonly` - Read calendar events

**Token Lifecycle**:
- Access token: Valid for **1 hour** (3599 seconds)
- Refresh token: Valid for **7 days** (604799 seconds from last use)
- Auto-refresh: MCP server automatically refreshes access tokens

---

### 3. Git Security

**`.gitignore` Protection**
**Location**: `/Users/gavinslater/projects/life/.gitignore`

```
# MCP GSuite OAuth credentials - keep these secure!
.gauth.json
.accounts.json
.oauth2.*.json
```

This ensures OAuth credentials are never committed to version control.

---

## 📊 Configuration Summary

| Component | Location | Owner | Purpose |
|-----------|----------|-------|---------|
| **MCP Config** | `/Users/gavinslater/Library/Application Support/Claude/claude_desktop_config.json` | `gavinslater` | Server configuration (shared) |
| **OAuth Client** | `/Users/gavinslater/mcp-gsuite-test/credentials/.gauth.json` | `gavinslater` | Google Cloud credentials |
| **OAuth Tokens** | `/Users/gavinslater/mcp-gsuite-test/credentials/.oauth2.*.json` | `gavinslater` | Access/refresh tokens |
| **Accounts** | `/Users/gavinslater/mcp-gsuite-test/.accounts.json` | `gavinslater` | Account list |

---

## 🛠️ Maintenance Procedures

### Check Token Status

```bash
# Check current token expiry
python3 -c "
from datetime import datetime
import json

with open('/Users/gavinslater/mcp-gsuite-test/credentials/.oauth2.gavin.n.slater@gmail.com.json') as f:
    token = json.load(f)

expiry = datetime.fromisoformat(token['token_expiry'].replace('Z', '+00:00'))
now = datetime.now(expiry.tzinfo)

print(f'Token expired: {now > expiry}')
print(f'Expiry: {expiry}')
print(f'Time until expiry: {expiry - now}')
"
```

### Manual Re-authentication

If tokens expire or authentication fails:

```bash
# Navigate to credentials directory
cd /Users/gavinslater/mcp-gsuite-test

# Run manual authentication
uvx mcp-gsuite --gauth-file ./credentials/.gauth.json

# Browser will open - sign in with gavin.n.slater@gmail.com
# Grant permissions when prompted
# New tokens saved automatically to credentials/.oauth2.*.json
```

### Test MCP Server

```bash
# Test the server can start and authenticate
uvx mcp-gsuite \
  --gauth-file /Users/gavinslater/mcp-gsuite-test/credentials/.gauth.json \
  --oauth2-dir /Users/gavinslater/mcp-gsuite-test/credentials \
  --credentials-dir /Users/gavinslater/mcp-gsuite-test/credentials \
  --accounts-file /Users/gavinslater/mcp-gsuite-test/.accounts.json

# Should start without errors
# Press Ctrl+C to exit
```

### Verify File Permissions

```bash
# Check all files are owned by gavinslater
ls -la /Users/gavinslater/mcp-gsuite-test/credentials/

# Expected output (all owned by gavinslater:staff):
# -rw-r--r--  1 gavinslater  staff  .gauth.json
# -rw-r--r--  1 gavinslater  staff  .oauth2.gavin.n.slater@gmail.com.json
```

---

## 🚨 Troubleshooting

### Issue: "Authentication failed" errors

**Symptoms**: MCP server can't access Gmail/Calendar

**Solutions**:
1. Check token expiry: Run "Check Token Status" command above
2. Re-authenticate: Run "Manual Re-authentication" procedure
3. Verify file permissions: Ensure all auth files readable by your user
4. Check Google OAuth consent: Visit [Google Account](https://myaccount.google.com/permissions) and verify app access

### Issue: "No such file or directory" errors

**Symptoms**: MCP server can't find configuration files

**Solutions**:
1. Verify files exist:
   ```bash
   ls -la /Users/gavinslater/mcp-gsuite-test/credentials/.gauth.json
   ls -la /Users/gavinslater/mcp-gsuite-test/.accounts.json
   ```
2. Check `claude_desktop_config.json` for typos in file paths
3. Ensure all paths are **absolute** (start with `/Users/...`)

### Issue: MCP server not starting

**Symptoms**: Gmail tools not available in Claude Desktop/Code

**Solutions**:
1. Restart Claude Desktop completely (Quit and reopen)
2. Restart VS Code if using Claude Code
3. Check Claude Desktop logs: `~/Library/Logs/Claude/`
4. Test server manually (see "Test MCP Server" above)
5. Verify `uvx` installed: `which uvx` (should return path)
6. Reinstall mcp-gsuite: `uvx --reinstall mcp-gsuite`

### Issue: Works in Desktop but not Code (or vice versa)

**Symptoms**: Different behavior between applications

**Solution**:
- This should NOT happen - they share the same configuration
- If it occurs:
  1. Completely quit both applications
  2. Reopen Claude Desktop first, wait for it to fully load
  3. Then open VS Code with Claude Code
  4. Check macOS System Settings > Privacy & Security > Files and Folders
  5. Ensure both apps have necessary file access permissions

### Issue: Token keeps expiring

**Symptoms**: Need to re-authenticate frequently

**Possible Causes**:
1. **7+ days of inactivity**: Refresh token expires after 7 days without use
2. **System clock issues**: Check your Mac's time/timezone settings
3. **Google security**: Account security settings may be revoking tokens

**Solutions**:
- Use the integration at least once every 7 days to keep refresh token active
- Verify system clock: `date` (should match current time)
- Check Google Account security settings for unusual activity

---

## 🔐 Security Best Practices

### Credentials Storage
- ✅ Credentials stored locally (not in cloud)
- ✅ Protected by `.gitignore` (not committed to git)
- ✅ Client secret in plain text (normal for OAuth installed apps)
- ✅ Access tokens auto-expire hourly
- ✅ Refresh tokens expire after 7 days of inactivity

### OAuth Scopes (Current Permissions)
**Read-only access**:
- `gmail.readonly` - Can read but not send/delete emails
- `calendar.readonly` - Can read but not modify calendar

**To Add More Permissions**:
1. Update OAuth client in [Google Cloud Console](https://console.cloud.google.com/)
2. Add new scopes to the OAuth consent screen
3. Delete `.oauth2.*.json` to force re-authentication
4. Run manual re-authentication to grant new permissions

### Credential Compromise Response
If credentials are compromised:
1. Revoke access in [Google Account Permissions](https://myaccount.google.com/permissions)
2. Delete all auth files: `rm /Users/gavinslater/mcp-gsuite-test/credentials/.oauth2.*.json`
3. Create new OAuth client in Google Cloud Console (if client secret exposed)
4. Update `.gauth.json` with new credentials
5. Re-authenticate using manual re-authentication procedure

---

## 📚 Reference Links

### Official Documentation
- **MCP GSuite**: https://github.com/oomol-lab/mcp-gsuite
- **Model Context Protocol**: https://modelcontextprotocol.io/
- **Claude Code MCP**: https://docs.claude.com/en/docs/claude-code/mcp-servers

### Google OAuth Documentation
- **OAuth 2.0 Overview**: https://developers.google.com/identity/protocols/oauth2
- **Gmail API Scopes**: https://developers.google.com/gmail/api/auth/scopes
- **Calendar API Scopes**: https://developers.google.com/calendar/api/auth
- **Google Cloud Console**: https://console.cloud.google.com/

### Internal Documentation
- **UFC System**: `/Users/gavinslater/projects/life/CLAUDE.md`
- **Gmail MCP Context**: `/.claude/context/tools/gmail-mcp-context.md`
- **Email Management Agent**: `/.claude/agents/email-management-agent.md`

---

## 🔄 Token Lifecycle Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  Initial Setup (One-time)                                   │
│  1. Create OAuth client in Google Cloud Console             │
│  2. Download credentials → .gauth.json                      │
│  3. Run: uvx mcp-gsuite --gauth-file .gauth.json            │
│  4. Browser opens → Sign in → Grant permissions             │
│  5. Tokens saved → .oauth2.gavin.n.slater@gmail.com.json    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Normal Operation (Automatic)                               │
│  • Access token valid for 1 hour                            │
│  • MCP server auto-refreshes using refresh token            │
│  • Refresh token valid for 7 days from last use             │
│  • Using the integration resets the 7-day timer             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Re-authentication Required (After 7+ days inactivity)      │
│  1. MCP server reports authentication error                 │
│  2. Run: uvx mcp-gsuite --gauth-file .gauth.json            │
│  3. Browser opens → Sign in → Grant permissions             │
│  4. New tokens saved                                        │
│  5. Return to Normal Operation                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Quick Reference

### Common Commands

```bash
# Check if MCP server is configured
cat "/Users/gavinslater/Library/Application Support/Claude/claude_desktop_config.json" | grep -A 10 "mcp-gsuite"

# Check token expiry
python3 -c "from datetime import datetime; import json; token = json.load(open('/Users/gavinslater/mcp-gsuite-test/credentials/.oauth2.gavin.n.slater@gmail.com.json')); print(f\"Expires: {token['token_expiry']}\")"

# Re-authenticate
cd /Users/gavinslater/mcp-gsuite-test && uvx mcp-gsuite --gauth-file ./credentials/.gauth.json

# Test server
uvx mcp-gsuite --gauth-file /Users/gavinslater/mcp-gsuite-test/credentials/.gauth.json

# Check file permissions
ls -la /Users/gavinslater/mcp-gsuite-test/credentials/
```

### File Locations Quick Reference

```
Claude Desktop Config:
/Users/gavinslater/Library/Application Support/Claude/claude_desktop_config.json

Auth Files:
/Users/gavinslater/mcp-gsuite-test/
├── .accounts.json
└── credentials/
    ├── .gauth.json
    └── .oauth2.gavin.n.slater@gmail.com.json

Git Protection:
/Users/gavinslater/projects/life/.gitignore
```

---

**End of Documentation**

*This guide reflects the current production state as of 2025-10-15. Update this document when configuration changes are made.*
