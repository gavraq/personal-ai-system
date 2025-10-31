# Gmail MCP Integration Context

## Status: ✅ Connected and Operational
- **MCP Server**: mcp-gsuite (both Claude Desktop and Claude Code)
- **Integration Level**: Full email and calendar management
- **Authentication**: Google account credentials via MCP server

## Capabilities
- **Email Operations**: Read, send, organize, prioritize, search
- **Calendar Management**: Schedule review, meeting coordination, conflict resolution
- **Response Management**: Professional tone, context-aware drafting
- **Communication Intelligence**: Priority identification, follow-up tracking

## Usage Patterns
- **Morning Routine**: Overnight email processing and priority identification
- **Schedule Coordination**: 3-day office/2-day WFH pattern integration
- **Meeting Management**: Calendar optimization considering commute schedule
- **Follow-up Tracking**: Professional relationship maintenance

## Agent Integration
- **Primary**: Email Management Agent (`email-management-agent`)
- **Available Tools**: mcp_* tools via mcp-gsuite server
- **Context Awareness**: Work schedule, personal priorities, professional tone

## Triggers
- "Check my emails" → Email processing and summary
- "Schedule a meeting" → Calendar coordination
- "Any urgent emails?" → Priority identification
- "Draft response" → Professional email composition

## Technical Setup
For complete MCP server configuration, authentication, and troubleshooting details, see:
**[GSuite MCP Setup Guide](../../../docs/gsuite-mcp-setup-guide.md)**

Includes:
- Complete configuration file locations
- OAuth authentication flow
- Token lifecycle management
- Troubleshooting procedures
- Security best practices

---
*Last updated: 2025-10-15*