# AIOS Mobile Guide - Docker-Lite System

**Run your entire AI system on mobile (Termux) without Docker overhead!**

---

## 🚀 Quick Start (Copy & Paste)

### Start All Services
```bash
cd /storage/emulated/0/projects/aios
./docker-lite up
```

### Start Specific Service
```bash
./docker-lite up webui      # WebUI only
./docker-lite up bot        # Telegram bot only
```

### Run in Background
```bash
./docker-lite up -d         # Start all in background
```

### Check Running Services
```bash
./docker-lite ps            # List all services
```

### View Logs
```bash
./docker-lite logs webui       # View WebUI logs
./docker-lite logs bot -f      # Follow bot logs in real-time
./docker-lite logs webui --tail 100  # Last 100 lines
```

### Stop Services
```bash
./docker-lite down          # Stop all
./docker-lite down webui    # Stop specific service
./docker-lite down --force  # Force kill
```

---

## 📊 System Monitoring

### Check Resource Usage
```bash
./docker-lite stats         # CPU, Memory, PID
```

### View Running Services
```bash
./docker-lite ps            # Service list with uptime
```

---

## 🎯 Common Workflows

### 1. Development (Follow Logs)
```bash
# Terminal 1
./docker-lite up
```
This starts all services and follows logs until Ctrl+C.

### 2. Background Operation
```bash
# Terminal 1
./docker-lite up -d

# Terminal 2 (optional)
./docker-lite ps
./docker-lite logs webui -f
```

### 3. Testing + Running
```bash
./docker-lite exec pytest tests/    # Run tests
./docker-lite up                    # Start services
```

### 4. Multi-Service Setup
```bash
# Terminal 1 - WebUI only
./docker-lite up webui

# Terminal 2 - Bot only
./docker-lite up bot

# Terminal 3 - Monitor both
./docker-lite ps
./docker-lite logs webui -f
./docker-lite logs bot -f
```

---

## 🔧 Docker-Lite Commands

| Command | Purpose |
|---------|---------|
| `up [services] [-d]` | Start services |
| `down [services] [--force]` | Stop services |
| `ps` | List running services |
| `logs <service> [-f] [--tail N]` | View logs |
| `stats` | Resource usage |
| `exec <cmd>` | Execute command |
| `help` | Show help |

---

## 📱 Mobile-Specific Tips

### Battery Optimization
```bash
# Start without detach to stop easily with Ctrl+C
./docker-lite up

# Or use background mode
./docker-lite up -d
# Monitor with: ./docker-lite ps
# Stop with: ./docker-lite down
```

### Storage Optimization
- Logs are stored in `logs/` directory
- Rotate old logs:
  ```bash
  rm -rf logs/*_old_*
  ```

### Memory Management
```bash
# Monitor memory usage
./docker-lite stats

# Kill specific service if memory is high
./docker-lite down bot
```

---

## 🎮 Interactive Mode (MASTER_RUN.sh)

For manual control with menu:
```bash
bash MASTER_RUN.sh
```

This provides interactive menu for:
- Start all services
- Start individual services
- Run tests
- View logs
- Health checks
- Stop services

---

## 📝 Service Details

### WebUI Service
```bash
./docker-lite up webui

# Access: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Health: http://localhost:8000/health
```

### Telegram Bot Service
```bash
./docker-lite up bot

# Status: Polling for messages
# Test: Send /start to your bot
# Commands: /research, /code, /status, /memory, /help
```

---

## 🔍 Troubleshooting

### Service won't start
```bash
./docker-lite logs <service>  # Check error logs
./docker-lite down --force    # Force kill and retry
./docker-lite up <service>    # Start again
```

### High memory usage
```bash
./docker-lite stats           # Check which service
./docker-lite down <service>  # Stop heavy service
```

### Check .env configuration
```bash
cat .env | grep -E "GROQ|GOOGLE|TELEGRAM"
```

### Verify all dependencies
```bash
python -c "from dotenv import load_dotenv; from bot_service import HermesBot; print('✓ All ready')"
```

---

## 🆚 Docker-Lite vs Docker

| Feature | Docker-Lite | Docker |
|---------|-------------|--------|
| **Overhead** | Minimal | High |
| **Mobile** | ✓ Perfect | ✗ Heavy |
| **Logs** | Unified | Separate |
| **Process Mgmt** | Simple | Complex |
| **CLI** | Docker-like | Full Docker |
| **Storage** | ~100MB | >500MB |

---

## 📊 File Structure

```
/storage/emulated/0/projects/aios/
├── docker-lite              # Main command
├── docker-lite.py           # Python engine
├── MASTER_RUN.sh            # Interactive menu
├── .docker-lite             # Service state (auto-created)
├── logs/                    # All service logs
│   ├── webui_*.log
│   └── bot_*.log
├── webui/                   # FastAPI app
├── bot_service/             # Telegram bot
├── agents/                  # AI agents
└── services/                # LLM services
```

---

## ✨ Performance

- **Startup time**: ~5 seconds
- **Memory per service**: ~50-100MB
- **CPU usage**: Minimal (idle)
- **Log storage**: ~1MB per session
- **Total overhead**: ~200-300MB (much less than Docker)

---

## 🎯 Recommended Setup for Mobile

### Option 1: Quick Daily Use
```bash
./docker-lite up -d          # Start in background
./docker-lite ps             # Check status
# ... use WebUI and Bot ...
./docker-lite down           # Stop when done
```

### Option 2: Development
```bash
./docker-lite up             # Follow logs during dev
# Press Ctrl+C when done (logs stop, services stop)
```

### Option 3: Always Running (with monitoring)
```bash
nohup bash -c './docker-lite up -d; tail -f logs/*.log' &
# Monitor in another terminal: ./docker-lite ps
```

---

## 🚀 Next Steps

1. **Start now**: `./docker-lite up`
2. **Check services**: `./docker-lite ps`
3. **View WebUI**: `http://localhost:8000`
4. **Test bot**: Send `/start` to your bot
5. **Monitor**: `./docker-lite logs webui -f`
6. **Stop**: `./docker-lite down`

---

**Docker-Lite: Enterprise-grade containerization for mobile! 🎯**

