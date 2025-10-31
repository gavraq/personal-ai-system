---
name: risk-register-generator
description: Create and maintain comprehensive risk registers with scoring, prioritization, and treatment plans
domain: change-agent
category: risk-management
taxonomy: change-agent/risk-management
parameters:
  - risk_description
  - likelihood
  - impact
output_format: mixed
estimated_duration: 3-5 minutes
tags:
  - risk-management
  - risk-register
  - mitigation
  - risk-assessment
version: 1.0.0
author: Risk Agents Team
---

# Risk Register Generator Skill

## Purpose
Create comprehensive risk register entries with probability/impact scoring, risk priority calculation, treatment strategies, and monitoring plans using industry-standard risk management frameworks.

## When to Use This Skill
- At project initiation to identify initial risks
- During risk assessment workshops
- When new risks are identified during execution
- For monthly/quarterly risk reviews
- When preparing risk reports for stakeholders or governance

## How It Works
This skill transforms risk information into a structured risk register entry with:

1. **Risk Identification**: Clear description of the risk event
2. **Probability & Impact Assessment**: Scoring using 5x5 matrix
3. **Risk Score Calculation**: Priority score (P x I)
4. **Risk Classification**: Category, type, and risk owner
5. **Treatment Strategy**: Avoid, Mitigate, Transfer, or Accept with action plan
6. **Monitoring Plan**: How risk will be tracked over time

**Risk Scoring Framework** (5x5 Matrix):
- **Probability**: 1 (Very Low) to 5 (Very High)
- **Impact**: 1 (Negligible) to 5 (Catastrophic)
- **Risk Score**: Probability × Impact (1-25)
- **Priority**: Low (1-6), Medium (8-12), High (15-20), Critical (25)

## Parameters

### Required Parameters
- **`risk_description`** (string or object): Description of the risk
  - As string: "Budget overrun due to scope creep"
  - As object with details (recommended)

### Recommended Parameters
- **`likelihood`** (number 1-5 or string): Probability of occurrence
- **`impact`** (number 1-5 or string): Impact if it occurs

### Optional Parameters
- **`risk_category`** (string): Type of risk (schedule, budget, technical, resource, external)
- **`risk_owner`** (string): Person responsible for managing this risk
- **`current_controls`** (array): Existing mitigation measures
- **`treatment_strategy`** (string): Preferred approach (avoid, mitigate, transfer, accept)

## Expected Output

Mixed format with Markdown register entry + JSON data:

```markdown
# Risk Register Entry #RISK-015

**Risk ID**: RISK-015
**Date Identified**: October 26, 2025
**Status**: 🔴 ACTIVE - Critical Priority
**Risk Owner**: Sarah Johnson (Project Manager)
**Last Reviewed**: October 26, 2025
**Next Review**: November 9, 2025

---

## Risk Statement

**IF** key technical resources leave the project **THEN** development timeline will slip by 4-6 weeks **RESULTING IN** missed Q1 2026 launch date and $50K revenue loss.

**Category**: Resource Risk
**Sub-Category**: Key Person Dependency
**Phase**: Development (Weeks 8-16)

---

## Risk Assessment

### Probability (Likelihood)
**Score**: 4 / 5 (High - 60-80% chance)

**Indicators**:
- Tech Lead has expressed interest in external opportunities
- Market demand for PostgreSQL developers is very high
- Recent salary survey shows team 15% below market rate
- 2 developers recently interviewed elsewhere (via Linked In activity)

**Probability Justification**:
High probability due to market conditions, below-market compensation, and observed job-seeking behavior.

### Impact
**Score**: 5 / 5 (Catastrophic)

**Impact Dimensions**:
| Dimension | Impact Level | Description |
|-----------|-------------|-------------|
| **Schedule** | Critical (5/5) | 4-6 week delay, misses Q1 launch window |
| **Budget** | Major (4/5) | $75K cost (recruitment, onboarding, productivity loss) |
| **Quality** | Major (4/5) | Knowledge loss, potential defects, technical debt |
| **Scope** | Moderate (3/5) | May need to descope features to meet deadline |
| **Team Morale** | Major (4/5) | Remaining team stress, decreased confidence |
| **Business** | Critical (5/5) | $50K revenue loss, market opportunity missed |

**Overall Impact**: 5 / 5 (Average: 4.2, max dimension: 5)

### Risk Score & Priority

**Risk Score**: **20 / 25** (Probability 4 × Impact 5)

**Priority Matrix Position**:
```
IMPACT
  5 │ M15  H20  H20 🔴H20  C25
  4 │ M12  M12  H16  H16  H20
  3 │ L6   M9   M12  M12  M15
  2 │ L4   L6   M8   M8   M12
  1 │ L2   L4   L6   L6   M10
    └─────────────────────────
      1    2    3    4    5
           PROBABILITY
