# Context

The `.claude/context/` directory is your context system. The context system is entirely filesystem-based. It contains critical information that you will **require** to successfully complete tasks as a personal assistant.

**YOU** are solely responsible for maintaining the context system up-to-date and leveraging it to effectively serve the user.

## Context System Structure

The `.claude/context/` system is organized into the following subsystems:

1. `.claude/context/profile/` : This is your memory system. Leveraging your memory system by remembering important details about the user, their preferences, and their goals will help you provide more personalized and helpful responses. It is entirely maintained by you.

2. `.claude/context/active-projects/` : This is your project system. Projects contain domain-specific data and context that is critical to understanding and effectively managing specific areas of the user's life.

3. `.claude/context/tools/` : This is your tool documentation system. All MCP servers and tools that you have access to are comprehensively documented here. It's critical that you read the tool documentation to thoroughly understand each tool's purpose, usage, and data contracts before using them.

## Subsystem Details

Each subsystem has its own CLAUDE.md with detailed file listings and usage guidance:

- `profile/CLAUDE.md` - Memory system files and maintenance guidelines
- `active-projects/CLAUDE.md` - Current project files and loading guidance
- `tools/CLAUDE.md` - Sub-agent portfolio and tools-first protocol

## Loading Context

**Always load** the complete context directory at the start of each session to establish full system awareness. This provides:
- Personal identity and preferences (profile)
- Current project states and priorities (active-projects)
- Available tools and integrations (tools)

**Conditionally load** detailed implementation from:
- `/.claude/agents/` - Full agent definitions
- `/integrations/` - Specific API implementations
- Project directories - Deep implementation details

## Maintaining Context

When you learn new information about the user or their projects:
1. Determine which context file is most appropriate
2. Update the file with new information
3. Ensure consistency across related files
4. Remove outdated information

Keep context files concise but comprehensive. They serve as your persistent memory across sessions.
