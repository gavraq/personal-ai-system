"""
Query Routes - Claude AI Query Endpoints
Handles standard and streaming queries to Claude using the Agent SDK

Module 3.3 Enhancements:
- Query history storage and retrieval
- Query analytics and statistics
- Enhanced context persistence
"""

from fastapi import APIRouter, HTTPException, Query as QueryParam, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, AsyncIterator, List
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import os
import uuid

from agent import RiskAgentClient, ContextManager
from api.dependencies import get_optional_user
from api.auth import User

# Create router
router = APIRouter(prefix="/query", tags=["query"])

# Initialize components (will be set on startup)
agent_client: Optional[RiskAgentClient] = None
context_manager: Optional[ContextManager] = None

# Query history storage (in-memory for development, replace with DB in production)
# Structure: {query_id: QueryHistoryEntry}
query_history: Dict[str, Dict[str, Any]] = {}

# Analytics tracking
query_analytics = {
    "total_queries": 0,
    "streaming_queries": 0,
    "standard_queries": 0,
    "average_response_time": 0.0,
    "total_tokens": 0,
    "queries_by_hour": defaultdict(int),
    "popular_queries": defaultdict(int)
}


# Request/Response Models
class QueryRequest(BaseModel):
    """Standard query request"""
    query: str = Field(..., description="The user's query to Claude", min_length=1)
    session_id: Optional[str] = Field(None, description="Optional session ID for context")
    system_prompt: Optional[str] = Field(None, description="Optional custom system prompt")
    include_context: bool = Field(True, description="Whether to include session context")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Help me capture meeting minutes from this transcript: ...",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "include_context": True
            }
        }


class QueryResponse(BaseModel):
    """Standard query response"""
    response: str = Field(..., description="Claude's response")
    session_id: Optional[str] = Field(None, description="Session ID if provided")
    tokens_used: Optional[int] = Field(None, description="Approximate tokens used")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "I'll help you capture meeting minutes. Based on the transcript...",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "tokens_used": 1500
            }
        }


class StreamQueryRequest(BaseModel):
    """Streaming query request"""
    query: str = Field(..., description="The user's query to Claude", min_length=1)
    session_id: Optional[str] = Field(None, description="Optional session ID for context")
    system_prompt: Optional[str] = Field(None, description="Optional custom system prompt")
    include_context: bool = Field(True, description="Whether to include session context")


# NEW - Module 3.3: Query History Models
class QueryHistoryEntry(BaseModel):
    """Single query history entry"""
    query_id: str = Field(..., description="Unique query identifier")
    query: str = Field(..., description="The query text")
    response: str = Field(..., description="Claude's response")
    session_id: Optional[str] = Field(None, description="Session ID if provided")
    user_id: Optional[str] = Field(None, description="User ID if authenticated")
    timestamp: datetime = Field(..., description="When the query was executed")
    response_time: float = Field(..., description="Response time in seconds")
    tokens_used: int = Field(..., description="Approximate tokens used")
    query_type: str = Field(..., description="standard or streaming")
    success: bool = Field(..., description="Whether the query succeeded")
    error: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "query_id": "550e8400-e29b-41d4-a716-446655440000",
                "query": "Help me capture meeting minutes",
                "response": "I'll help you capture meeting minutes...",
                "session_id": "session-123",
                "user_id": "test-user-1",
                "timestamp": "2025-10-24T17:30:00",
                "response_time": 2.5,
                "tokens_used": 1500,
                "query_type": "standard",
                "success": True
            }
        }


class QueryHistoryResponse(BaseModel):
    """Paginated query history response"""
    queries: List[QueryHistoryEntry] = Field(..., description="List of query history entries")
    total: int = Field(..., description="Total number of queries")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of queries per page")
    has_more: bool = Field(..., description="Whether there are more queries")


