# Phase 1: Foundation (Docker + Auth + Database)

**Features**: feat-34, feat-35, feat-1, feat-2, feat-3, feat-4
**Priority**: P1 - Must complete before other phases

## Pre-requisites
- [x] Verify Docker Desktop is running *(Docker processes detected, but CLI commands hanging - may need Docker Desktop restart)*
- [x] Verify bun is installed for FeatureRegistry commands *(bun 1.3.3 verified)*

## 1.1 Docker Compose Setup (feat-34)

- [x] Create `docker-compose.yml` with services: frontend (Next.js), backend (FastAPI), db (PostgreSQL 15), redis (optional cache) *(file exists with all 4 services configured)*
- [x] Create `backend/Dockerfile` with Python 3.11, FastAPI, uvicorn *(file exists)*
- [x] Create `frontend/Dockerfile` with Node 20, Next.js dev server *(file exists)*
- [x] Create `.env.example` with all required environment variables *(file exists with DB, JWT, Google, Anthropic vars)*
- [ ] Run `docker-compose up --build` and verify all services start *(BLOCKED 2026-01-21 14:56 UTC: Re-verified in Maestro loop 00002 - Docker CLI STILL frozen. Same hung processes (PID 99055 `docker info`, PID 98962 `docker version`) from 14:45 remain stuck. **USER ACTION REQUIRED - CANNOT PROCEED**: 1) Kill hung processes: `kill -9 99055 98962`, 2) Quit Docker Desktop via menu bar → "Quit Docker Desktop", 3) Force quit if needed: `killall Docker`, 4) Wait 15 seconds, 5) Restart Docker Desktop from /Applications, 6) Wait for green "running" status, 7) Test with `docker info`, 8) Re-run Maestro.)*
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-34 passing`

## 1.2 Database Schema (feat-35)

- [ ] Create `backend/alembic/` directory for migrations
- [ ] Create initial migration with all tables: users, deals, deal_members, files, file_shares, google_connections, agent_runs, agent_messages, audit_log, activity
- [ ] Run migration against Docker PostgreSQL
- [ ] Verify tables created with `\dt` in psql
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-35 passing`

## 1.3 User Registration (feat-1)

- [ ] Create `backend/app/models/user.py` with User SQLAlchemy model
- [ ] Create `backend/app/schemas/auth.py` with Pydantic schemas (RegisterRequest, UserResponse)
- [ ] Create `backend/app/routers/auth.py` with POST `/api/auth/register` endpoint
- [ ] Implement password hashing with bcrypt
- [ ] Add email uniqueness validation (409 on duplicate)
- [ ] Add password complexity validation (min 8 chars)
- [ ] Test: Register with valid credentials returns 201
- [ ] Test: Register with existing email returns 409
- [ ] Test: Register with weak password returns 400
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-1 passing`

## 1.4 User Login JWT (feat-2)

- [ ] Create `backend/app/core/security.py` with JWT token creation/verification
- [ ] Add POST `/api/auth/login` endpoint returning access + refresh tokens
- [ ] Add POST `/api/auth/refresh` endpoint for token refresh
- [ ] Add POST `/api/auth/logout` endpoint (token invalidation)
- [ ] Configure JWT expiry: access=15min, refresh=7days
- [ ] Create `backend/app/core/deps.py` with `get_current_user` dependency
- [ ] Test: Login with valid credentials returns JWT
- [ ] Test: Login with invalid password returns 401
- [ ] Test: Access protected route without token returns 401
- [ ] Test: Token refresh returns new access token
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-2 passing`

## 1.5 Role Assignment (feat-3)

- [ ] Add `role` enum field to User model (admin, partner, viewer)
- [ ] Create PUT `/api/users/{user_id}/role` endpoint (admin only)
- [ ] Create GET `/api/users` endpoint to list users (admin only)
- [ ] Add role check decorator/dependency for endpoint protection
- [ ] Test: Admin can assign Partner role
- [ ] Test: Partner cannot change roles (403)
- [ ] Test: Role change reflects in user permissions
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-3 passing`

## 1.6 Session Management (feat-4)

- [ ] Implement token blacklist for logout (Redis or DB table)
- [ ] Add automatic token refresh logic
- [ ] Test: Token expiry triggers refresh or redirect
- [ ] Test: Logout invalidates tokens
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-4 passing`

## 1.7 Next.js Frontend Setup

- [ ] Initialize Next.js 14 app with App Router in `frontend/`
- [ ] Install dependencies: tailwindcss, shadcn/ui, axios, zustand
- [ ] Create `frontend/app/login/page.tsx` with login form
- [ ] Create `frontend/app/register/page.tsx` with registration form
- [ ] Create `frontend/lib/api.ts` for API client with auth headers
- [ ] Create `frontend/lib/auth.ts` for token storage and refresh
- [ ] Test: Login form submits and redirects to dashboard on success
- [ ] Test: Register form creates account and redirects to login

## Phase 1 Completion

- [ ] All 6 features (feat-34, feat-35, feat-1, feat-2, feat-3, feat-4) marked as passing
- [ ] Docker Compose starts all services with `docker-compose up`
- [ ] Can register user, login, and access protected endpoint
- [ ] Run `bun .claude/skills/CORE/Tools/FeatureRegistry.ts verify family-office-files` to confirm
