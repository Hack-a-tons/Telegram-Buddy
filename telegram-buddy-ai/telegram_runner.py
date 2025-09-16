# telegram_runner.py
"""
Standalone runner for Telegram bot
Run this alongside your FastAPI web demo
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def main():
    """Run the Telegram bot"""
    try:
        from app.connectors.telegram_bot import TelegramBuddy
        
        bot = TelegramBuddy()
        logger.info("Telegram Buddy AI is starting...")
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()