class QueryAnalyticsResponse(BaseModel):
    """Query analytics and statistics"""
    total_queries: int = Field(..., description="Total number of queries")
    streaming_queries: int = Field(..., description="Number of streaming queries")
    standard_queries: int = Field(..., description="Number of standard queries")
    average_response_time: float = Field(..., description="Average response time in seconds")
    total_tokens: int = Field(..., description="Total tokens used")
    queries_by_hour: Dict[str, int] = Field(..., description="Queries grouped by hour")
    popular_queries: List[Dict[str, Any]] = Field(..., description="Top 10 popular queries")

    class Config:
        json_schema_extra = {
            "example": {
                "total_queries": 150,
                "streaming_queries": 75,
                "standard_queries": 75,
                "average_response_time": 2.3,
                "total_tokens": 45000,
                "queries_by_hour": {"2025-10-24T17": 25, "2025-10-24T18": 30},
                "popular_queries": [
                    {"query": "Help me capture meeting minutes", "count": 15},
                    {"query": "Analyze this document", "count": 12}
                ]
            }
        }


# Initialize function (called from api_server.py startup)
def initialize_query_routes(skills_dir: Path, context_dir: Path):
    """Initialize query routes with agent client and context manager"""
    global agent_client, context_manager

    agent_client = RiskAgentClient(skills_dir=skills_dir)
    context_manager = ContextManager(context_dir=context_dir)

    print("✅ Query routes initialized")


@router.post("/", response_model=QueryResponse)
async def query_claude(
    request: QueryRequest,
    current_user: Optional[User] = Depends(get_optional_user)
) -> QueryResponse:
    """
    Execute a standard (non-streaming) query to Claude

    This endpoint sends a query to Claude and returns the complete response.
    Use this for simple queries where you want the full response at once.

    **Module 3.3 Enhancement**: Now tracks query history and analytics

    Args:
        request: Query request with query text and optional session context
        current_user: Optional authenticated user (from Module 3.2)

    Returns:
        QueryResponse with Claude's response

    Raises:
        HTTPException: If agent client not initialized or query fails
    """
    if agent_client is None:
        raise HTTPException(
            status_code=500,
            detail="Agent client not initialized. Check ANTHROPIC_API_KEY environment variable."
        )

    # Generate query ID and track start time (Module 3.3)
    query_id = str(uuid.uuid4())
    start_time = datetime.now()

    try:
        # Build context if requested
        context = None
        if request.include_context and request.session_id and context_manager:
            context = context_manager.consult(
                query=request.query,
                session_id=request.session_id
            )

        # Execute query
        response = agent_client.query(
            user_message=request.query,
            context=context,
            system_prompt=request.system_prompt
        )

        # Calculate metrics (Module 3.3)
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        tokens_used = len(response.split()) * 2  # Rough estimate

        # Save to query history (Module 3.3)
        query_history[query_id] = {
            "query_id": query_id,
            "query": request.query,
            "response": response,
            "session_id": request.session_id,
            "user_id": current_user.user_id if current_user else None,
            "timestamp": start_time,
            "response_time": response_time,
            "tokens_used": tokens_used,
            "query_type": "standard",
            "success": True,
            "error": None
        }

        # Update analytics (Module 3.3)
        query_analytics["total_queries"] += 1
        query_analytics["standard_queries"] += 1
        query_analytics["total_tokens"] += tokens_used

        # Update average response time
        total_queries = query_analytics["total_queries"]
        current_avg = query_analytics["average_response_time"]
        query_analytics["average_response_time"] = (
            (current_avg * (total_queries - 1) + response_time) / total_queries
        )

        # Track queries by hour
        hour_key = start_time.strftime("%Y-%m-%dT%H")
        query_analytics["queries_by_hour"][hour_key] += 1

        # Track popular queries (normalize query text)
        query_normalized = request.query.lower().strip()[:100]
        query_analytics["popular_queries"][query_normalized] += 1

        # Update session history if session provided
        if request.session_id and context_manager:
            try:
                context_manager.update_session(
                    request.session_id,
                    add_history={
                        "action": "query",
                        "query_id": query_id,  # Include query_id (Module 3.3)
                        "query": request.query,
                        "response_length": len(response),
                        "response_time": response_time,
                        "timestamp": start_time.isoformat()
                    }
                )
            except FileNotFoundError:
                # Session doesn't exist - that's okay, continue without updating
                pass

        return QueryResponse(
            response=response,
            session_id=request.session_id,
            tokens_used=tokens_used
        )

    except Exception as e:
        # Log failure to history (Module 3.3)
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()

        query_history[query_id] = {
            "query_id": query_id,
            "query": request.query,
            "response": "",
            "session_id": request.session_id,
            "user_id": current_user.user_id if current_user else None,
            "timestamp": start_time,
            "response_time": response_time,
            "tokens_used": 0,
            "query_type": "standard",
            "success": False,
            "error": str(e)
        }

        raise HTTPException(
            status_code=500,
            detail=f"Query failed: {str(e)}"
        )


