---
name: daily-note
description: Create standardized daily note in Obsidian vault with UFC context integration
allowed-tools: [Task, Read, Write, Bash]
---

# Daily Note Command

## Purpose
Create a standardized daily note in Gavin's Obsidian knowledge vault with integrated quantified self tracking and goal alignment.

## Context Loading Protocol
**Auto-load UFC Context**:
- `/profile/personal-profile.md` - For personalized note structure and focus areas
- `/profile/goals-objectives.md` - For goal progress tracking integration
- `/active-projects/daily-journal-context.md` - For current journal system context

## Implementation
Delegate to Knowledge Manager Agent with enhanced UFC awareness:

**File Path Pattern**:
`/Users/gavinslater/Library/Mobile Documents/iCloud~md~obsidian/Documents/GavinsiCloudVault/Calendar/YYYY/MM-MonthName/YYYY-MM-DD-DayName.md`

**Template Structure**:
- **YAML Frontmatter**: `dailynote` tag, date metadata, goal tracking fields
- **Goal Progress**: Quick status on current 30K feet objectives
- **Actions**: Todo items with GTD context tags (`#todo/personal/nextaction`)
- **Quantified Self**: Health metrics, productivity data, progress indicators
- **Sections**: YouTube/TV, Meals, Exercise, Work, Other
- **Insights**: Connections to ongoing projects and learning

## Expected Output
- **Daily Note**: Properly formatted with today's date
- **Goal Integration**: Progress tracking aligned with UFC objectives
- **Quantified Self**: Data capture for continuous optimization
- **Cross-references**: Wikilinks to relevant projects and goals

## Usage
Run `/daily-note` to create today's note with full UFC context integration. If note exists, open for review/editing.