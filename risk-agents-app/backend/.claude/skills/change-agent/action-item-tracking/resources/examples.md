# Action Item Tracking Examples

## Example 1: Simple String Array Input

### Input

```json
{
  "action_items": [
    "Update project timeline",
    "Review design mockups with team",
    "Get budget approval from finance",
    "Schedule kickoff meeting"
  ]
}
```

### Output

```json
{
  "status": "success",
  "summary": {
    "total_items": 4,
    "by_status": {
      "pending": 4,
      "in_progress": 0,
      "blocked": 0,
      "completed": 0
    },
    "by_priority": {
      "critical": 0,
      "high": 2,
      "medium": 2,
      "low": 0
    },
    "at_risk_count": 0
  },
  "action_items": [
    {
      "id": 1,
      "description": "Update project timeline with current milestones and dependencies",
      "owner": "Unassigned",
      "due_date": "2025-11-02",
      "priority": "high",
      "status": "pending",
      "estimated_effort": "2 hours",
      "dependencies": [],
      "blocking": [2, 4],
      "tags": ["planning", "timeline", "documentation"],
      "risk_level": "low",
      "risk_reason": "None",
      "next_steps": [
        "Gather current milestone data from team",
        "Update timeline document with latest dates",
        "Share updated timeline with stakeholders"
      ]
    },
    {
      "id": 2,
      "description": "Review design mockups with team and collect feedback",
      "owner": "Unassigned",
      "due_date": "2025-11-05",
      "priority": "medium",
      "status": "pending",
      "estimated_effort": "1 hour",
      "dependencies": [1],
      "blocking": [],
      "tags": ["design", "review", "team-meeting"],
      "risk_level": "low",
      "risk_reason": "None",
      "next_steps": [
        "Schedule team review meeting",
        "Prepare mockups for presentation",
        "Document feedback and next iterations"
      ]
    },
    {
      "id": 3,
      "description": "Get budget approval from finance department",
      "owner": "Unassigned",
      "due_date": "2025-11-08",
      "priority": "high",
      "status": "pending",
      "estimated_effort": "30 minutes",
      "dependencies": [],
      "blocking": [],
      "tags": ["finance", "approval", "budget"],
      "risk_level": "medium",
      "risk_reason": "Approval processes can take longer than expected",
      "next_steps": [
        "Prepare budget justification document",
        "Submit approval request to finance",
        "Follow up if not approved within 3 days"
      ]
    },
    {
      "id": 4,
      "description": "Schedule project kickoff meeting with all stakeholders",
      "owner": "Unassigned",
      "due_date": "2025-11-10",
      "priority": "medium",
      "status": "pending",
      "estimated_effort": "30 minutes",
      "dependencies": [1],
      "blocking": [],
      "tags": ["meeting", "kickoff", "stakeholders"],
      "risk_level": "low",
      "risk_reason": "None",
      "next_steps": [
        "Identify all required stakeholders",
        "Find mutually available time slot",
        "Send calendar invites with agenda"
      ]
    }
  ],
  "dependencies_graph": {
    "2": [1],
    "4": [1]
  },
  "critical_path": [1, 2],
  "recommendations": [
    {
      "type": "priority",
      "message": "Item #1 (Update project timeline) is blocking 2 other items - prioritize this first"
    },
    {
      "type": "capacity",
      "message": "All 4 items are unassigned - assign owners to ensure accountability"
    },
    {
      "type": "risk",
      "message": "Item #3 (budget approval) has medium risk due to potential approval delays - start early"
    }
  ],
  "metadata": {
    "generated_at": "2025-10-26T15:45:00Z",
    "skill_name": "action-item-tracking",
    "version": "1.0.0",
    "project_context": null
  }
}
```

### Why This Output

- **Enrichment**: Simple strings enriched with full descriptions, next steps, and metadata
- **Owner**: All items marked "Unassigned" since no owners provided
- **Due Dates**: Estimated based on typical urgency (2-10 days from now)
- **Dependencies**: Automatically detected that design review and kickoff depend on timeline
- **Priorities**: Timeline and budget marked "high" as they're typically critical; others "medium"
- **Recommendations**: Actionable suggestions to assign owners and prioritize blocking items

---

## Example 2: Partially Structured with Project Context

### Input

```json
{
  "action_items": [
    {
      "description": "Finalize requirements document",
      "owner": "Sarah Johnson",
      "status": "in_progress"
    },
    {
      "description": "Begin development sprint",
      "owner": "Dev Team",
      "notes": "Can't start until requirements are done"
    },
    {
      "description": "Set up CI/CD pipeline",
      "owner": "DevOps",
      "due_date": "2025-11-15"
    },
    {
      "description": "Security audit",
      "notes": "Required before launch"
    }
  ],
  "project_context": {
    "project_name": "Customer Portal Redesign",
    "project_deadline": "2025-12-31",
    "critical_path_items": ["Finalize requirements document", "Begin development sprint"]
  }
}
```

