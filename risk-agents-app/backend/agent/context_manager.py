"""
Context Manager for Session Management
Handles capture, storage, and retrieval of session context
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import uuid


class ContextManager:
    """
    Manage session context and captured information

    This implements a simplified version of the "3 C's" (Capture, Curate, Consult):
    - Capture: Store information from conversations
    - Curate: Organize and structure captured data
    - Consult: Retrieve relevant context for queries

    For MVP, we use file-based storage. Future versions could use a database.
    """

    def __init__(self, context_dir: Path):
        """
        Initialize the Context Manager

        Args:
            context_dir: Path to context storage directory
        """
        self.context_dir = context_dir
        self.captured_dir = context_dir / "captured"
        self.sessions_dir = context_dir / "sessions"

        # Ensure directories exist
        self.captured_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def create_session(self, user_id: Optional[str] = None) -> str:
        """
        Create a new session

        Args:
            user_id: Optional user identifier

        Returns:
            Session ID (UUID)
        """
        session_id = str(uuid.uuid4())
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "context": {},
            "history": []
        }

        session_path = self.sessions_dir / f"{session_id}.json"
        with open(session_path, 'w') as f:
            json.dump(session_data, f, indent=2)

        return session_id

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve session data

        Args:
            session_id: Session identifier

        Returns:
            Session data dictionary

        Raises:
            FileNotFoundError: If session doesn't exist
        """
        session_path = self.sessions_dir / f"{session_id}.json"

        if not session_path.exists():
            raise FileNotFoundError(f"Session not found: {session_id}")

        with open(session_path, 'r') as f:
            return json.load(f)

    def update_session(
        self,
        session_id: str,
        context: Optional[Dict[str, Any]] = None,
        add_history: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update session with new context or history

        Args:
            session_id: Session identifier
            context: New context data to merge
            add_history: History item to append
        """
        session = self.get_session(session_id)

        # Update context
        if context:
            session["context"].update(context)

        # Add to history
        if add_history:
            session["history"].append({
                **add_history,
                "timestamp": datetime.utcnow().isoformat()
            })

        # Update timestamp
        session["updated_at"] = datetime.utcnow().isoformat()

        # Save
        session_path = self.sessions_dir / f"{session_id}.json"
        with open(session_path, 'w') as f:
            json.dump(session, f, indent=2)

    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """
        Get just the context portion of a session

        Args:
            session_id: Session identifier

        Returns:
            Context dictionary
        """
        session = self.get_session(session_id)
        return session.get("context", {})

    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get session history

        Args:
            session_id: Session identifier
            limit: Optional limit on number of history items

        Returns:
            List of history items (most recent first)
        """
        session = self.get_session(session_id)
        history = session.get("history", [])

        # Reverse to get most recent first
        history = list(reversed(history))

        if limit:
            history = history[:limit]

        return history

    def capture(
        self,
        data: Dict[str, Any],
        capture_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Capture information (from meetings, documents, etc.)

        This is the "Capture" part of the 3 C's.

        Args:
            data: The captured data
            capture_type: Type of capture (meeting, document, note, etc.)
            metadata: Optional metadata about the capture

        Returns:
            Capture ID
        """
        capture_id = str(uuid.uuid4())
        capture_data = {
            "capture_id": capture_id,
            "capture_type": capture_type,
            "captured_at": datetime.utcnow().isoformat(),
            "data": data,
            "metadata": metadata or {}
        }

        capture_path = self.captured_dir / f"{capture_id}.json"
        with open(capture_path, 'w') as f:
            json.dump(capture_data, f, indent=2)

        return capture_id

    def get_capture(self, capture_id: str) -> Dict[str, Any]:
        """
        Retrieve captured information

        Args:
            capture_id: Capture identifier

        Returns:
            Captured data dictionary
        """
        capture_path = self.captured_dir / f"{capture_id}.json"

        if not capture_path.exists():
            raise FileNotFoundError(f"Capture not found: {capture_id}")

        with open(capture_path, 'r') as f:
            return json.load(f)

    def list_captures(
        self,
        capture_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List all captures, optionally filtered by type

        Args:
            capture_type: Optional filter by capture type
            limit: Optional limit on number of results

        Returns:
            List of capture summaries
        """
        captures = []

        for capture_file in self.captured_dir.glob("*.json"):
            with open(capture_file, 'r') as f:
                capture = json.load(f)

                # Filter by type if specified
                if capture_type and capture.get("capture_type") != capture_type:
                    continue

                # Add summary info
                captures.append({
                    "capture_id": capture["capture_id"],
                    "capture_type": capture["capture_type"],
                    "captured_at": capture["captured_at"],
                    "metadata": capture.get("metadata", {})
                })

        # Sort by date (most recent first)
        captures.sort(key=lambda x: x["captured_at"], reverse=True)

        if limit:
            captures = captures[:limit]

        return captures

    def consult(
        self,
        query: str,
        session_id: Optional[str] = None,
        capture_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Consult captured information and session context

        This is the "Consult" part of the 3 C's - retrieving relevant context.

        Args:
            query: The user's query
            session_id: Optional session to include context from
            capture_types: Optional list of capture types to include

        Returns:
            Dictionary with relevant context
        """
        context = {}

        # Add session context if provided
        if session_id:
            try:
                session_context = self.get_session_context(session_id)
                if session_context:
                    context["session"] = session_context
            except FileNotFoundError:
                pass

        # Add recent captures
        captures = self.list_captures(limit=5)
        if captures:
            context["recent_captures"] = captures

        # TODO: Future enhancement - semantic search over captured data
        # For now, we just return recent items

        return context

    def list_sessions(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all sessions

        Args:
            limit: Optional limit on number of results

        Returns:
            List of session summaries
        """
        sessions = []

        for session_file in self.sessions_dir.glob("*.json"):
            with open(session_file, 'r') as f:
                session = json.load(f)

                sessions.append({
                    "session_id": session["session_id"],
                    "user_id": session.get("user_id"),
                    "created_at": session["created_at"],
                    "updated_at": session["updated_at"],
                    "history_count": len(session.get("history", []))
                })

        # Sort by update date (most recent first)
        sessions.sort(key=lambda x: x["updated_at"], reverse=True)

        if limit:
            sessions = sessions[:limit]

        return sessions

    def delete_session(self, session_id: str) -> None:
        """
        Delete a session

        Args:
            session_id: Session identifier
        """
        session_path = self.sessions_dir / f"{session_id}.json"
        if session_path.exists():
            session_path.unlink()

    def delete_capture(self, capture_id: str) -> None:
        """
        Delete a capture

        Args:
            capture_id: Capture identifier
        """
        capture_path = self.captured_dir / f"{capture_id}.json"
        if capture_path.exists():
            capture_path.unlink()
