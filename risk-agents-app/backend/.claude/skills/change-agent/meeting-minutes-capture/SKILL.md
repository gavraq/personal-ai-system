---
name: meeting-minutes-capture
description: Capture meeting minutes from transcripts or notes and extract structured action items, decisions, and next steps
domain: change-agent
category: meeting-management
taxonomy: change-agent/meeting-management
parameters:
  - meeting_transcript
  - meeting_date
  - attendees
output_format: structured_markdown
estimated_duration: 2-3 minutes
---

# Meeting Minutes Capture Skill

## Purpose
Transform unstructured meeting notes or transcripts into structured meeting minutes with clear action items, decisions, and next steps.

## When to Use This Skill
- After a meeting when you have raw notes or transcript
- When you need to formalize ad-hoc discussion notes
- When extracting action items from voice recordings
- When distributing meeting outcomes to stakeholders

## How It Works
This skill takes raw meeting content (transcript, notes, or recording) and structures it into a professional meeting minutes document with:

1. **Meeting Metadata**: Date, attendees, duration, location
2. **Agenda Items**: Topics discussed with key points
3. **Decisions Made**: Clear record of decisions and rationale
4. **Action Items**: Tasks with owners and due dates
5. **Next Steps**: Follow-up meetings or activities

## Instructions
For detailed instructions on using this skill:
- See `instructions/capture.md` - How to capture minutes from different formats
- See `instructions/extract-actions.md` - How to extract and assign action items

## Resources
- `resources/meeting-template.md` - Standard output template
- `resources/examples.md` - Example transformations

## Knowledge References
This skill utilizes knowledge from the Change Agent domain:
- **meeting-types.md** - Understanding different meeting types and what to capture for each
- **action-items-standards.md** - Standards for complete, actionable action items (WHAT, WHO, WHEN, WHY)
- **decision-capture.md** - Standards for properly documenting decisions with rationale and authority

These knowledge documents provide best practices and standards that enhance the quality of the skill execution.

## Expected Output
A structured markdown document containing:

```markdown
# Meeting Minutes: [Meeting Title]

**Date**: [Date]
**Time**: [Start] - [End]
**Location**: [Location/Virtual]
**Attendees**: [List of attendees]

## Agenda

### 1. [Topic]
- Key discussion points
- Important context

## Decisions

1. **[Decision Title]**
   - Decision: [What was decided]
   - Rationale: [Why this decision was made]
   - Impact: [Who/what is affected]

## Action Items

| Item | Owner | Due Date | Status |
|------|-------|----------|--------|
| [Action description] | [Name] | [Date] | Pending |

## Next Steps

- [ ] [Next action]
- [ ] Schedule follow-up meeting for [date]

## Notes

[Any additional context or notes]
```

## Success Criteria
- All attendees identified
- Key decisions clearly documented
- Action items have owners and due dates
- Output is ready to share with stakeholders

## Tips for Best Results
- Provide as much context as possible (date, attendees, meeting purpose)
- Include any decisions that were made during the meeting
- Mention action items explicitly if discussed
- Note any follow-up meetings or next steps
