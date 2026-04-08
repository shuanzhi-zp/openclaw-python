# OpenClaw 快速启动指南

## 项目已完成

我已经成功用Python语言1:1还原了OpenClaw(龙虾)项目的核心功能。

## 项目位置

```
c:\Users\admin\Desktop\py_claw\openclaw\
```

## 已实现的核心模块

### 1. Gateway (网关服务器)
- WebSocket实时通信
- 身份验证系统
- RPC远程调用
- 连接管理

### 2. Channels (消息渠道)
- Console控制台渠道
- Telegram电报渠道
- 可扩展的渠道架构

### 3. LLM集成
- OpenAI GPT
- Anthropic Claude
- Ollama本地模型

### 4. Sessions (会话管理)
- 对话历史持久化
- 自动清理过期会话
- 多渠道会话跟踪

### 5. Plugins (插件系统)
- 动态加载插件
- 自定义RPC方法
- 消息处理钩子

### 6. Tools (工具执行)
- 沙箱安全执行
- 内置命令工具
- 可配置权限控制

### 7. CLI命令行工具
- openclaw start - 启动服务
- openclaw status - 查看状态
- openclaw init - 生成配置
- 等等...

## 快速开始

### 1. 安装依赖
```bash
cd c:\Users\admin\Desktop\py_claw\openclaw
pip install -e .
```

### 2. 验证安装
```bash
python verify_install.py
```

所有测试应该通过,显示:
```
[OK] All tests passed! OpenClaw is ready to use.
```

### 3. 生成配置文件
```bash
openclaw init
```

这会创建 `openclaw-config.yaml` 文件。

### 4. 配置LLM API密钥

编辑 `openclaw-config.yaml`:
```yaml
llms:
  default:
    provider: "openai"
    api_key: "sk-your-api-key-here"  # 填入你的API密钥
    model: "gpt-4"
```

或者设置环境变量:
```bash
set OPENCLAW_LLM_API_KEY=sk-your-api-key
```

### 5. 启动服务
```bash
openclaw start
```

服务将在 `ws://127.0.0.1:18789` 启动。

## 项目结构

```
openclaw/
├── src/openclaw/          # 源代码
│   ├── gateway/           # WebSocket网关
│   ├── channels/          # 消息渠道
│   ├── sessions/          # 会话管理
│   ├── llm/               # LLM集成
│   ├── plugins/           # 插件系统
│   ├── tools/             # 工具执行
│   ├── config/            # 配置管理
│   └── cli.py             # 命令行界面
├── examples/              # 示例代码
├── tests/                 # 测试文件
├── pyproject.toml         # 项目配置
├── README.md              # 详细文档
└── PROJECT_SUMMARY.md     # 项目总结
```

## 使用示例

### Python代码方式使用

```python
import asyncio
from openclaw import Config, GatewayServer

async def main():
    config = Config()
    config.gateway.port = 18789

    gateway = GatewayServer(config)
    await gateway.start()

    print("Gateway running...")
    while True:
        await asyncio.sleep(1)

asyncio.run(main())
```

### WebSocket客户端连接

```python
import asyncio
import json
import websockets

async def connect():
    async with websockets.connect("ws://localhost:18789") as ws:
        # 认证
        await ws.send(json.dumps({
            "type": "auth",
            "token": "your-token"
        }))

        # 发送消息
        await ws.send(json.dumps({
            "type": "rpc_call",
            "id": "1",
            "method": "ping",
            "params": {}
        }))

        response = await ws.recv()
        print(f"Response: {response}")

asyncio.run(connect())
```

### 创建自定义插件

```python
from openclaw.plugins import BasePlugin

class MyPlugin(BasePlugin):
    async def initialize(self):
        print("Plugin initialized")
        return True

    async def shutdown(self):
        print("Plugin shutdown")

    def get_rpc_methods(self):
        return {
            "my_method": self.handle_request
        }

    async def handle_method(self, **kwargs):
        return {"result": "success"}
```

## 技术特点

1. **异步优先**: 所有I/O操作都是异步的
2. **模块化设计**: 各组件独立可替换
3. **类型安全**: 完整的类型提示和Pydantic验证
4. **可扩展**: 插件系统便于功能扩展
5. **安全性**: 沙箱工具执行
6. **自托管**: 完全控制数据和API密钥

## 依赖项

主要依赖:
- websockets >= 12.0
- aiohttp >= 3.9.0
- pydantic >= 2.5.0
- click >= 8.1.0
- rich >= 13.7.0
- httpx >= 0.26.0
- pyyaml >= 6.0

## 测试运行

```bash
pytest tests/ -v
```

## 下一步

你可以:
1. 添加更多渠道适配器 (Discord, Slack等)
2. 创建自定义插件
3. 配置多个LLM提供商
4. 启用会话持久化
5. 部署到生产环境

## 文档

- `README.md` - 完整文档
- `PROJECT_SUMMARY.md` - 项目总结
- `examples/` - 代码示例
- `tests/` - 测试用例

## 版本信息

- **版本**: 2026.4.1
- **Python要求**: 3.10+
- **许可证**: MIT

---

项目已完全实现并通过验证,可以立即使用!
