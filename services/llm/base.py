"""
BaseProvider: Abstract base class for LLM provider implementations.

Defines the interface for provider integration with the AIOS framework.
Each provider must implement both streaming and non-streaming chat completions.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncGenerator, Optional
from enum import Enum


class ProviderStatus(Enum):
    """Health status of a provider."""
    HEALTHY = "healthy"
    RATE_LIMITED = "rate_limited"
    INVALID_KEY = "invalid_key"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class Message:
    """Chat message in OpenAI format."""
    role: str  # "user", "assistant", "system"
    content: str


@dataclass
class ChatCompletion:
    """Response from chat completion."""
    model: str
    content: str
    provider: str
    tokens_used: Optional[int] = None


@dataclass
class StreamChunk:
    """Streaming chunk with delta content."""
    content: str
    provider: str
    finish_reason: Optional[str] = None  # "stop", "length", "tool_calls", etc.


class BaseProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    Implementations must provide:
    - chat_completion: Non-streaming completions
    - stream_chat_completion: Streaming completions
    - get_health_status: Health check probe
    """

    def __init__(self, name: str, api_key: str, base_url: Optional[str] = None):
        """
        Initialize provider.
        
        Args:
            name: Provider identifier (e.g., "groq", "gemini", "openrouter")
            api_key: API key for authentication
            base_url: Optional custom endpoint (for OpenAI-compatible providers)
        """
        self.name = name
        self.api_key = api_key
        self.base_url = base_url
        self.status = ProviderStatus.UNKNOWN

    @abstractmethod
    async def chat_completion(
        self,
        messages: list[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> ChatCompletion:
        """
        Send a chat completion request.
        
        Args:
            messages: List of Message objects
            model: Model identifier (e.g., "gpt-4", "llama-3.3-70b")
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            **kwargs: Provider-specific parameters
            
        Returns:
            ChatCompletion with response content
            
        Raises:
            ValueError: If API key is invalid
            RuntimeError: If provider is rate-limited or erroring
        """
        pass

    @abstractmethod
    async def stream_chat_completion(
        self,
        messages: list[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Stream a chat completion response.
        
        Args:
            messages: List of Message objects
            model: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            **kwargs: Provider-specific parameters
            
        Yields:
            StreamChunk with delta content
            
        Raises:
            ValueError: If API key is invalid
            RuntimeError: If provider is rate-limited or erroring
        """
        pass

    @abstractmethod
    async def get_health_status(self) -> ProviderStatus:
        """
        Probe provider health with a simple test request.
        
        Returns:
            ProviderStatus enum value
        """
        pass

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """
        Return list of available models for this provider.
        
        Returns:
            List of model identifiers
        """
        pass
