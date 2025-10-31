# Module 7: Knowledge Layer Options Comparison

## Scenario: Market Risk VAR Calculation Skill

Let's use a concrete example from your Risk Taxonomy Framework:

**Use Case**: You have a skill called `var-calculation` (Market Risk domain) that needs to reference:
- **Policy Document**: Market Risk Policy (governance, methodology approval)
- **Methodology Document**: VAR Methodology specification
- **Data Dictionary**: Market data fields required
- **Model Inventory**: Which VAR model to use
- **Feed Specification**: Market data feed IDD

---

## Option A: Plain Markdown (Current System)

### Knowledge Structure
```
backend/knowledge/
├── market-risk/
│   ├── policies/
│   │   └── market-risk-policy.md
│   ├── methodologies/
│   │   └── var-methodology.md
│   ├── data/
│   │   └── market-data-dictionary.md
│   ├── models/
│   │   └── var-model-inventory.md
│   └── feeds/
│       └── market-data-feed-idd.md
```

### Example Document: `market-risk-policy.md`
```markdown
# Market Risk Policy

## Purpose
This policy governs the management of market risk...

## Governance
- Market Risk Committee (monthly)
- ALCO (quarterly)

## Key Controls
1. Daily VAR calculation
2. Stress testing
3. Limit monitoring

## References
See also:
- [[methodologies/var-methodology.md]]
- [[models/var-model-inventory.md]]
```

### Example Skill: `var-calculation/SKILL.md`
```yaml
---
name: var-calculation
description: Calculate Value at Risk for trading portfolio
domain: market-risk
category: risk-metrics
parameters:
  - portfolio_positions
  - confidence_level
  - time_horizon
output_format: json
related_knowledge:
  - market-risk/policies/market-risk-policy.md
  - market-risk/methodologies/var-methodology.md
  - market-risk/models/var-model-inventory.md
  - market-risk/data/market-data-dictionary.md
---

# VAR Calculation Skill

## Overview
Calculate Value at Risk using approved methodology...

## References
This skill must be executed in accordance with:
- Market Risk Policy (see [[market-risk/policies/market-risk-policy.md]])
- VAR Methodology (see [[market-risk/methodologies/var-methodology.md]])
```

### How It Works in Practice

**User asks**: "Calculate VAR for my FX portfolio"

**System flow**:
1. ✅ Skill `var-calculation` is executed
2. ❌ **No structured link** - skills reference knowledge via plain text mentions
3. ❌ **No reverse lookup** - can't easily find "which skills use this policy?"
4. ❌ **No metadata filtering** - can't search by "Show me all Market Risk policies"
5. ✅ **Basic navigation** - can click wiki-style links in UI

**Pros**:
- ✅ Simple - just Markdown files
- ✅ Fast to implement (~2 hours)
- ✅ Human-readable
- ✅ Works now (already implemented)

**Cons**:
- ❌ No structured relationships
- ❌ Limited search (text only)
- ❌ Can't filter by metadata
- ❌ Hard to track "what references what?"
- ❌ No validation of cross-references

---

## Option B: YAML Frontmatter (Enhanced System)

### Knowledge Structure
```
backend/knowledge/
├── market-risk/
│   ├── policies/
│   │   └── market-risk-policy.md         (with YAML)
│   ├── methodologies/
│   │   └── var-methodology.md            (with YAML)
│   ├── data/
│   │   └── market-data-dictionary.md     (with YAML)
│   ├── models/
│   │   └── var-model-inventory.md        (with YAML)
│   └── feeds/
│       └── market-data-feed-idd.md       (with YAML)
```