### Output

```json
{
  "status": "success",
  "summary": {
    "total_items": 4,
    "by_status": {
      "pending": 3,
      "in_progress": 1,
      "blocked": 0,
      "completed": 0
    },
    "by_priority": {
      "critical": 2,
      "high": 1,
      "medium": 1,
      "low": 0
    },
    "at_risk_count": 1
  },
  "action_items": [
    {
      "id": 1,
      "description": "Finalize requirements document for Customer Portal Redesign",
      "owner": "Sarah Johnson",
      "due_date": "2025-11-01",
      "priority": "critical",
      "status": "in_progress",
      "estimated_effort": "1 day",
      "dependencies": [],
      "blocking": [2],
      "tags": ["requirements", "documentation", "critical-path"],
      "risk_level": "high",
      "risk_reason": "On critical path, currently in progress with nearby due date",
      "next_steps": [
        "Complete stakeholder review section",
        "Get sign-off from product owner",
        "Publish final version to team wiki"
      ]
    },
    {
      "id": 2,
      "description": "Begin development sprint for Customer Portal Redesign",
      "owner": "Dev Team",
      "due_date": "2025-11-05",
      "priority": "critical",
      "status": "pending",
      "estimated_effort": "2 weeks",
      "dependencies": [1],
      "blocking": [4],
      "tags": ["development", "sprint", "critical-path"],
      "risk_level": "medium",
      "risk_reason": "Blocked by item #1 which is currently in progress",
      "next_steps": [
        "Wait for requirements finalization",
        "Set up development environment",
        "Plan sprint backlog and assign tasks"
      ]
    },
    {
      "id": 3,
      "description": "Set up CI/CD pipeline for automated deployments",
      "owner": "DevOps",
      "due_date": "2025-11-15",
      "priority": "high",
      "status": "pending",
      "estimated_effort": "3 days",
      "dependencies": [],
      "blocking": [],
      "tags": ["devops", "automation", "infrastructure"],
      "risk_level": "low",
      "risk_reason": "None",
      "next_steps": [
        "Design pipeline architecture",
        "Configure build and test stages",
        "Test deployment to staging environment"
      ]
    },
    {
      "id": 4,
      "description": "Complete security audit before launch",
      "owner": "Unassigned",
      "due_date": "2025-12-20",
      "priority": "medium",
      "status": "pending",
      "estimated_effort": "1 week",
      "dependencies": [2],
      "blocking": [],
      "tags": ["security", "audit", "compliance", "pre-launch"],
      "risk_level": "medium",
      "risk_reason": "Depends on development completion, no owner assigned yet",
      "next_steps": [
        "Assign security team owner",
        "Schedule audit timeframe",
        "Prepare application for security review"
      ]
    }
  ],
  "dependencies_graph": {
    "2": [1],
    "4": [2]
  },
  "critical_path": [1, 2, 4],
  "recommendations": [
    {
      "type": "priority",
      "message": "Focus on item #1 (Finalize requirements) - it's on the critical path and blocking development"
    },
    {
      "type": "capacity",
      "message": "Sarah Johnson has critical item #1 in progress - provide support if needed to complete quickly"
    },
    {
      "type": "risk",
      "message": "Item #1 is at high risk due to critical path status - monitor closely"
    },
    {
      "type": "dependency",
      "message": "Item #2 (Development) can't start until #1 completes - prepare in parallel where possible"
    }
  ],
  "metadata": {
    "generated_at": "2025-10-26T15:45:00Z",
    "skill_name": "action-item-tracking",
    "version": "1.0.0",
    "project_context": {
      "project_name": "Customer Portal Redesign",
      "project_deadline": "2025-12-31"
    }
  }
}
```

### Why This Output

- **Critical Path Recognition**: Items marked as critical path got "critical" priority
- **Dependency Detection**: Detected dependencies from notes ("Can't start until...")
- **Date Inference**: Provided due dates based on project context and typical timelines
- **Risk Assessment**: Item #1 flagged as high risk (critical path + in progress + near deadline)
- **Smart Recommendations**: Specific guidance based on dependencies and critical path analysis
- **Owner Assignment**: Security audit flagged as "Unassigned" to prompt assignment

---

## Example 3: Complex Multi-Project Scenario

### Input

```json
{
  "action_items": [
    {
      "description": "Q4 roadmap review",
      "owner": "PM Team",
      "due_date": "2025-10-28",
      "status": "in_progress"
    },
    {
      "description": "Hire senior engineer",
      "owner": "HR",
      "due_date": "2025-11-30"
    },
    {
      "description": "Launch mobile app beta",
      "owner": "Mobile Team",
      "due_date": "2025-11-15",
      "status": "blocked",
      "notes": "Waiting on app store approval"
    },
    {
      "description": "Customer feedback analysis",
      "owner": "Product",
      "due_date": "2025-11-05"
    },
    {
      "description": "Database migration",
      "owner": "Backend Team",
      "due_date": "2025-10-30",
      "status": "in_progress",
      "notes": "Critical - blocks new features"
    }
  ],
  "project_context": {
    "project_name": "Q4 Product Initiatives",
    "project_deadline": "2025-12-31"
  }
}
```

