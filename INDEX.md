# AIOS - Complete System Index

**Your AI Orchestration System - Choose Your Deployment**

---

## 🎯 START HERE - Pick Your Method

### 🚀 I'm on Mobile (Android/Termux)
```bash
bash docker-lite up
```
**→ See:** [MOBILE_GUIDE.md](MOBILE_GUIDE.md)

### 🖥️ I Want Development Mode
```bash
bash MASTER_RUN.sh
```
**→ See:** [COMMANDS.md](COMMANDS.md)

### 🐳 I Want Production Docker
```bash
docker-compose up -d
```
**→ See:** [DEPLOYMENT_OPTIONS.md](DEPLOYMENT_OPTIONS.md)

### 🔧 I Want Simple Direct Control
```bash
python -m uvicorn webui.app:app --host 0.0.0.0 --port 8000
```
**→ See:** [QUICK_START.md](QUICK_START.md)

---

## 📚 Documentation Guide

| File | Purpose | Best For |
|------|---------|----------|
| **[MOBILE_GUIDE.md](MOBILE_GUIDE.md)** | Docker-Lite system guide | Mobile users |
| **[DEPLOYMENT_OPTIONS.md](DEPLOYMENT_OPTIONS.md)** | All deployment methods | Understanding options |
| **[COMMANDS.md](COMMANDS.md)** | 100+ commands reference | Command reference |
| **[QUICK_START.md](QUICK_START.md)** | Quick reference card | Quick lookup |
| **[README.md](README.md)** | Project overview | Understanding AIOS |
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | Production setup | Server deployment |
| **[TESTING_GUIDE.md](TESTING_GUIDE.md)** | Testing procedures | Running tests |
| **[TELEGRAM_SETUP.md](TELEGRAM_SETUP.md)** | Bot configuration | Bot setup |

---

## 🚀 System Components

### Core Services
- **WebUI** - FastAPI dashboard at `http://localhost:8000`
- **Telegram Bot** - Message handler with `/start`, `/research`, `/code`, etc.
- **LLM Providers** - 8 providers: Groq, Google, OpenRouter, Together, Cerebras, SambaNova, GitHub, Ollama
- **Agent Framework** - Hermes orchestration with Research & Coding agents

### Key Directories
```
.
├── docker-lite.py           # Mobile container engine
├── docker-lite              # CLI wrapper
├── MASTER_RUN.sh            # Interactive launcher
├── Dockerfile               # Docker image
├── docker-compose.yml       # Container orchestration
│
├── webui/                   # FastAPI application
├── bot_service/             # Telegram bot
├── agents/                  # AI agents (Hermes)
├── services/                # LLM integration
│
├── tests/                   # Test suite
├── configs/                 # Configuration files
├── logs/                    # Application logs
│
└── [Documentation files]
```

---

## 🎮 Deployment Methods Comparison

| Feature | Mobile | Docker | Desktop | Direct |
|---------|--------|--------|---------|--------|
| **Command** | `docker-lite up` | `docker-compose up` | `MASTER_RUN.sh` | `python -m ...` |
| **Setup** | 🟢 Easy | 🟡 Medium | 🟢 Easy | 🟢 Easy |
| **Resource** | 💚 Low | 🔴 High | 💛 Medium | 💚 Low |
| **Best For** | Termux | Production | Learning | Simple |

---

## 📖 Common Tasks

### Start Services
**Mobile:** `bash docker-lite up`
**Docker:** `docker-compose up -d`
**Desktop:** `bash MASTER_RUN.sh` → option 5

### Check Status
**Mobile:** `bash docker-lite ps`
**Docker:** `docker-compose ps`
**Desktop:** `bash MASTER_RUN.sh` → option 6

### View Logs
**Mobile:** `bash docker-lite logs webui -f`
**Docker:** `docker-compose logs -f webui`
**Desktop:** `bash MASTER_RUN.sh` → option 11

### Stop Services
**Mobile:** `bash docker-lite down`
**Docker:** `docker-compose down`
**Desktop:** `bash MASTER_RUN.sh` → option 10

### Run Tests
**All:** `pytest tests/ -v`

---

## 🔗 Quick Links

