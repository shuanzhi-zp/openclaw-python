"""Sandboxed tool execution environment."""

import asyncio
import logging
import shlex
from typing import Optional, Dict, Any, List
from ..config import Config

logger = logging.getLogger(__name__)


class ToolSandbox:
    """Provides sandboxed execution for shell commands and tools."""

    def __init__(self, config: Config):
        """Initialize tool sandbox.

        Args:
            config: Application configuration
        """
        self.config = config
        self.enabled = config.sandbox.enabled
        self.allowed_commands = config.sandbox.allowed_commands
        self.timeout = config.sandbox.timeout
        self.working_directory = config.sandbox.working_directory

    async def execute_command(
        self,
        command: str,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Execute a shell command in sandbox.

        Args:
            command: Command to execute
            cwd: Working directory (overrides config)
            env: Environment variables

        Returns:
            Dictionary with 'success', 'stdout', 'stderr', 'returncode'
        """
        if not self.enabled:
            return await self._execute_unsafe(command, cwd, env)

        # Validate command
        if not self._is_command_allowed(command):
            logger.warning(f"Command not allowed: {command}")
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command not allowed: {command}",
                "returncode": -1,
            }

        return await self._execute_safe(command, cwd, env)

    async def _execute_safe(
        self,
        command: str,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Execute command with safety restrictions.

        Args:
            command: Command to execute
            cwd: Working directory
            env: Environment variables

        Returns:
            Execution result
        """
        try:
            # Parse command safely
            args = shlex.split(command)

            # Set working directory
            work_dir = cwd or self.working_directory

            # Create subprocess
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=work_dir,
                env=env,
            )

            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout,
                )

                return {
                    "success": process.returncode == 0,
                    "stdout": stdout.decode("utf-8", errors="replace"),
                    "stderr": stderr.decode("utf-8", errors="replace"),
                    "returncode": process.returncode,
                }

            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Command timed out after {self.timeout} seconds",
                    "returncode": -1,
                }

        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
            }

    async def _execute_unsafe(
        self,
        command: str,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Execute command without sandbox (when disabled).

        Args:
            command: Command to execute
            cwd: Working directory
            env: Environment variables

        Returns:
            Execution result
        """
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                env=env,
            )

            stdout, stderr = await process.communicate()

            return {
                "success": process.returncode == 0,
                "stdout": stdout.decode("utf-8", errors="replace"),
                "stderr": stderr.decode("utf-8", errors="replace"),
                "returncode": process.returncode,
            }

        except Exception as e:
            logger.error(f"Unsafe command execution error: {e}")
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
            }

    def _is_command_allowed(self, command: str) -> bool:
        """Check if a command is allowed.

        Args:
            command: Command to check

        Returns:
            True if command is allowed
        """
        # If no allowed commands specified, allow all
        if not self.allowed_commands:
            return True

        # Extract command name
        try:
            cmd_name = shlex.split(command)[0]
        except Exception:
            return False

        # Check against allowed list
        return cmd_name in self.allowed_commands

    def add_allowed_command(self, command: str) -> None:
        """Add a command to the allowed list.

        Args:
            command: Command name to allow
        """
        if command not in self.allowed_commands:
            self.allowed_commands.append(command)
            logger.info(f"Added allowed command: {command}")

    def remove_allowed_command(self, command: str) -> bool:
        """Remove a command from the allowed list.

        Args:
            command: Command name to remove

        Returns:
            True if command was removed
        """
        if command in self.allowed_commands:
            self.allowed_commands.remove(command)
            logger.info(f"Removed allowed command: {command}")
            return True
        return False
