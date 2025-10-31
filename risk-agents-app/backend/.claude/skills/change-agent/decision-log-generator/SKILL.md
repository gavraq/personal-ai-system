---
name: decision-log-generator
description: Document and track project decisions with context, rationale, alternatives considered, and impacts
domain: change-agent
category: decision-management
taxonomy: change-agent/decision-management
parameters:
  - decision_text
  - context
output_format: structured_markdown
estimated_duration: 2-4 minutes
tags:
  - decisions
  - decision-log
  - documentation
  - governance
version: 1.0.0
author: Risk Agents Team
---

# Decision Log Generator Skill

## Purpose
Create structured decision log entries that capture critical decisions with full context, rationale, alternatives considered, stakeholder input, and expected impacts for future reference and accountability.

## When to Use This Skill
- After making key project or technical decisions
- When documenting architectural or design choices
- For governance and audit trail requirements
- When decisions need stakeholder approval or sign-off
- To prevent "decision amnesia" on long-running projects

## How It Works
This skill transforms decision information into a well-structured decision log entry with:

1. **Decision Statement**: Clear, concise statement of what was decided
2. **Context**: Situation that led to the decision being needed
3. **Alternatives Considered**: Other options that were evaluated
4. **Rationale**: Why this decision was made (pros/cons analysis)
5. **Impact Analysis**: Who/what is affected and how
6. **Implementation**: Next steps and responsible parties
7. **Review Criteria**: When/how this decision should be revisited

## Parameters

### Required Parameters
- **`decision_text`** (string): The decision that was made

### Recommended Parameters
- **`context`** (object or string): Background information
  - `situation` (string): What prompted this decision
  - `constraints` (array): Known constraints or limitations
  - `stakeholders` (array): Who was involved or affected

### Optional Parameters
- **`alternatives`** (array): Other options that were considered
- **`approval_required`** (boolean): Whether this needs formal approval
- **`decision_maker`** (string): Person/role who made the decision
- **`decision_date`** (date): When decision was made

## Expected Output

Structured Markdown decision log entry:

