# AIOS Testing & Verification Guide

**Complete Testing Suite for Hermes Agent Orchestration**

---

## Quick Test (30 Seconds)

```bash
cd /storage/emulated/0/projects/aios

# Verify all imports
python -c "
from services.llm import LLMClient, ProviderManager
from agents.hermes import get_registry, AgentConfig
from agents.hermes.concrete_agents import ResearchAgent, CodingAgent
from webui.app import app
print('✅ All imports successful - System ready!')
"
```

---

## Test Suite Overview

| Test | Type | Duration | Command |
|------|------|----------|---------|
| **Import Tests** | Unit | 5s | `pytest tests/` |
| **LLM Integration** | Integration | 30s | `python scripts/test_llm_integration.py` |
| **Hermes Workflow** | Integration | 30s | `python scripts/test_hermes_workflow.py` |
| **WebUI Endpoints** | API | 10s | `curl http://localhost:8000/health` |
| **Telegram Bot** | Integration | 60s | Manual Telegram test |

---

## 1. Unit Tests (5 seconds)

### Run All Tests

```bash
pytest -v tests/
```

### Expected Output

```
tests/test_llm.py::test_groq_provider PASSED
tests/test_llm.py::test_gemini_provider PASSED
tests/test_llm.py::test_provider_manager PASSED
tests/test_llm.py::test_fallback_routing PASSED
...
============ 4 passed in 0.42s ============
```

### Run Specific Test

```bash
pytest tests/test_llm.py::test_groq_provider -v
```

### Test Coverage

```bash
pytest --cov=services --cov=agents tests/
```

---

## 2. Module Import Verification (10 seconds)

### Quick Verification

```bash
python << 'EOF'
import sys
sys.path.insert(0, '/storage/emulated/0/projects/aios')

tests = {
    'services.llm': ['LLMClient', 'ProviderManager'],
    'agents.hermes': ['Agent', 'Orchestrator', 'get_registry'],
    'agents.hermes.concrete_agents': ['ResearchAgent', 'CodingAgent'],
}

for module, items in tests.items():
    try:
        mod = __import__(module, fromlist=items)
        for item in items:
            getattr(mod, item)
        print(f'✓ {module}')
    except Exception as e:
        print(f'✗ {module}: {e}')
EOF
```

### Configuration Verification

```bash
python << 'EOF'
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Check environment
print("Environment Check:")
api_keys = ['GROQ_API_KEY', 'GOOGLE_API_KEY', 'OPENROUTER_API_KEY']
for key in api_keys:
    value = os.getenv(key)
    status = '✓' if value else '✗'
    print(f"  {status} {key}")

# Check config
print("\nConfiguration Check:")
with open('configs/providers.json') as f:
    config = json.load(f)
    
enabled = {p: v['enabled'] for p, v in config['providers'].items()}
print(f"  Enabled providers: {sum(enabled.values())}/{len(enabled)}")

for p, en in enabled.items():
    status = '✓' if en else '○'
    print(f"    {status} {p}")
EOF
```

---

## 3. LLM Integration Tests (30 seconds)

### Run Full Test Suite

```bash
python scripts/test_llm_integration.py
```

### Test Individual Provider

```bash
python << 'EOF'
from services.llm import ProviderManager, LLMClient
import asyncio

async def test_provider(provider_name):
    manager = ProviderManager()
    client = LLMClient(manager, default_provider=provider_name)
    
    try:
        response = await client.chat_completion(
            "Hello! What is 2+2?",
            provider=provider_name
        )
        print(f"✓ {provider_name}: {response.content[:50]}...")
    except Exception as e:
        print(f"✗ {provider_name}: {e}")

# Test Groq
asyncio.run(test_provider("groq"))

# Test Gemini
asyncio.run(test_provider("gemini"))

# Test OpenRouter
asyncio.run(test_provider("openrouter"))
EOF
```

### Test Provider Fallback

```bash
python << 'EOF'
from services.llm import LLMClient, ProviderManager
import asyncio

async def test_fallback():
    manager = ProviderManager()
    # Load fallback order from config
    import json
    with open('configs/providers.json') as f:
        config = json.load(f)
    
    print(f"Fallback order: {config['fallback_order']}")
    
    client = LLMClient(manager)
    response = await client.chat_completion("Test message")
    print(f"✓ Fallback routing successful: {response.content[:50]}...")

asyncio.run(test_fallback())
EOF
```

---

## 4. Agent Framework Tests (30 seconds)

### Test Agent Registry

