"""Example plugin demonstrating plugin capabilities."""

import logging
from typing import Dict, Any, List
from .base import BasePlugin

logger = logging.getLogger(__name__)


class ExamplePlugin(BasePlugin):
    """Example plugin that adds custom commands and tools."""

    async def initialize(self) -> bool:
        """Initialize the example plugin."""
        logger.info("Example plugin initialized")
        return True

    async def shutdown(self) -> None:
        """Shutdown the example plugin."""
        logger.info("Example plugin shutdown")

    def get_rpc_methods(self) -> Dict[str, callable]:
        """Get RPC methods provided by this plugin."""
        return {
            "example_ping": self.rpc_ping,
            "example_info": self.rpc_info,
        }

    def get_tools(self) -> Dict[str, callable]:
        """Get tools provided by this plugin."""
        return {
            "example_calculate": self.tool_calculate,
        }

    def get_commands(self) -> List[Dict[str, Any]]:
        """Get chat commands provided by this plugin."""
        return [
            {
                "command": "/example",
                "description": "Example command from plugin",
                "handler": self.handle_example_command,
            },
            {
                "command": "/help",
                "description": "Show help information",
                "handler": self.handle_help_command,
            },
        ]

    # RPC Methods

    async def rpc_ping(self, **kwargs) -> Dict[str, Any]:
        """Example RPC ping method.

        Returns:
            Ping response
        """
        return {
            "status": "ok",
            "message": "pong from example plugin",
            "plugin": self.name,
            "version": self.version,
        }

    async def rpc_info(self, **kwargs) -> Dict[str, Any]:
        """Get plugin information.

        Returns:
            Plugin info
        """
        return self.get_info()

    # Tools

    async def tool_calculate(self, expression: str, **kwargs) -> Dict[str, Any]:
        """Safely evaluate a mathematical expression.

        Args:
            expression: Mathematical expression to evaluate

        Returns:
            Calculation result
        """
        try:
            # Only allow safe characters
            allowed_chars = set("0123456789+-*/(). ")
            if not all(c in allowed_chars for c in expression):
                return {
                    "success": False,
                    "error": "Invalid characters in expression",
                }

            result = eval(expression)
            return {
                "success": True,
                "expression": expression,
                "result": result,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    # Command Handlers

    async def handle_example_command(self, args: str) -> str:
        """Handle /example command.

        Args:
            args: Command arguments

        Returns:
            Response message
        """
        return f"Hello from Example Plugin v{self.version}! You said: {args}"

    async def handle_help_command(self, args: str) -> str:
        """Handle /help command.

        Args:
            args: Command arguments

        Returns:
            Help message
        """
        commands = self.get_commands()
        help_text = "Available commands:\n\n"

        for cmd in commands:
            help_text += f"{cmd['command']} - {cmd['description']}\n"

        return help_text
