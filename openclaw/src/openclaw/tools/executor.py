"""Tool executor for managing and executing various tools."""

import logging
from typing import Dict, Callable, Any, Optional, Awaitable
from .sandbox import ToolSandbox
from ..config import Config

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Manages tool registration and execution."""

    def __init__(self, config: Config):
        """Initialize tool executor.

        Args:
            config: Application configuration
        """
        self.config = config
        self.sandbox = ToolSandbox(config)
        self.tools: Dict[str, Callable[..., Awaitable[Any]]] = {}

        # Register built-in tools
        self._register_builtin_tools()

    def _register_builtin_tools(self) -> None:
        """Register built-in tools."""
        self.register("execute_command", self._tool_execute_command)
        self.register("read_file", self._tool_read_file)
        self.register("list_directory", self._tool_list_directory)

    def register(self, name: str, func: Callable[..., Awaitable[Any]]) -> None:
        """Register a tool.

        Args:
            name: Tool name
            func: Async function to execute
        """
        self.tools[name] = func
        logger.debug(f"Registered tool: {name}")

    def unregister(self, name: str) -> bool:
        """Unregister a tool.

        Args:
            name: Tool name

        Returns:
            True if tool was removed
        """
        if name in self.tools:
            del self.tools[name]
            return True
        return False

    async def execute(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool.

        Args:
            tool_name: Name of tool to execute
            **kwargs: Tool parameters

        Returns:
            Execution result
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool not found: {tool_name}",
            }

        try:
            result = await self.tools[tool_name](**kwargs)
            return {
                "success": True,
                "result": result,
            }
        except Exception as e:
            logger.error(f"Tool execution error: {tool_name} - {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    def list_tools(self) -> Dict[str, str]:
        """List available tools.

        Returns:
            Dictionary mapping tool names to descriptions
        """
        return {
            "execute_command": "Execute a shell command",
            "read_file": "Read contents of a file",
            "list_directory": "List files in a directory",
            **{name: "Custom tool" for name in self.tools.keys() if name not in [
                "execute_command", "read_file", "list_directory"
            ]},
        }

    # Built-in tools

    async def _tool_execute_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """Execute a shell command.

        Args:
            command: Command to execute
            **kwargs: Additional parameters

        Returns:
            Command execution result
        """
        return await self.sandbox.execute_command(command)

    async def _tool_read_file(self, filepath: str, **kwargs) -> str:
        """Read a file.

        Args:
            filepath: Path to file
            **kwargs: Additional parameters

        Returns:
            File contents
        """
        import asyncio

        def read_sync():
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, read_sync)

    async def _tool_list_directory(self, path: str, **kwargs) -> list:
        """List directory contents.

        Args:
            path: Directory path
            **kwargs: Additional parameters

        Returns:
            List of files and directories
        """
        import asyncio
        from pathlib import Path

        def list_sync():
            p = Path(path)
            if not p.exists():
                return []
            return [str(item) for item in p.iterdir()]

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, list_sync)
