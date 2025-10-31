# SKILL TEMPLATE

**Purpose**: Copy-paste template for creating new Claude Skills Framework skills
**Usage**: Copy this entire file structure to create a new skill
**Last Updated**: October 26, 2025

---

## Instructions

1. **Copy this file** to `backend/.claude/skills/{domain}/{skill-name}/SKILL.md`
2. **Replace all [PLACEHOLDERS]** with actual values
3. **Delete unused sections** (e.g., progressive disclosure if not needed)
4. **Create supporting files** (instructions/, resources/) if needed
5. **Test the skill** with realistic inputs
6. **Update progress tracking** when complete

---

## SKILL.md Template

```markdown
---
name: [skill-name]
description: [Brief one-sentence description - max 150 chars - shown in Skills Browser]
domain: [change-agent|credit-risk|market-risk|operational-risk]
category: [sub-category-within-domain]
taxonomy: [domain]/[category]
parameters:
  - [parameter_1]
  - [parameter_2]
  - [parameter_3]
output_format: [json|structured_markdown|csv|table|mixed]
estimated_duration: [X-Y minutes]
tags:
  - [tag1]
  - [tag2]
  - [tag3]
version: 1.0.0
author: Risk Agents Team
---

# [Skill Name] Skill

## Purpose
[What problem does this skill solve? 2-3 sentences explaining the core value proposition]

## When to Use This Skill
- [Use case 1 - specific scenario]
- [Use case 2 - specific scenario]
- [Use case 3 - specific scenario]
- [Use case 4 - specific scenario]

## How It Works
[Explain the skill's approach in 3-5 bullet points or short paragraphs]

1. **[Step 1]**: [What happens in this step]
2. **[Step 2]**: [What happens in this step]
3. **[Step 3]**: [What happens in this step]
4. **[Step 4]**: [What happens in this step]

## Parameters

### Required Parameters
- **`[parameter_1]`** (string): [Description of what this parameter is and how to provide it]
- **`[parameter_2]`** (array): [Description of what this parameter is and how to provide it]

### Optional Parameters
- **`[parameter_3]`** (string): [Description - include default value if applicable]
  - Default: [default_value]
  - Allowed values: [value1, value2, value3] (if enum)

## Instructions
[OPTIONAL - Delete this section if skill doesn't use progressive disclosure]

For detailed instructions on using this skill:
- See `instructions/01-[step-name].md` - [Brief description]
- See `instructions/02-[step-name].md` - [Brief description]
- See `instructions/03-[step-name].md` - [Brief description]

## Resources
[OPTIONAL - Delete this section if no supporting resources needed]

- `resources/template.md` - [Description of template]
- `resources/examples.md` - [Description of examples]
- `resources/validation.md` - [Description of validation rules]

## Knowledge References
[OPTIONAL - Delete this section if skill doesn't reference knowledge documents]

This skill utilizes knowledge from the [Domain Name] domain:
- **[knowledge-doc-1].md** - [What this document provides]
- **[knowledge-doc-2].md** - [What this document provides]
- **[knowledge-doc-3].md** - [What this document provides]

These knowledge documents provide best practices and standards that enhance the quality of the skill execution.

## Expected Output

[Describe the output format and structure. Provide a concrete example.]

### JSON Output Example
[If output_format is json, show example structure]

```json
{
  "status": "success",
  "result": {
    "[key]": "[value]",
    "[array_key]": [
      {
        "id": 1,
        "field1": "value1",
        "field2": "value2"
      }
    ]
  },
  "metadata": {
    "generated_at": "2025-10-26T14:30:00Z",
    "skill_name": "[skill-name]",
    "version": "1.0.0"
  }
}
```

### Markdown Output Example
[If output_format is structured_markdown, show example document]

```markdown
# [Document Title]

**[Metadata Field 1]**: [Value]
**[Metadata Field 2]**: [Value]
**[Metadata Field 3]**: [Value]

## [Section 1 Heading]

[Section 1 content description]

### [Subsection 1.1]
- [Bullet point 1]
- [Bullet point 2]

## [Section 2 Heading]

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |

## [Section 3 Heading]

