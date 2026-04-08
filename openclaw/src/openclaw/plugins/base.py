"""Base plugin interface."""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class BasePlugin(ABC):
    """Base class for all plugins.

    Plugins can extend OpenClaw functionality by:
    - Adding new RPC methods
    - Processing messages
    - Providing custom tools
    - Hooking into lifecycle events
    """

    def __init__(self, name: str, version: str = "1.0.0", config: Dict[str, Any] = None):
        """Initialize plugin.

        Args:
            name: Plugin name
            version: Plugin version
            config: Plugin configuration
        """
        self.name = name
        self.version = version
        self.config = config or {}
        self._enabled = False

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the plugin.

        Returns:
            True if initialization succeeded
        """
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the plugin."""
        pass

    async def on_message(self, message: dict) -> Optional[dict]:
        """Process an incoming message.

        Override this method to intercept and modify messages.

        Args:
            message: Message dictionary

        Returns:
            Modified message or None to drop the message
        """
        return message

    async def on_response(self, response: dict) -> Optional[dict]:
        """Process an outgoing response.

        Override this method to intercept and modify responses.

        Args:
            response: Response dictionary

        Returns:
            Modified response or None to drop the response
        """
        return response

    def get_rpc_methods(self) -> Dict[str, callable]:
        """Get RPC methods provided by this plugin.

        Returns:
            Dictionary mapping method names to functions
        """
        return {}

    def get_tools(self) -> Dict[str, callable]:
        """Get tools provided by this plugin.

        Returns:
            Dictionary mapping tool names to functions
        """
        return {}

    def get_commands(self) -> List[Dict[str, Any]]:
        """Get chat commands provided by this plugin.

        Returns:
            List of command definitions
        """
        return []

    @property
    def is_enabled(self) -> bool:
        """Check if plugin is enabled."""
        return self._enabled

    async def enable(self) -> bool:
        """Enable the plugin.

        Returns:
            True if plugin was enabled successfully
        """
        if self._enabled:
            return True

        try:
            if await self.initialize():
                self._enabled = True
                logger.info(f"Plugin enabled: {self.name} v{self.version}")
                return True
            else:
                logger.error(f"Failed to enable plugin: {self.name}")
                return False
        except Exception as e:
            logger.error(f"Error enabling plugin {self.name}: {e}", exc_info=True)
            return False

    async def disable(self) -> None:
        """Disable the plugin."""
        if not self._enabled:
            return

        try:
            await self.shutdown()
            self._enabled = False
            logger.info(f"Plugin disabled: {self.name}")
        except Exception as e:
            logger.error(f"Error disabling plugin {self.name}: {e}", exc_info=True)

    def get_info(self) -> Dict[str, Any]:
        """Get plugin information.

        Returns:
            Plugin info dictionary
        """
        return {
            "name": self.name,
            "version": self.version,
            "enabled": self._enabled,
            "config": self.config,
        }
