"""Session manager for handling chat sessions."""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Optional, Dict, List
from ..config import Config
from .models import Session, Message

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages chat sessions with persistence and cleanup."""

    def __init__(self, config: Config):
        """Initialize session manager.

        Args:
            config: Application configuration
        """
        self.config = config
        self.sessions: Dict[str, Session] = {}
        self.storage_path = config.session.storage_path
        self._cleanup_task = None

        # Create storage directory if needed
        if self.storage_path:
            Path(self.storage_path).mkdir(parents=True, exist_ok=True)

    async def start(self) -> None:
        """Start the session manager (cleanup task)."""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    def get_or_create_session(self, channel: str, chat_id: str) -> Session:
        """Get existing session or create a new one.

        Args:
            channel: Channel name
            chat_id: Chat ID

        Returns:
            Session instance
        """
        session_key = f"{channel}:{chat_id}"

        if session_key in self.sessions:
            session = self.sessions[session_key]
            session.last_activity = time.time()
            return session

        # Create new session
        session = Session(channel=channel, chat_id=chat_id)
        self.sessions[session_key] = session

        logger.info(f"Created new session: {session_key}")
        return session

    def get_session(self, channel: str, chat_id: str) -> Optional[Session]:
        """Get an existing session.

        Args:
            channel: Channel name
            chat_id: Chat ID

        Returns:
            Session instance or None
        """
        session_key = f"{channel}:{chat_id}"
        return self.sessions.get(session_key)

    def delete_session(self, channel: str, chat_id: str) -> bool:
        """Delete a session.

        Args:
            channel: Channel name
            chat_id: Chat ID

        Returns:
            True if session was deleted
        """
        session_key = f"{channel}:{chat_id}"

        if session_key in self.sessions:
            # Save before deleting if storage is enabled
            if self.storage_path:
                self._save_session(self.sessions[session_key])

            del self.sessions[session_key]
            logger.info(f"Deleted session: {session_key}")
            return True

        return False

    def add_message(
        self,
        channel: str,
        chat_id: str,
        role: str,
        content: str,
        **metadata,
    ) -> Message:
        """Add a message to a session.

        Args:
            channel: Channel name
            chat_id: Chat ID
            role: Message role
            content: Message content
            **metadata: Additional metadata

        Returns:
            Created message
        """
        session = self.get_or_create_session(channel, chat_id)

        # Enforce max history limit
        if len(session.messages) >= self.config.session.max_history:
            # Remove oldest messages
            excess = len(session.messages) - self.config.session.max_history + 1
            session.messages = session.messages[excess:]

        message = session.add_message(role, content, **metadata)

        # Auto-save if storage is enabled
        if self.storage_path:
            self._save_session(session)

        return message

    def get_session_messages(self, channel: str, chat_id: str, count: int = 10) -> List[Message]:
        """Get recent messages from a session.

        Args:
            channel: Channel name
            chat_id: Chat ID
            count: Number of messages to retrieve

        Returns:
            List of recent messages
        """
        session = self.get_session(channel, chat_id)
        if not session:
            return []

        return session.get_recent_messages(count)

    def clear_session_history(self, channel: str, chat_id: str) -> bool:
        """Clear message history for a session.

        Args:
            channel: Channel name
            chat_id: Chat ID

        Returns:
            True if history was cleared
        """
        session = self.get_session(channel, chat_id)
        if not session:
            return False

        session.clear_history()

        if self.storage_path:
            self._save_session(session)

        return True

    def _save_session(self, session: Session) -> None:
        """Save session to disk.

        Args:
            session: Session to save
        """
        if not self.storage_path:
            return

        try:
            session_file = Path(self.storage_path) / f"{session.id}.json"
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(session.model_dump(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save session {session.id}: {e}")

    def load_session(self, session_id: str) -> Optional[Session]:
        """Load a session from disk.

        Args:
            session_id: Session ID

        Returns:
            Loaded session or None
        """
        if not self.storage_path:
            return None

        try:
            session_file = Path(self.storage_path) / f"{session_id}.json"
            if not session_file.exists():
                return None

            with open(session_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            session = Session(**data)
            session_key = f"{session.channel}:{session.chat_id}"
            self.sessions[session_key] = session

            logger.info(f"Loaded session: {session_id}")
            return session

        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")
            return None

    async def stop(self) -> None:
        """Stop the session manager (cleanup task)."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

    async def _cleanup_loop(self) -> None:
        """Periodically clean up expired sessions."""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                await self._cleanup_expired_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")

    async def _cleanup_expired_sessions(self) -> None:
        """Remove expired sessions."""
        now = time.time()
        timeout = self.config.session.timeout
        expired_keys = []

        for key, session in self.sessions.items():
            if now - session.last_activity > timeout:
                expired_keys.append(key)

        for key in expired_keys:
            session = self.sessions[key]
            logger.info(f"Cleaning up expired session: {key}")

            if self.storage_path:
                self._save_session(session)

            del self.sessions[key]

    def get_active_session_count(self) -> int:
        """Get number of active sessions.

        Returns:
            Number of active sessions
        """
        return len(self.sessions)
