"""Session and message models."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import time
import uuid


class Message(BaseModel):
    """Chat message model."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Message ID")
    role: str = Field(description="Message role (user, assistant, system)")
    content: str = Field(description="Message content")
    timestamp: float = Field(default_factory=time.time, description="Message timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class Session(BaseModel):
    """Chat session model."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Session ID")
    channel: str = Field(description="Channel name")
    chat_id: str = Field(description="Chat/conversation ID")
    messages: List[Message] = Field(default_factory=list, description="Message history")
    created_at: float = Field(default_factory=time.time, description="Session creation time")
    last_activity: float = Field(default_factory=time.time, description="Last activity time")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Session metadata")

    def add_message(self, role: str, content: str, **kwargs) -> Message:
        """Add a message to the session.

        Args:
            role: Message role
            content: Message content
            **kwargs: Additional message metadata

        Returns:
            Created message
        """
        message = Message(
            role=role,
            content=content,
            metadata=kwargs,
        )
        self.messages.append(message)
        self.last_activity = time.time()
        return message

    def get_recent_messages(self, count: int = 10) -> List[Message]:
        """Get most recent messages.

        Args:
            count: Number of messages to retrieve

        Returns:
            List of recent messages
        """
        return self.messages[-count:]

    def clear_history(self) -> None:
        """Clear message history."""
        self.messages.clear()

    def to_llm_messages(self) -> List[Dict[str, str]]:
        """Convert session messages to LLM format.

        Returns:
            List of message dictionaries for LLM API
        """
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.messages
        ]
