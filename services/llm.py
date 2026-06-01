"""OpenAI-compatible LLM abstraction for free providers."""

import httpx
from typing import Optional
from enum import Enum


class LLMProvider(Enum):
    """Free LLM providers."""
    GROQ = "https://api.groq.com/openai/v1"
    TOGETHER = "https://api.together.xyz/v1"
    LEPTON = "https://api.lepton.ai/v1"


class LLMClient:
    """OpenAI-compatible LLM client for free providers."""
    
    def __init__(
        self,
        provider: LLMProvider = LLMProvider.GROQ,
        api_key: Optional[str] = None,
        model: str = "mixtral-8x7b-32768",
    ):
        """Initialize LLM client.
        
        Args:
            provider: LLM provider endpoint
            api_key: API key for the provider
            model: Model name for the provider
        """
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.base_url = provider.value
    
    async def complete(self, prompt: str, **kwargs) -> str:
        """Generate completion using OpenAI-compatible API.
        
        Args:
            prompt: Text prompt
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            Generated completion
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": kwargs.get("max_tokens", 512),
            "temperature": kwargs.get("temperature", 0.7),
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]


class StreamingLLMClient(LLMClient):
    """Streaming-enabled LLM client."""
    
    async def stream_complete(self, prompt: str, **kwargs):
        """Stream completion tokens as they arrive.
        
        Args:
            prompt: Text prompt
            **kwargs: Additional parameters
            
        Yields:
            Completion tokens
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
            "max_tokens": kwargs.get("max_tokens", 512),
            "temperature": kwargs.get("temperature", 0.7),
        }
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=60.0,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        chunk = line[6:]
                        if chunk == "[DONE]":
                            break
                        try:
                            data = json.loads(chunk)
                            token = data["choices"][0]["delta"].get("content", "")
                            if token:
                                yield token
                        except (json.JSONDecodeError, KeyError):
                            pass
