# Docker Quick Reference Guide

## Essential Commands

### Starting the App

```bash
# First time setup (build containers)
docker-compose up --build

# After first build (start containers)
docker-compose up

# Run in background (detached mode)
docker-compose up -d

# View logs while running in background
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stopping the App

```bash
# Stop containers (keeps them around)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop, remove containers, and remove volumes
docker-compose down -v
```

### Rebuilding After Changes

```bash
# Rebuild specific service
docker-compose build backend
docker-compose build frontend

# Rebuild and restart
docker-compose up --build

# Rebuild just one service and restart
docker-compose up --build backend
```

### Accessing Containers

```bash
# Run commands inside backend container
docker-compose exec backend bash
docker-compose exec backend python -m pytest

# Run commands inside frontend container
docker-compose exec frontend sh
docker-compose exec frontend npm run lint

# View running containers
docker-compose ps
```

### Cleaning Up

```bash
# Remove stopped containers
docker-compose rm

# Remove all containers, networks, and volumes
docker-compose down -v

# Clean up Docker system (careful!)
docker system prune -f

# Remove all unused images
docker image prune -a
```

## Common Development Workflows

### Adding a New Python Dependency

```bash
# 1. Add dependency using UV
docker-compose exec backend uv add <package-name>

# 2. Rebuild backend container
docker-compose build backend

# 3. Restart backend
docker-compose up -d backend
```

### Adding a New npm Package

```bash
# 1. Add package
docker-compose exec frontend npm install <package-name>

# 2. Rebuild frontend container
docker-compose build frontend

# 3. Restart frontend
docker-compose up -d frontend
```

### Debugging When Something Goes Wrong

```bash
# View all logs
docker-compose logs

# View backend errors
docker-compose logs backend | grep -i error

# Check container status
docker-compose ps

# Inspect container details
docker-compose exec backend env
docker-compose exec backend ls -la

# Check if ports are accessible
curl http://localhost:8050/health
curl http://localhost:3050
```

### Resetting Everything

```bash
# Nuclear option - complete reset
docker-compose down -v
docker system prune -f
docker-compose up --build
```

## Accessing the Application

- **Frontend**: http://localhost:3050
- **Backend API**: http://localhost:8050
- **API Documentation**: http://localhost:8050/docs (when FastAPI is set up)

## Understanding Docker Volumes

Volumes allow code changes to reflect immediately without rebuilding:

- `./backend:/app` - Backend code synced to container
- `./backend/.claude/skills:/app/.claude/skills` - Skills Framework synced
- `./backend/knowledge:/app/knowledge` - Knowledge base synced
- `./frontend:/app` - Frontend code synced
- `/app/node_modules` - node_modules stays in container (not synced)
- `/app/.next` - Next.js build cache stays in container

## Understanding Docker Networks

The `risk-agents` network allows containers to communicate:

- Frontend can reach backend at `http://backend:8050`
- Backend can be accessed from host at `http://localhost:8050`
- Frontend can be accessed from host at `http://localhost:3050`

## Health Checks

The backend container includes a health check:

```bash
# Check backend health
docker-compose exec backend curl http://localhost:8050/health

# View health status
docker-compose ps
```

## Tips & Tricks

### Hot Reload Not Working?

1. Check volumes are mounted: `docker-compose config`
2. Restart containers: `docker-compose restart`
3. Rebuild if needed: `docker-compose up --build`

### Port Already in Use?

```bash
# Check what's using port 8050
lsof -i :8050

# Kill process using port
kill -9 <PID>

# Or change ports in docker-compose.yml
# Change "8050:8050" to "8051:8050" for example
```

### Container Won't Start?

1. Check logs: `docker-compose logs backend`
2. Check environment variables: `.env` file exists and has valid values
3. Try rebuilding: `docker-compose build backend`
4. Try without cache: `docker-compose build --no-cache backend`

### Out of Disk Space?

```bash
# Check Docker disk usage
docker system df

# Clean up everything not in use
docker system prune -a --volumes

# Remove old images
docker image prune -a
```

## Production Considerations

For production deployment, you'll need to:

1. Create optimized Dockerfiles with multi-stage builds
2. Remove `--reload` from backend CMD
3. Build Next.js for production (`npm run build`)
4. Use environment-specific .env files
5. Set up reverse proxy (Nginx)
6. Configure SSL certificates
7. Set up monitoring and logging

See Module 10 in the implementation plan for production deployment.