### Example Document: `market-risk-policy.md`
```markdown
---
title: Market Risk Policy
domain: market-risk
category: policies
slug: market-risk-policy
description: Policy governing the management of market risk exposures
tags:
  - policy
  - governance
  - var
  - stress-testing
artefact_type: Policy               # From your taxonomy framework!
governance_forums:
  - Market Risk Committee
  - ALCO
review_frequency: Annual
last_reviewed: 2025-01-15
next_review: 2026-01-15
owner: Head of Market Risk
related_skills:
  - var-calculation
  - stress-testing
  - limit-monitoring
related_documents:
  - var-methodology
  - var-model-inventory
related_artefacts:                  # Links to other taxonomy layers!
  methodologies:
    - var-methodology
  models:
    - var-model-inventory
  reports:
    - daily-var-report
  processes:
    - daily-risk-calculation-process
difficulty: Intermediate
reading_time: 15 min
---

# Market Risk Policy

## Purpose
This policy governs the management of market risk exposures...

## Governance
- **Market Risk Committee**: Monthly review of VAR, limits, breaches
- **ALCO**: Quarterly review of overall risk appetite

## Key Controls
1. **Daily VAR Calculation**
   - Methodology: [[var-methodology]]
   - Model: [[var-model-inventory]]
   - Data: [[market-data-dictionary]]
   - Process: [[daily-risk-calculation-process]]

2. **Stress Testing**
   - Methodology: [[stress-testing-methodology]]
   - Scenarios: [[stress-scenario-library]]

3. **Limit Monitoring**
   - Limits: [[market-risk-limits]]
   - Escalation: [[limit-breach-escalation-process]]

## Referenced By
This policy is implemented through:
- Skills: [VAR Calculation](../skills/var-calculation), [Stress Testing](../skills/stress-testing)
- Reports: [Daily VAR Report](../reports/daily-var-report)
- Processes: [Daily Risk Calculation](../processes/daily-risk-calculation)
```

### Example Skill: `var-calculation/SKILL.md`
```yaml
---
name: var-calculation
description: Calculate Value at Risk for trading portfolio
domain: market-risk
category: risk-metrics
parameters:
  - name: portfolio_positions
    description: Portfolio holdings
    required: true
  - name: confidence_level
    description: Confidence level (95%, 99%)
    default: 99%
  - name: time_horizon
    description: Time horizon in days
    default: 1
output_format: json
related_knowledge:
  policies:
    - market-risk/policies/market-risk-policy
  methodologies:
    - market-risk/methodologies/var-methodology
  models:
    - market-risk/models/var-model-inventory
  data:
    - market-risk/data/market-data-dictionary
  feeds:
    - market-risk/feeds/market-data-feed-idd
tags:
  - var
  - market-risk
  - quantitative
artefact_dependencies:               # From your taxonomy!
  - type: policy
    name: Market Risk Policy
    path: market-risk/policies/market-risk-policy
  - type: methodology
    name: VAR Methodology
    path: market-risk/methodologies/var-methodology
  - type: model
    name: VAR Model
    path: market-risk/models/var-model-inventory
---

# VAR Calculation Skill

[Rest of skill content...]
```

### How It Works in Practice

**User asks**: "Calculate VAR for my FX portfolio"

**System flow**:
1. ✅ Skill `var-calculation` is executed
2. ✅ **Structured links** - system knows exactly which artefacts are needed
3. ✅ **Auto-loading** - Claude can automatically load referenced policies/methodologies
4. ✅ **Validation** - system validates all artefacts exist before execution
5. ✅ **Reverse lookup** - "Market Risk Policy" page shows "Used by: var-calculation skill"
6. ✅ **Rich filtering** - search by tags, artefact type, owner, review status

**Example API call with auto-loading**:
```python
# System automatically detects artefact dependencies
skill = agent.get_skill("var-calculation")

# Loads all referenced knowledge automatically
context = agent.load_skill_context(skill)
# Returns:
# - market-risk-policy.md (full text)
# - var-methodology.md (full text)
# - var-model-inventory.md (full text)
# - market-data-dictionary.md (full text)

# Claude receives enriched prompt with all context
result = agent.execute_skill(
    skill="var-calculation",
    parameters={
        "portfolio_positions": positions,
        "confidence_level": "99%"
    },
    context=context  # All referenced documents loaded
)
```

---

## Comparison: Practical Scenarios

### Scenario 1: "Show me all artefacts related to VAR"

**Option A** (Plain Markdown):
```
Search: "VAR"
Results: 15 documents containing "VAR"
- market-risk-policy.md (mentions VAR 5 times)
- var-methodology.md (main document)
- stress-testing.md (mentions VAR)
- [12 other documents...]

❌ No way to filter by artefact type
❌ Can't see relationships between artefacts
❌ Manual work to find all dependencies
```

