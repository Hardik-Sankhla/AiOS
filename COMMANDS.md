# AIOS Complete Command Reference

**All commands to run the entire Hermes AIOS project**

---

## 🚀 FASTEST START (Copy & Paste)

### Quick Test (30 seconds)
```bash
cd /storage/emulated/0/projects/aios
./RUN_PROJECT.sh
# Choose option 1
```

### Start Everything in Background
```bash
cd /storage/emulated/0/projects/aios
./RUN_PROJECT.sh
# Choose option 5
```

### Start WebUI
```bash
cd /storage/emulated/0/projects/aios
python -m uvicorn webui.app:app --host 0.0.0.0 --port 8000
# Access: http://localhost:8000
```

### Start Telegram Bot
```bash
cd /storage/emulated/0/projects/aios
python -m telegram.bot
```

---

## 📋 INTERACTIVE LAUNCHER (Recommended)

### Main Launcher with Menu
```bash
cd /storage/emulated/0/projects/aios
./RUN_PROJECT.sh
```

**Menu Options:**
- 1) Quick Test (30 seconds)
- 2) Start WebUI Only
- 3) Start Telegram Bot Only
- 4) Start WebUI + Bot (2 terminals)
- 5) Start WebUI + Bot (background)
- 6) Run All Tests
- 7) Unit Tests Only
- 8) Integration Tests
- 9) Health Check
- 10) Stop All Services
- 11) View Logs
- 12) Exit

### Bot Launcher with Menu
```bash
cd /storage/emulated/0/projects/aios
./start_bot.sh
```

**Menu Options:**
- 1) Run bot (foreground)
- 2) Run bot (background)
- 3) Run tests
- 4) View logs
- 5) Stop running bot
- 6) Exit

---

## 🌐 WEBUI COMMANDS

### Start WebUI (Development)
```bash
cd /storage/emulated/0/projects/aios
python -m uvicorn webui.app:app --reload --host 0.0.0.0 --port 8000
```

### Start WebUI (Production)
```bash
cd /storage/emulated/0/projects/aios
python -m uvicorn webui.app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Start WebUI (Background with Logs)
```bash
cd /storage/emulated/0/projects/aios
nohup python -m uvicorn webui.app:app --host 0.0.0.0 --port 8000 > webui.log 2>&1 &
```

### Access WebUI
```bash
# Dashboard
http://localhost:8000

# API Documentation (Auto-generated)
http://localhost:8000/docs

# API Redoc
http://localhost:8000/redoc

# Health Check
http://localhost:8000/health

# Get Agents
http://localhost:8000/api/agents

# Get Providers
http://localhost:8000/api/providers
```

### View WebUI Logs
```bash
tail -f webui.log
```

### Stop WebUI
```bash
# Method 1: Kill process
pkill -f "uvicorn webui.app"

# Method 2: Get PID and kill
ps aux | grep uvicorn
kill <PID>
```

---

## 🤖 TELEGRAM BOT COMMANDS

### Start Bot (Foreground)
```bash
cd /storage/emulated/0/projects/aios
python -m telegram.bot
```

### Start Bot (Background)
```bash
cd /storage/emulated/0/projects/aios
nohup python -m telegram.bot > telegram.log 2>&1 &
```

### Start Bot with Debug
```bash
cd /storage/emulated/0/projects/aios
TELEGRAM_DEBUG=true python -m telegram.bot
```

### Using Launcher Script
```bash
cd /storage/emulated/0/projects/aios
./start_bot.sh
```

### View Bot Logs
```bash
tail -f telegram.log
```

### Stop Bot
```bash
# Method 1: Kill process
pkill -f "python.*telegram.bot"

# Method 2: Get PID and kill
ps aux | grep telegram.bot
kill <PID>
```

### Test Bot in Telegram
```
/start           # Initialize
/research        # Research mode
/code            # Coding mode
/status          # System status
/memory          # View memories
/help            # Command help
```

---

## 🧪 TESTING COMMANDS

### Quick Test (30 seconds)
```bash
cd /storage/emulated/0/projects/aios
python << 'EOF'
import sys
sys.path.insert(0, '/storage/emulated/0/projects/aios')
from services.llm import LLMClient
from agents.hermes import get_registry
from telegram.bot import HermesBot
print('✅ All systems ready')
EOF
```

### Run All Tests
```bash
cd /storage/emulated/0/projects/aios
pytest tests/ -v
```

### Run Specific Test File
```bash
cd /storage/emulated/0/projects/aios
pytest tests/test_llm.py -v
```

### Run with Coverage
```bash
cd /storage/emulated/0/projects/aios
pytest --cov=services --cov=agents tests/
```

### LLM Integration Tests
```bash
cd /storage/emulated/0/projects/aios
python scripts/test_llm_integration.py
```

### Hermes Workflow Tests
```bash
cd /storage/emulated/0/projects/aios
python scripts/test_hermes_workflow.py
```

### Run All Scripts
```bash
cd /storage/emulated/0/projects/aios
bash << 'EOF'
echo "Running all tests..."
pytest tests/ -v
python scripts/test_llm_integration.py
python scripts/test_hermes_workflow.py
echo "All tests complete"
EOF
```

---

## 📊 HEALTH CHECK COMMANDS

### Full System Check
```bash
cd /storage/emulated/0/projects/aios
python << 'EOF'
import sys
sys.path.insert(0, '/storage/emulated/0/projects/aios')

