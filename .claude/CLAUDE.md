# Claude Code Configuration

The `.claude/` directory contains all Claude Code configuration, context, and agent definitions for Gavin's Personal AI Infrastructure.

## Directory Structure

### Context System
`.claude/context/` - Universal File Context (UFC) system containing personal context, active projects, and tool documentation. See `.claude/context/CLAUDE.md` for full details.

### Agent Definitions
`.claude/agents/` - Specialized sub-agent definitions. Each agent has specific tools and capabilities for domain-specific tasks:
- `personal-consultant.md` - Master orchestrator
- `gmail-calendar-agent.md` - Email and calendar operations
- `freeagent-invoice-agent.md` - Financial operations
- `job-search-agent.md` - Career development
- `health-agent.md` - Fitness tracking
- `location-agent.md` - Movement analysis
- `knowledge-manager-agent.md` - Obsidian vault management
- `gtd-task-manager-agent.md` - Task management
- `daily-journal-agent.md` - Daily planning orchestration
- `daily-brief-agent.md` - News curation
- `interactive-cv-website-agent.md` - Portfolio development
- `content-processor-agent.md` - Fabric AI patterns
- `weekly-review-agent.md` - GTD weekly reviews
- `project-setup-review-agent.md` - Project definition
- `horizons-reviewer-agent.md` - Goals and vision

### Slash Commands
`.claude/commands/` - Simple repeatable tasks:
- `daily-brief.md` - Personalized news curation
- `daily-note.md` - Obsidian daily note creation
- `daily-journal-morning.md` - Morning briefing
- `daily-journal-evening.md` - Evening reflection
- `youtube-transcript.md` - YouTube transcript extraction

### Hooks
`.claude/hooks/` - Event-driven automation scripts

### Output Styles
`.claude/output-styles/` - Custom output formatting

## Loading Priority

1. **Always load** `.claude/context/` for full system awareness
2. **Conditionally load** `.claude/agents/` when delegating to sub-agents
3. **Use** `.claude/commands/` via SlashCommand tool for routine tasks
