---
name: daily-journal-morning
description: Generate concise morning briefing with sleep, weather, and priorities
allowed-tools: [Task, Read, WebFetch, Bash]
---

# Daily Journal Morning Command

Two-phase morning workflow: (1) Complete yesterday's note with actual data, (2) Plan today with fresh briefing.

## Implementation: Two-Phase Execution

### Phase 1: Complete Yesterday's Note (PARALLEL Data Gathering)

Calculate yesterday's date and gather complete data now available.

Execute these Task calls in PARALLEL in a SINGLE response:

```
Task: location-agent "Analyze location data for [YESTERDAY YYYY-MM-DD]. Provide:
- Complete timeline of locations visited with timestamps
- Time spent at each major location (home, office, stations)
- Travel segments and commute times
- Movement pattern summary
Format as concise summary ready for daily note insertion."

Task: health-agent "Provide complete health metrics for [YESTERDAY YYYY-MM-DD]:
- Step count (Apple Watch priority)
- Active energy burned
- Exercise minutes
- Heart rate summary (resting, walking average, HRV)
- Distance walked/run
- Comparison to weekly averages
Format as concise summary ready for daily note insertion."
```

Then update yesterday's daily note sections:
```
Task: daily-journal-agent "Update yesterday's daily note [YESTERDAY YYYY-MM-DD] with complete data.

YESTERDAY DATA PROVIDED:
---
LOCATION DATA: [from location-agent]
HEALTH DATA: [from health-agent]
---

UPDATE THESE SECTIONS ONLY:
1. Location Information: Replace placeholder/evening-only data with complete timeline
2. Today's Health Metrics: Replace incomplete/morning data with full day metrics
3. Health Analysis: Add pattern insights comparing to weekly averages
4. Tracking: Verify evening exercises checkbox status

DO NOT change other sections (Weather, Work, Other, Morning Plan, Evening Reflection already complete).

Return brief confirmation of updates made."
```

### Phase 2: Today's Morning Briefing

**Target Date**: Today (auto-calculated as YYYY-MM-DD, DayName)
**Daily Note**: `Calendar/YYYY/MM-MonthName/YYYY-MM-DD-DayName.md`

```
Task: daily-journal-agent "Execute morning briefing for [TODAY YYYY-MM-DD DayName].

REQUIREMENTS:
1. Fetch sleep data via health-agent (last night)
2. Fetch weather from Met Office UK (Esher)
3. Read GTD Dashboard for priorities
4. Calculate habit streaks from last 7 daily notes
5. Update daily note with CONCISE sections:
   - Weather (3 lines: morning, day summary, impact)
   - Health & Fitness > Morning Energy Outlook (4-5 bullets only)
   - Health & Fitness > Morning Plan (priorities list only)

OUTPUT FORMAT - CONCISE ONLY:
**Energy**: [High/Medium/Low] ([X]h [Y]m sleep)
**Weather**: [Temp]°C, [Conditions]
**Top Priorities**:
  1. [Task] ([time]) - [context]
  2. [Task] ([time]) - [context]
  3. [Task] ([time]) - [context]
**Health Reminder**: [Streak or exercise note if relevant]

✅ Daily note updated: Calendar/YYYY/MM-MonthName/YYYY-MM-DD-DayName.md"
```

## Expected Output

### Phase 1 Output (Yesterday Update):
```markdown
✅ Yesterday's note completed ([YYYY-MM-DD]):
- Location: Full timeline with [X] locations, [Y]h [Z]m tracked
- Health: Complete metrics - [X,XXX] steps, [XXX] kcal, [XX] exercise min
- Tracking: Evening exercises verified ✅

Updated: Calendar/YYYY/MM-MonthName/YYYY-MM-DD-DayName.md
```

### Phase 2 Output (Today's Briefing):
Concise user summary matching Oct 7-10 format:
```markdown
**Energy**: [High/Medium/Low] ([X]h [Y]m sleep)
**Weather**: [Temp]°C, [Conditions]
**Top Priorities**:
  1. [Task] ([time]) - [context]
  2. [Task] ([time]) - [context]
  3. [Task] ([time]) - [context]
**Health Reminder**: [Streak or exercise note if relevant]

✅ Today's note updated: Calendar/YYYY/MM-MonthName/YYYY-MM-DD-DayName.md
```

## Key Benefits

**Yesterday Completion**:
- Full location data (complete tracking available by morning)
- Complete health metrics (overnight sync captures full day)
- Accurate habit tracking (evening exercises confirmed)
- Pattern analysis with complete data

**Today Planning**:
- Fresh energy assessment with last night's sleep
- Current weather conditions
- Priority focus from GTD Dashboard
- Informed by yesterday's completion patterns

