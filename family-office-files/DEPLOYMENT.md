# Deployment Guide

This document provides detailed instructions for deploying Family Office Files (FOP) to production environments.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Environment Configuration](#environment-configuration)
4. [Docker Deployment](#docker-deployment)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Cloud Deployments](#cloud-deployments)
7. [Database Management](#database-management)
8. [SSL/TLS Configuration](#ssltls-configuration)
9. [Monitoring & Logging](#monitoring--logging)
10. [Backup & Recovery](#backup--recovery)
11. [Security Hardening](#security-hardening)
12. [Troubleshooting](#troubleshooting)

---

## Overview

### Architecture

```
                    ┌─────────────────┐
                    │   Load Balancer │
                    │   (nginx/ALB)   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ Frontend │  │ Frontend │  │ Frontend │
        │ (Next.js)│  │ (Next.js)│  │ (Next.js)│
        └────┬─────┘  └────┬─────┘  └────┬─────┘
             │              │              │
             └──────────────┼──────────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ Backend  │  │ Backend  │  │ Backend  │
        │ (FastAPI)│  │ (FastAPI)│  │ (FastAPI)│
        └────┬─────┘  └────┬─────┘  └────┬─────┘
             │              │              │
             └──────────────┼──────────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │PostgreSQL│  │  Redis   │  │   GCS    │
        │   (DB)   │  │ (Cache)  │  │ (Files)  │
        └──────────┘  └──────────┘  └──────────┘
```

### Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | Next.js 14 | Web interface |
| Backend | FastAPI | REST API |
| Database | PostgreSQL 15 | Data persistence |
| Cache | Redis 7 | Session/query caching |
| File Storage | Google Cloud Storage | Document storage |
| AI | Anthropic Claude | Research agents |

---

## Prerequisites

### Required Software

- Docker 24.0+ and Docker Compose 2.0+
- Node.js 20+ (for local builds)
- Python 3.11+ (for local builds)
- PostgreSQL client tools (`psql`, `pg_dump`)

### Cloud Provider Accounts

- **Google Cloud Platform** (required)
  - Cloud Storage bucket for files
  - OAuth credentials for Drive integration
- **Anthropic** (required for AI agents)
  - API key for Claude access

### Domain & SSL

- Domain name configured
- SSL certificate (Let's Encrypt recommended)

---

## Environment Configuration

### Production Environment Variables

Create a `.env.production` file with the following variables:

```bash
# ============================================
# DATABASE
# ============================================
DATABASE_URL=postgresql://fop_user:SECURE_PASSWORD@db-host:5432/fop_db

# ============================================
# AUTHENTICATION
# ============================================
# Generate with: openssl rand -hex 32
JWT_SECRET=your-256-bit-secret-key-here

# Token expiry (adjust based on security requirements)
JWT_EXPIRY_MINUTES=15
REFRESH_TOKEN_EXPIRY_DAYS=7

# ============================================
# REDIS CACHE
# ============================================
REDIS_URL=redis://:REDIS_PASSWORD@redis-host:6379/0

# ============================================
# GOOGLE CLOUD
# ============================================
GCS_BUCKET=fop-files-production
GOOGLE_CLIENT_ID=your-oauth-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-oauth-client-secret
GOOGLE_REDIRECT_URI=https://api.yourdomain.com/api/integrations/google/callback

# ============================================
# AI AGENTS
# ============================================
ANTHROPIC_API_KEY=sk-ant-your-api-key

# ============================================
# FRONTEND
# ============================================
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### Environment Variable Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | Yes | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `JWT_SECRET` | Yes | Secret for JWT signing (256-bit) | `openssl rand -hex 32` |
| `JWT_EXPIRY_MINUTES` | No | Access token lifetime | `15` |
| `REFRESH_TOKEN_EXPIRY_DAYS` | No | Refresh token lifetime | `7` |
| `REDIS_URL` | Yes | Redis connection string | `redis://:pass@host:6379/0` |
| `GCS_BUCKET` | Yes | GCS bucket name | `fop-files-production` |
| `GOOGLE_CLIENT_ID` | Yes | OAuth 2.0 client ID | `*.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Yes | OAuth 2.0 client secret | Google-provided |
| `GOOGLE_REDIRECT_URI` | Yes | OAuth callback URL | `https://api.domain.com/...` |
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key | `sk-ant-*` |
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL for frontend | `https://api.domain.com` |

---

## Docker Deployment

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    restart: always
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
    networks:
      - fop-network
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    restart: always
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - JWT_SECRET=${JWT_SECRET}
      - JWT_EXPIRY_MINUTES=${JWT_EXPIRY_MINUTES:-15}
      - REFRESH_TOKEN_EXPIRY_DAYS=${REFRESH_TOKEN_EXPIRY_DAYS:-7}
      - REDIS_URL=${REDIS_URL}
      - GCS_BUCKET=${GCS_BUCKET}
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
      - GOOGLE_REDIRECT_URI=${GOOGLE_REDIRECT_URI}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - db
      - redis
    networks:
      - fop-network
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M

  db:
    image: postgres:15-alpine
    restart: always
    environment:
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - fop-network

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - fop-network

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
    depends_on:
      - frontend
      - backend
    networks:
      - fop-network

networks:
  fop-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

### Production Dockerfiles

**Backend - `backend/Dockerfile.prod`:**

```dockerfile
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 appuser

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**Frontend - `frontend/Dockerfile.prod`:**

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM node:20-alpine

WORKDIR /app

RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV NODE_ENV=production
ENV PORT=3000

CMD ["node", "server.js"]
```

### Deployment Commands

```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale backend=3 --scale frontend=2

# Run database migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Stop services
docker-compose -f docker-compose.prod.yml down
```

---

## Kubernetes Deployment

### Namespace and ConfigMap

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: fop-production

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fop-config
  namespace: fop-production
data:
  JWT_EXPIRY_MINUTES: "15"
  REFRESH_TOKEN_EXPIRY_DAYS: "7"
```

### Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: fop-secrets
  namespace: fop-production
type: Opaque
stringData:
  DATABASE_URL: postgresql://user:pass@db:5432/fop_db
  JWT_SECRET: your-secret-key
  REDIS_URL: redis://:pass@redis:6379/0
  GOOGLE_CLIENT_ID: your-client-id
  GOOGLE_CLIENT_SECRET: your-client-secret
  ANTHROPIC_API_KEY: your-api-key
```

### Backend Deployment

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fop-backend
  namespace: fop-production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fop-backend
  template:
    metadata:
      labels:
        app: fop-backend
    spec:
      containers:
      - name: backend
        image: your-registry/fop-backend:latest
        ports:
        - containerPort: 8000
        envFrom:
        - secretRef:
            name: fop-secrets
        - configMapRef:
            name: fop-config
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: fop-backend
  namespace: fop-production
spec:
  selector:
    app: fop-backend
  ports:
  - port: 8000
    targetPort: 8000
```

### Frontend Deployment

```yaml
# k8s/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fop-frontend
  namespace: fop-production
spec:
  replicas: 2
  selector:
    matchLabels:
      app: fop-frontend
  template:
    metadata:
      labels:
        app: fop-frontend
    spec:
      containers:
      - name: frontend
        image: your-registry/fop-frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "https://api.yourdomain.com"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"

---
apiVersion: v1
kind: Service
metadata:
  name: fop-frontend
  namespace: fop-production
spec:
  selector:
    app: fop-frontend
  ports:
  - port: 3000
    targetPort: 3000
```

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fop-ingress
  namespace: fop-production
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - yourdomain.com
    - api.yourdomain.com
    secretName: fop-tls
  rules:
  - host: yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: fop-frontend
            port:
              number: 3000
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: fop-backend
            port:
              number: 8000
```

---

## Cloud Deployments

### Google Cloud Platform (GCP)

#### Cloud Run Deployment

```bash
# Build and push images
gcloud builds submit --tag gcr.io/PROJECT_ID/fop-backend ./backend
gcloud builds submit --tag gcr.io/PROJECT_ID/fop-frontend ./frontend

# Deploy backend
gcloud run deploy fop-backend \
  --image gcr.io/PROJECT_ID/fop-backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars "DATABASE_URL=..." \
  --set-env-vars "JWT_SECRET=..." \
  --allow-unauthenticated

# Deploy frontend
gcloud run deploy fop-frontend \
  --image gcr.io/PROJECT_ID/fop-frontend \
  --platform managed \
  --region us-central1 \
  --set-env-vars "NEXT_PUBLIC_API_URL=https://api.yourdomain.com" \
  --allow-unauthenticated
```

#### Cloud SQL Setup

```bash
# Create PostgreSQL instance
gcloud sql instances create fop-db \
  --database-version=POSTGRES_15 \
  --tier=db-custom-2-4096 \
  --region=us-central1 \
  --storage-size=20GB \
  --storage-auto-increase

# Create database
gcloud sql databases create fop_db --instance=fop-db

# Create user
gcloud sql users create fop_user \
  --instance=fop-db \
  --password=SECURE_PASSWORD
```

### AWS Deployment

#### ECS with Fargate

```bash
# Create ECR repositories
aws ecr create-repository --repository-name fop-backend
aws ecr create-repository --repository-name fop-frontend

# Build and push
aws ecr get-login-password | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.REGION.amazonaws.com
docker build -t fop-backend ./backend
docker tag fop-backend:latest ACCOUNT.dkr.ecr.REGION.amazonaws.com/fop-backend:latest
docker push ACCOUNT.dkr.ecr.REGION.amazonaws.com/fop-backend:latest
```

#### RDS PostgreSQL

```bash
aws rds create-db-instance \
  --db-instance-identifier fop-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 15 \
  --master-username fop_admin \
  --master-user-password SECURE_PASSWORD \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxx
```

---

## Database Management

### Initial Setup

```bash
# Create database
createdb -h HOST -U USER fop_db

# Run migrations
cd backend
alembic upgrade head
```

### Migration Commands

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# View current revision
alembic current
```

### Backup and Restore

```bash
# Backup database
pg_dump -h HOST -U USER -d fop_db -F c -f backup_$(date +%Y%m%d).dump

# Restore database
pg_restore -h HOST -U USER -d fop_db backup.dump

# Automated backup script
#!/bin/bash
BACKUP_DIR=/backups
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME -F c -f $BACKUP_DIR/fop_$DATE.dump
# Keep only last 7 days
find $BACKUP_DIR -name "fop_*.dump" -mtime +7 -delete
```

---

## SSL/TLS Configuration

### Let's Encrypt with Certbot

```bash
# Install certbot
apt-get install certbot python3-certbot-nginx

# Obtain certificate
certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Auto-renewal (add to crontab)
0 0 * * * certbot renew --quiet
```

### Nginx SSL Configuration

```nginx
# /etc/nginx/conf.d/fop.conf
server {
    listen 80;
    server_name yourdomain.com api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://frontend:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Monitoring & Logging

### Health Check Endpoints

The backend exposes health check endpoints:

- `GET /health` - Basic health check
- `GET /docs` - API documentation (Swagger UI)
- `GET /redoc` - API documentation (ReDoc)

### Logging Configuration

```python
# backend/app/core/logging.py
import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
```

### Prometheus Metrics (Optional)

```python
# Add to requirements.txt
prometheus-fastapi-instrumentator==6.0.0

# In main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### Recommended Monitoring Stack

- **Prometheus** - Metrics collection
- **Grafana** - Visualization
- **Loki** - Log aggregation
- **AlertManager** - Alerting

---

## Backup & Recovery

### Automated Backup Strategy

| Component | Frequency | Retention | Method |
|-----------|-----------|-----------|--------|
| PostgreSQL | Daily | 30 days | pg_dump to GCS |
| Redis | Hourly | 7 days | RDB snapshots |
| GCS Files | Continuous | Versioned | Native versioning |

### Disaster Recovery

1. **Database Recovery**
   ```bash
   # Restore from backup
   pg_restore -h NEW_HOST -U USER -d fop_db backup.dump

   # Verify data integrity
   psql -h NEW_HOST -U USER -d fop_db -c "SELECT COUNT(*) FROM deals;"
   ```

2. **Service Recovery**
   ```bash
   # Pull latest images
   docker-compose -f docker-compose.prod.yml pull

   # Start services
   docker-compose -f docker-compose.prod.yml up -d

   # Run pending migrations
   docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
   ```

---

## Security Hardening

### Checklist

- [ ] Strong JWT secret (256-bit minimum)
- [ ] Database password policy enforced
- [ ] Redis authentication enabled
- [ ] HTTPS only (redirect HTTP)
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] API key rotation policy
- [ ] Security headers configured
- [ ] Audit logging enabled
- [ ] Regular dependency updates

### Security Headers (Nginx)

```nginx
# Add to nginx configuration
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';" always;
```

### Rate Limiting

```nginx
# Rate limiting zone
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

server {
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://backend:8000;
    }
}
```

---

## Troubleshooting

### Common Issues

#### Database Connection Failed

```bash
# Check database is running
docker-compose ps db

# Test connection
psql -h localhost -p 5433 -U fop_user -d fop_db

# Check logs
docker-compose logs db
```

#### Redis Connection Failed

```bash
# Check Redis is running
docker-compose ps redis

# Test connection
redis-cli -h localhost -p 6379 ping

# Check logs
docker-compose logs redis
```

#### Backend Not Starting

```bash
# Check logs
docker-compose logs backend

# Run migrations manually
docker-compose exec backend alembic upgrade head

# Check environment variables
docker-compose exec backend env
```

#### Frontend Build Errors

```bash
# Check logs
docker-compose logs frontend

# Rebuild with no cache
docker-compose build --no-cache frontend
```

### Debug Mode

For debugging in production, temporarily enable debug logging:

```bash
docker-compose exec backend python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
"
```

### Performance Issues

1. **Database slow queries**
   ```sql
   -- Enable query logging
   ALTER SYSTEM SET log_min_duration_statement = 1000;
   SELECT pg_reload_conf();
   ```

2. **Redis memory issues**
   ```bash
   redis-cli INFO memory
   redis-cli MEMORY DOCTOR
   ```

3. **Container resource limits**
   ```bash
   docker stats
   ```

---

## Support

For issues and support:

1. Check the [troubleshooting](#troubleshooting) section
2. Review application logs
3. Contact the development team

---

*Last updated: January 2026*
