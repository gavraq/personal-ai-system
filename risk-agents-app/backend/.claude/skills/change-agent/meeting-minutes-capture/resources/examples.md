# Meeting Minutes Capture - Examples

This document provides real-world examples of transforming raw meeting content into structured meeting minutes.

## Example 1: Simple Team Meeting

### Input (Raw Notes):
```
Team standup - Jan 15 2025
Present: John, Sarah, Mike

John: Finished the API integration, tested successfully
Sarah: Working on frontend components, need design specs from Mike
Mike: Will send designs by EOW, also need to discuss deployment strategy
John volunteered to set up CI/CD pipeline
Next meeting Friday 10am
```

### Output (Structured Minutes):
```markdown
# Meeting Minutes: Team Standup

**Date**: 2025-01-15
**Time**: 09:00 - 09:15 EST
**Location**: Virtual (Zoom)
**Meeting Type**: Status Update

## Attendees
**Present**:
- John - Backend Developer
- Sarah - Frontend Developer
- Mike - Lead Designer

## Agenda

### 1. Progress Updates

**Discussion**:
- John completed API integration and testing
- Sarah progressing on frontend components, blocked on design specs
- Mike to provide designs by end of week
- Deployment strategy needs discussion

## Action Items

| # | Item | Owner | Due Date | Priority | Status |
|---|------|-------|----------|----------|--------|
| 1 | Send design specs to Sarah | Mike | 2025-01-19 | High | Pending |
| 2 | Set up CI/CD pipeline | John | 2025-01-22 | Medium | Pending |
| 3 | Schedule deployment strategy discussion | Mike | 2025-01-19 | High | Pending |

## Next Steps
- [ ] Mike to send designs by EOW
- [ ] Team to review CI/CD setup next week

## Next Meeting
- **Date**: 2025-01-19
- **Time**: 10:00 AM EST
- **Agenda**: Deployment strategy discussion

---
**Minutes Prepared By**: AI Assistant
**Date Prepared**: 2025-01-15
```

## Example 2: Client Meeting with Decisions

### Input (Transcript):
```
Meeting with Acme Corp - Jan 16 2025
Attendees: Sarah (us), Tom and Lisa (Acme)

Tom: We've reviewed your proposal. We like the approach but concerned about timeline.
Sarah: What timeline were you thinking?
Tom: We need to launch by Q2. Can you do March 31?
Sarah: That's tight but feasible if we reduce scope Phase 1. Move reporting to Phase 2?
Lisa: That works. Budget approved for Phase 1 is $150K.
Tom: Agreed. Let's proceed.
Sarah: I'll send updated SOW by Friday. Need signed contract by Jan 25 to hit March deadline.
Lisa: We can do that. Tom will be main point of contact.
```

