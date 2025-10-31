---
name: communication-plan-generator
description: Develop comprehensive stakeholder communication plans with channels, frequency, messaging, and success metrics
domain: change-agent
category: communication-management
taxonomy: change-agent/communication-management
parameters:
  - stakeholders
  - project_context
output_format: structured_markdown
estimated_duration: 4-6 minutes
tags:
  - communication
  - stakeholder-engagement
  - messaging
  - change-management
version: 1.0.0
author: Risk Agents Team
---

# Communication Plan Generator Skill

## Purpose
Generate comprehensive communication plans tailored to stakeholder needs with appropriate channels, frequency, messaging strategies, and success metrics for effective project communication.

## When to Use This Skill
- At project kickoff to establish communication framework
- During change management initiatives
- When stakeholder communication issues arise
- For crisis communication planning
- When onboarding new stakeholders mid-project

## How It Works
This skill creates a structured communication plan with:

1. **Stakeholder Analysis**: Communication needs per stakeholder group
2. **Channel Strategy**: Optimal communication channels for each audience
3. **Frequency Planning**: How often each stakeholder should be contacted
4. **Message Mapping**: Key messages tailored to each audience
5. **Calendar**: Communication schedule with specific events
6. **Metrics**: How to measure communication effectiveness
7. **Escalation Paths**: When and how to escalate issues

## Parameters

### Required Parameters
- **`stakeholders`** (array): List of stakeholders (strings or objects)

### Recommended Parameters
- **`project_context`** (object): Project information
  - `project_name` (string): Name of project
  - `project_phase` (string): Current phase (planning, execution, etc.)
  - `key_milestones` (array): Upcoming milestones
  - `known_concerns` (array): Stakeholder concerns to address

### Optional Parameters
- **`communication_objectives`** (array): Specific communication goals
- **`constraints`** (object): Budget, time, channel limitations

## Expected Output

Structured Markdown communication plan:

