# Module 7: Implementation Plan with Existing ICBC Knowledge

**Date**: October 27, 2025
**Status**: Planning
**Existing Knowledge**: 28 FINAL policy documents + Committees/Processes/Risk_Taxonomy/Org_Charts

---

## Discovery: What We Have

### Existing Knowledge Location
**Source**: `/Users/gavinslater/projects/riskagent/data/companies/icbc_standard_bank/background`

**Structure**:
```
background/
├── Committees/          # Governance artefacts
├── Processes/           # Process documents
├── Risk_Taxonomy/       # Risk definitions
├── policies/            # 28 FINAL policy documents
│   ├── Model_Risk/
│   ├── Market_Risk/
│   ├── Credit_Risk/
│   ├── Operational_Risk/
│   └── ...
├── org_charts/          # Organization structure
├── metrics/
└── procedures/
```

### FINAL Policy Documents (28 files)

**Model Risk** (4 policies):
- Model and Tool Risk Management Policy
- Credit Risk Model Standards
- Model Risk Standards
- Model Validation Policy

**Operational Risk** (7 policies):
- Operational Risk Management Policy
- Risk Identification and Control Process Policy
- Global Privacy (Personal Data Protection) Policy
- Operational Risk Acceptance & Tolerance Policy
- Scenario Analysis Policy
- Materiality Matrix
- Operational Risk Incident Management Policy

**Market Risk** (6 policies):
- Commodities Inventory Risk Policy
- Value-At-Risk Policy
- Issuer Risk Policy
- Liquidity Limit EWI Monitoring Policy
- Interest Rate Risk in the Banking Book Policy
- Market Risk Stress Testing Framework

**Credit Risk** (multiple):
- Credit Delegated Authority Policy
- [Additional credit risk policies...]

**Other** (multiple):
- New Product Approval Policy
- Insurance Policy
- [Additional policies...]

### Current Document Format

