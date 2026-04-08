"""简单的WebSocket客户端测试"""
import asyncio
import json
import websockets


async def chat_with_openclaw():
    """连接到OpenClaw并发送消息"""

    uri = "ws://localhost:18789"

    try:
        async with websockets.connect(uri) as websocket:
            print(f"已连接到 {uri}\n")

            # 步骤1: 认证 (如果配置了auth_token需要提供)
            auth_message = {
                "type": "auth",
                "token": ""  # 如果config中设置了auth_token,在这里填写
            }
            await websocket.send(json.dumps(auth_message))

            response = await websocket.recv()
            print(f"认证响应: {response}\n")

            # 步骤2: 测试RPC调用 - ping
            print("测试RPC ping...")
            ping_msg = {
                "type": "rpc_call",
                "id": "1",
                "method": "ping",
                "params": {}
            }
            await websocket.send(json.dumps(ping_msg))

            response = await websocket.recv()
            print(f"Ping响应: {response}\n")

            # 步骤3: 查看可用的RPC方法
            print("查看可用方法...")
            list_msg = {
                "type": "rpc_call",
                "id": "2",
                "method": "list_methods",
                "params": {}
            }
            await websocket.send(json.dumps(list_msg))

            response = await websocket.recv()
            print(f"可用方法: {response}\n")

            # 步骤4: 发送聊天消息
            print("发送聊天消息...")
            chat_msg = {
                "type": "channel_message",
                "channel": "console",
                "chat_id": "user1",
                "sender": "test_user",
                "content": "你好,请简单回复我"
            }
            await websocket.send(json.dumps(chat_msg))

            # 等待响应 (在实际应用中,响应会通过channel发送回去)
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"聊天响应: {response}")
            except asyncio.TimeoutError:
                print("等待响应超时(这是正常的,消息已发送)")

            print("\n测试完成!")

    except ConnectionRefusedError:
        print("错误: 无法连接到OpenClaw服务器")
        print("请确保已运行 'openclaw start' 启动服务")
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    asyncio.run(chat_with_openclaw())