```

**Classification**: 🔴 **HIGH PRIORITY** (Score 20 - requires immediate action)

---

## Current Risk Response

### Existing Controls (Baseline)
**Control Effectiveness**: Limited - 30%

1. **Documentation**: Technical documentation exists but incomplete (60% coverage)
2. **Knowledge Sharing**: Weekly team sync meetings (basic knowledge transfer)
3. **Cross-Training**: Minimal - each developer owns specific modules
4. **Redundancy**: No backup for Tech Lead role

**Current Controls Assessment**: Insufficient to significantly reduce risk

### Residual Risk
**Without additional treatment**: High probability (4/5) remains, impact slightly reduced to 4/5
**Residual Risk Score**: 16 / 25 (still High Priority)

---

## Risk Treatment Strategy

**Selected Strategy**: **MITIGATE** (Reduce probability AND impact)

**Treatment Plan Overview**:
- **Objective**: Reduce probability from 4 to 2, reduce impact from 5 to 3
- **Target Risk Score**: 6 / 25 (Low Priority)
- **Cost**: $25,000
- **Timeline**: 4 weeks to implement
- **Owner**: Sarah Johnson + HR

### Treatment Actions

#### Action 1: Retention Package (Reduce Probability)
**Objective**: Reduce likelihood of key resources leaving
**Timeline**: Week 1-2
**Cost**: $15,000
**Owner**: HR + Sponsor

**Steps**:
- [ ] Conduct market salary survey (Week 1)
- [ ] Propose 10-15% salary adjustments for key roles (Week 1)
- [ ] Offer retention bonuses ($5K) tied to project completion (Week 2)
- [ ] Create career development plans for top performers (Week 2)

**Expected Outcome**: Reduce probability from 4 (High) to 2 (Low)

#### Action 2: Knowledge Transfer Program (Reduce Impact)
**Objective**: Reduce impact if resource loss occurs
**Timeline**: Week 1-4
**Cost**: $8,000 (100 hours @ $80/hour for documentation time)
**Owner**: Tech Lead + PM

**Steps**:
- [ ] Complete technical documentation to 100% (Week 1-2)
- [ ] Record video walkthroughs of critical components (Week 2-3)
- [ ] Implement pair programming for critical modules (Week 2-4)
- [ ] Cross-train 2 backup developers on each module (Week 3-4)
- [ ] Document tribal knowledge in wiki (Week 1-4)

**Expected Outcome**: Reduce impact from 5 (Catastrophic) to 3 (Moderate)

#### Action 3: Recruitment Contingency (Transfer/Prepare)
**Objective**: Prepare backup plan if loss occurs despite mitigation
**Timeline**: Week 1 (planning only)
**Cost**: $2,000 (recruiter retainer)
**Owner**: HR

**Steps**:
- [ ] Identify recruiting firms specializing in PostgreSQL developers
- [ ] Pre-qualify 3-5 potential contractors for rapid engagement
- [ ] Prepare job descriptions and requirements
- [ ] Negotiate standby agreements with contractors (30-day notice)

**Expected Outcome**: Reduce impact from 5 to 4 (have fallback option ready)

### Treatment Cost-Benefit Analysis

**Treatment Cost**: $25,000
**Risk Cost (if realized)**: $75,000 (recruitment) + $50,000 (revenue loss) = $125,000
**Expected Value**:
- Current: 0.70 probability × $125K = $87,500
- After treatment: 0.30 probability × $45K (reduced impact) = $13,500
- **Net Benefit**: $87,500 - $13,500 - $25,000 = **$49,000 saved**

**ROI**: 196% (benefit $49K / cost $25K)
**Recommendation**: ✅ Implement treatment plan immediately

---

## Alternative Treatment Strategies (Not Selected)

### Option 1: AVOID - Cancel Development Phase
**Description**: Cancel in-house development, outsource to vendor
**Impact**: Eliminates resource risk entirely
**Cost**: $200K+ (outsourcing cost)
**Outcome**: Not selected - too expensive, loses internal capability

### Option 2: TRANSFER - Hire Contractors from Start
**Description**: Replace full-time employees with contractors
**Impact**: Reduces retention risk
**Cost**: $150K (contractor premium over FTE)
**Outcome**: Not selected - higher cost, less team cohesion

### Option 3: ACCEPT - Do Nothing
**Description**: Accept the risk and deal with it if it happens
**Impact**: No upfront cost, full risk exposure
**Cost**: $0 upfront, $125K if realized
**Outcome**: Not selected - expected value $87.5K too high

---

## Monitoring & Review

### Leading Indicators (Early Warning Signals)
Monitor these signals monthly for risk escalation:

1. **LinkedIn Activity**: Team members updating profiles or networking activity ⚠️
2. **Interview Requests**: HR notified of reference checks for team members 🔴
3. **Engagement Scores**: Team satisfaction survey scores declining 🟡
4. **Resignation Letters**: Formal notice given 🔴 (risk realized)
5. **Recruiter Contact**: Team members contacted by recruiters (via informal check-ins) ⚠️

**Thresholds**:
- 🟢 Green: 0-1 warning signals
- 🟡 Amber: 2-3 warning signals (increase monitoring)
- 🔴 Red: 4+ warning signals (escalate immediately)

### Lagging Indicators (Risk Realized)
1. Key resource provides resignation notice
2. Multiple team members leave simultaneously
3. Critical knowledge lost

### Review Schedule
- **Weekly**: Check leading indicators (PM + HR)
- **Bi-weekly**: Risk score reassessment during status meeting
- **Monthly**: Formal risk review with sponsor
- **Trigger-based**: Immediate review if any leading indicator triggers

### Success Metrics (Treatment Effectiveness)
- **Salary Competitiveness**: Team within 5% of market rate by Nov 15
- **Retention Rate**: Zero departures through project completion (Feb 2026)
- **Documentation Coverage**: 100% critical modules documented by Nov 30
- **Cross-Training**: 2+ backup developers per critical module by Nov 30

---

## Escalation & Contingency

### Escalation Triggers
Escalate to Executive Sponsor immediately if:
1. Tech Lead or 2+ senior developers give notice
2. Multiple leading indicators turn 🔴 Red
3. Competing offer received by key resource
4. Treatment actions not reducing risk score within 2 weeks

### Contingency Plan (If Risk Realizes)
**Scenario**: Tech Lead resigns effective 2 weeks from notice

**Immediate Response (Day 1-2)**:
1. Activate pre-qualified contractor (ready within 48 hours)
2. Prioritize knowledge transfer sessions in final 2 weeks
3. Offer counter-offer if appropriate (up to 20% salary increase)

**Short-term Response (Week 1-4)**:
1. Promote senior developer to interim Tech Lead
2. Engage recruiting firm for permanent replacement
3. Reassess project timeline and scope

**Medium-term Response (Month 1-3)**:
1. Hire permanent replacement
2. Complete knowledge transfer to new Tech Lead
3. Adjust project plan if needed

---

## Risk Dependencies & Related Risks

### Dependent Risks (Caused by This Risk)
- **RISK-016**: Project timeline delay (70% probability if RISK-015 realizes)
- **RISK-017**: Budget overrun due to contractor costs (80% probability)
- **RISK-018**: Quality issues from knowledge loss (60% probability)

### Related Risks (Correlation)
- **RISK-012**: Team burnout from tight timeline (may increase probability of RISK-015)
- **RISK-009**: Scope creep (combined with resource loss = critical timeline impact)

---

## Updates Log

| Date | Update | Risk Score | Status |
|------|--------|-----------|--------|
| Oct 26, 2025 | Initial risk identified | 20/25 (High) | Active |
| TBD | Treatment plan implemented | TBD | TBD |
| TBD | Post-treatment reassessment | TBD | TBD |

---

## Appendix: Risk Classification Framework

### Risk Categories
- **Strategic**: Business strategy, market, competition
- **Financial**: Budget, funding, cash flow
- **Operational**: Processes, resources, capacity
- **Technical**: Technology, architecture, integration
- **External**: Regulatory, vendor, natural disasters
- **Organizational**: Culture, change resistance, politics

### Probability Scale (1-5)
| Score | Level | Probability | Description |
|-------|-------|-------------|-------------|
| 5 | Very High | 80-100% | Almost certain to occur |
| 4 | High | 60-80% | Likely to occur |
| 3 | Medium | 40-60% | May occur |
| 2 | Low | 20-40% | Unlikely to occur |
| 1 | Very Low | 0-20% | Rare, almost impossible |

### Impact Scale (1-5)
| Score | Level | Schedule | Budget | Quality |
|-------|-------|----------|--------|---------|
| 5 | Catastrophic | >20% delay | >20% overrun | Unusable |
| 4 | Major | 10-20% delay | 10-20% overrun | Major defects |
| 3 | Moderate | 5-10% delay | 5-10% overrun | Some defects |
| 2 | Minor | <5% delay | <5% overrun | Minor defects |
| 1 | Negligible | No delay | No overrun | No impact |

---

**Document Version**: 1.0
**Created**: October 26, 2025
**Last Updated**: October 26, 2025
**Next Review**: November 9, 2025
**Owner**: Sarah Johnson
```

