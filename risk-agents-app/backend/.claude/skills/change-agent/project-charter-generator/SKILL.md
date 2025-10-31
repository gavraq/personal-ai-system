---
name: project-charter-generator
description: Generate comprehensive project charters with objectives, scope, stakeholders, success criteria, and governance structure
domain: change-agent
category: project-management
taxonomy: change-agent/project-management
parameters:
  - project_name
  - project_objectives
  - stakeholders
  - scope
output_format: structured_markdown
estimated_duration: 5-7 minutes
tags:
  - project-charter
  - project-initiation
  - governance
  - scope
version: 1.0.0
author: Risk Agents Team
---

# Project Charter Generator Skill

## Purpose
Generate a professional, comprehensive project charter document that formally authorizes a project and provides the project manager with authority to apply resources to project activities.

## When to Use This Skill
- At project initiation to formally authorize the project
- When defining project scope and objectives
- When establishing project governance structure
- When securing stakeholder buy-in and approval
- When documenting constraints, assumptions, and risks

## How It Works
This skill transforms basic project information into a complete project charter including:

1. **Executive Summary**: High-level project overview and business case
2. **Objectives & Success Criteria**: Clear, measurable goals with SMART criteria
3. **Scope**: In-scope items, out-of-scope items, constraints, and assumptions
4. **Stakeholders**: Key stakeholders with roles, responsibilities, and influence levels
5. **Governance**: Decision-making structure, escalation paths, and approval authority
6. **Risks & Issues**: Initial risk assessment and mitigation strategies
7. **Timeline & Milestones**: High-level project phases and key dates
8. **Budget & Resources**: Resource requirements and budget allocation

## Parameters

### Required Parameters
- **`project_name`** (string): Name of the project
- **`project_objectives`** (string or array): Primary objectives and goals of the project

### Recommended Parameters
- **`stakeholders`** (array): List of key stakeholders with their roles
- **`scope`** (object): Scope definition including in-scope and out-of-scope items
  - `in_scope` (array): Items within project scope
  - `out_of_scope` (array): Items explicitly outside scope
  - `constraints` (array): Project constraints (budget, timeline, resources)
  - `assumptions` (array): Key assumptions being made

### Optional Parameters
- **`timeline`** (object): Project timeline information
  - `start_date` (date): Project start date
  - `target_completion` (date): Target completion date
  - `key_milestones` (array): Major milestones
- **`budget`** (object): Budget information
  - `total_budget` (number): Total project budget
  - `currency` (string): Currency code (USD, GBP, EUR, etc.)
- **`background`** (string): Project background and business case
- **`success_metrics`** (array): How success will be measured

## Resources

- `resources/charter-template.md` - Standard project charter structure
- `resources/examples.md` - Example charters for different project types

## Expected Output

A comprehensive project charter document in structured Markdown format:

