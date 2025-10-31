# Module 1, Step 1.2: Docker Setup

**Module**: Foundation Setup (Week 1)
**Goal**: Create Docker infrastructure for containerized development
**Status**: ✅ Complete
**Date**: 2025-10-21

---

## What We Built

We created the complete Docker infrastructure that allows you to run the entire Risk Agents app with a single command: `docker-compose up`. This includes containerization for both backend (Python/FastAPI) and frontend (Next.js), with hot-reload support for development.

---

## Files Created

### Docker Configuration Files

1. **docker/backend.Dockerfile** - Backend container (Python 3.11 + UV)
2. **docker/frontend.Dockerfile** - Frontend container (Node 20 + Next.js)
3. **docker-compose.yml** - Orchestrates both containers
4. **docker/.dockerignore** - Excludes files from Docker builds
5. **.env.example** - Environment variables template
6. **DOCKER-GUIDE.md** - Quick reference for Docker commands

---

## Understanding Each File

### 1. Backend Dockerfile (`docker/backend.Dockerfile`)

```dockerfile
FROM python:3.11-slim

# Install UV package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first (Docker layer caching)
COPY backend/pyproject.toml backend/uv.lock* ./

# Install dependencies
RUN uv sync --frozen || echo "uv.lock not found, will create on first sync"

# Copy application code
COPY backend/ .

EXPOSE 8050

# Run FastAPI with hot-reload
CMD ["uv", "run", "uvicorn", "api.api_server:app", "--host", "0.0.0.0", "--port", "8050", "--reload"]
```

**Key Concepts**:

- **`FROM python:3.11-slim`** - Start with official Python 3.11 image (slim = smaller size)
- **UV Package Manager** - Copied from official UV container (10-100x faster than pip)
- **Layer Caching** - Dependencies copied before code, so changes to code don't reinstall dependencies
- **`EXPOSE 8050`** - Documents that this container uses port 8050
- **`--reload`** - Enables hot-reloading (code changes reflected without restart)

### 2. Frontend Dockerfile (`docker/frontend.Dockerfile`)

```dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy package files first (Docker layer caching)
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY frontend/ .

EXPOSE 3050

# Run Next.js in development mode
CMD ["npm", "run", "dev"]
```

**Key Concepts**:

- **`FROM node:20-alpine`** - Alpine Linux = very small image size
- **`npm ci`** - Clean install using package-lock.json (reproducible builds)
- **Layer Caching** - Same principle as backend (dependencies before code)
- **`npm run dev`** - Next.js development server with hot-reload

### 3. Docker Compose (`docker-compose.yml`)

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: docker/backend.Dockerfile
    container_name: risk-agents-backend
    ports:
      - "8050:8050"
    volumes:
      - ./backend:/app
      - ./backend/.claude/skills:/app/.claude/skills
      - ./backend/knowledge:/app/knowledge
      - ./backend/context:/app/context
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - JWT_SECRET=${JWT_SECRET}
      - ENVIRONMENT=${ENVIRONMENT:-development}
    restart: unless-stopped
    networks:
      - risk-agents
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8050/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: .
      dockerfile: docker/frontend.Dockerfile
    container_name: risk-agents-frontend
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

**Key Concepts**:

**Ports Mapping**:
- `"8050:8050"` - Maps host port 8050 to container port 8050
- `"3050:3050"` - Maps host port 3050 to container port 3050

**Volumes (Hot Reload)**:
- `./backend:/app` - Syncs backend code to container (changes reflect immediately)
- `./backend/.claude/skills:/app/.claude/skills` - Syncs Skills Framework
- `/app/node_modules` - Excludes node_modules from sync (stays in container)

**Environment Variables**:
- Loaded from `.env` file
- `${ANTHROPIC_API_KEY}` - Your Claude API key
- `${ENVIRONMENT:-development}` - Defaults to "development" if not set

**Depends On**:
- Frontend starts after backend (ensures backend is ready)

**Networks**:
- Both containers on same network for inter-communication
- Frontend can reach backend at `http://backend:8050`

**Health Checks**:
- Backend includes health check endpoint
- Docker monitors if service is healthy

### 4. Environment Variables (`.env.example`)

```bash
# Anthropic API
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Authentication
JWT_SECRET=your_jwt_secret_here
NEXTAUTH_SECRET=your_nextauth_secret_here

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8050
API_URL=http://backend:8050

# NextAuth
NEXTAUTH_URL=http://localhost:3050

# Environment
ENVIRONMENT=development
```

**How to Use**:
1. Copy to `.env`: `cp .env.example .env`
2. Fill in real values (especially ANTHROPIC_API_KEY)
3. Generate secrets: `openssl rand -base64 32`

---

## Docker Concepts Explained

### What is Docker?

Docker packages your application and all its dependencies into a **container**. Think of it like a shipping container - everything needed to run the app is inside.

**Benefits**:
- ✅ **Consistency** - Same environment everywhere (dev, staging, production)
- ✅ **Isolation** - Backend and frontend don't interfere with each other
- ✅ **Easy Setup** - New developers just run `docker-compose up`
- ✅ **No "Works on My Machine"** - If it works in Docker, it works everywhere

