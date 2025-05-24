# webhook.py
import logging
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram_bot import TelegramBot
from config import CONFIG

from telegram.ext import AIORateLimiter  # fixes async command rate issues

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    bot = TelegramBot()
    app = (
        ApplicationBuilder()
        .token(CONFIG["TELEGRAM_BOT_TOKEN"])
        .rate_limiter(AIORateLimiter())  # ✅ important for async
        .build()
    )

    # 🔄 Wrap async handlers in .run_async so they work in sync run_polling
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("help", bot.help_command))
    app.add_handler(CommandHandler("fart", bot.fart))
    app.add_handler(CommandHandler("price", bot.price))
    app.add_handler(CommandHandler("hot", bot.hot))

    app.bot.delete_webhook(drop_pending_updates=True)
    app.run_polling(stop_signals=None)

if __name__ == "__main__":
    main()
