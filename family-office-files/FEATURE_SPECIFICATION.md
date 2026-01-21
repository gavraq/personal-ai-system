# Family Office Files (FOP) - Feature Specification

## Project Overview

**Project Name:** `family-office-files`
**Purpose:** Collaboration platform for Family Office Partnership in Zurich
**Build Method:** Long-running agent harness with automated verification
**Frontend Testing:** Claude Browser Tool (Chrome Extension)

## Technology Stack

| Component | Technology | Deployment |
|-----------|------------|------------|
| Frontend | Next.js 14+ (App Router) | Vercel |
| Backend | Python FastAPI | Google Cloud Run |
| Database | PostgreSQL 15 | Docker (dev) / Cloud SQL (prod) |
| File Storage | Hybrid: Google Drive + GCS | Google Cloud |
| Auth | JWT (simple username/password) | Self-managed |
| Containerization | Docker Compose | Full stack local dev |

## Docker Architecture

```yaml
services:
  frontend:     # Next.js dev server
  backend:      # FastAPI application
  db:           # PostgreSQL 15
  redis:        # Session/cache (optional)
```

---

## Feature Specifications

### F1: Authentication & Authorization

#### F1.1 User Registration
**Description:** New users can create accounts with email and password.

**Acceptance Criteria:**
- [ ] Registration form accepts email, password, confirm password
- [ ] Password minimum 8 characters with complexity requirements
- [ ] Email must be unique in system
- [ ] User created in database with hashed password
- [ ] Welcome email sent (stubbed for demo)

**API Endpoints:**
- `POST /api/auth/register` - Create new user

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F1.1.1 | Register with valid credentials | User created, 201 response | Navigate to /register, fill form, submit, verify redirect to login |
| F1.1.2 | Register with existing email | 409 Conflict error | Fill form with existing email, verify error message displayed |
| F1.1.3 | Register with weak password | 400 Bad Request | Fill form with "123", verify validation error |

---

#### F1.2 User Login (JWT)
**Description:** Users authenticate and receive JWT token for session.

**Acceptance Criteria:**
- [ ] Login form accepts email and password
- [ ] Valid credentials return JWT access token + refresh token
- [ ] Invalid credentials return 401 Unauthorized
- [ ] JWT contains user_id, role, expiry
- [ ] Token stored in httpOnly cookie or localStorage

**API Endpoints:**
- `POST /api/auth/login` - Authenticate user
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Invalidate session

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F1.2.1 | Login with valid credentials | JWT returned, redirect to dashboard | Navigate to /login, enter credentials, verify dashboard loads |
| F1.2.2 | Login with invalid password | 401 error, stay on login | Enter wrong password, verify error message |
| F1.2.3 | Access protected route without token | Redirect to login | Navigate to /dashboard without auth, verify redirect |
| F1.2.4 | Token refresh flow | New access token issued | Wait for token expiry, verify auto-refresh |

---

#### F1.3 Role Assignment (Admin/Partner/Viewer)
**Description:** Admins can assign roles to users controlling their access level.

**Acceptance Criteria:**
- [ ] Three roles: Admin, Partner, Viewer
- [ ] Only Admins can modify user roles
- [ ] Role changes take effect immediately
- [ ] Audit log entry created on role change

**API Endpoints:**
- `PUT /api/users/{user_id}/role` - Update user role (Admin only)
- `GET /api/users` - List users with roles (Admin only)

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F1.3.1 | Admin assigns Partner role | Role updated in DB | Login as Admin, go to Users, change role, verify update |
| F1.3.2 | Partner tries to change role | 403 Forbidden | Login as Partner, attempt role change, verify denied |
| F1.3.3 | Role change reflects in permissions | Access changes immediately | Change user to Viewer, verify upload button hidden |

---

#### F1.4 Session Management
**Description:** Secure session handling with token expiry and refresh.

**Acceptance Criteria:**
- [ ] Access token expires in 15 minutes
- [ ] Refresh token expires in 7 days
- [ ] Logout invalidates all tokens
- [ ] Concurrent session support

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F1.4.1 | Token expiry handling | Auto-refresh or redirect to login | Wait 15+ minutes, verify session continues or login required |
| F1.4.2 | Manual logout | Tokens invalidated | Click logout, verify redirect, cannot access protected routes |