**Plus JSON Summary**:
```json
{
  "risk_id": "RISK-015",
  "risk_statement": "Key technical resources leaving project",
  "probability": 4,
  "impact": 5,
  "risk_score": 20,
  "priority": "high",
  "category": "resource",
  "owner": "Sarah Johnson",
  "treatment_strategy": "mitigate",
  "treatment_cost": 25000,
  "target_risk_score": 6,
  "status": "active",
  "next_review": "2025-11-09"
}
```

## Success Criteria
- Risk statement follows IF-THEN-RESULTING IN format
- Probability and impact justified with evidence
- Risk score calculated correctly (P × I)
- Treatment strategy selected based on cost-benefit analysis
- Monitoring plan includes leading indicators
- Escalation criteria clearly defined
- Treatment actions are specific and actionable

## Tips for Best Results

### Risk Statement Format
**Good**: "IF key resources leave THEN timeline slips 6 weeks RESULTING IN missed launch and $50K loss"
**Poor**: "We might have resource problems"

### Probability Assessment
Use evidence, not gut feel:
- Look at historical data
- Consider current indicators
- Assess enabling conditions

### Impact Assessment
Consider multiple dimensions:
- Schedule
- Budget
- Quality
- Scope
- Team
- Business value

### Treatment Strategy Selection
- **Avoid**: Eliminate the risk (change plan)
- **Mitigate**: Reduce probability or impact
- **Transfer**: Move risk to third party (insurance, vendor)
- **Accept**: Do nothing, accept the consequences

## Version History

- **1.0.0** (2025-10-26): Initial release
