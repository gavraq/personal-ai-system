# Module 7: Knowledge Layer & Taxonomy

**Module Goal**: Build the Knowledge Layer with backend structure and frontend UI
**Estimated Time**: 6-8 hours
**Status**: 🚧 IN PROGRESS
**Started**: October 27, 2025

---

## Overview

Module 7 implements the Knowledge Layer - a structured repository of domain knowledge that supports and enriches the Skills Framework. While Skills define "how to do things," Knowledge provides the "what to know" - best practices, methodologies, frameworks, and reference materials.

### What is the Knowledge Layer?

The Knowledge Layer serves three primary purposes:

1. **Skill Enrichment**: Provides context and guidance that skills can reference
2. **User Education**: Helps users understand risk management concepts and methodologies
3. **Taxonomy Organization**: Creates a structured, browsable knowledge base

### Simplified Taxonomy Approach

Following the hybrid approach defined in the implementation plan, we're using a **simplified taxonomy** for MVP:

- **Category-based organization** (not complex numbered codes)
- **Human-readable structure** (project-management, meeting-management, etc.)
- **Easy to browse and discover** (tree navigation)
- **Practical over perfect** (can add complexity later)

---

## Module Structure

Module 7 is divided into 4 steps:

### Step 7.1: Backend Knowledge Structure ⏸️
**Goal**: Create backend knowledge loader and API endpoints
**Time**: ~2 hours
**Deliverables**:
- Knowledge document format (Markdown with YAML frontmatter)
- Knowledge loader (reads /knowledge directory)
- API endpoints (list, get, search knowledge)
- Knowledge metadata system

### Step 7.2: Initial Knowledge Documents ⏸️
**Goal**: Create 3-5 foundational knowledge documents
**Time**: ~2-3 hours
**Deliverables**:
- Meeting management best practices
- Project management methodologies
- Requirements gathering techniques
- (Optional) RACI matrix guide
- (Optional) Risk assessment frameworks

### Step 7.3: Frontend Knowledge Browser ⏸️
**Goal**: Build UI for browsing knowledge documents
**Time**: ~2-3 hours
**Deliverables**:
- Knowledge Browser page (/knowledge)
- Tree navigation component (taxonomy sidebar)
- Document viewer component (Markdown rendering)
- Search and filter functionality
- Related documents section

### Step 7.4: Backend-Frontend Integration ⏸️
**Goal**: Connect Knowledge Browser to backend API
**Time**: ~1 hour
**Deliverables**:
- API client methods for knowledge
- Real data integration (replace mock data)
- Loading and error states
- Document metadata display

---

## Architecture Overview

### Backend Structure

```
backend/
├── knowledge/                    # Knowledge Layer root
│   ├── change-agent/            # Domain: Change Agent
│   │   ├── meeting-management/  # Category
│   │   │   ├── effective-meetings.md
│   │   │   ├── meeting-minutes-guide.md
│   │   │   └── meeting-types.md
│   │   ├── project-management/
│   │   │   ├── project-charter-guide.md
│   │   │   ├── stakeholder-management.md
│   │   │   └── raci-matrix-guide.md
│   │   └── requirements-gathering/
│   │       ├── requirements-techniques.md
│   │       └── user-stories-guide.md
│   └── taxonomy.json            # Taxonomy structure (optional)
│
└── agent/
    └── knowledge_loader.py      # Knowledge loading logic
```

### Frontend Structure

```
frontend/
├── app/
│   └── knowledge/
│       ├── page.tsx             # Knowledge Browser main page
│       └── [domain]/
│           └── [category]/
│               └── [slug]/
│                   └── page.tsx # Individual document page
│
└── components/
    └── knowledge/
        ├── KnowledgeTree.tsx    # Taxonomy navigation tree
        ├── DocumentCard.tsx     # Document preview card
        ├── DocumentViewer.tsx   # Markdown document renderer
        ├── DocumentSearch.tsx   # Search and filter
        └── RelatedDocuments.tsx # Related docs sidebar
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/knowledge/` | GET | List all knowledge documents |
| `/api/knowledge/domains` | GET | Get available domains |
| `/api/knowledge/categories` | GET | Get categories by domain |
| `/api/knowledge/{domain}/{category}/{slug}` | GET | Get specific document |
| `/api/knowledge/search?q={query}` | GET | Search knowledge base |

---

## Document Format

Knowledge documents use Markdown with YAML frontmatter:

