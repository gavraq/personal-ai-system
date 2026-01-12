---
name: daily-journal-morning
description: Generate concise morning briefing with sleep, weather, calendar, and priorities
allowed-tools: [Task, Read, WebFetch, mcp__google-calendar__*, mcp__google-calendar__get-current-time, mcp__google-calendar__list-events]
---

# Daily Journal Morning Command

Two-phase morning workflow: (1) Complete yesterday's note with actual data, (2) Plan today with fresh briefing.

## CRITICAL: Date Verification First

**BEFORE ANY OTHER ACTION**, verify today's date using Google Calendar MCP:

```
mcp__google-calendar__get-current-time
```

This returns the authoritative current date/time. Use this verified date for ALL subsequent operations.

**Calculate dates**:
- **Today**: Use the date returned from get-current-time
- **Yesterday**: Today minus 1 day
- **Day names**: Calculate correctly (Monday, Tuesday, etc.)

**NEVER assume dates** - always verify first.

## Implementation: Two-Phase Execution

### Phase 1: Complete Yesterday's Note (PARALLEL Data Gathering)

Using the VERIFIED yesterday's date, gather complete data now available.

Execute these Task calls in PARALLEL in a SINGLE response:

```
Task: location-agent "Analyze location data for [VERIFIED YESTERDAY YYYY-MM-DD].

Run: python3 location_agent.py --analyze-date YYYY-MM-DD

The location agent returns structured data:
- day_type: e.g., 'weekend_parkrun', 'work_wfh', 'work_office'
- primary_location: Where most time was spent
- timeline: List of segments with start_time, end_time, location_name, duration_minutes
- detected_activities: Parkrun, dog walking, golf sessions detected

Format the timeline for daily note as:
**Timeline:**
- HH:MM-HH:MM: Location Name (Xh Ym)
- HH:MM-HH:MM: Location Name (Xh Ym)

**Day Type:** [day_type]
**Primary Location:** [primary_location]
**Activities:** [list any detected activities with times]"

Task: health-agent "Provide complete health metrics for [VERIFIED YESTERDAY YYYY-MM-DD]:
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
Task: daily-journal-agent "Update yesterday's daily note [VERIFIED YESTERDAY YYYY-MM-DD DayName] with complete data.

YESTERDAY DATA PROVIDED:
---
LOCATION DATA: [from location-agent]
HEALTH DATA: [from health-agent]
---

UPDATE THESE SECTIONS ONLY:
1. Location Information: Replace placeholder data with complete timeline
2. Today's Health Metrics: Replace incomplete data with full day metrics
3. Health Analysis: Add pattern insights comparing to weekly averages
4. Tracking: Verify evening exercises checkbox status

DO NOT change other sections (Weather, Work, Other, Morning Plan, Evening Reflection already complete).

Return brief confirmation of updates made."
```

### Phase 2: Today's Morning Briefing

**Target Date**: VERIFIED today from get-current-time (YYYY-MM-DD, DayName)
**Daily Note**: `Calendar/YYYY/MM-MonthName/YYYY-MM-DD-DayName.md`

**Step 1: Check Calendar FIRST**
```
mcp__google-calendar__list-events with calendarId: "primary", timeMin: [TODAY 00:00], timeMax: [TODAY 23:59]
```

Extract:
- Fixed time commitments (meetings, appointments)
- Available work blocks between commitments
- Note if clear schedule or meeting-heavy day

**Step 2: Fetch Sleep Data**
```
Task: health-agent "Provide sleep data for last night [YESTERDAY to TODAY]:
- Total sleep duration
- Time in bed vs actual sleep
- Sleep window (bed time → wake time)
- Sleep stages breakdown (Deep/Core/REM/Awake)
- Quality assessment
Format as concise summary for morning energy assessment."
```

**Step 3: Extract GTD Tasks (Grep-based)**

Since Dashboard.md contains dynamic Obsidian Tasks queries that can't be rendered, grep directly for uncompleted tasks. **Optimization**: Tasks are captured in daily notes, so focus on Calendar folder (not entire vault):

```
Grep for uncompleted tasks:
Path: /Users/gavinslater/Library/Mobile Documents/iCloud~md~obsidian/Documents/GavinsiCloudVault/Calendar
Pattern: "- \[ \]"
Exclude: #tracking (these are milestone checkboxes, not actionable tasks)
```

