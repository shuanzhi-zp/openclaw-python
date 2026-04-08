"""Tests for gateway module."""

import pytest
import asyncio
from openclaw.config import Config
from openclaw.gateway import GatewayServer, ConnectionManager, RPCHandler


def test_rpc_handler():
    """Test RPC handler registration and calls."""
    handler = RPCHandler()
    handler.register_builtins()

    assert "ping" in handler.methods
    assert "get_status" in handler.methods
    assert "list_methods" in handler.methods


@pytest.mark.asyncio
async def test_rpc_ping():
    """Test RPC ping method."""
    handler = RPCHandler()
    handler.register_builtins()

    result = await handler.ping()
    assert result["status"] == "ok"
    assert result["message"] == "pong"


def test_connection_manager():
    """Test connection manager initialization."""
    manager = ConnectionManager(max_connections=10)
    assert manager.max_connections == 10
    assert manager.get_connection_count() == 0
    assert manager.get_authenticated_count() == 0


def test_config_initialization():
    """Test gateway initialization with config."""
    config = Config()
    gateway = GatewayServer(config)

    assert gateway.config == config
    assert gateway.connection_manager is not None
    assert gateway.rpc_handler is not None