---

### F2: Dashboard

#### F2.1 Deal Overview Cards
**Description:** Main dashboard displays cards for all accessible deals.

**Acceptance Criteria:**
- [ ] Cards show deal title, status, file count, last activity
- [ ] Cards filtered by user's deal access permissions
- [ ] Click card navigates to deal detail
- [ ] Status badge (Draft/Active/Closed) color-coded

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F2.1.1 | Dashboard loads deals | All accessible deals displayed as cards | Login, verify deal cards render within 3s |
| F2.1.2 | Deal card click | Navigate to deal detail page | Click deal card, verify URL changes to /deals/{id} |
| F2.1.3 | Permission filtering | Only assigned deals visible | Login as Partner with 2 deals, verify only 2 cards shown |

---

#### F2.2 Recent Activity Feed
**Description:** Real-time feed showing recent actions across deals.

**Acceptance Criteria:**
- [ ] Shows file uploads, deal updates, agent runs
- [ ] Displays actor, action, timestamp
- [ ] Limited to user's accessible deals
- [ ] Updates within 5 seconds of action

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F2.2.1 | Activity appears after upload | New upload shown in feed | Upload file, verify appears in activity within 5s |
| F2.2.2 | Activity filtering | Only shows permitted deal activity | Verify no activity from inaccessible deals |

---

#### F2.3 Agent Output Summaries
**Description:** Dashboard shows latest agent results per deal.

**Acceptance Criteria:**
- [ ] Summary card per agent type with latest result
- [ ] Expandable to see full output
- [ ] Timestamp of last run
- [ ] Quick re-run button

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F2.3.1 | Agent summary displays | Latest output shown per agent | Run agent, refresh dashboard, verify summary card |
| F2.3.2 | Expand agent output | Full result visible in modal | Click summary, verify modal with full output |

---

#### F2.4 Quick Actions
**Description:** Dashboard provides quick action buttons for common tasks.

**Acceptance Criteria:**
- [ ] "Create Deal" button (Admin/Partner)
- [ ] "Upload File" button (Admin/Partner)
- [ ] "Run Agent" dropdown (all roles)
- [ ] Buttons respect role permissions

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F2.4.1 | Quick action buttons render | All applicable buttons visible | Login as Admin, verify all 3 buttons |
| F2.4.2 | Viewer sees limited actions | No create/upload buttons | Login as Viewer, verify only Run Agent visible |
| F2.4.3 | Create Deal quick action | Opens create deal modal | Click Create Deal, verify modal opens |

---

### F3: Deal/Transaction Management

#### F3.1 Create Deal
**Description:** Users can create new deals/transactions to organize files.

**Acceptance Criteria:**
- [ ] Form: title, description, status (default: Draft)
- [ ] Auto-assigns creator as member
- [ ] Generates unique deal ID
- [ ] Admin/Partner only

**API Endpoints:**
- `POST /api/deals` - Create new deal

