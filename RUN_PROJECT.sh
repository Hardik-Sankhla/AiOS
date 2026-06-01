#!/bin/bash

# AIOS Complete Project Runner
# Run entire system: WebUI + Telegram Bot + Tests

PROJECT_DIR="/storage/emulated/0/projects/aios"
cd "$PROJECT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

clear

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          AIOS - COMPLETE PROJECT LAUNCHER                   ║"
echo "║     Telegram Bot + WebUI + Testing Suite                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

print_section() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Menu
echo ""
echo -e "${YELLOW}SELECT OPERATION:${NC}"
echo ""
echo "  QUICK OPERATIONS:"
echo "    1) Quick Test (30 seconds)"
echo "    2) Start WebUI Only"
echo "    3) Start Telegram Bot Only"
echo ""
echo "  COMBINED OPERATIONS:"
echo "    4) Start WebUI + Bot (2 terminals)"
echo "    5) Start WebUI + Bot (background)"
echo ""
echo "  TESTING:"
echo "    6) Run All Tests"
echo "    7) Unit Tests Only"
echo "    8) Integration Tests"
echo ""
echo "  UTILITIES:"
echo "    9) Health Check"
echo "    10) Stop All Services"
echo "    11) View Logs"
echo "    12) Exit"
echo ""
read -p "Enter choice (1-12): " choice

case $choice in
    1)
        print_section "QUICK TEST (30 SECONDS)"
        python3 << 'TESTEOF'
import sys
sys.path.insert(0, '/storage/emulated/0/projects/aios')

print("\n[1/5] Checking LLM layer...", flush=True)
try:
    from services.llm import LLMClient, ProviderManager
    print("✓ LLM layer ready", flush=True)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

print("[2/5] Checking agent framework...", flush=True)
try:
    from agents.hermes import get_registry
    registry = get_registry()
    print("✓ Agent framework ready", flush=True)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

print("[3/5] Checking configuration...", flush=True)
try:
    import json
    with open('configs/providers.json') as f:
        config = json.load(f)
    enabled = sum(1 for p in config['providers'].values() if p.get('enabled'))
    print(f"✓ Configuration ready ({enabled} providers enabled)", flush=True)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

print("[4/5] Checking WebUI...", flush=True)
try:
    from webui.app import app
    print("✓ WebUI ready", flush=True)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

print("[5/5] Checking Telegram bot...", flush=True)
try:
    from telegram.bot import HermesBot
    print("✓ Telegram bot ready", flush=True)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

