# Action Item Tracking Output Template

Use this exact JSON structure for action-item-tracking skill outputs:

```json
{
  "status": "success",
  "summary": {
    "total_items": [NUMBER],
    "by_status": {
      "pending": [NUMBER],
      "in_progress": [NUMBER],
      "blocked": [NUMBER],
      "completed": [NUMBER]
    },
    "by_priority": {
      "critical": [NUMBER],
      "high": [NUMBER],
      "medium": [NUMBER],
      "low": [NUMBER]
    },
    "at_risk_count": [NUMBER]
  },
  "action_items": [
    {
      "id": [SEQUENTIAL_NUMBER],
      "description": "[WHAT needs to be done - specific and actionable]",
      "owner": "[WHO is responsible - name or 'Unassigned']",
      "due_date": "[WHEN it's due - YYYY-MM-DD format]",
      "priority": "[critical|high|medium|low]",
      "status": "[pending|in_progress|blocked|completed]",
      "estimated_effort": "[Rough estimate: '30 minutes', '2 hours', '1 day', etc.]",
      "dependencies": [[ARRAY of item IDs this depends on]],
      "blocking": [[ARRAY of item IDs blocked by this one]],
      "tags": [[ARRAY of relevant tags for categorization]],
      "risk_level": "[low|medium|high - based on deadline, dependencies, complexity]",
      "risk_reason": "[WHY this item is at risk - specific reason or 'None']",
      "next_steps": [
        "[Immediate next action 1]",
        "[Immediate next action 2]",
        "[Immediate next action 3]"
      ]
    }
  ],
  "dependencies_graph": {
    "[ITEM_ID]": [[ARRAY of dependencies]],
    "[ITEM_ID]": [[ARRAY of dependencies]]
  },
  "critical_path": [[ARRAY of item IDs in sequence forming the critical path]],
  "recommendations": [
    {
      "type": "[priority|risk|capacity|dependency]",
      "message": "[Specific, actionable recommendation]"
    }
  ],
  "metadata": {
    "generated_at": "[ISO 8601 timestamp]",
    "skill_name": "action-item-tracking",
    "version": "1.0.0",
    "project_context": {
      "project_name": "[Project name if provided]",
      "project_deadline": "[Project deadline if provided]"
    }
  }
}
```

## Field Definitions

### Summary Section
- **total_items**: Count of all action items
- **by_status**: Breakdown of items by current status
- **by_priority**: Breakdown of items by priority level
- **at_risk_count**: Number of items flagged as at-risk

### Action Item Fields
- **id**: Unique sequential number (1, 2, 3...)
- **description**: Clear, specific, actionable description (WHAT)
- **owner**: Person or team responsible (WHO) - use "Unassigned" if not specified
- **due_date**: Target completion date (WHEN) in YYYY-MM-DD format
- **priority**: critical (must do now), high (important), medium (should do), low (nice to have)
- **status**: pending (not started), in_progress (actively working), blocked (waiting), completed (done)
- **estimated_effort**: Rough time estimate based on description complexity
- **dependencies**: Array of item IDs that must be completed before this one
- **blocking**: Array of item IDs that are waiting for this one
- **tags**: Relevant categorization tags (meeting, technical, approval, etc.)
- **risk_level**: Assessment of completion risk (low, medium, high)
- **risk_reason**: Explanation of why item is at risk or "None" if not at risk
- **next_steps**: 1-3 immediate actionable next steps for this item

### Dependencies Graph
- Key-value pairs where key is item ID and value is array of dependency IDs
- Makes it easy to visualize dependency chains

### Critical Path
- Ordered array of item IDs that form the critical path
- Items that must be completed in sequence and determine overall timeline

### Recommendations
- Actionable insights based on analysis
- Types: priority (focus areas), risk (deadline concerns), capacity (workload), dependency (blockers)

---

**Template Version**: 1.0.0
**Last Updated**: 2025-10-26