```yaml
---
title: Effective Meeting Management
domain: change-agent
category: meeting-management
slug: effective-meetings
description: Best practices for running effective meetings
tags:
  - meetings
  - facilitation
  - productivity
related_skills:
  - meeting-minutes-capture
  - action-item-tracking
related_documents:
  - meeting-types
  - meeting-minutes-guide
last_updated: 2025-10-27
---

# Effective Meeting Management

## Overview
[Content in Markdown format...]

## Key Principles
- **Purpose-driven**: Every meeting should have clear objectives
- **Time-boxed**: Set and stick to time limits
- **Action-oriented**: End with clear next steps

## Best Practices
...
```

### Frontmatter Fields

**Required**:
- `title`: Document title
- `domain`: Domain (e.g., "change-agent")
- `category`: Category (e.g., "meeting-management")
- `slug`: URL-friendly identifier
- `description`: Short summary (1-2 sentences)

**Optional**:
- `tags`: Array of searchable tags
- `related_skills`: Links to skills that use this knowledge
- `related_documents`: Links to other knowledge docs
- `author`: Document author
- `last_updated`: Last update date
- `difficulty`: Beginner/Intermediate/Advanced
- `reading_time`: Estimated reading time

---

## Taxonomy Structure

### Simplified Taxonomy (MVP)

```
Knowledge Base
├── Change Agent (domain)
│   ├── Meeting Management (category)
│   │   ├── Effective Meetings
│   │   ├── Meeting Minutes Guide
│   │   └── Meeting Types
│   ├── Project Management (category)
│   │   ├── Project Charter Guide
│   │   ├── Stakeholder Management
│   │   └── RACI Matrix Guide
│   └── Requirements Gathering (category)
│       ├── Requirements Techniques
│       └── User Stories Guide
```

### Future Domains (Post-MVP)

```
├── Credit Risk (domain)
│   ├── Credit Analysis
│   ├── Portfolio Management
│   └── Default Prediction
├── Market Risk (domain)
│   ├── VaR Methodologies
│   ├── Stress Testing
│   └── Scenario Analysis
└── Operational Risk (domain)
    ├── Risk Assessment
    ├── Control Frameworks
    └── Incident Management
```

---

## Integration with Skills

Knowledge documents support skills in three ways:

### 1. Skill References to Knowledge

Skills can reference knowledge documents in their YAML frontmatter:

```yaml
---
name: meeting-minutes-capture
description: Extract structured meeting minutes
related_knowledge:
  - change-agent/meeting-management/meeting-minutes-guide
  - change-agent/meeting-management/effective-meetings
---
```

### 2. Knowledge References to Skills

Knowledge documents list related skills:

```yaml
---
title: Meeting Minutes Guide
related_skills:
  - meeting-minutes-capture
  - action-item-tracking
---
```

### 3. Dynamic Linking in UI

The UI shows:
- Skills page → "Related Knowledge" section
- Knowledge page → "Related Skills" section
- Bidirectional navigation

---

## User Experience Flow

### Discovery Flow
```
User lands on /knowledge
  ↓
Sees taxonomy tree (domains → categories)
  ↓
Clicks category (e.g., "Meeting Management")
  ↓
Sees document cards (3-5 docs)
  ↓
Clicks document (e.g., "Effective Meetings")
  ↓
Reads document with:
  - Markdown content
  - Related skills sidebar
  - Related documents links
  - Tags for filtering
```

### Search Flow
```
User types search query
  ↓
Backend searches:
  - Document titles
  - Descriptions
  - Tags
  - Full content
  ↓
Returns ranked results
  ↓
User clicks result → Document viewer
```

---

## Design Decisions

### Why Simplified Taxonomy?

**Decision**: Use category-based organization instead of complex numbered codes (Fabrix)

**Reasoning**:
- **Faster to implement**: No need to design complex taxonomy system
- **Easier to understand**: Users can browse intuitively
- **Practical for MVP**: 10-15 documents don't need complex structure
- **Extensible**: Can add Fabrix numbering later if needed

**Trade-offs**:
- Less "sophisticated" than full taxonomy
- Harder to scale to 1000+ documents
- No hierarchical numbering system
- Acceptable for Phase 1 MVP

### Why Markdown?

**Decision**: Use Markdown files with YAML frontmatter

**Reasoning**:
- **Human-readable**: Easy to write and edit
- **Git-friendly**: Version control and collaboration
- **Rich formatting**: Headers, lists, code blocks, tables
- **Metadata support**: YAML frontmatter for structure

**Trade-offs**:
- Not a "proper" CMS
- No WYSIWYG editor (yet)
- Acceptable for Phase 1

### Why File-based Storage?

**Decision**: Store knowledge as files in `/knowledge` directory

