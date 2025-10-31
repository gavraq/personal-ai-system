# Module 2, Step 2.5: Knowledge Layer

**What You'll Learn**: How to create the Knowledge Layer that provides domain-specific reference material for Claude to consult when executing skills, based on the Risk Taxonomy Framework principles.

**Prerequisites**:
- Module 2 Steps 2.1-2.4 completed
- Understanding of Skills Framework (Step 2.2)
- Understanding of Context Manager (Step 2.3)

**Estimated Time**: 45 minutes

---

## Overview

The Knowledge Layer provides structured domain knowledge that Claude can reference when executing skills. This is inspired by your Risk Taxonomy Framework approach to knowledge management in Risk Management.

### Knowledge Layer Purpose

Just as your Risk Taxonomy Framework provides:
- **Completeness**: Comprehensive coverage across risk domains
- **Consistency**: Standard application across different domains
- **Communication**: Clear articulation to staff, regulators, auditors

Our Knowledge Layer provides:
- **Domain Expertise**: Structured knowledge for each domain (Change Agent, Risk Management, etc.)
- **Skill Enhancement**: Reference material that makes skills more effective
- **Context Enrichment**: Additional context beyond session data

### Knowledge vs. Skills vs. Context

Let's clarify the three layers:

| Layer | Purpose | Example | When Used |
|-------|---------|---------|-----------|
| **Skills** | Step-by-step instructions for specific tasks | "How to capture meeting minutes" | Every skill execution |
| **Knowledge** | Domain-specific reference material | "What makes a good action item" | When skill needs domain expertise |
| **Context** | Session-specific captured information | "Last meeting had 5 attendees" | When session_id provided |

### Adapting Risk Taxonomy Framework: The Dual Context Pattern

Your Risk Taxonomy Framework reveals a critical insight: **domains operate in dual contexts**.

#### Context 1: Change Agent as Its Own Domain

Each domain (Market Risk, Credit Risk, Change Agent, etc.) has its own complete set of artefacts across all taxonomy levels:

| Risk Taxonomy Component | Change Agent Domain Artefacts | Example |
|------------------------|-------------------------------|---------|
| **Risks** | Risks specific to change management | "Poorly captured requirements lead to failed projects" |
| **Governance** | Change Agent governance forums | "Project steering committee structure" |
| **Policies** | Change management best practices | "Meeting minutes retention policy" |
| **Processes** | Meeting management processes | "Standard meeting structure with decision capture" |
| **Controls** | Quality controls for outputs | "Action item completeness checklist" |
| **Products** | Change Agent deliverables | "Meeting minutes, action logs, decision records" |
| **Reports** | Change management reports | "Project progress updates, meeting summaries" |
| **Feeds** | Information flows into Change Agent | "Meeting transcripts, notes, recordings" |
| **Data** | Change metrics | "Action item completion rates, meeting frequency" |
| **Methodologies** | Change frameworks | "Agile, Waterfall, Hybrid approaches" |
| **Systems** | Tools for change management | "Jira, meeting recording tools" |

#### Context 2: Change Agent as Change Modifier

This is the **key insight** from your framework: Change Agent also operates as a **modifier** of other domains.

**Example Scenario**: Market Risk onboards a new product
- **Change Agent captures** the decision in a meeting
- **Change Agent updates** Market Risk domain artefacts:
  - Market Risk Policies (add new product)
  - Market Risk Procedures (update risk calculation process)
  - Bank-wide Products list (add product)
  - Market Risk Data Feeds (ensure new metrics flow)
  - Market Risk Methodologies (add calculation methods)

**The Check-Out/Check-In Workflow**:
1. **Check Out**: Change Agent "checks out" current Market Risk artefacts
2. **Modify**: Updates are made during the change project
3. **Track**: Change Agent tracks what's changing and why
4. **Validate**: Changes are tested and signed off
5. **Check In**: Updated artefacts are "checked in" to production

This dual context means our Knowledge Layer must support:
- **Static knowledge**: Standards for Change Agent domain itself
- **Dynamic knowledge**: Tracking changes to other domain knowledge
- **Cross-domain linking**: References between domain knowledge bases

#### Domain-Specific vs. Shared Artefacts

Your framework also clarifies:
- **Domain-Specific**: Risks, Methodologies, Data (each domain has unique ones)
- **Shared**: Products (bank-wide list), some Governance (cross-domain committees)
- **Variable**: Change Agent has fewer artefacts in some areas (Data, Feeds, Models) compared to Risk Management

#### Implementation for MVP

For our MVP, we'll implement **Context 1** (Change Agent as its own domain) with the foundation for **Context 2** (change modifier):