### Output (Structured Minutes):
```markdown
# Meeting Minutes: Acme Corp - Project Kickoff

**Date**: 2025-01-16
**Time**: 14:00 - 14:30 EST
**Location**: Virtual (Google Meet)
**Meeting Type**: Client Meeting

## Attendees
**Present**:
- Sarah - Account Manager (Our Company)
- Tom - Project Sponsor (Acme Corp)
- Lisa - Procurement Manager (Acme Corp)

## Meeting Objectives
Review and finalize project proposal, timeline, and budget

## Agenda

### 1. Proposal Review & Timeline Discussion

**Discussion**:
- Acme reviewed proposal and approves the approach
- Concern raised about timeline to meet Q2 launch
- Hard deadline of March 31, 2025 required
- Sarah proposed reducing Phase 1 scope by moving reporting features to Phase 2
- Client agreed to phased approach

**Outcome**:
- Proceed with reduced Phase 1 scope
- Phase 2 (reporting) to be scheduled post-launch

### 2. Budget & Contracting

**Discussion**:
- Budget approved for Phase 1: $150,000
- Contract signing needed by Jan 25 to meet March deadline
- Tom designated as main point of contact

## Decisions Made

### Decision 1: Phase 1 Scope Reduction
- **Decision**: Move reporting features from Phase 1 to Phase 2
- **Rationale**: Enable March 31 launch deadline while delivering core functionality
- **Impact**: Phase 1 delivers core features only; reporting deferred to Q2
- **Effective Date**: Immediate
- **Decided By**: Tom (Acme), approved by Lisa

### Decision 2: Project Approval & Budget
- **Decision**: Proceed with project at $150K Phase 1 budget
- **Rationale**: Proposal meets requirements within acceptable budget
- **Impact**: Project kicks off upon contract execution
- **Effective Date**: Upon contract signing (target: Jan 25)
- **Decided By**: Lisa (Procurement) & Tom (Sponsor)

### Decision 3: Point of Contact
- **Decision**: Tom is primary POC for project
- **Rationale**: Tom is project sponsor and stakeholder
- **Impact**: All project communications route through Tom
- **Effective Date**: Immediate

## Action Items

| # | Item | Owner | Due Date | Priority | Status | Dependencies |
|---|------|-------|----------|----------|--------|--------------|
| 1 | Send updated SOW with Phase 1 scope | Sarah | 2025-01-19 | Critical | Pending | None |
| 2 | Review and approve updated SOW | Tom | 2025-01-22 | Critical | Pending | Item #1 |
| 3 | Execute contract | Lisa | 2025-01-25 | Critical | Pending | Item #2 |
| 4 | Schedule project kickoff meeting | Sarah | 2025-01-26 | High | Pending | Item #3 |

## Next Steps
- [ ] Sarah to prepare revised SOW by EOW
- [ ] Acme to review and provide feedback
- [ ] Target contract signing by Jan 25
- [ ] Project kickoff scheduled for week of Jan 29

## Next Meeting
- **Date**: TBD (Week of Jan 29)
- **Time**: TBD
- **Location**: TBD
- **Agenda**: Project Kickoff, Team Introductions, Sprint Planning

---
**Minutes Prepared By**: Sarah Johnson
**Date Prepared**: 2025-01-16
**Distribution List**: Tom (Acme), Lisa (Acme), Project Team
```

## Example 3: Complex Planning Meeting

### Input (Detailed Notes):
```
Q1 Planning Meeting - Jan 17, 2025
10am-12pm Conference Room B
Present: Sarah (PM), John (Dev), Mike (Design), Lisa (QA), Tom (Product)

[10:00] Tom presented Q1 objectives: launch new dashboard, improve performance
[10:15] Mike raised concern about current design system being outdated
[10:20] Discussed creating new design system - estimated 3 weeks
[10:30] John suggested performance audit first before optimization work
[10:45] Lisa mentioned QA resources are limited - only available 50% time
[11:00] Decided to split Q1 into 2 sprints
[11:15] Sprint 1: Design system + performance audit (weeks 1-6)
[11:20] Sprint 2: Dashboard development (weeks 7-13)
[11:30] Concerns about timeline being tight
[11:40] Agreed to weekly check-ins, bi-weekly sprint reviews
[11:50] Tom to get budget approval for potential contractor if needed
```

