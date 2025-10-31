# Risk Agents App

A standalone AI-powered project management application using Claude Agent SDK with Skills Framework architecture.

## Project Structure

```
risk-agents-app/
├── backend/                    # Python + FastAPI + Claude Agent SDK
│   ├── .claude/               # Claude Skills Framework (KEY INNOVATION)
│   │   └── skills/            # Skills with progressive disclosure
│   │       └── change-agent/  # Change Agent domain skills
│   ├── agent/                 # Claude Agent SDK integration
│   ├── api/                   # FastAPI server & routes
│   ├── knowledge/             # Knowledge Layer (simplified taxonomy)
│   └── context/               # Session context storage
│
├── frontend/                   # Next.js 15 + TypeScript
│   ├── app/                   # Next.js App Router pages
│   ├── components/            # React components
│   ├── lib/                   # API client, utilities
│   └── public/                # Static assets
│
├── docker/                     # Docker configuration
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
│
└── docker-compose.yml         # Docker Compose orchestration
```

## Architecture Approach: Hybrid (12 weeks)

**Phase 1 - MVP (Current):**
- ✅ Full Claude Skills Framework (progressive disclosure)
- ✅ Simplified Knowledge Taxonomy
- ✅ Change Agent domain (10-15 skills)

**Phase 2 - Post-MVP:**
- ⏸️ Fabrix Pattern System
- ⏸️ GTD Horizons Integration
- ⏸️ Natural Language Query Engine
- ⏸️ Additional Risk Domains

## Key Concepts

### Claude Skills Framework
Skills use **progressive disclosure** - only load what's needed:
1. **Metadata** (YAML frontmatter in SKILL.md) - loaded first
2. **Instructions** (instructions/*.md) - loaded on demand
3. **Resources** (resources/*.md) - loaded on demand
4. **Code** (code/*.py) - optional helpers

### Simplified Taxonomy
Knowledge organized by simple categories:
- Meeting Management
- Project Management
- Requirements Gathering
- Project Artifacts
- Status Tracking

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Git
- API key from Anthropic (for Claude)

### Quick Start

1. **Clone and setup**
   ```bash
   cd risk-agents-app
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

2. **Start with Docker**
   ```bash
   docker-compose up --build
   ```

3. **Access the app**
   - Frontend: http://localhost:3050
   - Backend API: http://localhost:8050
   - API Docs: http://localhost:8050/docs

## Development Workflow

```bash
# Start development environment
docker-compose up

# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# Rebuild after dependency changes
docker-compose up --build
```

**For more Docker commands**, see [DOCKER-GUIDE.md](DOCKER-GUIDE.md)

## Technology Stack

**Backend:**
- Python 3.11
- FastAPI (API server)
- Claude Agent SDK (AI engine)
- UV (package manager)

**Frontend:**
- Next.js 15 (App Router)
- TypeScript
- Tailwind CSS
- NextAuth.js (authentication)

**Deployment:**
- Docker + Docker Compose
- Containerized backend + frontend

## Learning Journey

This project follows a step-by-step learning approach. See [risk-agents-app-implementation-plan.md](../risk-agents-app-implementation-plan.md) for the complete 10-module learning path.

## Documentation

- [Implementation Plan](../risk-agents-app-implementation-plan.md) - Full 12-week plan
- [Architecture Document](../path/to/architecture.md) - Complete architecture overview
- [Module Documentation](docs/) - Step-by-step module guides
  - [Module 1, Step 1.1: Project Structure](docs/module-1-step-1.1-project-structure.md) ✅
  - [Module 1, Step 1.2: Docker Setup](docs/module-1-step-1.2-docker-setup.md) ✅
  - [Module 1, Step 1.3: Backend Setup](docs/module-1-step-1.3-backend-setup.md) ✅
  - [Module 1, Step 1.4: Frontend Setup](docs/module-1-step-1.4-frontend-setup.md) ✅
  - [Module 1, Step 1.5: Integration Testing](docs/module-1-step-1.5-integration-testing.md) ✅
- Backend API: http://localhost:8050/docs (when running)
- Frontend App: http://localhost:3050 (when running)

## Module 1 Status: COMPLETE! 🎉

All foundation infrastructure is in place and tested:
- ✅ Docker containerization working
- ✅ FastAPI backend with hot-reload
- ✅ Next.js 15 frontend with hot-reload
- ✅ Full stack integration verified
- ✅ Development workflow optimized

**Ready for Module 2: Claude Agent SDK + Skills Framework**

## License

Private project - All rights reserved