**Database Schema:**
```sql
CREATE TABLE deals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F3.1.1 | Create deal with valid data | Deal created, appears in list | Fill create form, submit, verify deal card appears |
| F3.1.2 | Create deal missing title | Validation error | Submit without title, verify error |
| F3.1.3 | Viewer creates deal | 403 Forbidden | Login as Viewer, attempt create, verify denied |

---

#### F3.2 Edit Deal Metadata
**Description:** Authorized users can update deal information.

**Acceptance Criteria:**
- [ ] Edit title, description, status
- [ ] Changes persist on refresh
- [ ] Audit log updated
- [ ] Admin or deal member with Partner role

**API Endpoints:**
- `PUT /api/deals/{deal_id}` - Update deal

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F3.2.1 | Edit deal title | Title updated, persists | Edit title, save, refresh, verify new title |
| F3.2.2 | Edit by non-member | 403 Forbidden | Login as unassigned user, attempt edit |

---

#### F3.3 Deal Permissions
**Description:** Control which users can access each deal.

**Acceptance Criteria:**
- [ ] Assign/remove users from deals
- [ ] Per-deal role override (optional)
- [ ] Admin can access all deals
- [ ] Users only see assigned deals

**API Endpoints:**
- `POST /api/deals/{deal_id}/members` - Add member
- `DELETE /api/deals/{deal_id}/members/{user_id}` - Remove member
- `GET /api/deals/{deal_id}/members` - List members

**Database Schema:**
```sql
CREATE TABLE deal_members (
    deal_id UUID REFERENCES deals(id),
    user_id UUID REFERENCES users(id),
    role_override VARCHAR(20), -- NULL means use user's global role
    added_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (deal_id, user_id)
);
```

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F3.3.1 | Add member to deal | User can now access deal | Add user, login as that user, verify deal visible |
| F3.3.2 | Remove member | User loses access | Remove user, verify deal disappears from their view |
| F3.3.3 | Non-member access attempt | 403 Forbidden | Try to access deal not assigned to |

---

#### F3.4 Deal Status Workflow
**Description:** Deals progress through defined status stages.

**Acceptance Criteria:**
- [ ] Statuses: Draft → Active → Closed
- [ ] Status change requires Partner/Admin
- [ ] Closed deals are read-only
- [ ] Status history tracked

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F3.4.1 | Change status Draft to Active | Status updates, badge changes color | Click status, select Active, verify badge |
| F3.4.2 | Upload to Closed deal | 403 Forbidden | Close deal, attempt upload, verify denied |

---

### F4: File Repository (Hybrid Storage)

#### F4.1 Google Drive OAuth
**Description:** Family offices can connect their Google Drive accounts.

**Acceptance Criteria:**
- [ ] OAuth 2.0 flow for Google Drive API
- [ ] Store refresh token per user/organization
- [ ] Token refresh handling
- [ ] Disconnect option

**API Endpoints:**
- `GET /api/integrations/google/auth` - Initiate OAuth
- `GET /api/integrations/google/callback` - OAuth callback
- `DELETE /api/integrations/google` - Disconnect

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F4.1.1 | Connect Google Drive | OAuth completes, Drive accessible | Click Connect Drive, complete OAuth, verify success message |
| F4.1.2 | Disconnect Google Drive | Token removed, Drive unavailable | Click Disconnect, verify Drive picker disabled |

---

#### F4.2 Drive Picker Integration
**Description:** Full Google Drive Picker UI embedded in platform.

**Acceptance Criteria:**
- [ ] Google Picker API integration
- [ ] Browse connected Drive
- [ ] Select files/folders
- [ ] Link selected items to current deal

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F4.2.1 | Open Drive Picker | Picker modal loads with Drive contents | Click "Link from Drive", verify picker opens |
| F4.2.2 | Select file from Drive | File linked to deal | Select file, click Add, verify file appears in deal |
| F4.2.3 | Select multiple files | All files linked | Select 3 files, verify all 3 added |

---

#### F4.3 Direct File Upload (GCS)
**Description:** Upload files directly to platform storage (for non-Drive users).

**Acceptance Criteria:**
- [ ] Drag-and-drop upload UI
- [ ] File type validation
- [ ] Max file size: 100MB
- [ ] Progress indicator
- [ ] Stored in Google Cloud Storage

**API Endpoints:**
- `POST /api/deals/{deal_id}/files/upload` - Upload file
- `GET /api/files/{file_id}/download` - Download file

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F4.3.1 | Upload valid file | File uploaded, appears in list | Drag file to drop zone, verify upload completes |
| F4.3.2 | Upload oversized file | Error: file too large | Upload 150MB file, verify error message |
| F4.3.3 | Download uploaded file | File downloads correctly | Click download, verify file contents |

---

#### F4.4 File Listing Per Deal
**Description:** Deal page shows all associated files from both sources.

**Acceptance Criteria:**
- [ ] Unified list of Drive links + GCS uploads
- [ ] Source indicator (Drive icon vs Upload icon)
- [ ] Sort by name, date, type
- [ ] Search/filter files

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F4.4.1 | List shows both sources | Drive and GCS files displayed | Add files from both, verify both appear with icons |
| F4.4.2 | Sort by date | Files ordered by date | Click date header, verify sort order |
| F4.4.3 | Search files | Filter results shown | Type in search, verify filtered list |

---

#### F4.5 File Preview
**Description:** Preview files without downloading.

**Acceptance Criteria:**
- [ ] PDF preview in modal
- [ ] Image preview
- [ ] Document preview (via Google Docs Viewer for Drive files)
- [ ] Fallback to download for unsupported types

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F4.5.1 | Preview PDF | PDF renders in modal | Click PDF file, verify preview loads |
| F4.5.2 | Preview image | Image displays in modal | Click image, verify image renders |
| F4.5.3 | Preview unsupported type | Download prompt | Click .zip file, verify download offered |

---

#### F4.6 File Permissions
**Description:** Role-based file access control.

**Acceptance Criteria:**
- [ ] Viewer: view/download only
- [ ] Partner: view/download/upload
- [ ] Admin: full control including delete
- [ ] Cross-FO sharing requires explicit grant

**Database Schema:**
```sql
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID REFERENCES deals(id),
    name VARCHAR(255) NOT NULL,
    source VARCHAR(20) NOT NULL, -- 'drive' or 'gcs'
    source_id VARCHAR(500), -- Drive file ID or GCS path
    mime_type VARCHAR(100),
    size_bytes BIGINT,
    uploaded_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE file_shares (
    file_id UUID REFERENCES files(id),
    shared_with UUID REFERENCES users(id),
    permission VARCHAR(20) DEFAULT 'view',
    shared_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (file_id, shared_with)
);
```

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F4.6.1 | Viewer cannot upload | Upload button hidden/disabled | Login as Viewer, verify no upload option |
| F4.6.2 | Partner can upload | Upload succeeds | Login as Partner, upload file, verify success |
| F4.6.3 | Admin can delete | File removed | Login as Admin, delete file, verify removed |

---

### F5: Permission System

#### F5.1 Role-Based Access Control
**Description:** System-wide role enforcement.

**Acceptance Criteria:**
- [ ] All API endpoints check role
- [ ] UI elements hidden based on role
- [ ] Role hierarchy: Admin > Partner > Viewer

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F5.1.1 | Viewer API restrictions | 403 on write operations | Call POST endpoints as Viewer, verify denied |
| F5.1.2 | UI reflects role | Appropriate elements hidden | Login as each role, verify UI differences |

---

#### F5.2 Deal-Level Permissions
**Description:** Users only access deals they're assigned to.

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F5.2.1 | Unassigned deal access | 403 Forbidden | Try to access deal not a member of |
| F5.2.2 | Admin override | Admin can access all deals | Login as Admin, verify all deals visible |

---

#### F5.3 File-Level Permissions
**Description:** Fine-grained file sharing across organizations.

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F5.3.1 | Share file with external user | User gains access | Share file, login as recipient, verify access |
| F5.3.2 | Revoke file share | Access removed | Revoke share, verify 403 on access |

---

#### F5.4 Permission Audit Log
**Description:** Track all permission changes.

**Acceptance Criteria:**
- [ ] Log: who, what, when, from/to values
- [ ] Immutable audit entries
- [ ] Admin can view audit log

**Database Schema:**
```sql
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id UUID REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    old_value JSONB,
    new_value JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F5.4.1 | Role change logged | Audit entry created | Change role, verify audit log entry |
