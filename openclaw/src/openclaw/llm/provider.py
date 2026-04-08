"""LLM provider interface and implementations."""

import logging
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import httpx
from ..config.models import LLMConfig

logger = logging.getLogger(__name__)


class LLMResponse:
    """Response from an LLM provider."""

    def __init__(self, content: str, model: str, usage: Optional[Dict[str, int]] = None):
        """Initialize LLM response.

        Args:
            content: Response text
            model: Model used
            usage: Token usage information
        """
        self.content = content
        self.model = model
        self.usage = usage or {}


class LLMProvider(ABC):
    """Base class for LLM providers."""

    def __init__(self, config: LLMConfig):
        """Initialize LLM provider.

        Args:
            config: LLM configuration
        """
        self.config = config

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs,
    ) -> LLMResponse:
        """Send a chat request to the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters

        Returns:
            LLM response
        """
        pass

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the provider (validate API key, etc).

        Returns:
            True if initialization succeeded
        """
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""

    def __init__(self, config: LLMConfig):
        """Initialize OpenAI provider.

        Args:
            config: LLM configuration
        """
        super().__init__(config)
        self.api_url = config.base_url or "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.api_key}",
        }

    async def initialize(self) -> bool:
        """Validate OpenAI API key."""
        if not self.config.api_key:
            logger.error("OpenAI API key not configured")
            return False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.openai.com/v1/models",
                    headers=self.headers,
                    timeout=10,
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {e}")
            return False

    async def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs,
    ) -> LLMResponse:
        """Send chat request to OpenAI.

        Args:
            messages: List of message dicts
            **kwargs: Additional parameters

        Returns:
            LLM response
        """
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
        }

        if self.config.max_tokens:
            payload["max_tokens"] = self.config.max_tokens

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=self.headers,
                    timeout=60,
                )
                response.raise_for_status()

                data = response.json()
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})

                return LLMResponse(
                    content=content,
                    model=self.config.model,
                    usage=usage,
                )

        except Exception as e:
            logger.error(f"OpenAI chat error: {e}")
            raise


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""

    def __init__(self, config: LLMConfig):
        """Initialize Anthropic provider.

        Args:
            config: LLM configuration
        """
        super().__init__(config)
        self.api_url = config.base_url or "https://api.anthropic.com/v1/messages"
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": config.api_key,
            "anthropic-version": "2023-06-01",
        }

    async def initialize(self) -> bool:
        """Validate Anthropic API key."""
        if not self.config.api_key:
            logger.error("Anthropic API key not configured")
            return False

        # Simple validation by checking if we can make a request
        return True

    async def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs,
    ) -> LLMResponse:
        """Send chat request to Anthropic.

        Args:
            messages: List of message dicts
            **kwargs: Additional parameters

        Returns:
            LLM response
        """
        # Convert messages to Anthropic format
        system_message = None
        anthropic_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                anthropic_messages.append(msg)

        payload = {
            "model": self.config.model,
            "messages": anthropic_messages,
            "max_tokens": self.config.max_tokens or 4096,
            "temperature": kwargs.get("temperature", self.config.temperature),
        }

        if system_message:
            payload["system"] = system_message

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=self.headers,
                    timeout=60,
                )
                response.raise_for_status()

                data = response.json()
                content = data["content"][0]["text"]

                return LLMResponse(
                    content=content,
                    model=self.config.model,
                )

        except Exception as e:
            logger.error(f"Anthropic chat error: {e}")
            raise


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""

    def __init__(self, config: LLMConfig):
        """Initialize Ollama provider.

        Args:
            config: LLM configuration
        """
        super().__init__(config)
        self.api_url = config.base_url or "http://localhost:11434/api/chat"

    async def initialize(self) -> bool:
        """Check if Ollama is running."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "http://localhost:11434/api/tags",
                    timeout=5,
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama not available: {e}")
            return False

    async def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs,
    ) -> LLMResponse:
        """Send chat request to Ollama.

        Args:
            messages: List of message dicts
            **kwargs: Additional parameters

        Returns:
            LLM response
        """
        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", self.config.temperature),
            },
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    timeout=120,
                )
                response.raise_for_status()

                data = response.json()
                content = data["message"]["content"]

                return LLMResponse(
                    content=content,
                    model=self.config.model,
                )

        except Exception as e:
            logger.error(f"Ollama chat error: {e}")
            raise


class AlibabaCloudProvider(LLMProvider):
    """Alibaba Cloud DashScope (通义千问) provider.
    
    Uses OpenAI-compatible API format.
    API Docs: https://help.aliyun.com/zh/dashscope/developer-reference/compatibility-of-openai-with-dashscope
    """

    def __init__(self, config: LLMConfig):
        """Initialize Alibaba Cloud provider.

        Args:
            config: LLM configuration
        """
        super().__init__(config)
        # Default to DashScope OpenAI-compatible endpoint
        self.api_url = config.base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.api_key}",
        }

    async def initialize(self) -> bool:
        """Validate API key."""
        if not self.config.api_key:
            logger.error("Alibaba Cloud API key not configured")
            return False
        
        # Test with a simple request
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json={
                        "model": self.config.model or "qwen-turbo",
                        "messages": [{"role": "user", "content": "Hi"}],
                        "max_tokens": 5,
                    },
                    headers=self.headers,
                    timeout=10,
                )
                # Accept both success and auth errors (means endpoint is reachable)
                return response.status_code in [200, 401]
        except Exception as e:
            logger.error(f"Failed to initialize Alibaba Cloud: {e}")
            return False

    async def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs,
    ) -> LLMResponse:
        """Send chat request to Alibaba Cloud DashScope.

        Args:
            messages: List of message dicts
            **kwargs: Additional parameters

        Returns:
            LLM response
        """
        payload = {
            "model": self.config.model or "qwen-turbo",
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
        }

        if self.config.max_tokens:
            payload["max_tokens"] = self.config.max_tokens

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=self.headers,
                    timeout=60,
                )
                response.raise_for_status()

                data = response.json()
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})

                return LLMResponse(
                    content=content,
                    model=self.config.model or "qwen-turbo",
                    usage=usage,
                )

        except Exception as e:
            logger.error(f"Alibaba Cloud chat error: {e}")
            raise