**Phase 1 (MVP)**: Change Agent Domain Knowledge
- Meeting management processes
- Action item standards
- Decision capture standards

**Phase 2 (Future)**: Cross-Domain Knowledge Evolution
- Knowledge versioning (check-out/check-in)
- Cross-domain linking
- Change impact tracking

We'll start with the 3 most critical components for Context 1, with architecture that supports Context 2 expansion.

---

## Step 1: Create Knowledge Directory Structure

Let's create a taxonomy-based knowledge structure:

```bash
cd /Users/gavinslater/projects/life/risk-agents-app/backend
mkdir -p knowledge/change-agent/meeting-management
mkdir -p knowledge/change-agent/project-management
mkdir -p knowledge/change-agent/requirements-gathering
```

**Directory Structure**:
```
backend/knowledge/
└── change-agent/                    # Domain
    ├── meeting-management/          # Category
    │   ├── meeting-types.md         # Knowledge document
    │   ├── action-items-standards.md
    │   └── decision-capture.md
    ├── project-management/          # Future category
    └── requirements-gathering/      # Future category
```

**Why This Structure**:
- Mirrors Skills Framework structure (domain/category)
- Federated ownership: Each category owned by domain experts
- Linkage-based: Knowledge docs reference each other
- Scalable: Easy to add new domains and categories

---

## Step 2: Create Meeting Types Knowledge Document

This document defines the different types of meetings and their characteristics.

Create **`backend/knowledge/change-agent/meeting-management/meeting-types.md`**:

```markdown
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

## Links to Other Knowledge
- [[action-items-standards.md]] - Standards for capturing action items
- [[decision-capture.md]] - Standards for capturing decisions
```

---

## Step 3: Create Action Items Standards Knowledge Document

This document defines what makes a complete, actionable action item.

Create **`backend/knowledge/change-agent/meeting-management/action-items-standards.md`**:

```markdown
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

## Links to Other Knowledge
- [[meeting-types.md]] - Different meeting types and their requirements
- [[decision-capture.md]] - How to capture decisions separately from actions
```

---

## Step 4: Create Decision Capture Knowledge Document

This document defines how to properly capture decisions made in meetings.

Create **`backend/knowledge/change-agent/meeting-management/decision-capture.md`**:

```markdown
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

Decision: Approved to proceed with Project X
Rationale: All readiness criteria met, risks acceptable
Decision Maker: Project Steering Committee
Alternatives: Delay until Q1 (rejected - business case time-sensitive)
Implementation: Project Manager to initiate project by Nov 1
Date: 2025-10-23

### Vendor Selection

Decision: Selected Vendor A for cloud infrastructure
Rationale: Superior technical capabilities, 24/7 support, meets compliance requirements
Decision Maker: CTO with input from Architecture Board
Alternatives: Vendor B (lower cost, limited support), Vendor C (declined)
Implementation: Procurement to issue PO by Oct 30, implementation begins Nov 1
Date: 2025-10-23
Review: Assess vendor performance at 6-month mark

### Scope Change

Decision: Remove Feature Y from current sprint, move to next sprint
Rationale: Feature X taking longer than estimated, risking sprint commitment
Decision Maker: Scrum Master with team consensus
Alternatives: Extend sprint (rejected - disrupts cadence), reduce Feature X scope (rejected - impacts quality)
Implementation: Product Owner to update backlog, communicate to stakeholders
Date: 2025-10-23

### Budget Approval

Decision: Approved budget increase from $80k to $100k
Rationale: Additional developers needed to meet committed timeline
Decision Maker: Finance Director and VP Engineering
Alternatives: Maintain budget with extended timeline (rejected - contract penalty), maintain budget with reduced scope (rejected - minimum viable product)
Implementation: Finance to update budget in system by Oct 25
Date: 2025-10-23

---

## Decision vs. Action Item

**Decision**: We will increase the budget to $100k
**Action Items generated from decision**:
1. Finance to update project budget in system by Oct 25
2. Project Manager to hire 2 developers by Nov 1
3. CFO to notify Board of budget change in November meeting

**Key Difference**: Decision is the choice made. Actions are the tasks needed to implement that choice.

---

## Links to Other Knowledge
- [[meeting-types.md]] - Decision-making meeting type
- [[action-items-standards.md]] - How to capture actions generated from decisions

---

## Step 5: Update Skills to Reference Knowledge Layer

Now we need to update our meeting-minutes-capture skill to reference this knowledge.

Update **`backend/.claude/skills/change-agent/meeting-management/meeting-minutes-capture/SKILL.md`**:

Find the "Instructions Available" section and update it:

## Instructions Available

This skill provides detailed step-by-step instructions:

1. **capture.md** - How to capture comprehensive meeting minutes
2. **extract-actions.md** - How to extract and format action items

## Knowledge References

This skill utilizes knowledge from the Change Agent domain:

- **meeting-types.md** - Understanding different meeting types and what to capture for each
- **action-items-standards.md** - Standards for complete, actionable action items
- **decision-capture.md** - Standards for properly documenting decisions

These knowledge documents provide best practices and standards that enhance the quality of the skill execution.
```

