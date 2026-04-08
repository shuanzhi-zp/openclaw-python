"""
OpenClaw - Your own personal AI assistant. Any OS. Any Platform.

An open-source AI agent framework that connects multiple channels to various LLMs
with a plugin architecture and sandboxed tool execution.
"""

__version__ = "2026.4.1"
__author__ = "OpenClaw Team"

from .gateway import GatewayServer
from .config import Config

__all__ = ["GatewayServer", "Config"]
