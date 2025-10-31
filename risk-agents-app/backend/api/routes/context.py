"""
Context Routes - Session and Context Management Endpoints
Handles sessions, captures, and the 3 C's (Capture, Curate, Consult)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from pathlib import Path

from agent import ContextManager

# Create router
router = APIRouter(prefix="/context", tags=["context"])

# Initialize components (will be set on startup)
context_manager: Optional[ContextManager] = None


# Request/Response Models
class CreateSessionRequest(BaseModel):
    """Create session request"""
    user_id: Optional[str] = Field(None, description="Optional user identifier")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "john@example.com"
            }
        }


class SessionResponse(BaseModel):
    """Session response"""
    session_id: str
    user_id: Optional[str]
    created_at: str
    updated_at: str
    context: Dict[str, Any]
    history_count: int


class UpdateSessionRequest(BaseModel):
    """Update session request"""
    context: Optional[Dict[str, Any]] = Field(None, description="Context data to merge")
    add_history: Optional[Dict[str, Any]] = Field(None, description="History item to append")

    class Config:
        json_schema_extra = {
            "example": {
                "context": {"project": "Q4 Planning", "budget": 100000},
                "add_history": {"action": "decision_made", "decision": "Approved budget"}
            }
        }


class CaptureRequest(BaseModel):
    """Capture information request"""
    data: Dict[str, Any] = Field(..., description="The captured data")
    capture_type: str = Field(..., description="Type of capture (meeting, document, note, etc.)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "data": {
                    "title": "Q4 Planning Meeting",
                    "attendees": ["Alice", "Bob"],
                    "decisions": ["Approved budget increase"]
                },
                "capture_type": "meeting",
                "metadata": {"duration": "45 min", "location": "Conf Room A"}
            }
        }


class CaptureResponse(BaseModel):
    """Capture response"""
    capture_id: str
    capture_type: str
    captured_at: str


class CaptureSummary(BaseModel):
    """Capture summary for listing"""
    capture_id: str
    capture_type: str
    captured_at: str
    metadata: Dict[str, Any]


class SessionSummary(BaseModel):
    """Session summary for listing"""
    session_id: str
    user_id: Optional[str]
    created_at: str
    updated_at: str
    history_count: int


class ConsultResponse(BaseModel):
    """Consult response with relevant context"""
    session_context: Optional[Dict[str, Any]]
    recent_captures: List[CaptureSummary]


# Initialize function (called from api_server.py startup)
def initialize_context_routes(context_dir: Path):
    """Initialize context routes with context manager"""
    global context_manager
    context_manager = ContextManager(context_dir=context_dir)
    print("✅ Context routes initialized")


@router.post("/sessions", response_model=SessionResponse, status_code=201)
async def create_session(request: CreateSessionRequest) -> SessionResponse:
    """
    Create a new session

    Sessions represent conversations or workflows with their own context and history.

    Args:
        request: Create session request with optional user ID

    Returns:
        New session details

    Raises:
        HTTPException: If context manager not initialized
    """
    if context_manager is None:
        raise HTTPException(
            status_code=500,
            detail="Context manager not initialized"
        )

    try:
        session_id = context_manager.create_session(user_id=request.user_id)
        session = context_manager.get_session(session_id)

        return SessionResponse(
            session_id=session["session_id"],
            user_id=session.get("user_id"),
            created_at=session["created_at"],
            updated_at=session["updated_at"],
            context=session["context"],
            history_count=len(session.get("history", []))
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create session: {str(e)}"
        )


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str) -> SessionResponse:
    """
    Get session details

    Args:
        session_id: Session identifier

    Returns:
        Session details

    Raises:
        HTTPException: If session not found or context manager not initialized
    """
    if context_manager is None:
        raise HTTPException(
            status_code=500,
            detail="Context manager not initialized"
        )

    try:
        session = context_manager.get_session(session_id)

        return SessionResponse(
            session_id=session["session_id"],
            user_id=session.get("user_id"),
            created_at=session["created_at"],
            updated_at=session["updated_at"],
            context=session["context"],
            history_count=len(session.get("history", []))
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Session not found: {session_id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session: {str(e)}"
        )


@router.put("/sessions/{session_id}")
async def update_session(session_id: str, request: UpdateSessionRequest):
    """
    Update session context or add history

    Args:
        session_id: Session identifier
        request: Update request with context and/or history

    Returns:
        Success message

    Raises:
        HTTPException: If session not found or update fails
    """
    if context_manager is None:
        raise HTTPException(
            status_code=500,
            detail="Context manager not initialized"
        )

    try:
        context_manager.update_session(
            session_id,
            context=request.context,
            add_history=request.add_history
        )

        return {"message": "Session updated successfully"}

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Session not found: {session_id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update session: {str(e)}"
        )


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session

    Args:
        session_id: Session identifier

    Returns:
        Success message
    """
    if context_manager is None:
        raise HTTPException(
            status_code=500,
            detail="Context manager not initialized"
        )

    try:
        context_manager.delete_session(session_id)
        return {"message": "Session deleted successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete session: {str(e)}"
        )


