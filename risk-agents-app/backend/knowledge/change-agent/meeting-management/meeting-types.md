# Meeting Types Knowledge

## Purpose
Defines standard meeting types, their characteristics, and what information should be captured for each type.

## Meeting Type Taxonomy

### 1. Decision-Making Meeting
**Purpose**: Make specific decisions on issues requiring consensus

**Key Characteristics**:
- Clear agenda with decision points
- Defined decision-making authority
- Quorum requirements may apply
- Formal voting may be required

**Critical Capture Elements**:
- Decision made (explicit statement)
- Rationale for decision
- Dissenting opinions (if any)
- Implementation owner
- Implementation timeline

**Example**: Board meeting, steering committee, approval forum

---

### 2. Planning Meeting
**Purpose**: Develop plans, strategies, or roadmaps

**Key Characteristics**:
- Forward-looking focus
- Multiple scenarios may be discussed
- Dependencies and constraints identified
- Resource requirements identified

**Critical Capture Elements**:
- Objectives agreed
- Key milestones identified
- Resource commitments
- Dependencies noted
- Next planning checkpoint

**Example**: Sprint planning, project kickoff, quarterly planning

---

### 3. Status Update Meeting
**Purpose**: Share progress updates and identify blockers

**Key Characteristics**:
- Regular cadence (daily, weekly, monthly)
- Structured format (often round-robin)
- Focus on blockers and risks
- Brief and focused

**Critical Capture Elements**:
- Progress since last meeting
- Blockers identified
- Risks raised
- Help requested
- Next checkpoint

**Example**: Daily standup, weekly team sync, monthly status review

---

### 4. Problem-Solving Meeting
**Purpose**: Analyze and resolve specific problems or issues

**Key Characteristics**:
- Problem statement clearly defined
- Root cause analysis
- Solution options explored
- Action plan developed

**Critical Capture Elements**:
- Problem definition
- Root causes identified
- Solution options considered
- Chosen solution and rationale
- Action plan with owners

**Example**: Incident review, troubleshooting session, root cause analysis

---

### 5. Brainstorming Meeting
**Purpose**: Generate ideas and explore possibilities

**Key Characteristics**:
- Open and creative environment
- No idea criticism during generation phase
- High volume of ideas encouraged
- Ideas recorded without judgment

**Critical Capture Elements**:
- All ideas generated (even if not pursued)
- Ideas that will be explored further
- Next steps for idea evaluation
- Follow-up meeting plans

**Example**: Innovation workshop, design thinking session, strategy offsite

---

### 6. Information Sharing Meeting
**Purpose**: Disseminate information to stakeholders

**Key Characteristics**:
- One-way or primarily one-way communication
- May include Q&A
- Often has presentation materials
- May be recorded for those unable to attend

**Critical Capture Elements**:
- Key information shared
- Questions asked and answers provided
- Concerns raised
- Follow-up information requests
- Where to find more details

**Example**: Town hall, training session, project briefing

---

## Meeting Type Selection Guide

Use this decision tree to identify meeting type:

1. **Is the primary purpose to make a decision?** → Decision-Making Meeting
2. **Is the primary purpose to develop a plan?** → Planning Meeting
3. **Is this a regular progress check?** → Status Update Meeting
4. **Is there a specific problem to solve?** → Problem-Solving Meeting
5. **Is the purpose to generate new ideas?** → Brainstorming Meeting
6. **Is the purpose to share information?** → Information Sharing Meeting

---

## Hybrid Meetings

Some meetings may combine multiple types:
- "Planning & Decision Meeting": Develop plan AND approve it
- "Status & Problem-Solving": Update progress AND resolve blockers
- "Brainstorming & Planning": Generate ideas AND prioritize them

For hybrid meetings, capture critical elements from BOTH meeting types.

---

---

## Cross-Domain Meeting Context

Different meeting types often involve different domains. Understanding which domains are affected helps identify what knowledge artefacts may need updating.

### Meeting Type → Domain Impact Mapping

| Meeting Type | Typical Domains Involved | Likely Cross-Domain Updates |
|--------------|-------------------------|----------------------------|
| **Decision-Making** | Change Agent + 1-3 other domains | Policy updates, approval lists, governance records |
| **Planning** | Change Agent + Project domain | Project plans, resource allocations, milestone schedules |
| **Status Update** | Single domain (usually) | Progress reports, risk logs (minimal cross-domain impact) |
| **Problem-Solving** | 2-3 domains (cross-functional) | Issue logs, process fixes, system configurations |
| **Brainstorming** | Single domain (usually) | Ideas database (minimal cross-domain impact) |
| **Information Sharing** | All domains (broadcast) | No knowledge updates (read-only) |

