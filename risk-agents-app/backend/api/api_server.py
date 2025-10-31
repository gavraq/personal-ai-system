"""
Risk Agents Backend API Server
FastAPI application with Claude Agent SDK integration
"""

from fastapi import FastAPI, Request, status, WebSocket, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime
from pathlib import Path
from typing import Optional
import os
import logging

# Import route modules
from api.routes import query, skills, context, auth, knowledge
import api.websocket_handler as ws_handler

# Import custom middleware and exceptions
from api.middleware import (
    RequestIDMiddleware,
    LoggingMiddleware,
    TimingMiddleware,
    ErrorHandlingMiddleware,
    SecurityHeadersMiddleware,
    get_request_id
)
from api.exceptions import RiskAgentsException, create_error_response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("risk-agents-api")

# Create FastAPI application instance
app = FastAPI(
    title="Risk Agents API",
    description="AI-powered project management API using Claude Agent SDK with Skills Framework",
    version="0.2.0",  # Version bump for Module 3
    docs_url="/docs",  # Swagger UI at http://localhost:8050/docs
    redoc_url="/redoc",  # ReDoc at http://localhost:8050/redoc
)

# Configure CORS (Cross-Origin Resource Sharing)
# This allows the frontend (port 3050) to make requests to backend (port 8050)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3050",  # Frontend in development
        "http://frontend:3050",   # Frontend from Docker network
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Add custom middleware (order matters - first added = last executed)
# Execution order: Security → Error → Request ID → Logging → Timing → Routes

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware, log_body=False)  # Set to True for debugging
app.add_middleware(TimingMiddleware, slow_threshold=1.0)  # Log requests > 1 second

# Exception Handlers

@app.exception_handler(RiskAgentsException)
async def risk_agents_exception_handler(request: Request, exc: RiskAgentsException):
    """Handle custom Risk Agents exceptions"""
    request_id = get_request_id(request)

    logger.warning(
        f"[{request_id}] Risk Agents Exception: {exc.error_code} - {exc.detail}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            request_id=request_id,
            error_code=exc.error_code,
            message=exc.detail,
            status_code=exc.status_code
        ),
        headers=exc.headers or {}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    request_id = get_request_id(request)

    logger.warning(
        f"[{request_id}] Validation Error: {exc.errors()}"
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            request_id=request_id,
            error_code="VALIDATION_ERROR",
            message="Request validation failed",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"errors": exc.errors()}
        )
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    request_id = get_request_id(request)

    logger.error(
        f"[{request_id}] Unexpected Exception: {str(exc)}",
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            request_id=request_id,
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    )


# Include API routers
app.include_router(auth.router, prefix="/api")  # Authentication routes (Module 3.2)
app.include_router(query.router, prefix="/api")
app.include_router(skills.router, prefix="/api")
app.include_router(knowledge.router, prefix="/api/knowledge")  # Knowledge routes (Module 3.5)
app.include_router(context.router, prefix="/api")


