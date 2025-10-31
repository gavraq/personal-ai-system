# GTD Task Management Context

## Current Status
- **Methodology**: Getting Things Done (GTD) by David Allen
- **Platform**: Obsidian with Tasks plugin integration
- **Agent**: GTD Task Manager Agent (`gtd-task-manager-agent`)
- **Location**: `/Users/gavinslater/Library/Mobile Documents/iCloud~md~obsidian/Documents/GavinsiCloudVault/GTD/`

## System Structure

### Core GTD Files
- **Dashboard.md**: Central task overview with Tasks plugin queries
- **Capture.md**: Quick capture location for unprocessed items
- **Mindsweep.md**: Focus area analysis for large projects
- **Context Files**: @Computer Tasks.md, @Home Tasks.md, @Work Tasks.md, @Waiting for Task List.md, @Someday Maybe Tasks.md

### Task Creation Workflow
- **Primary Location**: Daily note Actions section (`Calendar/YYYY/MM-Month/YYYY-MM-DD-Weekday.md`)
- **Format**: `- [ ] Task description @context`
- **Auto-organization**: Tasks automatically appear in Dashboard via Tasks plugin queries

## Context System

### GTD Contexts
- **@computer**: Tasks requiring computer/online work
- **@home**: Household and personal tasks
- **@work**: Professional tasks and projects
- **@out**: Errands and tasks requiring leaving home
- **@waiting**: Items waiting for others' responses
- **@someday**: Future/aspirational tasks (not immediate)
- **@reading**: Books, articles, research tasks
- **@scheduled**: Time/date specific tasks with due dates

### Processing Flow
1. **Capture** → Daily note Actions or Capture.md
2. **Clarify** → Convert to actionable tasks with contexts
3. **Organize** → Automatic via Tasks plugin queries
4. **Reflect** → Dashboard provides overview
5. **Engage** → Context-based task execution

## Tasks Plugin Integration

### Query Structure
- **Dashboard Queries**: `description includes @context` filters
- **Status Filters**: `not done`, `done on YYYY-MM-DD`
- **Due Dates**: `due today`, `due after today`
- **Processing Queue**: Tasks without context appear in "To Process"

### Task Format Requirements
- **New Tasks**: `- [ ] Description @context`
- **Completed**: `- [x] Description @context ✅ YYYY-MM-DD`
- **Due Dates**: `📅 YYYY-MM-DD` format
- **No Context**: Appears in "To Process" queue

## Agent Capabilities

### GTD Task Manager Agent Functions
1. **Task Creation**: Add tasks to daily note Actions section
2. **Task Completion**: Mark tasks as done across vault
3. **Task Review**: Context-based task lists and overviews
4. **Capture Processing**: Convert capture items to actionable tasks
5. **Daily Note Integration**: Auto-create daily notes when needed

### Primary Use Cases (ALWAYS use GTD Task Manager Agent for):
- Creating new tasks or todos (user requests like "create a task", "add todo", "I need to remember to...")
- Task organization and context assignment (@computer, @home, @work, etc.)
- Marking tasks as complete or reviewing task status
- Processing items from capture lists
- Task-related planning and workflow
- Daily note Actions section management

### Integration Points
- **Daily Note Command**: Uses `/daily-note` for note creation
- **Dashboard Monitoring**: Read-only access to overview
- **Vault Search**: Find tasks for completion
- **Context Organization**: Leverage existing @context system

## Current Focus Areas

### High-Priority Contexts
- **@computer**: AI learning, coding projects, LinkedIn optimization
- **@home**: Organization, decluttering, family tasks
- **@work**: ICBC projects, handover documentation

### Success Metrics
- **Capture Rate**: Items processed from Capture.md
- **Context Completion**: Tasks completed by context
- **Dashboard Health**: Overdue task management
- **Daily Integration**: Task creation in daily notes

## Integration with UFC System

### Goal Alignment
- **20K Feet**: Life domains (Health, Career, Family)
- **30K Feet**: Specific objectives (AI transition, content creation)
- **Task Level**: Daily actions supporting higher-level goals

### Quantified Self Connection
- **Completion Rates**: Track productivity patterns
- **Context Analysis**: Identify high-performance contexts
- **Progress Correlation**: Connect task completion to goal advancement

---
*GTD system supports all UFC goals through systematic task management and context-based execution*