print("=== AIOS SYSTEM CHECK ===\n")

# Check imports
print("[1/5] LLM Services...")
from services.llm import LLMClient, ProviderManager
print("✓ LLM ready\n")

print("[2/5] Agent Framework...")
from agents.hermes import get_registry
print("✓ Agents ready\n")

print("[3/5] Configuration...")
import json
with open('configs/providers.json') as f:
    config = json.load(f)
enabled = sum(1 for p in config['providers'].values() if p.get('enabled'))
print(f"✓ Config ready ({enabled} providers)\n")

print("[4/5] WebUI...")
from webui.app import app
print("✓ WebUI ready\n")

print("[5/5] Telegram Bot...")
from telegram.bot import HermesBot
print("✓ Bot ready\n")

print("✅ SYSTEM HEALTHY")
EOF
```

### WebUI Health Check (requires running)
```bash
curl http://localhost:8000/health | python -m json.tool
```

### Check Providers
```bash
cd /storage/emulated/0/projects/aios
python << 'EOF'
import json
with open('configs/providers.json') as f:
    config = json.load(f)

print("Providers Status:")
for name, prov in config['providers'].items():
    status = "✓" if prov.get('enabled') else "○"
    print(f"  {status} {name}: {prov.get('type', 'unknown')}")

print(f"\nFallback order: {' → '.join(config['fallback_order'])}")
EOF
```

### Check Dependencies
```bash
pip list | grep -E "fastapi|uvicorn|python-telegram|httpx|requests"
```

---

## 🔄 COMBINED OPERATIONS

### Start Everything (WebUI + Bot in Background)
```bash
cd /storage/emulated/0/projects/aios

# WebUI
python -m uvicorn webui.app:app --host 0.0.0.0 --port 8000 > webui.log 2>&1 &
echo "WebUI started"

# Bot
python -m telegram.bot > telegram.log 2>&1 &
echo "Bot started"

# Show status
echo ""
echo "Access WebUI: http://localhost:8000"
echo "View logs: tail -f webui.log & tail -f telegram.log"
```

### Run Tests Then Start Services
```bash
cd /storage/emulated/0/projects/aios

# Run tests first
echo "Running tests..."
pytest tests/ -v

# If tests pass, start services
echo ""
echo "Tests complete. Starting services..."
python -m uvicorn webui.app:app --host 0.0.0.0 --port 8000 > webui.log 2>&1 &
python -m telegram.bot > telegram.log 2>&1 &
echo "Services started"
```

### Complete Development Workflow
```bash
cd /storage/emulated/0/projects/aios

# 1. Test
echo "Step 1: Testing..."
pytest tests/ -v

# 2. Check health
echo -e "\nStep 2: Health check..."
python scripts/test_llm_integration.py

# 3. Start WebUI
echo -e "\nStep 3: Starting WebUI..."
python -m uvicorn webui.app:app --host 0.0.0.0 --port 8000 > webui.log 2>&1 &
sleep 2

# 4. Start Bot
echo "Step 4: Starting Telegram Bot..."
python -m telegram.bot > telegram.log 2>&1 &

# 5. Show status
echo -e "\n✅ All systems running"
echo "WebUI: http://localhost:8000"
echo "Logs: tail -f webui.log & tail -f telegram.log"
```

---

## 🛑 STOPPING SERVICES

### Stop WebUI
```bash
pkill -f "uvicorn webui.app"
```

### Stop Telegram Bot
```bash
pkill -f "python.*telegram.bot"
```

### Stop Everything
```bash
pkill -f "uvicorn webui.app"
pkill -f "python.*telegram.bot"
echo "All services stopped"
```

### Kill by Process ID
```bash
# Find processes
ps aux | grep -E "uvicorn|telegram" | grep -v grep

