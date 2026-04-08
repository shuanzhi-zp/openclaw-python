"""Tests for configuration module."""

import pytest
import tempfile
from pathlib import Path
from openclaw.config import Config
from openclaw.config.models import LLMConfig


def test_default_config():
    """Test default configuration."""
    config = Config()
    assert config.gateway.host == "127.0.0.1"
    assert config.gateway.port == 18789
    assert len(config.channels) == 0
    assert len(config.llms) == 0


def test_config_from_dict():
    """Test creating config from dictionary."""
    data = {
        "gateway": {
            "host": "0.0.0.0",
            "port": 8080,
        },
        "llms": {
            "default": {
                "provider": "openai",
                "api_key": "test-key",
                "model": "gpt-4",
            }
        },
    }

    config = Config.from_dict(data)
    assert config.gateway.host == "0.0.0.0"
    assert config.gateway.port == 8080
    assert "default" in config.llms
    assert config.llms["default"].provider == "openai"


def test_config_save_load():
    """Test saving and loading configuration."""
    config = Config()
    config.llms["test"] = LLMConfig(
        provider="openai",
        api_key="test-key",
        model="gpt-4",
    )

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_path = f.name

    try:
        # Save config
        config.save_to_file(temp_path)

        # Load config
        loaded_config = Config(config_path=temp_path)
        assert "test" in loaded_config.llms
        assert loaded_config.llms["test"].provider == "openai"
    finally:
        Path(temp_path).unlink()


def test_config_to_dict():
    """Test converting config to dictionary."""
    config = Config()
    data = config.to_dict()

    assert "gateway" in data
    assert "channels" in data
    assert "llms" in data
    assert "plugins" in data
    assert "session" in data
    assert "sandbox" in data
