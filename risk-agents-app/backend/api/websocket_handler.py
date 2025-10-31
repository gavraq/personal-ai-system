"""
WebSocket Handler
Real-time bidirectional communication for query streaming
"""

from fastapi import WebSocket, WebSocketDisconnect, Query
from typing import Optional, Dict, Any
from datetime import datetime
import logging
import json
import asyncio

from api.connection_manager import ConnectionManager
from agent import RiskAgentClient

logger = logging.getLogger("risk-agents-api")

# Global connection manager (initialized on startup)
connection_manager: Optional[ConnectionManager] = None
agent_client: Optional[RiskAgentClient] = None


def initialize_websocket_handler(client: RiskAgentClient) -> ConnectionManager:
    """
    Initialize WebSocket handler with agent client

    Args:
        client: RiskAgentClient instance for query execution

    Returns:
        Initialized ConnectionManager
    """
    global connection_manager, agent_client
    agent_client = client
    connection_manager = ConnectionManager()
    logger.info("✅ WebSocket handler initialized")
    return connection_manager


async def handle_websocket_connection(
    websocket: WebSocket,
    session_id: str = Query(..., description="Session ID for this connection"),
    user_id: Optional[str] = Query(None, description="Optional user ID for authentication")
) -> None:
    """
    Handle WebSocket connection lifecycle

    This endpoint provides bidirectional streaming communication with the following features:
    - Real-time query streaming (send queries, receive streaming responses)
    - Session-based conversation history
    - Message buffering for offline reconnection
    - Keepalive pings for connection health
    - Error handling and graceful disconnection

    **Connection URL**:
    ```
    ws://localhost:8050/ws?session_id=abc123&user_id=user1
    ```

    **Message Format** (Client → Server):
    ```json
    {
      "type": "query",
      "query": "Help me analyze this document",
      "session_id": "abc123",
      "include_context": true,
      "system_prompt": "You are a helpful assistant"
    }
    ```

    **Message Format** (Server → Client):
    ```json
    {
      "type": "chunk|complete|error|keepalive",
      "content": "Response text...",
      "session_id": "abc123",
      "timestamp": "2025-10-25T12:34:56"
    }
    ```

    **Message Types**:
    - `query`: Client sends a query to execute
    - `chunk`: Server sends a streaming response chunk
    - `complete`: Server signals query completion
    - `error`: Server reports an error
    - `keepalive`: Server sends periodic keepalive ping
    - `disconnect`: Client requests disconnection

    Args:
        websocket: WebSocket connection
        session_id: Unique session identifier (required query param)
        user_id: Optional user identifier for authentication (query param)
    """
    # Connect client
    await connection_manager.connect(websocket, session_id, user_id)

    # Send welcome message
    await connection_manager.send_personal_message(
        {
            "type": "connected",
            "message": "WebSocket connection established",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        },
        session_id,
        buffer_if_offline=False
    )

    try:
        # Main message loop
        while True:
            # Receive message from client
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
            except json.JSONDecodeError as e:
                await connection_manager.send_personal_message(
                    {
                        "type": "error",
                        "error": f"Invalid JSON: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    },
                    session_id,
                    buffer_if_offline=False
                )
                continue

            # Handle different message types
            message_type = message.get("type")

            if message_type == "query":
                # Execute streaming query
                await handle_query_message(websocket, message, session_id)

            elif message_type == "ping":
                # Respond to ping with pong
                await connection_manager.send_personal_message(
                    {
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    },
                    session_id,
                    buffer_if_offline=False
                )

            elif message_type == "disconnect":
                # Client requested disconnect
                await connection_manager.send_personal_message(
                    {
                        "type": "disconnected",
                        "message": "Disconnect acknowledged",
                        "timestamp": datetime.now().isoformat()
                    },
                    session_id,
                    buffer_if_offline=False
                )
                break

            else:
                # Unknown message type
                await connection_manager.send_personal_message(
                    {
                        "type": "error",
                        "error": f"Unknown message type: {message_type}",
                        "timestamp": datetime.now().isoformat()
                    },
                    session_id,
                    buffer_if_offline=False
                )

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {session_id}: {e}")
        try:
            await connection_manager.send_personal_message(
                {
                    "type": "error",
                    "error": f"Server error: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                },
                session_id,
                buffer_if_offline=False
            )
        except:
            pass
    finally:
        # Clean up connection
        connection_manager.disconnect(session_id)


async def handle_query_message(
    websocket: WebSocket,
    message: Dict[str, Any],
    session_id: str
) -> None:
    """
    Handle a query message by streaming the response

    Args:
        websocket: WebSocket connection
        message: Query message from client
        session_id: Session ID
    """
    query = message.get("query")
    if not query:
        await connection_manager.send_personal_message(
            {
                "type": "error",
                "error": "Missing 'query' field in message",
                "timestamp": datetime.now().isoformat()
            },
            session_id,
            buffer_if_offline=False
        )
        return

    if agent_client is None:
        await connection_manager.send_personal_message(
            {
                "type": "error",
                "error": "Agent client not initialized",
                "timestamp": datetime.now().isoformat()
            },
            session_id,
            buffer_if_offline=False
        )
        return

    # Extract optional parameters
    system_prompt = message.get("system_prompt")
    context = message.get("context")

    # Send query start notification
    await connection_manager.send_personal_message(
        {
            "type": "query_start",
            "query": query,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        },
        session_id,
        buffer_if_offline=False
    )

    try:
        # Stream response chunks
        chunk_count = 0
        full_response = []

        for chunk in agent_client.query_stream(
            user_message=query,
            context=context,
            system_prompt=system_prompt
        ):
            chunk_count += 1
            full_response.append(chunk)

            # Send chunk to client
            await connection_manager.send_personal_message(
                {
                    "type": "chunk",
                    "content": chunk,
                    "chunk_number": chunk_count,
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                },
                session_id,
                buffer_if_offline=False
            )

        # Send completion notification
        await connection_manager.send_personal_message(
            {
                "type": "complete",
                "full_response": "".join(full_response),
                "total_chunks": chunk_count,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            },
            session_id,
            buffer_if_offline=False
        )

        logger.info(f"Query completed for {session_id}: {chunk_count} chunks")

    except Exception as e:
        logger.error(f"Query execution failed for {session_id}: {e}")
        await connection_manager.send_personal_message(
            {
                "type": "error",
                "error": f"Query execution failed: {str(e)}",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            },
            session_id,
            buffer_if_offline=False
        )


async def websocket_health_check() -> Dict[str, Any]:
    """
    Get WebSocket connection statistics

    Returns:
        Dictionary with WebSocket health and statistics
    """
    if connection_manager is None:
        return {
            "status": "uninitialized",
            "active_connections": 0
        }

    stats = connection_manager.get_statistics()

    return {
        "status": "healthy",
        "active_connections": stats["active_connections"],
        "total_buffered_messages": stats["total_buffered_messages"],
        "sessions_with_buffer": stats["sessions_with_buffer"],
        "total_messages_sent": stats["total_messages_sent"]
    }
