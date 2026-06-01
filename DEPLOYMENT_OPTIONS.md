# AIOS Deployment Options - Complete Reference

Choose your deployment method based on your platform and needs.

---

## 🎯 Quick Decision Matrix

| Environment | Recommended | Command |
|------------|-------------|---------|
| **Mobile (Termux)** | Docker-Lite | `bash docker-lite up` |
| **Linux VPS** | Docker Compose | `docker-compose up -d` |
| **Desktop Dev** | MASTER_RUN.sh | `bash MASTER_RUN.sh` |
| **Simple Start** | Direct Python | `python -m uvicorn ...` |

---

## 1. 📱 MOBILE (Termux/Android) - Docker-Lite

**Best for:** Android, Termux, resource-constrained devices

### Setup
```bash
cd /storage/emulated/0/projects/aios
```

### Start All Services
```bash
bash docker-lite up
```

### Start in Background
```bash
bash docker-lite up -d
docker-lite ps              # Check status
docker-lite logs webui -f   # Follow logs
```

### Commands
```bash
docker-lite ps              # List services
docker-lite logs bot -f     # Follow bot logs
docker-lite stats           # Resource usage
docker-lite down            # Stop all services
```

### Advantages
- ✓ Minimal overhead (200-300MB vs 500MB+ for Docker)
- ✓ No Docker required
- ✓ Docker-like experience
- ✓ Perfect for Termux
- ✓ Battery efficient

### Files
- `docker-lite.py` - Engine (500+ lines)
- `docker-lite` - CLI wrapper
- `.docker-lite` - Service state
- `logs/` - Unified logs

---

## 2. 🐳 DOCKER (Full Deployment)

**Best for:** Production, Linux VPS, consistent environments

### Option A: Docker Compose (Recommended)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# View specific service
docker-compose logs -f webui
```

### Option B: Docker Build & Run
```bash
# Build image
docker build -t aios .

# Run WebUI
docker run -p 8000:8000 \
  -e GROQ_API_KEY="your_key" \
  -e TELEGRAM_BOT_TOKEN="your_token" \
  aios

# Run Bot
docker run \
  -e GROQ_API_KEY="your_key" \
  -e TELEGRAM_BOT_TOKEN="your_token" \
  aios python -m bot_service
```

### Advantages
- ✓ Production-ready
- ✓ Isolated environments
- ✓ Easy scaling
- ✓ Standard DevOps tools
- ✓ Cloud deployment ready

### Files
- `Dockerfile` - Image definition
- `docker-compose.yml` - Orchestration
- `.env` - Configuration

---

## 3. 🖥️ DESKTOP/DEVELOPMENT - MASTER_RUN.sh

**Best for:** Development, learning, debugging

### Interactive Menu
```bash
cd /storage/emulated/0/projects/aios
bash MASTER_RUN.sh
```

Then select from 12 options:
```
1) Quick Test (30 seconds)
2) Start WebUI Only
3) Start Telegram Bot Only
4) Start WebUI + Bot (2 terminals)
5) Start WebUI + Bot (background) ⭐
6) Run All Tests
7) Unit Tests Only
8) Integration Tests
9) Health Check
10) Stop All Services
11) View Logs
12) Exit
```

### Non-Interactive Usage
```bash
bash MASTER_RUN.sh --start-all          # Start all services
bash MASTER_RUN.sh --start-webui        # WebUI only
bash MASTER_RUN.sh --start-bot          # Bot only
bash MASTER_RUN.sh --test               # Run tests
bash MASTER_RUN.sh --health             # Health check
bash MASTER_RUN.sh --logs               # View logs
bash MASTER_RUN.sh --stop               # Stop all
```

### Advantages
- ✓ Interactive menu
- ✓ Easy to use
- ✓ Good for learning
- ✓ Multiple operation modes
- ✓ Detailed logging

### Files
- `MASTER_RUN.sh` - Interactive launcher
- `logs/` - Session logs
- `.aios_pids` - Process tracking

---

## 4. 🔧 DIRECT PYTHON (Manual)

**Best for:** Testing, debugging, learning internals

### Start WebUI
```bash
cd /storage/emulated/0/projects/aios
python -m uvicorn webui.app:app --host 0.0.0.0 --port 8000

