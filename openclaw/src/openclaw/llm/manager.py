"""LLM manager for handling multiple providers."""

import logging
from typing import Optional, Dict, List, Type
from ..config import Config
from .provider import (
    LLMProvider, 
    LLMResponse, 
    OpenAIProvider, 
    AnthropicProvider, 
    OllamaProvider,
    AlibabaCloudProvider,
)

logger = logging.getLogger(__name__)


class LLMManager:
    """Manages multiple LLM providers."""

    def __init__(self, config: Config):
        """Initialize LLM manager.

        Args:
            config: Application configuration
        """
        self.config = config
        self.providers: Dict[str, LLMProvider] = {}
        self.provider_types: Dict[str, Type[LLMProvider]] = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "ollama": OllamaProvider,
            "alibaba": AlibabaCloudProvider,
            "dashscope": AlibabaCloudProvider,  # Alias for Alibaba Cloud
            "qwen": AlibabaCloudProvider,  # Alias for Qwen
        }

    async def initialize_providers(self) -> None:
        """Initialize all configured LLM providers."""
        for name, llm_config in self.config.llms.items():
            try:
                provider_type = llm_config.provider.lower()

                if provider_type not in self.provider_types:
                    logger.warning(f"Unknown LLM provider type: {provider_type}")
                    continue

                provider_class = self.provider_types[provider_type]
                provider = provider_class(llm_config)

                if await provider.initialize():
                    self.providers[name] = provider
                    logger.info(f"Initialized LLM provider: {name} ({provider_type})")
                else:
                    logger.error(f"Failed to initialize LLM provider: {name}")

            except Exception as e:
                logger.error(f"Error initializing LLM provider {name}: {e}", exc_info=True)

    def get_provider(self, name: str = "default") -> Optional[LLMProvider]:
        """Get an LLM provider by name.

        Args:
            name: Provider name

        Returns:
            LLM provider or None
        """
        return self.providers.get(name)

    async def chat(
        self,
        messages: List[Dict[str, str]],
        provider_name: str = "default",
        **kwargs,
    ) -> Optional[LLMResponse]:
        """Send a chat request to an LLM provider.

        Args:
            messages: List of message dicts
            provider_name: Provider to use
            **kwargs: Additional parameters

        Returns:
            LLM response or None
        """
        provider = self.get_provider(provider_name)

        if not provider:
            logger.error(f"LLM provider not found: {provider_name}")
            return None

        try:
            return await provider.chat(messages, **kwargs)
        except Exception as e:
            logger.error(f"Chat error with provider {provider_name}: {e}", exc_info=True)
            return None

    def list_providers(self) -> List[str]:
        """List available LLM providers.

        Returns:
            List of provider names
        """
        return list(self.providers.keys())

    def register_provider(self, name: str, provider: LLMProvider) -> None:
        """Register a custom LLM provider.

        Args:
            name: Provider name
            provider: LLM provider instance
        """
        self.providers[name] = provider
        logger.info(f"Registered custom LLM provider: {name}")