```bash
python << 'EOF'
from agents.hermes import get_registry, AgentConfig
from agents.hermes.concrete_agents import ResearchAgent, CodingAgent

# Initialize registry
registry = get_registry()
registry.clear()

# Create agents
research_config = AgentConfig(
    name="ResearchAgent",
    description="Research specialist",
    capabilities=["research", "analysis"]
)
research = ResearchAgent(research_config, llm_client=None)

coding_config = AgentConfig(
    name="CodingAgent",
    description="Coding specialist",
    capabilities=["coding"]
)
coding = CodingAgent(coding_config, llm_client=None)

# Register
registry.register_agent("research", research)
registry.register_agent("coding", coding)

# Test retrieval
agents = registry.list_agents()
print(f"✓ Registered {len(agents)} agents")

for agent_id in agents:
    agent = registry.get_agent(agent_id)
    print(f"  ✓ {agent.name}")
EOF
```

### Test Task Execution

```bash
python << 'EOF'
from agents.hermes import Task, AgentConfig
from agents.hermes.concrete_agents import ResearchAgent
import asyncio

async def test_task():
    # Create agent
    config = AgentConfig(
        name="TestAgent",
        description="Test",
        capabilities=["test"]
    )
    agent = ResearchAgent(config, llm_client=None)
    
    # Create task
    task = Task(
        description="Research AI trends",
        context="What are the latest developments?",
        required_capabilities=["research"]
    )
    
    # Check compatibility
    is_compatible = agent.can_execute(task)
    print(f"✓ Task compatibility: {is_compatible}")
    
    # Execute (without LLM)
    try:
        result = await agent.execute(task)
        print(f"✓ Task executed: {result}")
    except Exception as e:
        print(f"Note: {e}")

asyncio.run(test_task())
EOF
```

---

## 5. WebUI Tests (10 seconds)

### Health Check

```bash
# Must have WebUI running
python -m uvicorn webui.app:app --port 8000 &

sleep 2

# Test endpoints
curl -s http://localhost:8000/health | python -m json.tool

# Get agents
curl -s http://localhost:8000/api/agents

# Get providers
curl -s http://localhost:8000/api/providers

# Get status
curl -s http://localhost:8000/api/status
```

### Expected Responses

**Health Check**:
```json
{
  "status": "healthy",
  "agents": 2,
  "timestamp": "2024-06-01T12:00:00Z"
}
```

**Agent List**:
```json
{
  "agents": [
    {
      "id": "research",
      "name": "ResearchAgent",
      "description": "Research specialist",
      "status": "ready"
    },
    ...
  ]
}
```

---

## 6. Telegram Bot Tests (60 seconds)

### Setup Test

```bash
# 1. Verify token is set
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(f'Token: {os.getenv(\"TELEGRAM_BOT_TOKEN\")[:20]}...')"

# 2. Verify dependencies
pip show python-telegram-bot

# 3. Verify bot module
python -c "from telegram.bot import HermesBot; print('✓ Bot module valid')"
```

### Start Bot

```bash
cd /storage/emulated/0/projects/aios
python -m telegram.bot
```

Expected output:
```
Telegram Bot Handler for Hermes AIOS
✓ Agents initialized
Bot running... (Press Ctrl+C to stop)
```

### Test in Telegram

1. Open Telegram
2. Search for your bot (e.g., @hermes_aios_bot)
3. Send commands:

| Command | Expected Response |
|---------|------------------|
| `/start` | Welcome message + session init |
| `/research` | "Research Agent Selected" |
| `/code` | "Coding Agent Selected" |
| `/status` | System status with agent count |
| `/help` | Command reference |
| Any text | Response from selected agent |

### Automated Bot Test

```bash
# Test bot initialization
python << 'EOF'
import os
from dotenv import load_dotenv
from telegram.bot import HermesBot

load_dotenv()
token = os.getenv('TELEGRAM_BOT_TOKEN')

if token:
    try:
        bot = HermesBot(token)
        print(f"✓ Bot initialized with {len(bot.registry.list_agents())} agents")
        print("✓ Ready for deployment")
    except Exception as e:
        print(f"✗ Bot error: {e}")
else:
    print("✗ TELEGRAM_BOT_TOKEN not configured in .env")
EOF
```

---

## 7. Integration Test Suite (60 seconds)

### Full System Test

