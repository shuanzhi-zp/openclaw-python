"""
Example: Creating a custom plugin

This example shows how to create a custom plugin that adds new functionality.
"""

from openclaw.plugins import BasePlugin
from typing import Dict, Any


class WeatherPlugin(BasePlugin):
    """Example plugin that provides weather information."""

    async def initialize(self) -> bool:
        """Initialize the weather plugin."""
        print("Weather plugin initialized")
        return True

    async def shutdown(self) -> None:
        """Shutdown the weather plugin."""
        print("Weather plugin shutdown")

    def get_rpc_methods(self) -> Dict[str, callable]:
        """Register RPC methods."""
        return {
            "get_weather": self.get_weather,
        }

    def get_tools(self) -> Dict[str, callable]:
        """Register tools."""
        return {
            "check_weather": self.check_weather,
        }

    async def get_weather(self, city: str, **kwargs) -> Dict[str, Any]:
        """Get weather for a city (mock implementation).

        Args:
            city: City name

        Returns:
            Weather information
        """
        # In a real plugin, you would call a weather API here
        return {
            "city": city,
            "temperature": 20,
            "condition": "sunny",
            "humidity": 60,
        }

    async def check_weather(self, city: str, **kwargs) -> Dict[str, Any]:
        """Tool to check weather.

        Args:
            city: City name

        Returns:
            Weather result
        """
        weather = await self.get_weather(city)
        return {
            "success": True,
            "weather": weather,
            "message": f"Weather in {city}: {weather['temperature']}°C, {weather['condition']}",
        }


# To use this plugin:
# 1. Save it as weather_plugin.py
# 2. Add to your config:
#    plugins:
#      weather_plugin.WeatherPlugin:
#        enabled: true
#        config: {}
