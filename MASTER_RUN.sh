#!/bin/bash

################################################################################
#                    AIOS MASTER STARTUP SCRIPT                               #
#         Run entire system autonomously: WebUI + Bot + Tests + Logs          #
#                   Single Script, Multiple Services, One Output              #
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Directories
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
PID_FILE="$PROJECT_DIR/.aios_pids"

# Create logs directory
mkdir -p "$LOG_DIR"

# Timestamps
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

# Log files
WEBUI_LOG="$LOG_DIR/webui_$TIMESTAMP.log"
BOT_LOG="$LOG_DIR/bot_$TIMESTAMP.log"
TEST_LOG="$LOG_DIR/tests_$TIMESTAMP.log"
MASTER_LOG="$LOG_DIR/master_$TIMESTAMP.log"

################################################################################
# Helper Functions
################################################################################

log() {
    local level=$1
    shift
    local msg="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${msg}" | tee -a "$MASTER_LOG"
}

log_info() {
    log "${BLUE}INFO${NC}" "$@"
}

log_success() {
    log "${GREEN}✓${NC}" "$@"
}

log_error() {
    log "${RED}✗${NC}" "$@"
}

log_warn() {
    log "${YELLOW}⚠${NC}" "$@"
}

separator() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$MASTER_LOG"
}

header() {
    separator
    echo -e "${BLUE}$@${NC}" | tee -a "$MASTER_LOG"
    separator
}

################################################################################
# Cleanup Functions
################################################################################

cleanup_pids() {
    if [ -f "$PID_FILE" ]; then
        while IFS= read -r pid; do
            if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
                kill -TERM "$pid" 2>/dev/null || true
                sleep 1
                kill -9 "$pid" 2>/dev/null || true
                log_info "Killed process $pid"
            fi
        done < "$PID_FILE"
        rm -f "$PID_FILE"
    fi
}

cleanup() {
    log_info "Shutting down services..."
    cleanup_pids
    log_success "Cleanup complete"
}

trap cleanup EXIT INT TERM

################################################################################
# System Checks
################################################################################

check_requirements() {
    header "Checking System Requirements"
    
    # Check Python
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        log_error "Python not found"
        exit 1
    fi
    log_success "Python found"
    
    # Check .env
    if [ ! -f "$PROJECT_DIR/.env" ]; then
        log_error ".env file not found. Copy from .env.example"
        exit 1
    fi
    log_success ".env configured"
    
    # Check requirements
    if [ ! -f "$PROJECT_DIR/requirements.txt" ]; then
        log_error "requirements.txt not found"
        exit 1
    fi
    log_success "requirements.txt found"
    
    # Check directories
    for dir in webui agents services bot_service configs; do
        if [ ! -d "$PROJECT_DIR/$dir" ]; then
            log_error "Directory $dir not found"
            exit 1
        fi
    done
    log_success "All required directories present"
}

################################################################################
# Service Startup Functions
################################################################################

start_webui() {
    header "Starting WebUI (FastAPI)"
    
    log_info "Launching WebUI on port 8000..."
    
    cd "$PROJECT_DIR"
    nohup python -m uvicorn webui.app:app \
        --host 0.0.0.0 \
        --port 8000 \
        --log-level info \
        > "$WEBUI_LOG" 2>&1 &
    
    local webui_pid=$!
    echo "$webui_pid" >> "$PID_FILE"
    
    # Wait for WebUI to start
    sleep 3
    
    if kill -0 "$webui_pid" 2>/dev/null; then
        log_success "WebUI started (PID: $webui_pid)"
        log_info "Access: http://localhost:8000"
        log_info "API Docs: http://localhost:8000/docs"
        log_info "Health: http://localhost:8000/health"
        return 0
    else
        log_error "WebUI failed to start"
        tail -20 "$WEBUI_LOG" | tee -a "$MASTER_LOG"
        return 1
    fi
}

