---
name: daily-journal-evening
description: Generate brief evening reflection with health metrics and accomplishments
allowed-tools: [Task, Read, WebFetch, Bash]
---

# Daily Journal Evening Command

Generate concise evening reflection and update today's daily note with location, health, and task completion data.

## Implementation

Calculate today's date and delegate to daily-journal-agent with minimal output.

**Target Date**: Today (auto-calculated as YYYY-MM-DD, DayName)
**Daily Note**: `Calendar/YYYY/MM-MonthName/YYYY-MM-DD-DayName.md`

### Workflow

```
Task: daily-journal-agent "Execute evening reflection for [YYYY-MM-DD DayName].

REQUIREMENTS:
1. Fetch location data via location-agent (today's movement)
2. Fetch health metrics via health-agent (steps, energy, heart rate)
3. Fetch calendar summary via email-management-agent (today's events)
4. Fetch weather (today's conditions)
5. Calculate habit streaks from last 7 daily notes
6. Update daily note with CONCISE sections:
   - Location Information (timeline + time distribution)
   - Health & Fitness > Today's Health Metrics (bullet list)
   - Health & Fitness > Health Analysis (2-3 sentences max)
   - Health & Fitness > Tracking (streak status + checkbox)
   - Health & Fitness > Evening Reflection (brief accomplishments)

OUTPUT FORMAT - CONCISE ONLY:
**Health**: [Steps], [Active energy], [Exercise min]
**Location**: [Pattern summary - office/WFH/weekend]
**Habits**:
  - Evening exercises: [Status] ([X] day streak)
  - Daily note: ✅ ([X] day streak)
**Accomplishments**: [Brief factual summary if identifiable from calendar]

✅ Daily note updated: Calendar/YYYY/MM-MonthName/YYYY-MM-DD-DayName.md"
```

## Expected Output

Concise user summary matching Oct 7-10 format:
- 5-6 lines total
- Factual data only
- Brief habit tracking
- No essays or philosophical content
- Leaves Work/Other sections for manual entry