```markdown
# Project Charter: Website Redesign

**Project Manager**: Sarah Johnson
**Sponsor**: John Smith, VP of Marketing
**Charter Date**: 2025-10-26
**Last Updated**: 2025-10-26

---

## Executive Summary

The Website Redesign project aims to modernize our company website to improve user experience, increase conversion rates, and better represent our brand in the marketplace. The current website, built in 2019, no longer meets user expectations for mobile experience and lacks the modern functionality needed to support our growing product portfolio.

**Business Case**: Improving website user experience is expected to increase conversion rates by 25%, reduce bounce rates by 30%, and improve customer satisfaction scores. The investment of $150,000 over 4 months will generate an estimated ROI of 200% in the first year through increased sales and reduced support costs.

---

## Project Objectives

### Primary Objectives
1. **User Experience**: Redesign website with mobile-first approach to improve usability scores by 40%
2. **Performance**: Reduce page load time to under 2 seconds (currently 5-7 seconds)
3. **Conversion**: Increase contact form conversions by 25% within 3 months of launch
4. **Brand Alignment**: Update visual design to reflect new brand guidelines approved in Q2 2025

### Success Criteria (SMART)
- **Specific**: New website with responsive design, under 2-second load time, 25% conversion increase
- **Measurable**: User satisfaction score > 4.5/5, bounce rate < 40%, conversion rate increase 25%+
- **Achievable**: Based on industry benchmarks and our current baseline metrics
- **Relevant**: Directly supports company growth objectives and digital transformation strategy
- **Time-bound**: Launch by February 28, 2026; measure success metrics by May 31, 2026

---

## Scope

### In Scope
- Complete website redesign (front-end only)
- Mobile-responsive design for all pages
- Integration with existing CRM system
- SEO optimization
- Content migration from old site
- User testing with 50+ participants
- 1 month of post-launch support

### Out of Scope
- Backend system changes (API remains unchanged)
- CRM system modifications
- Mobile app development
- Content creation (client provides all content)
- Ongoing website maintenance beyond 1-month support period

### Constraints
- **Budget**: $150,000 total (firm cap)
- **Timeline**: Must launch by February 28, 2026 (market window)
- **Resources**: Limited to internal team + 1 external design agency
- **Technology**: Must use current tech stack (React, Next.js, existing CMS)

### Assumptions
- Client will provide all content by December 15, 2025
- Current hosting infrastructure can support new site
- Brand guidelines are finalized and won't change mid-project
- Key stakeholders available for weekly reviews

---

## Stakeholders

| Name | Role | Responsibility | Interest | Influence | Communication Frequency |
|------|------|----------------|----------|-----------|------------------------|
| John Smith | Executive Sponsor | Final approval, budget owner | High | High | Bi-weekly status |
| Sarah Johnson | Project Manager | Day-to-day management, delivery | High | Medium | Daily |
| Emily Chen | Design Lead | UX/UI design, user testing | High | Medium | Daily |
| Michael Rodriguez | Tech Lead | Technical implementation | High | Medium | Daily |
| Lisa Wang | Marketing Director | Content strategy, SEO | High | Medium | Weekly |
| David Kim | Legal | Compliance review | Medium | Low | As needed |
| External Users | End Users | Website usage, feedback | High | Low | Testing sessions |

---

## Governance Structure

### Decision-Making Authority
- **Strategic Decisions** (>$10K, scope changes): Executive Sponsor approval required
- **Tactical Decisions** (design, technical): Project Manager + relevant lead (Design/Tech)
- **Operational Decisions** (daily execution): Team members within their domain

### Escalation Path
1. Team Member → Project Manager (0-24 hours)
2. Project Manager → Executive Sponsor (24-48 hours)
3. Executive Sponsor → Steering Committee (48-72 hours)

### Change Control Process
1. Change request submitted to Project Manager
2. Impact assessment (scope, budget, timeline)
3. Recommendation to Executive Sponsor
4. Sponsor approval/rejection
5. Update project plan and communicate to team

### Meeting Cadence
- **Daily Standups**: 15 minutes, core team
- **Weekly Status**: 1 hour, all stakeholders
- **Bi-weekly Sponsor Review**: 30 minutes, PM + Sponsor
- **Monthly Steering Committee**: 1 hour, executive stakeholders

---

## Timeline & Milestones

### Project Phases

**Phase 1: Discovery & Planning** (Nov 2025)
- Stakeholder interviews
- User research and personas
- Technical architecture design
- Project plan finalization

**Phase 2: Design** (Dec 2025 - Jan 2026)
- Wireframes and mockups
- User testing (2 rounds)
- Final design approval

**Phase 3: Development** (Jan - Feb 2026)
- Front-end development
- CRM integration
- Content migration
- QA testing

**Phase 4: Launch & Support** (Feb - Mar 2026)
- Soft launch (beta users)
- Full public launch
- Post-launch monitoring
- 1 month support period

### Key Milestones
| Milestone | Target Date | Owner |
|-----------|-------------|-------|
| Project Kickoff | November 1, 2025 | Sarah Johnson |
| Design Approval | December 20, 2025 | Emily Chen |
| Development Complete | February 15, 2026 | Michael Rodriguez |
| User Acceptance Testing | February 22, 2026 | Sarah Johnson |
| Public Launch | February 28, 2026 | John Smith |
| Success Metrics Review | May 31, 2026 | Sarah Johnson |

---

## Budget & Resources

### Budget Allocation
| Category | Amount | Percentage |
|----------|--------|------------|
| Design Agency | $60,000 | 40% |
| Development (Internal) | $50,000 | 33% |
| User Testing & Research | $15,000 | 10% |
| Project Management | $15,000 | 10% |
| Contingency (10%) | $10,000 | 7% |
| **Total** | **$150,000** | **100%** |

### Resource Requirements
- **Project Manager**: 100% allocation (4 months)
- **Design Lead**: 75% allocation (2 months)
- **Tech Lead**: 75% allocation (2 months)
- **Developers**: 3 FTE (2 months)
- **QA Tester**: 50% allocation (1 month)
- **External Design Agency**: Full engagement (2 months)

---

## Risks & Mitigation

| Risk | Probability | Impact | Mitigation Strategy | Owner |
|------|------------|---------|---------------------|-------|
| Content delays from client | High | High | Buffer 2 weeks, start with placeholder content | Sarah Johnson |
| Design approval delays | Medium | High | Weekly stakeholder reviews, early alignment | Emily Chen |
| Technical complexity underestimated | Medium | Medium | Technical spike in Phase 1, experienced dev team | Michael Rodriguez |
| Key resource unavailability | Low | High | Cross-train team members, identify backup resources | Sarah Johnson |
| Scope creep | High | High | Strict change control process, regular scope reviews | Sarah Johnson |
| Browser compatibility issues | Medium | Medium | Test across browsers throughout development | QA Team |

---

## Success Metrics

### Quantitative Metrics
- **User Satisfaction**: Score > 4.5/5 (current: 3.2/5)
- **Page Load Time**: < 2 seconds (current: 5-7 seconds)
- **Bounce Rate**: < 40% (current: 58%)
- **Mobile Traffic**: > 60% (current: 45%)
- **Conversion Rate**: 25% increase (baseline: 2.5% → target: 3.1%)
- **SEO Rankings**: Top 3 for 10 key search terms (current: Top 10)

### Qualitative Metrics
- Stakeholder satisfaction with delivery process
- Team morale and collaboration effectiveness
- Quality of design and brand alignment
- Technical architecture sustainability

### Measurement Plan
- **Baseline**: Capture all metrics before launch (February 2026)
- **Monitoring**: Daily metrics tracking for first month post-launch
- **Review**: Formal success review at 1 month (March) and 3 months (May)
- **Reporting**: Weekly metric reports to stakeholders

---

## Approval & Sign-Off

This project charter has been reviewed and approved by the following stakeholders:

| Name | Role | Signature | Date |
|------|------|-----------|------|
| John Smith | Executive Sponsor | ___________________ | _________ |
| Sarah Johnson | Project Manager | ___________________ | _________ |
| Emily Chen | Design Lead | ___________________ | _________ |
| Michael Rodriguez | Tech Lead | ___________________ | _________ |

---

**Document Version**: 1.0
**Last Updated**: October 26, 2025
**Next Review**: December 1, 2025
```

## Success Criteria
- Charter is comprehensive and covers all standard sections
- Objectives are SMART (Specific, Measurable, Achievable, Relevant, Time-bound)
- Stakeholders are clearly identified with roles and influence levels
- Scope is well-defined with clear in/out boundaries
- Governance structure provides clear decision-making framework
- Risks are identified with mitigation strategies
- Success metrics are measurable and baseline established

## Tips for Best Results

### For Better Charters
- Provide clear, specific objectives rather than vague goals
- Include known constraints upfront (budget, timeline, resources)
- List all key stakeholders with their actual roles
- Be honest about assumptions and risks
- Define success metrics that can actually be measured

### Input Recommendations
- **Minimum Input**: Project name + 2-3 objectives → Get basic charter
- **Recommended Input**: Name + objectives + stakeholders + scope → Get comprehensive charter
- **Optimal Input**: All parameters including timeline, budget, risks → Get production-ready charter

## Version History

- **1.0.0** (2025-10-26): Initial release
