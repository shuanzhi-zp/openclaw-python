"""
OpenClaw 使用演示
展示启动后的各种使用方式
"""

print("""
================================================================================
                     OpenClaw 使用指南
================================================================================

启动服务后,你有以下几种使用方式:

方式1: 控制台直接对话 (最简单)
----------------------------------------
启动命令: openclaw start

你会看到提示符 > ,直接输入消息即可:
  > 你好
  [Bot]: 你好!有什么可以帮助你的吗?
  > 帮我写一个Python函数
  [Bot]: def hello(): ...


方式2: WebSocket客户端编程访问
----------------------------------------
运行测试脚本: python test_client.py

或在你的代码中连接:
  import websockets
  async with websockets.connect("ws://localhost:18789") as ws:
      # 认证
      await ws.send('{"type": "auth", "token": ""}')
      # 发送消息
      await ws.send('{"type": "channel_message", ...}')


方式3: Telegram机器人
----------------------------------------
1. 在Telegram找 @BotFather 创建机器人,获取token
2. 编辑 openclaw-config.yaml:
   channels:
     telegram:
       enabled: true
       config:
         bot_token: "YOUR_TOKEN"
3. 重启服务: openclaw start
4. 在Telegram中搜索你的机器人并开始对话!


方式4: 集成到你的应用
----------------------------------------
见 example_app.py 文件,展示了如何:
- 配置LLM提供商
- 启用渠道
- 以编程方式启动网关


方式5: 自定义插件扩展
----------------------------------------
见 examples/custom_plugin.py
可以添加:
- 新的RPC方法
- 自定义工具
- 聊天命令处理


常用RPC方法:
----------------------------------------
- ping: 健康检查
- get_status: 获取服务状态
- list_methods: 列出所有可用方法
- list_sessions: 查看活跃会话
- list_providers: 查看LLM提供商
- list_tools: 查看可用工具


配置文件位置:
----------------------------------------
openclaw-config.yaml - 主配置文件
.env - 环境变量(可选)


需要帮助?
----------------------------------------
- 查看 README.md 完整文档
- 查看 QUICKSTART.md 快速开始
- 运行 openclaw --help 查看CLI帮助
- 运行 openclaw status 查看当前状态

================================================================================
""")

# 检查服务是否运行
import subprocess
import sys

def check_service():
    """检查OpenClaw服务是否在运行"""
    print("\n正在检查OpenClaw服务状态...\n")

    try:
        # 尝试连接到WebSocket
        import asyncio
        import websockets

        async def test_connection():
            try:
                async with websockets.connect("ws://localhost:18789", close_timeout=1):
                    return True
            except:
                return False

        is_running = asyncio.run(test_connection())

        if is_running:
            print("[OK] OpenClaw服务正在运行!")
            print("\n你现在可以:")
            print("  1. 在当前终端直接输入消息对话")
            print("  2. 打开新终端运行: python test_client.py")
            print("  3. 通过配置的Telegram机器人对话")
        else:
            print("[INFO] OpenClaw服务未运行")
            print("\n启动服务:")
            print("  openclaw start")
            print("\n或者运行演示应用:")
            print("  python example_app.py")

    except ImportError:
        print("[WARN] 无法检查服务状态(websockets未安装)")
    except Exception as e:
        print(f"[INFO] {e}")


if __name__ == "__main__":
    check_service()
