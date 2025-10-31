# Module 7: Knowledge Layer & Taxonomy Integration

**Started**: October 27, 2025
**Status**: 🚧 IN PROGRESS (70% complete)
**Implementation Time**: ~5 hours
**Files Created**: 4 new files
**Files Modified**: 5 existing files
**Documents Migrated**: 2 of 7 policies

---

## Overview

Module 7 enhances the existing Knowledge Layer (from Module 3.5) with YAML frontmatter metadata support to implement the Risk Taxonomy Framework. This module integrates 28 existing ICBC Standard Bank policy documents with rich metadata for governance, cross-referencing, and skills integration.

### What's New in Module 7

**Key Enhancement**: YAML frontmatter support for knowledge documents

**What Changed**:
- 🔧 Enhanced `backend/agent/knowledge_manager.py` (Module 2.5) - Added YAML parsing
- 🔧 Enhanced `backend/api/routes/knowledge.py` (Module 3.5) - Added metadata fields
- 🔧 Enhanced `frontend/components/knowledge/*` (Module 5.4) - Added metadata display
- 🔧 Enhanced `frontend/app/knowledge/page.tsx` (Module 5.4) - Added API integration
- ✨ Created 2 new policy documents with YAML frontmatter

### What's the Same

**Unchanged Components** (backward compatible):
- ✅ Knowledge base structure (`knowledge/` directory)
- ✅ API endpoints (`/api/knowledge/*`)
- ✅ Plain Markdown document support
- ✅ Cross-reference extraction (`[[document.md]]`)
- ✅ Full-text search functionality

---

## Goals

### Primary Goals
1. ✅ Add YAML frontmatter support to knowledge manager
2. ✅ Migrate 2 representative policies (VAR Policy, Stress Testing Framework)
3. ✅ Enhance API to return metadata
4. ✅ Create UI components to display metadata
5. ✅ Integrate frontend with backend API
6. ⏸️ Document complete implementation

### Secondary Goals (Future)
7. ⏸️ Migrate remaining 5 policies (Model Risk, Operational Risk, Credit Risk, Product Risk)
8. ⏸️ Add clickable related artefacts (navigate between documents)
9. ⏸️ Add clickable skills (execute from knowledge document)
10. ⏸️ Add advanced filtering (by artefact type, risk domain, difficulty)

---

## Architecture

