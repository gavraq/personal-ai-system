# Decision Capture Standards

## Purpose
Defines how to properly capture and document decisions made during meetings to ensure clarity, accountability, and traceability.

## What is a Decision?

A decision is a conscious choice between two or more alternatives where the group or authority commits to a specific course of action.

**Decisions are NOT**:
- Discussions or debates
- Options being considered
- Recommendations (unless formally accepted)
- Action items (though decisions often generate actions)
- Information shared

---

## Complete Decision Structure

Every decision MUST contain these elements:

### 1. Decision Statement (WHAT)
**Requirement**: Clear, unambiguous statement of what was decided

**Good Examples**:
- ✅ "Approved budget increase from $80k to $100k for Q4 project"
- ✅ "Selected Vendor A for cloud infrastructure implementation"
- ✅ "Decided to postpone feature release from November to December"
- ✅ "Rejected proposal to restructure team, will keep current structure"

**Bad Examples**:
- ❌ "Discussed the budget" (no decision made)
- ❌ "We should probably increase the budget" (not committed)
- ❌ "Maybe postpone the release" (ambiguous)
- ❌ "Team structure" (not a complete statement)

**Standards**:
- Use definitive language: "Approved", "Decided", "Selected", "Rejected"
- Include specific details (amounts, dates, names)
- State the outcome, not the process
- One clear sentence

---

### 2. Rationale (WHY)
**Requirement**: Brief explanation of why this decision was made

**Good Examples**:
- ✅ "Budget increase needed to accommodate 2 additional developers identified as critical for timeline"
- ✅ "Vendor A selected based on superior technical capabilities and 24/7 support, despite higher cost"
- ✅ "Release postponed due to unresolved security vulnerabilities in authentication module"

**Bad Examples**:
- ❌ "Because it's better"
- ❌ "Everyone agreed"
- ❌ [no rationale provided]

**Standards**:
- 1-3 sentences explaining reasoning
- Reference key factors considered
- Include trade-offs if relevant
- Link to supporting data or analysis if available

---

### 3. Decision Maker (WHO)
**Requirement**: Person or body with authority to make this decision

**Good Examples**:
- ✅ "Project Steering Committee"
- ✅ "Sarah Johnson (VP Engineering)"
- ✅ "Team consensus with final approval by Tech Lead"
- ✅ "Board of Directors"

**Bad Examples**:
- ❌ "Everyone" (unclear authority)
- ❌ "The team" (too vague)
- ❌ [no decision maker identified]

**Standards**:
- Named individual or formal body
- Must have authority to make this decision
- If consensus, note who had final authority
- If escalated, note escalation path

---

### 4. Alternatives Considered (OPTIONAL BUT RECOMMENDED)
**Requirement**: Other options that were evaluated

**Good Examples**:
- ✅ "Alternatives considered: (1) Keep $80k budget with reduced scope, (2) Delay project to Q1, (3) Increase to $100k (selected)"
- ✅ "Other vendors evaluated: Vendor B (lower cost but limited support) and Vendor C (declined to bid)"

**Standards**:
- List 2-5 main alternatives
- Brief note on why not selected
- Helps explain decision rationale
- Useful for future reference if decision needs review

---

### 5. Implementation (WHO DOES WHAT)
**Requirement**: How this decision will be implemented

**Good Examples**:
- ✅ "Finance to update project budget in system by Oct 25. Project Manager to hire 2 developers by Nov 1."
- ✅ "Procurement to issue PO to Vendor A by Oct 30. Technical team to begin onboarding Nov 1."

**Standards**:
- Specific implementation steps
- Owners for each step
- Timeline for implementation
- Often generates action items

---

### 6. Decision Date (WHEN)
**Requirement**: When the decision was made

**Good Examples**:
- ✅ "October 23, 2025"
- ✅ "Meeting held on 2025-10-23"

**Standards**:
- ISO date format (YYYY-MM-DD)
- Include meeting name/context if helpful

---

### 7. Review Criteria (OPTIONAL)
**Requirement**: When/how to review if decision should be revisited

**Good Examples**:
- ✅ "Review decision at Dec 1 checkpoint if budget overruns continue"
- ✅ "Revisit vendor selection in 6 months based on actual support performance"
- ✅ "Decision final unless security issue is resolved before Nov 15"

**Standards**:
- Specify review trigger (date, event, metric)
- Note what would cause reconsideration
- Helpful for reversible decisions

---

## Decision Types

### Strategic Decision
**Characteristics**: High impact, long-term, affects direction
**Authority Required**: Senior leadership, Board
**Documentation**: Most comprehensive, including analysis
**Examples**: Market entry, major partnership, reorganization

### Tactical Decision
**Characteristics**: Medium impact, implements strategy
**Authority Required**: Management, Project leads
**Documentation**: Standard decision capture
**Examples**: Vendor selection, resource allocation, timeline changes

### Operational Decision
**Characteristics**: Day-to-day, low impact, short-term
**Authority Required**: Team leads, Individual contributors
**Documentation**: Brief decision note
**Examples**: Meeting rescheduling, task assignment, minor process changes

---

## Decision Quality Checklist

Before finalizing decision capture, verify:

