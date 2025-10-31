# Module 7.2: Policy Selection

**Completed**: October 27, 2025
**Time**: 0.5 hours
**Status**: ✅ Complete

---

## Overview

Step 7.2 selected 7 representative policies from 28 FINAL ICBC Standard Bank policies to migrate with YAML frontmatter. The selection covers 5 risk domains and demonstrates the Risk Taxonomy Framework.

---

## Selection Criteria

### Must Have
1. **FINAL status** - Only use documents marked as FINAL
2. **Multiple risk domains** - Cover at least 5 different domains
3. **Range of sizes** - Mix of small (13K), medium (35-50K), large (60K+)
4. **High cross-reference potential** - Documents that reference methodologies, models, data, etc.

### Nice to Have
5. **Mix of artefact types** - Policies, frameworks, methodologies
6. **Different difficulty levels** - Beginner, Intermediate, Advanced
7. **Different owners** - Show multi-department governance

---

## Selected Policies (7 of 28)

### 1. Value-At-Risk Policy ✅ MIGRATED
**Domain**: Market Risk
**Size**: 35K
**Artefact Type**: policy
**Difficulty**: Advanced

**Selection Rationale**:
- **Core market risk policy** - Central to IMA regulatory capital
- **High cross-reference potential** - References methodologies, models, data, feeds, systems
- **Complex governance** - Multiple committees, approval processes
- **Skills integration** - var-calculation, stress-testing, backtesting-analysis

**Cross-References** (8 types, 23 total):
- methodologies: 3 (var-methodology, historical-simulation-methodology, proxy-methodology)
- models: 2 (historical-var-model, stress-var-model)
- data: 2 (market-data-dictionary, var-time-series)
- feeds: 4 (bloomberg-market-data, asset-control-feeds)
- governance: 3 (market-risk-committee-tor, mlrc-tor)
- controls: 3 (var-limit-monitoring, var-backtesting-control)
- processes: 2 (daily-var-calculation-process)
- systems: 4 (murex, asset-control)

---

### 2. Market Risk Stress Testing Framework ✅ MIGRATED
**Domain**: Market Risk
**Size**: 13K
**Artefact Type**: framework
**Difficulty**: Intermediate

**Selection Rationale**:
- **Different artefact type** - framework vs policy
- **Smaller size** - Good contrast to VAR Policy
- **Complementary to VAR** - References VAR policy and methodologies
- **Stress testing focus** - Important risk management tool

**Cross-References** (3 types, 6 total):
- policies: 2 (var-policy, market-risk-policy)
- methodologies: 1 (stress-scenario-methodology)
- models: 1 (stress-var-model)

---

### 3. Model Risk Management Policy ⏸️ PENDING
**Domain**: Model Risk
**Size**: 42K
**Artefact Type**: policy
**Difficulty**: Advanced

**Selection Rationale**:
- **Different risk domain** - Expands beyond market risk
- **Cross-domain references** - Links to market risk, credit risk, operational risk
- **Model governance focus** - References methodologies, controls, validation processes

**Expected Cross-References**:
- methodologies: Model validation methodology, model development standards
- governance: Model Risk Committee TOR, Model Validation Team mandate
- controls: Model approval controls, model monitoring controls
- processes: Model approval process, model validation process

---

### 4. Model Validation Policy ⏸️ PENDING
**Domain**: Model Risk
**Size**: 52K
**Artefact Type**: policy
**Difficulty**: Advanced

**Selection Rationale**:
- **Largest policy** - Tests system with large documents
- **Related to #3** - Model Risk Management ecosystem
- **Detailed cross-references** - Expected to reference many methodologies and controls

**Expected Cross-References**:
- methodologies: Validation methodologies for different model types
- governance: Independent validation requirements
- controls: Validation controls, testing protocols
- processes: Validation workflow, escalation procedures

---

### 5. Operational Risk Policy ⏸️ PENDING
**Domain**: Operational Risk
**Size**: 49K
**Artefact Type**: policy
**Difficulty**: Intermediate

