"""
Quick verification script to test OpenClaw installation.
Run this after installing to verify everything works.
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        import openclaw
        print("[OK] openclaw")
    except ImportError as e:
        print(f"[FAIL] openclaw: {e}")
        return False

    try:
        from openclaw import Config, GatewayServer
        print("[OK] Config, GatewayServer")
    except ImportError as e:
        print(f"[FAIL] Core imports: {e}")
        return False

    try:
        from openclaw.config import Config
        from openclaw.gateway import GatewayServer, RPCHandler, ConnectionManager
        from openclaw.channels import BaseChannel, ChannelManager
        from openclaw.sessions import SessionManager, Session
        from openclaw.llm import LLMProvider, LLMManager
        from openclaw.plugins import BasePlugin, PluginManager
        from openclaw.tools import ToolSandbox, ToolExecutor
        print("[OK] All submodules")
    except ImportError as e:
        print(f"[FAIL] Submodule imports: {e}")
        return False

    return True


def test_config():
    """Test configuration system."""
    print("\nTesting configuration...")

    try:
        from openclaw import Config

        config = Config()
        assert config.gateway.host == "127.0.0.1"
        assert config.gateway.port == 18789
        print("✓ Default configuration")

        # Test config manipulation
        config.gateway.port = 9999
        assert config.gateway.port == 9999
        print("✓ Configuration modification")

        return True
    except Exception as e:
        print(f"✗ Configuration test: {e}")
        return False


def test_components():
    """Test component initialization."""
    print("\nTesting components...")

    try:
        from openclaw import Config
        from openclaw.gateway import GatewayServer, RPCHandler
        from openclaw.sessions import SessionManager
        from openclaw.tools import ToolExecutor

        config = Config()

        # Test Gateway
        gateway = GatewayServer(config)
        print("[OK] GatewayServer initialization")

        # Test RPC Handler
        rpc = RPCHandler()
        rpc.register_builtins()
        print("[OK] RPCHandler initialization")

        # Test Session Manager (no longer starts task in __init__)
        session_mgr = SessionManager(config)
        print("[OK] SessionManager initialization")

        # Test Tool Executor
        tool_exec = ToolExecutor(config)
        tools = tool_exec.list_tools()
        assert len(tools) > 0
        print(f"[OK] ToolExecutor initialization ({len(tools)} tools)")

        return True
    except Exception as e:
        print(f"[FAIL] Component test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("OpenClaw Installation Verification")
    print("=" * 60)

    results = []

    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Components", test_components()))

    print("\n" + "=" * 60)
    print("Results:")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        symbol = "[OK]" if passed else "[FAIL]"
        print(f"{symbol} {name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n[OK] All tests passed! OpenClaw is ready to use.")
        print("\nNext steps:")
        print("  1. Run: openclaw init")
        print("  2. Edit openclaw-config.yaml with your settings")
        print("  3. Run: openclaw start")
        return 0
    else:
        print("\n[FAIL] Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