---

## Step 6: Integrate Knowledge into SkillsLoader

Now we need to extend `SkillsLoader` to load knowledge documents.

Update **`backend/agent/skills_loader.py`** to add knowledge loading capability:

Add this method after the `load_skill_resources` method (around line 250):

```python
def load_knowledge(self, domain: str, category: str, knowledge_file: str) -> str:
    """
    Load a knowledge document from the knowledge layer.

    Args:
        domain: Domain name (e.g., "change-agent")
        category: Category name (e.g., "meeting-management")
        knowledge_file: Knowledge file name (e.g., "action-items-standards.md")

    Returns:
        str: Content of the knowledge document

    Raises:
        FileNotFoundError: If knowledge file doesn't exist
    """
    knowledge_path = Path("knowledge") / domain / category / knowledge_file

    if not knowledge_path.exists():
        raise FileNotFoundError(f"Knowledge file not found: {knowledge_path}")

    with open(knowledge_path, 'r', encoding='utf-8') as f:
        return f.read()


def get_knowledge_files(self, domain: str, category: str) -> List[str]:
    """
    Get list of available knowledge files for a domain/category.

    Args:
        domain: Domain name
        category: Category name

    Returns:
        List[str]: List of knowledge file names
    """
    knowledge_dir = Path("knowledge") / domain / category

    if not knowledge_dir.exists():
        return []

    return [f.name for f in knowledge_dir.glob("*.md")]
```

---

## Step 7: Update RiskAgentClient to Use Knowledge

Update **`backend/agent/agent_client.py`** to enhance system prompts with knowledge.

Add this method after the `_build_system_prompt` method (around line 180):

```python
def _enhance_with_knowledge(self, skill_metadata: SkillMetadata, system_prompt: str) -> str:
    """
    Enhance system prompt with relevant knowledge documents.

    Args:
        skill_metadata: Skill metadata to determine relevant knowledge
        system_prompt: Base system prompt

    Returns:
        str: Enhanced system prompt with knowledge
    """
    # Get knowledge files for this skill's domain/category
    knowledge_files = self.skills_loader.get_knowledge_files(
        domain=skill_metadata.domain,
        category=skill_metadata.category
    )

    if not knowledge_files:
        return system_prompt  # No knowledge available, return as-is

    # Load up to 3 most relevant knowledge documents
    knowledge_content = []
    for knowledge_file in knowledge_files[:3]:  # Limit to 3 to manage context size
        try:
            content = self.skills_loader.load_knowledge(
                domain=skill_metadata.domain,
                category=skill_metadata.category,
                knowledge_file=knowledge_file
            )
            knowledge_content.append(f"## Knowledge: {knowledge_file}\n\n{content}")
        except FileNotFoundError:
            continue  # Skip if file not found

    if knowledge_content:
        knowledge_section = "\n\n---\n\n# DOMAIN KNOWLEDGE\n\n" + "\n\n".join(knowledge_content)
        return system_prompt + knowledge_section

    return system_prompt
```

Now update the `query` method to use this enhancement (around line 100):

```python
def query(self, user_message: str, context: Optional[Dict[str, Any]] = None,
          system_prompt: Optional[str] = None, skill_name: Optional[str] = None) -> str:
    """
    Send a query to Claude with optional skill, context, and knowledge.

    Args:
        user_message: The user's query
        context: Optional context from ContextManager
        system_prompt: Optional custom system prompt (overrides default)
        skill_name: Optional skill name to load and include

    Returns:
        str: Claude's response
    """
    # Build base system prompt
    final_system_prompt = system_prompt or self._build_system_prompt()

    # If skill specified, enhance with skill instructions AND knowledge
    if skill_name:
        try:
            # Find skill metadata
            skills = self.skills_loader.list_skills()
            skill_metadata = next((s for s in skills if s.name == skill_name), None)

            if skill_metadata:
                # Load skill content
                skill_data = self.skills_loader.load_skill_details(skill_metadata.skill_path)
                final_system_prompt += f"\n\n# SKILL: {skill_name}\n\n{skill_data['content']}"

                # Enhance with knowledge
                final_system_prompt = self._enhance_with_knowledge(skill_metadata, final_system_prompt)
        except FileNotFoundError:
            pass  # Skill not found, continue without it

    # Add context if provided
    if context:
        context_text = self._format_context(context)
        final_system_prompt += f"\n\n{context_text}"

    # Call Claude API
    response = self.client.messages.create(
        model=self.model,
        max_tokens=self.max_tokens,
        system=final_system_prompt,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )

    return response.content[0].text
```