```markdown
# Decision Log Entry #DEC-042

**Decision ID**: DEC-042
**Decision Date**: October 26, 2025
**Decision Maker**: Sarah Johnson (Project Manager)
**Status**: ✅ Approved
**Review Date**: January 26, 2026 (3 months)

---

## Decision Statement

**We will migrate the application to use PostgreSQL instead of MySQL for the database layer.**

**Category**: Technical Architecture
**Scope**: System-wide
**Reversibility**: Difficult (2-3 months effort to reverse)

---

## Context & Background

### Situation
Our current MySQL database is experiencing performance issues at scale:
- Query response times degraded 300% over 6 months as data grew
- Limited support for advanced JSON querying needed for new features
- Horizontal scaling challenges with current architecture
- Team expertise shifting toward PostgreSQL on other projects

### Constraints
- Must complete migration before Q1 2026 launch (3 months)
- Cannot afford significant downtime (max 4 hours acceptable)
- Budget: $30K available for migration work
- Current team has 2 PostgreSQL experts, 4 MySQL experts

### Stakeholders Involved
- **Sarah Johnson** (PM) - Decision maker
- **Michael Rodriguez** (Tech Lead) - Technical recommendation
- **John Smith** (Sponsor) - Budget approval
- **Dev Team** (6 members) - Implementation
- **Operations Team** - Infrastructure support

---

## Alternatives Considered

### Option 1: Stay with MySQL + Optimization
**Pros**:
- No migration cost or risk
- Team already expert in MySQL
- Familiar tooling and processes

**Cons**:
- Only addresses symptoms, not root cause
- Performance gains limited (20-30% max)
- Doesn't enable new features (JSON querying)
- Technical debt increases

**Outcome**: Rejected - doesn't solve long-term scaling needs

---

### Option 2: Migrate to PostgreSQL (SELECTED)
**Pros**:
- Superior JSON support (required for new features)
- Better query optimization and performance (2-5x faster for our use cases)
- Horizontal scaling easier with extensions
- Industry trend - easier to hire talent
- Team gaining PostgreSQL experience on other projects

**Cons**:
- Migration effort: 4-6 weeks, 2-3 engineers
- Risk of data loss/corruption during migration
- 4-hour downtime required
- Team retraining needed (estimated 2 weeks ramp-up)

**Outcome**: Selected - best long-term solution despite short-term cost

---

### Option 3: Cloud-Native Database (AWS Aurora)
**Pros**:
- Fully managed service (reduced ops burden)
- Automatic scaling and high availability
- Compatible with PostgreSQL syntax

**Cons**:
- 40% higher ongoing cost ($5K/month vs $3K/month)
- Vendor lock-in to AWS
- Less team control over configuration
- Migration complexity similar to Option 2

**Outcome**: Rejected - cost not justified for current scale

---

## Decision Rationale

**Why PostgreSQL over MySQL**:
1. **Performance**: Benchmarks show 3x improvement for complex queries
2. **Features**: Native JSON support critical for upcoming mobile app integration
3. **Scalability**: Better partitioning and sharding options for future growth
4. **Team Alignment**: 2 team members already PostgreSQL experts, others eager to learn
5. **Industry Momentum**: PostgreSQL is preferred for modern applications, easier hiring

**Why Not Cloud-Native**:
- Current scale doesn't justify 40% cost increase
- Can migrate to Aurora later if needed (PostgreSQL compatibility)
- Team values control over infrastructure at this stage

**Risk Acceptance**:
- Accepting 4-hour downtime during migration (scheduled for Sunday 2am)
- Accepting 2-week team productivity dip during ramp-up
- Mitigated by thorough testing and rollback plan

---

## Impact Analysis

### Technical Impact
- **Systems Affected**:
  - Primary application database
  - 3 microservices (user service, order service, inventory service)
  - Reporting dashboard
  - Data warehouse ETL pipeline

- **Breaking Changes**:
  - MySQL-specific SQL syntax needs updating (~150 queries)
  - Stored procedures need rewriting (12 procedures)
  - ORM configurations require updates

- **Performance Impact**:
  - Expected 3x improvement in query performance
  - 50% reduction in database server load
  - Better support for concurrent connections

### Business Impact
- **Timeline**: 6-week migration project (Dec 2025 - Jan 2026)
- **Budget**: $25,000 (within $30K allocation)
  - 400 hours engineering time @ $50/hour = $20K
  - 40 hours DBA consulting @ $150/hour = $6K
  - Infrastructure costs = $2K
  - Contingency = $2K

- **Risks Mitigated**:
  - Eliminates performance degradation risk before Q1 launch
  - Enables mobile app features that require JSON querying
  - Improves system reliability and reduces incidents

### Team Impact
- **Workload**: 2-3 engineers dedicated for 6 weeks
- **Training**: All 6 engineers need PostgreSQL fundamentals (2 weeks)
- **Morale**: Positive - team excited to work with modern tech
- **Hiring**: Easier to recruit with PostgreSQL (more candidates available)

### Customer Impact
- **Downtime**: 4 hours during migration (Sunday 2am - 6am, low traffic)
- **Performance**: Noticeable improvement post-migration
- **Features**: Enables faster release of mobile app (customer-requested)
- **Risk**: Data loss during migration (mitigated with backup/rollback plan)

---

## Implementation Plan

### Phase 1: Preparation (Weeks 1-2)
- [ ] Set up PostgreSQL staging environment
- [ ] Audit all MySQL-specific code
- [ ] Rewrite stored procedures
- [ ] Update ORM configurations
- [ ] Create migration scripts

**Owner**: Michael Rodriguez (Tech Lead)
**Deadline**: December 8, 2025

### Phase 2: Testing (Weeks 3-4)
- [ ] Migrate copy of production data to PostgreSQL staging
- [ ] Run full test suite
- [ ] Performance testing and benchmarking
- [ ] Load testing with production-like traffic
- [ ] Train team on PostgreSQL administration

**Owner**: QA Team + Tech Lead
**Deadline**: December 22, 2025

### Phase 3: Migration (Week 5)
- [ ] Final data sync from MySQL to PostgreSQL
- [ ] Schedule maintenance window (Sunday Jan 5, 2am-6am)
- [ ] Execute migration with live monitoring
- [ ] Verify data integrity
- [ ] Rollback plan ready if issues arise

**Owner**: Operations + Tech Lead
**Deadline**: January 5, 2026

### Phase 4: Post-Migration (Week 6)
- [ ] Monitor performance for 1 week
- [ ] Address any issues or bugs
- [ ] Decommission MySQL database
- [ ] Update documentation
- [ ] Team retrospective

**Owner**: Full Team
**Deadline**: January 12, 2026

---

## Success Criteria

### Functional Success
- ✅ All data migrated without loss (100% data integrity verified)
- ✅ All application features working post-migration
- ✅ Test suite passes at 100%
- ✅ No critical bugs introduced by migration

### Performance Success
- ✅ Query response times improved by 2x minimum (target: 3x)
- ✅ Database CPU utilization reduced by 30%+
- ✅ Support for 2x concurrent connections without degradation

### Business Success
- ✅ Migration completed within 6-week timeline
- ✅ Budget: $25K or less
- ✅ Downtime: 4 hours or less
- ✅ Zero customer data loss

### Team Success
- ✅ All 6 engineers proficient in basic PostgreSQL (2-week training)
- ✅ Operations team comfortable with PostgreSQL admin
- ✅ Documentation updated and comprehensive

---

## Rollback Plan

**If Critical Issues Arise**:
1. **Immediate (0-1 hour)**: Switch application back to MySQL
2. **Data Sync**: Sync any changes made during migration window back to MySQL
3. **Verification**: Test application functionality on MySQL
4. **Communication**: Notify stakeholders of rollback and revised timeline

**Rollback Triggers**:
- Data integrity verification fails (> 0.01% discrepancy)
- Critical functionality broken post-migration
- Performance worse than MySQL (unlikely but possible)
- Downtime exceeds 6 hours

**Rollback Time**: 30 minutes maximum

---

## Review & Monitoring

### Review Schedule
- **1 Week Post-Migration**: Performance review, issue triage
- **1 Month Post-Migration**: Success criteria assessment, lessons learned
- **3 Months Post-Migration**: Formal decision review (reassess if needed)

### Monitoring Metrics
- Query response times (daily average, p95, p99)
- Database CPU and memory utilization
- Connection pool saturation
- Application error rates
- Customer-reported issues

### Decision Validity
This decision is considered **valid for 1 year** unless:
- PostgreSQL doesn't deliver expected performance gains
- New requirements emerge that PostgreSQL can't support
- Cost of operation exceeds projections by >50%
- Better alternative becomes available

---

## Lessons Learned (Post-Implementation)

*This section will be updated after migration completes in January 2026*

### What Went Well
- TBD

### What Could Be Improved
- TBD

### Recommendations for Future Decisions
- TBD

---

## Approval & Sign-Off

| Role | Name | Approval | Date |
|------|------|----------|------|
| **Decision Maker** | Sarah Johnson (PM) | ✅ Approved | Oct 26, 2025 |
| **Technical Lead** | Michael Rodriguez | ✅ Approved | Oct 26, 2025 |
| **Executive Sponsor** | John Smith | ✅ Approved | Oct 27, 2025 |
| **Operations Lead** | Lisa Wang | ✅ Approved | Oct 27, 2025 |

---

## Related Decisions

- **DEC-038**: Decision to increase database infrastructure budget (enabled this migration)
- **DEC-041**: Mobile app technical stack (requires JSON support, motivated this decision)
- **Future**: DEC-XXX: Decision on cloud migration (may revisit Aurora option)

---

## Document Metadata

**Document Version**: 1.0
**Created**: October 26, 2025
**Last Updated**: October 26, 2025
**Next Review**: January 26, 2026
**Classification**: Internal - Engineering
**Tags**: #database #architecture #migration #postgresql #technical-decision
```

## Success Criteria
- Decision statement is clear and unambiguous
- Context explains why decision was needed
- At least 2-3 alternatives were considered
- Rationale includes pros/cons analysis
- Impact analysis covers technical, business, team, and customer dimensions
- Implementation plan is actionable with owners and dates
- Success criteria are measurable
- Rollback plan exists for high-risk decisions

## Tips for Best Results

### For Better Decision Documentation
- Provide the decision statement clearly upfront
- Explain context: what problem prompted this decision?
- List alternatives actually considered (not just strawmen)
- Be honest about cons of selected option
- Specify who made the decision and their authority level

### Decision Categories
- **Strategic**: Long-term direction, hard to reverse
- **Technical**: Architecture, technology choices
- **Process**: How work gets done
- **Resource**: Budget, hiring, allocation
- **Scope**: What's in/out of scope

### Reversibility Assessment
- **Easy**: Can reverse in < 1 week with < $5K cost
- **Moderate**: Can reverse in 1-4 weeks with $5K-$25K cost
- **Difficult**: Requires > 1 month or > $25K to reverse
- **Irreversible**: Cannot practically reverse (e.g., data deletion)

## Version History

- **1.0.0** (2025-10-26): Initial release
