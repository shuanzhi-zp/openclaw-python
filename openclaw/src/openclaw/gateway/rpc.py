"""RPC handler for processing remote procedure calls."""

import logging
import asyncio
from typing import Dict, Callable, Any, Optional, Awaitable
from .models import RPCCall, RPCResponse

logger = logging.getLogger(__name__)


class RPCHandler:
    """Handles RPC method registration and invocation."""

    def __init__(self):
        """Initialize RPC handler."""
        self.methods: Dict[str, Callable[..., Awaitable[Any]]] = {}
        self.pending_calls: Dict[str, asyncio.Future] = {}

    def register(self, name: str, func: Callable[..., Awaitable[Any]]) -> None:
        """Register an RPC method.

        Args:
            name: Method name
            func: Async function to call
        """
        self.methods[name] = func
        logger.debug(f"Registered RPC method: {name}")

    def unregister(self, name: str) -> bool:
        """Unregister an RPC method.

        Args:
            name: Method name to remove

        Returns:
            True if method was removed
        """
        if name in self.methods:
            del self.methods[name]
            logger.debug(f"Unregistered RPC method: {name}")
            return True
        return False

    async def handle_call(self, call: RPCCall) -> RPCResponse:
        """Handle an incoming RPC call.

        Args:
            call: RPC call request

        Returns:
            RPC response
        """
        logger.debug(f"RPC call: {call.method} (id: {call.id})")

        if call.method not in self.methods:
            return RPCResponse(
                id=call.id,
                success=False,
                error=f"Method not found: {call.method}",
            )

        try:
            result = await self.methods[call.method](**call.params)
            return RPCResponse(
                id=call.id,
                success=True,
                result=result,
            )
        except Exception as e:
            logger.error(f"RPC call failed: {call.method} - {e}", exc_info=True)
            return RPCResponse(
                id=call.id,
                success=False,
                error=str(e),
            )

    # Built-in RPC methods

    async def ping(self, **kwargs) -> Dict[str, Any]:
        """Ping endpoint for health check."""
        return {"status": "ok", "message": "pong"}

    async def get_status(self, **kwargs) -> Dict[str, Any]:
        """Get gateway status."""
        return {
            "status": "running",
            "methods_count": len(self.methods),
            "pending_calls": len(self.pending_calls),
        }

    async def list_methods(self, **kwargs) -> Dict[str, Any]:
        """List available RPC methods."""
        return {
            "methods": list(self.methods.keys()),
            "count": len(self.methods),
        }

    def register_builtins(self) -> None:
        """Register built-in RPC methods."""
        self.register("ping", self.ping)
        self.register("get_status", self.get_status)
        self.register("list_methods", self.list_methods)
