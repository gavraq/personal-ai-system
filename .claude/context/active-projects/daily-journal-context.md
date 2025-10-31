# Daily Journal & Knowledge Management Context

## Current Status
- **Platform**: Obsidian vault
- **Location**: `/Users/gavinslater/Library/Mobile Documents/iCloud~md~obsidian/Documents/GavinsiCloudVault`
- **Structure**: GTD system with daily notes, project tracking
- **Implementation**: Dual-workflow orchestration agent (Oct 2025)

## Daily Journal System

### Architecture (Oct 2025 Enhanced)
- **Specialized Agent**: `daily-journal-agent` - Central orchestration hub
- **Morning Workflow**: `/daily-journal-morning` - Start-of-day planning with weather, calendar, health predictions
- **Evening Workflow**: `/daily-journal-evening` - End-of-day reflection with movement, health metrics, task completion
- **Legacy Command**: `/daily-note` - Quick manual template creation (maintained)

### Daily Note Structure
**Location**: `/Calendar/YYYY/MM-MonthName/YYYY-MM-DD-DayName.md`

**Standard Sections**:
- Weather (Met Office UK forecast)
- Actions (GTD Dashboard tasks with context tags)
- Youtube videos & TV (manual entry)
- Meals (manual entry)
- Location Information (location-agent movement summary)
- Health & Fitness (health-agent metrics + parkrun data)
- Work (manual entry, calendar-enhanced)
- Other (cross-agent insights + reflections)

### Agent Orchestration
**Morning Planning** (Manual trigger: `/daily-journal-morning`):
- PARALLEL: health-agent (sleep + energy), email-management-agent (calendar + emails), location-agent (day pattern)
- SEQUENTIAL: GTD Dashboard analysis, Met Office weather, 7-day pattern analysis
- OUTPUT: Energy outlook, top 3 priorities, project opportunities, proactive suggestions

**Evening Reflection** (Manual trigger: `/daily-journal-evening`):
- PARALLEL: location-agent (movement), health-agent (metrics), email-management-agent (events), gtd-task-manager-agent (completion)
- SEQUENTIAL: 7-day pattern analysis, habit streak calculation, energy prediction validation
- OUTPUT: Accomplishments, health metrics, habit tracking, pattern insights, tomorrow's focus

### Pattern Learning & Intelligence
- **Habit Tracking**: Evening exercises streak, parkrun consistency, daily note creation streak
- **Energy Patterns**: Sleep quality → energy correlation, calendar density impact
- **Movement Patterns**: Office vs WFH day detection, typical location patterns by day of week
- **Productivity Patterns**: Task completion rates by context, meeting density impact
- **Health Trends**: Step count vs weekly average, exercise frequency, parkrun performance

### Data Integration
**Connected Agents**:
- `health-agent`: Apple Health (5.3M records) + parkrun API
- `location-agent`: Owntracks geolocation + movement analysis
- `email-management-agent`: Gmail MCP (calendar + communications)
- `gtd-task-manager-agent`: Obsidian Tasks + GTD Dashboard
- `knowledge-manager-agent`: Obsidian vault file operations

**External Data Sources**:
- Met Office UK: Weather forecasting for Esher/London
- GTD Dashboard: `/GTD/Dashboard.md` task prioritization
- Historical Daily Notes: 7-day rolling pattern analysis

## Key Features

### Proactive Intelligence
- **Energy Optimization**: Sleep-based energy prediction → task-energy matching
- **Project Advancement**: Calendar gap detection → project opportunity suggestions
- **Habit Formation**: Streak tracking + encouragement for consistent behaviors
- **Pattern Recognition**: Cross-domain insights (e.g., WFH days → 2x deep work completion)

### Quantified Self Integration
- **Health Metrics**: Steps, active energy, exercise minutes, heart rate (Apple Watch priority)
- **Movement Analytics**: Time at locations, travel patterns, commute tracking
- **Productivity Tracking**: Task completion rates, meeting density analysis
- **Habit Consistency**: Daily note creation, evening exercises, parkrun attendance

### GTD Alignment
- **Dashboard Integration**: Parse task queries by context (@computer, @home, @work, @out, @waiting)
- **Priority Determination**: Urgent+Important → Calendar-Aligned → Energy-Matched → Project-Advancing → Quick Wins
- **Action Format**: `- [ ] Task @context #project/name 📅 YYYY-MM-DD`
- **Completion Tracking**: Mark completed tasks, generate follow-ups, identify blockers

## Agent Integration

### Specialized Agent Portfolio
- **Primary Orchestrator**: Daily Journal Agent (`daily-journal-agent`)
- **File Operations**: Knowledge Manager Agent (`knowledge-manager-agent`)
- **Health Data**: Health Agent (`health-agent`)
- **Movement Data**: Location Agent (`location-agent`)
- **Communications**: Email Management Agent (`email-management-agent`)
- **Task Management**: GTD Task Manager Agent (`gtd-task-manager-agent`)

### Command Interface
- **`/daily-journal-morning`**: Morning planning workflow (6-7 AM recommended)
- **`/daily-journal-evening`**: Evening reflection workflow (6-7 PM recommended)
- **`/daily-note`**: Quick manual template creation (legacy, maintained)

### Cross-Agent Coordination
- **Personal Consultant**: May delegate daily journal workflows
- **Weekly Review Agent**: Consumes daily note summaries
- **Goal Tracking**: Feeds progress data to horizons review
- **Learning Acceleration**: Pattern insights inform habit optimization

## Current Usage

### Daily Workflow
- **Morning** (6:00-7:00 AM): Run `/daily-journal-morning` for planning briefing
- **Evening** (6:00-7:00 PM): Run `/daily-journal-evening` for reflection capture

### Weekly Workflow
- **Sunday Planning**: Review upcoming week patterns
- **Weekly Review**: Analyze 7-day daily notes for insights
- **Goal Tracking**: Document progress toward 30K/40K/50K feet objectives

### Pattern-Informed Optimization
- **Office Days** (Mon/Tue/Thu): Meeting-heavy, commute planning, lower deep work
- **WFH Days** (Wed/Fri): Deep work optimized, 2x task completion potential
- **Weekends**: Saturday parkrun pattern, rest day recognition, family time

## Success Metrics
- **Daily Note Consistency**: 95% of days (current target)
- **Agent Integration Success**: 90% data completeness (current target)
- **Pattern Accuracy**: Validated through user feedback
- **Proactive Value**: Measured via suggestion follow-through rates
- **Time Efficiency**: Morning <2min, Evening <3min (target)

---
*Full vault location: iCloud Obsidian Documents/GavinsiCloudVault*
*Agent definitions: `/.claude/agents/daily-journal-agent.md`*
*Commands: `/.claude/commands/daily-journal-morning.md`, `/.claude/commands/daily-journal-evening.md`*