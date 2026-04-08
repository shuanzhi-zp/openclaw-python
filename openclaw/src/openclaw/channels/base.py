"""Base channel adapter interface."""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from ..gateway.models import ChannelMessage

logger = logging.getLogger(__name__)


class BaseChannel(ABC):
    """Base class for all channel adapters."""

    def __init__(self, name: str, config: Dict[str, Any]):
        """Initialize channel adapter.

        Args:
            name: Channel name (e.g., 'telegram', 'discord')
            config: Channel-specific configuration
        """
        self.name = name
        self.config = config
        self._running = False
        self._message_callback = None

    @abstractmethod
    async def start(self) -> None:
        """Start the channel adapter."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the channel adapter."""
        pass

    @abstractmethod
    async def send_message(
        self,
        chat_id: str,
        content: str,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """Send a message to a chat.

        Args:
            chat_id: Target chat ID
            content: Message content
            attachments: Optional attachments

        Returns:
            True if message was sent successfully
        """
        pass

    def set_message_callback(self, callback) -> None:
        """Set callback for incoming messages.

        Args:
            callback: Async function to call when message is received
        """
        self._message_callback = callback

    async def _handle_incoming_message(self, message: ChannelMessage) -> None:
        """Handle an incoming message by calling the registered callback.

        Args:
            message: Incoming message
        """
        if self._message_callback:
            try:
                await self._message_callback(message)
            except Exception as e:
                logger.error(f"Error in message callback for {self.name}: {e}", exc_info=True)
        else:
            logger.warning(f"No message callback registered for channel: {self.name}")

    @property
    def is_running(self) -> bool:
        """Check if channel is running."""
        return self._running

    async def initialize(self) -> bool:
        """Initialize the channel (validate config, setup connections).

        Returns:
            True if initialization succeeded
        """
        return True
