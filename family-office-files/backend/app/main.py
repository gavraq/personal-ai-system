"""
Family Office Files - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from .core.exceptions import register_exception_handlers
from .routers import auth_router, users_router, deals_router, integrations_router, files_router, activity_router, agents_router, audit_router

app = FastAPI(
    title="Family Office Files API",
    description="Collaboration platform for Family Office Partnership",
    version="0.1.0"
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