**Deployment:**
- [DEPLOYMENT_OPTIONS.md](DEPLOYMENT_OPTIONS.md) - Compare all methods
- [MOBILE_GUIDE.md](MOBILE_GUIDE.md) - Mobile optimization
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production setup

**Usage:**
- [COMMANDS.md](COMMANDS.md) - All 100+ commands
- [QUICK_START.md](QUICK_START.md) - One-page reference
- [README.md](README.md) - Project overview

**Configuration:**
- [.env.example](.env.example) - Configuration template
- [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md) - Bot configuration
- [configs/providers.json](configs/providers.json) - LLM providers

**Testing:**
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Test procedures
- [tests/](tests/) - Test files
- [scripts/](scripts/) - Test scripts

---

## ⚙️ System Details

### LLM Providers (8 Total)
- **Tier 1:** Groq (fastest), Google Gemini, OpenRouter (100+ models), Together AI
- **Tier 2:** Cerebras, SambaNova, GitHub Models
- **Local:** Ollama (fallback)

### Agents Available
- **Research Agent** - Analysis and research capabilities
- **Coding Agent** - Code generation and architecture
- **Custom Agents** - Extensible framework

### API Endpoints
- `GET /` - Dashboard
- `GET /health` - Health check
- `GET /api/agents` - List agents
- `GET /api/providers` - List providers
- `POST /api/chat` - Chat endpoint
- `WS /ws/chat/{client_id}` - WebSocket

---

## 🎯 Workflows

### Quick Test (30 seconds)
```bash
# Mobile
bash docker-lite up -d
bash docker-lite ps

# Desktop
bash MASTER_RUN.sh → 1
```

### Development (Follow Logs)
```bash
# Mobile
bash docker-lite up

# Desktop
bash MASTER_RUN.sh → 5
```

### Background Deployment
```bash
# Mobile
bash docker-lite up -d
bash docker-lite logs webui -f

# Docker
docker-compose up -d
docker-compose logs -f
```

### Full Testing
```bash
pytest tests/ -v
python scripts/test_llm_integration.py
python scripts/test_hermes_workflow.py
```

---

## 🔍 Troubleshooting

### Can't start bot
```bash
# Check .env
cat .env | grep TELEGRAM

# Check logs
docker-lite logs bot
```

### WebUI not responding
```bash
# Check port
lsof -i :8000

# Check health
curl http://localhost:8000/health
```

### High memory usage
```bash
# Monitor
docker-lite stats

# Stop heavy service
docker-lite down bot
```

---

## 📱 Mobile Setup (Quick)

```bash
cd /storage/emulated/0/projects/aios
bash docker-lite up              # Start all
# or
bash docker-lite up -d           # Background
docker-lite ps                   # Check
docker-lite logs webui -f        # Monitor
docker-lite down                 # Stop
```

---

## 🐳 Docker Setup (Quick)

```bash
docker-compose up -d             # Start all
docker-compose logs -f           # Monitor
docker-compose down              # Stop
```

---

## 🚀 Deploy to Cloud

```bash
# SSH to server
ssh user@server.com

# Clone project
git clone https://github.com/yourusername/aios.git
cd aios

# Setup
cp .env.example .env
# Edit .env with your keys

# Deploy
docker-compose up -d

# Access
http://server.com:8000
```

---

## 📞 Support

**Issues?** Check the specific guide:
- Mobile issues → [MOBILE_GUIDE.md](MOBILE_GUIDE.md)
- Docker issues → [DEPLOYMENT_OPTIONS.md](DEPLOYMENT_OPTIONS.md)
- Testing issues → [TESTING_GUIDE.md](TESTING_GUIDE.md)
- Bot issues → [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md)

**Commands?** See:
- [COMMANDS.md](COMMANDS.md) - All commands
- [QUICK_START.md](QUICK_START.md) - Common commands

---

## ✅ Status

- ✅ All deployment methods ready
- ✅ Bot service operational
- ✅ WebUI server tested
- ✅ Tests passing
- ✅ Documentation complete
- ✅ Mobile optimized
- ✅ Production ready

---

**Choose your deployment method and start building! 🚀**

[→ Get Started with Your Method](#start-here---pick-your-method)

