"""LLMClient: High-level interface to the free LLM abstraction layer."""

from typing import Optional, AsyncGenerator
import json
import os

from .base import Message, ChatCompletion, StreamChunk
from .manager import ProviderManager
from .providers import (
    GroqProvider,
    TogetherAIProvider,
    OpenRouterProvider,
    OpenAICompatibleProvider,
)


class LLMClient:
    """High-level LLM client with OpenAI-compatible interface."""

    def __init__(self, manager: ProviderManager, default_model: str = "auto"):
        """Initialize LLM client."""
        self.manager = manager
        self.default_model = default_model

    @classmethod
    def from_config(cls, config_path: str):
        """Load client configuration from JSON file."""
        config_path = os.path.expandvars(config_path)

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r") as f:
            config = json.load(f)

        providers = {}
        for provider_name, provider_config in config.get("providers", {}).items():
            if not provider_config.get("enabled", True):
                continue

            prov_type = provider_config.get("type")
            api_key = os.path.expandvars(provider_config.get("api_key", ""))

            if prov_type == "groq":
                providers[provider_name] = GroqProvider(provider_name, api_key)

            elif prov_type == "together":
                providers[provider_name] = TogetherAIProvider(provider_name, api_key)

            elif prov_type == "openrouter":
                providers[provider_name] = OpenRouterProvider(provider_name, api_key)

            elif prov_type == "openai-compatible":
                base_url = provider_config.get("base_url", "http://localhost:8000/v1")
                models = provider_config.get("models", ["gpt-4"])
                providers[provider_name] = OpenAICompatibleProvider(
                    provider_name, api_key, base_url, models
                )

        fallback_order = config.get("fallback_order") or sorted(providers.keys())
        manager = ProviderManager(providers, fallback_order)
        default_model = config.get("default_model", "auto")

        return cls(manager, default_model)

    async def chat_completion(self, messages: list, model: Optional[str] = None, temperature: float = 0.7, max_tokens: Optional[int] = None, **kwargs) -> dict:
        """Send chat completion request (OpenAI-compatible)."""
        msg_objects = [
            Message(role=m["role"], content=m["content"]) for m in messages
        ]

        model = model or self.default_model

        result = await self.manager.chat_completion(
            messages=msg_objects,
            model=model if model != "auto" else None,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        return {
            "id": "aios-" + str(id(result))[:8],
            "object": "chat.completion",
            "created": 0,
            "model": result.model,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": result.content},
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": result.tokens_used or 0,
                "total_tokens": result.tokens_used or 0,
            },
            "x-routed-via": result.provider,
        }

    async def stream_chat_completion(self, messages: list, model: Optional[str] = None, temperature: float = 0.7, max_tokens: Optional[int] = None, **kwargs):
        """Stream chat completion response (OpenAI-compatible)."""
        msg_objects = [
            Message(role=m["role"], content=m["content"]) for m in messages
        ]

        model = model or self.default_model

        async for chunk in self.manager.stream_chat_completion(
            messages=msg_objects,
            model=model if model != "auto" else None,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        ):
            yield {
                "id": "aios-chunk",
                "object": "chat.completion.chunk",
                "created": 0,
                "model": chunk.provider,
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": chunk.content},
                        "finish_reason": chunk.finish_reason,
                    }
                ],
            }

    async def get_available_models(self, provider: Optional[str] = None) -> list:
        """Get list of available models."""
        if provider:
            if provider in self.manager.providers:
                return self.manager.providers[provider].get_available_models()
            return []

        all_models = []
        for prov in self.manager.providers.values():
            all_models.extend(prov.get_available_models())

        return list(set(all_models))

    async def get_provider_health(self) -> dict:
        """Get health status of all providers."""
        statuses = await self.manager.probe_all_providers()
        return {name: status.value for name, status in statuses.items()}

    async def get_stats(self) -> dict:
        """Get provider statistics (requests, tokens, rate limits)."""
        return self.manager.get_provider_stats()
