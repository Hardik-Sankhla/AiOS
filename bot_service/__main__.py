"""Run the Telegram bot as a module: python -m bot_service"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import and run
try:
    import telegram
    from bot_service.bot import main
    print("✓ python-telegram-bot is installed")
    asyncio.run(main())
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("  Install with: pip install 'python-telegram-bot>=20.0'")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
