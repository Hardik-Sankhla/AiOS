"""LLM services module - Provider abstraction layer."""

from .base import (
    BaseProvider,
    ProviderStatus,
    Message,
    ChatCompletion,
    StreamChunk,
)
from .providers import (
    GroqProvider,
    TogetherAIProvider,
    OpenRouterProvider,
    OpenAICompatibleProvider,
    GeminiProvider,
    CerebrasProvider,
    SambaNovAProvider,
    GitHubModelsProvider,
)
from .manager import ProviderManager, RateLimitTracker
from .client import LLMClient

__all__ = [
    # Base classes
    "BaseProvider",
    "ProviderStatus",
    "Message",
    "ChatCompletion",
    "StreamChunk",
    # Providers
    "GroqProvider",
    "TogetherAIProvider",
    "OpenRouterProvider",
    "OpenAICompatibleProvider",
    "GeminiProvider",
    "CerebrasProvider",
    "SambaNovAProvider",
    "GitHubModelsProvider",
    # Manager and client
    "ProviderManager",
    "RateLimitTracker",
    "LLMClient",
]

__version__ = "0.2.0"
__description__ = "Unified LLM provider abstraction with support for free and open-source models"