**Option B** (YAML Frontmatter):
```
Filter: artefact_type = "policy" + tags contains "var"
Results: 1 policy
- Market Risk Policy

Show related artefacts:
├── Methodologies
│   └── VAR Methodology
├── Models
│   └── VAR Model Inventory
├── Data
│   └── Market Data Dictionary
├── Skills
│   ├── VAR Calculation
│   └── Stress Testing
└── Reports
    └── Daily VAR Report

✅ Structured view of all VAR-related artefacts
✅ Shows relationships across taxonomy layers
✅ Can navigate entire dependency tree
```

### Scenario 2: "Which policies need review this month?"

**Option A**:
```
❌ Not possible - no review date metadata
❌ Manual check of each policy document
❌ No tracking of review cycles
```

**Option B**:
```
Filter: artefact_type = "policy" + next_review <= "2025-11-30"
Results: 3 policies
- Market Risk Policy (due 2025-11-15)
- Credit Risk Policy (due 2025-11-22)
- Operational Risk Policy (due 2025-11-28)

For each: Show owner, last_reviewed, related_artefacts
✅ Automated review tracking
✅ Can set reminders
✅ Shows who owns what
```

### Scenario 3: "Audit asks: How do you ensure VAR calculation follows policy?"

**Option A**:
```
Manual process:
1. Find Market Risk Policy document
2. Search for "VAR" mentions
3. Find VAR Methodology document
4. Search for skills mentioning VAR
5. Cross-reference manually
6. Write audit response

❌ Time-consuming (2-3 hours)
❌ Error-prone
❌ Hard to prove completeness
```

**Option B**:
```
Automated report:
GET /api/knowledge/audit-trail?artefact=market-risk-policy

Returns:
{
  "policy": "Market Risk Policy",
  "implementing_skills": [
    {
      "skill": "var-calculation",
      "references_policy": true,
      "references_methodology": true,
      "last_executed": "2025-10-27",
      "success_rate": "98%"
    }
  ],
  "supporting_artefacts": [
    { "type": "methodology", "name": "VAR Methodology", "linked": true },
    { "type": "model", "name": "VAR Model", "linked": true },
    { "type": "data", "name": "Market Data Dict", "linked": true }
  ],
  "completeness_check": {
    "policy_has_methodology": true,
    "methodology_has_model": true,
    "skill_references_all": true,
    "status": "COMPLETE"
  }
}

✅ Instant audit trail
✅ Provable completeness
✅ Automated compliance check
```

### Scenario 4: "Onboarding new Market Risk analyst"

**Option A**:
```
Manual reading list:
1. Here's the Market Risk Policy (link)
2. Here's the VAR Methodology (link)
3. Here's the Model Inventory (link)
4. [Analyst must piece together relationships]

❌ No guided learning path
❌ Missing dependencies unclear
❌ No difficulty progression
```

**Option B**:
```
Generated learning path:
GET /api/knowledge/learning-path?domain=market-risk&role=analyst

Returns:
Level 1 (Beginner):
- Market Risk Policy (15 min read)
- Risk Types Overview (10 min read)
- VAR Basics (20 min read)

Level 2 (Intermediate):
- VAR Methodology (30 min read)
- Prerequisites: Market Risk Policy, VAR Basics
- Related skills: var-calculation, stress-testing

Level 3 (Advanced):
- Model Methodology Documents (45 min read)
- Prerequisites: VAR Methodology
- Related skills: model-validation

✅ Structured learning path
✅ Clear prerequisites
✅ Difficulty progression
✅ Time estimates
```

---

## Your Taxonomy Framework Integration

### Mapping Your Framework to Knowledge Layer