print("\n✅ ALL SYSTEMS READY FOR OPERATION\n")
TESTEOF
        ;;

    2)
        print_section "STARTING WEBUI (FastAPI)"
        print_info "WebUI will start on http://localhost:8000"
        print_info "API Docs at http://localhost:8000/docs"
        print_info "Health check at http://localhost:8000/health"
        echo ""
        python -m uvicorn webui.app:app --host 0.0.0.0 --port 8000 --reload
        ;;

    3)
        print_section "STARTING TELEGRAM BOT"
        print_info "Bot will start and begin polling for messages"
        print_info "Send /start to your bot in Telegram to test"
        echo ""
        python -m telegram.bot
        ;;

    4)
        print_section "STARTING WEBUI + BOT (2 TERMINALS)"
        print_info "This requires two terminal sessions"
        echo ""
        print_info "Terminal 1: WebUI"
        echo "  python -m uvicorn webui.app:app --host 0.0.0.0 --port 8000"
        echo ""
        print_info "Terminal 2: Telegram Bot"
        echo "  python -m telegram.bot"
        echo ""
        read -p "Press Enter to start WebUI in background, then start bot in foreground..."
        
        python -m uvicorn webui.app:app --host 0.0.0.0 --port 8000 > webui.log 2>&1 &
        WEBUI_PID=$!
        print_status "WebUI started (PID: $WEBUI_PID)"
        print_info "WebUI logs: tail -f webui.log"
        
        sleep 2
        
        print_section "NOW STARTING TELEGRAM BOT"
        python -m telegram.bot
        
        echo ""
        print_info "Stopping WebUI..."
        kill $WEBUI_PID 2>/dev/null || true
        ;;

    5)
        print_section "STARTING WEBUI + BOT (BACKGROUND)"
        
        python -m uvicorn webui.app:app --host 0.0.0.0 --port 8000 > webui.log 2>&1 &
        WEBUI_PID=$!
        
        python -m telegram.bot > telegram.log 2>&1 &
        BOT_PID=$!
        
        print_status "WebUI started (PID: $WEBUI_PID, Log: webui.log)"
        print_status "Telegram Bot started (PID: $BOT_PID, Log: telegram.log)"
        
        echo ""
        print_info "Access points:"
        echo "  • WebUI: http://localhost:8000"
        echo "  • API Docs: http://localhost:8000/docs"
        echo "  • Health: http://localhost:8000/health"
        echo "  • Telegram: Search for your bot"
        
        echo ""
        print_info "View logs:"
        echo "  • WebUI: tail -f webui.log"
        echo "  • Bot: tail -f telegram.log"
        
        echo ""
        print_info "Stop services:"
        echo "  • kill $WEBUI_PID (WebUI)"
        echo "  • kill $BOT_PID (Bot)"
        echo "  • Or run: ./RUN_PROJECT.sh → option 10"
        ;;

    6)
        print_section "RUNNING ALL TESTS"
        echo ""
        print_info "Test 1: Module Import Tests"
        pytest tests/ -v || print_error "Unit tests failed"
        
        echo ""
        print_info "Test 2: Integration Tests"
        python scripts/test_llm_integration.py || print_error "Integration tests failed"
        
        echo ""
        print_info "Test 3: Hermes Workflow"
        python scripts/test_hermes_workflow.py || print_error "Workflow tests failed"
        
        echo ""
        print_status "All tests completed"
        ;;

    7)
        print_section "UNIT TESTS (pytest)"
        pytest tests/ -v --tb=short
        ;;

    8)
        print_section "INTEGRATION TESTS"
        echo ""
        print_info "LLM Integration Test"
        python scripts/test_llm_integration.py
        
        echo ""
        print_info "Hermes Workflow Test"
        python scripts/test_hermes_workflow.py
        ;;

    9)
        print_section "HEALTH CHECK"
        
        echo ""
        print_info "Checking modules..."
        python3 << 'HEALTHEOF'
import sys
sys.path.insert(0, '/storage/emulated/0/projects/aios')

try:
    from services.llm import LLMClient, ProviderManager
    from agents.hermes import get_registry
    from webui.app import app
    from telegram.bot import HermesBot
    print("✓ All modules loaded successfully\n")
    
    import json
    with open('configs/providers.json') as f:
        config = json.load(f)
    
    print("Providers Status:")
    for name, prov in config['providers'].items():
        status = "✓ enabled" if prov.get('enabled') else "○ disabled"
        print(f"  {status}: {name}")
    
    print("\n✓ System healthy and ready for operation")
except Exception as e:
    print(f"✗ Health check failed: {e}")
    import traceback
    traceback.print_exc()
HEALTHEOF

        echo ""
        print_info "Check WebUI (requires running): curl http://localhost:8000/health"
        ;;

    10)
        print_section "STOPPING ALL SERVICES"
        
        print_info "Stopping WebUI..."
        pkill -f "uvicorn webui.app" || print_error "WebUI not running"
        print_status "WebUI stopped"
        
        echo ""
        print_info "Stopping Telegram Bot..."
        pkill -f "python.*telegram.bot" || print_error "Bot not running"
        print_status "Bot stopped"
        
        echo ""
        print_status "All services stopped"
        ;;

    11)
        print_section "VIEW LOGS"
        echo ""
        echo -e "${YELLOW}Available logs:${NC}"
        echo "  1) WebUI log"
        echo "  2) Telegram bot log"
        echo "  3) System messages"
        echo ""
        read -p "Enter choice (1-3): " log_choice
        
        case $log_choice in
            1)
                if [ -f webui.log ]; then
                    tail -50 webui.log
                else
                    print_error "WebUI log not found"
                fi
                ;;
            2)
                if [ -f telegram.log ]; then
                    tail -50 telegram.log
                else
                    print_error "Telegram log not found"
                fi
                ;;
            3)
                print_info "Current processes:"
                ps aux | grep -E "python|uvicorn|telegram" | grep -v grep
                ;;
        esac
        ;;

    12)
        print_info "Exiting"
        exit 0
        ;;

    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

