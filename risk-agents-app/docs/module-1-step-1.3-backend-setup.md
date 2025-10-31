# Module 1, Step 1.3: Python Backend Setup with UV

**Module**: Foundation Setup (Week 1)
**Goal**: Initialize Python backend with UV package manager and create minimal FastAPI server
**Status**: ✅ Complete
**Date**: 2025-10-21

---

## What We Built

We initialized the Python backend with UV package manager, configured project dependencies, and created a minimal FastAPI server with health check endpoint. The backend is now ready to run in Docker.

---

## Files Created

### Python Project Files

1. **backend/pyproject.toml** - Python project configuration (like package.json for Node.js)
2. **backend/api/api_server.py** - Main FastAPI application with health check
3. **backend/README.md** - Backend documentation
4. **.env** - Environment variables (generated from .env.example)

---

## Understanding Each File

### 1. Project Configuration (`backend/pyproject.toml`)

```toml
[project]
name = "risk-agents-backend"
version = "0.1.0"
description = "Risk Agents AI-powered project management backend"
requires-python = ">=3.11"

dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.0.0",
    "python-jose[cryptography]>=3.3.0",
    "python-multipart>=0.0.6",
    "pyyaml>=6.0",
    "anthropic>=0.34.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "httpx>=0.25.0",
]
```

**Key Concepts**:

- **`[project]` section** - Project metadata
- **`requires-python`** - Minimum Python version (3.11)
- **`dependencies`** - Required packages for running the app
- **`dev` dependencies** - Optional packages for development (testing, linting)

**Core Dependencies Explained**:

- **fastapi** - Modern web framework for building APIs
  - Fast (built on Starlette and Pydantic)
  - Auto-generates API documentation
  - Type hints for validation

- **uvicorn** - ASGI server to run FastAPI
  - Handles HTTP requests
  - Supports WebSocket for real-time streaming
  - `[standard]` includes extra features

- **pydantic** - Data validation using Python type hints
  - Validates request/response data
  - Automatic JSON serialization
  - Used by FastAPI

- **python-jose** - JWT (JSON Web Token) handling
  - For authentication
  - Secure token generation and validation

- **pyyaml** - YAML parsing
  - For reading Skills Framework files (SKILL.md)
  - Human-readable configuration

- **anthropic** - Claude SDK
  - Will be used for Claude Agent SDK integration
  - Added now so UV creates proper lock file

### 2. FastAPI Server (`backend/api/api_server.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Risk Agents API",
    description="AI-powered project management API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3050"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "risk-agents-backend",
        "timestamp": datetime.utcnow().isoformat(),
    }
```

**Key Concepts**:

**FastAPI Application**:
- `FastAPI()` creates the application instance
- `docs_url="/docs"` enables Swagger UI (interactive API documentation)
- `redoc_url="/redoc"` enables ReDoc (alternative documentation)

**CORS (Cross-Origin Resource Sharing)**:
- Allows frontend (port 3050) to make requests to backend (port 8050)
- Without CORS, browser blocks requests between different ports
- `allow_methods=["*"]` allows all HTTP methods (GET, POST, PUT, DELETE)

**Async/Await**:
- `async def` defines async functions
- FastAPI supports both sync and async
- Async is better for I/O operations (database, API calls)

**Health Check Endpoint**:
- Used by Docker to monitor if service is running
- Returns simple status JSON
- Should always respond quickly (< 1 second)

### 3. Environment Variables (`.env`)

```bash
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-placeholder-key-replace-with-real-key

# Authentication
JWT_SECRET=qUIVjdFdxfW7yrNowZj/qfRjabZKZPIKRV2UeBBHP4I=
NEXTAUTH_SECRET=qUIVjdFdxfW7yrNowZj/qfRjabZKZPIKRV2UeBBHP4I=

# Environment
ENVIRONMENT=development
```

**Important**:
- ⚠️ **NEVER commit `.env` to git** (it's in `.gitignore`)
- `.env.example` is the template (safe to commit)
- `.env` contains real secrets (not safe to commit)
- You'll need to add your real Anthropic API key later

---

## API Endpoints

Once running, the backend provides:

### Current Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API information and links |
| GET | `/health` | Health check (Docker uses this) |
| GET | `/test` | Test endpoint to verify API works |
| GET | `/docs` | Swagger UI (interactive docs) |
| GET | `/redoc` | ReDoc (alternative docs) |

### Example Responses

**GET /** - Root endpoint:
```json
{
  "message": "Welcome to Risk Agents API",
  "version": "0.1.0",
  "docs": "/docs",
  "redoc": "/redoc",
  "health": "/health"
}
```

**GET /health** - Health check:
```json
{
  "status": "healthy",
  "service": "risk-agents-backend",
  "timestamp": "2025-10-21T18:12:34.567890",
  "environment": "development",
  "version": "0.1.0"
}
```

---

## Understanding UV Package Manager

### What is UV?

UV is a modern Python package manager (like npm for Node.js):

**Benefits over pip**:
- ⚡ **10-100x faster** - Written in Rust
- 🔒 **Lock files** - Reproducible installations (uv.lock)
- 📦 **Better resolution** - Smarter dependency conflict resolution
- 🎯 **Modern** - Uses `pyproject.toml` standard

### UV Commands

```bash
# Install dependencies (creates uv.lock)
uv sync

# Add a package
uv add <package-name>

# Add dev dependency
uv add --dev <package-name>

