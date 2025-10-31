---
name: status-report-generator
description: Generate executive status reports with RAG status, key metrics, accomplishments, risks, and next steps
domain: change-agent
category: project-management
taxonomy: change-agent/project-management
parameters:
  - project_data
  - reporting_period
output_format: structured_markdown
estimated_duration: 4-6 minutes
tags:
  - status-report
  - executive-summary
  - rag-status
  - project-health
version: 1.0.0
author: Risk Agents Team
---

# Status Report Generator Skill

## Purpose
Generate professional, executive-level status reports with RAG (Red/Amber/Green) indicators, key metrics, accomplishments, risks, issues, and next steps for stakeholder communication.

## When to Use This Skill
- Weekly/bi-weekly project status updates
- Monthly executive summaries
- Board or steering committee reporting
- Stakeholder communication and transparency
- Project health dashboards

## How It Works
This skill transforms project data into an executive-friendly status report with:

1. **Executive Summary**: High-level project health and key messages (3-4 sentences)
2. **RAG Status**: Red/Amber/Green indicators for scope, schedule, budget, quality
3. **Key Metrics**: Quantitative progress indicators with trend arrows
4. **Accomplishments**: What was delivered this period (wins and achievements)
5. **Risks & Issues**: Active concerns with severity and mitigation
6. **Next Steps**: Upcoming milestones and focus areas
7. **Decisions Needed**: Items requiring executive input or approval

## Parameters

### Required Parameters
- **`project_data`** (object): Project information including:
  - `project_name` (string): Name of the project
  - `status` (object): Current status across dimensions
  - `accomplishments` (array): Recent achievements
  - `metrics` (object): Key performance indicators

### Recommended Parameters
- **`reporting_period`** (object): Time period for this report
  - `start_date` (date): Period start
  - `end_date` (date): Period end
  - `report_date` (date): Report generation date

### Optional Parameters
- **`previous_period_data`** (object): Data from previous report for trend comparison
- **`forecast`** (object): Forward-looking projections
- **`custom_sections`** (array): Additional sections to include

## Expected Output

Structured Markdown executive status report:

