"""
Example: Basic OpenClaw usage

This example demonstrates how to use OpenClaw programmatically.
"""

import asyncio
from openclaw import Config, GatewayServer


async def main():
    # Create configuration
    config = Config()
    config.gateway.host = "127.0.0.1"
    config.gateway.port = 18789

    # Add an LLM provider
    from openclaw.config.models import LLMConfig
    config.llms["default"] = LLMConfig(
        provider="openai",
        api_key="your-api-key-here",
        model="gpt-4",
    )

    # Create and start gateway
    gateway = GatewayServer(config)

    try:
        await gateway.start()
        print("Gateway started! Press Ctrl+C to stop.")

        # Keep running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down...")
        await gateway.stop()


if __name__ == "__main__":
    asyncio.run(main())
