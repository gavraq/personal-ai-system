# Environment Variables Reference

This document provides a comprehensive reference for all environment variables used in Family Office Files (FOP).

## Table of Contents

1. [Quick Setup](#quick-setup)
2. [Backend Variables](#backend-variables)
3. [Frontend Variables](#frontend-variables)
4. [Docker Variables](#docker-variables)
5. [Security Best Practices](#security-best-practices)
6. [Environment-Specific Configuration](#environment-specific-configuration)

---

## Quick Setup

Copy `.env.example` to `.env` and configure the required variables:

```bash
cp .env.example .env
```

**Minimum required variables for local development:**

```bash
DATABASE_URL=postgresql://fop_user:fop_password@localhost:5433/fop_db
JWT_SECRET=your-secret-key-minimum-32-characters
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Backend Variables

### Database Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | **Yes** | `postgresql://fop_user:fop_password@db:5432/fop_db` | PostgreSQL connection string |

**Format:** `postgresql://USER:PASSWORD@HOST:PORT/DATABASE`

**Examples:**
```bash
# Local development
DATABASE_URL=postgresql://fop_user:fop_password@localhost:5433/fop_db

# Docker Compose
DATABASE_URL=postgresql://fop_user:fop_password@db:5432/fop_db

# Production (Cloud SQL)
DATABASE_URL=postgresql://fop_user:SECURE_PASSWORD@/fop_db?host=/cloudsql/PROJECT:REGION:INSTANCE
```

---

### Authentication (JWT)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_SECRET` | **Yes** | `your-super-secret-jwt-key-change-in-production` | Secret key for signing JWT tokens (256-bit minimum recommended) |
| `JWT_EXPIRY_MINUTES` | No | `15` | Access token lifetime in minutes |
| `REFRESH_TOKEN_EXPIRY_DAYS` | No | `7` | Refresh token lifetime in days |

**Generate a secure JWT secret:**
```bash
# Using OpenSSL
openssl rand -hex 32

# Using Python
python -c "import secrets; print(secrets.token_hex(32))"
```

**Security Notes:**
- Use a unique secret per environment (dev/staging/prod)
- Never commit JWT secrets to version control
- Rotate secrets periodically in production

---

### Cache (Redis)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REDIS_URL` | No | `redis://redis:6379/0` | Redis connection string for caching |

**Format:** `redis://[:PASSWORD@]HOST:PORT/DATABASE`

**Examples:**
```bash
# Local development (no auth)
REDIS_URL=redis://localhost:6379/0

# Docker Compose
REDIS_URL=redis://redis:6379/0

# Production (with password)
REDIS_URL=redis://:REDIS_PASSWORD@redis-host:6379/0

# Redis Cloud
REDIS_URL=redis://default:PASSWORD@HOST.redis-cloud.com:PORT
```

**Features requiring Redis:**
- User session caching
- Deal membership caching
- API response caching

---

### Google Cloud Storage

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GCS_BUCKET` | **Yes** | `fop-files` | Google Cloud Storage bucket name for file storage |

**Setup Steps:**
1. Create a GCS bucket in Google Cloud Console
2. Set appropriate permissions (Storage Object Admin for backend service account)
3. Enable versioning for data protection (optional but recommended)

**Examples:**
```bash
# Development
GCS_BUCKET=fop-files-dev

# Production
GCS_BUCKET=fop-files-production
```

---

### Google OAuth (Drive Integration)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_CLIENT_ID` | **Yes*** | - | OAuth 2.0 client ID from Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | **Yes*** | - | OAuth 2.0 client secret |
| `GOOGLE_REDIRECT_URI` | **Yes*** | `http://localhost:8000/api/integrations/google/callback` | OAuth callback URL |

*Required for Google Drive integration feature

**Setup Steps:**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create OAuth 2.0 credentials (Web application type)
3. Add authorized redirect URIs:
   - Development: `http://localhost:8000/api/integrations/google/callback`
   - Production: `https://api.yourdomain.com/api/integrations/google/callback`
4. Enable Google Drive API

**Examples:**
```bash
# Development
GOOGLE_CLIENT_ID=123456789.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnop
GOOGLE_REDIRECT_URI=http://localhost:8000/api/integrations/google/callback

# Production
GOOGLE_REDIRECT_URI=https://api.yourdomain.com/api/integrations/google/callback
```

---

### AI Agents (Anthropic)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | **Yes*** | - | Anthropic API key for Claude AI access |

*Required for AI research agents feature

**Setup Steps:**
1. Create an account at [Anthropic Console](https://console.anthropic.com)
2. Generate an API key
3. Set usage limits to control costs

**Example:**
```bash
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx
```

**Features requiring this key:**
- Market Research Agent
- Document Analysis Agent
- Due Diligence Agent
- News Alerts Agent

---

## Frontend Variables

All frontend environment variables must be prefixed with `NEXT_PUBLIC_` to be accessible in the browser.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | **Yes** | `http://localhost:8000` | Backend API base URL |
| `NEXT_PUBLIC_GOOGLE_CLIENT_ID` | No | - | Google OAuth client ID (for Drive Picker) |
| `NEXT_PUBLIC_GOOGLE_API_KEY` | No | - | Google API key (for Drive Picker) |

**Examples:**
```bash
# Development
NEXT_PUBLIC_API_URL=http://localhost:8000

# Production
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# With Google Drive Picker
NEXT_PUBLIC_GOOGLE_CLIENT_ID=123456789.apps.googleusercontent.com
NEXT_PUBLIC_GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXX
```

**Note:** `NEXT_PUBLIC_GOOGLE_CLIENT_ID` can be the same as the backend `GOOGLE_CLIENT_ID`. The `NEXT_PUBLIC_GOOGLE_API_KEY` is a separate API key (not OAuth) created in Google Cloud Console.

---

## Docker Variables

These variables are used in `docker-compose.yml` for container configuration:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_USER` | No | `fop_user` | PostgreSQL username |
| `DB_PASSWORD` | No | `fop_password` | PostgreSQL password |
| `DB_NAME` | No | `fop_db` | PostgreSQL database name |
| `REDIS_PASSWORD` | No | - | Redis authentication password |

**Examples:**
```bash
# docker-compose.yml environment
DB_USER=fop_user
DB_PASSWORD=secure_password_here
DB_NAME=fop_db
REDIS_PASSWORD=redis_secure_password
```

---

## Security Best Practices

### 1. Secret Management

**Never commit secrets to version control.** Use one of these approaches:

- **Environment files**: Use `.env` files (gitignored)
- **Secret managers**: AWS Secrets Manager, Google Secret Manager, HashiCorp Vault
- **CI/CD secrets**: GitHub Secrets, GitLab CI Variables

### 2. Secret Rotation

| Secret | Rotation Frequency | Procedure |
|--------|-------------------|-----------|
| `JWT_SECRET` | Quarterly | Deploy new secret, old tokens expire naturally |
| `DATABASE_URL` | As needed | Update password, restart services |
| `ANTHROPIC_API_KEY` | As needed | Generate new key, revoke old |
| `GOOGLE_CLIENT_SECRET` | Annually | Create new credentials, update config |

### 3. Access Control

```bash
# Set restrictive permissions on .env files
chmod 600 .env
chmod 600 .env.production
```

### 4. Validation

Ensure required variables are set before starting:

```python
# Python validation example
import os

required_vars = ['DATABASE_URL', 'JWT_SECRET']
missing = [var for var in required_vars if not os.getenv(var)]
if missing:
    raise ValueError(f"Missing required environment variables: {missing}")
```

---

## Environment-Specific Configuration

### Development (.env)

```bash
# Database
DATABASE_URL=postgresql://fop_user:fop_password@localhost:5433/fop_db

# Authentication
JWT_SECRET=development-secret-key-not-for-production
JWT_EXPIRY_MINUTES=60
REFRESH_TOKEN_EXPIRY_DAYS=30

# Redis (optional in dev)
REDIS_URL=redis://localhost:6379/0

# Google Cloud
GCS_BUCKET=fop-files-dev
GOOGLE_CLIENT_ID=dev-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=dev-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/integrations/google/callback

# AI
ANTHROPIC_API_KEY=sk-ant-dev-key

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Staging (.env.staging)

```bash
# Database
DATABASE_URL=postgresql://fop_user:staging_password@staging-db:5432/fop_db

# Authentication (shorter expiry for testing)
JWT_SECRET=staging-unique-secret-key-minimum-32-chars
JWT_EXPIRY_MINUTES=15
REFRESH_TOKEN_EXPIRY_DAYS=7

# Redis
REDIS_URL=redis://:staging_pass@staging-redis:6379/0

# Google Cloud
GCS_BUCKET=fop-files-staging
GOOGLE_REDIRECT_URI=https://api-staging.yourdomain.com/api/integrations/google/callback

# AI (separate key with lower limits)
ANTHROPIC_API_KEY=sk-ant-staging-key

# Frontend
NEXT_PUBLIC_API_URL=https://api-staging.yourdomain.com
```

### Production (.env.production)

```bash
# Database (use secret manager in production)
DATABASE_URL=postgresql://fop_user:${DB_PASSWORD}@prod-db:5432/fop_db

# Authentication
JWT_SECRET=${JWT_SECRET_FROM_VAULT}
JWT_EXPIRY_MINUTES=15
REFRESH_TOKEN_EXPIRY_DAYS=7

# Redis
REDIS_URL=redis://:${REDIS_PASSWORD}@prod-redis:6379/0

# Google Cloud
GCS_BUCKET=fop-files-production
GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID_FROM_SECRET_MANAGER}
GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET_FROM_SECRET_MANAGER}
GOOGLE_REDIRECT_URI=https://api.yourdomain.com/api/integrations/google/callback

# AI
ANTHROPIC_API_KEY=${ANTHROPIC_KEY_FROM_SECRET_MANAGER}

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

---

## Troubleshooting

### Variable Not Found

```bash
# Check if variable is set
echo $DATABASE_URL

# Check in Docker container
docker-compose exec backend env | grep DATABASE_URL
```

### Frontend Variable Not Available

Ensure variables are prefixed with `NEXT_PUBLIC_`:
```bash
# Wrong
API_URL=http://localhost:8000

# Correct
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Rebuild the frontend after changing environment variables:
```bash
npm run build
# or
docker-compose build frontend
```

### Connection Issues

**Database connection failed:**
```bash
# Test PostgreSQL connection
psql $DATABASE_URL -c "SELECT 1"
```

**Redis connection failed:**
```bash
# Test Redis connection
redis-cli -u $REDIS_URL ping
```

---

## Summary Table

| Variable | Backend | Frontend | Required | Feature |
|----------|---------|----------|----------|---------|
| `DATABASE_URL` | Yes | - | Yes | Core |
| `JWT_SECRET` | Yes | - | Yes | Auth |
| `JWT_EXPIRY_MINUTES` | Yes | - | No | Auth |
| `REFRESH_TOKEN_EXPIRY_DAYS` | Yes | - | No | Auth |
| `REDIS_URL` | Yes | - | No | Caching |
| `GCS_BUCKET` | Yes | - | Yes | Files |
| `GOOGLE_CLIENT_ID` | Yes | - | Yes* | Drive |
| `GOOGLE_CLIENT_SECRET` | Yes | - | Yes* | Drive |
| `GOOGLE_REDIRECT_URI` | Yes | - | Yes* | Drive |
| `ANTHROPIC_API_KEY` | Yes | - | Yes* | AI Agents |
| `NEXT_PUBLIC_API_URL` | - | Yes | Yes | Core |
| `NEXT_PUBLIC_GOOGLE_CLIENT_ID` | - | Yes | No | Drive Picker |
| `NEXT_PUBLIC_GOOGLE_API_KEY` | - | Yes | No | Drive Picker |

*Required for specific features

---

*Last updated: January 2026*