**Reasoning**:
- **Simple**: No database needed for MVP
- **Fast**: File system reads are quick
- **Version control**: Git tracks all changes
- **Portable**: Easy to backup and deploy

**Trade-offs**:
- Not ideal for large scale (1000+ docs)
- No real-time collaboration
- Acceptable for MVP with 10-50 documents

---

## Success Criteria

### Technical Requirements
- [ ] Backend can load knowledge documents from file system
- [ ] API endpoints return knowledge metadata and content
- [ ] Frontend displays knowledge in tree navigation
- [ ] Document viewer renders Markdown correctly
- [ ] Search functionality works across titles and content
- [ ] Related skills/documents links work

### Functional Requirements
- [ ] Users can browse knowledge by domain and category
- [ ] Users can read individual knowledge documents
- [ ] Users can search knowledge base
- [ ] Users can navigate between related documents
- [ ] Users can see which skills use knowledge documents

### Quality Requirements
- [ ] Loading states for async operations
- [ ] Error handling for missing documents
- [ ] Responsive design (mobile/tablet/desktop)
- [ ] Consistent with Skills Browser design
- [ ] Accessible navigation and content

---

## Implementation Strategy

### Phase 1: Backend (Step 7.1)
1. Create knowledge document format specification
2. Implement knowledge loader (read Markdown + YAML)
3. Create API endpoints (list, get, search)
4. Add validation and error handling

### Phase 2: Content (Step 7.2)
1. Write 3-5 foundational documents
2. Ensure quality and consistency
3. Link to existing skills
4. Add metadata and tags

### Phase 3: Frontend UI (Step 7.3)
1. Build Knowledge Browser page
2. Create taxonomy tree navigation
3. Implement document viewer (Markdown renderer)
4. Add search and filter UI

### Phase 4: Integration (Step 7.4)
1. Connect frontend to backend API
2. Replace mock data with real API calls
3. Add loading and error states
4. Test end-to-end flow

---

## Estimated Timeline

| Step | Task | Time | Status |
|------|------|------|--------|
| 7.1 | Backend knowledge structure | 2 hours | ⏸️ Pending |
| 7.2 | Create knowledge documents | 2-3 hours | ⏸️ Pending |
| 7.3 | Frontend Knowledge Browser | 2-3 hours | ⏸️ Pending |
| 7.4 | Backend-Frontend integration | 1 hour | ⏸️ Pending |
| **Total** | | **7-9 hours** | |

---

## Deliverables

### Backend
- [ ] `backend/agent/knowledge_loader.py` - Knowledge loading logic
- [ ] `backend/api/routes/knowledge.py` - API endpoints
- [ ] `backend/knowledge/` - Directory structure with 3-5 documents

### Frontend
- [ ] `frontend/app/knowledge/page.tsx` - Knowledge Browser page
- [ ] `frontend/components/knowledge/KnowledgeTree.tsx` - Tree navigation
- [ ] `frontend/components/knowledge/DocumentViewer.tsx` - Markdown renderer
- [ ] `frontend/components/knowledge/DocumentCard.tsx` - Document cards
- [ ] `frontend/lib/api.ts` - Knowledge API methods (updated)

### Documentation
- [ ] `docs/module-7-knowledge-layer-overview.md` - This document
- [ ] `docs/module-7-progress.md` - Progress tracking
- [ ] `docs/module-7.1-backend-structure.md` - Step 7.1 documentation
- [ ] `docs/module-7.2-knowledge-documents.md` - Step 7.2 documentation
- [ ] `docs/module-7.3-frontend-ui.md` - Step 7.3 documentation
- [ ] `docs/module-7.4-integration.md` - Step 7.4 documentation

---

## Dependencies

### Prerequisites (Already Complete)
- ✅ Module 5: Frontend Features (Skills Browser as template)
- ✅ Module 6: Backend Skills (pattern for backend structure)
- ✅ Design System (for consistent UI)

### External Dependencies
- React Markdown library (for rendering)
- remark/rehype plugins (for Markdown processing)
- FastAPI (for backend API)
- Python Markdown library (for backend parsing - optional)

---

## Related Documentation

- [Implementation Plan](../risk-agents-app-implementation-plan.md) - Overall project plan
- [Module 6 Overview](./module-6-adding-change-agent-skills-overview.md) - Skills Framework (parallel structure)
- [Module 5.4 Documentation](./module-5.4-knowledge-browser.md) - Knowledge Browser UI (frontend mockup)
- [IMPLEMENTATION-STATUS.md](./IMPLEMENTATION-STATUS.md) - Project-wide status

---

**Status**: Ready to begin Step 7.1 - Backend Knowledge Structure
**Next**: Create knowledge loader and API endpoints