| F5.4.2 | View audit log | Log displayed for Admins | Login as Admin, navigate to audit log |

---

### F6: Research Agents

#### F6.1 Market Research Agent
**Description:** Analyzes market trends, competitors, investment opportunities.

**Acceptance Criteria:**
- [ ] Input: company/sector query
- [ ] Output: structured market analysis
- [ ] Sources cited
- [ ] Results saved to deal

**API Endpoints:**
- `POST /api/agents/market-research` - Run agent
- `GET /api/agents/market-research/{run_id}` - Get results

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F6.1.1 | Run market research | Analysis returned | Enter query, submit, verify results displayed |
| F6.1.2 | Results saved | Retrievable later | Run agent, refresh, verify results persist |

---

#### F6.2 Document Analysis Agent
**Description:** Extracts insights, summaries from uploaded documents.

**Acceptance Criteria:**
- [ ] Input: file reference
- [ ] Output: summary, key points, entities
- [ ] Supports PDF, DOCX, TXT
- [ ] Results linked to file

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F6.2.1 | Analyze PDF document | Summary and insights returned | Select PDF, run analysis, verify output |
| F6.2.2 | Analyze Drive file | Agent can read Drive file | Link Drive file, analyze, verify success |

---

#### F6.3 Due Diligence Agent
**Description:** Research on companies, individuals, transactions.

