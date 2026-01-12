---
name: daily-brief
description: Generate personalized daily news briefing with UFC context loading
allowed-tools: [WebSearch, WebFetch, Read, Write, Glob]
---

# Daily Brief Command

## Purpose
Generate a personalized daily news briefing by analyzing Gavin's interests from UFC context files and curating relevant current events from the past 7 days ONLY.

## Context Loading Protocol
**Auto-load UFC Context** (for dynamic interest extraction):
- `/.claude/context/profile/personal-profile.md` - For interest alignment, expertise areas, and communication style
- `/.claude/context/profile/goals-objectives.md` - For relevance scoring against current objectives
- `/.claude/context/active-projects/ai-coding-projects.md` - AI/tech focus areas
- `/.claude/context/active-projects/career-development.md` - Career transition context

## CRITICAL: Date Enforcement

**STRICT 7-DAY WINDOW REQUIREMENT**:
1. Calculate today's date from system
2. Calculate the date 7 days ago
3. When searching news, EXPLICITLY include date range in search queries (e.g., "AI news December 2025")
4. **REJECT any article older than 7 days** - do not include in brief regardless of relevance
5. Verify publication dates before including any article

Example date enforcement:
- Today: 2025-12-03
- Valid articles: 2025-11-26 to 2025-12-03 ONLY
- Articles from October 2025 or earlier: REJECT

## Implementation

### Step 1: Load Context
Read the UFC context files listed above to extract current interests, goals, and focus areas.

### Step 2: Search for News
Use **WebSearch tool directly** with date-constrained queries:
- Include current month/year in search queries
- Search for each major interest area separately
- Example queries:
  - "AI artificial intelligence news December 2025"
  - "Python programming developments December 2025"
  - "Financial technology fintech news December 2025"
  - "Risk management regulatory news December 2025"

### Step 3: Validate and Filter
- Check publication date of each article
- **DISCARD any article older than 7 days**
- Score remaining articles for relevance (0.0-1.0)
- Keep only articles with relevance >= 0.3

### Step 4: Generate Brief
Create markdown file with:
- Date and generation timestamp
- Interest areas extracted from UFC context
- 10-15 relevant, DATE-VERIFIED articles
- Relevance scores and actionable insights

### Step 5: Save Output
Write to: `/Users/gavinslater/Library/Mobile Documents/iCloud~md~obsidian/Documents/GavinsiCloudVault/Daily Brief/daily-brief-YYYY-MM-DD.md`

## Expected Output
- **File**: `daily-brief-YYYY-MM-DD.md` in Obsidian vault Daily Brief folder
- **Content**: 10-15 relevant articles from LAST 7 DAYS ONLY
- **Format**: Structured with actionable insights and goal connections
- **Context**: Aligned with current AI transition and quantified self objectives

## Usage
Run `/daily-brief` to generate today's personalized briefing with full UFC context loading.

---
*Full implementation details: `/Users/gavinslater/projects/life/daily-brief-system/CLAUDE.md`*