### What is Docker Compose?

Docker Compose orchestrates multiple containers. Our app needs:
- 1 container for backend (Python/FastAPI)
- 1 container for frontend (Next.js)

Docker Compose starts both, networks them together, and manages their lifecycle.

### Layer Caching

Docker builds images in **layers**. Each instruction in Dockerfile creates a layer:

```dockerfile
COPY backend/pyproject.toml ./    # Layer 1: Dependencies list
RUN uv sync --frozen              # Layer 2: Install dependencies
COPY backend/ .                   # Layer 3: Application code
```

**Why This Order?**
- Dependencies change rarely
- Code changes frequently
- If only code changes, Docker reuses Layers 1 & 2 (faster builds!)

### Volumes (Hot Reload)

Volumes sync files between your computer and the container:

```yaml
volumes:
  - ./backend:/app  # Your backend folder → Container's /app folder
```

**Result**: Edit code on your computer → Changes instantly appear in container → App reloads automatically

**Exception**: Some folders stay in container:
- `node_modules` - Stays in container (faster, platform-specific)
- `.next` - Next.js build cache stays in container

---

## Essential Docker Commands

### Starting the App

```bash
# First time (build + start)
docker-compose up --build

# After first time (just start)
docker-compose up

# Run in background
docker-compose up -d
```

### Viewing Logs

```bash
# All logs
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### Stopping the App

```bash
# Stop (keep containers)
docker-compose stop

# Stop and remove containers
docker-compose down

# Nuclear option (remove everything)
docker-compose down -v
```

### Rebuilding

```bash
# Rebuild everything
docker-compose build

# Rebuild specific service
docker-compose build backend

# Rebuild and restart
docker-compose up --build
```

### Running Commands Inside Containers

```bash
# Backend bash shell
docker-compose exec backend bash

# Frontend shell
docker-compose exec frontend sh

# Run pytest in backend
docker-compose exec backend python -m pytest

# Install npm package in frontend
docker-compose exec frontend npm install <package>
```

---

## Accessing the Application

Once running with `docker-compose up`:

- **Frontend**: http://localhost:3050
- **Backend API**: http://localhost:8050
- **API Docs**: http://localhost:8050/docs (once FastAPI is set up)

---

## Common Issues & Solutions

### Port Already in Use

**Error**: `bind: address already in use`

**Solution**:
```bash
# Find what's using the port
lsof -i :8050

# Kill the process
kill -9 <PID>

# Or change port in docker-compose.yml
# "8051:8050" instead of "8050:8050"
```

### Hot Reload Not Working

**Solutions**:
1. Check volumes are mounted: `docker-compose config`
2. Restart: `docker-compose restart`
3. Rebuild: `docker-compose up --build`

### Container Won't Start

**Debug Steps**:
```bash
# 1. Check logs
docker-compose logs backend

# 2. Check if .env file exists
ls -la .env

# 3. Rebuild without cache
docker-compose build --no-cache backend

# 4. Check container status
docker-compose ps
```

### Out of Disk Space

```bash
# Check usage
docker system df

# Clean up
docker system prune -a --volumes
```

---

## What's Next?

**Next Step: Module 1, Step 1.3 - Python Backend Setup with UV**

We'll:
1. Initialize Python project with UV (`pyproject.toml`)
2. Install core dependencies (FastAPI, Claude SDK)
3. Create a minimal FastAPI server
4. Add a health check endpoint
5. Test the backend container

---

## Verification Checklist

- [x] `docker/backend.Dockerfile` created
- [x] `docker/frontend.Dockerfile` created
- [x] `docker-compose.yml` created
- [x] `docker/.dockerignore` created
- [x] `.env.example` created
- [x] `DOCKER-GUIDE.md` created
- [x] README.md updated with Docker guide link

---

## Key Learnings

### Why UV Instead of pip?

**UV is 10-100x faster** than pip:
- Written in Rust (extremely fast)
- Better dependency resolution
- Creates lock files for reproducible installs
- Modern Python package management

### Why Separate Dockerfiles?

Backend and frontend have different:
- Base images (Python vs Node)
- Dependencies
- Build processes
- Runtime requirements

Separation = cleaner, more maintainable.

### Why Alpine for Frontend?

Alpine Linux is **tiny** (5MB vs 100MB+):
- Faster builds
- Smaller images
- Less attack surface
- Perfect for Node.js apps

### Why Port 8050 and 3050?

Standard ports (8000, 3000) are often in use. We chose:
- **8050** - Backend (8000 + 50)
- **3050** - Frontend (3000 + 50)

These are less likely to conflict.

---

## Resources

- [Docker Documentation](https://docs.docker.com/) - Official Docker docs
- [Docker Compose](https://docs.docker.com/compose/) - Compose documentation
- [UV Package Manager](https://docs.astral.sh/uv/) - UV documentation
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/) - Docker best practices
- [DOCKER-GUIDE.md](../DOCKER-GUIDE.md) - Our quick reference guide

---

**Status**: ✅ Complete
**Time Taken**: ~20 minutes
**Next Module**: Module 1, Step 1.3 - Python Backend with UV
