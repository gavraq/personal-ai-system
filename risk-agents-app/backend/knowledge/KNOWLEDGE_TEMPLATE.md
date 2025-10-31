# Knowledge Document Template

This template defines the format for all knowledge documents in the Risk Agents Knowledge Layer.

---

## File Format

Knowledge documents use **Markdown** with **YAML frontmatter** for metadata.

### Required Structure

```markdown
---
# === REQUIRED FIELDS ===
title: Document Title Here
domain: change-agent
category: meeting-management
slug: document-slug-here
description: Short 1-2 sentence description of the document

# === OPTIONAL FIELDS ===
tags:
  - tag1
  - tag2
  - tag3

related_skills:
  - skill-slug-1
  - skill-slug-2

related_documents:
  - document-slug-1
  - document-slug-2

author: Author Name (optional)
last_updated: 2025-10-27
difficulty: Beginner  # Beginner | Intermediate | Advanced
reading_time: 5 min   # Estimated reading time
---

# Document Title

## Overview

Provide a brief overview of the topic (2-3 paragraphs).

## Key Concepts

### Concept 1
Description of concept 1...

### Concept 2
Description of concept 2...

## Best Practices

1. **Practice 1**: Description
2. **Practice 2**: Description
3. **Practice 3**: Description

## Common Pitfalls

- **Pitfall 1**: Description and how to avoid it
- **Pitfall 2**: Description and how to avoid it

## Examples

### Example 1: [Scenario Name]

**Context**: Describe the situation

**Approach**: How to handle it

**Outcome**: Expected results

## Related Skills

- [Skill Name](link) - How this skill uses this knowledge
- [Skill Name](link) - Another related skill

## Additional Resources

- External link 1
- External link 2
- Internal reference

## Summary

Key takeaways (2-3 bullet points):
- Takeaway 1
- Takeaway 2
- Takeaway 3
```

---

## YAML Frontmatter Fields

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `title` | string | Document title | `"Effective Meeting Management"` |
| `domain` | string | Domain (lowercase-kebab) | `"change-agent"` |
| `category` | string | Category (lowercase-kebab) | `"meeting-management"` |
| `slug` | string | URL-friendly identifier | `"effective-meetings"` |
| `description` | string | Short summary (1-2 sentences) | `"Best practices for running effective meetings"` |

### Optional Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `tags` | array | Searchable tags | `["meetings", "facilitation"]` |
| `related_skills` | array | Skills that use this knowledge | `["meeting-minutes-capture"]` |
| `related_documents` | array | Related knowledge docs | `["meeting-types"]` |
| `author` | string | Document author | `"John Doe"` |
| `last_updated` | date | Last update date (YYYY-MM-DD) | `"2025-10-27"` |
| `difficulty` | string | Difficulty level | `"Beginner"` or `"Intermediate"` or `"Advanced"` |
| `reading_time` | string | Estimated reading time | `"5 min"` |

---

## Content Structure Guidelines

### 1. Overview Section
- **Purpose**: Introduce the topic
- **Length**: 2-3 paragraphs
- **Content**: What, why, and when to use this knowledge

### 2. Key Concepts Section
- **Purpose**: Define core concepts
- **Format**: H3 subsections for each concept
- **Content**: Clear definitions and explanations

### 3. Best Practices Section
- **Purpose**: Actionable guidance
- **Format**: Numbered or bulleted list
- **Content**: Specific, practical recommendations

### 4. Common Pitfalls Section
- **Purpose**: Warn about common mistakes
- **Format**: Bulleted list with bold headings
- **Content**: What to avoid and why

### 5. Examples Section
- **Purpose**: Demonstrate practical application
- **Format**: H3 subsections for each example
- **Content**: Real-world scenarios with context/approach/outcome

### 6. Related Skills Section
- **Purpose**: Link to skills that use this knowledge
- **Format**: Bulleted list with links
- **Content**: Skill names and brief descriptions

### 7. Additional Resources Section (Optional)
- **Purpose**: External references
- **Format**: Bulleted list
- **Content**: Links to books, articles, tools

### 8. Summary Section
- **Purpose**: Key takeaways
- **Format**: 2-3 bullet points
- **Content**: Main points to remember

---

## Writing Style Guidelines

### Tone
- **Professional but accessible**
- **Authoritative but not condescending**
- **Practical over theoretical**

### Language
- **Clear and concise**
- **Active voice preferred**
- **Avoid jargon (or explain when necessary)**

### Formatting
- **Use headings for structure** (H2, H3)
- **Use bold for emphasis** (sparingly)
- **Use lists for readability** (bullets or numbers)
- **Use tables for comparisons** (when appropriate)
- **Use code blocks for examples** (when relevant)

### Length
- **Minimum**: 300 lines (substantial content)
- **Optimal**: 400-600 lines (comprehensive)
- **Maximum**: 800 lines (avoid overwhelming)

---

## Markdown Features

### Supported Elements

**Headers**:
```markdown
# H1 - Document Title (use once)
## H2 - Main Sections
### H3 - Subsections
```

