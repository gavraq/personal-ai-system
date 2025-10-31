# Backend Dockerfile - Python 3.11 with UV Package Manager
# This creates a container for the FastAPI backend with Claude Agent SDK

FROM python:3.11-slim

# Install UV package manager from official source
# UV is 10-100x faster than pip and handles dependencies better
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files first (for Docker layer caching)
# If dependencies don't change, this layer is reused
COPY backend/pyproject.toml backend/uv.lock* ./

# Install dependencies using UV
# --frozen ensures we use exact versions from uv.lock
RUN uv sync --frozen || echo "uv.lock not found, will create on first sync"

# Copy application code
# This is done after dependencies so code changes don't invalidate dependency cache
COPY backend/ .

# Expose port 8050 (our backend API port)
EXPOSE 8050

# Run the FastAPI application using UV
# --reload enables hot-reloading during development
CMD ["uv", "run", "uvicorn", "api.api_server:app", "--host", "0.0.0.0", "--port", "8050", "--reload"]
