#!/bin/bash

# AIOS Telegram Bot Starter Script
# Quick setup and launch for Hermes AIOS Telegram integration

set -e  # Exit on error

PROJECT_DIR="/storage/emulated/0/projects/aios"
cd "$PROJECT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════╗"
echo "║     AIOS Telegram Bot Startup Script              ║"
echo "║     Hermes Agent Orchestration Platform           ║"
echo "╚════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check .env file
echo ""
print_info "Checking configuration..."
if [ ! -f .env ]; then
    print_error ".env file not found"
    echo "Creating from template..."
    cp .env.example .env
    print_status ".env created from template"
    print_info "Please edit .env and add your TELEGRAM_BOT_TOKEN"
    exit 1
fi

# Check token is set
TELEGRAM_TOKEN=$(grep "TELEGRAM_BOT_TOKEN=" .env | cut -d '=' -f2 | tr -d ' "'\''')
if [ -z "$TELEGRAM_TOKEN" ]; then
    print_error "TELEGRAM_BOT_TOKEN not configured in .env"
    print_info "Edit .env and add: TELEGRAM_BOT_TOKEN=your_token_here"
    exit 1
fi

if [ "$TELEGRAM_TOKEN" = "your_bot_token_here" ] || [ "$TELEGRAM_TOKEN" = "xxxxxxxxxxxxxxxxxxxxxxxx" ]; then
    print_error "TELEGRAM_BOT_TOKEN is placeholder - configure real token"
    exit 1
fi

print_status ".env file configured"

# Check Python
echo ""
print_info "Checking Python environment..."
if ! command -v python3 &> /dev/null; then
    print_error "Python3 not found"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
print_status "Python $PYTHON_VERSION found"

# Check dependencies
echo ""
print_info "Checking dependencies..."

# Check if python-telegram-bot is installed
if ! python3 -c "import telegram" 2>/dev/null; then
    print_error "python-telegram-bot not installed"
    echo "Installing..."
    pip install 'python-telegram-bot>=20.0'
    print_status "Dependencies installed"
else
    print_status "Dependencies already installed"
fi

# Verify module imports
echo ""
print_info "Verifying module imports..."
python3 << 'PYTHONEOF'
import sys
sys.path.insert(0, '/storage/emulated/0/projects/aios')

try:
    from services.llm import LLMClient, ProviderManager
    print("✓ LLM layer", flush=True)
    
    from agents.hermes import get_registry
    print("✓ Agent framework", flush=True)
    
    from telegram.bot import HermesBot
    print("✓ Telegram bot", flush=True)
    
    print("✓ All modules ready")
except Exception as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
PYTHONEOF

# Show bot information
echo ""
print_info "Bot Information:"
echo "  Token: ${TELEGRAM_TOKEN:0:20}..."
echo "  Project: $PROJECT_DIR"
echo "  Python: $PYTHON_VERSION"

# Offer options
echo ""
echo -e "${YELLOW}Select mode:${NC}"
echo "  1) Run bot (foreground)"
echo "  2) Run bot (background)"
echo "  3) Run tests"
echo "  4) View logs"
echo "  5) Stop running bot"
echo "  6) Exit"
echo ""
read -p "Enter choice (1-6): " choice

case $choice in
    1)
        print_info "Starting Telegram bot (foreground)..."
        python3 -m telegram.bot
        ;;
    2)
        print_info "Starting Telegram bot (background)..."
        nohup python3 -m telegram.bot > telegram.log 2>&1 &
        BOT_PID=$!
        print_status "Bot started with PID $BOT_PID"
        print_info "View logs: tail -f telegram.log"
        print_info "Stop bot: kill $BOT_PID"
        ;;
    3)
        print_info "Running tests..."
        python3 << 'TESTEOF'
import sys
sys.path.insert(0, '/storage/emulated/0/projects/aios')

from services.llm import ProviderManager
from agents.hermes import get_registry, AgentConfig
from agents.hermes.concrete_agents import ResearchAgent
from telegram.bot import HermesBot
import os
from dotenv import load_dotenv

load_dotenv()

print("\n=== AIOS TEST SUITE ===\n")

# Test 1: Providers
print("[1/3] Testing LLM Providers...")
try:
    manager = ProviderManager()
    enabled = [p for p, c in manager.providers.items() if c.get('enabled')]
    print(f"  ✓ {len(enabled)} providers enabled")
except Exception as e:
    print(f"  ✗ {e}")

# Test 2: Agents
print("[2/3] Testing Agent Framework...")
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
    print(f"  ✓ {len(agents)} agent(s) registered")
except Exception as e:
    print(f"  ✗ {e}")

# Test 3: Bot
print("[3/3] Testing Telegram Bot...")
try:
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if token and not token.startswith('x'):
        bot = HermesBot(token)
        print(f"  ✓ Bot initialized with {len(bot.registry.list_agents())} agents")
    else:
        print("  ○ Bot token not configured")
except Exception as e:
    print(f"  ✗ {e}")

print("\n✅ Tests complete\n")
TESTEOF
        ;;
    4)
        if [ -f telegram.log ]; then
            print_info "Showing logs (last 50 lines):"
            tail -50 telegram.log
        else
            print_error "telegram.log not found"
            print_info "Bot not running in background, or logs cleared"
        fi
        ;;
    5)
        print_info "Stopping bot..."
        pkill -f "python.*telegram.bot" || print_error "No bot process found"
        print_status "Bot stopped (if running)"
        ;;
    6)
        print_info "Exiting"
        exit 0
        ;;
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