```markdown
# Communication Plan: Customer Portal Redesign

**Project**: Customer Portal Redesign
**Project Manager**: Sarah Johnson
**Plan Version**: 1.0
**Effective Date**: November 1, 2025
**Review Frequency**: Monthly

---

## Communication Objectives

### Primary Objectives
1. **Alignment**: Ensure all stakeholders understand project goals, status, and their role
2. **Transparency**: Provide regular, honest updates on progress, risks, and issues
3. **Engagement**: Build and maintain stakeholder support and enthusiasm
4. **Coordination**: Enable effective collaboration across teams and stakeholders
5. **Risk Management**: Identify and address concerns before they become blockers

### Success Criteria
- **Stakeholder Satisfaction**: > 8/10 on quarterly communication survey
- **Engagement Rate**: > 80% attendance at key stakeholder meetings
- **Response Time**: < 24 hours for critical stakeholder inquiries
- **Awareness**: 100% of stakeholders aware of project status and next milestones

---

## Stakeholder Communication Matrix

| Stakeholder | Interest | Power | Communication Needs | Frequency | Primary Channel | Secondary Channel |
|-------------|----------|-------|---------------------|-----------|-----------------|-------------------|
| **Executive Sponsor** (John Smith) | High | High | Strategic updates, decisions needed, risks | Weekly | 1:1 Meeting | Email Summary |
| **Project Team** (6 members) | High | Medium | Detailed progress, tasks, blockers | Daily | Standup + Slack | Email |
| **Steering Committee** (5 execs) | Medium | High | Executive summary, milestones, budget | Monthly | Meeting | Report |
| **End Users** (500+) | High | Low | Feature updates, training, launch date | Milestone-based | Email | User Portal |
| **IT Operations** | Medium | Medium | Technical changes, deployment schedule | Bi-weekly | Meeting | Email |
| **Finance** | Low | High | Budget status, forecast, approvals | Monthly | Email | Dashboard |
| **Legal/Compliance** | Low | Medium | Compliance updates, risk items | As-needed | Email | Meeting |

---

## Communication Channels Strategy

### Channel Selection Guide

| Channel | Best For | Frequency | Audience Size | Formality |
|---------|----------|-----------|---------------|-----------|
| **1:1 Meeting** | Strategic discussions, decisions, sensitive topics | Weekly-Monthly | 1-2 people | Formal |
| **Team Meeting** | Collaboration, problem-solving, alignment | Daily-Weekly | 3-15 people | Semi-formal |
| **Email** | Status updates, documentation, announcements | Daily-Weekly | Any size | Formal |
| **Slack/Teams** | Quick questions, informal updates, coordination | Real-time | Any size | Informal |
| **Dashboard** | Self-service metrics, real-time status | Continuous | Any size | Formal |
| **Newsletter** | Broader updates, achievements, upcoming events | Weekly-Monthly | 50+ people | Semi-formal |
| **Town Hall** | Major announcements, Q&A, team building | Quarterly | 20+ people | Formal |

### Channel Usage Matrix

**Synchronous Channels** (Real-time):
- 1:1 Meetings: Executive Sponsor (weekly), key decision makers
- Team Meetings: Daily standup (15 min), weekly planning (1 hour)
- Slack/Teams: Team coordination, quick questions
- Town Halls: Quarterly all-hands (1 hour)

**Asynchronous Channels** (Time-shifted):
- Email: Status reports, formal announcements, documentation
- Dashboard: Real-time project metrics, KPIs
- Wiki/Confluence: Project documentation, meeting notes
- Newsletter: Weekly project highlights

---

## Communication Schedule

### Daily Communications

**Daily Standup** (Team)
- **Time**: 9:00 AM, 15 minutes
- **Participants**: Project team (6 people)
- **Format**: In-person/video call
- **Agenda**: Yesterday's progress, today's plan, blockers
- **Owner**: Project Manager
- **Documentation**: Notes in Slack, blockers tracked

### Weekly Communications

**Executive Sponsor 1:1** (Monday 2pm, 30 min)
- **Participants**: PM + Executive Sponsor
- **Format**: 1:1 meeting
- **Agenda**:
  - Project health (RAG status)
  - Key accomplishments this week
  - Decisions needed
  - Risks and issues
  - Budget status
- **Preparation**: Send pre-read email 24 hours before
- **Follow-up**: Email summary with action items within 4 hours

**Team Planning Meeting** (Friday 10am, 1 hour)
- **Participants**: Full project team
- **Format**: Working session
- **Agenda**:
  - Review week's accomplishments
  - Plan next week's work
  - Address blockers
  - Risk review
- **Documentation**: Meeting notes in Confluence

**Stakeholder Email Update** (Friday 4pm)
- **Recipients**: All stakeholders (30 people)
- **Format**: Email (< 500 words)
- **Content**:
  - **Status**: RAG indicators (Scope, Schedule, Budget, Quality)
  - **This Week**: Top 3 accomplishments
  - **Next Week**: Top 3 priorities
  - **Help Needed**: Specific asks or blockers
  - **Upcoming**: Next milestone date

### Bi-Weekly Communications

**IT Operations Sync** (Every other Wednesday 3pm, 30 min)
- **Participants**: PM, Tech Lead, Ops Team
- **Format**: Video call
- **Focus**: Technical changes, deployment planning, infrastructure needs

### Monthly Communications

**Steering Committee Meeting** (First Thursday, 1 hour)
- **Participants**: Executive Sponsor, PM, Committee (5 execs)
- **Format**: Formal presentation + Q&A
- **Materials**:
  - Executive dashboard (pre-distributed)
  - Status report (detailed)
  - Decision papers for approvals
- **Agenda**:
  - 10 min: Executive summary presentation
  - 20 min: Deep dive on key issues/risks
  - 20 min: Decisions and approvals
  - 10 min: Q&A

**Finance Review** (Last Friday, email)
- **Recipients**: Finance team
- **Format**: Budget dashboard + commentary
- **Content**:
  - Budget vs. actual
  - Forecast to completion
  - Variance explanations
  - Upcoming expenses

**All-Hands Project Update** (Monthly, 30 min optional)
- **Participants**: Open to all interested stakeholders
- **Format**: Virtual town hall
- **Content**:
  - Demo of latest features
  - Upcoming milestones
  - Q&A session

---

## Message Mapping by Stakeholder

### Executive Sponsor
**Communication Style**: Strategic, concise, decision-focused
**Key Messages**:
- "Project is on track for Q1 2026 launch" (status)
- "We need your approval on $5K additional budget for user testing" (decision)
- "Risk: Resource retention - mitigation plan in place" (transparency)

**What They Care About**:
- ROI and business value
- Timeline adherence
- Major risks
- Strategic alignment

**Communication Dos**:
✅ Lead with status (Green/Amber/Red)
✅ Be concise - respect their time
✅ Come prepared with recommendations
✅ Escalate early, not late

**Communication Don'ts**:
❌ Surprise them with bad news
❌ Present problems without solutions
❌ Get lost in technical details
❌ Waste time on low-priority items

---

### Project Team
**Communication Style**: Collaborative, detailed, tactical
**Key Messages**:
- "Sprint 2 complete - 32 story points delivered" (achievement)
- "Next sprint focus: CRM integration + user testing prep" (clarity)
- "Blocker: API docs delayed, workaround in progress" (transparency)

**What They Care About**:
- Clear priorities and tasks
- Removing blockers quickly
- Recognition for achievements
- Technical challenges and solutions

**Communication Dos**:
✅ Be specific about tasks and deadlines
✅ Recognize contributions publicly
✅ Address blockers immediately
✅ Provide context for decisions

**Communication Don'ts**:
❌ Micromanage
❌ Change priorities without explanation
❌ Ignore technical concerns
❌ Miss daily standups

---

### End Users
**Communication Style**: Simple, benefit-focused, reassuring
**Key Messages**:
- "New website launching Feb 28 - faster, easier to use" (benefit)
- "You'll be invited to test the beta in January" (involvement)
- "Training sessions scheduled for February - optional" (support)

**What They Care About**:
- How it affects them personally
- When changes happen
- How to get help
- What's in it for them

**Communication Dos**:
✅ Explain benefits in simple terms
✅ Give advance notice of changes
✅ Provide training and support
✅ Listen to feedback

**Communication Don'ts**:
❌ Use technical jargon
❌ Surprise them with changes
❌ Ignore their concerns
❌ Over-communicate low-impact items

---

## Communication Templates

### Weekly Status Email Template

```
Subject: [Project Name] - Weekly Update - [Date]

