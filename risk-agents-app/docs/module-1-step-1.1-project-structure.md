# Module 1, Step 1.1: Project Directory Structure

**Module**: Foundation Setup (Week 1)
**Goal**: Create the complete directory structure for Risk Agents app
**Status**: ✅ Complete
**Date**: 2025-10-21

---

## What We Built

We created the complete directory structure for the Risk Agents application following the **Hybrid Architecture** approach. This structure implements the Claude Skills Framework with progressive disclosure and a simplified Knowledge Layer.

---

## Directory Structure

```
risk-agents-app/
├── README.md                          ✅ Project documentation
├── .gitignore                         ✅ Git ignore rules
│
├── backend/                           ✅ Python backend
│   ├── __init__.py
│   ├── .claude/                       🎯 Skills Framework (KEY!)
│   │   └── skills/
│   │       └── change-agent/          (Ready for skills)
│   ├── agent/                         ✅ Claude SDK integration
│   │   └── __init__.py
│   ├── api/                           ✅ FastAPI server
│   │   ├── __init__.py
│   │   └── routes/
│   │       └── __init__.py
│   ├── knowledge/                     🎯 Knowledge Layer (NEW!)
│   │   ├── taxonomy/
│   │   └── change-agent/
│   │       ├── meeting-management/
│   │       ├── project-management/
│   │       └── requirements-gathering/
│   └── context/                       ✅ Session storage
│       ├── captured/
│       └── templates/
│
├── frontend/                          ✅ Next.js frontend
│   ├── app/                           Next.js App Router
│   │   ├── auth/
│   │   │   ├── login/
│   │   │   └── signup/
│   │   ├── dashboard/
│   │   ├── chat/
│   │   ├── skills/
│   │   ├── knowledge/                 🎯 Knowledge browser
│   │   └── context/
│   ├── components/
│   │   ├── chat/
│   │   ├── skills/
│   │   ├── knowledge/                 🎯 Knowledge components
│   │   ├── dashboard/
│   │   └── ui/
│   ├── lib/                           API client
│   └── public/
│       └── images/
│
├── docker/                            ✅ Docker config (ready)
│
└── docs/                              📚 Documentation
    └── module-1-step-1.1-project-structure.md (this file)
```

---

## Files Created

### Configuration Files
- **README.md** - Project overview, getting started guide, architecture summary
- **.gitignore** - Git ignore rules for Python, Node.js, Docker, environment files
- **.gitkeep** files - Preserve empty directories in git (context/captured, context/templates)

### Python Package Files
- **backend/__init__.py** - Backend package
- **backend/agent/__init__.py** - Agent module package
- **backend/api/__init__.py** - API module package
- **backend/api/routes/__init__.py** - Routes sub-package

---

## Key Directories Explained

### Backend Structure

#### `backend/.claude/skills/`
**Purpose**: Claude Skills Framework with progressive disclosure
**Why Important**: This is the architectural innovation that makes Risk Agents powerful
- Not just simple YAML files
- Each skill has: `SKILL.md` + `instructions/` + `resources/` + optional `code/`
- Skills loaded progressively (metadata → instructions → resources)