### Output:
```markdown
# Meeting Minutes: Q1 Planning Meeting

**Date**: 2025-01-17
**Time**: 10:00 - 12:00 EST
**Location**: Conference Room B
**Meeting Type**: Planning

## Attendees
**Present**:
- Sarah - Project Manager
- John - Senior Developer
- Mike - Lead Designer
- Lisa - QA Manager
- Tom - Product Owner

## Meeting Objectives
Plan Q1 deliverables, timeline, and resource allocation

## Agenda

### 1. Q1 Objectives Review (10:00 - 10:15)
**Discussion**:
- Tom presented Q1 goals: launch new dashboard and improve application performance
- Team acknowledged objectives

### 2. Design System Discussion (10:15 - 10:30)
**Discussion**:
- Mike raised concern that current design system is outdated
- Creating new design system estimated at 3 weeks effort
- New system would benefit both dashboard and future work

### 3. Performance Strategy (10:30 - 10:45)
**Discussion**:
- John recommended starting with performance audit before optimization
- Audit will identify specific bottlenecks and prioritize fixes
- Estimated 2 weeks for comprehensive audit

### 4. Resource Constraints (10:45 - 11:00)
**Discussion**:
- Lisa flagged that QA team only available at 50% capacity for Q1
- May impact testing timeline
- Tom noted possibility of bringing in contractor if needed

### 5. Sprint Planning (11:00 - 11:40)
**Discussion**:
- Team agreed timeline is tight for Q1
- Decision to split work into 2 focused sprints
- Sprint 1: Foundation work (design system + performance audit)
- Sprint 2: Dashboard development and optimization implementation
- Weekly check-ins and bi-weekly sprint reviews for close monitoring

## Decisions Made

### Decision 1: Create New Design System
- **Decision**: Build new design system before dashboard development
- **Rationale**: Current system outdated; new system benefits multiple initiatives
- **Impact**: 3-week investment upfront, faster development afterward
- **Effective Date**: Sprint 1 (Weeks 1-6)
- **Decided By**: Team consensus

### Decision 2: Conduct Performance Audit First
- **Decision**: Run comprehensive performance audit before optimization work
- **Rationale**: Data-driven approach to identify actual bottlenecks
- **Impact**: 2 weeks for audit, ensures optimization efforts are targeted
- **Effective Date**: Sprint 1 (Weeks 1-6)
- **Decided By**: John (recommended), team agreed

### Decision 3: Two-Sprint Approach for Q1
- **Decision**: Split Q1 into 2 six-week sprints
  - Sprint 1: Design system + Performance audit (Weeks 1-6)
  - Sprint 2: Dashboard development + Optimization (Weeks 7-13)
- **Rationale**: Tight timeline requires focused execution; foundation work enables faster Sprint 2
- **Impact**: Sequential delivery, dashboard launches end of Q1
- **Effective Date**: Immediate
- **Decided By**: Team consensus, approved by Tom

### Decision 4: Weekly Check-ins & Reviews
- **Decision**: Weekly team check-ins, bi-weekly sprint reviews
- **Rationale**: Tight timeline requires close monitoring
- **Impact**: Increased meeting time, better visibility and risk management
- **Effective Date**: Starting next week
- **Decided By**: Sarah (recommended), team agreed

## Action Items

| # | Item | Owner | Due Date | Priority | Status | Dependencies |
|---|------|-------|----------|----------|--------|--------------|
| 1 | Define design system scope and components | Mike | 2025-01-24 | Critical | Pending | None |
| 2 | Create performance audit plan | John | 2025-01-24 | Critical | Pending | None |
| 3 | Finalize Sprint 1 & 2 detailed plans | Sarah | 2025-01-24 | High | Pending | Items #1,#2 |
| 4 | Get budget approval for potential contractor | Tom | 2025-01-31 | Medium | Pending | None |
| 5 | Set up weekly check-in meetings | Sarah | 2025-01-19 | High | Pending | None |
| 6 | Assess QA capacity and create testing plan | Lisa | 2025-01-31 | High | Pending | Item #3 |

## Open Issues

| # | Issue | Raised By | Status | Notes |
|---|-------|-----------|--------|-------|
| 1 | QA resource capacity constraint (50% available) | Lisa | Open | May need contractor; Tom to pursue budget approval |
| 2 | Risk of timeline slippage | Sarah | Open | Monitoring via weekly check-ins |

## Parking Lot
- Mobile responsiveness improvements (deferred to Q2)
- Accessibility audit (deferred to Q2)

## Next Steps
- [ ] Sprint 1 planning meeting scheduled for Jan 22
- [ ] Team to finalize work estimates by Jan 24
- [ ] Weekly check-ins start Jan 24 (Tuesdays 10am)
- [ ] First sprint review scheduled for March 5

## Next Meeting
- **Date**: 2025-01-22
- **Time**: 10:00 AM EST
- **Location**: Conference Room B
- **Agenda**: Sprint 1 Detailed Planning

---
**Minutes Prepared By**: Sarah Thompson
**Date Prepared**: 2025-01-17
**Distribution List**: All attendees, Executive Team (FYI)
```

## Key Takeaways from Examples

1. **Simpler meetings = simpler minutes**: Example 1 is brief and to-the-point
2. **Decision-heavy meetings need detail**: Example 2 captures all decisions with context
3. **Long meetings need structure**: Example 3 uses timestamps and clear sections
4. **Action items always in table format**: Consistent, scannable, trackable
5. **Include context**: Rationale for decisions helps future understanding
6. **Be specific**: Dates, names, and deliverables are concrete
