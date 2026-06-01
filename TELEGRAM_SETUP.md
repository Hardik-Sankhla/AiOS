# Telegram Bot Setup & Configuration Guide

**Hermes AIOS Telegram Integration**

---

## Quick Setup (5 Minutes)

### Step 1: Create Bot with BotFather

1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Follow prompts:
   - Enter bot name: `Hermes AIOS Bot`
   - Enter username: `hermes_aios_bot` (must be unique)
5. **Copy the token** provided

### Step 2: Configure Environment

```bash
# Edit .env file
nano /storage/emulated/0/projects/aios/.env

# Add this line:
TELEGRAM_BOT_TOKEN=your_token_here
```

**Example**:
```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklmnopQRSTUvwxyz_abcdef1234
```

### Step 3: Install Dependencies (if not already installed)

```bash
pip install 'python-telegram-bot>=20.0'
```

### Step 4: Start Bot

```bash
cd /storage/emulated/0/projects/aios
python -m telegram.bot
```

### Step 5: Test in Telegram

1. Search for your bot by username in Telegram
2. Send: `/start`
3. Expected response: Welcome message with available commands

---

## Bot Commands Reference

### Available Commands

```
/start       - Initialize bot session
/research    - Switch to Research Agent 🔍
/code        - Switch to Coding Agent 💻
/status      - Check system status 📊
/memory      - View agent memories 🧠
/help        - Show all commands ❓
```

### Usage Examples

**Switch to Research Agent**:
```
User: /research
Bot: 🔍 Research Agent Selected
     I'm now in Research mode. Ask me to research topics, analyze data, or provide insights.
```

**Ask a Question**:
```
User: What are the latest AI trends?
Bot: [Agent response based on selected agent]
```

**Check Status**:
```
User: /status
Bot: 📊 System Status
     Agents: 2
     Active Sessions: N
     Bot Status: 🟢 Running
```

**View Memory**:
```
User: /memory
Bot: 🧠 ResearchAgent Memory:
     • topic_1: AI trends analysis
     • topic_2: Machine learning applications
     ... (last 10 entries)
```

---

## Configuration Details

### Environment Variables

```bash
# Required
TELEGRAM_BOT_TOKEN=your_bot_token

# Optional (WebUI integration)
TELEGRAM_WEBHOOK_URL=https://your-domain.com/telegram
TELEGRAM_CHAT_ID=your_chat_id_for_notifications

# Optional (for production)
TELEGRAM_DEBUG=false
LOG_LEVEL=INFO
```

### .env.example Template

See [.env.example](.env.example) for full template with all variables.

---

## Running the Bot

### Local Development

```bash
# Start bot with logging
TELEGRAM_DEBUG=true python -m telegram.bot
```

### Background Process (Linux/Mac)

```bash
# Using nohup
nohup python -m telegram.bot > telegram.log 2>&1 &

# View logs
tail -f telegram.log

# Stop bot
pkill -f "python -m telegram.bot"
```

### Termux (Persistent)

**Option 1: Termux Session**
```bash
# Create new session in Termux
# Long-press → New Session

# In new session:
cd /storage/emulated/0/projects/aios
python -m telegram.bot
```

**Option 2: Background Service**
```bash
# Install tmux
pkg install tmux

# Create session
tmux new-session -d -s telegram

# Run bot in session
tmux send-keys -t telegram "cd /storage/emulated/0/projects/aios && python -m telegram.bot" Enter

# View output
tmux attach -t telegram

# Detach: Ctrl+B then D
```

### Docker

```bash
docker run -e TELEGRAM_BOT_TOKEN="your_token" aios python -m telegram.bot
```

---

## Features & Capabilities

### Agent Switching

Users can switch between agents mid-conversation:

```
/research  → Research mode
/code      → Coding mode
```

### Session Management

Each user has independent session:
- Selected agent persists across messages
- Message count tracked
- Memory per agent

### Message Handling

```
User message → Bot routes to selected agent → Agent processes → Response sent
```

### Memory System

- **Per-agent memory**: Each agent maintains separate memory
- **Persistent storage**: Memory survives across sessions
- **View command**: `/memory` shows last 10 items

---

## Troubleshooting

