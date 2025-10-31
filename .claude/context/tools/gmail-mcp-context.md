# Gmail & Calendar MCP Integration Context

## Status: ✅ Fully Operational with Native MCP Servers

### Gmail MCP Server
- **Package**: @gongrzhe/server-gmail-autoauth-mcp
- **Tools Available**: 18 Gmail tools
- **Status**: ✅ Connected and tested

### Google Calendar MCP Server
- **Package**: @cocal/google-calendar-mcp
- **Tools Available**: 10+ calendar tools
- **Status**: ✅ Connected and tested

### Authentication
- **Method**: OAuth 2.0 via Google Cloud Platform
- **Account**: gavin.n.slater@gmail.com
- **Configuration**: `~/.claude.json`
- **Credentials**:
  - Gmail: `~/.gmail-mcp/credentials.json`
  - Calendar: `~/.config/google-calendar-mcp/tokens.json`
  - OAuth Keys: `~/.gmail-mcp/gcp-oauth.keys.json` (shared)

## Capabilities

### Email Operations (18 tools)
- **Send/Draft/Read**: Complete email composition and reading
- **Search**: Gmail query syntax support
- **Labels**: Create, update, delete, organize
- **Filters**: Automated email organization
- **Batch Operations**: Process multiple emails efficiently
- **Attachments**: Download and manage file attachments

### Calendar Operations (10+ tools)
- **Event Management**: Create, update, delete events
- **Multi-Calendar**: Access all calendars (primary, family, work, shared)
- **Free/Busy**: Check availability across calendars
- **Search**: Find events by text query
- **Scheduling**: Optimize meeting times considering commute

## Usage Patterns

### Morning Routine
- Overnight email processing and priority identification
- Calendar review for the day
- Schedule conflicts resolution

### Schedule Coordination
- 3-day office (Mon/Tue/Thu) / 2-day WFH (Wed/Fri) pattern
- Commute integration: 6:52am train, ~6:30pm return
- Focus time blocking on WFH days

### Meeting Management
- Calendar optimization considering commute schedule
- Office days: 10am-4pm optimal for meetings
- WFH days: Flexible scheduling for deep work

### Follow-up Tracking
- Professional relationship maintenance
- Response time monitoring
- Action item tracking

## Agent Integration

### Primary Agent
**Gmail & Calendar Agent** (`gmail-calendar-agent`)
- Direct access to all Gmail and Calendar MCP tools
- Native integration (no workarounds needed)
- Context-aware: Work schedule, personal priorities, professional tone

### Available Tools
**Gmail**: `mcp__gmail__*` (18 tools)
**Calendar**: `mcp__google-calendar__*` (10+ tools)

### Cross-Agent Coordination
- **Personal Consultant**: Strategic email/calendar guidance
- **Knowledge Manager**: File important emails to Obsidian
- **Job Search Agent**: Career-related email processing
- **Daily Journal Agent**: Include email/calendar context in daily notes

## Common Triggers

### Email
- "Check my emails" → Email processing and summary
- "Any urgent emails?" → Priority identification
- "Draft response to..." → Professional email composition
- "Search for emails about..." → Gmail search
- "Create a filter for..." → Automated organization

### Calendar
- "What's on my calendar?" → Schedule review
- "Schedule a meeting" → Calendar coordination
- "When am I free?" → Availability check
- "Move the meeting" → Event rescheduling
- "Find all meetings with..." → Calendar search

## Technical Setup

### Configuration Files
- **MCP Config**: `~/.claude.json`
- **Gmail Credentials**: `~/.gmail-mcp/credentials.json`
- **Calendar Tokens**: `~/.config/google-calendar-mcp/tokens.json`
- **OAuth Keys**: `~/.gmail-mcp/gcp-oauth.keys.json`

### Google Cloud Console
- **OAuth Client ID**: 609165529264-l3otuicp2smu7vvpl8gjrahm4nflloe9
- **APIs Enabled**: Gmail API, Google Calendar API
- **Redirect URIs**:
  - Gmail: `http://localhost:3000/oauth2callback`
  - Calendar: `http://localhost:3500/oauth2callback`

### Re-authentication
**Gmail**:
```bash
npx @gongrzhe/server-gmail-autoauth-mcp auth
```

**Calendar**:
```bash
GOOGLE_OAUTH_CREDENTIALS=~/.gmail-mcp/gcp-oauth.keys.json npx @cocal/google-calendar-mcp auth
```

### Verification
```bash
claude mcp list | grep -E "gmail|google-calendar"
```

## Complete Documentation

For detailed setup, usage examples, and troubleshooting:
**[Gmail & Calendar Integration Guide](../../../integrations/gmail-calendar/README.md)**

Includes:
- Complete tool reference (28+ tools)
- Usage examples for common scenarios
- Gmail query syntax guide
- Calendar scheduling best practices
- Troubleshooting procedures
- Migration history

---

**Last updated**: October 31, 2025
**Migration**: Switched from mcp-gsuite to native Gmail/Calendar MCP servers
