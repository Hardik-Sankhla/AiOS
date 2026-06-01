"""Integration test for LLM layer with real provider API keys."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.llm import LLMClient


async def test_real_provider(client, provider_name, model):
    """Test a specific provider with a real request."""
    print(f"\n{'='*70}")
    print(f"Testing {provider_name.upper()} - {model}")
    print('='*70)
    
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "What is the capital of France? Reply in one sentence."}
    ]
    
    try:
        print(f"\nSending request to {provider_name}...")
        response = await client.chat_completion(
            messages=messages,
            model=model if model else None,
            temperature=0.7,
            max_tokens=100
        )
        
        print(f"\n✓ Success!")
        print(f"  Provider: {response.get('x-routed-via', 'unknown')}")
        print(f"  Model: {response['model']}")
        print(f"  Response: {response['choices'][0]['message']['content']}")
        print(f"  Tokens: {response['usage']['total_tokens']}")
        
        return True
        
    except ValueError as e:
        print(f"\n✗ Invalid API key: {e}")
        print(f"  Please set the {provider_name.upper()}_API_KEY environment variable")
        return False
        
    except RuntimeError as e:
        print(f"\n✗ Request failed: {e}")
        return False
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_streaming(client):
    """Test streaming response."""
    print(f"\n{'='*70}")
    print("Testing Streaming Response")
    print('='*70 + "\n")
    
    messages = [
        {"role": "user", "content": "Count from 1 to 5, one number per line"}
    ]
    
    try:
        print("Streaming response:\n")
        async for chunk in client.stream_chat_completion(messages=messages):
            content = chunk["choices"][0]["delta"].get("content", "")
            if content:
                print(content, end="", flush=True)
        
        print("\n\n✓ Streaming test complete")
        return True
        
    except Exception as e:
        print(f"\n✗ Streaming test failed: {e}")
        return False


async def main():
    """Run integration tests."""
    print("\n" + "╔"+"="*68+"╗")
    print("║" + " "*15 + "LLM LAYER - REAL PROVIDER INTEGRATION TESTS" + " "*11 + "║")
    print("╚"+"="*68+"╝")
    
    # Load configuration
    try:
        client = LLMClient.from_config("configs/providers.json")
        print("\n✓ Configuration loaded")
        print(f"  Providers: {len(client.manager.providers)}")
        print(f"  Fallback chain: {' → '.join(client.manager.fallback_order)}")
    except Exception as e:
        print(f"\n✗ Failed to load config: {e}")
        return
    
    # Get provider health
    print("\n" + "-"*70)
    print("Provider Health Status")
    print("-"*70)
    
    health = await client.get_provider_health()
    for provider, status in health.items():
        icon = "✓" if status == "healthy" else "⚠"
        print(f"  {icon} {provider:15} {status}")
    
    # Test each provider
    print("\n" + "-"*70)
    print("Testing Providers")
    print("-"*70)
    
    # Get available models
    models_by_provider = {}
    for provider in client.manager.providers.keys():
        models = client.manager.providers[provider].get_available_models()
        if models:
            models_by_provider[provider] = models[0]  # Use first model
    
    results = {}
    for provider, model in models_by_provider.items():
        provider_config = client.manager.providers.get(provider)
        if provider_config and provider_config.api_key:
            results[provider] = await test_real_provider(client, provider, model)
        else:
            print(f"\n⚠ {provider}: No API key configured")
            results[provider] = None
    
    # Test streaming (if at least one provider works)
    if any(results.values()):
        await test_streaming(client)
    
    # Final summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    successful = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    
    for provider, result in results.items():
        if result is True:
            icon = "✓"
        elif result is False:
            icon = "✗"
        else:
            icon = "⊘"
        print(f"  {icon} {provider}")
    
    print(f"\nTotal: {successful} successful, {failed} failed, {skipped} skipped")
    
    if successful > 0:
        print("\n✓ LLM layer is operational!")
    else:
        print("\n⚠ Configure API keys to test providers")
        print("\nExample setup:")
        print("  export GROQ_API_KEY='your-key'")
        print("  export TOGETHER_API_KEY='your-key'")
        print("  export OPENROUTER_API_KEY='your-key'")
        print("  python scripts/test_llm_integration.py")


if __name__ == "__main__":
    asyncio.run(main())