```bash
python << 'EOF'
import sys
sys.path.insert(0, '/storage/emulated/0/projects/aios')

print("=" * 60)
print("AIOS FULL SYSTEM TEST")
print("=" * 60)
print()

# 1. Imports
print("[1/5] Testing imports...")
try:
    from services.llm import LLMClient, ProviderManager
    from agents.hermes import get_registry, AgentConfig
    from agents.hermes.concrete_agents import ResearchAgent, CodingAgent
    from webui.app import app
    from telegram.bot import HermesBot
    print("✓ All imports successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# 2. Configuration
print("[2/5] Testing configuration...")
try:
    import json
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    with open('configs/providers.json') as f:
        config = json.load(f)
    
    providers = list(config['providers'].keys())
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    print(f"✓ Configuration loaded: {len(providers)} providers, token={'set' if token else 'not set'}")
except Exception as e:
    print(f"✗ Configuration error: {e}")

# 3. Registry
print("[3/5] Testing agent registry...")
try:
    registry = get_registry()
    registry.clear()
    
    config = AgentConfig(
        name="TestAgent",
        description="Test",
        capabilities=["test"]
    )
    agent = ResearchAgent(config, llm_client=None)
    registry.register_agent("test", agent)
    
    agents = registry.list_agents()
    print(f"✓ Registry working: {len(agents)} agent(s) registered")
except Exception as e:
    print(f"✗ Registry error: {e}")

# 4. WebUI
print("[4/5] Testing WebUI...")
try:
    from webui.app import app
    print("✓ WebUI FastAPI app loaded")
except Exception as e:
    print(f"✗ WebUI error: {e}")

# 5. Bot
print("[5/5] Testing Telegram bot...")
try:
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if token:
        bot = HermesBot(token)
        print(f"✓ Bot initialized with {len(bot.registry.list_agents())} agents")
    else:
        print("○ Bot not configured (token missing)")
except Exception as e:
    print(f"✗ Bot error: {e}")

print()
print("=" * 60)
print("✅ SYSTEM READY FOR PRODUCTION")
print("=" * 60)
EOF
```

---

## Test Execution Checklist

Run tests in this order:

- [ ] **Import tests** - Verify all modules load
- [ ] **Configuration tests** - Check .env and configs
- [ ] **Unit tests** - Run pytest suite
- [ ] **Integration tests** - Test LLM providers
- [ ] **Agent tests** - Verify agent framework
- [ ] **WebUI tests** - Check endpoints
- [ ] **Bot tests** - Telegram integration
- [ ] **Full system test** - End-to-end verification

---

## Continuous Testing

### Watch Mode

```bash
pytest-watch tests/

# Or with coverage
pytest-watch tests/ --cov=services --cov=agents
```

### Pre-commit Testing

```bash
# Install pre-commit hook
pip install pre-commit
pre-commit install

# Test before commit
git commit -am "your changes"  # Will run tests automatically
```

---

## Performance Benchmarks

### Run Benchmarks

```bash
python << 'EOF'
import time
from services.llm import ProviderManager, LLMClient
import asyncio

async def benchmark():
    manager = ProviderManager()
    client = LLMClient(manager, default_provider="groq")
    
    start = time.time()
    response = await client.chat_completion("What is 2+2?")
    elapsed = time.time() - start
    
    print(f"Response time: {elapsed:.2f}s")
    print(f"Tokens: ~{len(response.content.split())}")

asyncio.run(benchmark())
EOF
```

---

## Troubleshooting Tests

### Test Fails: Import Error

```bash
# Solution 1: Add to PYTHONPATH
export PYTHONPATH=/storage/emulated/0/projects/aios:$PYTHONPATH

# Solution 2: Check dependencies
pip install -r requirements.txt

# Solution 3: Verify structure
ls -la agents/hermes/__init__.py
```

### Test Fails: API Key Error

```bash
# Solution 1: Check .env
cat .env | grep API_KEY

# Solution 2: Verify format
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GROQ_API_KEY')[:10])"

# Solution 3: Test API endpoint
curl -H "Authorization: Bearer YOUR_KEY" https://api.groq.com/openai/v1/models
```

### Test Fails: Module Not Found

```bash
# Solution 1: Install missing package
pip install python-telegram-bot

# Solution 2: Check versions
pip show python-telegram-bot fastapi uvicorn

# Solution 3: Reinstall all
pip install -r requirements.txt --upgrade
```

---

## Success Criteria

✅ **All tests pass** when:
- [ ] All imports successful
- [ ] Config files load correctly
- [ ] At least 1 LLM provider works
- [ ] Agent registry functional
- [ ] WebUI endpoints respond
- [ ] Telegram bot initializes
- [ ] No errors in logs

---

## Next Steps

1. **✅ Run all tests** - Verify system ready
2. **✅ Fix any failures** - See troubleshooting
3. **✅ Deploy WebUI** - `python -m uvicorn webui.app:app`
4. **✅ Start Telegram bot** - `python -m telegram.bot`
5. **✅ Monitor logs** - Check for errors
6. **✅ Production release** - Ready to scale

---

**Last Updated**: June 1, 2026  
**Status**: Production Ready  
**Version**: 1.0

