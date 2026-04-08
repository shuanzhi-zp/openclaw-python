"""
Example: WebSocket client for OpenClaw

This example shows how to connect to the OpenClaw gateway via WebSocket.
"""

import asyncio
import json
import websockets


async def main():
    """Connect to OpenClaw gateway and send messages."""

    uri = "ws://localhost:18789"
    auth_token = "your-auth-token"  # Set this in your config

    async with websockets.connect(uri) as websocket:
        print(f"Connected to {uri}")

        # Authenticate
        auth_message = {
            "type": "auth",
            "token": auth_token,
        }
        await websocket.send(json.dumps(auth_message))

        response = await websocket.recv()
        print(f"Auth response: {response}")

        # Send a ping
        ping_message = {
            "type": "rpc_call",
            "id": "1",
            "method": "ping",
            "params": {},
        }
        await websocket.send(json.dumps(ping_message))

        response = await websocket.recv()
        print(f"Ping response: {response}")

        # List available methods
        list_methods = {
            "type": "rpc_call",
            "id": "2",
            "method": "list_methods",
            "params": {},
        }
        await websocket.send(json.dumps(list_methods))

        response = await websocket.recv()
        print(f"Methods: {response}")

        # Send heartbeat
        heartbeat = {
            "type": "heartbeat",
        }
        await websocket.send(json.dumps(heartbeat))

        response = await websocket.recv()
        print(f"Heartbeat: {response}")

    print("Connection closed")


if __name__ == "__main__":
    asyncio.run(main())
