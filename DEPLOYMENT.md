# AIOS Deployment Guide

**AI Operating System** - Hermes Agent Orchestration Platform

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Termux/Android Deployment](#termuxandroid-deployment)
4. [Linux VPS Deployment](#linux-vps-deployment)
5. [Docker Deployment](#docker-deployment)
6. [Telegram Bot Setup](#telegram-bot-setup)
7. [Configuration](#configuration)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **CPU**: ARM64 (aarch64) or x86_64
- **RAM**: 512MB minimum (1GB recommended)
- **Storage**: 500MB for base system + dependencies
- **Python**: 3.9+ (3.11+ recommended)

### API Keys (Optional)

Get these free API keys to enable providers:

1. **Groq** (Recommended)
   - Fast free inference
   - Get at: https://console.groq.com
   - Models: Llama 3.3, Mixtral 8x7B

2. **Google Gemini**
   - Free quota with strong reasoning
   - Get at: https://makersuite.google.com/app/apikey
   - Models: Gemini Pro, Pro Vision

3. **OpenRouter**
   - Huge model catalog
   - Get at: https://openrouter.ai/keys
   - Models: Mistral, Llama, GPT-3.5

### Optional Services

- **Local LLM**: Ollama, LM Studio, vLLM (for offline inference)
- **Telegram**: Telegram Bot Token (for chat interface)
- **Database**: SQLite (bundled) or PostgreSQL (optional)

---

## Local Development

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/aios.git
cd aios
```

### 2. Setup Python Environment

```bash
# Option A: Python venv
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Option B: conda
conda create -n aios python=3.11
conda activate aios

# Option C: UV (recommended for Termux)
uv venv aios-env
source aios-env/bin/activate
```

### 3. Install Dependencies

```bash
# Core dependencies
pip install httpx requests rich typer python-dotenv

# WebUI dependencies
pip install fastapi uvicorn jinja2

# Telegram (optional)
pip install 'python-telegram-bot>=20.0'

# Or install all at once
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env with your API keys
nano .env  # or: vim .env, or open in editor

# Required minimum:
GROQ_API_KEY=gsk_xxxxxx
GOOGLE_API_KEY=AIzaSyDxxxxxx
OPENROUTER_API_KEY=sk-or-xxxxxx
```

### 5. Run WebUI

```bash
# Start FastAPI server
python -m uvicorn webui.app:app --reload --host 0.0.0.0 --port 8000

# Open browser: http://localhost:8000
```

### 6. Run Telegram Bot (Optional)

```bash
# Set bot token
export TELEGRAM_BOT_TOKEN="your_bot_token_here"

# Start bot
python -m telegram.bot
```

---

## Termux/Android Deployment

### Prerequisites

- Termux app installed
- Storage access enabled
- Python 3.11+ (`pkg install python`)

### Installation Steps

#### 1. Setup Termux

```bash
# Update packages
pkg update && pkg upgrade

# Install Python
pkg install python -y

# Install build essentials (if needed)
pkg install build-essential -y

# Install git
pkg install git -y
```

#### 2. Clone AIOS

```bash
# Navigate to storage
cd /storage/emulated/0

# Clone repository
git clone https://github.com/yourusername/aios.git
cd aios
```

#### 3. Install Python Packages

```bash
# Install system-wide (recommended for Termux shared storage)
pip install --system httpx requests rich typer python-dotenv

# WebUI
pip install --system fastapi uvicorn jinja2

# Telegram (optional)
pip install --system 'python-telegram-bot>=20.0'
```

#### 4. Configure .env

```bash
cp .env.example .env

# Edit with vim or nano
nano .env

# Add your API keys:
# GROQ_API_KEY=gsk_xxxxxx
# GOOGLE_API_KEY=AIzaSyDxxxxxx
# etc...
```

#### 5. Start WebUI

```bash
# Direct invocation
python webui/app.py

# Or with Termux specific options
python -m uvicorn webui.app:app --host 0.0.0.0 --port 8000
```

#### 6. Keep Running

**Option A: Termux App Sessions**

```bash
# Create new session for persistence
# Long-press on Termux window → New Session

# In new session, start bot:
python -m telegram.bot
```

**Option B: Screen/tmux**

```bash
# Install tmux
pkg install tmux

# Create session
tmux new-session -d -s aios

# Run in session
tmux send-keys -t aios "cd ~/storage/shared/projects/aios && python webui/app.py" Enter

# View
tmux attach -t aios

# Detach: Ctrl+B then D
```

**Option C: Cron (Requires Termux:Boot)**

```bash
# Install Termux:Boot from F-Droid
# Create script: ~/.termux/boot/aios.sh

#!/data/data/com.termux/files/usr/bin/sh
cd /storage/emulated/0/aios
python webui/app.py >> /storage/emulated/0/aios.log 2>&1
```

---

## Linux VPS Deployment

### Prerequisites

- Ubuntu 20.04+ or equivalent
- SSH access
- ~1GB RAM minimum

### Installation

#### 1. Connect to VPS

```bash
ssh root@your_vps_ip
```

#### 2. System Setup

```bash
# Update system
apt update && apt upgrade -y

# Install Python
apt install python3.11 python3.11-venv python3-pip git -y

# Create app user
useradd -m -s /bin/bash aios
su - aios
```

#### 3. Clone Repository

```bash
git clone https://github.com/yourusername/aios.git
cd aios

# Create venv
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install httpx requests rich typer python-dotenv
pip install fastapi uvicorn jinja2
pip install 'python-telegram-bot>=20.0'
```

#### 4. Configure

```bash
cp .env.example .env
nano .env  # Add your API keys
```

#### 5. Systemd Service

```bash
# Exit to root
exit

# Create service file
sudo nano /etc/systemd/system/aios-webui.service
```

Add:

```ini
[Unit]
Description=AIOS WebUI
After=network.target

[Service]
Type=simple
User=aios
WorkingDirectory=/home/aios/aios
ExecStart=/home/aios/aios/venv/bin/python -m uvicorn webui.app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable aios-webui
sudo systemctl start aios-webui

# Check status
sudo systemctl status aios-webui

# View logs
sudo journalctl -u aios-webui -f
```

#### 6. Nginx Reverse Proxy (Recommended)

```bash
sudo apt install nginx -y

# Create config
sudo nano /etc/nginx/sites-available/aios
```

Add:

```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
```

Enable:

```bash
sudo ln -s /etc/nginx/sites-available/aios /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy application
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir \
    httpx requests rich typer python-dotenv \
    fastapi uvicorn jinja2 \
    'python-telegram-bot>=20.0'

# Expose ports
EXPOSE 8000

# Environment
ENV WEBUI_HOST=0.0.0.0
ENV WEBUI_PORT=8000

# Run
CMD ["python", "-m", "uvicorn", "webui.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  aios-webui:
    build: .
    container_name: aios
    ports:
      - "8000:8000"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - DEBUG=false
    volumes:
      - ./.env:/app/.env
      - ./configs:/app/configs
    restart: always

  aios-telegram:
    build: .
    container_name: aios-telegram
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    volumes:
      - ./.env:/app/.env
    entrypoint: ["python", "-m", "telegram.bot"]
    restart: always
    depends_on:
      - aios-webui
```

### Deploy

```bash
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Telegram Bot Setup

### 1. Get Bot Token

1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Follow instructions
5. Copy the token

### 2. Configure

```bash
# Edit .env
nano .env

# Add:
TELEGRAM_BOT_TOKEN=your_token_here
```

### 3. Start Bot

```bash
python -m telegram.bot
```

### 4. Test Commands

In Telegram chat with your bot:

```
/start
/research
/code
/status
/memory
/help
```

---

## Configuration

### Environment Variables

See `.env.example` for all options.

Key variables:

```bash
# Providers
GROQ_API_KEY=gsk_xxxxxx
GOOGLE_API_KEY=AIzaSyDxxxxxx
OPENROUTER_API_KEY=sk-or-xxxxxx

# WebUI
WEBUI_HOST=0.0.0.0
WEBUI_PORT=8000
DEBUG=false

# Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklmnopQRSTUvwxyz
```

### Provider Selection

Edit `configs/providers.json`:

```json
{
  "providers": {
    "groq": {
      "enabled": true,  // Enable/disable
      "api_key": "${GROQ_API_KEY}"
    }
  },
  "fallback_order": ["groq", "gemini", "openrouter"]
}
```

---

## Troubleshooting

### Common Issues

#### 1. Python Version

```bash
# Check version
python3 --version  # Should be 3.9+

# Install if missing (Ubuntu)
sudo apt install python3.11 -y
```

#### 2. Import Errors

```bash
# Ensure PYTHONPATH includes project root
export PYTHONPATH=/path/to/aios:$PYTHONPATH
```

#### 3. API Key Issues

```bash
# Verify keys in .env
cat .env | grep API_KEY

# Test connection
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('GROQ_API_KEY'))"
```

#### 4. Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
python webui/app.py --port 8001
```

#### 5. Termux Storage Permission

```bash
# Grant permission via Android settings
# Settings → Apps → Termux → Permissions → Files
```

---

## Monitoring

### Health Check

```bash
# Check WebUI
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","agents":2,"timestamp":"..."}
```

### Logs

```bash
# WebUI logs
tail -f /path/to/aios.log

# Systemd logs
sudo journalctl -u aios-webui -f

# Docker logs
docker logs -f aios
```

---

## Production Best Practices

1. **Use HTTPS**
   - Deploy behind nginx with SSL
   - Use Let's Encrypt for free certificates

2. **Environment Secrets**
   - Never commit .env file
   - Use secrets manager (Vault, GitHub Secrets, etc.)

3. **Monitoring**
   - Setup uptime monitoring
   - Log aggregation (ELK, Loki, etc.)

4. **Backups**
   - Backup configs/ regularly
   - Version control all changes

5. **Rate Limiting**
   - Configure in configs/providers.json
   - Monitor API usage

6. **Updates**
   - Run `git pull` to get latest
   - Test in dev before production

---

## Support

- **Issues**: https://github.com/yourusername/aios/issues
- **Discussions**: https://github.com/yourusername/aios/discussions
- **Documentation**: ./README.md

---

**Last Updated**: June 2026