# Or with options
python -m uvicorn webui.app:app \
  --reload \
  --host 0.0.0.0 \
  --port 8000 \
  --log-level debug
```

### Start Bot (New Terminal)
```bash
python -m bot_service
```

### Run Tests
```bash
pytest tests/ -v
python scripts/test_llm_integration.py
python scripts/test_hermes_workflow.py
```

### Access
- Dashboard: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

### Advantages
- ✓ Full control
- ✓ Easy debugging
- ✓ Direct output
- ✓ No overhead

---

## 5. ☁️ CLOUD DEPLOYMENT

**Best for:** AWS, GCP, Azure, Heroku

### Step 1: Create cloud server
```bash
# AWS EC2, DigitalOcean, etc.
ssh user@your-server.com
```

### Step 2: Clone & setup
```bash
cd /home/deploy
git clone https://github.com/yourusername/aios.git
cd aios
cp .env.example .env
# Edit .env with your keys
```

### Step 3: Deploy
```bash
# Option A: Docker Compose
docker-compose up -d

# Option B: systemd service
sudo cp deployment/aios.service /etc/systemd/system/
sudo systemctl enable aios
sudo systemctl start aios
```

### Access from Anywhere
```bash
# http://your-server.com:8000
# https://your-server.com (with nginx/SSL)
```

---

## 📊 Comparison Table

| Feature | Docker-Lite | Docker | MASTER_RUN | Direct Python |
|---------|------------|--------|-----------|-----------------|
| **Platform** | Mobile | Linux | Desktop | Any |
| **Setup** | ⚡ Fast | ⏱️ Medium | ⚡ Fast | ⚡ Fast |
| **Resource** | 💚 Light | 🔴 Heavy | 💛 Medium | 💚 Light |
| **Learning** | ✓ Good | ✓ Excellent | ✓✓ Best | ✓ Good |
| **Production** | ⚠️ Limited | ✓✓ Best | ❌ No | ❌ No |
| **Scaling** | ❌ No | ✓✓ Yes | ❌ No | ❌ No |
| **CLI** | Docker-like | Docker | Menu | None |

---

## 🚀 Getting Started

### I have Termux on Android
👉 Use **Docker-Lite**
```bash
bash docker-lite up
```
See [MOBILE_GUIDE.md](MOBILE_GUIDE.md)

### I want to develop locally
👉 Use **MASTER_RUN.sh**
```bash
bash MASTER_RUN.sh
```

### I want production deployment
👉 Use **Docker Compose**
```bash
docker-compose up -d
```

### I want maximum control
👉 Use **Direct Python**
```bash
python -m uvicorn webui.app:app --host 0.0.0.0 --port 8000
```

---

## 📝 Configuration

All methods use the same `.env` file:
```bash
GROQ_API_KEY=your_key
GOOGLE_API_KEY=your_key
TELEGRAM_BOT_TOKEN=your_token
```

See `.env.example` for all available options.

---

## 🔍 Troubleshooting

### Port Already in Use
```bash
# Find what's using port 8000
lsof -i :8000

# Use different port
docker-lite up webui --port 8001
python -m uvicorn webui.app:app --port 8001
```

### Services won't start
```bash
# Check logs
docker-lite logs webui       # Docker-Lite
docker-compose logs webui    # Docker
cat logs/webui_*.log         # Direct

# Check .env
cat .env | grep GROQ
```

### Out of memory
```bash
# Check usage
docker-lite stats

# Reduce services
docker-lite down bot         # Keep WebUI only
```

---

## 🎯 Quick Reference

**Mobile (Termux)**
```bash
bash docker-lite up
```

**Desktop Dev**
```bash
bash MASTER_RUN.sh
```

**Production (Docker)**
```bash
docker-compose up -d
```

**Direct Control**
```bash
python -m uvicorn webui.app:app --host 0.0.0.0 --port 8000
```

---

## 📚 Related Files

- [MOBILE_GUIDE.md](MOBILE_GUIDE.md) - Mobile-specific deployment
- [COMMANDS.md](COMMANDS.md) - All available commands
- [QUICK_START.md](QUICK_START.md) - Quick reference
- [README.md](README.md) - Project overview
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment details

---

**Choose your deployment method and start building! 🚀**