**Acceptance Criteria:**
- [ ] Input: entity name, type
- [ ] Output: structured due diligence report
- [ ] Risk flags highlighted
- [ ] Source citations

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F6.3.1 | Run due diligence on company | Report generated | Enter company name, run, verify report structure |
| F6.3.2 | Risk flags displayed | Risks highlighted in UI | Run on risky entity, verify flag visibility |

---

#### F6.4 News & Alerts Agent
**Description:** Monitor news sources, generate alerts on matches.

**Acceptance Criteria:**
- [ ] Configure alert keywords/entities
- [ ] Periodic monitoring (daily)
- [ ] Alert notifications
- [ ] Alert history

**API Endpoints:**
- `POST /api/agents/alerts` - Create alert
- `GET /api/agents/alerts` - List alerts
- `DELETE /api/agents/alerts/{alert_id}` - Remove alert

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F6.4.1 | Create news alert | Alert saved and active | Fill alert form, submit, verify in list |
| F6.4.2 | Alert triggers | Notification received | Trigger alert condition, verify notification |

---

#### F6.5 Agent Delegation Framework
**Description:** Agents run via Task tool pattern from life project.

**Acceptance Criteria:**
- [ ] Agent interface standardized
- [ ] Async execution with status polling
- [ ] Results stored in database
- [ ] Error handling and retry

**Architecture:**
```python
class BaseAgent:
    async def run(self, input: AgentInput) -> AgentOutput
    async def get_status(self, run_id: str) -> AgentStatus

class MarketResearchAgent(BaseAgent): ...
class DocumentAnalysisAgent(BaseAgent): ...
class DueDiligenceAgent(BaseAgent): ...
class NewsAlertsAgent(BaseAgent): ...
```

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F6.5.1 | Agent async execution | Status polling works | Run agent, verify loading state, then results |
| F6.5.2 | Agent error handling | Error displayed gracefully | Trigger agent error, verify message |

---

#### F6.6 Agent Chat UI
**Description:** Conversational interface for each agent.

**Acceptance Criteria:**
- [ ] Chat-style message interface
- [ ] Message history per agent per deal
- [ ] Streaming responses
- [ ] Quick prompts/suggestions

**Test Criteria:**
| Test ID | Test Case | Expected Result | Browser Test |
|---------|-----------|-----------------|--------------|
| F6.6.1 | Send chat message | Response received | Type message, send, verify response |
| F6.6.2 | Message history | Previous messages displayed | Refresh page, verify history loads |
| F6.6.3 | Streaming response | Text streams in real-time | Send query, verify incremental display |

---

### F7: Browser Testing (Claude Browser Tool)

#### F7.1 Dashboard Loads
**Test:** Navigate to root URL, verify dashboard renders.

**Steps:**
1. Open browser to `http://localhost:3000`
2. Verify login page or dashboard loads
3. Check for no console errors
4. Verify load time < 3 seconds

---

#### F7.2 Login Flow
**Test:** Complete login flow from UI.

**Steps:**
1. Navigate to `/login`
2. Enter valid email and password
3. Click submit
4. Verify redirect to `/dashboard`
5. Verify user name displayed in header

---

#### F7.3 Create Deal Flow
**Test:** Create a new deal via UI.

**Steps:**
1. Login as Admin/Partner
2. Click "Create Deal" button
3. Fill in title: "Test Deal"
4. Fill in description: "Test description"
5. Click submit
6. Verify deal card appears on dashboard
7. Click deal card, verify detail page loads

---

#### F7.4 Drive Picker Flow
**Test:** Link file from Google Drive.

**Steps:**
1. Login and navigate to deal
2. Click "Link from Drive"
3. Verify Google Picker opens
4. Select a file
5. Click "Select"
6. Verify file appears in deal's file list

---

