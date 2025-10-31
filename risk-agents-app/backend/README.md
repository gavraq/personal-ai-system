# Risk Agents Backend

Python backend for Risk Agents using FastAPI and Claude Agent SDK.

## Technology Stack

- **Python 3.11** - Modern Python with type hints
- **FastAPI** - Modern, fast web framework for building APIs
- **UV** - Fast Python package manager (10-100x faster than pip)
- **Uvicorn** - ASGI server for running FastAPI
- **Claude Agent SDK** - Anthropic's AI agent framework (to be added)

## Project Structure

```
backend/
├── api/
│   ├── __init__.py
│   ├── api_server.py          # Main FastAPI application
│   └── routes/                # API endpoints (to be created)
│       ├── __init__.py
│       ├── query.py           # Chat/query endpoints
│       ├── skills.py          # Skills API
│       └── knowledge.py       # Knowledge API
│
├── agent/
│   ├── __init__.py
│   ├── agent_client.py        # Claude SDK wrapper (to be created)
│   ├── skills_loader.py       # Skills Framework loader (to be created)
│   └── context_manager.py     # Context management (to be created)
│
├── .claude/
│   └── skills/                # Claude Skills Framework
│       └── change-agent/      # Change Agent domain skills
│
├── knowledge/                 # Knowledge Layer
│   ├── taxonomy/              # Taxonomy structure
│   └── change-agent/          # Domain-specific knowledge
│
├── context/                   # Session context storage
│   ├── captured/              # Captured session data
│   └── templates/             # Context templates
│
├── pyproject.toml            # Python project configuration (UV)
└── README.md                 # This file
```

## Dependencies

### Core Dependencies
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `python-jose` - JWT tokens
- `pyyaml` - YAML parsing for skills
- `anthropic` - Claude SDK (to be added)

### Development Dependencies
- `pytest` - Testing framework
- `black` - Code formatter
- `ruff` - Fast linter
- `httpx` - HTTP client for testing

## Development

### Running Locally (with Docker)

```bash
# From project root
docker-compose up backend
```

The backend will be available at:
- API: http://localhost:8050
- Docs: http://localhost:8050/docs
- ReDoc: http://localhost:8050/redoc

### Running Without Docker

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run the server
uv run uvicorn api.api_server:app --host 0.0.0.0 --port 8050 --reload
```

### Adding Dependencies

```bash
# Inside Docker container
docker-compose exec backend uv add <package-name>

# Or locally
uv add <package-name>
```

### Running Tests

```bash
# Inside Docker container
docker-compose exec backend pytest

# Or locally
uv run pytest
```

## API Endpoints

### Current Endpoints

- `GET /` - API information
- `GET /health` - Health check (used by Docker)
- `GET /test` - Test endpoint
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

### Planned Endpoints

- `POST /api/query` - Natural language queries
- `GET /api/skills` - List all skills
- `GET /api/skills/{skill_id}` - Get skill details
- `POST /api/skills/{skill_id}/execute` - Execute a skill
- `GET /api/knowledge/taxonomy` - Get taxonomy structure
- `GET /api/knowledge/{category}` - List documents in category

## Configuration

Environment variables (from `.env` file):

- `ANTHROPIC_API_KEY` - Your Anthropic API key
- `JWT_SECRET` - Secret for JWT tokens
- `ENVIRONMENT` - `development` or `production`

## Skills Framework

Skills are located in `.claude/skills/` and follow progressive disclosure:

```
.claude/skills/change-agent/meeting-minutes-capture/
├── SKILL.md                    # Skill definition (YAML frontmatter)
├── instructions/               # Step-by-step instructions
├── resources/                  # Reference materials
└── code/                       # Optional helper scripts
```

See Module 2 documentation for creating skills.

## Knowledge Layer

Knowledge is organized by simplified taxonomy in `knowledge/`:

```
knowledge/
├── taxonomy/
│   └── structure.md           # Taxonomy reference
└── change-agent/
    ├── meeting-management/
    ├── project-management/
    └── requirements-gathering/
```

## Next Steps

1. Install Claude Agent SDK (`uv add anthropic`)
2. Create agent_client.py (Claude SDK wrapper)
3. Create skills_loader.py (Skills Framework loader)
4. Implement first skill (meeting-minutes-capture)
5. Create API endpoints for skills

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [UV Documentation](https://docs.astral.sh/uv/)
- [Claude SDK Documentation](https://docs.anthropic.com/)
- [Implementation Plan](../docs/) - Module documentation
