"""
Family Office Files - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth_router, users_router, deals_router, integrations_router, files_router, activity_router

app = FastAPI(
    title="Family Office Files API",
    description="Collaboration platform for Family Office Partnership",
    version="0.1.0"
)

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