- [ ] [Checklist item 1]
- [ ] [Checklist item 2]
- [ ] [Checklist item 3]
```

### CSV/Table Output Example
[If output_format is csv or table, show example]

```csv
[Column1],[Column2],[Column3],[Column4]
[Value1],[Value2],[Value3],[Value4]
[Value1],[Value2],[Value3],[Value4]
```

## Success Criteria
- [Criterion 1 - what makes a successful execution]
- [Criterion 2 - quality check]
- [Criterion 3 - completeness check]
- [Criterion 4 - validation requirement]

## Tips for Best Results
- [Tip 1 - how to get better outputs]
- [Tip 2 - common mistake to avoid]
- [Tip 3 - how to provide better inputs]
- [Tip 4 - edge case to be aware of]

## Known Limitations
[OPTIONAL - Delete if no notable limitations]

- [Limitation 1 - what the skill cannot do]
- [Limitation 2 - edge case that may not work well]

## Version History
[OPTIONAL - Track significant changes]

- **1.0.0** (2025-10-26): Initial release
```

---

## Detailed Parameters Template (Alternative)

If you need more detailed parameter definitions, use this YAML structure in the frontmatter:

```yaml
---
name: [skill-name]
description: [Brief description]
domain: [domain]
parameters:
  - name: [parameter_1]
    type: string
    required: true
    description: [Full description of this parameter]
    example: "[Example value]"
    min_length: 10
    max_length: 5000

  - name: [parameter_2]
    type: array
    required: true
    description: [Full description of this array parameter]
    items:
      type: string
    min_items: 1
    max_items: 50

  - name: [parameter_3]
    type: string
    required: false
    description: [Full description of this optional parameter]
    enum: [option1, option2, option3]
    default: option1

  - name: [parameter_4]
    type: object
    required: false
    description: [Full description of this object parameter]
    properties:
      sub_field1:
        type: string
        required: true
      sub_field2:
        type: number
        required: false
---
```

---

## Progressive Disclosure Template

### instructions/01-[step-name].md

```markdown
# Step 1: [Step Name]

## Purpose
[What is accomplished in this step - 1-2 sentences]

## Inputs Available
- [Input 1 from parameters]
- [Input 2 from parameters]
- [Input 3 derived or computed]

## Processing Steps
1. [First action to take]
2. [Second action to take]
3. [Third action to take]
4. [Quality check or validation]

## Outputs to Next Step
- [Output 1 that next step needs]
- [Output 2 that next step needs]
- [Interim result or state]

## Quality Checks
- ✅ [Check 1 - what must be true]
- ✅ [Check 2 - what must be verified]
- ✅ [Check 3 - validation requirement]

## Common Issues
- **Issue**: [Description of common problem]
  **Solution**: [How to handle it]

- **Issue**: [Description of another problem]
  **Solution**: [How to handle it]
```

### instructions/02-[step-name].md

[Copy structure from 01- template above]

### instructions/03-[step-name].md

[Copy structure from 01- template above]

---

## Resources Template

### resources/template.md

```markdown
# [Skill Name] Output Template

Use this exact structure for [skill-name] skill outputs:

---

# [Main Document Title]

**[Metadata Field 1]**: [Placeholder or instruction]
**[Metadata Field 2]**: [Placeholder or instruction]

## [Section 1]

[Instructions for what goes here - be specific about format, structure, required content]

### [Subsection 1.1]

[Template content with placeholders in [square brackets]]

## [Section 2]

| [Column Header 1] | [Column Header 2] | [Column Header 3] |
|-------------------|-------------------|-------------------|
| [Value guidance]  | [Value guidance]  | [Value guidance]  |

## [Section 3]

- [ ] [Checklist item template]
- [ ] [Checklist item template]

---

**Template Version**: 1.0.0
**Last Updated**: 2025-10-26
```

### resources/examples.md