# Kill specific
kill <PID>
```

---

## 🐳 DOCKER COMMANDS

### Build Docker Image
```bash
cd /storage/emulated/0/projects/aios
docker build -t aios .
```

### Run WebUI in Docker
```bash
docker run -p 8000:8000 \
  -e GROQ_API_KEY="your_key" \
  -e TELEGRAM_BOT_TOKEN="your_token" \
  aios
```

### Run with docker-compose
```bash
cd /storage/emulated/0/projects/aios
docker-compose up -d
```

### View Docker Logs
```bash
docker logs -f <container_id>
```

---

## 📁 CONFIGURATION COMMANDS

### Check .env File
```bash
cd /storage/emulated/0/projects/aios
cat .env | grep -E "GROQ|GOOGLE|OPENROUTER|TELEGRAM"
```

### Verify Configuration
```bash
cd /storage/emulated/0/projects/aios
python << 'EOF'
import os
from dotenv import load_dotenv

load_dotenv()

print("Configuration Check:")
print(f"  GROQ_API_KEY: {'✓' if os.getenv('GROQ_API_KEY') else '✗'}")
print(f"  GOOGLE_API_KEY: {'✓' if os.getenv('GOOGLE_API_KEY') else '✗'}")
print(f"  TELEGRAM_BOT_TOKEN: {'✓' if os.getenv('TELEGRAM_BOT_TOKEN') else '✗'}")
print(f"  OPENROUTER_API_KEY: {'✓' if os.getenv('OPENROUTER_API_KEY') else '✗'}")
EOF
```

---

## 💾 LOG COMMANDS

### View WebUI Logs
```bash
tail -f /storage/emulated/0/projects/aios/webui.log
```

### View Bot Logs
```bash
tail -f /storage/emulated/0/projects/aios/telegram.log
```

### View Last 50 Lines
```bash
tail -50 /storage/emulated/0/projects/aios/webui.log
tail -50 /storage/emulated/0/projects/aios/telegram.log
```

### Real-time Log Monitoring
```bash
# Both logs in one window
tail -f /storage/emulated/0/projects/aios/webui.log &
tail -f /storage/emulated/0/projects/aios/telegram.log
```

### Clear Logs
```bash
> /storage/emulated/0/projects/aios/webui.log
> /storage/emulated/0/projects/aios/telegram.log
```

---

## 🔍 DEBUGGING COMMANDS

### Check Python Path
```bash
python -c "import sys; print('\n'.join(sys.path))"
```

### Verify Imports
```bash
cd /storage/emulated/0/projects/aios
python << 'EOF'
import sys
sys.path.insert(0, '/storage/emulated/0/projects/aios')

modules = [
    'services.llm',
    'agents.hermes',
    'webui.app',
    'telegram.bot'
]

for mod in modules:
    try:
        __import__(mod)
        print(f"✓ {mod}")
    except Exception as e:
        print(f"✗ {mod}: {e}")
EOF
```

### List Running Processes
```bash
ps aux | grep -E "python|uvicorn|telegram" | grep -v grep
```

### Check Port Usage
```bash
lsof -i :8000  # WebUI
ps aux | grep telegram.bot  # Bot
```

---

## 📈 MONITORING

### System Status
```bash
top -p $(pgrep -f "uvicorn|python")
```

### Real-time Statistics
```bash
watch -n 1 'ps aux | grep -E "uvicorn|telegram"'
```

### Test Load
```bash
# Run multiple concurrent requests
for i in {1..10}; do
  curl -s http://localhost:8000/health &
done
```

---

## 🚨 TROUBLESHOOTING

### Port Already in Use
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Use different port
python -m uvicorn webui.app:app --port 8001
```

### Import Errors
```bash
# Add to PYTHONPATH
export PYTHONPATH=/storage/emulated/0/projects/aios:$PYTHONPATH
python -m telegram.bot
```

### Bot Not Responding
```bash
# Check token
echo $TELEGRAM_BOT_TOKEN

# Test token validity
curl -X POST https://api.telegram.org/botTOKEN/getMe

# Restart bot
pkill -f "python.*telegram.bot"
python -m telegram.bot
```

### Dependencies Missing
```bash
pip install -r requirements.txt --upgrade
```

---

## 📞 Quick Command Summary

```bash
# 1. Navigate to project
cd /storage/emulated/0/projects/aios

# 2. Quick test (30 seconds)
./RUN_PROJECT.sh → option 1

# 3. Start WebUI
python -m uvicorn webui.app:app --host 0.0.0.0 --port 8000

# 4. Start Bot (new terminal)
python -m telegram.bot

# 5. Run tests
pytest tests/ -v

# 6. Health check
./RUN_PROJECT.sh → option 9

# 7. Stop services
./RUN_PROJECT.sh → option 10
```

---

**All commands are ready to copy and paste!**

