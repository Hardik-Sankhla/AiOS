"""Telegram Bot Handler for Hermes AIOS"""

import os
import asyncio
import logging
from typing import Optional
from pathlib import Path

# Note: This is a template. Requires: pip install python-telegram-bot
# from telegram import Update, BotCommand, MenuButton
# from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.hermes import get_registry, AgentConfig
from agents.hermes.concrete_agents import ResearchAgent, CodingAgent


# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class HermesBot:
    """Telegram bot for Hermes AIOS"""
    
    def __init__(self, token: str):
        """Initialize bot with token."""
        self.token = token
        self.registry = get_registry()
        self.user_sessions = {}
        
        # Initialize agents
        self._init_agents()
    
    def _init_agents(self):
        """Initialize Hermes agents."""
        self.registry.clear()
        
        # Research Agent
        research_config = AgentConfig(
            name="ResearchAgent",
            description="Research specialist",
            capabilities=["research", "analysis"]
        )
        research_agent = ResearchAgent(research_config, llm_client=None)
        self.registry.register_agent("research", research_agent)
        
        # Coding Agent
        coding_config = AgentConfig(
            name="CodingAgent",
            description="Coding specialist",
            capabilities=["coding", "architecture"]
        )
        coding_agent = CodingAgent(coding_config, llm_client=None)
        self.registry.register_agent("coding", coding_agent)
        
        logger.info("Agents initialized")
    
    async def start_handler(self, update, context):
        """Handle /start command."""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        
        self.user_sessions[user_id] = {
            "current_agent": "research",
            "message_count": 0,
        }
        
        welcome_msg = f"""
Welcome to **Hermes AIOS** 🤖

Hello {user_name}! I'm an AI-powered agent orchestration system.

Available commands:
/research - Switch to Research Agent
/code - Switch to Coding Agent
/status - Show system status
/help - Show all commands
/memory - View agent memory

Just send me a message to chat with the current agent!
        """
        
        await update.message.reply_text(welcome_msg, parse_mode="Markdown")
        logger.info(f"User {user_id} ({user_name}) started bot")
    
    async def research_handler(self, update, context):
        """Handle /research command."""
        user_id = update.effective_user.id
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {"current_agent": "research", "message_count": 0}
        
        self.user_sessions[user_id]["current_agent"] = "research"
        
        await update.message.reply_text(
            "🔍 *Research Agent Selected*\n\n"
            "I'm now in Research mode. Ask me to research topics, analyze data, or provide insights.",
            parse_mode="Markdown"
        )
    
    async def code_handler(self, update, context):
        """Handle /code command."""
        user_id = update.effective_user.id
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {"current_agent": "coding", "message_count": 0}
        
        self.user_sessions[user_id]["current_agent"] = "coding"
        
        await update.message.reply_text(
            "💻 *Coding Agent Selected*\n\n"
            "I'm now in Coding mode. Ask me to write code, review algorithms, or discuss architecture.",
            parse_mode="Markdown"
        )
    
    async def status_handler(self, update, context):
        """Handle /status command."""
        agent_count = len(self.registry.list_agents())
        session_count = len(self.user_sessions)
        
        status_msg = f"""
📊 *System Status*

Agents: {agent_count}
Active Sessions: {session_count}
Bot Status: 🟢 Running

Your Session:
- Current Agent: {self.user_sessions.get(update.effective_user.id, {}).get('current_agent', 'unknown')}
- Messages: {self.user_sessions.get(update.effective_user.id, {}).get('message_count', 0)}
        """
        
        await update.message.reply_text(status_msg, parse_mode="Markdown")
    
    async def memory_handler(self, update, context):
        """Handle /memory command."""
        user_id = update.effective_user.id
        agent_id = self.user_sessions.get(user_id, {}).get("current_agent", "research")
        agent = self.registry.get_agent(agent_id)
        
        if not agent:
            await update.message.reply_text("Agent not found.")
            return
        
        memory_items = agent.memory
        if not memory_items:
            await update.message.reply_text(f"*{agent.name}* has no memories yet.", parse_mode="Markdown")
            return
        
        memory_msg = f"*{agent.name} Memory:*\n\n"
        for key, value in list(memory_items.items())[:10]:  # Show last 10
            memory_msg += f"• {key}: {str(value)[:50]}...\n" if len(str(value)) > 50 else f"• {key}: {value}\n"
        
        await update.message.reply_text(memory_msg, parse_mode="Markdown")
    
    async def help_handler(self, update, context):
        """Handle /help command."""
        help_msg = """
*Available Commands:*

/start - Start the bot
/research - Switch to Research Agent 🔍
/code - Switch to Coding Agent 💻
/status - Show system status 📊
/memory - View agent memory 🧠
/help - Show this help message

*How to Use:*
1. Select an agent with /research or /code
2. Send any message to chat with the agent
3. Use /status to check system health
4. View agent memory with /memory

*Support:*
For issues, visit: https://github.com/yourname/aios
        """
        
        await update.message.reply_text(help_msg, parse_mode="Markdown")
    
    async def message_handler(self, update, context):
        """Handle regular text messages."""
        user_id = update.effective_user.id
        user_message = update.message.text
        
        # Initialize session if needed
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                "current_agent": "research",
                "message_count": 0,
            }
        
        # Get current agent
        agent_id = self.user_sessions[user_id]["current_agent"]
        agent = self.registry.get_agent(agent_id)
        
        if not agent:
            await update.message.reply_text("Agent not available.")
            return
        
        # Increment message count
        self.user_sessions[user_id]["message_count"] += 1
        
        # Demo response (would call agent in real implementation)
        response = f"""
*{agent.name}:* I received your message!

Your message: _{user_message}_

{self.user_sessions[user_id]['message_count']}. This is your message #{self.user_sessions[user_id]['message_count']}
        """
        
        await update.message.reply_text(response, parse_mode="Markdown")
        logger.info(f"User {user_id} message: {user_message}")
    
    def setup_handlers(self, app):
        """Setup all command and message handlers."""
        app.add_handler(CommandHandler("start", self.start_handler))
        app.add_handler(CommandHandler("research", self.research_handler))
        app.add_handler(CommandHandler("code", self.code_handler))
        app.add_handler(CommandHandler("status", self.status_handler))
        app.add_handler(CommandHandler("memory", self.memory_handler))
        app.add_handler(CommandHandler("help", self.help_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))


async def main():
    """Main bot execution (requires python-telegram-bot)."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set in .env")
        return
    
    logger.info("Starting Telegram bot...")
    
    try:
        from telegram.ext import Application
        
        # Create application
        app = Application.builder().token(token).build()
        
        # Initialize bot
        bot = HermesBot(token)
        bot.setup_handlers(app)
        
        # Start polling
        await app.run_polling()
    
    except ImportError:
        logger.error("python-telegram-bot not installed. Install with: pip install python-telegram-bot")
    except Exception as e:
        logger.error(f"Bot error: {e}")


if __name__ == "__main__":
    import sys
    
    # Check if python-telegram-bot is available
    try:
        import telegram
        print("✓ python-telegram-bot is installed")
        asyncio.run(main())
    except ImportError:
        print("✗ python-telegram-bot not installed")
        print("  Install with: pip install 'python-telegram-bot>=20.0'")
        sys.exit(1)