@router.post("/stream")
async def query_claude_stream(request: StreamQueryRequest):
    """
    Execute a streaming query to Claude

    This endpoint sends a query to Claude and streams the response back
    token by token. Use this for longer responses where you want to show
    progressive output to the user.

    Args:
        request: Stream query request with query text and optional session context

    Returns:
        StreamingResponse with Server-Sent Events (text/event-stream)

    Raises:
        HTTPException: If agent client not initialized or query fails
    """
    if agent_client is None:
        raise HTTPException(
            status_code=500,
            detail="Agent client not initialized. Check ANTHROPIC_API_KEY environment variable."
        )

    async def generate_stream() -> AsyncIterator[str]:
        """Generate streaming response"""
        try:
            # Build context if requested
            context = None
            if request.include_context and request.session_id and context_manager:
                context = context_manager.consult(
                    query=request.query,
                    session_id=request.session_id
                )

            # Stream query
            full_response = []
            for chunk in agent_client.query_stream(
                user_message=request.query,
                context=context,
                system_prompt=request.system_prompt
            ):
                full_response.append(chunk)
                yield f"data: {chunk}\n\n"

            # Send completion signal
            yield "data: [DONE]\n\n"

            # Update session history if session provided
            if request.session_id and context_manager:
                try:
                    complete_response = "".join(full_response)
                    context_manager.update_session(
                        request.session_id,
                        add_history={
                            "action": "query_stream",
                            "query": request.query,
                            "response_length": len(complete_response)
                        }
                    )
                except FileNotFoundError:
                    # Session doesn't exist - that's okay
                    pass

        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"  # Disable proxy buffering
        }
    )


# NEW - Module 3.3: Query History Endpoints

