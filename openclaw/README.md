# 🦞 OpenClaw (Python Edition)

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

**Your own personal AI assistant. Any OS. Any Platform.**

OpenClaw is an open-source AI agent framework that connects multiple messaging channels to various LLM providers with a plugin architecture and sandboxed tool execution.

---

## 🌟 Features

- 📱 **Multi-Channel Support**: Console, Telegram, Discord, and more
- 🤖 **Multiple LLM Providers**: OpenAI, Anthropic Claude, Alibaba Qwen, Ollama
- 🔌 **Plugin System**: Extend functionality with custom plugins
- 🔒 **Sandboxed Execution**: Safe tool execution with configurable restrictions
- 💬 **Session Management**: Persistent conversation history
- ⚡ **WebSocket Gateway**: Real-time bidirectional communication
- 🏠 **Self-Hosted**: Complete control over your data and API keys

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/openclaw.git
cd openclaw

# Install dependencies
pip install -e .

# Verify installation
python verify_install.py
```

### Configuration

```bash
# Generate configuration file
openclaw init

# Edit config and add your LLM API key
# See docs/ALIBABA_CLOUD_GUIDE.md for Alibaba Cloud setup
```

### Run

```bash
# Start the gateway server
openclaw start

# Or use custom config
openclaw start --config my-config.yaml
```

## 📖 Documentation

- [Quick Start Guide](QUICKSTART.md) - Get started in 5 minutes
- [Alibaba Cloud Setup](docs/ALIBABA_CLOUD_GUIDE.md) - Configure Qwen LLM
- [Project Summary](PROJECT_SUMMARY.md) - Architecture overview
- [Examples](examples/) - Code examples and tutorials

## 🛠️ Usage Examples

### Console Chat

```bash
openclaw start
> Hello!
[Bot]: Hi there! How can I help you?
```

### Telegram Bot

```yaml
# openclaw-config.yaml
channels:
  telegram:
    enabled: true
    config:
      bot_token: "YOUR_BOT_TOKEN"
```

### Python API

```python
from openclaw import Config, GatewayServer

config = Config()
gateway = GatewayServer(config)
await gateway.start()
```

## 🏗️ Architecture

```
openclaw/
├── src/openclaw/
│   ├── gateway/          # WebSocket server & RPC
│   ├── channels/         # Messaging adapters
│   ├── plugins/          # Plugin system
│   ├── sessions/         # Session management
│   ├── llm/              # LLM providers
│   ├── tools/            # Tool execution
│   └── config/           # Configuration
├── examples/             # Code examples
├── tests/                # Test suite
└── docs/                 # Documentation
```

## 🔧 Supported LLM Providers

| Provider | Models | Setup Guide |
|----------|--------|-------------|
| OpenAI | GPT-4, GPT-3.5 | Built-in |
| Anthropic | Claude 3 | Built-in |
| Alibaba | Qwen series | [Guide](docs/ALIBABA_CLOUD_GUIDE.md) |
| Ollama | Local models | Built-in |

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_config.py -v
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the original OpenClaw project
- Built with modern Python async features
- Community-driven development

## 📞 Support

- 📖 Read the [documentation](docs/)
- 💬 Open an [issue](https://github.com/YOUR_USERNAME/openclaw/issues)
- ⭐ Star this repo if you find it helpful!

---

**Made with ❤️ by the OpenClaw Team**