### Bot Not Responding

**Check 1: Token valid**
```bash
curl -X POST https://api.telegram.org/botTOKEN/getMe
```

Should return bot info.

**Check 2: Environment loaded**
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('TELEGRAM_BOT_TOKEN'))"
```

Should show token (not None).

**Check 3: Dependencies installed**
```bash
pip show python-telegram-bot
```

Should show version 20.0+.

### Common Errors

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: python_telegram_bot` | Run: `pip install 'python-telegram-bot>=20.0'` |
| `Invalid token` | Verify token in .env matches BotFather token |
| `Connection timeout` | Check internet connection, firewall rules |
| `Bot not responding` | Restart bot: `Ctrl+C` then start again |

### Debug Mode

Enable detailed logging:

```bash
# Run with debug
TELEGRAM_DEBUG=true python -m telegram.bot

# Or set in .env
TELEGRAM_DEBUG=true
```

---

## Advanced Setup

### Webhook (Production)

For production, use webhook instead of polling:

```bash
# In bot configuration
TELEGRAM_WEBHOOK_URL=https://your-domain.com/telegram
TELEGRAM_WEBHOOK_PORT=8443
```

Requires:
- Valid domain
- SSL certificate
- Public IP

### Multi-Bot Setup

Run multiple bots with different tokens:

```bash
# Terminal 1
TELEGRAM_BOT_TOKEN=token1 python -m telegram.bot

# Terminal 2
TELEGRAM_BOT_TOKEN=token2 python -m telegram.bot
```

### Integration with WebUI

Connect Telegram bot to WebUI:

```python
# In telegram/bot.py
from webui.app import get_agent_registry

# Route messages through shared registry
registry = get_agent_registry()
```

---

## Testing

### Manual Testing

1. **Test /start**
   ```
   /start
   ```
   Expected: Welcome message and session init

2. **Test agent switching**
   ```
   /research
   /code
   ```
   Expected: Agent switch confirmation

3. **Test regular message**
   ```
   Hello bot!
   ```
   Expected: Response from selected agent

4. **Test /memory**
   ```
   /memory
   ```
   Expected: Agent memory items (if any)

### Automated Testing

```bash
# Test bot module imports
python -c "from telegram.bot import HermesBot; print('✓ Bot module valid')"

# Test with mock token
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
token = os.getenv('TELEGRAM_BOT_TOKEN')
print(f'Token loaded: {bool(token)}')
"
```

---

## Production Checklist

- [ ] Token configured in .env
- [ ] Dependencies installed (`pip install 'python-telegram-bot>=20.0'`)
- [ ] Bot created with BotFather
- [ ] Bot tested locally
- [ ] Logging configured
- [ ] Error handling verified
- [ ] Memory system working
- [ ] Agent switching working
- [ ] Session management working
- [ ] Deployed and running

---

## Monitoring

### Check Bot Status

```bash
# Send health check
curl -X POST https://api.telegram.org/botTOKEN/getMe
```

### View Logs

```bash
# If running in background
tail -f telegram.log

# Or check system logs
journalctl -u telegram-bot -f
```

### User Session Monitoring

Track active sessions:

```python
from telegram.bot import HermesBot
bot = HermesBot(token)
print(f"Active sessions: {len(bot.user_sessions)}")
```

---

## Next Steps

1. **✅ Create bot** with BotFather
2. **✅ Configure .env** with token
3. **✅ Install dependencies** with pip
4. **✅ Start bot** with `python -m telegram.bot`
5. **✅ Test commands** in Telegram
6. **✅ Deploy** to production
7. **✅ Monitor** bot health

---

## Support

- **Issues**: Check [Troubleshooting](#troubleshooting) section
- **Documentation**: See [telegram/bot.py](telegram/bot.py)
- **API Docs**: https://python-telegram-bot.org
- **Questions**: Open GitHub issue

---

## Security Notes

1. **Never commit .env** - Keep token private
2. **Rotate tokens** - Regenerate if compromised
3. **Rate limiting** - Configure for production
4. **User validation** - Add auth if needed
5. **Logging** - Don't log sensitive data

---

**Last Updated**: June 1, 2026  
**Version**: 1.0  
**Status**: Production Ready