# Remove a package
uv remove <package-name>

# Run a command with UV
uv run <command>

# Run FastAPI with UV
uv run uvicorn api.api_server:app --reload
```

### pyproject.toml vs requirements.txt

**Old way (pip + requirements.txt)**:
```
fastapi==0.104.0
uvicorn==0.24.0
pydantic==2.0.0
```

**New way (UV + pyproject.toml)**:
```toml
[project]
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "pydantic>=2.0.0",
]
```

**Benefits of pyproject.toml**:
- ✅ Project metadata included (name, version, description)
- ✅ Separate dev dependencies
- ✅ Tool configuration (black, pytest, ruff)
- ✅ Standard format (PEP 621)

---

## How Docker Uses These Files

### Docker Build Process

When you run `docker-compose build backend`:

1. **Dockerfile copies pyproject.toml**
   ```dockerfile
   COPY backend/pyproject.toml backend/uv.lock* ./
   ```

2. **UV installs dependencies**
   ```dockerfile
   RUN uv sync --frozen
   ```

3. **Code is copied**
   ```dockerfile
   COPY backend/ .
   ```

4. **Container starts FastAPI**
   ```dockerfile
   CMD ["uv", "run", "uvicorn", "api.api_server:app", "--reload"]
   ```

### Why This Order?

**Layer caching optimization**:
- Dependencies change rarely → cache this layer
- Code changes frequently → separate layer
- Result: Fast rebuilds when you change code!

---

## Testing the Backend

### When Docker is Running

```bash
# Build the backend container
docker-compose build backend

# Start the backend
docker-compose up backend

# In another terminal, test the endpoints:

# Health check
curl http://localhost:8050/health

# Root endpoint
curl http://localhost:8050/

# Test endpoint
curl http://localhost:8050/test

# Open docs in browser
open http://localhost:8050/docs
```

### Expected Output

**Health check response**:
```json
{
  "status": "healthy",
  "service": "risk-agents-backend",
  "timestamp": "2025-10-21T18:12:34.567890",
  "environment": "development",
  "version": "0.1.0"
}
```

**Logs in terminal**:
```
🚀 Risk Agents Backend starting...
📍 Environment: development
🔧 API Docs: http://localhost:8050/docs
✅ Ready to accept requests
INFO:     Uvicorn running on http://0.0.0.0:8050
INFO:     Application startup complete.
```

---

## Next Steps

**Module 1, Step 1.4 - Next.js Frontend Setup**

We'll:
1. Initialize Next.js 15 project
2. Configure TypeScript and Tailwind CSS
3. Create minimal app structure
4. Test frontend container
5. Verify frontend can reach backend API

After that, both backend and frontend will be running and able to communicate!

---

## Verification Checklist

- [x] `backend/pyproject.toml` created with all dependencies
- [x] `backend/api/api_server.py` created with FastAPI app
- [x] Health check endpoint implemented (`/health`)
- [x] CORS middleware configured
- [x] `.env` file created with secrets
- [x] Backend README.md created
- [x] Backend structure ready for Docker build
- [ ] Tested in Docker (requires Docker running)

---

## Key Learnings

### Why FastAPI?

**FastAPI benefits**:
- ✨ **Auto docs** - Swagger UI and ReDoc generated automatically
- ⚡ **Fast** - One of the fastest Python frameworks
- 🔒 **Type safe** - Uses Pydantic for validation
- 🎯 **Modern** - Async support, dependency injection
- 📝 **Great DX** - Excellent developer experience

### Why Async/Await?

**Async is better for I/O operations**:
```python
# Sync (blocks while waiting)
def get_data():
    result = database.query()  # Waits here
    return result

# Async (non-blocking)
async def get_data():
    result = await database.query()  # Other requests can be handled
    return result
```

**When to use async**:
- ✅ Database queries
- ✅ API calls (like Claude SDK)
- ✅ File I/O
- ❌ CPU-intensive calculations (use regular sync)

### Why CORS?

**Browser security prevents cross-origin requests**:
- Frontend: http://localhost:3050
- Backend: http://localhost:8050
- Different ports = different origins
- CORS middleware tells browser "this is allowed"

**Without CORS**:
```
❌ Blocked: Cross-Origin Request from http://localhost:3050 to http://localhost:8050
```

**With CORS**:
```
✅ Allowed: CORS headers present
```

---

## Common Issues & Solutions

### ModuleNotFoundError

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**: Dependencies not installed
```bash
docker-compose build backend  # Rebuild container
```

### Port 8050 Already in Use

**Error**: `bind: address already in use`

**Solution**:
```bash
# Find what's using the port
lsof -i :8050

# Kill the process
kill -9 <PID>
```

### Import Errors

**Error**: `ImportError: attempted relative import with no known parent package`

**Solution**: Make sure `__init__.py` files exist:
```bash
touch backend/__init__.py
touch backend/api/__init__.py
touch backend/agent/__init__.py
```

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Official FastAPI docs
- [UV Documentation](https://docs.astral.sh/uv/) - UV package manager
- [Pydantic Documentation](https://docs.pydantic.dev/) - Data validation
- [Python Async/Await](https://docs.python.org/3/library/asyncio.html) - Async programming
- [CORS Explained](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS) - Cross-Origin Resource Sharing

---

**Status**: ✅ Complete
**Time Taken**: ~25 minutes
**Next Module**: Module 1, Step 1.4 - Next.js Frontend Setup