```markdown
# Project Status Report: Customer Portal Redesign

**Report Date**: October 26, 2025
**Reporting Period**: October 13 - October 26, 2025 (Week 3-4)
**Project Manager**: Sarah Johnson
**Executive Sponsor**: John Smith

---

## Executive Summary

The Customer Portal Redesign project is progressing well with **design phase 95% complete** and development starting on schedule. We achieved a major milestone this period with **stakeholder approval of final designs**. However, timeline is at risk (AMBER) due to a 3-day delay in CRM integration API documentation. Budget and scope remain on track (GREEN). Key decision needed: approve $5K additional budget for expedited user testing.

---

## Overall Health: 🟢 GREEN (Mostly On Track)

| Dimension | Status | Trend | Commentary |
|-----------|--------|-------|------------|
| **Scope** | 🟢 GREEN | → Stable | All deliverables defined, no scope changes this period |
| **Schedule** | 🟡 AMBER | ↓ Declining | 3-day delay in CRM API docs, mitigation plan in place |
| **Budget** | 🟢 GREEN | ↑ Improving | $142K of $150K spent (94.7%), tracking well |
| **Quality** | 🟢 GREEN | → Stable | User testing feedback positive (4.7/5), no quality issues |
| **Team** | 🟢 GREEN | → Stable | Team morale high, no resource constraints |
| **Risks** | 🟡 AMBER | → Stable | 2 active high risks, both have mitigation plans |

**Status Legend**:
- 🟢 **GREEN**: On track, no concerns
- 🟡 **AMBER**: At risk, mitigation plan in place
- 🔴 **RED**: Off track, immediate attention required
- **Trends**: ↑ Improving | → Stable | ↓ Declining

---

## Key Metrics

| Metric | Current | Target | % Complete | Trend | Status |
|--------|---------|--------|-----------|-------|--------|
| **Design Completion** | 95% | 100% | 95% | ↑ | 🟢 |
| **Development Progress** | 15% | 10% | 150% ahead of plan | ↑ | 🟢 |
| **User Testing Sessions** | 23 | 50 | 46% | ↑ | 🟢 |
| **Budget Spent** | $142K | $150K | 94.7% | → | 🟢 |
| **Days Remaining** | 94 days | - | - | ↓ | 🟡 |
| **Open Issues** | 5 | 0 | - | ↓ | 🟡 |

---

## Accomplishments This Period

### Major Milestones Achieved
- ✅ **Final design mockups approved** (Oct 20) - All stakeholders signed off
- ✅ **Development environment set up** (Oct 22) - Team ready to start coding
- ✅ **First development sprint started** (Oct 25) - On schedule

### Key Deliverables Completed
1. **Complete UI/UX Design Package** (Oct 20)
   - 47 screens designed and approved
   - Style guide and component library finalized
   - Design handoff to development complete

2. **User Testing Round 2** (Oct 18)
   - 23 user sessions completed (target: 25 for this round)
   - 4.7/5 average satisfaction score (↑ from 4.2/5 in Round 1)
   - 15 usability improvements identified and incorporated

3. **Technical Architecture Approved** (Oct 24)
   - Architecture review board approval received
   - Security audit passed with minor recommendations
   - Performance targets validated through spike

### Additional Progress
- Team velocity increasing: 32 story points completed (target: 25)
- Documentation 80% complete (user guides, technical specs)
- Stakeholder satisfaction survey: 8.5/10 (high confidence in delivery)

---

## Risks & Issues

### Active High Risks (Requires Attention)

**RISK-001: CRM API Documentation Delay** 🔴 **HIGH**
- **Impact**: Development team blocked on CRM integration (affects 20% of sprint)
- **Probability**: Already occurred (3-day delay)
- **Mitigation**:
  - Scheduled emergency call with CRM vendor (Oct 27)
  - Dev team working on other features in parallel
  - Can absorb 3-day delay within existing buffer
- **Owner**: Michael Rodriguez (Tech Lead)
- **Status**: In mitigation, tracking closely

**RISK-002: User Testing Recruitment** 🟡 **MEDIUM**
- **Impact**: May not hit 50-user target for final testing round
- **Probability**: Medium (currently at 23, need 27 more by Nov 15)
- **Mitigation**:
  - Expanded recruitment to include partner companies
  - Offering $50 gift cards for participation (approved by sponsor)
  - Backup plan: lower statistical confidence threshold if needed
- **Owner**: Sarah Johnson (PM)
- **Status**: On track with mitigation

### Active Issues (Being Resolved)

**ISSUE-003: Design Tool License Shortage** 🟢 **LOW** (Resolved)
- **Description**: Temporary shortage of Figma licenses for QA team review
- **Impact**: 1-day delay in QA design review
- **Resolution**: Temporary licenses secured, review completed
- **Status**: ✅ Closed (Oct 23)

### Closed Risks This Period
- ~~RISK-004: Stakeholder alignment on design~~ (Resolved: designs approved Oct 20)

---

## Issues Log

| ID | Issue | Severity | Owner | Status | ETA |
|----|-------|----------|-------|--------|-----|
| ISS-005 | CRM API docs incomplete | High | Tech Lead | Active | Oct 27 |
| ISS-006 | Testing recruitment slow | Medium | PM | Active | Nov 1 |
| ISS-007 | Minor browser compatibility | Low | Dev Team | Active | Nov 5 |

---

## Next Steps (Next 2 Weeks)

### Immediate Priorities (This Week)
1. **Resolve CRM API documentation** (Owner: Tech Lead, Due: Oct 27)
   - Emergency vendor call scheduled
   - Get complete API spec and access credentials
   - Unblock development team

2. **Complete Development Sprint 1** (Owner: Dev Team, Due: Nov 1)
   - Implement core navigation and layout
   - Set up state management
   - Complete 25 story points minimum

3. **User Testing Round 3 Recruitment** (Owner: PM, Due: Oct 31)
   - Recruit 15 additional participants
   - Schedule sessions for November
   - Prepare testing scripts

### Upcoming Milestones (Next Month)
- **Nov 5**: Development Sprint 1 Review
- **Nov 12**: Development Sprint 2 Complete
- **Nov 15**: User Testing Round 3 (Final Round)
- **Nov 20**: QA Testing Begins
- **Nov 30**: UAT Sign-off Target

---

## Decisions Needed

### Requiring Executive Approval

**DECISION-001: Additional Budget for Expedited User Testing** ⚠️ **APPROVAL NEEDED**
- **Amount**: $5,000 (3.3% increase)
- **Purpose**: Higher incentives ($50 vs $25 gift cards) to accelerate recruitment
- **Justification**: Current pace may miss 50-user target; higher incentives proven to work
- **Impact if Approved**: Hit testing target, maintain confidence in design decisions
- **Impact if Not Approved**: Lower statistical confidence, may need design iterations post-launch
- **Recommendation**: Approve (low cost, high value)
- **Requested by**: Sarah Johnson (PM)
- **Decision by**: October 30, 2025

### For Information Only

**INFO-001: Development Technology Choice**
- **Decision**: Using Next.js 14 with TypeScript (vs React + Vite)
- **Rationale**: Better SEO, server-side rendering, team expertise
- **Impact**: None to timeline or budget
- **Decided by**: Tech Lead, approved by PM
- **Status**: Final, already implemented

---

## Budget Status

**Total Budget**: $150,000
**Spent to Date**: $142,000 (94.7%)
**Remaining**: $8,000 (5.3%)
**Forecast at Completion**: $150,000 (on budget, assuming no additional decisions approved)

**Budget Breakdown**:
| Category | Budgeted | Actual | Variance | % Spent |
|----------|----------|--------|----------|---------|
| Design | $60,000 | $59,500 | -$500 | 99.2% |
| Development | $50,000 | $45,000 | -$5,000 | 90.0% |
| Testing | $15,000 | $12,500 | -$2,500 | 83.3% |
| PM & Admin | $15,000 | $15,000 | $0 | 100% |
| Contingency | $10,000 | $10,000 | $0 | 100% (reserved) |

---

## Team Update

**Current Team**:
- Sarah Johnson (PM) - 100%
- Emily Chen (Design Lead) - Transitioning off (95% → 25%)
- Michael Rodriguez (Tech Lead) - 100%
- 3x Developers - 100%
- 1x QA Engineer - 50% (ramping to 100% in November)

**Morale**: High (8.5/10 in last team survey)
**Velocity**: Increasing (25 → 32 story points)
**Concerns**: None currently

---

## Stakeholder Feedback

Recent stakeholder survey (Oct 24, N=8):
- **Confidence in Delivery**: 8.5/10 (↑ from 7.8 last month)
- **Communication Quality**: 9.2/10
- **Satisfaction with Progress**: 8.8/10
- **Overall Project Health**: 8.7/10

**Key Feedback Themes**:
- ✅ "Great progress on design, very impressed"
- ✅ "Communication is excellent, always know what's happening"
- ⚠️ "Concerned about timeline slip, but trust mitigation plan"

---

## Appendix

### Change Log This Period
- **OCT-15**: Added user testing incentive budget (+$5K pending approval)
- **OCT-20**: Design phase extended 2 days for final polish (within buffer)

### Upcoming Events
- **Weekly Status Meeting**: Every Monday, 2pm
- **Sprint Review**: Every other Friday
- **Executive Steering**: Nov 7, 3pm

---

**Report Prepared by**: Sarah Johnson, Project Manager
**Report Reviewed by**: Michael Rodriguez, Tech Lead
**Next Report Date**: November 9, 2025
**Questions?** Contact: sarah.johnson@company.com

---

*Document Version: 1.0*
*Generated*: October 26, 2025
*Classification*: Internal Use Only
```