Documents are **plain Markdown** with:
- ✅ Title headers (# Policy Name)
- ✅ Metadata tables (Approval date, Version, etc.)
- ✅ Section headers (## 1. Introduction, etc.)
- ✅ Confidentiality notices
- ❌ **No YAML frontmatter**
- ❌ **No artefact_type metadata**
- ❌ **No related_artefacts links**

---

## Module 7 Revised Plan

### Goal
Transform existing ICBC knowledge into Risk Agents Knowledge Layer with:
1. **YAML frontmatter** for structured metadata
2. **Artefact type classification** (Policy, Governance, Process, etc.)
3. **Cross-references** across taxonomy layers
4. **Skills integration** (which skills reference which artefacts)

### Approach: Phased Migration

#### Phase 1: Copy & Enhance Core Policies (This Module)
**Scope**: Select 5-8 representative policies across risk domains
**Time**: 3-4 hours
**Output**: Demonstration of YAML frontmatter system

#### Phase 2: Bulk Migration Script (Future)
**Scope**: Automated migration of remaining 20+ policies
**Time**: 2-3 hours
**Output**: All policies with frontmatter

#### Phase 3: Additional Artefacts (Future)
**Scope**: Committees, Processes, Risk_Taxonomy
**Time**: 4-6 hours
**Output**: Complete taxonomy implementation

---

## Phase 1 Implementation Plan (Module 7)

### Step 7.1: Create Migration Strategy ✅
**Status**: COMPLETE (this document)

**Decisions Made**:
- Use existing documents from `/Users/gavinslater/projects/riskagent/`
- Copy (not move) to preserve originals
- Add YAML frontmatter without changing content
- Focus on FINAL policies only
- Use your Risk Taxonomy Framework artefact types

---

### Step 7.2: Select Representative Policies
**Time**: 30 minutes
**Goal**: Choose 5-8 policies that demonstrate taxonomy

**Selection Criteria**:
1. Cover multiple risk domains (Market, Credit, Operational, Model)
2. Different complexity levels (some reference other policies)
3. Represent different taxonomy layers

**Proposed Selection**:

| Policy | Risk Domain | Artefact Type | Why Selected |
|--------|-------------|---------------|--------------|
| **Market Risk Policy** | Market Risk | Policy | Core market risk governance, references methodologies |
| **Value-At-Risk Policy** | Market Risk | Policy | Technical, references models/data/feeds |
| **Model Risk Management Policy** | Model Risk | Policy | Cross-domain, references governance + methodologies |
| **Model Validation Policy** | Model Risk | Policy | Process-heavy, references controls |
| **Operational Risk Policy** | Operational Risk | Policy | Broad scope, references many controls |
| **Credit Delegated Authority** | Credit Risk | Policy | Governance-focused, simple structure |
| **New Product Approval** | Product Risk | Policy | Cross-domain, references multiple areas |
| *(Optional)* **Stress Testing Framework** | Market Risk | Methodology | Different artefact type for variety |

**Rationale**: This selection provides:
- ✅ 4 risk domains represented
- ✅ Mix of governance and technical policies
- ✅ Simple and complex policies
- ✅ Opportunities for cross-references
- ✅ One methodology (not just policies)

---

### Step 7.3: Copy and Enhance Selected Documents
**Time**: 2-3 hours
**Goal**: Transform 5-8 documents with YAML frontmatter

**Process for Each Document**:

1. **Copy from source to knowledge layer**:
   ```bash
   cp /Users/gavinslater/projects/riskagent/data/companies/icbc_standard_bank/background/policies/Market_Risk/VaR/Value-At-Risk_Policy_FINAL.md \
      /Users/gavinslater/projects/life/risk-agents-app/backend/knowledge/market-risk/policies/var-policy.md
   ```

2. **Add YAML frontmatter** at top:
   ```yaml
   ---
   title: Value-At-Risk Policy
   domain: market-risk
   category: policies
   slug: var-policy
   description: Policy governing the calculation and monitoring of Value-at-Risk for trading portfolios
   artefact_type: policy
   risk_domain: Market Risk
   owner: Head of Market Risk
   approval_date: 2025-05-07
   approval_committee: Board Risk Management Committee
   version: "6.0"
   review_frequency: Annual
   next_review: 2026-05
   applicability: All Trading Desks
   tags:
     - market-risk
     - var
     - policy
     - governance
     - limits
   related_artefacts:
     methodologies:
       - var-methodology
       - historical-simulation-methodology
     models:
       - historical-var-model
     data:
       - market-data-dictionary
     feeds:
       - bloomberg-market-data
     governance:
       - market-risk-committee-tor
     controls:
       - var-limit-monitoring
       - var-backtesting
   related_skills:
     - var-calculation
     - stress-testing
     - limit-monitoring
   confidentiality: Confidential
   legal_entity: ICBC Standard Bank Plc
   ---

   # Value-At-Risk Policy

   **Confidential**

   [Original content continues unchanged...]
   ```

3. **Preserve original content** - No changes to policy text

4. **Document cross-references** - Note which policies reference each other

**Example Output**:
```
backend/knowledge/
├── market-risk/
│   ├── policies/
│   │   ├── var-policy.md                    (NEW - with YAML)
│   │   ├── market-risk-stress-testing.md    (NEW - with YAML)
│   │   └── liquidity-limit-policy.md        (NEW - with YAML)
│   └── methodologies/
│       └── var-methodology.md               (placeholder for now)
├── model-risk/
│   └── policies/
│       ├── model-risk-management.md         (NEW - with YAML)
│       └── model-validation-policy.md       (NEW - with YAML)
├── operational-risk/
│   └── policies/
│       └── operational-risk-policy.md       (NEW - with YAML)
└── credit-risk/
    └── policies/
        └── credit-delegated-authority.md    (NEW - with YAML)
```

---

### Step 7.4: Update Knowledge Loader (if needed)
**Time**: 30 minutes
**Goal**: Ensure knowledge_loader.py handles YAML frontmatter

**Check**:
- ✅ Does existing `knowledge_loader.py` parse YAML? (Yes - already implemented)
- ✅ Does it extract all metadata fields? (Yes)
- ✅ Does API return metadata? (Yes)

**Action**: Verify loading works, test with new documents

---

### Step 7.5: Update Frontend Knowledge Browser
**Time**: 1 hour
**Goal**: Display artefact_type and related_artefacts

**Changes to KnowledgeCard.tsx**:
```typescript
// Add artefact_type display
<span className="text-xs text-slate-400">
  {article.artefact_type} • {article.risk_domain}
</span>

// Show approval info for policies
{article.approval_date && (
  <span className="text-xs text-slate-500">
    Approved: {formatDate(article.approval_date)} v{article.version}
  </span>
)}
```

**Changes to KnowledgeDetails.tsx**:
```typescript
// Add "Related Artefacts" section
<div className="related-artefacts">
  <h3>Related Artefacts</h3>
  {article.related_artefacts?.methodologies && (
    <div>
      <strong>Methodologies:</strong>
      {article.related_artefacts.methodologies.map(...)}
    </div>
  )}
  {/* Same for models, data, feeds, etc. */}
</div>

// Add "Used by Skills" section
<div className="related-skills">
  <h3>Used by Skills</h3>
  {article.related_skills.map(skill => (
    <Link to={`/skills/${skill}`}>{skill}</Link>
  ))}
</div>
```

---

### Step 7.6: Connect Skills to Knowledge
**Time**: 30 minutes
**Goal**: Update 1-2 skills to reference policies

**Example**: Update `var-calculation` skill:
```yaml
# backend/.claude/skills/market-risk/var-calculation/SKILL.md
---
name: var-calculation
domain: market-risk
related_knowledge:
  - market-risk/policies/var-policy              # NEW
  - market-risk/methodologies/var-methodology
  - market-risk/models/historical-var-model
---
```

**Test**: Execute skill, verify knowledge loads correctly

---

### Step 7.7: Documentation
**Time**: 30 minutes

**Create**:
- `module-7.2-policy-migration.md` - Documents migration process
- Update `module-7-progress.md` - Mark steps complete
- Update `module-7-knowledge-layer-overview.md` - Note use of existing ICBC docs

---

## What Changed from Modules 3.5 and 5.4

### Module 3.5 (Knowledge API) - Changes

| Aspect | Module 3.5 (Original) | Module 7 (Enhanced) |
|--------|----------------------|---------------------|
| **Document Format** | Plain Markdown | Markdown + YAML frontmatter |
| **Metadata** | Title only (extracted from #) | Rich metadata (artefact_type, owner, approval_date, etc.) |
| **Cross-references** | `[[document.md]]` links | Structured `related_artefacts` in YAML |
| **Skills Integration** | Not connected | `related_skills` field links to skills |
| **Taxonomy** | Generic (domain/category) | Risk Taxonomy Framework aligned |
| **API Response** | Basic document info | Full metadata + related artefacts |

**Backward Compatible**: ✅ Yes - Module 3.5 API still works, just returns richer metadata

### Module 5.4 (Knowledge Browser) - Changes

| Aspect | Module 5.4 (Original) | Module 7 (Enhanced) |
|--------|----------------------|---------------------|
| **Category Display** | Generic categories | Risk Taxonomy Framework artefact types |
| **Metadata Display** | Title, summary, updated date | + Approval date, version, owner, confidentiality |
| **Related Items** | Generic "Related Articles" | Structured by taxonomy layer (methodologies, models, data, etc.) |
| **Skills Link** | Not present | "Used by Skills" section |
| **Filters** | By category | By artefact_type + risk_domain |
| **Search** | Title/content only | + Tags, owner, artefact_type |

**Backward Compatible**: ✅ Yes - UI gracefully handles documents without YAML (shows basic info)

---

## Migration Plan for Remaining Documents (Future)

### Bulk Migration Script
**Create**: `scripts/migrate-policies.py`

```python
#!/usr/bin/env python3
"""
Migrate ICBC policies to Risk Agents knowledge layer with YAML frontmatter
"""

import re
from pathlib import Path
import yaml

def extract_policy_metadata(content: str) -> dict:
    """Extract metadata from policy document tables"""
    metadata = {}

    # Extract approval date from table
    match = re.search(r'\| Approval date.*?\| (.*?) \|', content)
    if match:
        metadata['approval_date'] = match.group(1).strip()

    # Extract version
    match = re.search(r'\| Version.*?\| (.*?) \|', content)
    if match:
        metadata['version'] = match.group(1).strip()

    # [Similar for other fields...]

    return metadata

def add_yaml_frontmatter(filepath: Path, risk_domain: str) -> str:
    """Add YAML frontmatter to policy document"""

    with open(filepath, 'r') as f:
        content = f.read()

    # Extract title (first # heading)
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else filepath.stem

    # Extract metadata from document
    extracted_metadata = extract_policy_metadata(content)

    # Build YAML frontmatter
    frontmatter = {
        'title': title,
        'domain': risk_domain.lower().replace(' ', '-'),
        'category': 'policies',
        'slug': filepath.stem,
        'artefact_type': 'policy',
        'risk_domain': risk_domain,
        **extracted_metadata
    }

    # Create new document with frontmatter
    yaml_str = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
    new_content = f"---\n{yaml_str}---\n\n{content}"

    return new_content

def migrate_directory(source_dir: Path, dest_dir: Path, risk_domain: str):
    """Migrate all FINAL policies from source to dest"""

    for policy_file in source_dir.rglob('*FINAL*.md'):
        print(f"Migrating: {policy_file.name}")

        # Add frontmatter
        enhanced_content = add_yaml_frontmatter(policy_file, risk_domain)

        # Determine destination
        dest_file = dest_dir / policy_file.stem.replace('_FINAL', '').lower() / '.md'
        dest_file.parent.mkdir(parents=True, exist_ok=True)

        # Write enhanced document
        with open(dest_file, 'w') as f:
            f.write(enhanced_content)

        print(f"  → {dest_file}")

# Run migration
if __name__ == '__main__':
    source = Path('/Users/gavinslater/projects/riskagent/data/companies/icbc_standard_bank/background/policies')
    dest = Path('/Users/gavinslater/projects/life/risk-agents-app/backend/knowledge')

    # Migrate by risk domain
    migrate_directory(source / 'Market_Risk', dest / 'market-risk/policies', 'Market Risk')
    migrate_directory(source / 'Credit_Risk', dest / 'credit-risk/policies', 'Credit Risk')
    migrate_directory(source / 'Model_Risk', dest / 'model-risk/policies', 'Model Risk')
    migrate_directory(source / 'Operational_Risk', dest / 'operational-risk/policies', 'Operational Risk')
```

**Usage**:
```bash
python scripts/migrate-policies.py
# Migrates all remaining FINAL policies with YAML frontmatter
```

---

## Success Criteria

Module 7 is complete when:

### Phase 1 (This Module)
- [ ] 5-8 representative policies copied and enhanced with YAML frontmatter
- [ ] Knowledge loader successfully loads documents with frontmatter
- [ ] API returns rich metadata (artefact_type, related_artefacts, etc.)
- [ ] Frontend displays enhanced metadata
- [ ] At least 1-2 skills reference knowledge documents
- [ ] Documentation complete

### Future Phases
- [ ] Bulk migration script created
- [ ] All 28 FINAL policies migrated
- [ ] Committees, Processes, Risk_Taxonomy artefacts added
- [ ] Full taxonomy coverage achieved

---

## Timeline

**Phase 1 (Module 7)**:
- Step 7.2: Select policies (30 min)
- Step 7.3: Copy & enhance 5-8 policies (2-3 hours)
- Step 7.4: Verify knowledge loader (30 min)
- Step 7.5: Update frontend (1 hour)
- Step 7.6: Connect skills (30 min)
- Step 7.7: Documentation (30 min)

**Total**: ~5-6 hours for Phase 1

**Future Phases**: 6-10 hours (bulk migration + additional artefacts)

---

## Next Steps

1. ✅ Review this plan
2. ⏸️ Select 5-8 representative policies
3. ⏸️ Begin Step 7.3 (copy & enhance)
4. ⏸️ Test with knowledge loader
5. ⏸️ Update frontend
6. ⏸️ Connect to skills

**Ready to proceed with Step 7.2 (select policies)?**
