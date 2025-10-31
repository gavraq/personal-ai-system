---
name: action-item-tracking
description: Track and manage action items across projects with prioritization, assignments, and dependency management
domain: change-agent
category: project-management
taxonomy: change-agent/project-management
parameters:
  - action_items
  - project_context
output_format: json
estimated_duration: 3-5 minutes
tags:
  - action-items
  - task-management
  - project-tracking
  - accountability
version: 1.0.0
author: Risk Agents Team
---

# Action Item Tracking Skill

## Purpose
Transform unstructured or loosely organized action items into a prioritized, well-structured tracking system with clear ownership, dependencies, and deadlines.

## When to Use This Skill
- After collecting action items from multiple meetings or sources
- When you need to prioritize and organize a backlog of tasks
- When tracking progress across multiple workstreams
- When identifying dependencies between action items
- When preparing status updates or team coordination

## How It Works
This skill takes raw action items (from meetings, emails, discussions) and structures them into a comprehensive tracking system with:

1. **Action Item Enrichment**: Analyzes each item to ensure it has WHAT, WHO, WHEN, WHY
2. **Priority Assignment**: Evaluates urgency and importance to assign priorities
3. **Dependency Mapping**: Identifies relationships and dependencies between items
4. **Status Tracking**: Categorizes items by current status (pending, in-progress, blocked, complete)
5. **Risk Flagging**: Identifies items at risk of delay or requiring escalation

## Parameters

### Required Parameters
- **`action_items`** (array): List of action items to track. Can be simple strings or structured objects.
  - As strings: `["Update timeline", "Review design mockups", "Schedule kickoff"]`
  - As objects: `[{"description": "Update timeline", "owner": "John", "due_date": "2025-11-01"}]`

### Optional Parameters
- **`project_context`** (object): Additional project context to help with prioritization
  - `project_name` (string): Name of the project
  - `project_deadline` (date): Overall project deadline for urgency assessment
  - `key_stakeholders` (array): List of key stakeholders
  - `critical_path_items` (array): Items on the critical path
  - Default: None (skill will work without context but with less intelligent prioritization)

## Resources

- `resources/template.md` - Structured JSON output template
- `resources/examples.md` - Example transformations from various input formats

## Knowledge References

This skill utilizes knowledge from the Change Agent domain:
- **action-items-standards.md** - Standards for complete, actionable action items (WHAT, WHO, WHEN, WHY)

These knowledge documents provide best practices and standards that enhance the quality of the skill execution.

## Expected Output

A structured JSON object containing prioritized and enriched action items:

```json
{
  "status": "success",
  "summary": {
    "total_items": 12,
    "by_status": {
      "pending": 5,
      "in_progress": 4,
      "blocked": 2,
      "completed": 1
    },
    "by_priority": {
      "critical": 2,
      "high": 4,
      "medium": 5,
      "low": 1
    },
    "at_risk_count": 3
  },
  "action_items": [
    {
      "id": 1,
      "description": "Finalize Q4 project roadmap with detailed milestones",
      "owner": "Sarah Johnson",
      "due_date": "2025-11-01",
      "priority": "critical",
      "status": "in_progress",
      "estimated_effort": "4 hours",
      "dependencies": [5, 7],
      "blocking": [2, 3],
      "tags": ["planning", "roadmap", "q4"],
      "risk_level": "high",
      "risk_reason": "Due date is 5 days away, multiple dependencies not yet complete",
      "next_steps": [
        "Review draft with tech lead",
        "Incorporate stakeholder feedback",
        "Publish to team wiki"
      ]
    },
    {
      "id": 2,
      "description": "Schedule stakeholder review meeting",
      "owner": "John Smith",
      "due_date": "2025-11-03",
      "priority": "high",
      "status": "blocked",
      "estimated_effort": "30 minutes",
      "dependencies": [1],
      "blocking": [],
      "tags": ["meeting", "stakeholders", "review"],
      "risk_level": "medium",
      "risk_reason": "Blocked by item #1 (roadmap finalization)",
      "next_steps": [
        "Wait for roadmap completion",
        "Send calendar invites",
        "Prepare meeting agenda"
      ]
    }
  ],
  "dependencies_graph": {
    "1": [5, 7],
    "2": [1],
    "3": [1]
  },
  "critical_path": [5, 7, 1, 2, 3],
  "recommendations": [
    {
      "type": "priority",
      "message": "Focus on items #5 and #7 first - they are blocking the critical path"
    },
    {
      "type": "risk",
      "message": "3 items are at high risk of missing deadlines - consider re-prioritization"
    },
    {
      "type": "capacity",
      "message": "Sarah Johnson has 5 action items assigned - consider load balancing"
    }
  ],
  "metadata": {
    "generated_at": "2025-10-26T15:30:00Z",
    "skill_name": "action-item-tracking",
    "version": "1.0.0",
    "project_context": {
      "project_name": "Q4 Product Launch",
      "project_deadline": "2025-12-15"
    }
  }
}
```

## Success Criteria
- All action items have clear descriptions (WHAT)
- All action items have assigned owners (WHO)
- All action items have due dates (WHEN)
- Priority levels are assigned based on urgency and impact
- Dependencies are identified where applicable
- At-risk items are flagged with reasons
- Recommendations are actionable and specific

## Tips for Best Results

### For Better Prioritization
- Provide project context (project deadline, critical milestones)
- Indicate which items are on the critical path
- Mention any known dependencies upfront

### For Better Action Item Quality
- Include as much detail as possible in item descriptions
- Specify owners if known (even if tentative)
- Indicate rough due dates or relative urgency
- Mention any blocking issues or dependencies

### Input Format Examples

**Simple String Array** (skill will enrich):
```json
{
  "action_items": [
    "Update project timeline",
    "Review design mockups with team",
    "Schedule kickoff meeting",
    "Get budget approval from finance"
  ]
}
```

**Partially Structured** (skill will complete missing fields):
```json
{
  "action_items": [
    {
      "description": "Update project timeline",
      "owner": "Sarah"
    },
    {
      "description": "Review design mockups",
      "due_date": "2025-11-01"
    }
  ]
}
```

**Fully Structured** (skill will prioritize and identify dependencies):
```json
{
  "action_items": [
    {
      "description": "Finalize requirements document",
      "owner": "John Smith",
      "due_date": "2025-10-30",
      "status": "in_progress"
    },
    {
      "description": "Begin development sprint",
      "owner": "Dev Team",
      "due_date": "2025-11-05",
      "status": "pending",
      "notes": "Depends on requirements being finalized"
    }
  ],
  "project_context": {
    "project_name": "Customer Portal Redesign",
    "project_deadline": "2025-12-31"
  }
}
```

## Known Limitations

- **Estimated Effort**: Provides rough estimates based on description complexity, not actual time tracking
- **Owner Assignment**: If no owner specified, skill will flag as "Unassigned" rather than guess
- **Dependency Detection**: Automatic dependency detection works best when items mention each other or when hints are provided
- **Status Inference**: If status not provided, skill assumes "pending" as default

## Version History

- **1.0.0** (2025-10-26): Initial release
  - Basic action item enrichment
  - Priority assignment algorithm
  - Dependency mapping
  - Risk flagging
  - Critical path identification