Then categorize by GTD context (matching Dashboard structure):
- **@computer**: Digital/desk tasks (primary for WFH days)
- **@home**: House/physical tasks
- **@out**: Errands requiring leaving home
- **@scheduled**: Time-specific tasks
- **@waiting**: Delegated/waiting for response
- **@reading**: Reading list items
- **@someday**: Future/maybe items (lower priority)
- **Due dates**: Look for 📅 YYYY-MM-DD patterns, prioritize overdue/today

Extract:
- All uncompleted tasks grouped by context (excluding @someday for daily planning)
- Any tasks with due dates today or overdue (highest priority)
- Top 3-5 priority items to fit into available calendar blocks

**Step 4: Fetch Weather**
```
Skill: weather
```
Uses Met Office DataHub API to get reliable weather data for Claygate.
Returns: Temperature, conditions, wind, humidity, precipitation probability.
Format: Brief 2-3 lines with WFH impact note (e.g., dog walk timing).

If weather unavailable, note "Weather data unavailable" and continue.

**Step 5: Create Daily Note**
```
Task: daily-journal-agent "Create morning briefing for [VERIFIED TODAY YYYY-MM-DD DayName].

DATA PROVIDED:
---
DATE VERIFIED: [from get-current-time]
CALENDAR: [from list-events - meetings and available blocks]
SLEEP: [from health-agent]
GTD TASKS: [from Dashboard.md - top priorities]
WEATHER: [from weather skill]
---

Create daily note with sections:
1. Weather (brief, WFH context)
2. Last Night's Sleep (data + energy assessment)
3. Morning Energy Outlook (based on sleep only)
4. Morning Plan with:
   - Today's Schedule (calendar events + available blocks)
   - Top Priorities (tasks fitted to available time)
5. Empty sections for manual entry (Work, Other, Meals, Youtube)

DO NOT include:
- Today's Health Metrics (morning = no useful data yet)
- Commute/office references (WFH full-time)
- Habit streak calculations (evening task)

Return concise briefing summary."
```

## Expected Output

### Phase 1 Output (Yesterday Update):
```markdown
✅ Yesterday's note completed ([VERIFIED YYYY-MM-DD DayName]):
- Location: Full timeline with [X] locations, [Y]h [Z]m tracked
- Health: Complete metrics - [X,XXX] steps, [XXX] kcal, [XX] exercise min
- Tracking: Evening exercises verified ✅

Updated: Calendar/YYYY/MM-MonthName/YYYY-MM-DD-DayName.md
```

### Phase 2 Output (Today's Briefing):
```markdown
**Date**: [DayName], [Month] [Day], [Year] (verified)
**Energy**: [High/Medium/Low] ([X]h [Y]m sleep)
**Weather**: [Temp]°C, [Conditions] - [WFH impact]

**Calendar**:
- [HH:MM-HH:MM]: [Event] (or "Clear schedule - full day for focused work")
- Available: [X]h morning, [Y]h afternoon

**Top Priorities** (fitted to available time):
1. [Task from Dashboard] - [context/project]
2. [Task from Dashboard] - [context/project]
3. [Task from Dashboard] - [context/project]

✅ Daily note updated: Calendar/YYYY/MM-MonthName/YYYY-MM-DD-DayName.md
```

## Key Principles

**Date Accuracy**:
- ALWAYS verify date via Google Calendar MCP first
- Never assume day of week - calculate from verified date
- Use verified dates for ALL file paths and queries

**Calendar-First Planning**:
- Check calendar BEFORE looking at tasks
- Map fixed commitments first
- Fit tasks into available blocks
- Note meeting-heavy vs open schedule days

**WFH Context**:
- No commute references
- Flexible schedule focused on content creation and AI projects
- Weather impacts outdoor activities, not commute
- Intentional movement breaks needed without commute activity

**Morning Efficiency**:
- Skip today's health metrics (no useful data yet)
- Skip habit streaks (calculate in evening)
- Focus on actionable: sleep quality, calendar, priorities

## Error Handling

If calendar not accessible:
```markdown
⚠️ Calendar unavailable - assuming clear schedule
```

If sleep data not available:
```markdown
⚠️ Sleep data not synced - manual energy assessment needed
```

Create note with available data even if some sources fail.