### Output (Abbreviated)

```json
{
  "status": "success",
  "summary": {
    "total_items": 5,
    "by_status": {
      "pending": 2,
      "in_progress": 2,
      "blocked": 1,
      "completed": 0
    },
    "by_priority": {
      "critical": 2,
      "high": 2,
      "medium": 1,
      "low": 0
    },
    "at_risk_count": 3
  },
  "action_items": [
    {
      "id": 5,
      "description": "Complete database migration to support new feature rollout",
      "owner": "Backend Team",
      "due_date": "2025-10-30",
      "priority": "critical",
      "status": "in_progress",
      "estimated_effort": "3 days",
      "dependencies": [],
      "blocking": [],
      "tags": ["database", "migration", "infrastructure", "blocking"],
      "risk_level": "high",
      "risk_reason": "Due in 4 days, currently in progress, noted as critical and blocking new features",
      "next_steps": [
        "Complete migration testing in staging",
        "Schedule production migration window",
        "Execute migration with rollback plan ready"
      ]
    },
    {
      "id": 1,
      "description": "Complete Q4 roadmap review and finalize priorities",
      "owner": "PM Team",
      "due_date": "2025-10-28",
      "priority": "critical",
      "status": "in_progress",
      "estimated_effort": "2 days",
      "dependencies": [],
      "blocking": [],
      "tags": ["planning", "roadmap", "q4", "strategy"],
      "risk_level": "high",
      "risk_reason": "Due in 2 days, currently in progress",
      "next_steps": [
        "Consolidate stakeholder input",
        "Finalize priority rankings",
        "Present to leadership for approval"
      ]
    },
    {
      "id": 3,
      "description": "Launch mobile app beta to test users",
      "owner": "Mobile Team",
      "due_date": "2025-11-15",
      "priority": "high",
      "status": "blocked",
      "estimated_effort": "1 week",
      "dependencies": [],
      "blocking": [],
      "tags": ["mobile", "beta", "launch", "app-store"],
      "risk_level": "high",
      "risk_reason": "Blocked status, waiting on app store approval which is outside team control",
      "next_steps": [
        "Follow up with app store review team",
        "Prepare beta user list while waiting",
        "Draft beta testing plan and feedback process"
      ]
    }
  ],
  "dependencies_graph": {},
  "critical_path": [5, 1, 3, 4, 2],
  "recommendations": [
    {
      "type": "priority",
      "message": "Items #1 and #5 are both critical and due within 4 days - allocate maximum resources"
    },
    {
      "type": "risk",
      "message": "3 items are at high risk - 2 near deadlines, 1 blocked by external dependency"
    },
    {
      "type": "dependency",
      "message": "Item #3 (mobile app beta) is blocked - escalate app store approval to unblock"
    },
    {
      "type": "capacity",
      "message": "Backend Team and PM Team both have critical in-progress items - monitor for support needs"
    }
  ],
  "metadata": {
    "generated_at": "2025-10-26T15:45:00Z",
    "skill_name": "action-item-tracking",
    "version": "1.0.0",
    "project_context": {
      "project_name": "Q4 Product Initiatives",
      "project_deadline": "2025-12-31"
    }
  }
}
```

### Why This Output

- **Urgent Items First**: Items #5 and #1 prioritized by urgency (2-4 days away)
- **Risk Flagging**: 3 items flagged high risk for different reasons (deadline, blocked status, notes)
- **Blocked Status Preserved**: Item #3 kept as "blocked" with explanation
- **Critical Path**: Ordered by a combination of urgency, dependencies, and impact
- **Actionable Recommendations**: Specific guidance for resource allocation and escalation

---

## Key Patterns Demonstrated

### Pattern 1: Enrichment from Minimal Input
- Simple strings → Full structured objects
- Missing fields → Intelligent defaults based on context

### Pattern 2: Dependency Detection
- Explicit notes ("depends on", "blocked by") → dependency array
- Implicit relationships (timeline before design review) → automatic linking

### Pattern 3: Intelligent Prioritization
- Critical path items → critical priority
- Near deadlines → higher priority
- Blocking other items → elevated priority

### Pattern 4: Risk Assessment
- Due date proximity + status → risk level
- External dependencies (approvals) → medium/high risk
- Multiple dependencies → complexity risk

### Pattern 5: Actionable Recommendations
- Focus on blockers first
- Capacity warnings when individuals overloaded
- Escalation suggestions for blocked items
