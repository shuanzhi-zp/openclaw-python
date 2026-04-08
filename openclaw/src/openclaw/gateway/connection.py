"""Connection manager for WebSocket clients."""

import asyncio
import logging
from typing import Dict, Set, Optional
from datetime import datetime
import websockets
from websockets.asyncio.server import ServerConnection

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections to the gateway."""

    def __init__(self, max_connections: int = 100):
        """Initialize connection manager.

        Args:
            max_connections: Maximum number of concurrent connections
        """
        self.max_connections = max_connections
        self.connections: Dict[str, ServerConnection] = {}
        self.authenticated: Set[str] = {}
        self.connection_metadata: Dict[str, dict] = {}

    async def register(self, websocket: ServerConnection, client_id: str) -> bool:
        """Register a new connection.

        Args:
            websocket: WebSocket connection
            client_id: Unique client identifier

        Returns:
            True if registration succeeded, False otherwise
        """
        if len(self.connections) >= self.max_connections:
            logger.warning(f"Maximum connections ({self.max_connections}) reached")
            return False

        self.connections[client_id] = websocket
        self.connection_metadata[client_id] = {
            "connected_at": datetime.now(),
            "last_activity": datetime.now(),
            "authenticated": False,
        }

        logger.info(f"Client connected: {client_id} (total: {len(self.connections)})")
        return True

    async def unregister(self, client_id: str) -> None:
        """Unregister a connection.

        Args:
            client_id: Client identifier to remove
        """
        if client_id in self.connections:
            del self.connections[client_id]
        if client_id in self.authenticated:
            self.authenticated.discard(client_id)
        if client_id in self.connection_metadata:
            del self.connection_metadata[client_id]

        logger.info(f"Client disconnected: {client_id} (total: {len(self.connections)})")

    def mark_authenticated(self, client_id: str) -> None:
        """Mark a client as authenticated.

        Args:
            client_id: Client identifier
        """
        self.authenticated.add(client_id)
        if client_id in self.connection_metadata:
            self.connection_metadata[client_id]["authenticated"] = True

    def is_authenticated(self, client_id: str) -> bool:
        """Check if a client is authenticated.

        Args:
            client_id: Client identifier

        Returns:
            True if authenticated
        """
        return client_id in self.authenticated

    def update_activity(self, client_id: str) -> None:
        """Update last activity timestamp for a client.

        Args:
            client_id: Client identifier
        """
        if client_id in self.connection_metadata:
            self.connection_metadata[client_id]["last_activity"] = datetime.now()

    async def send_to_client(self, client_id: str, message: str) -> bool:
        """Send a message to a specific client.

        Args:
            client_id: Target client identifier
            message: Message to send

        Returns:
            True if message was sent successfully
        """
        if client_id not in self.connections:
            logger.warning(f"Client not found: {client_id}")
            return False

        try:
            await self.connections[client_id].send(message)
            self.update_activity(client_id)
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {client_id}: {e}")
            await self.unregister(client_id)
            return False

    async def broadcast(self, message: str, authenticated_only: bool = True) -> int:
        """Broadcast a message to all connected clients.

        Args:
            message: Message to broadcast
            authenticated_only: Only send to authenticated clients

        Returns:
            Number of clients message was sent to
        """
        sent_count = 0

        for client_id in list(self.connections.keys()):
            if authenticated_only and client_id not in self.authenticated:
                continue

            if await self.send_to_client(client_id, message):
                sent_count += 1

        return sent_count

    def get_connection_count(self) -> int:
        """Get total number of connections.

        Returns:
            Number of active connections
        """
        return len(self.connections)

    def get_authenticated_count(self) -> int:
        """Get number of authenticated connections.

        Returns:
            Number of authenticated clients
        """
        return len(self.authenticated)

    async def cleanup_stale_connections(self, timeout_seconds: int = 300) -> None:
        """Clean up connections that haven't had activity.

        Args:
            timeout_seconds: Timeout in seconds
        """
        now = datetime.now()
        stale_clients = []

        for client_id, metadata in self.connection_metadata.items():
            elapsed = (now - metadata["last_activity"]).total_seconds()
            if elapsed > timeout_seconds:
                stale_clients.append(client_id)

        for client_id in stale_clients:
            logger.info(f"Cleaning up stale connection: {client_id}")
            await self.unregister(client_id)
            if client_id in self.connections:
                try:
                    await self.connections[client_id].close()
                except Exception:
                    pass
