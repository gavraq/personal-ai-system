# Action Items Standards

## Purpose
Defines the standard structure and quality criteria for action items captured from meetings.

## What is an Action Item?

An action item is a specific task that someone has committed to complete by a certain date as a result of a meeting discussion.

**Action items are NOT**:
- General discussions or ideas
- Background information
- Context or rationale
- Decisions made (these are captured separately)
- Risks or issues (unless there's a specific action to address them)

---

## Complete Action Item Structure

Every action item MUST contain these 5 elements:

### 1. Task Description (WHAT)
**Requirement**: Clear, specific, verb-led description

**Good Examples**:
- ✅ "Prepare project charter with budget, timeline, and resource requirements"
- ✅ "Update stakeholder distribution list with new team members"
- ✅ "Review and provide feedback on draft requirements document"

**Bad Examples**:
- ❌ "Project charter" (not verb-led, unclear what action is needed)
- ❌ "Think about the budget" (not specific enough)
- ❌ "Handle the stakeholders" (vague, no clear outcome)

**Standards**:
- Start with action verb (Prepare, Update, Review, Send, Schedule, etc.)
- Include specific deliverable or outcome
- Include scope or constraints if relevant
- Maximum 1-2 sentences

---

### 2. Owner (WHO)
**Requirement**: Named individual responsible for completion

**Good Examples**:
- ✅ "Alice Johnson"
- ✅ "Bob (with support from Charlie)"
- ✅ "Sarah (delegating to team but accountable)"

**Bad Examples**:
- ❌ "The team" (not specific enough)
- ❌ "Someone" (no accountability)
- ❌ "TBD" (must be assigned before meeting ends)

**Standards**:
- Single named individual (even if delegating)
- Use full name or unambiguous identifier
- If support needed, note it but keep single owner
- Owner must be present in meeting or agreed to accept

---

### 3. Due Date (WHEN)
**Requirement**: Specific date or event-based deadline

**Good Examples**:
- ✅ "2025-10-30"
- ✅ "Friday, October 30"
- ✅ "Before next meeting (Nov 6)"
- ✅ "Within 3 business days"

**Bad Examples**:
- ❌ "Soon"
- ❌ "When possible"
- ❌ "End of month" (which month?)
- ❌ "ASAP" (not specific)

**Standards**:
- Use ISO date format (YYYY-MM-DD) or explicit date
- If event-based, specify the event date
- If relative, specify relative to what (meeting date, another milestone)
- Consider weekends and holidays

---

### 4. Context (WHY)
**Requirement**: Brief explanation of why this action is needed

**Good Examples**:
- ✅ "Needed for budget approval next week"
- ✅ "Addresses the data quality issue raised in the audit"
- ✅ "Prerequisite for project kickoff"

**Bad Examples**:
- ❌ "Because we need it" (not helpful)
- ❌ [no context provided]

**Standards**:
- 1 sentence explaining purpose
- Links to decision, issue, or discussion that triggered it
- Helps owner prioritize if they have competing deadlines

---

### 5. Dependencies (OPTIONAL)
**Requirement**: Any prerequisites or blocking factors

**Examples**:
- "Depends on: Charlie completing data analysis by Oct 25"
- "Blocked by: Waiting for vendor response"
- "Requires: Budget approval from finance"

**Standards**:
- Only include if genuinely blocking
- Name the dependency clearly
- Include expected resolution date if known

---

## Quality Checklist

Before finalizing action items, verify:

- [ ] Each action has WHAT, WHO, WHEN, WHY
- [ ] Task descriptions start with action verbs
- [ ] Each task is assigned to a single named individual
- [ ] Due dates are specific (not "soon" or "ASAP")
- [ ] Context explains why the action is needed
- [ ] Dependencies are noted (if any)
- [ ] No duplicate or overlapping actions
- [ ] Actions are achievable in the timeframe given
- [ ] Owner has accepted the action (or will be notified)

---

## Action Item Priority Levels

If prioritizing actions, use this standard classification:

### P0 - Critical
- Blocking other work
- Regulatory or compliance deadline
- System outage or critical issue
- Due within 24-48 hours

### P1 - High
- Impacts project timeline
- Customer-facing deliverable
- Committed external deadline
- Due within 1 week

### P2 - Medium
- Important but not blocking
- Internal deadline
- Can be rescheduled if needed
- Due within 2-4 weeks

### P3 - Low
- Nice to have
- Background work
- No immediate deadline
- Due date flexible

---

## Common Action Item Patterns

### Follow-up Meeting
- **Task**: "Schedule follow-up meeting with [attendees]"
- **Owner**: Meeting organizer or designated coordinator
- **Due Date**: Within 2 business days
- **Context**: "To review progress on action items"

### Document Review
- **Task**: "Review [document] and provide feedback via [method]"
- **Owner**: Named reviewer(s)
- **Due Date**: Specific date allowing time for revisions
- **Context**: "Feedback needed before [milestone]"

### Information Request
- **Task**: "Provide [specific information] to [recipient]"
- **Owner**: Person with access to information
- **Due Date**: When information is needed
- **Context**: "Required for [decision/meeting/milestone]"

### Approval Request
- **Task**: "Approve/reject [item] and notify [person]"
- **Owner**: Person with authority to approve
- **Due Date**: When decision is needed
- **Context**: "Approval needed to proceed with [next step]"

---

---

## Cross-Domain Action Items

Many action items captured in Change Agent meetings involve updating other domain knowledge. This reflects Change Agent's **dual context** role.

### Cross-Domain Action Item Examples

#### Example 1: Product Onboarding Action
**Action Item**:
- **Task**: "Update Market Risk approved products list to include FX Options with risk characteristics"
- **Owner**: Sarah (Market Risk Lead)
- **Due Date**: 2025-11-01
- **Context**: Decision made in Product Approval Committee to onboard FX Options
- **Dependencies**: Product specification document from Product team

**Cross-Domain Impact**:
- Updates: `[[market-risk/products/approved-products-list.md]]`
- Triggers check-out/check-in workflow (see [[../meta/knowledge-evolution.md]])
- Requires Market Risk domain expertise for completion
- Change Agent tracks completion but doesn't own the artefact

#### Example 2: Policy Update Action
**Action Item**:
- **Task**: "Update Change Agent documentation retention policy from 5 to 7 years across all policy documents"
- **Owner**: Mike (Change Agent Team)
- **Due Date**: 2025-10-30
- **Context**: Regulatory compliance requirement identified
- **Dependencies**: Legal approval of new retention period

**Cross-Domain Impact**:
- Updates: `[[change-agent/policies/documentation-standards.md]]`
- May also affect: `[[it-systems/storage/retention-policies.md]]`
- Change Agent owns this artefact directly
- Federated ownership means IT must align their systems

#### Example 3: Multi-Domain Implementation Action
**Action Item**:
- **Task**: "Configure trading systems to support FX Options, including risk limits and reporting"
- **Owner**: John (IT Systems Lead)
- **Due Date**: 2025-11-15
- **Context**: Part of FX Options product onboarding project
- **Dependencies**:
  - Market Risk must define limits first
  - Product team must provide specifications

**Cross-Domain Impact**:
- Updates: `[[operations/systems/trading-platform-config.md]]`
- References: `[[market-risk/methodologies/risk-calculations.md]]` for limit logic
- References: `[[product-management/products/fx-options-spec.md]]` for specifications
- Requires coordination across 3 domains (Change Agent, Market Risk, Operations)

### Tracking Cross-Domain Actions

When an action item affects other domains:

1. **Identify Affected Artefacts**: List which domain knowledge documents will be updated
2. **Assign Domain Owners**: Owner must have expertise in target domain
3. **Link to Change Context**: Reference change project managing the cross-domain update
4. **Track Dependencies**: Note which artefacts must be updated in sequence
5. **Verify Completion**: Check that domain artefacts were actually updated

**Action Item with Cross-Domain Tracking**:
```markdown
## Action Item: Update Risk Calculation Methodology

**Task**: Update Market Risk calculation methodology document to include FX Options delta and gamma calculations

**Owner**: Alice (Market Risk Quant)
**Due Date**: 2025-11-08
**Context**: FX Options product onboarding requires new risk calculations

**Cross-Domain Details**:
- **Target Artefact**: `[[market-risk/methodologies/risk-calculations.md]]`
- **Change Project**: PROJ-FX-OPTIONS-2025
- **Check-Out Required**: Yes (artefact currently in production)
- **Domain Approval**: Market Risk Director (Sarah)
- **Dependencies**:
  - Product specification must be finalized first (owner: Bob, due: 2025-11-01)
  - Data feeds must be configured first (owner: Charlie, due: 2025-11-05)

**Verification Checklist**:
- [ ] Methodology document updated with delta calculation
- [ ] Methodology document updated with gamma calculation
- [ ] Cross-references to data dictionary are correct
- [ ] Domain expert (Sarah) has reviewed and approved
- [ ] Version number incremented (v1.8 → v1.9)
- [ ] Change project records updated
- [ ] Artefact checked in to production
```

---

## Links to Other Knowledge

### Within Change Agent Domain
- [[meeting-types.md]] - Different meeting types and their requirements
- [[decision-capture.md]] - How to capture decisions separately from actions
- [[../meta/knowledge-evolution.md]] - How action items trigger cross-domain knowledge updates

### Cross-Domain Dependencies
When creating action items that affect other domains, consider:
- **Ownership**: Does the owner have expertise in the target domain?
- **Authority**: Does the owner have authority to update that domain's artefacts?
- **Dependencies**: What must happen before this artefact can be updated?
- **Validation**: Who in the target domain must approve the changes?

**Note**: Cross-domain references shown in monospace (e.g., `[[domain/category/doc.md]]`) represent future knowledge documents in other domains. For MVP, these serve as architectural placeholders demonstrating the dual context pattern.