| Your Taxonomy Layer | Knowledge Category | YAML Field | Example |
|---------------------|-------------------|------------|---------|
| **Risks** | `risks/` | `artefact_type: risk-definition` | Market Risk taxonomy |
| **Governance** | `governance/` | `artefact_type: governance`, `forums: [...]` | Market Risk Committee TOR |
| **Policies** | `policies/` | `artefact_type: policy`, `review_frequency`, `owner` | Market Risk Policy |
| **Processes** | `processes/` | `artefact_type: process`, `process_owner` | Daily VAR Calculation |
| **Controls** | `controls/` | `artefact_type: control`, `control_type: key/non-key` | Limit Monitoring Control |
| **Products** | `products/` | `artefact_type: product`, `approval_status` | FX Options |
| **Reports** | `reports/` | `artefact_type: report`, `frequency`, `distribution` | Daily VAR Report |
| **Feeds** | `feeds/` | `artefact_type: feed`, `sla`, `provider` | Bloomberg Market Data |
| **Data** | `data/` | `artefact_type: data-dictionary`, `dq_metrics` | Market Data Fields |
| **Models** | `models/` | `artefact_type: model`, `validation_status` | Historical Simulation VAR |
| **Systems** | `systems/` | `artefact_type: system`, `euc: true/false` | Murex, Summit |

### Example: Complete VAR Ecosystem

**With Option B**, you can represent your entire VAR ecosystem:

```yaml
# File: market-risk/policies/market-risk-policy.md
---
title: Market Risk Policy
artefact_type: Policy
owner: Head of Market Risk
review_frequency: Annual
related_artefacts:
  governance:
    - market-risk-committee-tor
  processes:
    - daily-var-calculation-process
  controls:
    - var-limit-monitoring-control
  reports:
    - daily-var-report
  models:
    - historical-simulation-var-model
---
```

```yaml
# File: market-risk/processes/daily-var-calculation-process.md
---
title: Daily VAR Calculation Process
artefact_type: Process
process_owner: Market Risk Analytics Team
related_artefacts:
  policies:
    - market-risk-policy
  methodologies:
    - var-methodology
  data:
    - market-data-dictionary
  feeds:
    - bloomberg-market-data-feed
  systems:
    - murex
    - summit
  models:
    - historical-simulation-var-model
  reports:
    - daily-var-report
---
```

```yaml
# File: market-risk/feeds/bloomberg-market-data-feed.md
---
title: Bloomberg Market Data Feed
artefact_type: Feed
provider: Bloomberg
sla: "T+0 by 10:00 London time"
idd_reference: "IDD-MKT-001"
related_artefacts:
  data:
    - market-data-dictionary
  systems:
    - bloomberg-interface
    - market-data-hub
  processes:
    - daily-data-validation-process
---
```

**Then queries like**:
- "Show me all feeds used in VAR calculation" → Instant answer
- "What's the SLA for Bloomberg data?" → In metadata
- "Which processes depend on this feed?" → Reverse lookup works
- "Has the Market Risk Policy been reviewed this year?" → Check `last_reviewed` field
- "What systems does VAR use?" → Follow `related_artefacts.systems`

---

## Recommendation: Option B with Phased Approach

### Phase 1: Core Enhancement (3-4 hours)
1. Add YAML frontmatter to 4 existing documents
2. Create 2 new documents with full metadata
3. Test taxonomy relationships

### Phase 2: Frontend (2-3 hours)
4. Build Knowledge Browser UI
5. Add filtering by artefact type
6. Show relationship visualizations

### Phase 3: Advanced Features (future)
7. Auto-loading skill context
8. Audit trail generation
9. Learning path generation
10. Review tracking dashboard

**Start with Phase 1** - it's only 3-4 hours and unlocks powerful capabilities that align perfectly with your Risk Taxonomy Framework.

---

## Summary

**Option A** is simpler but doesn't support your taxonomy framework properly:
- ❌ Can't distinguish policy from methodology from model
- ❌ Can't track review cycles
- ❌ Can't prove completeness to auditors
- ❌ Can't auto-load skill dependencies

**Option B** aligns with your taxonomy framework perfectly:
- ✅ Each artefact type explicitly tagged
- ✅ Relationships across taxonomy layers tracked
- ✅ Review cycles automated
- ✅ Audit trails automatic
- ✅ Skills auto-load relevant artefacts
- ✅ "Check-in/check-out" versioning possible (future)

**Given your taxonomy framework requirements**, Option B is strongly recommended.
