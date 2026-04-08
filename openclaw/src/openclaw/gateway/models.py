"""Gateway models and message types."""

from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field
import time
import uuid


class MessageType(str, Enum):
    """Message types for WebSocket communication."""

    # Client to Server
    AUTH = "auth"
    RPC_CALL = "rpc_call"
    CHANNEL_MESSAGE = "channel_message"
    HEARTBEAT = "heartbeat"

    # Server to Client
    AUTH_RESPONSE = "auth_response"
    RPC_RESPONSE = "rpc_response"
    CHANNEL_EVENT = "channel_event"
    ERROR = "error"
    NOTIFICATION = "notification"


class AuthRequest(BaseModel):
    """Authentication request."""

    type: str = MessageType.AUTH
    token: str = Field(description="Authentication token")


class AuthResponse(BaseModel):
    """Authentication response."""

    type: str = MessageType.AUTH_RESPONSE
    success: bool = Field(description="Whether authentication succeeded")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class RPCCall(BaseModel):
    """RPC call request."""

    type: str = MessageType.RPC_CALL
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Request ID")
    method: str = Field(description="Method name to call")
    params: Dict[str, Any] = Field(default_factory=dict, description="Method parameters")


class RPCResponse(BaseModel):
    """RPC call response."""

    type: str = MessageType.RPC_RESPONSE
    id: str = Field(description="Request ID from the call")
    success: bool = Field(description="Whether the call succeeded")
    result: Optional[Any] = Field(default=None, description="Result data if successful")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class ChannelMessage(BaseModel):
    """Message from a channel."""

    type: str = MessageType.CHANNEL_MESSAGE
    channel: str = Field(description="Channel name (e.g., telegram, discord)")
    chat_id: str = Field(description="Chat/conversation ID")
    message_id: Optional[str] = Field(default=None, description="Message ID")
    sender: str = Field(description="Sender identifier")
    content: str = Field(description="Message content")
    timestamp: float = Field(default_factory=time.time, description="Message timestamp")
    attachments: List[Dict[str, Any]] = Field(default_factory=list, description="Message attachments")


class ChannelEvent(BaseModel):
    """Event notification to channels."""

    type: str = MessageType.CHANNEL_EVENT
    channel: str = Field(description="Target channel")
    chat_id: str = Field(description="Target chat ID")
    event: str = Field(description="Event type")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data")


class ErrorMessage(BaseModel):
    """Error message."""

    type: str = MessageType.ERROR
    code: str = Field(description="Error code")
    message: str = Field(description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")


class Notification(BaseModel):
    """Notification message."""

    type: str = MessageType.NOTIFICATION
    level: str = Field(default="info", description="Notification level (info, warning, error)")
    message: str = Field(description="Notification message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Additional data")


class Heartbeat(BaseModel):
    """Heartbeat message."""

    type: str = MessageType.HEARTBEAT
    timestamp: float = Field(default_factory=time.time, description="Current timestamp")