#### F7.5 Agent Interaction
**Test:** Run agent and view results.

**Steps:**
1. Navigate to deal page
2. Open Market Research agent
3. Enter query: "Tech sector trends 2024"
4. Click submit
5. Verify loading indicator
6. Verify results display with structured output
7. Verify results saved (refresh and check)

---

## Implementation Phases

### Phase 1: Foundation (Docker + Auth + Database)
- Docker Compose setup
- PostgreSQL schema
- FastAPI skeleton
- Auth endpoints (register, login, JWT)
- Next.js project setup
- Basic login/register UI

### Phase 2: Core Platform (Deals + Files)
- Deal CRUD API
- Deal permissions API
- File upload to GCS
- File listing UI
- Deal management UI

### Phase 3: Google Drive Integration
- OAuth flow
- Drive Picker integration
- Hybrid file listing
- File preview

### Phase 4: Dashboard & Activity
- Dashboard layout
- Deal cards
- Activity feed
- Quick actions

### Phase 5: Research Agents
- Agent base framework
- Market Research agent
- Document Analysis agent
- Due Diligence agent
- News & Alerts agent
- Agent chat UI

### Phase 6: Polish & Testing
- Permission audit log
- Error handling
- Browser testing with Claude
- Performance optimization
- Documentation

---

## Database Schema Summary

```sql
-- Users and Auth
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'viewer',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Deals/Transactions
CREATE TABLE deals (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE deal_members (
    deal_id UUID REFERENCES deals(id),
    user_id UUID REFERENCES users(id),
    role_override VARCHAR(20),
    added_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (deal_id, user_id)
);

-- Files
CREATE TABLE files (
    id UUID PRIMARY KEY,
    deal_id UUID REFERENCES deals(id),
    name VARCHAR(255) NOT NULL,
    source VARCHAR(20) NOT NULL,
    source_id VARCHAR(500),
    mime_type VARCHAR(100),
    size_bytes BIGINT,
    uploaded_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE file_shares (
    file_id UUID REFERENCES files(id),
    shared_with UUID REFERENCES users(id),
    permission VARCHAR(20) DEFAULT 'view',
    shared_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (file_id, shared_with)
);

-- Google Integration
CREATE TABLE google_connections (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    access_token TEXT,
    refresh_token TEXT,
    token_expiry TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Agents
CREATE TABLE agent_runs (
    id UUID PRIMARY KEY,
    deal_id UUID REFERENCES deals(id),
    agent_type VARCHAR(50) NOT NULL,
    input JSONB NOT NULL,
    output JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE TABLE agent_messages (
    id UUID PRIMARY KEY,
    agent_run_id UUID REFERENCES agent_runs(id),
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Audit
CREATE TABLE audit_log (
    id UUID PRIMARY KEY,
    actor_id UUID REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    old_value JSONB,
    new_value JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Activity Feed
CREATE TABLE activity (
    id UUID PRIMARY KEY,
    deal_id UUID REFERENCES deals(id),
    actor_id UUID REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Test Summary

| Category | Feature Count | Test Count |
|----------|---------------|------------|
| F1: Auth | 4 | 11 |
| F2: Dashboard | 4 | 9 |
| F3: Deals | 4 | 10 |
| F4: Files | 6 | 14 |
| F5: Permissions | 4 | 7 |
| F6: Agents | 6 | 12 |
| F7: Browser | 5 | 5 |
| **Total** | **33** | **68** |

---

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@db:5432/fop

# JWT
JWT_SECRET=your-secret-key
JWT_EXPIRY_MINUTES=15
REFRESH_TOKEN_EXPIRY_DAYS=7

# Google Cloud
GCS_BUCKET=fop-files
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
GOOGLE_REDIRECT_URI=http://localhost:8000/api/integrations/google/callback

# AI Agents
ANTHROPIC_API_KEY=xxx
```

---

## Success Criteria

The platform is complete when:
1. All 68 tests pass
2. Browser tests complete successfully via Claude Browser Tool
3. Docker Compose starts all services with single command
4. Demo scenario works end-to-end:
   - Create user, login
   - Create deal
   - Upload file + link Drive file
   - Run each agent type
   - View results on dashboard
