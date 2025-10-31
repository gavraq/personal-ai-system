# Gmail & Calendar MCP Integration

**Status**: ✅ **Fully Functional** - Both Gmail and Google Calendar MCP Servers

## Overview

This directory contains the Gmail and Google Calendar MCP (Model Context Protocol) integrations for Claude Code, providing native email and calendar functionality directly within Claude conversations.

### Active Integrations

**Gmail MCP**: [@gongrzhe/server-gmail-autoauth-mcp](https://github.com/GongRzhe/Gmail-MCP-Server)
**Calendar MCP**: [@cocal/google-calendar-mcp](https://github.com/nspady/google-calendar-mcp)
**Authentication**: OAuth 2.0 via Google Cloud Platform
**Account**: gavin.n.slater@gmail.com

## Quick Start

### Prerequisites
- Node.js and npm installed
- Google Cloud Project with Gmail API and Calendar API enabled
- OAuth 2.0 credentials configured

### Installation

Both MCP servers are already installed and configured. No additional setup needed!

**Configuration Location**: `~/.claude.json`

```json
{
  "gmail": {
    "command": "npx",
    "args": ["@gongrzhe/server-gmail-autoauth-mcp"]
  },
  "google-calendar": {
    "command": "npx",
    "args": ["@cocal/google-calendar-mcp"],
    "env": {
      "GOOGLE_OAUTH_CREDENTIALS": "/Users/gavinslater/.gmail-mcp/gcp-oauth.keys.json"
    }
  }
}
```

**Credentials Locations**:
- Gmail: `~/.gmail-mcp/credentials.json`
- Calendar: `~/.config/google-calendar-mcp/tokens.json`
- OAuth Keys: `~/.gmail-mcp/gcp-oauth.keys.json` (shared)

## Available Tools

### Gmail Tools (18 total)

#### Email Operations
- `mcp__gmail__send_email` - Send emails with attachments
- `mcp__gmail__draft_email` - Create email drafts
- `mcp__gmail__read_email` - Read email content by ID
- `mcp__gmail__search_emails` - Search emails with Gmail query syntax
- `mcp__gmail__modify_email` - Change email labels/folders
- `mcp__gmail__delete_email` - Delete emails

#### Label Management
- `mcp__gmail__list_email_labels` - List all Gmail labels
- `mcp__gmail__create_label` - Create new labels
- `mcp__gmail__update_label` - Modify existing labels
- `mcp__gmail__delete_label` - Remove labels
- `mcp__gmail__get_or_create_label` - Get label or create if missing

#### Filter Management
- `mcp__gmail__create_filter` - Create Gmail filters
- `mcp__gmail__list_filters` - List all filters
- `mcp__gmail__get_filter` - Get filter details
- `mcp__gmail__delete_filter` - Remove filters
- `mcp__gmail__create_filter_from_template` - Use pre-defined filter templates

#### Batch Operations
- `mcp__gmail__batch_modify_emails` - Modify multiple emails
- `mcp__gmail__batch_delete_emails` - Delete multiple emails

#### Attachments
- `mcp__gmail__download_attachment` - Download email attachments

### Google Calendar Tools

#### Calendar Operations
- `mcp__google-calendar__list-calendars` - List all accessible calendars
- `mcp__google-calendar__list-events` - List events from calendars
- `mcp__google-calendar__search-events` - Search events by text query
- `mcp__google-calendar__get-event` - Get specific event details
- `mcp__google-calendar__list-colors` - List available color IDs

#### Event Management
- `mcp__google-calendar__create-event` - Create new calendar events
- `mcp__google-calendar__update-event` - Update existing events
- `mcp__google-calendar__delete-event` - Delete calendar events

#### Scheduling
- `mcp__google-calendar__get-freebusy` - Query free/busy information
- `mcp__google-calendar__get-current-time` - Get current time in calendar timezone

## Usage Examples

### Gmail Examples

**Search Recent Emails**:
```
Show me my last 5 emails from today
```

**Send an Email**:
```
Send an email to john@example.com with subject "Meeting Tomorrow"
and body "Hi John, Let's meet at 2pm tomorrow."
```

**Create a Filter**:
```
Create a filter to automatically label all emails from newsletters@company.com
with the "Newsletters" label and mark them as read
```

### Calendar Examples

**List Upcoming Events**:
```
What's on my calendar for the next week?
```

**Create an Event**:
```
Schedule a meeting with John next Tuesday at 2pm for 1 hour
```

**Check Availability**:
```
When am I free tomorrow afternoon?
```

**Find Events**:
```
Search my calendar for all meetings with Sarah in the last month
```

## Verification

Check if both MCP servers are running:

```bash
claude mcp list | grep -E "gmail|google-calendar"
```

Expected output:
```
gmail: npx @gongrzhe/server-gmail-autoauth-mcp - ✓ Connected
google-calendar: npx @cocal/google-calendar-mcp - ✓ Connected
```

## Re-authentication

### Gmail
If your Gmail OAuth token expires:

```bash
npx @gongrzhe/server-gmail-autoauth-mcp auth
```

### Google Calendar
If your Calendar OAuth token expires:

```bash
GOOGLE_OAUTH_CREDENTIALS=~/.gmail-mcp/gcp-oauth.keys.json npx @cocal/google-calendar-mcp auth
```

## Google Cloud Console Setup

### OAuth 2.0 Configuration

**Project**: Your Google Cloud Project
**Client ID**: 609165529264-l3otuicp2smu7vvpl8gjrahm4nflloe9.apps.googleusercontent.com

**Authorized Redirect URIs**:
- `http://localhost:3000/oauth2callback` (Gmail MCP)
- `http://localhost:3500/oauth2callback` (Calendar MCP)
- `http://localhost:4100/code` (Legacy - can be removed)

**Required APIs**:
- Gmail API (enabled)
- Google Calendar API (enabled)

**Scopes Required**:
- `https://www.googleapis.com/auth/gmail.modify` - Gmail access
- `https://www.googleapis.com/auth/gmail.settings.basic` - Gmail settings
- `https://www.googleapis.com/auth/calendar` - Calendar access

### To Update Configuration

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Select your OAuth 2.0 Client ID
3. Ensure redirect URIs are configured
4. Verify both APIs are enabled in [API Library](https://console.cloud.google.com/apis/library)

## Troubleshooting

### Server Not Connected

```bash
# Check server status
claude mcp list

# Restart VS Code completely
# Cmd+Q and reopen
```

### Gmail Authentication Errors

**Error 400: redirect_uri_mismatch**
- Add `http://localhost:3000/oauth2callback` to Google Cloud Console

**Token Expired**
- Run: `npx @gongrzhe/server-gmail-autoauth-mcp auth`

### Calendar Authentication Errors

**Error 400: redirect_uri_mismatch**
- Add `http://localhost:3500/oauth2callback` to Google Cloud Console

**Token Expired**
- Run: `GOOGLE_OAUTH_CREDENTIALS=~/.gmail-mcp/gcp-oauth.keys.json npx @cocal/google-calendar-mcp auth`

**Calendar API Not Enabled**
- Enable at: https://console.cloud.google.com/apis/library/calendar-json.googleapis.com

### Tools Not Available

1. Verify connection: `claude mcp list`
2. Restart VS Code completely (Cmd+Q and reopen)
3. Check credentials exist:
   - Gmail: `ls -la ~/.gmail-mcp/`
   - Calendar: `ls -la ~/.config/google-calendar-mcp/`

## Directory Structure

```
/Users/gavinslater/projects/life/integrations/gmail-calendar/
├── README.md                 # This file
├── MIGRATION-SUMMARY.md      # Migration documentation
└── credentials/              # Legacy credentials (backup)
    ├── .gauth.json           # OAuth client config
    └── .oauth2.gavin.n.slater@gmail.com.json  # Old tokens
```

**Note**: Active credentials are stored in:
- `~/.gmail-mcp/` (Gmail)
- `~/.config/google-calendar-mcp/` (Calendar)

## Migration History

**Previous Setup**: mcp-gsuite (Python-based via uvx)
**Current Setup**:
- Gmail: @gongrzhe/server-gmail-autoauth-mcp (Node.js via npx)
- Calendar: @cocal/google-calendar-mcp (Node.js via npx)

**Migration Date**: October 31, 2025

### Why We Switched

The previous mcp-gsuite server had issues:
- ❌ Tools not exposed in Claude Code (architectural limitation)
- ❌ JSON Schema validation errors
- ❌ Complex configuration with multiple credential files
- ❌ Cache bloat (13GB+ in UV cache)

The new servers provide:
- ✅ Native Claude Code compatibility
- ✅ Simpler architecture (npx vs uvx)
- ✅ Auto-authentication built-in
- ✅ More active maintenance
- ✅ Complete API coverage
- ✅ Separate Gmail and Calendar management

## Related Integrations

This integration works alongside:
- **Gmail & Calendar Agent** (`/.claude/agents/gmail-calendar-agent.md`) - AI agent for email and calendar workflow
- **Personal Consultant** (`/.claude/agents/personal-consultant.md`) - Master orchestrator
- **Knowledge Manager** (`/.claude/agents/knowledge-manager-agent.md`) - Obsidian integration

## Support

**Gmail MCP Server**: https://github.com/GongRzhe/Gmail-MCP-Server
**Calendar MCP Server**: https://github.com/nspady/google-calendar-mcp
**MCP Documentation**: https://modelcontextprotocol.io
**Claude Code Docs**: https://docs.claude.com/en/docs/claude-code

## Success Metrics

✅ **Gmail Server**: Connected with 18 tools
✅ **Calendar Server**: Connected with 10+ tools
✅ **Authentication**: OAuth 2.0 valid for both
✅ **Test Status**: Both servers tested successfully
✅ **Integration Date**: October 31, 2025

---

**Last Updated**: October 31, 2025
**Maintained By**: Gavin Slater
