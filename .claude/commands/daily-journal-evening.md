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
1. Fetch location data via location-agent:
   Run: python3 location_agent.py --analyze-date YYYY-MM-DD
   Returns structured data:
   - day_type: e.g., 'weekend_parkrun', 'work_wfh', 'work_office'
   - primary_location: Where most time was spent
   - timeline: Segments with location_name, start_time, end_time, duration_minutes
   - detected_activities: Parkrun, dog walking, golf with times

2. Fetch health metrics via health-agent (steps, energy, heart rate)

3. Fetch calendar summary via gmail-calendar-agent (today's events)

4. Fetch weather via weather skill (today's conditions)

5. Calculate habit streaks from last 7 daily notes

6. **ENRICH LOCATION DATA** - Add context from diary where available:
   - PRESERVE: All timestamps, durations, location names from location-agent
   - ENRICH: Cross-reference timeline with calendar events and daily note sections
   - Example enrichment:
     * '08:25-08:53: Bushy Park (27m)' → '08:25-08:53: Bushy Park - waiting for parkrun (27m)'
     * '12:36-13:10: Waitrose Car Park (34m)' → '12:36-13:10: Waitrose - grocery shopping (34m)'
   - If no diary context, keep location-agent output unchanged

7. Update daily note with CONCISE sections:
   - Location Information: Timeline from location-agent + day_type
   - Health & Fitness > Today's Health Metrics (bullet list)
   - Health & Fitness > Health Analysis (2-3 sentences max)
   - Health & Fitness > Tracking (streak status + checkbox)
   - Health & Fitness > Evening Reflection (brief accomplishments)

OUTPUT FORMAT - CONCISE ONLY:
**Health**: [Steps], [Active energy], [Exercise min]
**Location**: [day_type] - [primary_location]
**Activities**: [detected activities from location-agent]
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

