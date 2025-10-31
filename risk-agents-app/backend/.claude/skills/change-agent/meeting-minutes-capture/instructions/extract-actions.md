# How to Extract Action Items

## What is an Action Item?

An action item is a specific task that someone commits to completing, typically with:
- **Clear task description**: What needs to be done
- **Owner**: Who is responsible
- **Due date**: When it should be completed
- **Status**: Current state (Pending, In Progress, Complete)

## Identifying Action Items

### Explicit Action Items
Look for phrases like:
- "[Name] will [action]"
- "[Name] to [action] by [date]"
- "We need to [action]"
- "[Name] agreed to [action]"
- "Action: [description]"

**Examples**:
- "Sarah will create the project plan by Friday"
- "John to follow up with the client by EOD"
- "We need to schedule a follow-up meeting"

### Implicit Action Items
Sometimes actions are implied:
- Decisions that require implementation
- Questions that need answers
- Problems that need solutions
- Approvals that need to be obtained

**Example**:
Statement: "We decided to use AWS for hosting"
Implied Action: "Set up AWS infrastructure"

## Extraction Process

### Step 1: Scan for Commitments
Read through the meeting content and identify:
- Explicit commitments
- Implied tasks from decisions
- Questions requiring follow-up
- Approvals needed

### Step 2: Identify Owners
For each action:
- Who volunteered or was assigned?
- If no owner specified, mark as "TBD" or assign to meeting organizer
- For team actions, specify the team name

### Step 3: Determine Due Dates
Look for:
- Explicit dates mentioned ("by Friday", "next week")
- Meeting follow-up dates
- Project milestones
- If no date specified, use reasonable defaults based on urgency

### Step 4: Assess Priority
Mark actions as:
- **Critical**: Blocking other work
- **High**: Important for project progress
- **Medium**: Standard priority
- **Low**: Nice to have

### Step 5: Add Context
For each action item, include:
- Why it's needed (context from meeting)
- Dependencies (what must happen first)
- Success criteria (how to know it's done)

## Action Item Template

```markdown
| Item | Owner | Due Date | Priority | Status | Notes |
|------|-------|----------|----------|--------|-------|
| [Task description] | [Name] | [YYYY-MM-DD] | [H/M/L] | Pending | [Context] |
```

## Examples

### Example 1: Explicit Action
**From meeting**: "John will send the draft proposal to the client by Thursday."

**Extracted**:
| Item | Owner | Due Date | Priority | Status |
|------|-------|----------|----------|--------|
| Send draft proposal to client | John | 2025-01-18 | High | Pending |

### Example 2: Implied Action
**From meeting**: "We decided to migrate to the new platform, but we need IT approval first."

**Extracted**:
| Item | Owner | Due Date | Priority | Status |
|------|-------|----------|----------|--------|
| Get IT approval for platform migration | TBD | 2025-01-25 | Critical | Pending |
| Plan platform migration | TBD | TBD | High | Blocked |

### Example 3: Team Action
**From meeting**: "The dev team needs to review the architecture document."

**Extracted**:
| Item | Owner | Due Date | Priority | Status |
|------|-------|----------|----------|--------|
| Review architecture document | Dev Team | 2025-01-20 | Medium | Pending |

## Quality Checks

Before finalizing action items:
- [ ] Every action has a clear description
- [ ] Every action has an owner (or TBD)
- [ ] Dates are specific (not "soon" or "later")
- [ ] Priority is assigned based on meeting discussion
- [ ] Dependencies are noted
- [ ] No duplicate actions
- [ ] Actions are actionable (verbs used)

## Common Pitfalls

❌ **Too vague**: "Follow up on project"
✅ **Specific**: "Schedule 30-min call with PM to discuss Q1 timeline"

❌ **No owner**: "Someone needs to update the documentation"
✅ **Clear owner**: "Sarah to update user documentation | Due: 2025-01-22"

❌ **No deadline**: "Eventually we should review the contract"
✅ **Deadline**: "Review vendor contract | John | Due: 2025-02-01"