## Success Criteria
- Executive summary provides complete picture in 3-4 sentences
- RAG status is honest and accurate (no sugarcoating or hiding issues)
- Metrics show trends (↑↓→) not just current numbers
- Accomplishments are specific and measurable
- Risks have mitigation plans, not just descriptions
- Decisions needed are actionable with clear ask
- Report can be read in 5-10 minutes

## Tips for Best Results

### Input Data Quality
- Provide specific metrics with numbers (not vague "progressing well")
- Include both current and target values for metrics
- List actual accomplishments (deliverables completed, not activities done)
- Identify real risks with probability and impact
- Be specific about what decisions are needed

### RAG Status Guidelines
- **🟢 GREEN**: On track, confidence > 80%, no concerns
- **🟡 AMBER**: At risk, confidence 50-80%, mitigation plan exists
- **🔴 RED**: Off track, confidence < 50%, immediate action required

### Input Example

```json
{
  "project_data": {
    "project_name": "Customer Portal Redesign",
    "project_manager": "Sarah Johnson",
    "executive_sponsor": "John Smith",
    "status": {
      "scope": "green",
      "schedule": "amber",
      "budget": "green",
      "quality": "green"
    },
    "accomplishments": [
      "Final design mockups approved",
      "Development environment set up",
      "User testing round 2 completed (23 sessions)"
    ],
    "metrics": {
      "design_completion": {"current": 95, "target": 100},
      "budget_spent": {"current": 142000, "target": 150000},
      "days_remaining": 94
    },
    "risks": [
      {
        "id": "RISK-001",
        "description": "CRM API documentation delay",
        "severity": "high",
        "mitigation": "Emergency call with vendor scheduled"
      }
    ]
  },
  "reporting_period": {
    "start_date": "2025-10-13",
    "end_date": "2025-10-26",
    "report_date": "2025-10-26"
  }
}
```

## Version History

- **1.0.0** (2025-10-26): Initial release