**Text Formatting**:
```markdown
**Bold text**
*Italic text*
`inline code`
```

**Lists**:
```markdown
- Bullet point
- Bullet point

1. Numbered item
2. Numbered item
```

**Links**:
```markdown
[Link text](url)
[Internal doc](../category/slug)
```

**Tables**:
```markdown
| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
```

**Code Blocks**:
````markdown
```python
# Python code example
def hello():
    print("Hello")
```
````

**Blockquotes**:
```markdown
> Important quote or note
```

---

## File Naming Conventions

### Format
`{slug}.md`

### Rules
- **Lowercase**: All lowercase letters
- **Hyphens**: Use hyphens for spaces (kebab-case)
- **Descriptive**: Clear indication of content
- **Unique**: No duplicates within same category

### Examples
- ✅ `effective-meetings.md`
- ✅ `project-charter-guide.md`
- ✅ `stakeholder-management.md`
- ❌ `Meeting Management.md` (no spaces/caps)
- ❌ `doc1.md` (not descriptive)

---

## Directory Structure

```
backend/knowledge/
├── KNOWLEDGE_TEMPLATE.md          # This template
├── {domain}/                      # Domain directory
│   ├── {category}/                # Category directory
│   │   ├── {slug}.md             # Knowledge document
│   │   ├── {slug}.md
│   │   └── {slug}.md
│   └── {category}/
│       └── {slug}.md
```

### Example
```
backend/knowledge/
├── KNOWLEDGE_TEMPLATE.md
├── change-agent/
│   ├── meeting-management/
│   │   ├── effective-meetings.md
│   │   ├── meeting-minutes-guide.md
│   │   └── meeting-types.md
│   ├── project-management/
│   │   ├── project-charter-guide.md
│   │   └── stakeholder-management.md
│   └── requirements-gathering/
│       └── requirements-techniques.md
```

---

## Validation Checklist

Before committing a knowledge document, verify:

### Metadata
- [ ] All required YAML fields present
- [ ] `domain` matches directory structure
- [ ] `category` matches directory structure
- [ ] `slug` matches filename (without .md)
- [ ] `description` is concise (1-2 sentences)
- [ ] `tags` are relevant and searchable
- [ ] `related_skills` links are valid
- [ ] `related_documents` links are valid

### Content
- [ ] Overview section present (2-3 paragraphs)
- [ ] Key concepts clearly defined
- [ ] Best practices are actionable
- [ ] Examples are practical and clear
- [ ] Summary captures key takeaways
- [ ] No placeholder text (TODO, TBD, etc.)

### Formatting
- [ ] Proper Markdown syntax
- [ ] Headers use correct levels (H1 once, H2/H3 for structure)
- [ ] Lists formatted correctly
- [ ] Links work and are relevant
- [ ] Code blocks (if any) are properly formatted
- [ ] No trailing whitespace

### Quality
- [ ] Technically accurate
- [ ] Professional tone
- [ ] Clear and concise language
- [ ] Free of typos and grammar errors
- [ ] Appropriate length (300-600 lines)

---

## Example: Minimal Document

```markdown
---
title: Meeting Types Overview
domain: change-agent
category: meeting-management
slug: meeting-types
description: An overview of common meeting types and when to use each one
tags:
  - meetings
  - planning
related_skills:
  - meeting-minutes-capture
last_updated: 2025-10-27
difficulty: Beginner
reading_time: 5 min
---

# Meeting Types Overview

## Overview

Meetings come in many forms, each serving a different purpose. Understanding when to use each type helps ensure productive use of time and achieves desired outcomes.

This guide covers the most common meeting types in professional settings and provides guidance on when to use each format.

## Key Meeting Types

### Informational Meetings
**Purpose**: Share information with stakeholders
**When to use**: Updates, announcements, training
**Duration**: 15-30 minutes
**Best practices**: Prepare clear materials, allow Q&A time

### Decision-Making Meetings
**Purpose**: Make important decisions as a group
**When to use**: Strategic choices, approvals, problem-solving
**Duration**: 30-60 minutes
**Best practices**: Pre-circulate options, use structured decision process

### Brainstorming Meetings
**Purpose**: Generate creative ideas and solutions
**When to use**: Innovation, problem-solving, planning
**Duration**: 45-90 minutes
**Best practices**: Encourage all ideas, defer judgment, build on others

## Best Practices

1. **Match format to purpose**: Choose the right meeting type for your goal
2. **Prepare in advance**: Send agendas and materials ahead
3. **Respect time**: Start and end on schedule
4. **Follow up**: Document decisions and next steps

## Summary

- Different meeting types serve different purposes
- Match the meeting format to your objective
- Proper preparation and follow-up are essential

---

**Related Skills**: [Meeting Minutes Capture](../skills/meeting-minutes-capture)
```

---

## Next Steps

1. Create knowledge documents using this template
2. Place in appropriate domain/category directories
3. Validate using checklist above
4. Test loading via knowledge_loader.py
5. Verify display in Knowledge Browser UI

---

**Template Version**: 1.0
**Last Updated**: October 27, 2025
**Status**: Ready for use
