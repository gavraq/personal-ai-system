# Skill Development Guide

**Purpose**: Complete guide for creating Claude Skills Framework skills for Risk Agents
**Audience**: Developers adding new skills to the Change Agent domain (or future domains)
**Last Updated**: October 26, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Skill File Structure](#skill-file-structure)
3. [YAML Frontmatter Schema](#yaml-frontmatter-schema)
4. [Parameter Definition](#parameter-definition)
5. [Output Formatting Standards](#output-formatting-standards)
6. [Progressive Disclosure](#progressive-disclosure)
7. [Knowledge Integration](#knowledge-integration)
8. [Validation Patterns](#validation-patterns)
9. [Testing Guidelines](#testing-guidelines)
10. [Best Practices](#best-practices)

---

## Overview

### What is a Skill?

A **skill** in the Claude Skills Framework is a discrete capability that Claude can execute. Skills encapsulate:
- **Problem definition** - What problem does this solve?
- **Input requirements** - What information is needed?
- **Processing logic** - How Claude should approach the task
- **Output format** - What structure should the result have?
- **Best practices** - Domain knowledge and standards

### Skill Philosophy

Skills follow these principles:
1. **Single Responsibility** - Each skill solves one clear problem
2. **Self-Contained** - All necessary information is within the skill definition
3. **Progressive Disclosure** - Complex skills reveal complexity gradually
4. **Knowledge-Linked** - Skills reference domain knowledge documents
5. **Testable** - Skills can be validated with test inputs/outputs

---

## Skill File Structure

### Minimum Viable Skill

```
skill-name/
└── SKILL.md                    # Main skill definition (REQUIRED)
```

### Complete Skill Structure

```
skill-name/
├── SKILL.md                    # Main skill definition with YAML frontmatter
├── instructions/               # Progressive disclosure (for complex skills)
│   ├── step-1-setup.md        # First step instructions
│   ├── step-2-process.md      # Processing instructions
│   └── step-3-finalize.md     # Finalization instructions
└── resources/                  # Templates, examples, reference docs
    ├── template.md             # Output template
    ├── examples.md             # Example inputs/outputs
    └── validation.md           # Validation rules and edge cases
```

### Directory Naming Convention

- **Lowercase with hyphens**: `action-item-tracking` (not `ActionItemTracking` or `action_item_tracking`)
- **Descriptive**: Name clearly describes what the skill does
- **Verb-based**: Start with action verb when possible (`generate-`, `capture-`, `analyze-`)

---

## YAML Frontmatter Schema

### Required Fields

```yaml
---
name: skill-name                # Unique identifier (matches directory name)
description: Brief one-sentence description of what this skill does
domain: change-agent            # Domain this skill belongs to
---
```

### Complete Schema

```yaml
---
name: skill-name
description: Brief description (max 150 chars, shown in skill browser)
domain: change-agent            # Domain: change-agent, credit-risk, market-risk, etc.
category: meeting-management    # Sub-category within domain
taxonomy: change-agent/meeting-management  # Full taxonomy path
parameters:                     # Input parameters
  - meeting_transcript          # Simple form (string assumed)
  - meeting_date
  - attendees
output_format: structured_markdown  # Output type: json, markdown, csv, etc.
estimated_duration: 2-3 minutes     # How long execution typically takes
tags:                           # Searchable tags
  - meetings
  - action-items
  - documentation
version: 1.0.0                  # Semantic versioning
author: Risk Agents Team        # Who created/maintains this
---
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ Yes | Unique skill identifier (kebab-case) |
| `description` | string | ✅ Yes | One-sentence description for skill browser |
| `domain` | string | ✅ Yes | Primary domain (change-agent, credit-risk, etc.) |
| `category` | string | ⚠️ Recommended | Sub-category for organization |
| `taxonomy` | string | ⚠️ Recommended | Full taxonomy path (domain/category) |
| `parameters` | array | ⚠️ Recommended | List of input parameters |
| `output_format` | string | ⚠️ Recommended | Output type (json, markdown, csv, table) |
| `estimated_duration` | string | ⚠️ Recommended | Typical execution time |
| `tags` | array | ⏸️ Optional | Searchable tags for discovery |
| `version` | string | ⏸️ Optional | Semantic version (default: 1.0.0) |
| `author` | string | ⏸️ Optional | Creator/maintainer |

---

## Parameter Definition

### Simple Parameters (String)

```yaml
parameters:
  - meeting_transcript
  - project_name
  - stakeholder_list
```

**Interpretation**: All parameters are strings, all are required

### Detailed Parameters (With Types)

```yaml
parameters:
  - name: meeting_transcript
    type: string
    required: true
    description: Full text of the meeting transcript or notes
    example: "Team discussed Q4 roadmap..."

  - name: meeting_type
    type: string
    required: false
    description: Type of meeting (decision-making, brainstorming, status-update)
    enum: [decision-making, brainstorming, status-update, retrospective]
    default: status-update

  - name: attendees
    type: array
    required: true
    description: List of meeting attendees
    items:
      type: string
    min_items: 1

  - name: project_context
    type: object
    required: false
    description: Additional project context
    properties:
      project_name: string
      project_phase: string
      key_stakeholders: array
```

### Parameter Types

| Type | Description | Example |
|------|-------------|---------|
| `string` | Text value | "Project Alpha" |
| `number` | Numeric value | 42, 3.14 |
| `boolean` | True/false | true |
| `array` | List of values | ["item1", "item2"] |
| `object` | Structured data | {"key": "value"} |
| `date` | ISO date string | "2025-10-26" |
| `enum` | Fixed set of values | ["low", "medium", "high"] |

### Validation Rules

```yaml
parameters:
  - name: email
    type: string
    format: email               # Validates email format

  - name: priority
    type: string
    enum: [low, medium, high, critical]  # Must be one of these

  - name: due_date
    type: date
    format: iso8601             # YYYY-MM-DD format

  - name: team_size
    type: number
    minimum: 1
    maximum: 100

  - name: description
    type: string
    min_length: 10
    max_length: 500
```

---

## Output Formatting Standards

### Structured JSON Output

```yaml
output_format: json
```

**Example Output**:
```json
{
  "status": "success",
  "result": {
    "action_items": [
      {
        "id": 1,
        "description": "Update project timeline",
        "owner": "John Smith",
        "due_date": "2025-11-01",
        "priority": "high",
        "status": "pending"
      }
    ]
  },
  "metadata": {
    "generated_at": "2025-10-26T14:30:00Z",
    "skill_name": "action-item-tracking",
    "version": "1.0.0"
  }
}
```

**When to Use**:
- Data needs to be processed by other systems
- Frontend needs structured data to display
- Multiple related entities need to be returned

### Structured Markdown Output

```yaml
output_format: structured_markdown
```

**Example Output**:
```markdown
# Project Charter: Website Redesign

**Project Manager**: Sarah Johnson
**Start Date**: 2025-11-01
**Target Completion**: 2026-02-28

## Executive Summary

[2-3 paragraphs describing project purpose, scope, and expected outcomes]

## Objectives

1. Improve user experience with modern design
2. Increase conversion rate by 25%
3. Reduce page load time to < 2 seconds

## Stakeholders

| Name | Role | Interest Level | Influence Level |
|------|------|----------------|-----------------|
| John Doe | Sponsor | High | High |
| Jane Smith | Marketing Lead | High | Medium |

## Success Criteria

- [ ] User satisfaction score > 4.5/5
- [ ] Conversion rate increase of 25%+
- [ ] Page load time < 2 seconds
```

**When to Use**:
- Human-readable documents needed
- Reports, charters, plans
- Documents that will be shared as-is

### Table/CSV Output

```yaml
output_format: csv
```

**Example Output**:
```csv
Activity,Responsible,Accountable,Consulted,Informed
Requirements Gathering,PM,Sponsor,Tech Lead|Designer,Team
Design Mockups,Designer,PM,Sponsor|Tech Lead,Team
Development,Dev Team,Tech Lead,PM|Designer,Sponsor
Testing,QA Team,Tech Lead,PM,Sponsor|Dev Team
Deployment,DevOps,Tech Lead,PM,Sponsor|Team
```

**When to Use**:
- Matrix outputs (RACI, risk matrix, etc.)
- Data meant for spreadsheet import
- Tabular data with many rows

### Mixed Format Output

```yaml
output_format: mixed
```

**Example**: JSON with embedded markdown
```json
{
  "summary": "**5 high-priority action items** identified from meeting",
  "action_items": [...],
  "detailed_report": "# Full Meeting Analysis\n\n## Key Decisions\n\n1. ..."
}
```

---

## Progressive Disclosure

### When to Use Progressive Disclosure

Use `instructions/` directory when a skill:
- Has multiple distinct steps (3+)
- Requires different processing approaches for different scenarios
- Benefits from breaking down complexity
- Needs intermediate validation or checkpoints

### Instructions Directory Structure

```
skill-name/
└── instructions/
    ├── 01-preparation.md       # Numbered for clear sequence
    ├── 02-analysis.md
    ├── 03-synthesis.md
    └── 04-validation.md
```

### Instruction File Format

```markdown
# Step 1: Preparation

## Purpose
Prepare the input data for analysis by cleaning and structuring it.

## Inputs Available
- Raw meeting transcript (from SKILL.md parameters)
- Attendee list
- Meeting context

## Processing Steps
1. Identify meeting type from content
2. Extract speaker attribution if present
3. Segment transcript into topics
4. Flag any unclear or incomplete sections

## Outputs to Next Step
- Cleaned transcript with speaker attribution
- Topic segments
- List of any ambiguities needing clarification

## Quality Checks
- ✅ All speakers identified
- ✅ Topics are logically separated
- ✅ Ambiguities are flagged (not assumed)
```

### Resources Directory

```
skill-name/
└── resources/
    ├── template.md             # Output template
    ├── examples.md             # Example transformations
    ├── validation-rules.md     # Validation criteria
    └── edge-cases.md           # Known edge cases and handling
```

**template.md** - Exact output format:
```markdown
# [Template Name]

Use this exact structure for output:

[Template structure with placeholders]
```

**examples.md** - Real-world examples:
```markdown
# Examples

## Example 1: Simple Use Case

**Input**:
```
[Example input]
```

**Output**:
```
[Example output]
```

**Why This Output**: [Explanation of decisions made]
```

---

## Knowledge Integration

### Referencing Knowledge Documents

Skills should reference relevant knowledge documents from the knowledge base:

```markdown
## Knowledge References

This skill utilizes knowledge from the Change Agent domain:
- **meeting-types.md** - Understanding different meeting types
- **action-items-standards.md** - Standards for actionable items (WHAT, WHO, WHEN, WHY)
- **decision-capture.md** - Standards for documenting decisions

These knowledge documents provide best practices and standards that enhance skill execution quality.
```

### How Skills Use Knowledge

1. **Skills Loader** discovers skills from `backend/.claude/skills/`
2. **Knowledge Manager** loads relevant knowledge docs
3. **Agent Context** combines skill instructions + knowledge docs
4. **Claude** receives complete context for skill execution

### Knowledge Document Structure

Knowledge docs live in: `backend/knowledge/{domain}/{category}/{document}.md`

Example: `backend/knowledge/change-agent/meeting-management/action-items-standards.md`

---

## Validation Patterns

### Input Validation

**Required Parameter Check**:
```python
def validate_parameters(params: dict) -> tuple[bool, str]:
    """Validate skill parameters before execution."""
    required = ['meeting_transcript', 'attendees']

    for param in required:
        if param not in params or not params[param]:
            return False, f"Missing required parameter: {param}"

    return True, ""
```

**Type Validation**:
```python
def validate_types(params: dict) -> tuple[bool, str]:
    """Validate parameter types."""
    if not isinstance(params.get('attendees'), list):
        return False, "attendees must be a list"

    if not isinstance(params.get('meeting_transcript'), str):
        return False, "meeting_transcript must be a string"

    return True, ""
```

**Format Validation**:
```python
import re
from datetime import datetime

def validate_formats(params: dict) -> tuple[bool, str]:
    """Validate parameter formats."""
    # Email validation
    if 'email' in params:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, params['email']):
            return False, "Invalid email format"

    # Date validation
    if 'due_date' in params:
        try:
            datetime.fromisoformat(params['due_date'])
        except ValueError:
            return False, "Invalid date format (use YYYY-MM-DD)"

    return True, ""
```

### Output Validation

**Schema Validation** (using Pydantic):
```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class ActionItem(BaseModel):
    """Action item schema."""
    id: int
    description: str = Field(min_length=10, max_length=500)
    owner: str
    due_date: date
    priority: str = Field(pattern='^(low|medium|high|critical)$')
    status: str = 'pending'

class ActionItemsOutput(BaseModel):
    """Skill output schema."""
    status: str
    action_items: List[ActionItem]
    total_count: int

    def validate_consistency(self):
        """Custom validation logic."""
        assert len(self.action_items) == self.total_count
        return True
```

**Markdown Structure Validation**:
```python
def validate_markdown_output(output: str) -> tuple[bool, str]:
    """Validate markdown output structure."""
    required_sections = [
        '# Meeting Minutes:',
        '## Decisions',
        '## Action Items',
        '## Next Steps'
    ]

    for section in required_sections:
        if section not in output:
            return False, f"Missing required section: {section}"

    return True, ""
```

---

## Testing Guidelines

### Test Data Creation

**Create Realistic Test Cases**:
```python
# tests/skills/test_meeting_minutes_capture.py

SAMPLE_INPUTS = {
    "simple_meeting": {
        "meeting_transcript": """
            Team standup - Oct 26, 2025
            Attendees: John, Sarah, Mike

            John: Finished user authentication feature
            Sarah: Working on dashboard, needs design review
            Mike: Blocked on API access, needs John's help

            Decision: Ship auth feature Friday
            Action: John to help Mike with API (today)
            Action: Sarah to schedule design review (this week)
        """,
        "attendees": ["John Smith", "Sarah Johnson", "Mike Chen"],
        "meeting_date": "2025-10-26"
    },

    "complex_meeting": {
        # More complex example with ambiguities
    },

    "edge_case_no_decisions": {
        # Meeting with no clear decisions
    }
}
```

### Expected Outputs

**Define Expected Output Structure**:
```python
EXPECTED_OUTPUTS = {
    "simple_meeting": {
        "decisions_count": 1,
        "action_items_count": 2,
        "has_all_attendees": True,
        "has_next_steps": True
    }
}

def validate_output(output: dict, expected: dict) -> bool:
    """Validate skill output matches expectations."""
    assert len(output['decisions']) == expected['decisions_count']
    assert len(output['action_items']) == expected['action_items_count']
    return True
```

### Unit Testing Pattern

```python
import pytest
from agent import SkillExecutor

class TestMeetingMinutesCapture:
    """Test suite for meeting-minutes-capture skill."""

    def setup_method(self):
        """Set up test fixtures."""
        self.skill = SkillExecutor("meeting-minutes-capture")

    def test_simple_meeting(self):
        """Test with straightforward meeting transcript."""
        input_data = SAMPLE_INPUTS["simple_meeting"]
        result = self.skill.execute(input_data)

        assert result['status'] == 'success'
        assert 'action_items' in result
        assert len(result['action_items']) >= 2

    def test_missing_required_parameter(self):
        """Test validation of required parameters."""
        with pytest.raises(ValueError, match="Missing required parameter"):
            self.skill.execute({"attendees": ["John"]})  # Missing transcript

    def test_output_format(self):
        """Test output matches expected structure."""
        input_data = SAMPLE_INPUTS["simple_meeting"]
        result = self.skill.execute(input_data)

        # Validate schema
        output = ActionItemsOutput(**result)
        assert output.validate_consistency()
```

---

## Best Practices

### DO ✅

1. **Clear, Specific Descriptions**
   ```yaml
   description: Extract action items from meeting transcripts with owners and due dates
   ```
   Not: ~~`description: Process meetings`~~

2. **Well-Structured Parameters**
   ```yaml
   parameters:
     - name: transcript
       type: string
       required: true
       description: Full meeting transcript or notes
       min_length: 50
   ```

3. **Comprehensive Examples**
   - Show realistic, complete examples
   - Include edge cases in examples
   - Explain why certain decisions were made

4. **Link to Knowledge**
   - Reference relevant knowledge documents
   - Explain how knowledge enhances the skill
   - Keep skill definitions focused, put details in knowledge

5. **Validate Everything**
   - Validate inputs before execution
   - Validate outputs before returning
   - Provide clear error messages

### DON'T ❌

1. **Vague Descriptions**
   - ~~`description: Helps with projects`~~
   - ✅ `description: Generate comprehensive project charters with objectives, stakeholders, and success criteria`

2. **Unclear Parameters**
   - ~~`parameters: [data, info, stuff]`~~
   - ✅ Clear parameter names with types and descriptions

3. **Missing Output Specification**
   - Always specify `output_format`
   - Always provide example output
   - Always document output schema

4. **Kitchen Sink Skills**
   - Don't create one skill that does everything
   - Keep skills focused on single responsibility
   - Create multiple skills for different use cases

5. **Hardcoded Values**
   - Don't hardcode dates, names, etc.
   - Use parameters for all variable data
   - Make skills reusable across contexts

---

## Checklist for New Skills

Use this checklist when creating a new skill:

### Planning ✅
- [ ] Clear problem statement defined
- [ ] Input requirements identified
- [ ] Output format designed
- [ ] Edge cases considered
- [ ] Knowledge documents identified

### Implementation ✅
- [ ] Create skill directory with proper naming
- [ ] Write SKILL.md with complete YAML frontmatter
- [ ] Define all parameters with types and validation
- [ ] Specify output format with examples
- [ ] Add progressive disclosure if needed (instructions/)
- [ ] Add templates and examples (resources/)
- [ ] Link to relevant knowledge documents

### Validation ✅
- [ ] Test with realistic inputs
- [ ] Verify output format matches specification
- [ ] Test edge cases and error scenarios
- [ ] Validate parameter validation works
- [ ] Check knowledge document references are valid

### Documentation ✅
- [ ] Usage examples included
- [ ] Success criteria defined
- [ ] Tips for best results provided
- [ ] Common issues documented

### Integration ✅
- [ ] Skill loads correctly via SkillsLoader
- [ ] Appears in GET /api/skills endpoint
- [ ] Executes via POST /api/skills/{skill_id}/execute
- [ ] Frontend Skills Browser displays correctly
- [ ] Execution results render properly

---

## Skill Development Workflow

1. **Plan** (15 minutes)
   - Define problem and use cases
   - Sketch parameter structure
   - Design output format

2. **Create Structure** (5 minutes)
   - Create skill directory
   - Create SKILL.md with frontmatter
   - Create instructions/ and resources/ if needed

3. **Write Skill Definition** (20-30 minutes)
   - Complete YAML frontmatter
   - Write skill description and purpose
   - Document parameters and output
   - Add examples and templates

4. **Test** (10-15 minutes)
   - Create test inputs
   - Execute skill via API
   - Verify output format
   - Test edge cases

5. **Document** (5-10 minutes)
   - Add to skills catalog
   - Update progress tracking
   - Note any issues or limitations

**Total Time Per Skill**: 55-75 minutes (average 60 minutes)

---

## Resources

- [SKILL_TEMPLATE.md](./SKILL_TEMPLATE.md) - Copy-paste template for new skills
- [skill-testing-guide.md](./skill-testing-guide.md) - Comprehensive testing guide
- [Module 6 Overview](./module-6-overview.md) - Module 6 implementation plan
- [Claude Skills Framework Docs](https://docs.claude.com/en/docs/claude-code/skills) - Official documentation

---

**Last Updated**: October 26, 2025
**Version**: 1.0.0
**Maintainer**: Risk Agents Team