start_bot() {
    header "Starting Telegram Bot"
    
    log_info "Launching Telegram Bot..."
    
    cd "$PROJECT_DIR"
    nohup python -m bot_service \
        > "$BOT_LOG" 2>&1 &
    
    local bot_pid=$!
    echo "$bot_pid" >> "$PID_FILE"
    
    # Wait for bot to initialize
    sleep 3
    
    if kill -0 "$bot_pid" 2>/dev/null; then
        log_success "Telegram Bot started (PID: $bot_pid)"
        log_info "Status: Polling for messages"
        log_info "Test command: /start"
        return 0
    else
        log_error "Bot failed to start"
        tail -20 "$BOT_LOG" | tee -a "$MASTER_LOG"
        return 1
    fi
}

run_tests() {
    header "Running Test Suite"
    
    log_info "Executing unit tests..."
    
    cd "$PROJECT_DIR"
    if python -m pytest tests/ -v --tb=short > "$TEST_LOG" 2>&1; then
        log_success "All tests passed"
        grep -E "passed|failed|error" "$TEST_LOG" | tail -5 | tee -a "$MASTER_LOG"
        return 0
    else
        log_warn "Some tests failed"
        tail -20 "$TEST_LOG" | tee -a "$MASTER_LOG"
        return 1
    fi
}

################################################################################
# Status Functions
################################################################################

show_status() {
    header "System Status"
    
    log_info "Active Services:"
    
    if [ -f "$PID_FILE" ]; then
        local count=0
        while IFS= read -r pid; do
            if kill -0 "$pid" 2>/dev/null; then
                local process_name=$(ps -p "$pid" -o comm= 2>/dev/null || echo "unknown")
                log_success "  - $process_name (PID: $pid)"
                ((count++))
            fi
        done < "$PID_FILE"
        log_info "Total: $count service(s) running"
    else
        log_warn "No services running"
    fi
    
    log_info ""
    log_info "Log Files:"
    ls -lh "$LOG_DIR"/ 2>/dev/null | tail -10 | tee -a "$MASTER_LOG"
}

view_logs_realtime() {
    header "Real-time Logs"
    
    log_info "Displaying latest logs (Ctrl+C to exit)..."
    log_info ""
    
    tail -f \
        <(tail -f "$WEBUI_LOG" 2>/dev/null | sed "s/^/[WEBUI] /") \
        <(tail -f "$BOT_LOG" 2>/dev/null | sed "s/^/[BOT] /") \
        <(tail -f "$TEST_LOG" 2>/dev/null | sed "s/^/[TEST] /") \
        2>/dev/null || log_warn "No active logs to display"
}

view_latest_logs() {
    header "Latest Log Output"
    
    if [ -f "$WEBUI_LOG" ]; then
        echo -e "${BLUE}=== WebUI Log (Latest 20 lines) ===${NC}" | tee -a "$MASTER_LOG"
        tail -20 "$WEBUI_LOG" | tee -a "$MASTER_LOG"
        echo ""
    fi
    
    if [ -f "$BOT_LOG" ]; then
        echo -e "${BLUE}=== Bot Log (Latest 20 lines) ===${NC}" | tee -a "$MASTER_LOG"
        tail -20 "$BOT_LOG" | tee -a "$MASTER_LOG"
        echo ""
    fi
    
    if [ -f "$TEST_LOG" ]; then
        echo -e "${BLUE}=== Test Log (Latest 20 lines) ===${NC}" | tee -a "$MASTER_LOG"
        tail -20 "$TEST_LOG" | tee -a "$MASTER_LOG"
        echo ""
    fi
}

health_check() {
    header "Health Check"
    
    log_info "Checking services..."
    
    # WebUI health
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        log_success "WebUI is healthy"
    else
        log_warn "WebUI is not responding"
    fi
    
    # Check processes
    if [ -f "$PID_FILE" ]; then
        while IFS= read -r pid; do
            if kill -0 "$pid" 2>/dev/null; then
                local pname=$(ps -p "$pid" -o comm= 2>/dev/null || echo "unknown")
                log_success "$pname is running (PID: $pid)"
            else
                log_error "Process $pid is not running"
            fi
        done < "$PID_FILE"
    fi
    
    log_info ""
    log_info "Port Check:"
    log_info "  Port 8000 (WebUI): $(lsof -i :8000 2>/dev/null | wc -l) process(es)"
}