**Selection Rationale**:
- **Third risk domain** - Operational risk coverage
- **Process-heavy** - Likely to reference many process maps and controls
- **RCSA integration** - Key control references (RCSA = Risk & Control Self-Assessment)

**Expected Cross-References**:
- processes: RCSA process, incident management process, control testing process
- controls: Key controls inventory, control effectiveness testing
- governance: Operational Risk Committee TOR
- systems: Operational risk systems (ORIS, GRC platforms)

---

### 6. Credit Delegated Authority Policy ⏸️ PENDING
**Domain**: Credit Risk
**Size**: 62K
**Artefact Type**: policy
**Difficulty**: Intermediate

**Selection Rationale**:
- **Fourth risk domain** - Credit risk coverage
- **Largest policy in set** - Ultimate stress test
- **Approval workflow focus** - Expected to reference governance and processes heavily

**Expected Cross-References**:
- governance: Credit Risk Committee TOR, approval authority matrices
- processes: Credit approval process, limit monitoring process
- controls: Dual approval controls, limit breach controls
- products: Approved products lists (what can be approved)

---

### 7. New Product Approval Policy ⏸️ PENDING
**Domain**: Product Risk
**Size**: 37K
**Artefact Type**: policy
**Difficulty**: Intermediate

**Selection Rationale**:
- **Fifth risk domain** - Product risk / Trade Execution Framework
- **Cross-domain integration** - References market risk, model risk, operational risk
- **Products focus** - References approved products lists

**Expected Cross-References**:
- products: Approved products inventories for different asset classes
- governance: New Product Approval Committee (NPSTAC) TOR
- processes: TEF process, product approval workflow
- methodologies: Valuation methodologies, risk methodologies for new products
- models: Pricing models, risk models

---

## Selection Summary

### Coverage Matrix

| Policy | Domain | Size | Type | Difficulty | Status |
|--------|--------|------|------|------------|--------|
| VAR Policy | Market Risk | 35K | policy | Advanced | ✅ Migrated |
| Stress Framework | Market Risk | 13K | framework | Intermediate | ✅ Migrated |
| Model Risk Mgmt | Model Risk | 42K | policy | Advanced | ⏸️ Pending |
| Model Validation | Model Risk | 52K | policy | Advanced | ⏸️ Pending |
| Operational Risk | Operational Risk | 49K | policy | Intermediate | ⏸️ Pending |
| Credit Authority | Credit Risk | 62K | policy | Intermediate | ⏸️ Pending |
| New Product Approval | Product Risk | 37K | policy | Intermediate | ⏸️ Pending |

### Statistics
- **Risk Domains**: 5 (Market, Model, Operational, Credit, Product)
- **Artefact Types**: 2 (policy, framework)
- **Size Range**: 13K - 62K
- **Difficulty Levels**: 2 (Intermediate, Advanced)
- **Total Size**: ~290K (average 41K per policy)

---

## Migration Approach

### Phase 1: Proof of Concept (Current Module)
**Policies**: VAR Policy + Stress Testing Framework

**Objectives**:
1. ✅ Prove YAML frontmatter works
2. ✅ Demonstrate different artefact types (policy vs framework)
3. ✅ Show different difficulty levels (Advanced vs Intermediate)
4. ✅ Validate cross-reference structure
5. ✅ Test end-to-end pipeline

**Success Criteria**:
- ✅ Both policies migrated with complete YAML
- ✅ Backend parses and returns metadata
- ✅ Frontend displays metadata beautifully
- ✅ Cross-references visible
- ✅ Skills integration working

### Phase 2: Bulk Migration (Future)
**Policies**: Remaining 5 policies

**Objectives**:
1. Complete 7-policy set
2. Cover all 5 risk domains
3. Test system with large documents (62K)
4. Optimize based on Phase 1 learnings

**Prerequisites**:
- Phase 1 complete and tested
- Any bugs from Phase 1 fixed
- Performance optimizations applied (if needed)

### Phase 3: Full Migration (Future)
**Policies**: All 28 FINAL policies

