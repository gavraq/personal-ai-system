# Risk Agents App - Implementation Plan (Hybrid Approach)

## Overview
Building a standalone Risk Agents application following Cole Medin's Claude Agent SDK pattern with proper Skills Framework architecture. The app will be separate from the marketing website and provide a full-featured risk management platform powered by Claude AI.

**Architecture Approach**: Hybrid (12 weeks recommended)
- ✅ **Full Claude Skills Framework** implementation (progressive disclosure)
- ✅ **Simplified Risk Taxonomy** (Knowledge Layer organization)
- ⏸️ **Fabrix Pattern System** (deferred to Phase 2)
- ⏸️ **GTD Horizons Integration** (deferred to Phase 2)
- ⏸️ **Natural Language Query Engine** (deferred to Phase 2)

### Why Hybrid Approach?

**What We're Building Now (Phase 1 - MVP)**:
1. **Proper Skills Framework** - Essential foundation, must be done right
   - Skills with progressive disclosure (SKILL.md + instructions/ + resources/)
   - Not just simple YAML files, but proper Claude SDK skills structure
   - This is the architectural innovation that makes Risk Agents powerful

2. **Simplified Knowledge Taxonomy** - Practical organization layer
   - Category-based organization (meeting-management, project-management, etc.)
   - Not complex numbered codes initially
   - Easy to browse and discover relevant information

3. **Change Agent Domain** - Complete first use case
   - 10-15 fully implemented skills for project management
   - Meeting management, project setup, requirements gathering, etc.
   - Validates the architecture with real-world use cases

**What We're Deferring (Phase 2 - Post-MVP)**:
1. **Fabrix Pattern System** - Can wait until we have enough skills
2. **GTD Horizons** - Important for enterprise, but not blocking for learning
3. **Natural Language Query Engine** - Advanced feature, simpler chat works for MVP
4. **Additional Risk Domains** - Credit, Market, Operational risk (after validating with Change Agent)

**Timeline**: 12 weeks (vs 10 weeks originally, vs 16 weeks for full architecture)

---

## Architecture Pattern (Based on Cole Medin's Approach)

