"""
示例: 如何在自己的应用中使用OpenClaw
"""
import asyncio
from openclaw import Config, GatewayServer
from openclaw.config.models import LLMConfig, ChannelConfig


async def main():
    # 1. 创建配置
    config = Config()

    # 配置LLM (使用你自己的API密钥)
    config.llms["default"] = LLMConfig(
        provider="openai",
        api_key="sk-your-api-key-here",  # 替换为你的API密钥
        model="gpt-3.5-turbo",
        temperature=0.7
    )

    # 启用控制台渠道
    config.channels["console"] = ChannelConfig(
        enabled=True,
        config={}
    )

    # 2. 创建并启动网关
    gateway = GatewayServer(config)

    print("=" * 60)
    print("OpenClaw 已启动!")
    print("=" * 60)
    print(f"WebSocket地址: ws://{config.gateway.host}:{config.gateway.port}")
    print("在控制台输入消息与AI对话")
    print("按 Ctrl+C 停止服务")
    print("=" * 60)

    try:
        await gateway.start()

        # 保持运行
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\n正在关闭...")
        await gateway.stop()
        print("再见!")


if __name__ == "__main__":
    asyncio.run(main())
