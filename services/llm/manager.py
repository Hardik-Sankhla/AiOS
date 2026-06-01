"""ProviderManager: Intelligent provider routing and fallback logic."""

import asyncio
from typing import Optional
from datetime import datetime, timedelta
from .base import BaseProvider, ProviderStatus, Message, ChatCompletion, StreamChunk


class RateLimitTracker:
    """Track per-provider rate limit state."""

    def __init__(self, rpm_limit: int = 60, tpm_limit: int = 10000):
        self.rpm_limit = rpm_limit
        self.tpm_limit = tpm_limit
        self.request_times: list = []
        self.token_count: int = 0
        self.cooldown_until: Optional[datetime] = None

    def is_rate_limited(self) -> bool:
        """Check if provider is currently rate limited."""
        now = datetime.now()
        if self.cooldown_until and now < self.cooldown_until:
            return True
        one_minute_ago = now - timedelta(minutes=1)
        recent_requests = [t for t in self.request_times if t > one_minute_ago]
        if len(recent_requests) >= self.rpm_limit:
            return True
        return False

    def record_request(self, tokens_used: Optional[int] = None):
        """Record a successful request."""
        self.request_times.append(datetime.now())
        if tokens_used:
            self.token_count += tokens_used

    def mark_rate_limited(self, cooldown_seconds: int = 60):
        """Mark provider as rate limited with cooldown."""
        self.cooldown_until = datetime.now() + timedelta(seconds=cooldown_seconds)

    def cleanup_old_requests(self):
        """Remove requests older than 1 minute."""
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        self.request_times = [t for t in self.request_times if t > one_minute_ago]


class ProviderManager:
    """Manages multiple LLM providers with intelligent routing."""

    def __init__(self, providers: dict, fallback_order: list):
        """Initialize provider manager."""
        self.providers = providers
        self.fallback_order = fallback_order
        self.rate_limiters = {name: RateLimitTracker() for name in providers}
        self._health_cache: dict = {}

    async def chat_completion(self, messages, model=None, temperature=0.7, max_tokens=None, max_retries=3, **kwargs):
        """Send chat completion with automatic provider fallover."""
        attempts = 0
        last_error = None

        for _ in range(max_retries):
            for provider_name in self.fallback_order:
                if provider_name not in self.providers:
                    continue

                provider = self.providers[provider_name]
                limiter = self.rate_limiters[provider_name]

                if limiter.is_rate_limited():
                    continue

                if not await self._is_provider_healthy(provider):
                    continue

                try:
                    selected_model = model or provider.get_available_models()[0]
                    result = await provider.chat_completion(messages=messages, model=selected_model, temperature=temperature, max_tokens=max_tokens, **kwargs)
                    limiter.record_request(result.tokens_used)
                    return result

                except ValueError as e:
                    self._health_cache[provider_name] = ProviderStatus.INVALID_KEY
                    last_error = str(e)
                    continue

                except RuntimeError as e:
                    if "rate limited" in str(e).lower():
                        limiter.mark_rate_limited()
                    last_error = str(e)
                    continue

                except Exception as e:
                    last_error = str(e)
                    continue

            attempts += 1
            if attempts < max_retries:
                await asyncio.sleep(1)

        raise RuntimeError(f"All providers exhausted after {max_retries} retries. Last error: {last_error}")

    async def stream_chat_completion(self, messages, model=None, temperature=0.7, max_tokens=None, max_retries=3, **kwargs):
        """Stream chat completion with automatic provider fallover."""
        attempts = 0
        last_error = None

        for _ in range(max_retries):
            for provider_name in self.fallback_order:
                if provider_name not in self.providers:
                    continue

                provider = self.providers[provider_name]
                limiter = self.rate_limiters[provider_name]

                if limiter.is_rate_limited():
                    continue

                if not await self._is_provider_healthy(provider):
                    continue

                try:
                    selected_model = model or provider.get_available_models()[0]
                    tokens_used = 0
                    async for chunk in provider.stream_chat_completion(messages=messages, model=selected_model, temperature=temperature, max_tokens=max_tokens, **kwargs):
                        yield chunk
                        tokens_used += len(chunk.content) // 4

                    limiter.record_request(tokens_used)
                    return

                except ValueError as e:
                    self._health_cache[provider_name] = ProviderStatus.INVALID_KEY
                    last_error = str(e)
                    continue

                except RuntimeError as e:
                    if "rate limited" in str(e).lower():
                        limiter.mark_rate_limited()
                    last_error = str(e)
                    continue

                except Exception as e:
                    last_error = str(e)
                    continue

            attempts += 1
            if attempts < max_retries:
                await asyncio.sleep(1)

        raise RuntimeError(f"All providers exhausted after {max_retries} retries. Last error: {last_error}")

    async def _is_provider_healthy(self, provider: BaseProvider) -> bool:
        """Check if provider is healthy (cached)."""
        if provider.name in self._health_cache:
            cached_status = self._health_cache[provider.name]
            if cached_status == ProviderStatus.HEALTHY:
                return True
            if cached_status == ProviderStatus.INVALID_KEY:
                return False

        try:
            status = await provider.get_health_status()
            self._health_cache[provider.name] = status
            return status == ProviderStatus.HEALTHY
        except Exception:
            self._health_cache[provider.name] = ProviderStatus.ERROR
            return False

    async def probe_all_providers(self) -> dict:
        """Probe health of all providers."""
        results = {}
        tasks = []

        for name, provider in self.providers.items():
            tasks.append(self._probe_and_cache(name, provider))

        statuses = await asyncio.gather(*tasks, return_exceptions=True)
        for name, status in zip(self.providers.keys(), statuses):
            if isinstance(status, Exception):
                results[name] = ProviderStatus.ERROR
            else:
                results[name] = status

        return results

    async def _probe_and_cache(self, name: str, provider: BaseProvider) -> ProviderStatus:
        """Probe single provider and cache result."""
        try:
            status = await provider.get_health_status()
            self._health_cache[name] = status
            return status
        except Exception:
            self._health_cache[name] = ProviderStatus.ERROR
            return ProviderStatus.ERROR

    def get_provider_stats(self) -> dict:
        """Get statistics for all providers."""
        stats = {}
        for name, limiter in self.rate_limiters.items():
            limiter.cleanup_old_requests()
            stats[name] = {
                "health": self._health_cache.get(name, ProviderStatus.UNKNOWN).value,
                "requests_1m": len(limiter.request_times),
                "tokens_used": limiter.token_count,
                "rate_limited": limiter.is_rate_limited(),
            }
        return stats
