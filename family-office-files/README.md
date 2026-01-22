# Family Office Files (FOP)

A collaboration platform for Family Office Partnership in Zurich, enabling secure document management, deal tracking, and AI-powered research assistance.

## Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Frontend | Next.js (App Router) | 14.1.0 |
| Backend | Python FastAPI | 0.109.2 |
| Database | PostgreSQL | 15 |
| Cache | Redis | 7 |
| File Storage | Google Cloud Storage | - |
| Auth | JWT | - |
| AI Agents | Anthropic Claude | - |

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### 1. Clone and Setup Environment

```bash
cd family-office-files
cp .env.example .env
# Edit .env with your configuration
```

### 2. Start with Docker Compose

```bash
docker-compose up -d
```

This starts all services:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **PostgreSQL**: localhost:5433
- **Redis**: localhost:6379

### 3. Run Database Migrations

```bash
docker-compose exec backend alembic upgrade head
```

### 4. Access the Application

Open http://localhost:3000 in your browser.

## Local Development

### Backend (FastAPI)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (or use .env file)
export DATABASE_URL=postgresql://fop_user:fop_password@localhost:5433/fop_db
export JWT_SECRET=your-secret-key
export REDIS_URL=redis://localhost:6379/0

# Run development server
uvicorn app.main:app --reload --port 8000
```

### Frontend (Next.js)

```bash
cd frontend

# Install dependencies
npm install

# Set environment variables
export NEXT_PUBLIC_API_URL=http://localhost:8000

# Run development server
npm run dev
```

## Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate
pytest -v
```

### Frontend Tests

```bash
cd frontend
npm run test
```

## Project Structure

```
family-office-files/
├── backend/
│   ├── app/
│   │   ├── agents/          # AI research agents
│   │   ├── core/            # Configuration, auth, permissions
│   │   ├── models/          # SQLAlchemy models
│   │   ├── routers/         # API endpoints
│   │   ├── schemas/         # Pydantic schemas
│   │   └── main.py          # FastAPI application
│   ├── alembic/             # Database migrations
│   ├── tests/               # Backend tests
│   └── requirements.txt
├── frontend/
│   ├── app/                 # Next.js App Router pages
│   ├── components/          # React components
│   ├── lib/                 # Utilities and API client
│   └── __tests__/           # Frontend tests
├── docker-compose.yml
└── .env.example
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login (returns JWT)
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Current user info

### Users (Admin only)
- `GET /api/users` - List users
- `PUT /api/users/{user_id}/role` - Update user role

### Deals
- `GET /api/deals` - List accessible deals
- `POST /api/deals` - Create deal
- `GET /api/deals/{deal_id}` - Get deal details
- `PUT /api/deals/{deal_id}` - Update deal
- `DELETE /api/deals/{deal_id}` - Delete deal
- `POST /api/deals/{deal_id}/members` - Add member
- `DELETE /api/deals/{deal_id}/members/{user_id}` - Remove member
- `GET /api/deals/{deal_id}/members` - List members

### Files
- `POST /api/deals/{deal_id}/files/upload` - Upload file
- `GET /api/deals/{deal_id}/files` - List deal files
- `GET /api/files/{file_id}` - Get file details
- `GET /api/files/{file_id}/download` - Download file
- `DELETE /api/files/{file_id}` - Delete file
- `POST /api/files/{file_id}/share` - Share file
- `DELETE /api/files/{file_id}/share/{user_id}` - Revoke share
- `GET /api/files/shared` - List shared files

### Activity
- `GET /api/activity` - List all activity
- `GET /api/deals/{deal_id}/activity` - Deal activity

### Agents
- `POST /api/agents/market-research` - Run market research
- `POST /api/agents/document-analysis` - Analyze document
- `POST /api/agents/due-diligence` - Run due diligence
- `POST /api/agents/alerts` - Create news alert
- `GET /api/agents/alerts` - List alerts
- `DELETE /api/agents/alerts/{alert_id}` - Delete alert
- `GET /api/agents/runs/{run_id}` - Get agent run status

### Audit (Admin only)
- `GET /api/audit` - View audit log

### Integrations
- `GET /api/integrations/google/auth` - Google OAuth
- `GET /api/integrations/google/callback` - OAuth callback
- `DELETE /api/integrations/google` - Disconnect Google

## Roles & Permissions

| Role | Deals | Files | Users | Audit |
|------|-------|-------|-------|-------|
| **Admin** | Full access to all | Full access + delete | Manage roles | View |
| **Partner** | Access assigned + create | Upload/download | - | - |
| **Viewer** | Access assigned (read) | Download only | - | - |

### Permission Matrix

- **Deal Access**: Based on deal membership (Admin bypasses)
- **Deal-Level Override**: Users can have different roles per deal
- **File Sharing**: Cross-organization sharing with explicit grants

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `JWT_SECRET` | Secret key for JWT tokens | Required |
| `JWT_EXPIRY_MINUTES` | Access token expiry | 15 |
| `REFRESH_TOKEN_EXPIRY_DAYS` | Refresh token expiry | 7 |
| `REDIS_URL` | Redis connection string | Optional |
| `GCS_BUCKET` | Google Cloud Storage bucket | fop-files |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | Required for Drive |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | Required for Drive |
| `GOOGLE_REDIRECT_URI` | OAuth callback URL | Required for Drive |
| `ANTHROPIC_API_KEY` | Anthropic API key | Required for agents |
| `NEXT_PUBLIC_API_URL` | Backend API URL (frontend) | http://localhost:8000 |

## Features

### Deal Management
- Create and manage deals/transactions
- Assign team members with role-based permissions
- Track deal status (Draft -> Active -> Closed)

### File Repository
- Direct file upload to Google Cloud Storage
- Google Drive integration via OAuth
- File preview for PDFs and images
- Cross-organization file sharing

### AI Research Agents
- **Market Research**: Analyze market trends and competitors
- **Document Analysis**: Extract insights from uploaded documents
- **Due Diligence**: Research companies and individuals
- **News Alerts**: Monitor news sources for keywords

### Security & Compliance
- Role-based access control (RBAC)
- Deal-level permission overrides
- File-level sharing permissions
- Immutable audit log for all permission changes
- API response compression (GZip)
- Redis caching for performance

## License

Proprietary - Family Office Partnership
