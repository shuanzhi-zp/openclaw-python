"""Telegram channel adapter."""

import logging
from typing import Optional, Dict, Any, List
import aiohttp
from .base import BaseChannel
from ..gateway.models import ChannelMessage

logger = logging.getLogger(__name__)


class TelegramChannel(BaseChannel):
    """Telegram bot channel adapter.

    Uses Telegram Bot API to send and receive messages.
    """

    def __init__(self, name: str = "telegram", config: Dict[str, Any] = None):
        """Initialize Telegram channel.

        Args:
            name: Channel name
            config: Configuration with 'bot_token' key
        """
        super().__init__(name, config or {})
        self.bot_token = self.config.get("bot_token")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self._session = None
        self._polling_task = None

    async def initialize(self) -> bool:
        """Initialize Telegram connection."""
        if not self.bot_token:
            logger.error("Telegram bot token not configured")
            return False

        # Test the token
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/getMe") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        logger.info(f"Telegram bot initialized: {data['result']['username']}")
                        return True
                    else:
                        logger.error(f"Invalid Telegram bot token: {resp.status}")
                        return False
        except Exception as e:
            logger.error(f"Failed to initialize Telegram: {e}")
            return False

    async def start(self) -> None:
        """Start polling for messages."""
        self._running = True
        self._session = aiohttp.ClientSession()

        # Delete any existing webhook
        await self._session.get(f"{self.base_url}/deleteWebhook")

        # Start polling
        self._polling_task = asyncio.create_task(self._poll_messages())
        logger.info("Telegram channel started")

    async def stop(self) -> None:
        """Stop the Telegram channel."""
        self._running = False

        if self._polling_task:
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass

        if self._session:
            await self._session.close()

        logger.info("Telegram channel stopped")

    async def _poll_messages(self) -> None:
        """Poll for new messages from Telegram."""
        offset = 0

        while self._running:
            try:
                url = f"{self.base_url}/getUpdates"
                params = {
                    "offset": offset,
                    "timeout": 30,
                    "allowed_updates": ["message"],
                }

                async with self._session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()

                        for update in data.get("result", []):
                            message = update.get("message")
                            if message:
                                await self._process_telegram_message(message)
                                offset = update["update_id"] + 1
                    else:
                        logger.error(f"Telegram API error: {resp.status}")
                        await asyncio.sleep(5)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error polling Telegram: {e}")
                await asyncio.sleep(5)

    async def _process_telegram_message(self, tg_message: dict) -> None:
        """Process a Telegram message.

        Args:
            tg_message: Telegram message object
        """
        chat = tg_message.get("chat", {})
        sender = tg_message.get("from", {})

        message = ChannelMessage(
            channel=self.name,
            chat_id=str(chat.get("id")),
            message_id=str(tg_message.get("message_id")),
            sender=str(sender.get("username") or sender.get("id")),
            content=tg_message.get("text", ""),
            timestamp=tg_message.get("date"),
        )

        await self._handle_incoming_message(message)

    async def send_message(
        self,
        chat_id: str,
        content: str,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """Send a message via Telegram.

        Args:
            chat_id: Target chat ID
            content: Message content
            attachments: Optional attachments

        Returns:
            True if message was sent
        """
        if not self._session:
            logger.error("Telegram session not initialized")
            return False

        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": content,
                "parse_mode": "Markdown",
            }

            async with self._session.post(url, json=data) as resp:
                if resp.status == 200:
                    return True
                else:
                    error_data = await resp.json()
                    logger.error(f"Failed to send Telegram message: {error_data}")
                    return False

        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
