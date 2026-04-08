"""Plugin manager for loading and managing plugins."""

import logging
import importlib
from pathlib import Path
from typing import Dict, List, Optional, Type, Any
from ..config import Config
from .base import BasePlugin

logger = logging.getLogger(__name__)


class PluginManager:
    """Manages plugin lifecycle and discovery."""

    def __init__(self, config: Config):
        """Initialize plugin manager.

        Args:
            config: Application configuration
        """
        self.config = config
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_dirs: List[str] = []

    def add_plugin_directory(self, directory: str) -> None:
        """Add a directory to search for plugins.

        Args:
            directory: Directory path
        """
        self.plugin_dirs.append(directory)
        logger.info(f"Added plugin directory: {directory}")

    async def load_plugins(self) -> None:
        """Load all configured plugins."""
        # Load from config
        for name, plugin_config in self.config.plugins.items():
            if not plugin_config.enabled:
                logger.info(f"Plugin disabled in config: {name}")
                continue

            await self._load_plugin(name, plugin_config.config)

        # Auto-discover plugins from directories
        await self._discover_plugins()

    async def _load_plugin(self, name: str, config: dict) -> bool:
        """Load a specific plugin.

        Args:
            name: Plugin name/module path
            config: Plugin configuration

        Returns:
            True if plugin was loaded successfully
        """
        try:
            # Try to import the plugin module
            module = importlib.import_module(name)

            # Look for a Plugin class in the module
            plugin_class = getattr(module, "Plugin", None)

            if not plugin_class:
                # Try to find any class that inherits from BasePlugin
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, BasePlugin)
                        and attr != BasePlugin
                    ):
                        plugin_class = attr
                        break

            if not plugin_class:
                logger.error(f"No plugin class found in module: {name}")
                return False

            # Instantiate and enable the plugin
            plugin = plugin_class(name=name, config=config)

            if await plugin.enable():
                self.plugins[name] = plugin

                # Register RPC methods
                for method_name, method_func in plugin.get_rpc_methods().items():
                    logger.debug(f"Plugin {name} registered RPC method: {method_name}")

                # Register tools
                for tool_name, tool_func in plugin.get_tools().items():
                    logger.debug(f"Plugin {name} registered tool: {tool_name}")

                logger.info(f"Loaded plugin: {name} v{plugin.version}")
                return True
            else:
                logger.error(f"Failed to enable plugin: {name}")
                return False

        except Exception as e:
            logger.error(f"Error loading plugin {name}: {e}", exc_info=True)
            return False

    async def _discover_plugins(self) -> None:
        """Auto-discover plugins from plugin directories."""
        for plugin_dir in self.plugin_dirs:
            dir_path = Path(plugin_dir)

            if not dir_path.exists():
                continue

            # Look for Python files or directories with __init__.py
            for item in dir_path.iterdir():
                if item.is_file() and item.suffix == ".py" and not item.name.startswith("_"):
                    await self._try_load_plugin_file(item)
                elif item.is_dir() and (item / "__init__.py").exists():
                    await self._try_load_plugin_package(item)

    async def _try_load_plugin_file(self, filepath: Path) -> None:
        """Try to load a plugin from a Python file.

        Args:
            filepath: Path to Python file
        """
        try:
            spec = importlib.util.spec_from_file_location(filepath.stem, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find plugin class
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BasePlugin)
                    and attr != BasePlugin
                ):
                    plugin = attr(name=filepath.stem, config={})
                    if await plugin.enable():
                        self.plugins[filepath.stem] = plugin
                        logger.info(f"Auto-discovered plugin: {filepath.stem}")
                    break

        except Exception as e:
            logger.error(f"Error loading plugin file {filepath}: {e}")

    async def _try_load_plugin_package(self, dir_path: Path) -> None:
        """Try to load a plugin from a package directory.

        Args:
            dir_path: Path to plugin package
        """
        try:
            module = importlib.import_module(dir_path.name)

            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BasePlugin)
                    and attr != BasePlugin
                ):
                    plugin = attr(name=dir_path.name, config={})
                    if await plugin.enable():
                        self.plugins[dir_path.name] = plugin
                        logger.info(f"Auto-discovered plugin: {dir_path.name}")
                    break

        except Exception as e:
            logger.error(f"Error loading plugin package {dir_path}: {e}")

    async def unload_plugin(self, name: str) -> bool:
        """Unload a plugin.

        Args:
            name: Plugin name

        Returns:
            True if plugin was unloaded
        """
        if name not in self.plugins:
            return False

        plugin = self.plugins[name]
        await plugin.disable()
        del self.plugins[name]

        logger.info(f"Unloaded plugin: {name}")
        return True

    async def reload_plugin(self, name: str) -> bool:
        """Reload a plugin.

        Args:
            name: Plugin name

        Returns:
            True if plugin was reloaded
        """
        if name in self.plugins:
            await self.unload_plugin(name)

        return await self._load_plugin(name, {})

    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """Get a plugin by name.

        Args:
            name: Plugin name

        Returns:
            Plugin instance or None
        """
        return self.plugins.get(name)

    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all loaded plugins.

        Returns:
            List of plugin info dictionaries
        """
        return [plugin.get_info() for plugin in self.plugins.values()]

    async def process_message(self, message: dict) -> Optional[dict]:
        """Process a message through all plugins.

        Args:
            message: Message dictionary

        Returns:
            Processed message or None to drop
        """
        current_message = message

        for name, plugin in self.plugins.items():
            try:
                result = await plugin.on_message(current_message)
                if result is None:
                    logger.debug(f"Plugin {name} dropped message")
                    return None
                current_message = result
            except Exception as e:
                logger.error(f"Error in plugin {name} on_message: {e}")

        return current_message

    async def process_response(self, response: dict) -> Optional[dict]:
        """Process a response through all plugins.

        Args:
            response: Response dictionary

        Returns:
            Processed response or None to drop
        """
        current_response = response

        for name, plugin in self.plugins.items():
            try:
                result = await plugin.on_response(current_response)
                if result is None:
                    logger.debug(f"Plugin {name} dropped response")
                    return None
                current_response = result
            except Exception as e:
                logger.error(f"Error in plugin {name} on_response: {e}")

        return current_response

    async def shutdown_all(self) -> None:
        """Shutdown all plugins."""
        for name in list(self.plugins.keys()):
            await self.unload_plugin(name)
