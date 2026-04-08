"""Configuration models for OpenClaw."""

from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field


class GatewayConfig(BaseModel):
    """Gateway server configuration."""

    host: str = Field(default="127.0.0.1", description="Gateway host address")
    port: int = Field(default=18789, description="Gateway port number")
    auth_token: Optional[str] = Field(default=None, description="Authentication token")
    max_connections: int = Field(default=100, description="Maximum concurrent connections")
    heartbeat_interval: int = Field(default=30, description="Heartbeat interval in seconds")


class ChannelConfig(BaseModel):
    """Channel adapter configuration."""

    enabled: bool = Field(default=False, description="Whether channel is enabled")
    config: Dict[str, Any] = Field(default_factory=dict, description="Channel-specific configuration")


class LLMConfig(BaseModel):
    """LLM provider configuration."""

    provider: str = Field(description="LLM provider name (e.g., openai, anthropic)")
    api_key: Optional[str] = Field(default=None, description="API key for the provider")
    model: str = Field(default="gpt-4", description="Model identifier")
    base_url: Optional[str] = Field(default=None, description="Custom API base URL")
    temperature: float = Field(default=0.7, description="Sampling temperature")
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens to generate")


class PluginConfig(BaseModel):
    """Plugin configuration."""

    enabled: bool = Field(default=True, description="Whether plugin is enabled")
    config: Dict[str, Any] = Field(default_factory=dict, description="Plugin-specific configuration")


class SessionConfig(BaseModel):
    """Session management configuration."""

    max_history: int = Field(default=50, description="Maximum message history per session")
    timeout: int = Field(default=3600, description="Session timeout in seconds")
    storage_path: Optional[str] = Field(default=None, description="Path to store session data")


class SandboxConfig(BaseModel):
    """Tool execution sandbox configuration."""

    enabled: bool = Field(default=True, description="Enable sandboxed execution")
    allowed_commands: List[str] = Field(default_factory=list, description="Allowed shell commands")
    timeout: int = Field(default=30, description="Command execution timeout in seconds")
    working_directory: Optional[str] = Field(default=None, description="Working directory for commands")
