"""Channel manager for handling multiple channel adapters."""

import logging
from typing import Dict, Optional, Type, List
from ..config import Config
from .base import BaseChannel

logger = logging.getLogger(__name__)


class ChannelManager:
    """Manages multiple channel adapters."""

    def __init__(self, config: Config):
        """Initialize channel manager.

        Args:
            config: Application configuration
        """
        self.config = config
        self.channels: Dict[str, BaseChannel] = {}
        self.channel_types: Dict[str, Type[BaseChannel]] = {}

    def register_channel_type(self, name: str, channel_class: Type[BaseChannel]) -> None:
        """Register a channel type.

        Args:
            name: Channel type name
            channel_class: Channel class
        """
        self.channel_types[name] = channel_class
        logger.debug(f"Registered channel type: {name}")

    async def initialize_channels(self) -> None:
        """Initialize all configured channels."""
        for name, channel_config in self.config.channels.items():
            if not channel_config.enabled:
                logger.info(f"Channel disabled: {name}")
                continue

            if name not in self.channel_types:
                logger.warning(f"Unknown channel type: {name}")
                continue

            try:
                channel_class = self.channel_types[name]
                channel = channel_class(name=name, config=channel_config.config)

                if await channel.initialize():
                    self.channels[name] = channel
                    logger.info(f"Initialized channel: {name}")
                else:
                    logger.error(f"Failed to initialize channel: {name}")

            except Exception as e:
                logger.error(f"Error initializing channel {name}: {e}", exc_info=True)

    async def start_all(self) -> None:
        """Start all initialized channels."""
        for name, channel in self.channels.items():
            try:
                await channel.start()
                logger.info(f"Started channel: {name}")
            except Exception as e:
                logger.error(f"Error starting channel {name}: {e}", exc_info=True)

    async def stop_all(self) -> None:
        """Stop all channels."""
        for name, channel in self.channels.items():
            try:
                await channel.stop()
                logger.info(f"Stopped channel: {name}")
            except Exception as e:
                logger.error(f"Error stopping channel {name}: {e}", exc_info=True)

    def get_channel(self, name: str) -> Optional[BaseChannel]:
        """Get a channel by name.

        Args:
            name: Channel name

        Returns:
            Channel instance or None
        """
        return self.channels.get(name)

    def list_channels(self) -> List[str]:
        """List all active channels.

        Returns:
            List of channel names
        """
        return list(self.channels.keys())

    def set_message_callback(self, channel_name: str, callback) -> bool:
        """Set message callback for a channel.

        Args:
            channel_name: Channel name
            callback: Message callback function

        Returns:
            True if callback was set
        """
        channel = self.get_channel(channel_name)
        if channel:
            channel.set_message_callback(callback)
            return True
        return False