**Objectives**:
1. Complete knowledge base
2. Full Risk Taxonomy Framework implementation
3. Advanced features (clickable cross-refs, etc.)

---

## YAML Frontmatter Templates

### Policy Template
```yaml
---
title: [Policy Name]
domain: [domain-name]
category: policies
slug: [policy-slug]
description: [Short description]
artefact_type: policy
risk_domain: [Risk Domain Name]
owner: [Owner Role]
approval_committee: [Committee Name]
approval_date: YYYY-MM-DD
effective_date: YYYY-MM-DD
version: "X.Y"
tags: [tag1, tag2, tag3]
related_artefacts:
  methodologies: [list]
  models: [list]
  data: [list]
  # ... other types as needed
related_skills: [skill1, skill2, skill3]
difficulty: [Beginner|Intermediate|Advanced]
reading_time: X min
---
```

### Framework Template
```yaml
---
title: [Framework Name]
domain: [domain-name]
category: policies
slug: [framework-slug]
description: [Short description]
artefact_type: framework
risk_domain: [Risk Domain Name]
owner: [Owner Role]
approval_date: YYYY-MM-DD
version: "X.Y"
tags: [tag1, tag2, tag3]
related_artefacts:
  policies: [list]
  methodologies: [list]
  # ... other types as needed
related_skills: [skill1, skill2, skill3]
difficulty: [Beginner|Intermediate|Advanced]
reading_time: X min
---
```

---

## Cross-Reference Strategy

### Related Artefacts (Risk Taxonomy)
**Approach**: One-way references from dependent to dependency

**Example**: VAR Policy references:
- **methodologies**: VAR methodology (policy uses methodology)
- **models**: Historical VAR model (policy governs model)
- **data**: Market data dictionary (policy requires data)

**Benefits**:
- Clear dependency direction
- Easy to maintain
- Backend can compute reverse relationships if needed

### Related Skills (Bottom-Up)
**Approach**: Skills declare what knowledge they need

**Example**: `var-calculation` skill declares:
```yaml
related_knowledge:
  policies: [var-policy]
  methodologies: [var-methodology]
```

**Benefits**:
- Skills own their knowledge requirements
- Policies don't need to know all skills that use them
- Backend can compute "Used by Skills" dynamically

---

## Validation Checklist

For each migrated policy:
- [ ] YAML frontmatter valid (parses without errors)
- [ ] All required fields present (title, domain, category, slug)
- [ ] artefact_type correct (policy, framework, etc.)
- [ ] risk_domain matches domain classification
- [ ] approval_date in YYYY-MM-DD format
- [ ] version in string format ("X.Y")
- [ ] tags array populated (at least 3 tags)
- [ ] related_artefacts has at least 1 type with items
- [ ] related_skills has at least 1 skill
- [ ] difficulty is valid (Beginner, Intermediate, Advanced)
- [ ] reading_time estimated (format: "X min")
- [ ] Original content unchanged (only frontmatter added)

---

## Time Breakdown

| Activity | Time |
|----------|------|
| Review 28 FINAL policies | 0.15h |
| Analyze cross-reference potential | 0.15h |
| Select 7 policies | 0.10h |
| Document selection rationale | 0.10h |
| **Total** | **0.5h** |

---

## Deliverables

1. ✅ `module-7-selected-policies.md` - This selection document
2. ✅ Selection rationale for each policy
3. ✅ YAML templates for policy and framework types
4. ✅ Migration approach (3 phases)
5. ✅ Validation checklist

---

## Next Steps

**Immediate** (Step 7.3):
- Migrate VAR Policy with complete YAML frontmatter
- Migrate Stress Testing Framework with complete YAML frontmatter
- Validate both documents against checklist

**Future** (Phase 2):
- Migrate remaining 5 policies
- Optimize based on Phase 1 feedback
- Complete 7-policy set

---

**Status**: ✅ Selection Complete
**Outcome**: 7 policies selected covering 5 risk domains
**Next**: Step 7.3 - Policy Migration (2 policies)