- [ ] Decision statement is clear and unambiguous
- [ ] Rationale explains why this decision was made
- [ ] Decision maker identified with appropriate authority
- [ ] Alternatives considered (if applicable)
- [ ] Implementation steps and owners identified
- [ ] Decision date recorded
- [ ] Review criteria noted (if decision should be revisited)
- [ ] Related action items created (if needed)
- [ ] Stakeholders who need to be informed are identified

---

## Common Decision Patterns

### Go/No-Go Decision
```
Decision: Approved to proceed with Project X
Rationale: All readiness criteria met, risks acceptable
Decision Maker: Project Steering Committee
Alternatives: Delay until Q1 (rejected - business case time-sensitive)
Implementation: Project Manager to initiate project by Nov 1
Date: 2025-10-23
```

### Vendor Selection
```
Decision: Selected Vendor A for cloud infrastructure
Rationale: Superior technical capabilities, 24/7 support, meets compliance requirements
Decision Maker: CTO with input from Architecture Board
Alternatives: Vendor B (lower cost, limited support), Vendor C (declined)
Implementation: Procurement to issue PO by Oct 30, implementation begins Nov 1
Date: 2025-10-23
Review: Assess vendor performance at 6-month mark
```

### Scope Change
```
Decision: Remove Feature Y from current sprint, move to next sprint
Rationale: Feature X taking longer than estimated, risking sprint commitment
Decision Maker: Scrum Master with team consensus
Alternatives: Extend sprint (rejected - disrupts cadence), reduce Feature X scope (rejected - impacts quality)
Implementation: Product Owner to update backlog, communicate to stakeholders
Date: 2025-10-23
```

### Budget Approval
```
Decision: Approved budget increase from $80k to $100k
Rationale: Additional developers needed to meet committed timeline
Decision Maker: Finance Director and VP Engineering
Alternatives: Maintain budget with extended timeline (rejected - contract penalty), maintain budget with reduced scope (rejected - minimum viable product)
Implementation: Finance to update budget in system by Oct 25
Date: 2025-10-23
```

---

## Decision vs. Action Item

**Decision**: We will increase the budget to $100k
**Action Items generated from decision**:
1. Finance to update project budget in system by Oct 25
2. Project Manager to hire 2 developers by Nov 1
3. CFO to notify Board of budget change in November meeting

**Key Difference**: Decision is the choice made. Actions are the tasks needed to implement that choice.

---

---

## Cross-Domain Knowledge Integration

### When Decisions Affect Other Domains

Many decisions made in Change Agent meetings trigger updates to other domain knowledge. This reflects the **dual context** of Change Agent:
- **Context 1**: Managing change (captured in these meeting minutes)
- **Context 2**: Modifying other domains (updating their artefacts)

### Cross-Domain Decision Impact Examples

#### Product Onboarding Decision
**Decision**: "Approved FX Options product for trading"

**Change Agent Captures**:
- Meeting minutes with decision record
- Action items for implementation
- Decision rationale and authority

**Other Domains Affected** (Context 2 - Change Modifier):
- `[[market-risk/products/approved-products-list.md]]` - Add FX Options
- `[[market-risk/methodologies/risk-calculations.md]]` - Add risk methodology
- `[[market-risk/data/metrics-dictionary.md]]` - Define new metrics
- `[[credit-risk/policies/counterparty-limits.md]]` - Set credit limits
- `[[operations/systems/trading-platform-config.md]]` - Configure systems
- `[[compliance/reports/regulatory-reporting.md]]` - Update reports

**Check-Out/Check-In Workflow**:
See [[../meta/knowledge-evolution.md]] for how these cross-domain updates are managed through the formal change process.

#### Policy Change Decision
**Decision**: "Updated meeting minutes retention from 5 to 7 years"

**Change Agent Captures**:
- Decision record with regulatory rationale
- Action to update policy documents

**Other Domains Affected**:
- `[[change-agent/policies/documentation-standards.md]]` - Update retention policy
- `[[it-systems/storage/retention-policies.md]]` - Configure storage rules
- `[[compliance/policies/data-retention.md]]` - Align with regulatory requirements

#### Resource Allocation Decision
**Decision**: "Approved 2 additional developers for Project X"

**Change Agent Captures**:
- Budget approval decision
- Resource allocation action items

**Other Domains Affected**:
- `[[finance/budget/project-budgets.md]]` - Update budget allocation
- `[[hr/resources/headcount-plan.md]]` - Update hiring plan
- `[[project-management/projects/project-x/resources.md]]` - Assign resources

---

## Links to Other Knowledge

### Within Change Agent Domain
- [[meeting-types.md]] - Decision-making meeting type
- [[action-items-standards.md]] - How to capture actions generated from decisions
- [[../meta/knowledge-evolution.md]] - How decisions trigger cross-domain knowledge updates

### Cross-Domain Dependencies
When capturing decisions that affect other domains, consult:
- `[[risk-management/governance/decision-authority.md]]` - Who has authority to approve
- `[[product-management/products/product-categories.md]]` - Valid product types
- `[[finance/policies/budget-approval-limits.md]]` - Budget approval thresholds
- `[[compliance/policies/regulatory-requirements.md]]` - Regulatory constraints

**Note**: Cross-domain references shown in monospace (e.g., `[[domain/category/doc.md]]`) represent future knowledge documents in other domains. For MVP, these serve as architectural placeholders demonstrating the dual context pattern.
