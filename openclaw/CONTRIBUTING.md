# Contributing to OpenClaw

Thank you for your interest in contributing to OpenClaw! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/openclaw.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate it: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
5. Install dependencies: `pip install -e ".[dev]"`

## 📝 Development Workflow

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Run tests: `pytest tests/ -v`
4. Run linters: `black src/ && ruff check src/`
5. Commit your changes: `git commit -m "Add your message"`
6. Push to your fork: `git push origin feature/your-feature-name`
7. Open a Pull Request

## 🧪 Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Use descriptive test names

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=openclaw
```

## 💻 Code Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Write docstrings for functions and classes
- Keep functions focused and small

We use:
- **Black** for code formatting
- **Ruff** for linting
- **MyPy** for type checking

## 📖 Documentation

- Update documentation for user-facing changes
- Add docstrings to new functions/classes
- Include examples where helpful

## 🐛 Reporting Bugs

When reporting bugs, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

## 💡 Feature Requests

For feature requests, please:
- Explain the use case
- Describe the proposed solution
- Consider implementation complexity

## 🔒 Security

If you discover a security vulnerability, please:
- Do NOT open a public issue
- Email us privately at [YOUR_EMAIL]
- Allow time for a fix before disclosure

## 🎯 Areas Needing Help

- Adding new channel adapters (Discord, Slack, etc.)
- Writing more tests
- Improving documentation
- Creating example plugins
- Performance optimizations

## 📞 Questions?

Feel free to open an issue for questions or join discussions!

---

Thank you for contributing! 🎉