################################################################################
# Main Menu
################################################################################

show_menu() {
    echo ""
    separator
    echo -e "${CYAN}AIOS Master Startup - System Control${NC}" | tee -a "$MASTER_LOG"
    separator
    echo ""
    echo "  QUICK START:"
    echo "    1) Start All (WebUI + Bot + Tests)"
    echo "    2) Start All (WebUI + Bot, no tests)"
    echo ""
    echo "  INDIVIDUAL SERVICES:"
    echo "    3) Start WebUI Only"
    echo "    4) Start Bot Only"
    echo "    5) Run Tests Only"
    echo ""
    echo "  UTILITIES:"
    echo "    6) Show Status"
    echo "    7) Health Check"
    echo "    8) View Latest Logs"
    echo "    9) View Real-time Logs"
    echo "    10) Stop All Services"
    echo ""
    echo "  ADVANCED:"
    echo "    11) Restart All"
    echo "    12) Full System Reset"
    echo ""
    echo "    0) Exit"
    echo ""
}

################################################################################
# Main Execution
################################################################################

main() {
    clear
    
    # Show header
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║           AIOS MASTER STARTUP SYSTEM v1.0                 ║"
    echo "║      Autonomous Multi-Service Orchestration Platform      ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    log_info "Master startup script initialized"
    log_info "Project directory: $PROJECT_DIR"
    log_info "Log directory: $LOG_DIR"
    
    # Check requirements first
    check_requirements
    
    # Interactive menu
    while true; do
        show_menu
        read -p "Select option (0-12): " choice
        
        case $choice in
            1)
                header "Starting Complete System (All Services + Tests)"
                start_webui && start_bot && run_tests && show_status
                ;;
            2)
                header "Starting Core Services (WebUI + Bot)"
                start_webui && start_bot && show_status
                ;;
            3)
                start_webui && show_status
                ;;
            4)
                start_bot && show_status
                ;;
            5)
                run_tests && show_status
                ;;
            6)
                show_status
                ;;
            7)
                health_check
                ;;
            8)
                view_latest_logs
                ;;
            9)
                view_logs_realtime
                ;;
            10)
                log_info "Stopping all services..."
                cleanup
                log_success "All services stopped"
                ;;
            11)
                log_info "Restarting all services..."
                cleanup
                sleep 2
                start_webui && start_bot && show_status
                ;;
            12)
                log_warn "Performing full system reset..."
                cleanup
                rm -rf "$LOG_DIR"/*
                rm -f "$PID_FILE"
                mkdir -p "$LOG_DIR"
                log_success "System reset complete"
                ;;
            0)
                log_info "Exiting..."
                cleanup
                exit 0
                ;;
            *)
                log_error "Invalid option: $choice"
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Argument handling
if [ $# -eq 0 ]; then
    main
else
    case "$1" in
        --start-all)
            check_requirements
            start_webui && start_bot && run_tests && show_status
            ;;
        --start-services)
            check_requirements
            start_webui && start_bot && show_status
            ;;
        --start-webui)
            check_requirements
            start_webui
            ;;
        --start-bot)
            check_requirements
            start_bot
            ;;
        --test)
            check_requirements
            run_tests
            ;;
        --status)
            show_status
            ;;
        --health)
            health_check
            ;;
        --logs)
            view_latest_logs
            ;;
        --stop)
            cleanup
            ;;
        --help)
            echo "Usage: $0 [OPTION]"
            echo ""
            echo "Options:"
            echo "  --start-all         Start all services and run tests"
            echo "  --start-services    Start WebUI and Bot"
            echo "  --start-webui       Start WebUI only"
            echo "  --start-bot         Start Bot only"
            echo "  --test              Run tests only"
            echo "  --status            Show service status"
            echo "  --health            Run health check"
            echo "  --logs              View latest logs"
            echo "  --stop              Stop all services"
            echo "  --help              Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                       # Interactive menu"
            echo "  $0 --start-all          # Start everything"
            echo "  $0 --start-services     # Start services only"
            echo "  $0 --stop               # Stop all services"
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
fi

