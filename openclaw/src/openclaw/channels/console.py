"""Console channel for testing and development."""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from .base import BaseChannel
from ..gateway.models import ChannelMessage
import time

logger = logging.getLogger(__name__)


class ConsoleChannel(BaseChannel):
    """Console-based channel for testing and development.

    Reads messages from stdin and outputs to stdout.
    """

    def __init__(self, name: str = "console", config: Dict[str, Any] = None):
        """Initialize console channel.

        Args:
            name: Channel name
            config: Configuration (unused for console)
        """
        super().__init__(name, config or {})
        self._read_task = None

    async def start(self) -> None:
        """Start reading from console."""
        self._running = True
        logger.info("Console channel started")

        # Start reading messages in background
        self._read_task = asyncio.create_task(self._read_loop())

    async def stop(self) -> None:
        """Stop the console channel."""
        self._running = False
        if self._read_task:
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass
        logger.info("Console channel stopped")

    async def _read_loop(self) -> None:
        """Continuously read messages from stdin."""
        loop = asyncio.get_event_loop()

        while self._running:
            try:
                # Read line from stdin
                line = await loop.run_in_executor(None, input, "> ")

                if line.strip():
                    message = ChannelMessage(
                        channel=self.name,
                        chat_id="console",
                        sender="user",
                        content=line.strip(),
                        timestamp=time.time(),
                    )
                    await self._handle_incoming_message(message)

            except EOFError:
                break
            except Exception as e:
                logger.error(f"Error reading from console: {e}")
                await asyncio.sleep(0.1)

    async def send_message(
        self,
        chat_id: str,
        content: str,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """Send a message to console.

        Args:
            chat_id: Chat ID (ignored for console)
            content: Message content
            attachments: Optional attachments

        Returns:
            True if message was sent
        """
        try:
            print(f"[Bot]: {content}")
            if attachments:
                print(f"[Attachments]: {attachments}")
            return True
        except Exception as e:
            logger.error(f"Error sending console message: {e}")
            return False