@router.get("/sessions", response_model=List[SessionSummary])
async def list_sessions(limit: Optional[int] = None) -> List[SessionSummary]:
    """
    List all sessions

    Args:
        limit: Optional limit on number of results

    Returns:
        List of session summaries (most recent first)

    Raises:
        HTTPException: If context manager not initialized
    """
    if context_manager is None:
        raise HTTPException(
            status_code=500,
            detail="Context manager not initialized"
        )

    try:
        sessions = context_manager.list_sessions(limit=limit)

        return [
            SessionSummary(
                session_id=s["session_id"],
                user_id=s.get("user_id"),
                created_at=s["created_at"],
                updated_at=s["updated_at"],
                history_count=s["history_count"]
            )
            for s in sessions
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list sessions: {str(e)}"
        )


@router.post("/captures", response_model=CaptureResponse, status_code=201)
async def capture_information(request: CaptureRequest) -> CaptureResponse:
    """
    Capture information (meetings, documents, notes, etc.)

    This is the "Capture" part of the 3 C's.

    Args:
        request: Capture request with data, type, and metadata

    Returns:
        Capture details

    Raises:
        HTTPException: If context manager not initialized
    """
    if context_manager is None:
        raise HTTPException(
            status_code=500,
            detail="Context manager not initialized"
        )

    try:
        capture_id = context_manager.capture(
            data=request.data,
            capture_type=request.capture_type,
            metadata=request.metadata
        )

        capture = context_manager.get_capture(capture_id)

        return CaptureResponse(
            capture_id=capture["capture_id"],
            capture_type=capture["capture_type"],
            captured_at=capture["captured_at"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to capture information: {str(e)}"
        )


@router.get("/captures/{capture_id}")
async def get_capture(capture_id: str):
    """
    Get complete capture details

    Args:
        capture_id: Capture identifier

    Returns:
        Complete capture data

    Raises:
        HTTPException: If capture not found or context manager not initialized
    """
    if context_manager is None:
        raise HTTPException(
            status_code=500,
            detail="Context manager not initialized"
        )

    try:
        return context_manager.get_capture(capture_id)

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Capture not found: {capture_id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get capture: {str(e)}"
        )


@router.get("/captures", response_model=List[CaptureSummary])
async def list_captures(
    capture_type: Optional[str] = None,
    limit: Optional[int] = None
) -> List[CaptureSummary]:
    """
    List all captures with optional filtering

    Args:
        capture_type: Optional filter by capture type
        limit: Optional limit on number of results

    Returns:
        List of capture summaries (most recent first)

    Raises:
        HTTPException: If context manager not initialized
    """
    if context_manager is None:
        raise HTTPException(
            status_code=500,
            detail="Context manager not initialized"
        )

    try:
        captures = context_manager.list_captures(
            capture_type=capture_type,
            limit=limit
        )

        return [
            CaptureSummary(
                capture_id=c["capture_id"],
                capture_type=c["capture_type"],
                captured_at=c["captured_at"],
                metadata=c["metadata"]
            )
            for c in captures
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list captures: {str(e)}"
        )


@router.delete("/captures/{capture_id}")
async def delete_capture(capture_id: str):
    """
    Delete a capture

    Args:
        capture_id: Capture identifier

    Returns:
        Success message
    """
    if context_manager is None:
        raise HTTPException(
            status_code=500,
            detail="Context manager not initialized"
        )

    try:
        context_manager.delete_capture(capture_id)
        return {"message": "Capture deleted successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete capture: {str(e)}"
        )


@router.post("/consult", response_model=ConsultResponse)
async def consult_context(
    query: str,
    session_id: Optional[str] = None
) -> ConsultResponse:
    """
    Consult captured information and session context

    This is the "Consult" part of the 3 C's - retrieving relevant context.

    Args:
        query: The user's query
        session_id: Optional session to include context from

    Returns:
        Relevant context including session and recent captures

    Raises:
        HTTPException: If context manager not initialized
    """
    if context_manager is None:
        raise HTTPException(
            status_code=500,
            detail="Context manager not initialized"
        )

    try:
        context = context_manager.consult(query=query, session_id=session_id)

        return ConsultResponse(
            session_context=context.get("session"),
            recent_captures=[
                CaptureSummary(
                    capture_id=c["capture_id"],
                    capture_type=c["capture_type"],
                    captured_at=c["captured_at"],
                    metadata=c["metadata"]
                )
                for c in context.get("recent_captures", [])
            ]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to consult context: {str(e)}"
        )


@router.get("/health/status")
async def context_health():
    """
    Check context service health

    Returns:
        dict: Health status including context manager initialization
    """
    manager_initialized = context_manager is not None

    session_count = 0
    capture_count = 0

    if manager_initialized:
        try:
            session_count = len(context_manager.list_sessions())
            capture_count = len(context_manager.list_captures())
        except:
            pass

    return {
        "status": "healthy" if manager_initialized else "degraded",
        "manager_initialized": manager_initialized,
        "sessions_active": session_count,
        "captures_stored": capture_count,
        "ready": manager_initialized
    }
