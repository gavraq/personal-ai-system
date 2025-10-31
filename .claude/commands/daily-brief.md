---
name: daily-brief
description: Generate personalized daily news briefing with UFC context loading
allowed-tools: [Task, Read]
---

# Daily Brief Command

## Purpose
Generate a personalized daily news briefing by analyzing Gavin's interests and curating relevant current events from the past 7 days.

## Context Loading Protocol
**Auto-load UFC Context**:
- `/profile/core-identity.md` - For interest alignment and communication style
- `/profile/goals-objectives.md` - For relevance scoring against current objectives
- `/active-projects/ai-coding-projects.md` - AI/tech focus areas
- `/active-projects/job-search.md` - Career transition context

## Implementation
Use Task tool with daily-brief-agent to ensure web tool access:

```
Task(
    subagent_type="daily-brief-agent",
    description="Generate personalized daily brief",
    prompt="Generate personalized daily briefing with UFC context loading and save to Obsidian vault Daily Brief folder"
)
```

## Expected Output
- **File**: `daily-brief-YYYY-MM-DD.md` in Obsidian vault Daily Brief folder
- **Content**: 10-15 relevant articles with 0.3+ relevance scores
- **Format**: Structured with actionable insights and goal connections
- **Context**: Aligned with current AI transition and quantified self objectives

## Usage
Run `/daily-brief` to generate today's personalized briefing with full UFC context loading.

---
*Full implementation details: `/Users/gavinslater/projects/life/daily-brief-system/CLAUDE.md`*