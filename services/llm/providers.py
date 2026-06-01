"""Provider implementations for Groq, Together, OpenRouter, and OpenAI-compatible endpoints."""

import httpx
import json
from typing import Optional, AsyncGenerator
from .base import BaseProvider, ProviderStatus, Message, ChatCompletion, StreamChunk


class GroqProvider(BaseProvider):
    """Groq API provider (OpenAI-compatible)."""
    BASE_URL = "https://api.groq.com/openai/v1"
    MODELS = ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"]

    async def chat_completion(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(f"{self.BASE_URL}/chat/completions", json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                self.status = ProviderStatus.HEALTHY
                return ChatCompletion(
                    model=data["model"],
                    content=data["choices"][0]["message"]["content"],
                    provider=self.name,
                    tokens_used=data.get("usage", {}).get("total_tokens"),
                )
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    self.status = ProviderStatus.INVALID_KEY
                    raise ValueError("Invalid Groq API key")
                elif e.response.status_code == 429:
                    self.status = ProviderStatus.RATE_LIMITED
                    raise RuntimeError("Groq rate limited")
                else:
                    self.status = ProviderStatus.ERROR
                    raise

    async def stream_chat_completion(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "stream": True,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                async with client.stream("POST", f"{self.BASE_URL}/chat/completions", json=payload, headers=headers) as resp:
                    resp.raise_for_status()
                    self.status = ProviderStatus.HEALTHY
                    async for line in resp.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str == "[DONE]":
                                yield StreamChunk("", self.name, "stop")
                                break
                            try:
                                data = json.loads(data_str)
                                content = data["choices"][0]["delta"].get("content", "")
                                if content:
                                    yield StreamChunk(content, self.name, data["choices"][0].get("finish_reason"))
                            except json.JSONDecodeError:
                                pass
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    self.status = ProviderStatus.INVALID_KEY
                    raise ValueError("Invalid Groq API key")
                elif e.response.status_code == 429:
                    self.status = ProviderStatus.RATE_LIMITED
                    raise RuntimeError("Groq rate limited")
                else:
                    self.status = ProviderStatus.ERROR
                    raise

    async def get_health_status(self):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(f"{self.BASE_URL}/models", headers=headers)
                resp.raise_for_status()
                self.status = ProviderStatus.HEALTHY
                return self.status
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    self.status = ProviderStatus.INVALID_KEY
                elif e.response.status_code == 429:
                    self.status = ProviderStatus.RATE_LIMITED
                else:
                    self.status = ProviderStatus.ERROR
                return self.status
            except Exception:
                self.status = ProviderStatus.ERROR
                return self.status

    def get_available_models(self):
        return self.MODELS


class TogetherAIProvider(BaseProvider):
    """Together AI provider (OpenAI-compatible)."""
    BASE_URL = "https://api.together.xyz/v1"
    MODELS = ["meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo", "mistralai/Mixtral-8x7B-Instruct-v0.1"]

    async def chat_completion(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": model, "messages": [{"role": m.role, "content": m.content} for m in messages], "temperature": temperature}
        if max_tokens:
            payload["max_tokens"] = max_tokens
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(f"{self.BASE_URL}/chat/completions", json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                self.status = ProviderStatus.HEALTHY
                return ChatCompletion(model=data["model"], content=data["choices"][0]["message"]["content"], provider=self.name, tokens_used=data.get("usage", {}).get("total_tokens"))
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    self.status = ProviderStatus.INVALID_KEY
                    raise ValueError("Invalid Together API key")
                elif e.response.status_code == 429:
                    self.status = ProviderStatus.RATE_LIMITED
                    raise RuntimeError("Together rate limited")
                else:
                    self.status = ProviderStatus.ERROR
                    raise

    async def stream_chat_completion(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": model, "messages": [{"role": m.role, "content": m.content} for m in messages], "temperature": temperature, "stream": True}
        if max_tokens:
            payload["max_tokens"] = max_tokens
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                async with client.stream("POST", f"{self.BASE_URL}/chat/completions", json=payload, headers=headers) as resp:
                    resp.raise_for_status()
                    self.status = ProviderStatus.HEALTHY
                    async for line in resp.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str == "[DONE]":
                                yield StreamChunk("", self.name, "stop")
                                break
                            try:
                                data = json.loads(data_str)
                                content = data["choices"][0]["delta"].get("content", "")
                                if content:
                                    yield StreamChunk(content, self.name, data["choices"][0].get("finish_reason"))
                            except json.JSONDecodeError:
                                pass
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    self.status = ProviderStatus.INVALID_KEY
                    raise ValueError("Invalid Together API key")
                elif e.response.status_code == 429:
                    self.status = ProviderStatus.RATE_LIMITED
                    raise RuntimeError("Together rate limited")
                else:
                    self.status = ProviderStatus.ERROR
                    raise

    async def get_health_status(self):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(f"{self.BASE_URL}/models", headers=headers)
                resp.raise_for_status()
                self.status = ProviderStatus.HEALTHY
                return self.status
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    self.status = ProviderStatus.INVALID_KEY
                elif e.response.status_code == 429:
                    self.status = ProviderStatus.RATE_LIMITED
                else:
                    self.status = ProviderStatus.ERROR
                return self.status
            except Exception:
                self.status = ProviderStatus.ERROR
                return self.status

    def get_available_models(self):
        return self.MODELS


class OpenRouterProvider(BaseProvider):
    """OpenRouter provider."""
    BASE_URL = "https://openrouter.ai/api/v1"
    MODELS = ["mistralai/mistral-7b-instruct", "meta-llama/llama-2-70b-chat"]

    async def chat_completion(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json", "HTTP-Referer": "https://aios.local", "X-Title": "AIOS"}
        payload = {"model": model, "messages": [{"role": m.role, "content": m.content} for m in messages], "temperature": temperature}
        if max_tokens:
            payload["max_tokens"] = max_tokens
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(f"{self.BASE_URL}/chat/completions", json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                self.status = ProviderStatus.HEALTHY
                return ChatCompletion(model=data["model"], content=data["choices"][0]["message"]["content"], provider=self.name, tokens_used=data.get("usage", {}).get("total_tokens"))
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    self.status = ProviderStatus.INVALID_KEY
                    raise ValueError("Invalid OpenRouter key")
                elif e.response.status_code == 429:
                    self.status = ProviderStatus.RATE_LIMITED
                    raise RuntimeError("OpenRouter rate limited")
                else:
                    self.status = ProviderStatus.ERROR
                    raise

    async def stream_chat_completion(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json", "HTTP-Referer": "https://aios.local"}
        payload = {"model": model, "messages": [{"role": m.role, "content": m.content} for m in messages], "temperature": temperature, "stream": True}
        if max_tokens:
            payload["max_tokens"] = max_tokens
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                async with client.stream("POST", f"{self.BASE_URL}/chat/completions", json=payload, headers=headers) as resp:
                    resp.raise_for_status()
                    self.status = ProviderStatus.HEALTHY
                    async for line in resp.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str == "[DONE]":
                                yield StreamChunk("", self.name, "stop")
                                break
                            try:
                                data = json.loads(data_str)
                                content = data["choices"][0]["delta"].get("content", "")
                                if content:
                                    yield StreamChunk(content, self.name, data["choices"][0].get("finish_reason"))
                            except json.JSONDecodeError:
                                pass
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    self.status = ProviderStatus.INVALID_KEY
                    raise ValueError("Invalid OpenRouter key")
                elif e.response.status_code == 429:
                    self.status = ProviderStatus.RATE_LIMITED
                    raise RuntimeError("OpenRouter rate limited")
                else:
                    self.status = ProviderStatus.ERROR
                    raise

    async def get_health_status(self):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(f"{self.BASE_URL}/models", headers=headers)
                resp.raise_for_status()
                self.status = ProviderStatus.HEALTHY
                return self.status
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    self.status = ProviderStatus.INVALID_KEY
                elif e.response.status_code == 429:
                    self.status = ProviderStatus.RATE_LIMITED
                else:
                    self.status = ProviderStatus.ERROR
                return self.status
            except Exception:
                self.status = ProviderStatus.ERROR
                return self.status

    def get_available_models(self):
        return self.MODELS


class OpenAICompatibleProvider(BaseProvider):
    """Generic OpenAI-compatible provider (local Ollama, LM Studio, etc.)."""

    def __init__(self, name, api_key, base_url, models):
        super().__init__(name, api_key, base_url)
        self._models = models

    async def chat_completion(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
        headers = {"Authorization": f"Bearer {self.api_key}" if self.api_key else "", "Content-Type": "application/json"}
        payload = {"model": model, "messages": [{"role": m.role, "content": m.content} for m in messages], "temperature": temperature}
        if max_tokens:
            payload["max_tokens"] = max_tokens
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(f"{self.base_url}/chat/completions", json=payload, headers={k: v for k, v in headers.items() if v})
                resp.raise_for_status()
                data = resp.json()
                self.status = ProviderStatus.HEALTHY
                return ChatCompletion(model=data["model"], content=data["choices"][0]["message"]["content"], provider=self.name, tokens_used=data.get("usage", {}).get("total_tokens"))
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    self.status = ProviderStatus.INVALID_KEY
                    raise ValueError(f"Invalid {self.name} key")
                elif e.response.status_code == 429:
                    self.status = ProviderStatus.RATE_LIMITED
                    raise RuntimeError(f"{self.name} rate limited")
                else:
                    self.status = ProviderStatus.ERROR
                    raise

    async def stream_chat_completion(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
        headers = {"Authorization": f"Bearer {self.api_key}" if self.api_key else "", "Content-Type": "application/json"}
        payload = {"model": model, "messages": [{"role": m.role, "content": m.content} for m in messages], "temperature": temperature, "stream": True}
        if max_tokens:
            payload["max_tokens"] = max_tokens
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                async with client.stream("POST", f"{self.base_url}/chat/completions", json=payload, headers={k: v for k, v in headers.items() if v}) as resp:
                    resp.raise_for_status()
                    self.status = ProviderStatus.HEALTHY
                    async for line in resp.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str == "[DONE]":
                                yield StreamChunk("", self.name, "stop")
                                break
                            try:
                                data = json.loads(data_str)
                                if "choices" in data and len(data["choices"]) > 0:
                                    content = data["choices"][0]["delta"].get("content", "")
                                    if content:
                                        yield StreamChunk(content, self.name, data["choices"][0].get("finish_reason"))
                            except json.JSONDecodeError:
                                pass
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    self.status = ProviderStatus.INVALID_KEY
                    raise ValueError(f"Invalid {self.name} key")
                elif e.response.status_code == 429:
                    self.status = ProviderStatus.RATE_LIMITED
                    raise RuntimeError(f"{self.name} rate limited")
                else:
                    self.status = ProviderStatus.ERROR
                    raise

    async def get_health_status(self):
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(f"{self.base_url}/models", headers=headers)
                resp.raise_for_status()
                self.status = ProviderStatus.HEALTHY
                return self.status
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    self.status = ProviderStatus.INVALID_KEY
                elif e.response.status_code == 429:
                    self.status = ProviderStatus.RATE_LIMITED
                else:
                    self.status = ProviderStatus.ERROR
                return self.status
            except Exception:
                self.status = ProviderStatus.ERROR
                return self.status

    def get_available_models(self):
        return self._models
