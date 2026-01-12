# Multi-Agent Observability System - UFC Context

## Overview

**Multi-Agent Observability** is a real-time monitoring and visualization system for Claude Code agents through comprehensive hook event tracking.

**Status**: ✅ Deployed and Operational (Raspberry Pi)
**Location**: `/integrations/observability/`
**Access**:
- **Dashboard**: `https://agentdashboard.gavinslater.co.uk` (main UI)
- Server API: `https://observability.gavinslater.co.uk` (SSL via Nginx Proxy Manager)
- Server Direct: `http://192.168.5.190:4000`
- WebSocket: `wss://observability.gavinslater.co.uk/stream`

**Deployment**: Docker container on Raspberry Pi (`~/docker/observability-server/`)

## Purpose & Value

### Core Capabilities
- **Real-time Monitoring**: Watch Claude Code agents execute tasks with live event streaming
- **Session Tracking**: Track multiple concurrent agent sessions with color-coded visualization
- **Event Filtering**: Filter by app, session, event type with multi-select controls
- **Chat Transcripts**: View complete conversation history for any session
- **Live Pulse Chart**: Real-time activity visualization with session-colored bars

### Integration Value
1. **Debugging**: Understand exactly what Claude Code is doing and why
2. **Performance Analysis**: Track tool usage patterns and execution times
3. **Multi-Agent Coordination**: Monitor subagent spawning and completion
4. **Development Insights**: Learn from agent behavior to improve prompts and workflows

## Architecture

```
Claude Agents → Hook Scripts → HTTP POST → Bun Server → SQLite → WebSocket → Vue Client
```

### Components
- **Hook System** (`.claude/hooks/`): Python scripts intercepting Claude Code lifecycle events
- **Server** (`apps/server/`): Bun TypeScript server with SQLite and WebSocket
- **Client** (`apps/client/`): Vue 3 real-time dashboard with filtering and charts

## Event Types

| Event Type | Emoji | Purpose |
|------------|-------|---------|
| PreToolUse | 🔧 | Before tool execution |
| PostToolUse | ✅ | After tool completion |
| Notification | 🔔 | User interactions |
| Stop | 🛑 | Response completion |
| SubagentStop | 👥 | Subagent finished |
| PreCompact | 📦 | Context compaction |
| UserPromptSubmit | 💬 | User prompt submission |
| SessionStart | 🚀 | Session started |
| SessionEnd | 🏁 | Session ended |

## When to Use Observability

### DO Use For:
- ✅ Debugging complex multi-agent workflows
- ✅ Understanding why agents make certain decisions
- ✅ Monitoring long-running tasks
- ✅ Analyzing tool usage patterns
- ✅ Reviewing chat transcripts for session debugging

### DON'T Use For:
- ❌ Production monitoring (development tool only)
- ❌ Security auditing (not designed for this)

## Quick Start

```bash
# Open the dashboard (deployed on Pi)
open https://agentdashboard.gavinslater.co.uk

# Events from life and riskagent projects stream automatically
```

### Server Management (Pi)
```bash
# Check server status
curl https://observability.gavinslater.co.uk/health

# View logs
ssh pi@192.168.5.190 'docker logs observability-server -f'

# Restart server
ssh pi@192.168.5.190 'cd ~/docker/observability-server && docker-compose restart'
```

## Hook Configuration

Projects send events by configuring `.claude/settings.local.json`:

```json
{
  "hooks": {
    "PreToolUse": [{
      "hooks": [{
        "type": "command",
        "command": "uv run /path/to/.claude/hooks/send_event.py --source-app PROJECT_NAME --event-type PreToolUse --server-url https://observability.gavinslater.co.uk/events --summarize"
      }]
    }]
  }
}
```

### Configured Projects
- **life** - Full observability with all event types (`source_app: life`)
- **riskagent** - Core events: PreToolUse, PostToolUse, Notification, Stop, UserPromptSubmit (`source_app: riskagent`)

### Adding New Projects
1. Copy hooks: `cp -R /Users/gavinslater/projects/life/.claude/hooks /path/to/project/.claude/`
2. Add hooks configuration to `settings.local.json` with unique `--source-app` name
3. Events will appear in dashboard filtered by source app

## Key Features

### Dashboard Visualization
- **Dual-color system**: App colors (left border) + Session colors (right border)
- **Auto-scroll**: Follows new events with manual override option
- **Event limiting**: Configurable max events display
- **Theme support**: Dark/light mode

### AI Summarization
Events can include AI-generated summaries via `--summarize` flag, providing quick insight into what each event represents.

### Human-in-the-Loop (HITL)
Supports approval workflows where certain actions require user confirmation before proceeding.

## Integration with Life Project

The life project uses observability for:
- Monitoring GTD agent workflows
- Debugging sub-agent delegation chains
- Understanding tool usage in complex tasks
- Reviewing session transcripts for quality improvement

## Technical Stack

- **Server**: Bun, TypeScript, SQLite (WAL mode)
- **Client**: Vue 3, TypeScript, Vite, Tailwind CSS
- **Hooks**: Python 3.8+, Astral uv

## Documentation References

- **Main README**: `/integrations/observability/README.md`
- **Server Details**: `/integrations/observability/apps/server/README.md`
- **Client Details**: `/integrations/observability/apps/client/README.md`
- **HITL Documentation**: `/integrations/observability/app_docs/how_human_in_the_loop_v1_works.md`

---

**Last Updated**: November 2025 - Deployed to Raspberry Pi with SSL, configured for life and riskagent projects
