# Fabric Pattern Library Service
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (git for sync, ffmpeg for yt-dlp)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py pattern_loader.py youtube.py ./
COPY templates/ ./templates/

# Create patterns directory structure
RUN mkdir -p /root/.config/fabric/patterns \
    && mkdir -p /root/.config/fabric/custom-patterns

# Environment
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

CMD ["python", "main.py"]
