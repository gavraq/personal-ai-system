# Module 7.1: Migration Planning

**Completed**: October 27, 2025
**Time**: 1.5 hours
**Status**: ✅ Complete

---

## Overview

Step 7.1 analyzed the existing knowledge layer implementation (Modules 2.5 & 3.5) and planned the enhancement approach to add YAML frontmatter support for the Risk Taxonomy Framework.

### Key Decision

**Enhance existing implementation** rather than replace it:
- Maintain backward compatibility with plain Markdown
- Add YAML parsing to existing `knowledge_manager.py`
- Extend API models with optional metadata fields
- Preserve all existing functionality

---

## Analysis of Existing Implementation

### Module 2.5: Knowledge Manager (Original)
**File**: `backend/agent/knowledge_manager.py` (373 lines)

**Existing Features**:
- Reads Markdown files from `/knowledge` directory
- Hierarchical structure: `domain/category/document.md`
- Extracts cross-references `[[document.md]]`
- Basic metadata: title, domain, category, filename

**Missing**:
- YAML frontmatter parsing
- Rich metadata (owner, version, approval dates)
- Taxonomy classification (artefact types)
- Cross-references to other taxonomy components

### Module 3.5: Knowledge API (Original)
**File**: `backend/api/routes/knowledge.py` (475 lines)

**Existing Endpoints**:
- `GET /api/knowledge/taxonomy` - Full taxonomy tree
- `GET /api/knowledge/{domain}/{category}/{document}` - Get document
- `POST /api/knowledge/search` - Full-text search

**Missing**:
- Metadata fields in API responses
- Artefact type classification
- Related artefacts references
- Skills integration

---

## Enhancement Strategy

### 1. Backend Enhancements

**`knowledge_manager.py` Changes**:
```python
# ADD: YAML parsing method
def _parse_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
    """Parse YAML frontmatter, strip from content"""

# ENHANCE: KnowledgeDocument dataclass
@dataclass
class KnowledgeDocument:
    # Existing fields (unchanged)
    domain, category, filename, title, content, path, cross_references, size_bytes

    # NEW: 14 metadata fields
    slug, description, artefact_type, risk_domain, owner, approval_date,
    version, tags, related_artefacts, related_skills, difficulty, reading_time
```

**`knowledge API` Changes**:
```python
# ENHANCE: DocumentContent Pydantic model
class DocumentContent(BaseModel):
    # Existing fields (unchanged)
    domain, category, filename, title, content, path, cross_references, size_bytes

    # NEW: 14 metadata fields (all optional)
    slug, description, artefact_type, risk_domain, owner, approval_date,
    version, tags, related_artefacts, related_skills, difficulty, reading_time
```

### 2. Frontend Enhancements

**`KnowledgeArticle` Interface**:
- Add 9 optional YAML frontmatter fields
- Maintain existing fields for backward compatibility

**New Component**:
- `DocumentMetadata.tsx` - Display rich governance metadata

**Enhanced Components**:
- `KnowledgeDetails.tsx` - Integrate metadata display
- `knowledge/page.tsx` - Load from API instead of mock data

---

## Migration Strategy

### Content Source
**28 existing ICBC Standard Bank policy documents** from:
```
/Users/gavinslater/projects/riskagent/data/companies/icbc_standard_bank/background
```

**Selection Criteria**:
- Only use documents marked as "FINAL"
- Select representatives from multiple risk domains
- Range of sizes (13K - 62K)
- High cross-reference potential

### Phased Approach

**Phase 1: Proof of Concept** (Steps 7.2-7.6)
1. Select 7 representative policies (5 risk domains)
2. Migrate 2 policies with complete YAML frontmatter
3. Enhance backend to parse YAML
4. Create frontend UI components
5. Integrate API and test end-to-end
6. **Goal**: Prove the enhancement works

**Phase 2: Bulk Migration** (Future)
7. Migrate remaining 5 selected policies
8. Optimize based on Phase 1 learnings
9. **Goal**: Complete the 7-policy set

**Phase 3: Full Migration** (Future)
10. Migrate all 28 FINAL policies
11. Add advanced features (clickable cross-refs, etc.)
12. **Goal**: Complete knowledge base

---

## YAML Frontmatter Schema

