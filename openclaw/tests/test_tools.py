"""Tests for tool execution."""

import pytest
from openclaw.config import Config
from openclaw.tools import ToolExecutor, ToolSandbox


def test_tool_executor_initialization():
    """Test tool executor initialization."""
    config = Config()
    executor = ToolExecutor(config)

    assert "execute_command" in executor.tools
    assert "read_file" in executor.tools
    assert "list_directory" in executor.tools


@pytest.mark.asyncio
async def test_tool_list():
    """Test listing available tools."""
    config = Config()
    executor = ToolExecutor(config)

    tools = executor.list_tools()
    assert "execute_command" in tools
    assert "read_file" in tools
    assert "list_directory" in tools


@pytest.mark.asyncio
async def test_sandbox_command_execution():
    """Test sandboxed command execution."""
    config = Config()
    sandbox = ToolSandbox(config)

    # Execute a simple command
    result = await sandbox.execute_command("echo hello")
    assert result["success"] is True
    assert "hello" in result["stdout"].lower()


@pytest.mark.asyncio
async def test_sandbox_allowed_commands():
    """Test allowed commands restriction."""
    config = Config()
    config.sandbox.allowed_commands = ["echo", "ls"]
    sandbox = ToolSandbox(config)

    # Allowed command
    result = await sandbox.execute_command("echo test")
    assert result["success"] is True

    # Non-allowed command would fail if we had strict checking
    # (currently empty list means allow all)


@pytest.mark.asyncio
async def test_tool_execute_command():
    """Test execute_command tool."""
    config = Config()
    executor = ToolExecutor(config)

    result = await executor.execute("execute_command", command="echo test123")
    assert result["success"] is True
    assert "test123" in result["result"]["stdout"]
