# AIOS Quick Reference Card

**Hermes Agent Orchestration Platform**

---

## 30-Second Setup

```bash
cd /storage/emulated/0/projects/aios

# 1. Check configuration
cat .env | grep TELEGRAM_BOT_TOKEN

# 2. Install dependencies (if needed)
pip install 'python-telegram-bot>=20.0'

# 3. Start bot
python -m bot_service
```

---

## Using start_bot.sh

```bash
./start_bot.sh

# Menu options:
# 1) Run bot (foreground)
# 2) Run bot (background)
# 3) Run tests
# 4) View logs
# 5) Stop running bot
# 6) Exit
```

---

## Telegram Bot Commands

| Command | Effect |
|---------|--------|
| `/start` | Initialize session |
| `/research` | 🔍 Research mode |
| `/code` | 💻 Coding mode |
| `/status` | 📊 System status |
| `/memory` | 🧠 View memories |
| `/help` | ❓ Command help |

---

## WebUI

```bash
# Start server
python -m uvicorn webui.app:app --host 0.0.0.0 --port 8000

# Access
# Dashboard: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Health: http://localhost:8000/health
```

---

## Testing

```bash
# Quick test
pytest tests/ -v

# Integration test
python scripts/test_llm_integration.py

# Full system test
./start_bot.sh → option 3
```

---

## Key Files

| File | Purpose |
|------|---------|
| `.env` | Configuration (API keys, tokens) |
| `configs/providers.json` | LLM provider setup |
| `README.md` | Complete documentation |
| `DEPLOYMENT.md` | Production setup |
| `TELEGRAM_SETUP.md` | Bot configuration |
| `TESTING_GUIDE.md` | Testing procedures |
| `start_bot.sh` | Bot launcher script |

---

## Providers (8 Total)

```
Tier 1: Groq, Gemini, OpenRouter, Together
Tier 2: Cerebras, SambaNova, GitHub Models
Local: Ollama, LM Studio, vLLM, FreeLLMAPI
```

---

## LLM Services

```python
from services.llm import LLMClient, ProviderManager
import asyncio

async def test():
    manager = ProviderManager()
    client = LLMClient(manager, default_provider="groq")
    response = await client.chat_completion("Hello!")
    print(response.content)

asyncio.run(test())
```

---

## Agents

```python
from agents.hermes import get_registry, AgentConfig
from agents.hermes.concrete_agents import ResearchAgent

# Create agent
config = AgentConfig(name="ResearchAgent", description="Research", capabilities=["research"])
agent = ResearchAgent(config, llm_client=None)

# Register
registry = get_registry()
registry.register_agent("research", agent)

# Use
agent = registry.get_agent("research")
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Bot not responding | Check `.env` token, restart bot |
| Import errors | `export PYTHONPATH=/storage/emulated/0/projects/aios:$PYTHONPATH` |
| Port 8000 in use | Use different port: `--port 8001` |
| Dependencies missing | `pip install -r requirements.txt` |

---

## Documentation

- **README.md** - Full project guide
- **DEPLOYMENT.md** - Deployment across platforms
- **TELEGRAM_SETUP.md** - Telegram bot setup
- **TESTING_GUIDE.md** - Complete testing suite

---

## GitHub

```
Repository: github.com/Hardik-Sankhla/AiOS
Branch: main
Status: ✅ Production Ready
```

---

## Support

- **Issues**: Check troubleshooting in docs
- **Examples**: See `scripts/` directory
- **Questions**: Open GitHub issue

---

**Last Updated**: June 1, 2026  
**Version**: 1.0  
**Status**: Production Ready