#### `backend/knowledge/`
**Purpose**: Knowledge Layer with simplified taxonomy
**Why Important**: Organizes documentation and reference materials
- **taxonomy/** - Simple taxonomy reference document
- **change-agent/** - Organized by category:
  - `meeting-management/` - Meeting best practices
  - `project-management/` - PM methodologies
  - `requirements-gathering/` - Requirements techniques

#### `backend/agent/`
**Purpose**: Claude Agent SDK integration layer
**Files to create**:
- `agent_client.py` - Main Claude SDK wrapper
- `skills_loader.py` - Progressive disclosure skill loader
- `context_manager.py` - Session context management

#### `backend/api/`
**Purpose**: FastAPI server and REST API endpoints
**Files to create**:
- `api_server.py` - Main FastAPI application
- `auth.py` - Authentication middleware
- `websocket_handler.py` - Real-time streaming
- `routes/query.py` - Query endpoints
- `routes/skills.py` - Skills API
- `routes/knowledge.py` - Knowledge API

#### `backend/context/`
**Purpose**: Session-based context storage
**Structure**:
- `captured/` - Stores session data (captured information)
- `templates/` - Context templates for common scenarios

### Frontend Structure

#### `frontend/app/`
**Purpose**: Next.js 15 App Router pages
**Key Pages**:
- `auth/login/` - Login page
- `auth/signup/` - Signup page
- `dashboard/` - Main dashboard with metrics
- `chat/` - Natural language query interface
- `skills/` - Skills browser
- `knowledge/` - Knowledge browser (taxonomy-organized)
- `context/` - Context management UI

#### `frontend/components/`
**Purpose**: Reusable React components
**Organization**:
- `chat/` - Chat interface components (MessageList, QueryInput, ResponseStream)
- `skills/` - Skills browser components (SkillCard, SkillGrid, SkillDetails)
- `knowledge/` - Knowledge browser components (KnowledgeTree, DocumentCard, TaxonomyBrowser)
- `dashboard/` - Dashboard widgets
- `ui/` - Shared UI components (Button, Card, Navigation)

#### `frontend/lib/`
**Purpose**: Frontend utilities and API client
**Files to create**:
- `api-client.ts` - Fetch wrapper for backend API
- `websocket-client.ts` - WebSocket for streaming responses
- `auth.ts` - NextAuth configuration
- `utils.ts` - Helper utilities

### Docker Structure

#### `docker/`
**Purpose**: Docker configuration files
**Files to create**:
- `backend.Dockerfile` - Python 3.11 with UV package manager
- `frontend.Dockerfile` - Node 20 for Next.js
- `.dockerignore` - Files to exclude from Docker builds

---

## Architecture Highlights

### What Makes This Different?

This structure implements the **Hybrid Architecture** approach:

1. **Full Skills Framework** (Not just YAML)
   - `.claude/skills/` directory with proper structure
   - Progressive disclosure support built-in
   - Skills organized by domain (change-agent)

2. **Simplified Knowledge Taxonomy**
   - `knowledge/` directory organized by category
   - Not complex numbered codes (1.1.2, etc.)
   - Easy to browse and discover

3. **Separation of Concerns**
   - Backend: Python, FastAPI, Claude SDK
   - Frontend: TypeScript, Next.js, React
   - Docker: Containerization layer

4. **Production-Ready Structure**
   - Git-ready with proper `.gitignore`
   - Docker-ready with dedicated `docker/` directory
   - Documentation-ready with `docs/` directory

---

## Commands Used

```bash
# Create main project directory
mkdir -p risk-agents-app

# Create backend structure
mkdir -p backend/agent backend/api/routes \
  backend/.claude/skills/change-agent \
  backend/knowledge/taxonomy \
  backend/knowledge/change-agent/{meeting-management,project-management,requirements-gathering} \
  backend/context/captured backend/context/templates

# Create frontend structure
mkdir -p frontend/app/{auth/{login,signup},dashboard,chat,skills,knowledge,context} \
  frontend/components/{chat,skills,knowledge,dashboard,ui} \
  frontend/lib frontend/public/images

# Create docker directory
mkdir -p docker

# Create docs directory
mkdir -p docs

# Create Python package files
touch backend/__init__.py backend/agent/__init__.py \
  backend/api/__init__.py backend/api/routes/__init__.py

# Create .gitkeep files for empty directories
touch backend/context/captured/.gitkeep \
  backend/context/templates/.gitkeep

# Create configuration files
# (README.md, .gitignore created separately)
```

---

## What's Next?

**Next Step: Module 1, Step 1.2 - Docker Setup**

We'll create:
1. `docker/backend.Dockerfile` - Python 3.11 with UV package manager
2. `docker/frontend.Dockerfile` - Node 20 for Next.js
3. `docker-compose.yml` - Orchestrate both containers
4. `.env.example` - Environment variables template

This will enable running the entire app with just `docker-compose up`!

---

## Verification Checklist

- [x] Main project directory created (`risk-agents-app/`)
- [x] Backend directory structure created
- [x] `.claude/skills/` directory created (Skills Framework)
- [x] `knowledge/` directory created (Knowledge Layer)
- [x] Frontend directory structure created
- [x] Docker directory created
- [x] Docs directory created
- [x] Python `__init__.py` files created
- [x] `.gitkeep` files for empty directories
- [x] README.md created
- [x] .gitignore created

---

## Notes & Learnings

### Why This Structure?

**Skills Framework Directory** (`.claude/skills/`)
- This is the **key architectural innovation**
- Each skill will be a directory with progressive disclosure
- NOT just simple YAML files like in basic implementations
- Supports metadata → instructions → resources → code loading pattern

**Knowledge Layer** (`knowledge/`)
- Simple category-based organization
- No complex taxonomy codes initially (deferred to Phase 2)
- Easy to browse and add content
- Links to relevant skills

**Separation of Backend/Frontend**
- Complete independence enables:
  - Different deployment strategies
  - Independent scaling
  - Clear API contracts
  - Easier testing

**Docker-First Approach**
- All development happens in containers
- No "works on my machine" problems
- Same environment dev → production
- Easy onboarding for new developers

---

## Resources

- [Implementation Plan](../risk-agents-app-implementation-plan.md) - Full 12-week plan
- [Claude Skills Framework Docs](https://docs.claude.com/en/docs/claude-code/sub-agents) - Official documentation
- [Next.js App Router](https://nextjs.org/docs/app) - Next.js 15 documentation
- [FastAPI](https://fastapi.tiangolo.com/) - FastAPI framework docs
- [UV Package Manager](https://docs.astral.sh/uv/) - Modern Python package management

---

**Status**: ✅ Complete
**Time Taken**: ~15 minutes
**Next Module**: Module 1, Step 1.2 - Docker Setup
