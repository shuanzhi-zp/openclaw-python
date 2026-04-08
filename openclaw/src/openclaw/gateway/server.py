"""Gateway WebSocket server."""

import asyncio
import json
import logging
import uuid
from typing import Optional, Dict, Any
import websockets
from websockets.asyncio.server import ServerConnection, serve

from ..config import Config
from .connection import ConnectionManager
from .rpc import RPCHandler
from .models import (
    MessageType,
    AuthRequest,
    AuthResponse,
    RPCCall,
    RPCResponse,
    ChannelMessage,
    ErrorMessage,
    Heartbeat,
)

logger = logging.getLogger(__name__)


class GatewayServer:
    """Main gateway server handling WebSocket connections and message routing."""

    def __init__(self, config: Config):
        """Initialize gateway server.

        Args:
            config: Application configuration
        """
        self.config = config
        self.connection_manager = ConnectionManager(
            max_connections=config.gateway.max_connections
        )
        self.rpc_handler = RPCHandler()
        self.rpc_handler.register_builtins()

        # Callbacks for channel messages
        self.channel_callbacks: Dict[str, callable] = {}

        # Server instance
        self.server = None
        self._running = False

    async def start(self) -> None:
        """Start the gateway server."""
        host = self.config.gateway.host
        port = self.config.gateway.port

        logger.info(f"Starting Gateway on {host}:{port}")

        self.server = await serve(
            self._handle_connection,
            host,
            port,
            ping_interval=self.config.gateway.heartbeat_interval,
            ping_timeout=10,
        )

        self._running = True
        logger.info(f"Gateway started successfully on ws://{host}:{port}")

        # Start cleanup task
        asyncio.create_task(self._cleanup_loop())

    async def stop(self) -> None:
        """Stop the gateway server."""
        self._running = False

        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("Gateway stopped")

    async def _handle_connection(self, websocket: ServerConnection) -> None:
        """Handle a new WebSocket connection.

        Args:
            websocket: WebSocket connection
        """
        client_id = str(uuid.uuid4())

        try:
            # Register connection
            if not await self.connection_manager.register(websocket, client_id):
                await websocket.close(1008, "Maximum connections reached")
                return

            # Handle messages
            async for message in websocket:
                await self._handle_message(client_id, message)

        except websockets.exceptions.ConnectionClosed:
            logger.debug(f"Connection closed: {client_id}")
        except Exception as e:
            logger.error(f"Error handling connection {client_id}: {e}", exc_info=True)
        finally:
            await self.connection_manager.unregister(client_id)

    async def _handle_message(self, client_id: str, raw_message: str) -> None:
        """Process an incoming message.

        Args:
            client_id: Client identifier
            raw_message: Raw message string
        """
        try:
            data = json.loads(raw_message)
            msg_type = data.get("type")

            if not msg_type:
                await self._send_error(client_id, "invalid_request", "Missing message type")
                return

            # Route message based on type
            if msg_type == MessageType.AUTH:
                await self._handle_auth(client_id, data)
            elif msg_type == MessageType.RPC_CALL:
                await self._handle_rpc_call(client_id, data)
            elif msg_type == MessageType.CHANNEL_MESSAGE:
                await self._handle_channel_message(client_id, data)
            elif msg_type == MessageType.HEARTBEAT:
                await self._handle_heartbeat(client_id)
            else:
                await self._send_error(client_id, "unknown_type", f"Unknown message type: {msg_type}")

        except json.JSONDecodeError:
            await self._send_error(client_id, "invalid_json", "Invalid JSON format")
        except Exception as e:
            logger.error(f"Error processing message from {client_id}: {e}", exc_info=True)
            await self._send_error(client_id, "internal_error", str(e))

    async def _handle_auth(self, client_id: str, data: dict) -> None:
        """Handle authentication request.

        Args:
            client_id: Client identifier
            data: Message data
        """
        try:
            auth_req = AuthRequest(**data)
            expected_token = self.config.gateway.auth_token

            # If no token configured, allow all connections
            if expected_token is None or auth_req.token == expected_token:
                self.connection_manager.mark_authenticated(client_id)
                response = AuthResponse(success=True)
                await self.connection_manager.send_to_client(
                    client_id, response.model_dump_json()
                )
                logger.info(f"Client authenticated: {client_id}")
            else:
                response = AuthResponse(success=False, error="Invalid token")
                await self.connection_manager.send_to_client(
                    client_id, response.model_dump_json()
                )
                logger.warning(f"Authentication failed for client: {client_id}")

        except Exception as e:
            response = AuthResponse(success=False, error=str(e))
            await self.connection_manager.send_to_client(
                client_id, response.model_dump_json()
            )

    async def _handle_rpc_call(self, client_id: str, data: dict) -> None:
        """Handle RPC call.

        Args:
            client_id: Client identifier
            data: Message data
        """
        # Check authentication
        if not self.connection_manager.is_authenticated(client_id):
            await self._send_error(client_id, "not_authenticated", "Client not authenticated")
            return

        try:
            rpc_call = RPCCall(**data)
            response = await self.rpc_handler.handle_call(rpc_call)
            await self.connection_manager.send_to_client(
                client_id, response.model_dump_json()
            )
        except Exception as e:
            await self._send_error(client_id, "rpc_error", str(e))

    async def _handle_channel_message(self, client_id: str, data: dict) -> None:
        """Handle channel message.

        Args:
            client_id: Client identifier
            data: Message data
        """
        # Check authentication
        if not self.connection_manager.is_authenticated(client_id):
            await self._send_error(client_id, "not_authenticated", "Client not authenticated")
            return

        try:
            msg = ChannelMessage(**data)

            # Call registered callback if exists
            if msg.channel in self.channel_callbacks:
                await self.channel_callbacks[msg.channel](msg)
            else:
                logger.warning(f"No callback registered for channel: {msg.channel}")

        except Exception as e:
            await self._send_error(client_id, "channel_error", str(e))

    async def _handle_heartbeat(self, client_id: str) -> None:
        """Handle heartbeat message.

        Args:
            client_id: Client identifier
        """
        self.connection_manager.update_activity(client_id)
        heartbeat = Heartbeat()
        await self.connection_manager.send_to_client(
            client_id, heartbeat.model_dump_json()
        )

    async def _send_error(self, client_id: str, code: str, message: str) -> None:
        """Send error message to client.

        Args:
            client_id: Client identifier
            code: Error code
            message: Error message
        """
        error = ErrorMessage(code=code, message=message)
        await self.connection_manager.send_to_client(client_id, error.model_dump_json())

    async def _cleanup_loop(self) -> None:
        """Periodically clean up stale connections."""
        while self._running:
            try:
                await asyncio.sleep(60)  # Check every minute
                await self.connection_manager.cleanup_stale_connections(
                    timeout_seconds=self.config.gateway.heartbeat_interval * 5
                )
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    def register_channel_callback(self, channel: str, callback: callable) -> None:
        """Register a callback for channel messages.

        Args:
            channel: Channel name
            callback: Async callback function
        """
        self.channel_callbacks[channel] = callback
        logger.info(f"Registered callback for channel: {channel}")

    def register_rpc_method(self, name: str, func: callable) -> None:
        """Register an RPC method.

        Args:
            name: Method name
            func: Async function
        """
        self.rpc_handler.register(name, func)

    async def send_to_channel(self, channel: str, chat_id: str, event: str, data: dict) -> bool:
        """Send event to a specific channel.

        Args:
            channel: Target channel
            chat_id: Chat ID
            event: Event type
            data: Event data

        Returns:
            True if sent successfully
        """
        from .models import ChannelEvent

        event_msg = ChannelEvent(
            channel=channel,
            chat_id=chat_id,
            event=event,
            data=data,
        )

        count = await self.connection_manager.broadcast(
            event_msg.model_dump_json(),
            authenticated_only=True,
        )

        logger.debug(f"Sent channel event to {count} clients")
        return count > 0