@router.get("/history", response_model=QueryHistoryResponse)
async def get_query_history(
    page: int = QueryParam(1, ge=1, description="Page number"),
    page_size: int = QueryParam(20, ge=1, le=100, description="Results per page"),
    session_id: Optional[str] = QueryParam(None, description="Filter by session ID"),
    user_id: Optional[str] = QueryParam(None, description="Filter by user ID"),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get paginated query history

    **Module 3.3 Feature**: Retrieve historical queries with pagination and filtering

    Args:
        page: Page number (1-indexed)
        page_size: Number of results per page (1-100)
        session_id: Optional filter by session ID
        user_id: Optional filter by user ID (requires authentication)
        current_user: Optional authenticated user

    Returns:
        QueryHistoryResponse with paginated query history
    """
    # Filter queries
    filtered_queries = list(query_history.values())

    # Apply filters
    if session_id:
        filtered_queries = [q for q in filtered_queries if q.get("session_id") == session_id]

    if user_id:
        # Only allow filtering by user_id if authenticated as that user or admin
        if current_user and (current_user.user_id == user_id or "admin" in getattr(current_user, "scopes", [])):
            filtered_queries = [q for q in filtered_queries if q.get("user_id") == user_id]
        else:
            raise HTTPException(status_code=403, detail="Not authorized to view this user's queries")

    # Sort by timestamp (newest first)
    filtered_queries.sort(key=lambda x: x["timestamp"], reverse=True)

    # Pagination
    total = len(filtered_queries)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_queries = filtered_queries[start_idx:end_idx]

    return QueryHistoryResponse(
        queries=[QueryHistoryEntry(**q) for q in paginated_queries],
        total=total,
        page=page,
        page_size=page_size,
        has_more=end_idx < total
    )


@router.get("/history/{query_id}", response_model=QueryHistoryEntry)
async def get_query_by_id(
    query_id: str,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get a specific query by ID

    **Module 3.3 Feature**: Retrieve a single query's full details

    Args:
        query_id: The query ID to retrieve
        current_user: Optional authenticated user

    Returns:
        QueryHistoryEntry for the specified query

    Raises:
        HTTPException: If query not found or not authorized
    """
    if query_id not in query_history:
        raise HTTPException(status_code=404, detail="Query not found")

    query = query_history[query_id]

    # Check authorization if query belongs to a user
    if query.get("user_id"):
        if not current_user or (
            current_user.user_id != query["user_id"] and
            "admin" not in getattr(current_user, "scopes", [])
        ):
            raise HTTPException(status_code=403, detail="Not authorized to view this query")

    return QueryHistoryEntry(**query)


@router.get("/analytics", response_model=QueryAnalyticsResponse)
async def get_query_analytics(
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get query analytics and statistics

    **Module 3.3 Feature**: View usage statistics and trending queries

    Returns:
        QueryAnalyticsResponse with comprehensive analytics
    """
    # Get top 10 popular queries
    popular_queries_list = sorted(
        query_analytics["popular_queries"].items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    popular_queries_formatted = [
        {"query": query, "count": count}
        for query, count in popular_queries_list
    ]

    return QueryAnalyticsResponse(
        total_queries=query_analytics["total_queries"],
        streaming_queries=query_analytics["streaming_queries"],
        standard_queries=query_analytics["standard_queries"],
        average_response_time=round(query_analytics["average_response_time"], 3),
        total_tokens=query_analytics["total_tokens"],
        queries_by_hour=dict(query_analytics["queries_by_hour"]),
        popular_queries=popular_queries_formatted
    )


@router.delete("/history/{query_id}")
async def delete_query_from_history(
    query_id: str,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Delete a query from history

    **Module 3.3 Feature**: Remove a query from the history

    Args:
        query_id: The query ID to delete
        current_user: Optional authenticated user

    Returns:
        dict: Success message

    Raises:
        HTTPException: If query not found or not authorized
    """
    if query_id not in query_history:
        raise HTTPException(status_code=404, detail="Query not found")

    query = query_history[query_id]

    # Check authorization
    if query.get("user_id"):
        if not current_user or (
            current_user.user_id != query["user_id"] and
            "admin" not in getattr(current_user, "scopes", [])
        ):
            raise HTTPException(status_code=403, detail="Not authorized to delete this query")

    del query_history[query_id]

    return {"message": "Query deleted successfully", "query_id": query_id}


@router.post("/history/clear")
async def clear_query_history(
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Clear all query history (admin only or user's own queries)

    **Module 3.3 Feature**: Bulk delete query history

    Args:
        current_user: Authenticated user

    Returns:
        dict: Number of queries deleted

    Raises:
        HTTPException: If not authenticated or not authorized
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    # If admin, clear all queries
    if "admin" in getattr(current_user, "scopes", []):
        count = len(query_history)
        query_history.clear()
        return {"message": "All query history cleared", "deleted_count": count}

    # Otherwise, only clear user's own queries
    user_queries = [qid for qid, q in query_history.items() if q.get("user_id") == current_user.user_id]
    for qid in user_queries:
        del query_history[qid]

    return {"message": "Your query history cleared", "deleted_count": len(user_queries)}


@router.get("/health")
async def query_health():
    """
    Check query service health

    Returns:
        dict: Health status including API key configuration and Module 3.3 stats
    """
    api_key_configured = os.getenv("ANTHROPIC_API_KEY") is not None
    client_initialized = agent_client is not None
    context_initialized = context_manager is not None

    return {
        "status": "healthy" if (api_key_configured and client_initialized) else "degraded",
        "api_key_configured": api_key_configured,
        "agent_client_initialized": client_initialized,
        "context_manager_initialized": context_initialized,
        "ready": api_key_configured and client_initialized and context_initialized,
        # Module 3.3 stats
        "total_queries_tracked": len(query_history),
        "total_queries_processed": query_analytics["total_queries"]
    }
