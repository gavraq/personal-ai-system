"""
Family Office Files - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.utils import get_openapi

from .core.exceptions import register_exception_handlers
from .routers import auth_router, users_router, deals_router, integrations_router, files_router, activity_router, agents_router, audit_router

# OpenAPI documentation metadata
API_TITLE = "Family Office Files API"
API_VERSION = "1.0.0"
API_DESCRIPTION = """
# Family Office Files API

A collaboration platform for Family Office Partnership in Zurich, enabling secure document management, deal tracking, and AI-powered research assistance.

## Features

- **Deal Management** - Create and manage deals/transactions with role-based access
- **Document Repository** - Upload files to GCS or link Google Drive documents
- **AI Research Agents** - Market research, document analysis, due diligence, and news monitoring
- **File Sharing** - Cross-organization file sharing with granular permissions
- **Activity Tracking** - Complete audit trail of all actions
- **Role-Based Access Control** - Admin, Partner, and Viewer roles with deal-level overrides

## Authentication

All endpoints (except `/api/auth/login`, `/api/auth/register`) require JWT authentication.
Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

Access tokens expire after 15 minutes. Use the `/api/auth/refresh` endpoint to obtain a new token.

## Roles & Permissions

| Role | Description |
|------|-------------|
| **Admin** | Full access to all resources, user management, audit logs |
| **Partner** | Can create deals, upload files, manage deal members |
| **Viewer** | Read-only access to assigned deals |

## Error Responses

All errors follow a consistent format:

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {}
}
```
"""

# Tag metadata for grouping endpoints in documentation
TAGS_METADATA = [
    {
        "name": "auth",
        "description": "Authentication and authorization endpoints. Register, login, logout, and token refresh.",
    },
    {
        "name": "users",
        "description": "User management endpoints (Admin only). List users and manage roles.",
    },
    {
        "name": "deals",
        "description": "Deal/transaction management. Create, update, delete deals and manage deal members.",
    },
    {
        "name": "files",
        "description": "Document management. Upload files, link Google Drive documents, download, and share files.",
    },
    {
        "name": "activity",
        "description": "Activity feed. View actions taken on deals across the platform.",
    },
    {
        "name": "agents",
        "description": "AI research agents. Run market research, document analysis, due diligence, and news alerts.",
    },
    {
        "name": "audit",
        "description": "Audit log (Admin only). View immutable records of permission changes.",
    },
    {
        "name": "integrations",
        "description": "Third-party integrations. Connect Google Drive via OAuth.",
    },
]

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    openapi_tags=TAGS_METADATA,
    contact={
        "name": "Family Office Partnership",
        "email": "support@fop.ch",
    },
    license_info={
        "name": "Proprietary",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Register global exception handlers for consistent error responses
register_exception_handlers(app)

# GZip compression for responses larger than 500 bytes
# Reduces bandwidth usage and improves performance for API responses
app.add_middleware(GZipMiddleware, minimum_size=500)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint returning API status"""
    return {"status": "ok", "message": "Family Office Files API"}


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker healthcheck"""
    return {"status": "healthy"}


# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(deals_router)
app.include_router(integrations_router)
app.include_router(files_router)
app.include_router(activity_router)
app.include_router(agents_router)
app.include_router(audit_router)