# WebSocket endpoint (Module 3.6)
@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str = Query(...),
    user_id: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time bidirectional streaming

    Module 3.6 - WebSocket Handler

    This endpoint provides real-time bidirectional communication for:
    - Streaming query responses
    - Session-based conversations
    - Message buffering and offline reconnection
    - Connection health monitoring

    Connection URL: ws://localhost:8050/ws?session_id=abc123&user_id=user1
    """
    await ws_handler.handle_websocket_connection(websocket, session_id, user_id)


# WebSocket health endpoint
@app.get("/ws/health")
async def websocket_health():
    """
    WebSocket connection statistics and health check

    Returns:
        dict: WebSocket health and statistics
    """
    return await ws_handler.websocket_health_check()


# Health Check Endpoint
# This is used by Docker health checks and monitoring
@app.get("/health")
async def health_check():
    """
    Health check endpoint

    Returns:
        dict: Service health status with timestamp
    """
    return {
        "status": "healthy",
        "service": "risk-agents-backend",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": "0.2.0",  # Module 3 enhancement
        "module": "Module 3.1 - Server Enhancement Complete"
    }


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint - API information

    Returns:
        dict: API welcome message and documentation links
    """
    return {
        "message": "Welcome to Risk Agents API",
        "version": "0.2.0",
        "module": "Module 3 - Backend API Enhancement",
        "features": [
            "Claude Agent SDK Integration",
            "Skills Framework with Progressive Disclosure",
            "Knowledge Layer with Dual Context Pattern",
            "Request ID Tracking",
            "Logging & Timing Middleware",
            "Custom Exception Handling"
        ],
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Run when the application starts
    Initialize agent components and routes
    """
    print("\n" + "="*60)
    print("🚀 Risk Agents Backend v0.2.0")
    print("="*60)
    print(f"📍 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"🔧 Module: 3.6 - WebSocket Handler (FINAL)")  # Updated for Module 3.6
    print()

    # Setup directories
    skills_dir = Path(".claude/skills")
    context_dir = Path("context")
    knowledge_dir = Path("knowledge")

    # Initialize route modules with their dependencies
    logger.info("Initializing agent components...")
    try:
        # Module 3.4: query and skills routes now initialized together
        # The query module creates the agent_client, which we'll share
        query.initialize_query_routes(skills_dir=skills_dir, context_dir=context_dir)

        # Module 3.4: Pass agent_client from query module to skills module
        # This allows skills to execute using the same agent client
        from api.routes.query import agent_client as shared_agent_client
        skills.initialize_skills_routes(skills_dir=skills_dir, client=shared_agent_client)

        # Module 3.5: Initialize knowledge routes
        knowledge.initialize_knowledge_routes(knowledge_dir=knowledge_dir)

        # Module 3.6: Initialize WebSocket handler with shared agent client
        ws_handler.initialize_websocket_handler(client=shared_agent_client)

        context.initialize_context_routes(context_dir=context_dir)
        logger.info("✅ Agent components initialized")
    except Exception as e:
        logger.warning(f"⚠️  Failed to initialize some components: {e}")
        logger.warning("   API will run but some endpoints may not work without ANTHROPIC_API_KEY")

    print()
    print("✨ Features Enabled:")
    print("   - WebSocket Real-Time Streaming")  # NEW Module 3.6
    print("   - Bidirectional Communication")  # NEW Module 3.6
    print("   - Message Buffering & Offline Support")  # NEW Module 3.6
    print("   - Knowledge Base API with Taxonomy Navigation")
    print("   - Full-Text Knowledge Search")
    print("   - Document Access & Cross-References")
    print("   - Skill Execution with Tracking")
    print("   - Skill Usage Analytics & Metrics")
    print("   - Query History Storage & Retrieval")
    print("   - Query Analytics & Statistics")
    print("   - Paginated History API")
    print("   - JWT Token Authentication (access + refresh)")
    print("   - API Key Authentication")
    print("   - Rate Limiting (token bucket)")
    print("   - Request ID Tracking")
    print("   - Logging & Timing Middleware")
    print("   - Custom Exception Handling")
    print("   - Security Headers")
    print("   - Skills Framework (Progressive Disclosure)")
    print("   - Knowledge Layer (Dual Context Pattern)")
    print()
    print(f"📚 API Documentation: http://localhost:8050/docs")
    print(f"🏥 Health Check: http://localhost:8050/health")
    print()
    print("✅ Ready to accept requests")
    print("="*60 + "\n")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Run when the application shuts down
    """
    print("👋 Risk Agents Backend shutting down...")


# Example endpoint to test async functionality
@app.get("/test")
async def test_endpoint():
    """
    Test endpoint to verify API is working

    Returns:
        dict: Test message
    """
    return {
        "message": "API is working! Hot-reload test successful! 🔥",
        "timestamp": datetime.utcnow().isoformat(),
        "hot_reload": True
    }


if __name__ == "__main__":
    # This allows running the server directly with: python api/api_server.py
    # But normally we run it through uvicorn in Docker
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8050, reload=True)