### Data Flow: YAML Metadata Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                   Knowledge Document                        │
│  (Markdown with YAML Frontmatter)                           │
│                                                             │
│  ---                                                        │
│  title: Value-At-Risk Policy                               │
│  artefact_type: policy                                     │
│  risk_domain: Market Risk                                  │
│  owner: Head of Market Risk                                │
│  related_artefacts:                                        │
│    methodologies: [var-methodology, ...]                   │
│  related_skills: [var-calculation, ...]                    │
│  ---                                                        │
│                                                             │
│  # Value-At-Risk Policy                                    │
│  [Policy content...]                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│               Knowledge Manager (Backend)                   │
│  backend/agent/knowledge_manager.py                         │
│                                                             │
│  1. Parse YAML frontmatter (yaml.safe_load)                │
│  2. Extract metadata to KnowledgeDocument fields           │
│  3. Strip frontmatter from content                         │
│  4. Return KnowledgeDocument with 23 fields                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Endpoint                           │
│  backend/api/routes/knowledge.py                            │
│                                                             │
│  GET /api/knowledge/{domain}/{category}/{document}         │
│                                                             │
│  Returns JSON with all metadata:                           │
│  {                                                          │
│    "title": "Value-At-Risk Policy",                        │
│    "artefact_type": "policy",                              │
│    "risk_domain": "Market Risk",                           │
│    "related_artefacts": {...},                             │
│    "related_skills": [...],                                │
│    "content": "# Value-At-Risk Policy\n..."               │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                Frontend API Client                          │
│  frontend/lib/api.ts                                        │
│                                                             │
│  api.getDocument(domain, category, document)               │
│  → Returns KnowledgeDocument TypeScript interface          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Knowledge Browser Page                         │
│  frontend/app/knowledge/page.tsx                            │
│                                                             │
│  1. Fetch taxonomy (discover documents)                    │
│  2. Fetch each document (with metadata)                    │
│  3. Transform to KnowledgeArticle format                   │
│  4. Display in grid                                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│            DocumentMetadata Component                       │
│  frontend/components/knowledge/DocumentMetadata.tsx         │
│                                                             │
│  Displays:                                                  │
│  • Artefact type badge (color-coded)                       │
│  • Risk domain badge                                       │
│  • Difficulty badge (color-coded)                          │
│  • Document Information panel                              │
│  • Related Artefacts section (8 types)                     │
│  • Used by Skills section                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Steps

### Step 7.1: Migration Planning
**Status**: ✅ Complete
**Purpose**: Analyze existing implementation and plan enhancement approach
**Time**: 1.5 hours
**Documentation**: [module-7-step-7.1-migration-planning.md](module-7-step-7.1-migration-planning.md)

**What Was Delivered**:
- Analysis of existing knowledge manager (Module 2.5/3.5)
- Identification of required enhancements
- Decision to enhance existing code vs. replace
- Migration strategy for 28 ICBC policies

### Step 7.2: Policy Selection
**Status**: ✅ Complete
**Purpose**: Select representative policies for Phase 1 migration
**Time**: 0.5 hours
**Documentation**: [module-7-step-7.2-policy-selection.md](module-7-step-7.2-policy-selection.md)

**What Was Delivered**:
- Selection of 7 policies covering 5 risk domains
- Rationale for each policy selection
- Size analysis (13K - 62K per policy)
- Phase 1 approach: Migrate 2, test, then bulk migrate

### Step 7.3: Policy Migration
**Status**: ✅ Complete (2 of 7)
**Purpose**: Migrate policies with YAML frontmatter
**Time**: 1 hour
**Documentation**: [module-7-step-7.3-policy-migration.md](module-7-step-7.3-policy-migration.md)

**What Was Delivered**:
- VAR Policy (35K) with policy metadata
- Stress Testing Framework (13K) with framework metadata
- Complete YAML frontmatter schemas
- Related artefacts cross-references (8 types)
- Related skills references (3-4 skills per document)

### Step 7.4: Knowledge Manager Testing
**Status**: ✅ Complete
**Purpose**: Enhance knowledge manager to parse YAML frontmatter
**Time**: 0.5 hours
**Documentation**: [module-7-step-7.4-knowledge-manager-testing.md](module-7-step-7.4-knowledge-manager-testing.md)

**What Was Delivered**:
- Enhanced `KnowledgeDocument` dataclass (14 new fields)
- `_parse_frontmatter()` method (YAML parsing)
- Date serialization fix (datetime.date → string)
- API endpoint testing and verification

### Step 7.5: Frontend UI Update
**Status**: ✅ Complete
**Purpose**: Create UI components to display YAML metadata
**Time**: 0.75 hours
**Documentation**: [module-7-step-7.5-frontend-ui-update.md](module-7-step-7.5-frontend-ui-update.md)

**What Was Delivered**:
- `DocumentMetadata.tsx` component (200 lines)
- Enhanced `KnowledgeArticle` interface (9 new fields)
- Integration into `KnowledgeDetails.tsx` modal
- Color-coded badges for artefact types and difficulty

### Step 7.6: API Integration & Testing
**Status**: ✅ Complete
**Purpose**: Connect frontend to backend API
**Time**: 0.75 hours
**Documentation**: [module-7-step-7.6-api-integration.md](module-7-step-7.6-api-integration.md)

**What Was Delivered**:
- Enhanced `frontend/lib/api.ts` (3 new methods)
- Enhanced `frontend/app/knowledge/page.tsx` (API integration)
- `transformToArticle()` function (data mapping)
- Loading states and error handling
- End-to-end verification

### Step 7.7: Documentation
**Status**: ⏸️ Pending
**Purpose**: Finalize module documentation
**Time**: TBD

**What Will Be Delivered**:
- This overview document
- Consolidated progress document
- Individual step documents (7.1-7.6)
- Complete summary document

---

## YAML Frontmatter Schema

### Core Metadata Fields

```yaml
---
# Document Identity
title: Value-At-Risk Policy                    # Display title
slug: var-policy                                # URL-friendly identifier
description: Policy governing VaR and SVaR     # Short summary

# Taxonomy Classification
domain: market-risk                             # Knowledge domain
category: policies                              # Category within domain
artefact_type: policy                          # Type: policy, framework, methodology, model, etc.
risk_domain: Market Risk                        # Business risk domain

# Governance
owner: Head of Market Risk                      # Document owner
approval_committee: Market & Liquidity Risk Committee
approval_date: 2023-06-01                      # YYYY-MM-DD format
effective_date: 2024-08-01
version: "4.5"                                 # String format

# Discovery & Navigation
tags: [market-risk, var, svar, backtesting]   # Search tags
difficulty: Advanced                            # Beginner, Intermediate, Advanced
reading_time: 30 min                           # Estimated reading time

# Cross-References (Risk Taxonomy Framework - 11 Components)
related_artefacts:
  policies: [market-risk-policy, ...]          # Related policies
  governance: [market-risk-committee-tor, ...] # Governance documents
  processes: [daily-var-calculation-process]   # Process maps
  controls: [var-limit-monitoring, ...]        # Key controls
  products: [approved-products-list]           # Product inventories
  reports: [credit-risk-dashboard]             # MI reports
  feeds: [bloomberg-market-data, ...]          # Data feeds
  data: [market-data-dictionary]               # Data dictionaries
  methodologies: [var-methodology, ...]        # Methodologies & models
  systems: [murex, asset-control]              # Systems
  risks: [counterparty-credit-risk]            # Risk types

# Skills Integration (Bottom-Up References)
related_skills:
  - var-calculation                            # Skills that use this knowledge
  - stress-testing
  - backtesting-analysis
---

# Document Content in Markdown

[Content without frontmatter...]
```

### Artefact Types (Risk Taxonomy)

| Type | Description | Example | Badge Color |
|------|-------------|---------|-------------|
| `policy` | Governance policies | VAR Policy | Blue |
| `framework` | Risk frameworks | Stress Testing Framework | Purple |
| `governance` | Committees, mandates | Credit Risk Committee TOR | Slate |
| `processes` | Process maps | Credit Approval Process | Violet |
| `controls` | Control inventories | Limit Monitoring Controls | Indigo |
| `products` | Product inventories | Approved Products List | Blue |
| `reports` | MI reports | Credit Risk Dashboard | Cyan |
| `feeds` | Data feeds | Trading System Interface | Green |
| `data` | Data dictionaries | Credit Exposure Data | Yellow |
| `methodology` | Methods & models | CVA Methodology | Violet |
| `systems` | System inventories | CRMS Configuration | Indigo |
| `risks` | Risk taxonomies | Credit Risk Classification | Red |

---

## Changes to Earlier Modules

### Module 2.5: Knowledge Manager Enhancement

**File**: `backend/agent/knowledge_manager.py`
**Original Module**: Module 2.5 (Basic knowledge loading)
**Changes**: Added YAML frontmatter parsing

**What Changed**:
```python
# ADDED: Imports
import yaml
from dataclasses import dataclass, field

# ENHANCED: KnowledgeDocument dataclass
@dataclass
class KnowledgeDocument:
    # Original fields (unchanged)
    domain: str
    category: str
    filename: str
    title: str
    content: str
    path: str
    cross_references: List[str]
    size_bytes: int

    # NEW: YAML frontmatter fields (14 new fields)
    metadata: Dict[str, Any] = field(default_factory=dict)
    slug: Optional[str] = None
    description: Optional[str] = None
    artefact_type: Optional[str] = None
    risk_domain: Optional[str] = None
    owner: Optional[str] = None
    approval_date: Optional[str] = None
    version: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    related_artefacts: Dict[str, List[str]] = field(default_factory=dict)
    related_skills: List[str] = field(default_factory=list)
    difficulty: Optional[str] = None
    reading_time: Optional[str] = None

# NEW: YAML parsing method
def _parse_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
    """Parse YAML frontmatter from markdown content"""
    if not content.startswith('---'):
        return {}, content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content

    try:
        metadata = yaml.safe_load(parts[1].strip()) or {}
        content_without_frontmatter = parts[2].strip()
        return metadata, content_without_frontmatter
    except yaml.YAMLError:
        return {}, content

# ENHANCED: get_document() method
def get_document(self, domain: str, category: str, document: str) -> KnowledgeDocument:
    # NEW: Parse YAML frontmatter
    metadata, content = self._parse_frontmatter(full_content)

    # NEW: Extract all metadata fields
    return KnowledgeDocument(
        # Original fields...
        # NEW: YAML frontmatter fields
        slug=metadata.get('slug'),
        artefact_type=metadata.get('artefact_type'),
        risk_domain=metadata.get('risk_domain'),
        # ... all 14 new fields
    )
```

**Backward Compatibility**:
- ✅ Works with plain Markdown (no YAML)
- ✅ All YAML fields are optional
- ✅ Returns empty dict if no frontmatter detected

**Reference**: See [module-2-step-2.5-knowledge-layer.md](module-2-step-2.5-knowledge-layer.md) for original implementation

---

### Module 3.5: Knowledge API Enhancement

**File**: `backend/api/routes/knowledge.py`
**Original Module**: Module 3.5 (Knowledge API endpoints)
**Changes**: Added YAML metadata fields to API responses

**What Changed**:
```python
# ENHANCED: DocumentContent Pydantic model
class DocumentContent(BaseModel):
    # Original fields (unchanged)
    domain: str
    category: str
    filename: str
    title: str
    content: str
    path: str
    cross_references: List[str]
    size_bytes: int

    # NEW: YAML frontmatter fields (14 new fields)
    metadata: Dict[str, Any] = Field(default={})
    slug: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    artefact_type: Optional[str] = Field(default=None)
    risk_domain: Optional[str] = Field(default=None)
    owner: Optional[str] = Field(default=None)
    approval_date: Optional[str] = Field(default=None)
    version: Optional[str] = Field(default=None)
    tags: List[str] = Field(default=[])
    related_artefacts: Dict[str, List[str]] = Field(default={})
    related_skills: List[str] = Field(default=[])
    difficulty: Optional[str] = Field(default=None)
    reading_time: Optional[str] = Field(default=None)

# ENHANCED: get_document endpoint
@router.get("/{domain}/{category}/{document}")
async def get_document(...) -> DocumentContent:
    doc = knowledge_manager.get_document(...)
    return DocumentContent(
        # Original fields...
        # NEW: YAML frontmatter fields
        approval_date=str(doc.approval_date) if doc.approval_date else None,  # Date fix
        tags=doc.tags,
        related_artefacts=doc.related_artefacts,
        related_skills=doc.related_skills,
        # ... all 14 new fields
    )
```

**Backward Compatibility**:
- ✅ All new fields optional (default values)
- ✅ Existing API clients unaffected
- ✅ Existing endpoints unchanged

**Reference**: See [module-3-step-3.5-knowledge-api.md](module-3-step-3.5-knowledge-api.md) for original implementation

---

### Module 5.4: Knowledge Browser Enhancement

**Files**:
- `frontend/components/knowledge/KnowledgeCard.tsx`
- `frontend/components/knowledge/KnowledgeDetails.tsx`
- `frontend/app/knowledge/page.tsx`

**Original Module**: Module 5.4 (Knowledge Browser UI)
**Changes**: Added metadata display and API integration

**What Changed**:

**1. KnowledgeArticle Interface** (`KnowledgeCard.tsx`):
```typescript
export interface KnowledgeArticle {
  // Original fields (unchanged)
  id: string
  title: string
  summary: string
  category: string
  content?: string
  tags?: string[]
  lastUpdated: Date
  readTime?: number
  views?: number
  isBookmarked?: boolean
  author?: string
  relatedArticles?: string[]

  // NEW: YAML frontmatter fields (9 new fields)
  slug?: string
  description?: string
  artefact_type?: string
  risk_domain?: string
  owner?: string
  approval_date?: string
  version?: string
  related_artefacts?: Record<string, string[]>
  related_skills?: string[]
  difficulty?: string
  reading_time?: string
}
```

**2. DocumentMetadata Component** (`DocumentMetadata.tsx`):
```typescript
// NEW: 200-line component for displaying YAML metadata
export function DocumentMetadata({ article }: DocumentMetadataProps) {
  // Displays:
  // - Artefact type badge (color-coded by type)
  // - Risk domain badge
  // - Difficulty badge (color-coded by level)
  // - Document Information panel (owner, date, version)
  // - Related Artefacts section (grouped by type)
  // - Used by Skills section (skill chips)
}
```

**3. Knowledge Browser Page** (`page.tsx`):
```typescript
// CHANGED: From mock data to API data
const [articles, setArticles] = useState<KnowledgeArticle[]>([]); // Was: MOCK_ARTICLES

// NEW: API integration
useEffect(() => {
  async function loadKnowledge() {
    const taxonomy = await api.getTaxonomy();
    for (const domain of taxonomy.domains) {
      for (const category of domain.children) {
        for (const doc of category.children) {
          const fullDoc = await api.getDocument(...);
          allDocuments.push(fullDoc);
        }
      }
    }
    const articles = allDocuments.map(transformToArticle);
    setArticles(articles);
  }
  loadKnowledge();
}, []);

// NEW: Transformation function
function transformToArticle(doc: KnowledgeDocument): KnowledgeArticle {
  return {
    // Map API fields to UI fields
    id: doc.slug || doc.filename.replace('.md', ''),
    title: doc.title,
    summary: doc.description || doc.content.substring(0, 200) + '...',
    // Pass through all YAML fields
    artefact_type: doc.artefact_type,
    related_artefacts: doc.related_artefacts,
    related_skills: doc.related_skills,
    // ...
  };
}
```

**4. API Client** (`frontend/lib/api.ts`):
```typescript
// NEW: Knowledge API methods
export const api = {
  // ... existing methods ...

  // NEW: Knowledge methods
  getDocument: async (domain: string, category: string, document: string): Promise<KnowledgeDocument> => {
    return apiFetch<KnowledgeDocument>(`/api/knowledge/${domain}/${category}/${document}`)
  },

  getTaxonomy: async (): Promise<KnowledgeTaxonomy> => {
    return apiFetch<KnowledgeTaxonomy>('/api/knowledge/taxonomy')
  },
}

// NEW: TypeScript interfaces (matching backend models)
export interface KnowledgeDocument { /* ... */ }
export interface KnowledgeTaxonomy { /* ... */ }
```

**Backward Compatibility**:
- ✅ Works with plain Markdown documents (no metadata display)
- ✅ DocumentMetadata only renders if YAML fields present
- ✅ Fallback to mock data if API fails

**Reference**: See [module-5.4-knowledge-browser.md](module-5.4-knowledge-browser.md) for original implementation

---

## Testing

### Backend Testing

**Verified**:
- ✅ YAML parsing works correctly
- ✅ Date serialization (datetime.date → string)
- ✅ API returns all 14 metadata fields
- ✅ Plain Markdown still works (empty metadata)

**Test Commands**:
```bash
# Test VAR Policy endpoint
curl http://localhost:8050/api/knowledge/market-risk/policies/var-policy.md

# Expected: JSON with artefact_type="policy", difficulty="Advanced"

# Test Stress Testing Framework endpoint
curl http://localhost:8050/api/knowledge/market-risk/policies/stress-testing-framework.md

# Expected: JSON with artefact_type="framework", difficulty="Intermediate"
```

### Frontend Testing

**Verified** (via test guide):
- ✅ Knowledge Browser loads documents from API
- ✅ Loading spinner displays during fetch
- ✅ Error handling with fallback data
- ✅ DocumentMetadata component receives YAML fields
- ✅ Artefact type badges color-coded correctly
- ✅ Difficulty badges color-coded correctly
- ✅ Related artefacts grouped by type
- ✅ Related skills displayed as chips

**Browser Test**:
```
1. Navigate to http://localhost:3050/knowledge
2. Observe 6 documents load
3. Click "Value-At-Risk Policy"
4. Verify DocumentMetadata section displays:
   - [Policy] badge (blue)
   - [Market Risk] badge (slate)
   - [Advanced] badge (red)
   - Document Information panel
   - Related Artefacts (8 types)
   - Used by Skills (3 skills)
```

---

## Success Metrics

### Completed ✅
1. ✅ YAML frontmatter support added to knowledge manager
2. ✅ 2 policies migrated with complete metadata
3. ✅ API returns all metadata fields
4. ✅ DocumentMetadata component displays rich governance data
5. ✅ Frontend integrated with backend API
6. ✅ Backward compatibility maintained
7. ✅ End-to-end pipeline verified

### Remaining ⏸️
8. ⏸️ Remaining 5 policies migrated (29% → 100%)
9. ⏸️ Clickable related artefacts (navigate to referenced docs)
10. ⏸️ Clickable skills (execute from knowledge document)

---

## Performance

### Load Times
- Taxonomy endpoint: ~20ms
- Document endpoint: ~30-50ms per document
- Total page load: ~500-600ms for 6 documents

### Optimization Opportunities
1. **Parallel Fetching**: Use Promise.all() for simultaneous document fetches (6x faster)
2. **Lazy Loading**: Only fetch document content when modal opens
3. **Caching**: Store fetched documents in memory/localStorage

---

## Next Steps

### Immediate (Module 7 Completion)
1. ⏸️ Finalize documentation (this overview + step docs)
2. ⏸️ Create complete summary document
3. ⏸️ Update main project README

### Short-Term Enhancements
4. ⏸️ Optimize loading (parallel fetches)
5. ⏸️ Add caching (memory/localStorage)
6. ⏸️ Migrate remaining 5 policies

### Medium-Term Features
7. ⏸️ Clickable related artefacts navigation
8. ⏸️ Clickable skills execution
9. ⏸️ Advanced filtering (artefact type, risk domain, difficulty)
10. ⏸️ Full-text search enhancement

---

## Files Modified Summary

### Backend
| File | Module | Change Type | Lines Changed |
|------|--------|-------------|---------------|
| `backend/agent/knowledge_manager.py` | 2.5 | Enhanced | +80 lines |
| `backend/api/routes/knowledge.py` | 3.5 | Enhanced | +50 lines |

### Frontend
| File | Module | Change Type | Lines Changed |
|------|--------|-------------|---------------|
| `frontend/lib/api.ts` | 4.2 | Enhanced | +60 lines |
| `frontend/components/knowledge/KnowledgeCard.tsx` | 5.4 | Enhanced | +20 lines |
| `frontend/components/knowledge/DocumentMetadata.tsx` | NEW | Created | +200 lines |
| `frontend/components/knowledge/KnowledgeDetails.tsx` | 5.4 | Enhanced | +5 lines |
| `frontend/app/knowledge/page.tsx` | 5.4 | Enhanced | +100 lines |

### Knowledge Documents
| File | Type | Size | Status |
|------|------|------|--------|
| `backend/knowledge/market-risk/policies/var-policy.md` | NEW | 36K | ✅ Complete |
| `backend/knowledge/market-risk/policies/stress-testing-framework.md` | NEW | 13K | ✅ Complete |

---

## Documentation

### Module 7 Documents
- [x] `module-7-knowledge-taxonomy-integration.md` (this overview)
- [x] `module-7-progress.md` (progress tracking)
- [x] `module-7-step-7.1-migration-planning.md`
- [x] `module-7-step-7.2-policy-selection.md`
- [x] `module-7-step-7.3-policy-migration.md`
- [x] `module-7-step-7.4-knowledge-manager-testing.md`
- [x] `module-7-step-7.5-frontend-ui-update.md`
- [x] `module-7-step-7.6-api-integration.md`
- [ ] `module-7-complete-summary.md` (pending)

---

**Last Updated**: October 27, 2025
**Module Status**: 70% Complete
**Next**: Complete Step 7.7 documentation
