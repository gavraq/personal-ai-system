"""
WebSocket Connection Manager
Manages WebSocket connections with support for multiple concurrent clients
"""

from typing import Dict, List, Optional, Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger("risk-agents-api")


class ConnectionManager:
    """
    Manages WebSocket connections for real-time communication

    Features:
    - Multiple concurrent connections
    - Connection tracking by session ID
    - Broadcast messaging to all connections
    - Targeted messaging to specific sessions
    - Automatic cleanup on disconnect
    - Connection health monitoring
    """

    def __init__(self):
        """Initialize the connection manager"""
        # Active connections: {session_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}

        # Connection metadata: {session_id: metadata}
        self.connection_metadata: Dict[str, Dict] = {}

        # Message buffer for offline clients: {session_id: [messages]}
        self.message_buffer: Dict[str, List[Dict]] = {}

        # Maximum buffered messages per session
        self.max_buffer_size = 100

    async def connect(
        self,
        websocket: WebSocket,
        session_id: str,
        user_id: Optional[str] = None
    ) -> None:
        """
        Accept and register a new WebSocket connection

        Args:
            websocket: The WebSocket connection
            session_id: Unique session identifier
            user_id: Optional user identifier for authentication
        """
        await websocket.accept()

        # Store connection
        self.active_connections[session_id] = websocket

        # Store metadata
        self.connection_metadata[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "connected_at": datetime.now(),
            "last_activity": datetime.now(),
            "message_count": 0
        }

        # Deliver buffered messages if any
        if session_id in self.message_buffer:
            buffered_messages = self.message_buffer.pop(session_id)
            for message in buffered_messages:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.warning(f"Failed to deliver buffered message to {session_id}: {e}")

        logger.info(f"WebSocket connected: {session_id} (user: {user_id})")
        logger.info(f"Active connections: {len(self.active_connections)}")

    def disconnect(self, session_id: str) -> None:
        """
        Remove a WebSocket connection

        Args:
            session_id: Session identifier to disconnect
        """
        if session_id in self.active_connections:
            del self.active_connections[session_id]

        if session_id in self.connection_metadata:
            metadata = self.connection_metadata.pop(session_id)
            duration = (datetime.now() - metadata["connected_at"]).total_seconds()
            logger.info(
                f"WebSocket disconnected: {session_id} "
                f"(duration: {duration:.1f}s, messages: {metadata['message_count']})"
            )

        logger.info(f"Active connections: {len(self.active_connections)}")

    async def send_personal_message(
        self,
        message: Dict,
        session_id: str,
        buffer_if_offline: bool = True
    ) -> bool:
        """
        Send a message to a specific session

        Args:
            message: Message dictionary to send
            session_id: Target session ID
            buffer_if_offline: If True, buffer message for offline sessions

        Returns:
            True if message sent successfully, False otherwise
        """
        # Update last activity
        if session_id in self.connection_metadata:
            self.connection_metadata[session_id]["last_activity"] = datetime.now()
            self.connection_metadata[session_id]["message_count"] += 1

        # Try to send immediately if connected
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json(message)
                return True
            except WebSocketDisconnect:
                # Connection lost during send
                self.disconnect(session_id)
            except Exception as e:
                logger.error(f"Failed to send message to {session_id}: {e}")
                self.disconnect(session_id)

        # Buffer message if offline and buffering enabled
        if buffer_if_offline:
            if session_id not in self.message_buffer:
                self.message_buffer[session_id] = []

            # Add message to buffer (maintain max size)
            self.message_buffer[session_id].append(message)
            if len(self.message_buffer[session_id]) > self.max_buffer_size:
                self.message_buffer[session_id].pop(0)  # Remove oldest

            logger.info(
                f"Message buffered for offline session {session_id} "
                f"(buffer size: {len(self.message_buffer[session_id])})"
            )

        return False

    async def broadcast(self, message: Dict, exclude: Optional[Set[str]] = None) -> int:
        """
        Broadcast a message to all connected sessions

        Args:
            message: Message dictionary to broadcast
            exclude: Optional set of session IDs to exclude

        Returns:
            Number of sessions that received the message
        """
        exclude = exclude or set()
        sent_count = 0
        disconnected = []

        for session_id, websocket in self.active_connections.items():
            if session_id in exclude:
                continue

            try:
                await websocket.send_json(message)
                sent_count += 1

                # Update metadata
                if session_id in self.connection_metadata:
                    self.connection_metadata[session_id]["last_activity"] = datetime.now()
                    self.connection_metadata[session_id]["message_count"] += 1

            except WebSocketDisconnect:
                disconnected.append(session_id)
            except Exception as e:
                logger.error(f"Broadcast failed for {session_id}: {e}")
                disconnected.append(session_id)

        # Clean up disconnected sessions
        for session_id in disconnected:
            self.disconnect(session_id)

        if disconnected:
            logger.info(f"Broadcast cleaned up {len(disconnected)} disconnected sessions")

        return sent_count

    def is_connected(self, session_id: str) -> bool:
        """
        Check if a session is currently connected

        Args:
            session_id: Session ID to check

        Returns:
            True if session is connected, False otherwise
        """
        return session_id in self.active_connections

    def get_connection_count(self) -> int:
        """
        Get the number of active connections

        Returns:
            Number of active WebSocket connections
        """
        return len(self.active_connections)

    def get_session_metadata(self, session_id: str) -> Optional[Dict]:
        """
        Get metadata for a specific session

        Args:
            session_id: Session ID

        Returns:
            Metadata dictionary or None if session not found
        """
        return self.connection_metadata.get(session_id)

    def get_all_sessions(self) -> List[str]:
        """
        Get list of all connected session IDs

        Returns:
            List of session IDs
        """
        return list(self.active_connections.keys())

    def get_buffered_message_count(self, session_id: str) -> int:
        """
        Get the number of buffered messages for a session

        Args:
            session_id: Session ID

        Returns:
            Number of buffered messages
        """
        return len(self.message_buffer.get(session_id, []))

    def clear_buffer(self, session_id: str) -> int:
        """
        Clear buffered messages for a session

        Args:
            session_id: Session ID

        Returns:
            Number of messages cleared
        """
        if session_id in self.message_buffer:
            count = len(self.message_buffer[session_id])
            del self.message_buffer[session_id]
            return count
        return 0

    async def send_keepalive(self, session_id: str) -> bool:
        """
        Send a keepalive ping to a session

        Args:
            session_id: Session ID

        Returns:
            True if ping sent successfully, False otherwise
        """
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json({
                    "type": "keepalive",
                    "timestamp": datetime.now().isoformat()
                })
                return True
            except Exception as e:
                logger.warning(f"Keepalive failed for {session_id}: {e}")
                self.disconnect(session_id)
        return False

    async def broadcast_keepalive(self) -> int:
        """
        Send keepalive pings to all connected sessions

        Returns:
            Number of sessions that received keepalive
        """
        return await self.broadcast({
            "type": "keepalive",
            "timestamp": datetime.now().isoformat()
        })

    def get_statistics(self) -> Dict:
        """
        Get connection manager statistics

        Returns:
            Dictionary with connection statistics
        """
        total_buffered = sum(len(msgs) for msgs in self.message_buffer.values())
        total_messages = sum(
            meta.get("message_count", 0)
            for meta in self.connection_metadata.values()
        )

        return {
            "active_connections": len(self.active_connections),
            "total_buffered_messages": total_buffered,
            "sessions_with_buffer": len(self.message_buffer),
            "total_messages_sent": total_messages,
            "connected_sessions": self.get_all_sessions()
        }
