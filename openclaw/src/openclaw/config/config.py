"""Main configuration handler for OpenClaw."""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from .models import (
    GatewayConfig,
    ChannelConfig,
    LLMConfig,
    PluginConfig,
    SessionConfig,
    SandboxConfig,
)


class Config:
    """Main configuration class for OpenClaw."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration.

        Args:
            config_path: Path to configuration file (YAML)
        """
        # Load environment variables
        load_dotenv()

        # Default configuration
        self.gateway = GatewayConfig()
        self.channels: Dict[str, ChannelConfig] = {}
        self.llms: Dict[str, LLMConfig] = {}
        self.plugins: Dict[str, PluginConfig] = {}
        self.session = SessionConfig()
        self.sandbox = SandboxConfig()

        # Load from file if provided
        if config_path:
            self.load_from_file(config_path)

        # Override with environment variables
        self._load_from_env()

    def load_from_file(self, config_path: str) -> None:
        """Load configuration from YAML file.

        Args:
            config_path: Path to YAML configuration file
        """
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not data:
            return

        # Load gateway config
        if "gateway" in data:
            self.gateway = GatewayConfig(**data["gateway"])

        # Load channel configs
        if "channels" in data:
            for name, channel_data in data["channels"].items():
                self.channels[name] = ChannelConfig(**channel_data)

        # Load LLM configs
        if "llms" in data:
            for name, llm_data in data["llms"].items():
                self.llms[name] = LLMConfig(**llm_data)

        # Load plugin configs
        if "plugins" in data:
            for name, plugin_data in data["plugins"].items():
                self.plugins[name] = PluginConfig(**plugin_data)

        # Load session config
        if "session" in data:
            self.session = SessionConfig(**data["session"])

        # Load sandbox config
        if "sandbox" in data:
            self.sandbox = SandboxConfig(**data["sandbox"])

    def _load_from_env(self) -> None:
        """Override configuration with environment variables."""
        # Gateway
        if os.getenv("OPENCLAW_HOST"):
            self.gateway.host = os.getenv("OPENCLAW_HOST")
        if os.getenv("OPENCLAW_PORT"):
            self.gateway.port = int(os.getenv("OPENCLAW_PORT"))
        if os.getenv("OPENCLAW_AUTH_TOKEN"):
            self.gateway.auth_token = os.getenv("OPENCLAW_AUTH_TOKEN")

        # Default LLM
        if os.getenv("OPENCLAW_LLM_PROVIDER"):
            default_llm = LLMConfig(
                provider=os.getenv("OPENCLAW_LLM_PROVIDER"),
                api_key=os.getenv("OPENCLAW_LLM_API_KEY"),
                model=os.getenv("OPENCLAW_LLM_MODEL", "gpt-4"),
            )
            self.llms["default"] = default_llm

    def save_to_file(self, config_path: str) -> None:
        """Save configuration to YAML file.

        Args:
            config_path: Path to save YAML configuration file
        """
        data = {
            "gateway": self.gateway.model_dump(),
            "channels": {name: ch.model_dump() for name, ch in self.channels.items()},
            "llms": {name: llm.model_dump() for name, llm in self.llms.items()},
            "plugins": {name: pl.model_dump() for name, pl in self.plugins.items()},
            "session": self.session.model_dump(),
            "sandbox": self.sandbox.model_dump(),
        }

        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create configuration from dictionary.

        Args:
            data: Configuration dictionary

        Returns:
            Config instance
        """
        config = cls()

        if "gateway" in data:
            config.gateway = GatewayConfig(**data["gateway"])

        if "channels" in data:
            for name, channel_data in data["channels"].items():
                config.channels[name] = ChannelConfig(**channel_data)

        if "llms" in data:
            for name, llm_data in data["llms"].items():
                config.llms[name] = LLMConfig(**llm_data)

        if "plugins" in data:
            for name, plugin_data in data["plugins"].items():
                config.plugins[name] = PluginConfig(**plugin_data)

        if "session" in data:
            config.session = SessionConfig(**data["session"])

        if "sandbox" in data:
            config.sandbox = SandboxConfig(**data["sandbox"])

        return config

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            Configuration dictionary
        """
        return {
            "gateway": self.gateway.model_dump(),
            "channels": {name: ch.model_dump() for name, ch in self.channels.items()},
            "llms": {name: llm.model_dump() for name, llm in self.llms.items()},
            "plugins": {name: pl.model_dump() for name, pl in self.plugins.items()},
            "session": self.session.model_dump(),
            "sandbox": self.sandbox.model_dump(),
        }