---

## Step 8: Test Knowledge Layer

Let's test the knowledge layer integration:

```bash
# 1. Verify knowledge files exist
cd /Users/gavinslater/projects/life/risk-agents-app/backend
ls -la knowledge/change-agent/meeting-management/

# 2. Test loading knowledge via Skills Loader (Python REPL)
python3 << 'EOF'
from pathlib import Path
from agent.skills_loader import SkillsLoader

loader = SkillsLoader(Path(".claude/skills"))

# Test get_knowledge_files
files = loader.get_knowledge_files("change-agent", "meeting-management")
print(f"Knowledge files found: {files}")

# Test load_knowledge
content = loader.load_knowledge("change-agent", "meeting-management", "action-items-standards.md")
print(f"\nKnowledge content length: {len(content)} characters")
print(f"First 200 chars: {content[:200]}...")
EOF
```

---

## Concepts Explained

### 1. **Knowledge Layer vs. Skills Layer**

**Skills** = "How to do something" (instructions)
**Knowledge** = "What you need to know" (reference material)

Example:
- **Skill**: "How to capture meeting minutes" (capture.md)
- **Knowledge**: "What makes a good action item" (action-items-standards.md)

The skill tells Claude the steps. The knowledge helps Claude execute those steps with domain expertise.

### 2. **Taxonomy-Based Organization**

Inspired by your Risk Taxonomy Framework:
- **Inventory Components**: Meeting types, action standards, decision standards
- **Completeness**: Coverage of all meeting scenarios
- **Consistency**: Standard formats across all meetings
- **Communication**: Clear articulation to users

### 3. **Federated Ownership**

Just like your Risk Taxonomy Framework:
- **Central Framework**: Knowledge directory structure and standards
- **Distributed Maintenance**: Each category owned by domain experts
- **Change Process**: Update knowledge as practices evolve

### 4. **Linkage-Based Structure**

Knowledge documents link to each other:
```markdown
## Links to Other Knowledge
- [[meeting-types.md]] - Different meeting types
- [[action-items-standards.md]] - Action item standards
- [[decision-capture.md]] - Decision capture standards
```

This creates a "knowledge map" similar to your Risk Taxonomy artefact linkages.

### 5. **Progressive Disclosure Extended**

Now we have 4 layers that load progressively:

1. **Skill Metadata** - "What this skill does"
2. **Skill Instructions** - "How to execute this skill"
3. **Domain Knowledge** - "What you need to know for this domain"
4. **Session Context** - "What happened in this specific session"

Claude gets just enough context at each layer.

---

## What We Built

### Files Created (3 knowledge documents):

1. **`backend/knowledge/change-agent/meeting-management/meeting-types.md`**
   - Defines 6 standard meeting types
   - Critical capture elements for each type
   - Meeting type selection guide

2. **`backend/knowledge/change-agent/meeting-management/action-items-standards.md`**
   - Complete action item structure (WHAT, WHO, WHEN, WHY, Dependencies)
   - Quality checklist
   - Common patterns
   - Priority levels

3. **`backend/knowledge/change-agent/meeting-management/decision-capture.md`**
   - Complete decision structure
   - Decision quality checklist
   - Common decision patterns
   - Decision vs. action item distinction

### Code Enhanced (2 files):

1. **`backend/agent/skills_loader.py`**
   - Added `load_knowledge()` method
   - Added `get_knowledge_files()` method

2. **`backend/agent/agent_client.py`**
   - Added `_enhance_with_knowledge()` method
   - Updated `query()` method to use knowledge

### Knowledge Layer Benefits:

1. **Better Outputs**: Claude produces higher quality meeting minutes because it understands standards
2. **Consistency**: All meeting minutes follow the same structure and quality criteria
3. **Scalability**: Easy to add new knowledge documents as we grow
4. **Maintenance**: Update knowledge separately from skills (federated ownership)
5. **Reusability**: Same knowledge used across multiple skills

---

## Next Steps

In Step 2.6, we'll create API endpoints to:
- Browse available knowledge documents
- Load specific knowledge documents
- Integrate knowledge into query requests

In Step 2.7, we'll do end-to-end testing to verify:
- Skills can access knowledge
- Knowledge enhances Claude's responses
- Complete integration works properly

---

**Progress**: Module 2 is now **90% complete**!

**What's Next**: Step 2.6 - API Endpoints (15 minutes)