### Cross-Domain Meeting Examples

#### Product Approval Committee (Decision-Making + Cross-Domain)
**Domains Present**:
- Change Agent (facilitating)
- Product Management (presenting new product)
- Market Risk (assessing market risk)
- Credit Risk (assessing credit risk)
- Operations (confirming operational readiness)
- Compliance (regulatory approval)

**Critical Capture Elements** (includes cross-domain):
- **Decision**: Product approved or rejected
- **Rationale**: Risk assessment summary from each domain
- **Cross-Domain Updates Required**:
  - `[[product-management/products/approved-products-list.md]]` - Add product
  - `[[market-risk/products/products-risk-characteristics.md]]` - Add risk profile
  - `[[credit-risk/policies/counterparty-limits.md]]` - Set credit limits
  - `[[operations/systems/trading-platform-config.md]]` - Configure systems
  - `[[compliance/reports/regulatory-reporting.md]]` - Update filing requirements

**Change Agent Role**: Captures decision and creates action items for each domain to update their artefacts via check-out/check-in workflow.

#### Project Steering Committee (Planning + Decision + Cross-Domain)
**Domains Present**:
- Change Agent (facilitating)
- Project Management (project status)
- Finance (budget tracking)
- HR (resource allocation)
- IT (technical progress)

**Critical Capture Elements** (includes cross-domain):
- **Objectives**: Project milestones agreed
- **Resource Commitments**: Who from which domain
- **Budget Decisions**: Funding allocations
- **Cross-Domain Updates Required**:
  - `[[project-management/projects/project-x/plan.md]]` - Update project plan
  - `[[finance/budget/project-budgets.md]]` - Update budget allocation
  - `[[hr/resources/headcount-plan.md]]` - Update hiring plan
  - `[[it/systems/project-x/technical-spec.md]]` - Update technical specifications

**Change Agent Role**: Tracks commitments and ensures each domain updates their artefacts accordingly.

#### Risk Committee (Status Update + Problem-Solving + Cross-Domain)
**Domains Present**:
- Change Agent (facilitating, capturing minutes)
- Market Risk (reporting market risk metrics)
- Credit Risk (reporting credit risk metrics)
- Operational Risk (reporting operational incidents)
- Compliance (reporting regulatory issues)

**Critical Capture Elements** (includes cross-domain):
- **Progress**: Each risk domain reports key metrics
- **Blockers**: Issues requiring escalation or cross-domain coordination
- **Decisions**: Approvals for risk limit increases, exception handling
- **Cross-Domain Updates Triggered**:
  - `[[market-risk/reports/monthly-risk-report.md]]` - Update with committee feedback
  - `[[credit-risk/policies/credit-limits.md]]` - Update if limits changed
  - `[[operational-risk/incidents/incident-log.md]]` - Document incident resolutions
  - `[[compliance/regulatory/action-tracker.md]]` - Track regulatory actions

**Change Agent Role**: Captures the narrative and ensures domain-specific reports are updated to reflect committee decisions.

### Meeting Type Selection with Cross-Domain Awareness

When identifying meeting type, also consider:

1. **How many domains are involved?**
   - Single domain → Simpler capture, minimal cross-domain updates
   - Multi-domain → More complex, significant cross-domain coordination

2. **Are decisions affecting other domains?**
   - Yes → Check-out/check-in workflow will be triggered
   - No → Standard meeting capture sufficient

3. **Who owns the artefacts being discussed?**
   - Change Agent owns → Direct updates
   - Other domains own → Action items for domain owners

4. **What's the change impact?**
   - Low impact → Update meeting minutes only
   - High impact → Update multiple domain artefacts via formal change process

---

## Links to Other Knowledge

### Within Change Agent Domain
- [[action-items-standards.md]] - Standards for capturing action items (including cross-domain)
- [[decision-capture.md]] - Standards for capturing decisions (including cross-domain impact)
- [[../meta/knowledge-evolution.md]] - How meetings trigger cross-domain knowledge updates

### Cross-Domain Considerations
For cross-domain meetings, consult domain-specific knowledge:
- **Authority**: `[[risk-management/governance/decision-authority.md]]` - Who can approve cross-domain decisions
- **Products**: `[[product-management/products/product-categories.md]]` - Valid products across domains
- **Budgets**: `[[finance/policies/budget-approval-limits.md]]` - Budget thresholds requiring approval
- **Compliance**: `[[compliance/policies/regulatory-requirements.md]]` - Regulatory constraints affecting decisions

**Note**: Cross-domain references shown in monospace (e.g., `[[domain/category/doc.md]]`) represent future knowledge documents in other domains. For MVP, these serve as architectural placeholders demonstrating the dual context pattern.
