---
name: youtube-transcript
description: Extract transcripts from YouTube videos and save them as formatted markdown files to Obsidian vault or specified location. Use when user asks to get, extract, or save a YouTube video transcript.
---

# YouTube Transcript Extraction Skill

## Purpose
Extract transcripts from YouTube videos, format them as readable markdown with metadata, and save to Gavin's Obsidian vault or another specified location.

## When to Use
- User shares a YouTube URL and asks for the transcript
- User wants to save video content for later reference
- User wants to capture knowledge from video content

## Workflow

### Step 1: Extract Video ID
Parse the YouTube URL to get the video ID. Supported formats:
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`

### Step 2: Get Transcript
Use `uvx` to run the youtube-transcript-api:
```bash
uvx --from youtube-transcript-api youtube_transcript_api VIDEO_ID --format text
```

### Step 3: Get Video Metadata
Use `yt-dlp` to fetch video title, channel, date, and description:
```bash
uvx yt-dlp --skip-download --print "%(title)s|||%(channel)s|||%(upload_date)s|||%(description).500s" "YOUTUBE_URL"
```

### Step 4: Format Markdown
Create a well-structured markdown file with:
- YAML-style metadata header (title, channel, date, URL, description)
- Formatted transcript with section headers where appropriate
- Summary section if content structure is clear
- Relevant tags for Obsidian

### Step 5: Save File
Default location: `/Users/gavinslater/Library/Mobile Documents/iCloud~md~obsidian/Documents/GavinsiCloudVault/Resources/Transcripts/`

Filename format: `{Video Title} - Transcript.md`

## Markdown Template

```markdown
---
tags:
  - youtube-transcript
  - {topic-tags-lowercase-with-hyphens}
source: {YouTube URL}
channel: {Channel Name}
date: {YYYY-MM-DD}
---

# {Video Title}

## Video Details
- **Channel**: {Channel Name}
- **Date**: {Upload Date}
- **URL**: {YouTube URL}
- **Description**: {First 500 chars of description}

---

## Transcript

{Formatted transcript content with section headers}

---

## Related Notes
{Add [[wikilinks]] to related notes in the vault if applicable}
```

## Formatting Standards (Knowledge Manager Consistency)
- **YAML Frontmatter**: All notes MUST begin with YAML frontmatter containing tags
- **Tagging Convention**: Lowercase with hyphens (e.g., `ai-maturity`, `personal-ai`)
- **Required Tags**: Always include `youtube-transcript` plus topic-relevant tags
- **Common Tags**: `ai`, `productivity`, `career`, `technology`, `learning`, `personal-development`
- **Wikilinks**: Use `[[wikilinks]]` for connections to related vault notes
- **Date Format**: Use ISO format YYYY-MM-DD in frontmatter

## Error Handling
- If transcript unavailable: Inform user that video may not have captions enabled
- If metadata fetch fails: Proceed with transcript only, ask user for title
- If video is private/unavailable: Report error to user

## Notes
- Some videos have auto-generated captions which may have errors
- Very long videos will have lengthy transcripts
- Consider breaking extremely long transcripts into sections