### Core Fields
```yaml
---
# Identity
title: Value-At-Risk Policy
slug: var-policy
description: Policy governing VaR and SVaR measurement and control

# Taxonomy
domain: market-risk
category: policies
artefact_type: policy  # policy, framework, methodology, model, etc.
risk_domain: Market Risk

# Governance
owner: Head of Market Risk
approval_committee: Market & Liquidity Risk Committee
approval_date: 2023-06-01
effective_date: 2024-08-01
version: "4.5"

# Discovery
tags: [market-risk, var, svar, regulatory-capital, ima]
difficulty: Advanced  # Beginner, Intermediate, Advanced
reading_time: 30 min

# Risk Taxonomy Framework (11 Components)
related_artefacts:
  methodologies: [var-methodology, historical-simulation-methodology]
  models: [historical-var-model, stress-var-model]
  data: [market-data-dictionary, var-time-series]
  feeds: [bloomberg-market-data, asset-control-feeds]
  governance: [market-risk-committee-tor, mlrc-tor]
  controls: [var-limit-monitoring, var-backtesting-control]
  processes: [daily-var-calculation-process]
  systems: [murex, asset-control]
  # Also: policies, products, reports, risks

# Skills Integration (Bottom-Up)
related_skills:
  - var-calculation
  - stress-testing
  - backtesting-analysis
---
```

### Risk Taxonomy Framework (11 Components)

| Component | Description | Example |
|-----------|-------------|---------|
| policies | Governance policies | VAR Policy |
| governance | Committees, mandates | Credit Risk Committee TOR |
| processes | Process maps | Credit Approval Process |
| controls | Control inventories | Limit Monitoring Controls |
| products | Product inventories | Approved Products List |
| reports | MI reports | Credit Risk Dashboard |
| feeds | Data feeds | Trading System Interface |
| data | Data dictionaries | Credit Exposure Data |
| methodologies | Methods & models | CVA Methodology |
| systems | System inventories | CRMS Configuration |
| risks | Risk taxonomies | Credit Risk Classification |

---

## Backward Compatibility Strategy

### Design Principles
1. **All YAML fields optional** - Documents without frontmatter work unchanged
2. **Default values** - Missing fields return `None` or empty arrays
3. **Graceful degradation** - UI hides metadata section if no YAML
4. **No breaking changes** - Existing API contracts maintained

### Testing Approach
- ✅ Test with YAML frontmatter documents
- ✅ Test with plain Markdown documents
- ✅ Test with partial YAML (some fields missing)
- ✅ Verify existing API clients unaffected

---

## Success Criteria

### Technical Success
- ✅ YAML parsing works correctly
- ✅ Metadata flows through backend → API → frontend → UI
- ✅ Plain Markdown documents still work
- ✅ No breaking changes to existing code

### Business Success
- ✅ Rich governance metadata displayed
- ✅ Cross-references visible (related artefacts)
- ✅ Skills integration working (bottom-up references)
- ✅ Risk Taxonomy Framework implemented

---

## Deliverables

### Planning Documents
1. ✅ `module-7-implementation-with-existing-knowledge.md` - Analysis
2. ✅ `module-7-option-comparison.md` - Options analysis
3. ✅ `module-7-knowledge-layer-overview.md` - Overview

### Decision Record
**Decision**: Enhance existing implementation (Option 2)

**Rationale**:
- Faster (no rewrite needed)
- Lower risk (maintains existing functionality)
- Backward compatible (plain Markdown still works)
- Extensible (can add features incrementally)

---

## Time Breakdown

| Activity | Time |
|----------|------|
| Analyze existing implementation | 0.5h |
| Design enhancement approach | 0.5h |
| Document YAML schema | 0.25h |
| Create planning documents | 0.25h |
| **Total** | **1.5h** |

---

## Next Steps

**Immediate** (Step 7.2):
- Select 7 representative policies from 28 FINAL policies
- Document selection rationale
- Plan Phase 1 migration (2 policies)

**Future** (Steps 7.3-7.6):
- Migrate 2 policies with YAML frontmatter
- Enhance backend and API
- Create frontend UI components
- Integrate and test end-to-end

---

**Status**: ✅ Planning Complete
**Outcome**: Clear enhancement strategy with phased approach
**Next**: Step 7.2 - Policy Selection