### Core Concept
- **Backend**: Python + Claude Agent SDK (like Cole's Obsidian/Telegram integrations)
- **Frontend**: Next.js 15 + TypeScript (separate interface connecting to backend)
- **Communication**: REST API + WebSocket for real-time streaming
- **Authentication**: NextAuth.js (frontend) + JWT validation (backend)
- **Deployment**: Docker containers for both backend and frontend

### Architecture Diagram
```
                                    Docker Compose
                                          │
                    ┌─────────────────────┴─────────────────────┐
                    │                                             │
            ┌───────▼────────┐                          ┌────────▼────────┐
            │  Frontend      │                          │   Backend       │
            │  Container     │◄────────────────────────►│   Container     │
            │  (Next.js)     │     REST + WebSocket     │   (FastAPI)     │
            │  Port 3050     │                          │   Port 8050     │
            └────────────────┘                          └─────────┬───────┘
                                                                  │
                                                                  ▼
                                                        Claude Agent SDK
                                                        Skills/Patterns
                                                        Context Management

User → Frontend Container → Backend Container → Claude Agent SDK → Response Stream
```

---

## Project Structure (Hybrid Approach with Skills Framework)

```
/risk-agents-app/
├── /backend (Python - Claude Agent SDK)
│   ├── /agent
│   │   ├── agent_client.py         # Core Claude Agent SDK wrapper
│   │   ├── skills_loader.py        # Progressive disclosure skill loader
│   │   ├── context_manager.py      # Context management for skills
│   │   └── __init__.py
│   ├── /api
│   │   ├── api_server.py           # FastAPI main server
│   │   ├── auth.py                 # Authentication middleware (JWT validation)
│   │   ├── websocket_handler.py    # Real-time streaming responses
│   │   ├── routes/
│   │   │   ├── query.py            # Chat query endpoint
│   │   │   └── skills.py           # Skills management endpoints
│   │   └── __init__.py
│   │
│   ├── /.claude                    # Claude Skills Framework (NEW!)
│   │   └── /skills                 # Skills with progressive disclosure
│   │       └── /change-agent       # Change Agent domain (FIRST DOMAIN)
│   │           ├── /meeting-minutes-capture
│   │           │   ├── SKILL.md              # Skill definition (YAML frontmatter)
│   │           │   ├── /instructions
│   │           │   │   ├── capture.md        # How to capture minutes
│   │           │   │   └── extract-actions.md # How to extract actions
│   │           │   ├── /resources
│   │           │   │   └── meeting-template.md
│   │           │   └── /code (optional)
│   │           │       └── parser.py
│   │           │
│   │           ├── /action-item-tracking
│   │           │   ├── SKILL.md
│   │           │   ├── /instructions
│   │           │   └── /resources
│   │           │
│   │           ├── /project-charter-generator
│   │           │   ├── SKILL.md
│   │           │   ├── /instructions
│   │           │   └── /resources
│   │           │
│   │           ├── /stakeholder-analysis
│   │           ├── /raci-matrix-generator
│   │           └── ... (10-15 Change Agent skills)
│   │
│   ├── /knowledge                  # Knowledge Layer (Simplified Taxonomy)
│   │   ├── /taxonomy
│   │   │   └── structure.md        # Simple taxonomy reference
│   │   ├── /change-agent           # Organized by domain/category
│   │   │   ├── /project-management
│   │   │   ├── /meeting-management
│   │   │   └── /requirements-gathering
│   │   └── README.md               # Knowledge organization guide
│   │
│   ├── /context                    # Session context storage
│   │   ├── captured/               # Captured information
│   │   └── templates/              # Context templates
│   │
│   ├── pyproject.toml              # UV dependency management
│   ├── uv.lock                     # UV lock file
│   ├── .env.example
│   └── README.md
│
├── /frontend (Next.js 15 + TypeScript)
│   ├── /app
│   │   ├── /auth
│   │   │   ├── login/page.tsx
│   │   │   ├── signup/page.tsx
│   │   │   └── layout.tsx
│   │   ├── /dashboard
│   │   │   └── page.tsx            # Main dashboard with metrics
│   │   ├── /chat
│   │   │   └── page.tsx            # Natural language query interface
│   │   ├── /skills
│   │   │   ├── page.tsx            # Skills browser (all 100+)
│   │   │   └── [domain]/page.tsx   # Domain-specific skills
│   │   ├── /knowledge
│   │   │   └── page.tsx            # Knowledge browser (taxonomy-organized)
│   │   ├── /context
│   │   │   └── page.tsx            # 3 C's context management
│   │   ├── layout.tsx
│   │   └── page.tsx                # App home (redirects to dashboard)
│   ├── /components
│   │   ├── /chat
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── QueryInput.tsx
│   │   │   └── ResponseStream.tsx
│   │   ├── /skills
│   │   │   ├── SkillCard.tsx
│   │   │   ├── SkillGrid.tsx
│   │   │   ├── SkillDetails.tsx
│   │   │   └── DomainFilter.tsx
│   │   ├── /knowledge
│   │   │   ├── KnowledgeTree.tsx
│   │   │   ├── DocumentCard.tsx
│   │   │   └── TaxonomyBrowser.tsx
│   │   ├── /dashboard
│   │   │   ├── MetricsWidget.tsx
│   │   │   ├── RecentQueries.tsx
│   │   │   └── QuickActions.tsx
│   │   └── /ui                     # Reusable UI components
│   │       ├── Navigation.tsx
│   │       ├── Button.tsx
│   │       ├── Card.tsx
│   │       └── Badge.tsx
│   ├── /lib
│   │   ├── api-client.ts           # Fetch wrapper for backend API
│   │   ├── websocket-client.ts     # WebSocket for streaming responses
│   │   ├── auth.ts                 # NextAuth configuration
│   │   └── utils.ts
│   ├── /public
│   │   └── images/
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── package.json
│   └── .env.local.example
│
├── /docker                         # Docker configuration files
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── .dockerignore
├── docker-compose.yml              # Docker Compose for local development
├── docker-compose.prod.yml         # Docker Compose for production
├── .gitignore
└── README.md
```

---

## Implementation Phases

### Phase 1: Project Setup & Infrastructure (Week 1)

#### 1.1 Initialize Project Structure
- [ ] Create `/risk-agents-app` directory
- [ ] Set up Python backend structure
- [ ] Set up Next.js frontend structure
- [ ] Initialize Git repository
- [ ] Create `.gitignore` files

#### 1.2 Backend Setup (Using UV)
- [ ] Install UV package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- [ ] Initialize Python project with UV: `uv init backend`
- [ ] Install dependencies using UV:
  - `uv add claude-agent-sdk`
  - `uv add fastapi`
  - `uv add uvicorn`
  - `uv add python-jose[cryptography]`
  - `uv add python-multipart`
  - `uv add websockets`
  - `uv add pydantic`
  - `uv add pyyaml`
- [ ] UV will create `pyproject.toml` and `uv.lock` automatically
- [ ] Set up `.env` configuration

#### 1.3 Frontend Setup
- [ ] Initialize Next.js 15 with TypeScript
- [ ] Install dependencies:
  - `next-auth`
  - `tailwindcss`
  - `@types/node`, `@types/react`
  - `swr` or `react-query` (data fetching)
  - `socket.io-client` (WebSocket)
- [ ] Configure Tailwind CSS (reuse design system from marketing site)
- [ ] Set up `.env.local` configuration

#### 1.4 Docker Setup

**File: `docker/backend.Dockerfile`**
```dockerfile
FROM python:3.11-slim

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files
COPY backend/pyproject.toml backend/uv.lock* ./

# Install dependencies using UV
RUN uv sync --frozen

# Copy application code
COPY backend/ .

# Expose port
EXPOSE 8050

# Run the application using UV
CMD ["uv", "run", "uvicorn", "api.api_server:app", "--host", "0.0.0.0", "--port", "8050", "--reload"]
```

**File: `docker/frontend.Dockerfile`**
```dockerfile
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY frontend/package*.json ./
RUN npm ci

# Copy application code
COPY frontend/ .

# Expose port
EXPOSE 3050

# Run the application
CMD ["npm", "run", "dev"]
```

**File: `docker-compose.yml`** (Single environment - no separate dev/prod)
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: docker/backend.Dockerfile
    ports:
      - "8050:8050"
    volumes:
      - ./backend:/app
      - ./backend/skills:/app/skills
      - ./backend/patterns:/app/patterns
      - ./backend/context:/app/context
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - JWT_SECRET=${JWT_SECRET}
      - ENVIRONMENT=${ENVIRONMENT:-development}
    restart: unless-stopped
    networks:
      - risk-agents

  frontend:
    build:
      context: .
      dockerfile: docker/frontend.Dockerfile
    ports:
      - "3050:3050"
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8050
      - NEXTAUTH_URL=http://localhost:3050
      - NEXTAUTH_SECRET=${NEXTAUTH_SECRET}
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - risk-agents

networks:
  risk-agents:
    driver: bridge
```

**File: `.env.example`** (Root level - single environment)
```bash
# Anthropic API
ANTHROPIC_API_KEY=your_api_key_here

# Authentication
JWT_SECRET=your_jwt_secret_here
NEXTAUTH_SECRET=your_nextauth_secret_here
NEXTAUTH_URL=http://localhost:3050

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8050
API_URL=http://backend:8050

# Environment (development or production)
ENVIRONMENT=development
```

Tasks:
- [ ] Create `docker/` directory
- [ ] Create `backend.Dockerfile` with Python 3.11 and UV
- [ ] Create `frontend.Dockerfile` with Node 20
- [ ] Create single `docker-compose.yml` (works for both dev and production)
- [ ] Create `.dockerignore` files
- [ ] Create `.env.example` file
- [ ] Create `.env` file (copy from .env.example, add real values)
- [ ] Document Docker commands in README

**Docker Commands:**
```bash
# Build and start all containers
docker-compose up --build

# Start containers (after first build)
docker-compose up

# Stop containers
docker-compose down

# View logs
docker-compose logs -f

# Rebuild specific service
docker-compose build backend
docker-compose build frontend

# Run commands inside containers
docker-compose exec backend python -m pytest
docker-compose exec frontend npm run lint
```

#### 1.5 Development Environment
- [ ] Configure ESLint + Prettier
- [ ] Set up VS Code workspace settings
- [ ] Create development scripts
- [ ] Test Docker containers start successfully
- [ ] Verify frontend can reach backend API
- [ ] Test hot-reload works in both containers

---

### Phase 2: Backend Core (Claude Agent SDK + Skills Framework) (Week 2-3)

#### 2.1 Claude Agent SDK Wrapper
**File: `backend/agent/agent_client.py`**

```python
from claude_agent_sdk import AgentSDKClient
from typing import Iterator, Dict, Any
from pathlib import Path

class RiskAgentClient:
    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self.client = AgentSDKClient({
            "working_directory": str(skills_dir.parent),
            "system_prompt": self._build_system_prompt(),
            "permissions": {
                "read_skills": True,
                "execute_skills": True
            }
        })

    def query(self, user_message: str, context: Dict[str, Any]) -> Iterator:
        """Execute a query with Skills Framework context"""
        # Skills are loaded progressively by Claude SDK
        for message_block in self.client.query(user_message):
            yield message_block

    def _build_system_prompt(self) -> str:
        """Build system prompt with Skills Framework awareness"""
        return """You are Risk Agents, a specialized AI assistant for project management.

        You have access to Change Agent skills organized in the .claude/skills directory.
        Each skill follows progressive disclosure - load only what's needed when needed.

        Available skill categories:
        - Meeting Management (meeting-minutes-capture, action-item-tracking, etc.)
        - Project Setup (project-charter-generator, stakeholder-analysis, etc.)
        - Requirements Gathering (business-requirements-capture, etc.)
        - Project Artifacts (raci-matrix-generator, communication-plan, etc.)
        - Status Tracking (status-report-generator, milestone-tracker, etc.)

        When a user asks for help, select the appropriate skill(s) and invoke them.
        """
```

Tasks:
- [ ] Implement `RiskAgentClient` class with Skills Framework integration
- [ ] Configure Claude Agent SDK authentication
- [ ] Set up system prompts that reference .claude/skills/ structure
- [ ] Implement permission management for skills access
- [ ] Add error handling and logging

#### 2.2 Claude Skills Framework Implementation
**Key Concept**: Skills use **progressive disclosure** - metadata → instructions → resources → code

**Structure**: Each skill is a directory with `SKILL.md` + optional subdirectories

**Example Skill Structure**:
```
.claude/skills/change-agent/meeting-minutes-capture/
├── SKILL.md                    # Skill definition with YAML frontmatter
├── /instructions               # Step-by-step instructions (loaded on demand)
│   ├── capture.md             # How to capture minutes from text
│   └── extract-actions.md     # How to extract action items
├── /resources                  # Reference materials (loaded on demand)
│   ├── meeting-template.md    # Standard meeting template
│   └── examples.md            # Example outputs
└── /code (optional)            # Helper scripts (loaded on demand)
    └── parser.py              # Optional Python helper
```

**SKILL.md Format** (with YAML frontmatter):
```markdown
---
name: meeting-minutes-capture
description: Capture meeting minutes from transcripts or notes and extract structured action items, decisions, and next steps
domain: change-agent
category: meeting-management
taxonomy: change-agent/meeting-management  # Simplified taxonomy
parameters:
  - meeting_transcript (required)
  - meeting_date (optional)
  - attendees (optional)
output_format: structured_markdown
estimated_duration: "2-3 minutes"
---

# Meeting Minutes Capture Skill

## Purpose
Transform unstructured meeting notes or transcripts into structured meeting minutes with clear action items, decisions, and next steps.

## When to Use This Skill
- After a meeting when you have raw notes or transcript
- When you need to formalize ad-hoc discussion notes
- When extracting action items from voice recordings

## Instructions
For detailed instructions, see:
- `instructions/capture.md` - How to capture minutes from different formats
- `instructions/extract-actions.md` - How to extract and assign action items

## Resources
- `resources/meeting-template.md` - Standard output template
- `resources/examples.md` - Example transformations

## Expected Output
Structured markdown document with:
- Meeting metadata (date, attendees, duration)
- Key discussion points
- Decisions made
- Action items (with owners and due dates)
- Next meeting details
```

**File: `backend/agent/skills_loader.py`**
```python
from pathlib import Path
from typing import Dict, List
import yaml
from dataclasses import dataclass

@dataclass
class SkillMetadata:
    """Skill metadata from YAML frontmatter"""
    name: str
    description: str
    domain: str
    category: str
    taxonomy: str
    parameters: List[str]
    output_format: str
    estimated_duration: str
    skill_path: Path

class SkillsLoader:
    """Progressive disclosure skill loader"""

    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self._skill_cache: Dict[str, SkillMetadata] = {}

    def load_skill_metadata(self, skill_name: str) -> SkillMetadata:
        """Load only YAML frontmatter (progressive disclosure step 1)"""
        skill_path = self.skills_dir / skill_name
        skill_file = skill_path / "SKILL.md"

        # Parse YAML frontmatter
        with open(skill_file) as f:
            content = f.read()
            if content.startswith('---'):
                yaml_content = content.split('---')[1]
                metadata = yaml.safe_load(yaml_content)

                return SkillMetadata(
                    name=metadata['name'],
                    description=metadata['description'],
                    domain=metadata['domain'],
                    category=metadata['category'],
                    taxonomy=metadata['taxonomy'],
                    parameters=metadata['parameters'],
                    output_format=metadata['output_format'],
                    estimated_duration=metadata['estimated_duration'],
                    skill_path=skill_path
                )

    def load_skill_instructions(self, skill_name: str, instruction_file: str) -> str:
        """Load specific instruction file (progressive disclosure step 2)"""
        skill_meta = self.load_skill_metadata(skill_name)
        instruction_path = skill_meta.skill_path / "instructions" / instruction_file

        with open(instruction_path) as f:
            return f.read()

    def load_skill_resources(self, skill_name: str, resource_file: str) -> str:
        """Load specific resource file (progressive disclosure step 3)"""
        skill_meta = self.load_skill_metadata(skill_name)
        resource_path = skill_meta.skill_path / "resources" / resource_file

        with open(resource_path) as f:
            return f.read()

    def list_skills(self, domain: str = None) -> List[SkillMetadata]:
        """List all skills (metadata only) optionally filtered by domain"""
        skills = []

        # Scan .claude/skills directory
        for domain_dir in self.skills_dir.iterdir():
            if domain and domain_dir.name != domain:
                continue

            for skill_dir in domain_dir.iterdir():
                if (skill_dir / "SKILL.md").exists():
                    skills.append(self.load_skill_metadata(
                        f"{domain_dir.name}/{skill_dir.name}"
                    ))

        return skills
```

Tasks:
- [ ] Create `.claude/skills/` directory structure
- [ ] Implement `SkillsLoader` with progressive disclosure
- [ ] Create **First Skill**: meeting-minutes-capture (complete structure)
  - [ ] SKILL.md with YAML frontmatter
  - [ ] instructions/capture.md
  - [ ] instructions/extract-actions.md
  - [ ] resources/meeting-template.md
  - [ ] resources/examples.md
- [ ] Create remaining Change Agent skills (10-15 total):
  - [ ] **Meeting Management** (3 skills):
    - meeting-minutes-capture
    - action-item-tracking
    - follow-up-generator
  - [ ] **Project Setup** (3 skills):
    - project-charter-generator
    - stakeholder-analysis
    - project-plan-template
  - [ ] **Requirements Gathering** (3 skills):
    - business-requirements-capture
    - requirement-validation
    - use-case-generator
  - [ ] **Project Artifacts** (3 skills):
    - raci-matrix-generator
    - communication-plan
    - risk-register-setup
  - [ ] **Status Tracking** (3 skills):
    - status-report-generator
    - milestone-tracker
    - issue-log-manager
- [ ] Add skill validation (check YAML frontmatter format)
- [ ] Create skills registry endpoint

**FUTURE PHASES: Other Risk Domains**
- [ ] Credit Risk (15 skills) - Phase 2
- [ ] Market Risk (18 skills) - Phase 2
- [ ] Operational Risk (12 skills) - Phase 2
- [ ] Other domains - Phase 3+

#### 2.3 Knowledge Layer (Simplified Taxonomy)
**File: `backend/knowledge/taxonomy/structure.md`**

Simple taxonomy for organizing documentation and knowledge:

```markdown
# Risk Agents Knowledge Taxonomy (Simplified)

## Change Agent Domain
- Meeting Management
- Project Setup
- Requirements Gathering
- Project Artifacts
- Status Tracking

## Risk Domains (Future)
- Credit Risk
- Market Risk
- Operational Risk
- Liquidity Risk
- Model Risk
- Climate Risk
- Regulatory Risk
- Strategic Risk

## Cross-Domain
- Reporting
- Communication
- Data Analysis
```

**Directory Structure**:
```
knowledge/
├── taxonomy/
│   └── structure.md                    # Simple taxonomy reference
├── change-agent/
│   ├── meeting-management/
│   │   ├── best-practices.md
│   │   └── meeting-types.md
│   ├── project-management/
│   │   ├── methodologies.md
│   │   └── project-phases.md
│   └── requirements-gathering/
│       └── techniques.md
└── README.md                          # Knowledge organization guide
```

Tasks:
- [ ] Create `knowledge/` directory structure
- [ ] Create simple taxonomy reference (structure.md)
- [ ] Add 3-5 knowledge documents for Change Agent domain
- [ ] Organize by category (meeting-management, project-management, etc.)
- [ ] Create README explaining organization

#### 2.4 Context Management
**File: `backend/agent/context_manager.py`**

Simplified context management for this phase:

```python
class ContextManager:
    """Manage session context and captured information"""

    def __init__(self, context_dir: Path):
        self.context_dir = context_dir
        self.sessions = {}

    def capture(self, session_id: str, data: Dict[str, Any]) -> None:
        """Store captured information for a session"""
        session_path = self.context_dir / "captured" / f"{session_id}.json"
        with open(session_path, 'w') as f:
            json.dump(data, f, indent=2)

    def get_context(self, session_id: str) -> Dict[str, Any]:
        """Retrieve context for a session"""
        session_path = self.context_dir / "captured" / f"{session_id}.json"
        if session_path.exists():
            with open(session_path) as f:
                return json.load(f)
        return {}
```

Tasks:
- [ ] Implement basic `ContextManager` class
- [ ] Create context storage directories
- [ ] Add session-based context retrieval
- [ ] Simple file-based storage (JSON)

---

### Phase 3: Backend API (FastAPI Server) (Week 3-4)

#### 3.1 FastAPI Server Setup
**File: `backend/api/api_server.py`**

- [ ] Create FastAPI application
- [ ] Configure CORS (allow frontend origin)
- [ ] Add middleware (logging, timing)
- [ ] Set up error handlers
- [ ] Create health check endpoint

#### 3.2 Authentication System
**File: `backend/api/auth.py`**

- [ ] Implement JWT token validation
- [ ] Create authentication dependency
- [ ] Add user session management
- [ ] Implement rate limiting
- [ ] Add API key support (optional)

#### 3.3 Query API
**File: `backend/api/routes/query.py`**

Endpoints:
- [ ] `POST /api/query` - Natural language query
  - Accepts: `{ "query": "string", "context": {} }`
  - Returns: Streamed response
- [ ] `GET /api/query/history` - Query history
- [ ] `GET /api/query/{id}` - Get specific query result

#### 3.4 Skills API
**File: `backend/api/routes/skills.py`**

Endpoints:
- [ ] `GET /api/skills` - List all skills (metadata only - progressive disclosure)
- [ ] `GET /api/skills/{domain}` - Skills by domain
- [ ] `GET /api/skills/{skill_id}` - Skill details (full SKILL.md content)
- [ ] `GET /api/skills/{skill_id}/instructions/{file}` - Load specific instruction file
- [ ] `GET /api/skills/{skill_id}/resources/{file}` - Load specific resource file
- [ ] `POST /api/skills/{skill_id}/execute` - Execute a skill with parameters

#### 3.5 Knowledge API
**File: `backend/api/routes/knowledge.py`**

Endpoints:
- [ ] `GET /api/knowledge/taxonomy` - Get taxonomy structure
- [ ] `GET /api/knowledge/{category}` - List documents in category
- [ ] `GET /api/knowledge/{category}/{document}` - Get specific document
- [ ] `POST /api/knowledge/search` - Search knowledge base

#### 3.6 WebSocket Handler
**File: `backend/api/websocket_handler.py`**

- [ ] Create WebSocket endpoint `/ws`
- [ ] Implement streaming response handler
- [ ] Add connection management
- [ ] Handle disconnections gracefully
- [ ] Implement message buffering

---

### Phase 4: Frontend Core (Next.js + Authentication) (Week 4-5)

**Note**: Phase 4 has been restructured into detailed modules for better learning progression:
- **Module 4.1: Design System Implementation** (Foundation - establishes design tokens FIRST)
- Module 4.2: Enhanced API Client
- Module 4.3: Authentication UI
- Module 4.4: WebSocket Client
- Module 4.5: Base Components
- Module 4.6: State Management & Integration

See `docs/module-4-progress.md` for detailed progress tracking.

**Important**: Module 4.1 (Design System) comes FIRST because design systems should always be established before building UI components. This is the correct, professional approach - define your visual language, then use it to build components.

---

#### 4.1 Design System Implementation (Module 4.1)
**Status**: ✅ COMPLETE (Oct 26, 2025)
**Documentation**: `docs/module-4-step-4.1-design-system.md`

**Files Modified** (11 files):
- [x] `frontend/tailwind.config.ts` - Custom design tokens
- [x] `frontend/app/globals.css` - 259 lines of custom CSS utilities
- [x] `frontend/app/layout.tsx` - Dark body background
- [x] `frontend/app/page.tsx` - Glass navigation, card lift effects
- [x] `frontend/app/(auth)/layout.tsx` - Dark theme with circuit pattern
- [x] `frontend/app/(auth)/login/page.tsx` - Dark theme text colors
- [x] `frontend/app/(auth)/register/page.tsx` - Dark theme text colors
- [x] `frontend/components/auth/LoginForm.tsx` - Dark inputs, gradient buttons
- [x] `frontend/components/auth/RegisterForm.tsx` - Dark inputs, gradient buttons
- [x] `frontend/components/auth/UserProfile.tsx` - Dark theme, LED indicators
- [x] `frontend/app/dashboard/page.tsx` - Card lift effects, LED status

**Implemented**:
- [x] Unified dark slate theme across all pages
- [x] Circuit pattern backgrounds
- [x] Glass morphism navigation
- [x] Card lift hover animations
- [x] LED status indicators with blink animation
- [x] Custom typography scale (hero, section, card)
- [x] Gradient buttons and text effects
- [x] Terminal-style components
- [x] Badge components (AI, Retro, Circuit)
- [x] Custom shadows and glow effects

---

#### 4.2 Enhanced API Client (Module 4.2)
**Status**: ✅ COMPLETE (Oct 25, 2025)
**Documentation**: `docs/module-4-step-4.2-enhanced-api-client.md`

**Files Created**:
- [x] `frontend/lib/api.ts` - Enhanced with health check methods
- [x] `frontend/app/api-test/page.tsx` - API test page

**Implemented**:
- [x] TypeScript interfaces for all backend responses
- [x] Health check methods for all services
- [x] Environment-based configuration
- [x] Error handling and logging

---

#### 4.3 Authentication UI (Module 4.3)
**Status**: ✅ COMPLETE (Oct 26, 2025)
**Documentation**: `docs/module-4-step-4.3-authentication-ui.md`

**Files Created**:
- [x] `frontend/lib/auth/types.ts` - Auth TypeScript types
- [x] `frontend/lib/auth/session.ts` - JWT token storage & management
- [x] `frontend/lib/auth/middleware.ts` - Protected route hooks
- [x] `frontend/components/auth/LoginForm.tsx` - Login form
- [x] `frontend/components/auth/RegisterForm.tsx` - Register form with password strength
- [x] `frontend/components/auth/UserProfile.tsx` - User profile component
- [x] `frontend/app/(auth)/layout.tsx` - Auth layout
- [x] `frontend/app/(auth)/login/page.tsx` - Login page
- [x] `frontend/app/(auth)/register/page.tsx` - Register page
- [x] `frontend/app/dashboard/page.tsx` - Protected dashboard

**Files Modified**:
- [x] `frontend/lib/api.ts` - Added authentication methods

**Implemented**:
- [x] JWT token management with localStorage
- [x] Session persistence across page reloads
- [x] Protected route middleware
- [x] Password strength indicator (4 levels)
- [x] Login/logout flow with auto-redirect
- [x] All UI styled with design system from Module 4.1

---

#### 4.4 WebSocket Client (Module 4.4)
**Status**: ✅ COMPLETE (Oct 26, 2025)
**Documentation**: `docs/module-4-step-4.4-websocket-client.md`

**Files Created**:
- [x] `frontend/lib/websocket/client.ts` - WebSocket manager class
- [x] `frontend/lib/websocket/types.ts` - Message type definitions
- [x] `frontend/lib/websocket/hooks.ts` - React hooks
- [x] `frontend/components/websocket/ConnectionStatus.tsx` - Status indicator
- [x] `frontend/app/websocket-test/page.tsx` - Test page

**Implemented**:
- [x] WebSocket connection manager with reconnection logic
- [x] Exponential backoff (1s → 30s)
- [x] Message queue for offline resilience
- [x] Ping/pong keepalive (30s interval)
- [x] Event-driven message handling (8 event types)

---

#### 4.5 UI Component Library (Module 4.5)
**Status**: ✅ COMPLETE (Oct 26, 2025)
**Documentation**: `docs/module-4-step-4.5-base-components.md`

**Files Created**:
- [x] `frontend/components/ui/Button.tsx` - 6 variants, 3 sizes
- [x] `frontend/components/ui/Input.tsx` - Validation states
- [x] `frontend/components/ui/Card.tsx` - 5 variants
- [x] `frontend/components/ui/Loading.tsx` - Spinner, Skeleton, ProgressBar
- [x] `frontend/components/ui/Toast.tsx` - Toast notification system
- [x] `frontend/components/ui/Layout.tsx` - Header, Sidebar, Footer, etc.
- [x] `frontend/lib/utils.ts` - Utility functions

**Implemented**:
- [x] 30+ reusable UI components (~2,070 lines)
- [x] Full design system integration
- [x] Accessibility features (ARIA, semantic HTML)
- [x] Responsive design (mobile-first)

---

#### 4.6 State Management & Integration (Module 4.6)
**Status**: ✅ COMPLETE (Oct 26, 2025)
**Documentation**: `docs/module-4-step-4.6-state-management-integration.md`

**Files Created**:
- [x] `frontend/contexts/SessionContext.tsx` - Authentication state
- [x] `frontend/contexts/WebSocketContext.tsx` - WebSocket management
- [x] `frontend/components/ErrorBoundary.tsx` - Error boundary
- [x] `frontend/lib/errors.ts` - Error utilities
- [x] `frontend/app/components-showcase/page.tsx` - Component showcase
- [x] `frontend/app/layout.tsx` - Updated with all contexts

**Implemented**:
- [x] Global authentication state (SessionContext)
- [x] Centralized WebSocket management (WebSocketContext)
- [x] Error handling with custom error classes
- [x] HOCs for route protection (withAuth, withGuest)
- [x] Component showcase page at /components-showcase

---

### Phase 5: Frontend Features (Dashboard & Chat) (Week 5-6)

#### 5.1 Dashboard Page
**File: `frontend/app/dashboard/page.tsx`**

Components:
- [ ] Metrics widgets:
  - Total queries executed
  - Skills used
  - Patterns run
  - Success rate
- [ ] Recent queries list
- [ ] Quick actions (Run pattern, Execute skill)
- [ ] Domain activity chart

#### 5.2 Chat Interface (Natural Language Query)
**Status**: ✅ COMPLETE (Oct 26, 2025)
**Documentation**: `docs/module-5.2-chat-interface.md`

**Files Created** (5 files):
- [x] `frontend/components/chat/ChatInterface.tsx` - Main container (~180 lines)
- [x] `frontend/components/chat/MessageList.tsx` - Scrollable message list (~70 lines)
- [x] `frontend/components/chat/QueryInput.tsx` - Text input with submit (~130 lines)
- [x] `frontend/components/chat/Message.tsx` - Individual message component (~120 lines)
- [x] `frontend/app/chat/page.tsx` - Chat page route (~70 lines)

**Implemented Features**:
- [x] Real-time response streaming via WebSocketContext
- [x] Message history with user/assistant/system roles
- [x] Auto-scroll to latest message
- [x] Clear chat history
- [x] Typing indicators during streaming
- [x] Character count with 4000 char limit
- [x] Keyboard shortcuts (Enter to send, Shift+Enter for new line)
- [x] Connection status indicator
- [x] Error handling and display

**Deferred to Future** (not blocking MVP):
- [ ] Markdown rendering for responses (react-markdown)
- [ ] Copy responses to clipboard
- [ ] Message persistence (localStorage)
- [ ] Message editing and regeneration

#### 5.3 Skills Browser
**File: `frontend/app/skills/page.tsx`**

Components:
- [ ] `SkillGrid.tsx` - Grid of all skills
- [ ] `SkillCard.tsx` - Individual skill display
- [ ] `DomainFilter.tsx` - Filter by domain
- [ ] `SkillDetails.tsx` - Detailed view with execution

Features:
- [ ] Browse 100+ skills
- [ ] Filter by domain (9 domains)
- [ ] Search skills
- [ ] View skill details (description, parameters, success rate)
- [ ] Execute individual skills
- [ ] Favorite skills

#### 5.4 Knowledge Browser
**File: `frontend/app/knowledge/page.tsx`**

Components:
- [ ] `KnowledgeTree.tsx` - Taxonomy-based tree navigation
- [ ] `DocumentCard.tsx` - Document preview cards
- [ ] `TaxonomyBrowser.tsx` - Browse by category
- [ ] `SearchBar.tsx` - Search knowledge base

Features:
- [ ] Browse knowledge organized by simplified taxonomy
- [ ] Filter by category (meeting-management, project-management, etc.)
- [ ] View document content
- [ ] Search across knowledge base
- [ ] Link documents to relevant skills

---

### Phase 6: Context Management (3 C's Interface) (Week 7)

#### 6.1 Context Management Page
**File: `frontend/app/context/page.tsx`**

Features:
- [ ] **Capture Tab**:
  - Upload documents
  - Parse meeting notes
  - Import from APIs
  - Voice-to-text capture
- [ ] **Curate Tab**:
  - View captured data
  - Categorize by risk taxonomy
  - Enrich data
  - Validate information
- [ ] **Consult Tab**:
  - Search curated knowledge
  - View context used in queries
  - Context usage analytics

---

### Phase 7: Advanced Features (Week 8-9)

#### 7.1 Skills Enhancement
- [ ] Track skill usage analytics
- [ ] Add skill favoriting/bookmarking
- [ ] Create skill execution history
- [ ] Add skill performance metrics

#### 7.2 Knowledge Enhancement
- [ ] Knowledge graph visualization
- [ ] Related documents suggestions
- [ ] Knowledge contribution workflow
- [ ] Document versioning

#### 7.3 Collaborative Features
- [ ] Share queries with team
- [ ] Share skills outputs
- [ ] Commenting on results
- [ ] Team workspace

#### 7.4 Reporting & Export
- [ ] Generate PDF reports
- [ ] Export to Excel
- [ ] Export skill outputs to various formats
- [ ] Email integration for sharing

#### 7.5 Admin Features
- [ ] User management
- [ ] Usage analytics
- [ ] System configuration
- [ ] API key management

---

### Phase 8: Testing & Deployment (Week 10)

#### 8.1 Testing
- [ ] Backend unit tests (pytest)
- [ ] Frontend unit tests (Jest)
- [ ] Integration tests
- [ ] E2E tests (Playwright)
- [ ] Load testing

#### 8.2 Docker Production Optimization
- [ ] Optimize backend Dockerfile (multi-stage build)
- [ ] Optimize frontend Dockerfile (multi-stage build)
- [ ] Configure docker-compose.prod.yml
- [ ] Set up health checks in Docker containers
- [ ] Configure resource limits (CPU/memory)
- [ ] Create production environment variables

**Optimized Production Dockerfile (Backend):**
```dockerfile
FROM python:3.11-slim as builder

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY backend/ .

ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "api.api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Optimized Production Dockerfile (Frontend):**
```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci --only=production

FROM node:20-alpine AS builder
WORKDIR /app
COPY frontend/ .
COPY --from=deps /app/node_modules ./node_modules
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s \
  CMD node healthcheck.js || exit 1

CMD ["node", "server.js"]
```

#### 8.3 CI/CD Pipeline Setup
**File: `.github/workflows/deploy.yml`**
```yaml
name: Deploy Risk Agents App

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to Docker Registry
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push Backend
        uses: docker/build-push-action@v4
        with:
          context: .
          file: ./docker/backend.Dockerfile
          push: true
          tags: your-registry/risk-agents-backend:latest

      - name: Build and push Frontend
        uses: docker/build-push-action@v4
        with:
          context: .
          file: ./docker/frontend.Dockerfile
          push: true
          tags: your-registry/risk-agents-frontend:latest

      - name: Deploy to Server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            cd /opt/risk-agents
            docker-compose -f docker-compose.prod.yml pull
            docker-compose -f docker-compose.prod.yml up -d
            docker system prune -f
```

Tasks:
- [ ] Create optimized Dockerfiles for production
- [ ] Set up Docker Registry (Docker Hub or GitHub Container Registry)
- [ ] Configure GitHub Actions workflow
- [ ] Set up deployment secrets
- [ ] Test CI/CD pipeline

#### 8.4 Production Deployment Options

**Option 1: Self-Hosted VPS (Recommended for Docker)**
- [ ] Set up VPS (DigitalOcean, Linode, or AWS EC2)
- [ ] Install Docker and Docker Compose
- [ ] Configure firewall (ports 80, 443, 3000, 8000)
- [ ] Set up Nginx reverse proxy
- [ ] Configure SSL with Let's Encrypt
- [ ] Deploy using `docker-compose.prod.yml`

**Option 2: Cloud Platform (Railway/Render)**
- [ ] Connect GitHub repository
- [ ] Configure build settings (use Dockerfiles)
- [ ] Set environment variables
- [ ] Configure custom domain

**Option 3: AWS ECS/Fargate**
- [ ] Create ECS cluster
- [ ] Define task definitions (backend + frontend containers)
- [ ] Set up Application Load Balancer
- [ ] Configure auto-scaling
- [ ] Set up CloudWatch monitoring

Tasks:
- [ ] Choose deployment option
- [ ] Set up server infrastructure
- [ ] Configure domain (app.risk-agents.com)
- [ ] Set up SSL certificates
- [ ] Deploy containers to production
- [ ] Configure monitoring (Sentry)
- [ ] Set up logging (CloudWatch or self-hosted)
- [ ] Test production deployment

#### 8.4 Documentation
- [ ] User guide
- [ ] API documentation
- [ ] Deployment guide
- [ ] Skills & Patterns documentation

---

## Technology Stack Summary

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **AI Engine**: Claude Agent SDK (Anthropic)
- **Authentication**: JWT (python-jose)
- **WebSockets**: FastAPI WebSockets
- **Data Format**: YAML (skills/patterns definitions)
- **Monitoring**: Sentry (optional)

### Frontend
- **Framework**: Next.js 15
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: NextAuth.js
- **State Management**: React Context / SWR
- **WebSocket**: socket.io-client
- **UI Components**: Custom (based on marketing site design)

### Deployment
- **Containerization**: Docker + Docker Compose
- **Container Registry**: Docker Hub / GitHub Container Registry
- **Backend Hosting**: VPS (DigitalOcean, Linode) / Railway / AWS ECS
- **Frontend Hosting**: Same container infrastructure (not Vercel)
- **Reverse Proxy**: Nginx (for SSL termination)
- **Database**: PostgreSQL (optional, for user data)
- **File Storage**: Docker volumes / S3 (for context storage)
- **CI/CD**: GitHub Actions with Docker builds

---

## Docker Architecture Benefits

### Why Docker for Risk Agents?

1. **Consistent Development Environment**
   - Everyone runs the same Python version, Node version, dependencies
   - No "works on my machine" problems
   - New developers can start with `docker-compose up`

2. **Simplified Deployment**
   - Same containers run in development and production
   - No manual server setup or dependency installation
   - Easy rollback (just redeploy previous container version)

3. **Resource Isolation**
   - Backend and frontend run in separate containers
   - Easy to scale (run multiple backend containers)
   - Clear resource limits (CPU/memory per container)

4. **Development Productivity**
   - Hot reload works in both containers
   - Volume mounts for instant code updates
   - Easy to add new services (database, Redis, etc.)

5. **Cole Medin Pattern Compatible**
   - Claude Agent SDK runs perfectly in Docker
   - Python environment isolated and reproducible
   - Easy to manage Python dependencies

### Docker Best Practices for This Project

- **Multi-stage builds** for smaller production images
- **Volume mounts** for development (code changes reflect immediately)
- **Named volumes** for persistent data (skills, patterns, context)
- **Health checks** for container monitoring
- **Resource limits** to prevent memory/CPU issues
- **Docker networks** for container communication
- **Environment variables** for configuration
- **.dockerignore** to exclude unnecessary files

---

## Key Design Decisions

### 1. Docker-First Architecture
All development and deployment happens in Docker containers. This ensures:
- Consistent Python 3.11 environment for Claude Agent SDK
- Consistent Node 20 environment for Next.js
- Easy local development (`docker-compose up`)
- Production deployment is just running the same containers

### 2. Modular Backend (Cole Medin Pattern)
Following Cole's approach of using Claude Agent SDK as the core intelligence with different interfaces connecting to it. This allows:
- Easy addition of new interfaces (mobile app, Slack bot, etc.)
- Centralized AI logic
- Consistent behavior across interfaces

### 2. Real-Time Streaming
Using WebSocket for streaming responses provides:
- Better UX (see responses as they're generated)
- Lower perceived latency
- Ability to show tool usage in real-time

### 3. Claude Skills Framework Architecture (Progressive Disclosure)
- **Skills**: Modular capabilities with SKILL.md + instructions + resources
- **Progressive Disclosure**: Load metadata → instructions → resources as needed
- **Taxonomy Organization**: Simple category-based knowledge organization
- **Evolution**: Skills can be enhanced based on usage patterns (Phase 2)

### 4. Simplified Context Management
- **Session-based context**: Simple file-based storage for chat sessions
- **Context injection**: Add relevant context to skill executions
- *(Full 3 C's implementation deferred to Phase 2)*

### 5. Separation of Concerns
- Backend: AI logic, skills framework, knowledge layer, context
- Frontend: UI, authentication, API client
- Clear API boundaries for scalability

---

## Deferred to Phase 2 (Post-MVP)

The following architectural components from the full architecture document will be implemented in Phase 2:

1. **Fabrix Pattern System**
   - Composable workflows (combining multiple skills)
   - Pattern evolution and tracking
   - Pattern recommendation engine

2. **GTD Horizons Integration**
   - Organizational goal alignment
   - Horizon-tagged skills and outputs
   - Goal progress tracking

3. **Natural Language Query Engine**
   - Advanced query parsing
   - Pattern matching
   - <10 second response optimization

4. **Full 3 C's Context Management**
   - Document parsing and capture
   - Rich curation with validation
   - Advanced context retrieval

5. **Additional Risk Domains**
   - Credit Risk, Market Risk, Operational Risk, etc.
   - Full 100+ skills across 9 domains

---

## Success Metrics (Hybrid Approach)

### Phase 1-2 (Weeks 1-3) - Foundation + Skills Framework
- [ ] Docker containers running (backend + frontend)
- [ ] Backend server running with Claude Agent SDK
- [ ] Skills Framework structure in `.claude/skills/` directory
- [ ] First skill (meeting-minutes-capture) fully implemented with progressive disclosure
- [ ] Can execute skills via API
- [ ] Knowledge layer structure created with simple taxonomy

### Phase 3-4 (Weeks 3-5) - API + Frontend Core
- [ ] Complete FastAPI with skills and knowledge endpoints
- [ ] Frontend authentication working
- [ ] API client with WebSocket support implemented
- [ ] Chat interface with streaming responses working

### Phase 5-6 (Weeks 5-7) - Features + Knowledge
- [ ] Dashboard displaying skill usage metrics
- [ ] Skills browser with all Change Agent skills
- [ ] Knowledge browser with taxonomy navigation
- [ ] 10-15 Change Agent skills fully implemented
- [ ] 3-5 knowledge documents organized by taxonomy

### Phase 7-8 (Weeks 7-10) - Polish + Deployment
- [ ] Context management implemented (session-based)
- [ ] All UI features polished
- [ ] Tests written and passing
- [ ] Deployed to production
- [ ] Documentation complete

### MVP Success Criteria
- ✅ Proper Claude Skills Framework implementation (not just YAML files)
- ✅ Progressive disclosure working (metadata → instructions → resources)
- ✅ 10-15 working Change Agent skills
- ✅ Knowledge layer with simplified taxonomy
- ✅ Chat interface that invokes skills correctly
- ✅ Deployed and accessible app

---

## Next Steps

### Immediate Actions:
1. **Create project directory structure** (backend/, frontend/, docker/)
2. **Set up Docker infrastructure** (Dockerfiles, docker-compose.yml)
3. **Initialize Python backend** (requirements.txt, basic FastAPI server)
4. **Initialize Next.js frontend** (TypeScript, Tailwind CSS)
5. **Test Docker containers** (`docker-compose up` should work)
6. **Install Claude Agent SDK** in backend container
7. **Create first skills definitions** (5-10 to start)
8. **Build minimal FastAPI server** with health check endpoint
9. **Test end-to-end** (frontend → backend → Claude Agent SDK)

### First Milestone (Week 2):
- ✅ Docker containers running for both backend and frontend
- ✅ Backend accessible at http://localhost:8000
- ✅ Frontend accessible at http://localhost:3000
- ✅ Python backend with Claude Agent SDK installed
- ✅ Basic FastAPI server with health check
- ✅ 5-10 sample skills loaded from YAML
- ✅ Simple query endpoint that returns results
- ✅ Hot reload working in both containers

### Development Workflow:
```bash
# Start development environment
docker-compose up

# Access the app
# Frontend: http://localhost:3050
# Backend API: http://localhost:8050
# API Docs: http://localhost:8050/docs

# Make code changes → automatically reloaded in containers
# No need to restart Docker unless dependencies change

# Stop development environment
docker-compose down
```

---

## Step-by-Step Learning Approach

### Teaching Philosophy
This project will be built **incrementally** with you learning each concept before moving to the next. Each step will include:
1. **Explanation**: What we're building and why
2. **Code Walkthrough**: Line-by-line explanation of new code
3. **Hands-on Practice**: You'll create/modify files yourself
4. **Testing**: Verify each step works before continuing
5. **Debugging Together**: If something doesn't work, we'll fix it together

### Learning Modules

#### Module 1: Foundation Setup (Week 1)
**Goal**: Get Docker containers running with minimal backend and frontend

**Step 1.1: Project Structure**
- Create directory structure together
- Understand why each folder exists
- Learn about separation of concerns

**Step 1.2: Docker Basics**
- What is Docker and why use it?
- Understanding Dockerfiles (line by line)
- Understanding docker-compose.yml
- Running your first container

**Step 1.3: Backend Basics (Python + FastAPI)**
- What is FastAPI and why we chose it
- Creating a simple "Hello World" API
- Understanding async/await in Python
- Testing with `http://localhost:8050`

**Step 1.4: Frontend Basics (Next.js)**
- What is Next.js App Router
- Creating a simple page
- Understanding React components
- Testing with `http://localhost:3050`

**Deliverable**: Both containers running, can see "Hello World" on both

---

#### Module 2: UV and Python Dependencies (Week 1-2)
**Goal**: Understand modern Python dependency management

**Step 2.1: What is UV?**
- Why UV instead of pip/poetry
- How UV manages dependencies
- Understanding pyproject.toml and uv.lock

**Step 2.2: Installing Dependencies**
- Adding Claude Agent SDK
- Adding FastAPI dependencies
- Understanding how Docker caches dependencies

**Step 2.3: Running Python in Docker**
- Using `uv run` vs regular Python
- Debugging Python errors in container
- Viewing container logs

**Deliverable**: FastAPI running with all dependencies installed

---

#### Module 3: Claude Agent SDK Integration (Week 2)
**Goal**: Make your first Claude API call

**Step 3.1: Understanding the Claude Agent SDK**
- What is the Claude Agent SDK?
- How does it differ from Claude API?
- Cole Medin's pattern explained

**Step 3.2: Authentication**
- Setting up Anthropic API key
- Environment variables in Docker
- Security best practices

**Step 3.3: First Query**
- Create simple endpoint `/api/query`
- Send a prompt to Claude
- Get a response back
- Display in browser

**Deliverable**: Working endpoint that responds to queries via Claude

---

#### Module 4: Building Your First Skill (Week 2-3)
**Goal**: Create "meeting-minutes-capture" skill

**Step 4.1: Understanding Skills**
- What makes a skill?
- YAML schema explained
- How skills are loaded

**Step 4.2: Creating the Skill**
- Write YAML definition for meeting-minutes-capture
- Create skill loader Python code
- Test skill loading

**Step 4.3: Executing the Skill**
- Add skill execution to agent_client.py
- Create API endpoint for skill execution
- Test with sample meeting transcript

**Deliverable**: Working skill that captures meeting minutes from text

---

#### Module 5: Building the Chat Interface (Week 3)
**Goal**: Create natural language query interface

**Step 5.1: React Components**
- Understanding React component structure
- Props and state explained
- Creating ChatInterface component

**Step 5.2: API Integration**
- Fetch API basics
- Calling backend from frontend
- Error handling

**Step 5.3: Real-time Streaming**
- What is WebSocket?
- Streaming responses from Claude
- Displaying streaming text in UI

**Deliverable**: Chat interface where you can ask questions and get responses

---

#### Module 6: Backend Skills + Frontend Integration (Week 3-4) ✅ COMPLETE
**Goal**: Build out Change Agent skills and connect to frontend
**Status**: ✅ Complete (October 26-27, 2025)
**Time**: ~10.25 hours

**Step 6.1: Skill Templates & Standards** ✅
- Created skill-development-guide.md (~800 lines)
- Created SKILL_TEMPLATE.md (~450 lines)
- Established YAML schema and development standards

**Step 6.2: Core Skills (5 skills)** ✅
- action-item-tracking
- project-charter-generator
- stakeholder-analysis
- raci-matrix-generator
- status-report-generator

**Step 6.3: Advanced Skills (4 skills)** ✅
- decision-log-generator
- risk-register-generator
- requirements-gathering-facilitator
- communication-plan-generator

**Step 6.4: Integration & Testing** ✅
- Backend API validation
- Skills execution testing
- Metrics tracking validation

**Step 6.5: Frontend-Backend Integration** ✅
- Enhanced API client (lib/api.ts) with 7 skills methods
- Created skills utilities library (lib/skills-utils.ts)
- Integrated Skills Browser with backend API
- Removed all mock data
- Added loading states and error handling
- Connected localStorage favorites persistence

**Deliverable**: 10 working Change Agent skills + fully integrated Skills Browser UI

---

#### Module 7: Knowledge Layer & Taxonomy (Week 4)
**Goal**: Organize knowledge with simplified taxonomy

**Step 7.1: Understanding the Knowledge Layer**
- Why organize knowledge?
- Simple taxonomy vs complex taxonomy
- How taxonomy supports skills

**Step 7.2: Creating Knowledge Documents**
- Meeting management best practices
- Project management methodologies
- Requirements gathering techniques

**Step 7.3: Taxonomy-Based Organization**
- Organizing by category
- Linking knowledge to skills
- Making knowledge discoverable

**Step 7.4: Knowledge Browser UI**
- Tree navigation component
- Document viewer
- Search functionality

**Deliverable**: Knowledge base with 3-5 documents organized by simplified taxonomy

---

#### Module 8: Context Management (3 C's) (Week 5)
**Goal**: Implement Capture, Curate, Consult

**Step 8.1: Capture**
- File upload functionality
- Parsing different formats
- Storing captured data

**Step 8.2: Curate**
- Structuring captured information
- Categorizing by project
- Validating data

**Step 8.3: Consult**
- Retrieving relevant context
- Injecting context into prompts
- Context-aware responses

**Deliverable**: Context system that remembers project information

---

#### Module 9: Frontend Polish (Week 5-6)
**Goal**: Build out full UI

**Step 9.1: Dashboard**
- Metrics widgets (skills used, queries made)
- Recent activity feed
- Quick actions (favorite skills)
- Usage statistics

**Step 9.2: Skills Browser**
- Grid layout with skill cards
- Domain filtering
- Skill details modal
- Skill execution interface

**Step 9.3: Knowledge Browser**
- Taxonomy tree navigation
- Document cards and viewers
- Search and filtering
- Related documents

**Step 9.4: Design System Consistency**
- Reuse marketing site design
- Consistent colors and typography
- Responsive layouts
- Loading and error states

**Deliverable**: Full-featured UI for Change Agent with polished design

---

#### Module 10: Deployment (Week 6)
**Goal**: Deploy to production

**Step 10.1: Docker Optimization**
- Multi-stage builds
- Image size reduction
- Security hardening

**Step 10.2: Choosing Deployment Platform**
- VPS vs Cloud Platform
- Cost considerations
- Setting up infrastructure

**Step 10.3: Going Live**
- Domain setup
- SSL certificates
- Monitoring

**Deliverable**: Live Risk Agents app at app.risk-agents.com

---

### Learning Resources Provided

For each module, I'll provide:
- **Concept explanations** in plain English
- **Code examples** with line-by-line comments
- **Common pitfalls** and how to avoid them
- **Debugging tips** when things don't work
- **Best practices** for production code
- **Further reading** if you want to go deeper

### Pacing (Updated for Hybrid Approach)

- **Fast Track**: 1 module per day (10-12 weeks total with proper Skills Framework)
- **Comfortable**: 1-2 modules per week (12 weeks total - **RECOMMENDED**)
- **Deep Learning**: Take your time, explore concepts (14-16 weeks)

**Recommended Timeline**: 12 weeks
- Proper Skills Framework implementation takes more time than simple YAML
- Learning progressive disclosure patterns is valuable
- Building knowledge layer adds 1-2 weeks
- Quality over speed - understanding the architecture is key

You set the pace. We can spend extra time on modules that interest you or move quickly through familiar concepts.

### Questions Throughout

At any point you can ask:
- "Explain this in more detail"
- "Why did we do it this way?"
- "What's an alternative approach?"
- "Can you show me more examples?"
- "Let's debug this together"

The goal is **understanding**, not just getting it working.

---

Would you like to proceed with **Module 1, Step 1.1: Creating the project directory structure**?

I'll walk you through creating each directory and file, explaining the purpose of each one as we go.