```markdown
# [Skill Name] Examples

## Example 1: [Simple/Common Use Case]

### Input

**Parameter 1**: [Example value]
**Parameter 2**: [Example value]
**Parameter 3**: [Example value]

### Output

```[json|markdown|csv]
[Complete example output showing exact format]
```

### Why This Output

[Explanation of key decisions made in this output, what to notice, what's important]

---

## Example 2: [Complex Use Case]

### Input

**Parameter 1**: [More complex example value]
**Parameter 2**: [More complex example value]

### Output

```[json|markdown|csv]
[Complete example output for complex case]
```

### Why This Output

[Explanation highlighting how complexity is handled]

---

## Example 3: [Edge Case]

### Input

**Parameter 1**: [Edge case example - minimal data, ambiguous data, etc.]

### Output

```[json|markdown|csv]
[Example showing how edge case is handled]
```

### Why This Output

[Explanation of edge case handling approach]
```

### resources/validation.md

```markdown
# [Skill Name] Validation Rules

## Input Validation

### Required Parameters

- **`[parameter_1]`**:
  - Must be present
  - Must be non-empty string
  - Minimum length: [X] characters
  - Maximum length: [Y] characters

- **`[parameter_2]`**:
  - Must be present
  - Must be array
  - Minimum items: [X]
  - Maximum items: [Y]

### Optional Parameters

- **`[parameter_3]`**:
  - If present, must be one of: [value1, value2, value3]
  - Default: [value1] if not provided

## Output Validation

### Structural Requirements

- Output must include all required sections:
  - [Section 1]
  - [Section 2]
  - [Section 3]

### Content Requirements

- [Requirement 1 - e.g., all items must have owners and dates]
- [Requirement 2 - e.g., decisions must include rationale]
- [Requirement 3 - e.g., tables must have headers]

## Edge Cases

### Case 1: [Minimal Data]

**Scenario**: [Description of minimal data situation]
**Expected Behavior**: [How skill should handle it]
**Validation**: [What to check in output]

### Case 2: [Ambiguous Data]

**Scenario**: [Description of ambiguity]
**Expected Behavior**: [How skill should handle it - clarify, flag, assume?]
**Validation**: [What to check in output]

### Case 3: [Conflicting Data]

**Scenario**: [Description of conflict]
**Expected Behavior**: [How skill should resolve it]
**Validation**: [What to check in output]
```

---

## Directory Structure Checklist

When creating a new skill, create this structure:

```
✅ backend/.claude/skills/[domain]/[skill-name]/
   ✅ SKILL.md                                  # Main skill definition (REQUIRED)
   ⏸️ instructions/                            # Progressive disclosure (optional)
      ⏸️ 01-[step-name].md                     # First step
      ⏸️ 02-[step-name].md                     # Second step
      ⏸️ 03-[step-name].md                     # Third step
   ⏸️ resources/                               # Supporting materials (optional)
      ⏸️ template.md                           # Output template
      ⏸️ examples.md                           # Example inputs/outputs
      ⏸️ validation.md                         # Validation rules
```

---

## Quick Start Checklist

Use this checklist when creating a new skill from this template:

### Planning Phase
- [ ] Define problem statement clearly
- [ ] Identify all required input parameters
- [ ] Design output format and structure
- [ ] Consider edge cases and limitations
- [ ] Identify relevant knowledge documents

### Creation Phase
- [ ] Create skill directory: `backend/.claude/skills/[domain]/[skill-name]/`
- [ ] Copy SKILL_TEMPLATE.md to `SKILL.md` in skill directory
- [ ] Replace all [PLACEHOLDERS] with actual values
- [ ] Remove optional sections if not needed
- [ ] Add progressive disclosure (instructions/) if needed
- [ ] Add supporting resources if helpful

### Validation Phase
- [ ] Create test inputs (simple, complex, edge cases)
- [ ] Test skill via API: `POST /api/skills/[skill-id]/execute`
- [ ] Verify output format matches specification
- [ ] Check all success criteria are met
- [ ] Validate error handling for invalid inputs

### Documentation Phase
- [ ] Update module-6-progress.md
- [ ] Add skill to skills catalog
- [ ] Document any known issues or limitations
- [ ] Note completion time for future reference

---

## Related Documentation

- [Skill Development Guide](./skill-development-guide.md) - Complete skill development standards
- [Skill Testing Guide](./skill-testing-guide.md) - Testing methodology and examples
- [Module 6 Overview](./module-6-overview.md) - Module 6 implementation plan

---

**Template Version**: 1.0.0
**Last Updated**: October 26, 2025
**Maintainer**: Risk Agents Team
