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


class GeminiProvider(BaseProvider):
    """Google Gemini API provider."""
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
    MODELS = ["gemini-pro", "gemini-pro-vision"]

    async def chat_completion(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
        """Generate chat completion via Gemini API."""
        headers = {"Content-Type": "application/json"}
        
        # Convert to Gemini format (contents array with parts)
        contents = []
        for msg in messages:
            if msg.role == "user":
                contents.append({
                    "role": "user",
                    "parts": [{"text": msg.content}]
                })
            elif msg.role == "assistant":
                contents.append({
                    "role": "model",
                    "parts": [{"text": msg.content}]
                })
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
            }
        }
        if max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = max_tokens
        
        url = f"{self.BASE_URL}/{model}:generateContent?key={self.api_key}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                self.status = ProviderStatus.HEALTHY
                
                # Extract text from Gemini response format
                content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                
                return ChatCompletion(
                    model=model,
                    content=content,
                    provider=self.name,
                    tokens_used=None,
                )
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    self.status = ProviderStatus.INVALID_KEY
                    raise ValueError("Invalid Gemini API key")
                elif e.response.status_code == 429:
                    self.status = ProviderStatus.RATE_LIMITED
                    raise RuntimeError("Gemini rate limited")
                else:
                    self.status = ProviderStatus.ERROR
                    raise

    async def stream_chat_completion(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
        """Streaming not implemented for Gemini yet."""
        raise NotImplementedError("Streaming not yet implemented for Gemini provider")

    async def get_health_status(self):
        """Check Gemini API health."""
        try:
            url = f"{self.BASE_URL}?key={self.api_key}"
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)
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


class CerebrasProvider(BaseProvider):
    """Cerebras API provider (OpenAI-compatible)."""
    BASE_URL = "https://api.cerebras.ai/v1"
    MODELS = ["llama2-13b", "llama2-70b"]

    async def chat_completion(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
        """Generate chat completion via Cerebras."""
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
                    raise ValueError("Invalid Cerebras API key")
                elif e.response.status_code == 429:
                    self.status = ProviderStatus.RATE_LIMITED
                    raise RuntimeError("Cerebras rate limited")
                else:
                    self.status = ProviderStatus.ERROR
                    raise

    async def stream_chat_completion(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
        """Streaming chat completion."""
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "stream": True,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", f"{self.BASE_URL}/chat/completions", json=payload, headers=headers) as resp:
                try:
                    async for line in resp.aiter_lines():
                        if line.startswith("data: "):
                            data = json.loads(line[6:])
                            if data.get("choices"):
                                chunk = data["choices"][0].get("delta", {})
                                content = chunk.get("content", "")
                                if content:
                                    yield StreamChunk(content=content, provider=self.name)
                    self.status = ProviderStatus.HEALTHY
                except Exception:
                    self.status = ProviderStatus.ERROR
                    raise

    async def get_health_status(self):
        """Check Cerebras API health."""
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


class SambaNovAProvider(BaseProvider):
    """SambaNova API provider (OpenAI-compatible)."""
    BASE_URL = "https://api.sambanova.ai/v1"
    MODELS = ["meta-llama/Llama-2-7b-hf", "meta-llama/Llama-2-13b-hf"]

    async def chat_completion(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
        """Generate chat completion via SambaNova."""
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
                    raise ValueError("Invalid SambaNova API key")
                elif e.response.status_code == 429:
                    self.status = ProviderStatus.RATE_LIMITED
                    raise RuntimeError("SambaNova rate limited")
                else:
                    self.status = ProviderStatus.ERROR
                    raise

    async def stream_chat_completion(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
        """Streaming chat completion."""
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "stream": True,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", f"{self.BASE_URL}/chat/completions", json=payload, headers=headers) as resp:
                try:
                    async for line in resp.aiter_lines():
                        if line.startswith("data: "):
                            data = json.loads(line[6:])
                            if data.get("choices"):
                                chunk = data["choices"][0].get("delta", {})
                                content = chunk.get("content", "")
                                if content:
                                    yield StreamChunk(content=content, provider=self.name)
                    self.status = ProviderStatus.HEALTHY
                except Exception:
                    self.status = ProviderStatus.ERROR
                    raise

    async def get_health_status(self):
        """Check SambaNova API health."""
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


class GitHubModelsProvider(BaseProvider):
    """GitHub Models provider (OpenAI-compatible)."""
    BASE_URL = "https://models.inference.ai.azure.com"
    MODELS = ["gpt-4-turbo", "gpt-4", "llama-2-7b"]

    async def chat_completion(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
        """Generate chat completion via GitHub Models."""
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
                    raise ValueError("Invalid GitHub token")
                elif e.response.status_code == 429:
                    self.status = ProviderStatus.RATE_LIMITED
                    raise RuntimeError("GitHub Models rate limited")
                else:
                    self.status = ProviderStatus.ERROR
                    raise

    async def stream_chat_completion(self, messages, model, temperature=0.7, max_tokens=None, **kwargs):
        """Streaming chat completion."""
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "stream": True,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", f"{self.BASE_URL}/chat/completions", json=payload, headers=headers) as resp:
                try:
                    async for line in resp.aiter_lines():
                        if line.startswith("data: "):
                            data = json.loads(line[6:])
                            if data.get("choices"):
                                chunk = data["choices"][0].get("delta", {})
                                content = chunk.get("content", "")
                                if content:
                                    yield StreamChunk(content=content, provider=self.name)
                    self.status = ProviderStatus.HEALTHY
                except Exception:
                    self.status = ProviderStatus.ERROR
                    raise

    async def get_health_status(self):
        """Check GitHub Models API health."""
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