**Overall Status**: 🟢 Green / 🟡 Amber / 🔴 Red

**This Week's Wins**:
1. [Achievement 1]
2. [Achievement 2]
3. [Achievement 3]

**Next Week's Focus**:
1. [Priority 1]
2. [Priority 2]
3. [Priority 3]

**Help Needed**:
- [Specific ask or blocker - or "None"]

**Upcoming Milestone**:
- [Next milestone name] - [Date]

**Key Metrics**:
- Budget: $X spent of $Y (Z%)
- Timeline: X days remaining
- Team: [Any team changes]

**Detailed Status**:
- Scope: 🟢 [One sentence]
- Schedule: 🟡 [One sentence]
- Budget: 🟢 [One sentence]
- Quality: 🟢 [One sentence]

Questions? Reply to this email or ping me on Slack.

[Your name]
```

### Escalation Email Template

```
Subject: ESCALATION: [Issue] - Action Needed

**Issue**: [Clear statement of problem]

**Impact**: [Who/what is affected and how]

**Urgency**: [Why this needs immediate attention]

**Tried So Far**:
1. [Action 1 - outcome]
2. [Action 2 - outcome]

**Request**: [Specific action you need from recipient]

**Timeline**: [By when this needs to be resolved]

**Next Steps if No Response**: [Escalation path]
```

---

## Escalation Procedures

### Issue Severity Levels

| Level | Response Time | Escalation Path | Examples |
|-------|---------------|-----------------|----------|
| **P1 - Critical** | 2 hours | PM → Sponsor → Steering | Production outage, data loss, security breach |
| **P2 - High** | 8 hours | PM → Sponsor | Major milestone at risk, key resource loss |
| **P3 - Medium** | 24 hours | PM handles | Minor delays, resource conflicts |
| **P4 - Low** | 48 hours | Team handles | Questions, clarifications |

### Escalation Process
1. **Attempt Resolution**: Try to resolve at lowest level first
2. **Document**: Write clear escalation with impact and urgency
3. **Notify Next Level**: Follow escalation path
4. **Set Deadline**: Give response time based on severity
5. **Follow Up**: Track until resolved

---

## Communication Metrics & Monitoring

### Key Performance Indicators

**Engagement Metrics**:
- Meeting attendance rate: Target 90%+
- Email open rate: Target 80%+
- Survey response rate: Target 70%+

**Effectiveness Metrics**:
- Stakeholder satisfaction score: Target 8+/10
- Issue resolution time: Target <24 hours
- Decision turnaround: Target <48 hours

**Output Metrics**:
- Weekly status reports: 100% on-time
- Meeting notes published: Within 24 hours
- Dashboard updates: Real-time

### Monthly Communication Review

Review these questions monthly:
1. Are stakeholders satisfied with communication?
2. Are key messages reaching target audiences?
3. Are meetings effective (attendance, outcomes)?
4. Are issues being escalated appropriately?
5. What communication gaps exist?

---

## Crisis Communication Plan

**Crisis Triggers**:
- Major project failure or setback
- Security breach or data loss
- Key stakeholder opposition
- Budget overrun > 20%
- Timeline delay > 4 weeks

**Crisis Response**:
1. **Immediate** (0-2 hours):
   - Notify Executive Sponsor
   - Assess situation
   - Prepare holding statement

2. **Short-term** (2-24 hours):
   - Notify all stakeholders
   - Schedule emergency meeting
   - Develop action plan

3. **Ongoing**:
   - Daily updates until resolved
   - Transparent communication
   - Post-mortem after resolution

---

## Communication Plan Governance

### Plan Owner
- **Primary**: Sarah Johnson (Project Manager)
- **Backup**: Michael Rodriguez (Tech Lead)

### Review Schedule
- **Monthly**: Assess effectiveness, adjust as needed
- **Quarterly**: Stakeholder survey
- **Post-Milestone**: Lessons learned

### Change Control
Changes to this plan require:
- PM approval (minor changes: frequency, channels)
- Sponsor approval (major changes: adding stakeholders, escalation paths)

---

**Document Version**: 1.0
**Created**: October 26, 2025
**Last Updated**: October 26, 2025
**Next Review**: November 26, 2025
**Owner**: Sarah Johnson (PM)
```

## Success Criteria
- All stakeholders identified with communication needs assessed
- Appropriate channels selected for each audience
- Communication frequency balances information needs vs. overload
- Messages tailored to stakeholder interests and communication styles
- Schedule is realistic and sustainable
- Metrics defined to measure effectiveness
- Escalation procedures clear and actionable

## Tips for Best Results

### Better Communication Plans
- Segment stakeholders by communication needs, not just hierarchy
- Use multiple channels (email + meeting) for important messages
- Schedule regular check-ins, don't wait for problems
- Tailor messages: executives want "so what", teams want "how"

### Common Pitfalls to Avoid
- ❌ One-size-fits-all communication
- ❌ Over-communicating to some, under-communicating to others
- ❌ Using wrong channel (Slack for formal decisions)
- ❌ No feedback mechanism
- ❌ Communication plan created but not followed

## Version History

- **1.0.0** (2025-10-26): Initial release
