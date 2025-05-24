# webhook.py
import logging
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram_bot import TelegramBot
from config import CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_bot():
    bot_instance = TelegramBot()
    app = (
        ApplicationBuilder()
        .token(CONFIG["TELEGRAM_BOT_TOKEN"])
        .build()
    )

    app.add_handler(CommandHandler("start", bot_instance.start))
    app.add_handler(CommandHandler("help", bot_instance.help_command))
    app.add_handler(CommandHandler("fart", bot_instance.fart))
    app.add_handler(CommandHandler("price", bot_instance.price))
    app.add_handler(CommandHandler("hot", bot_instance.hot))

    await app.bot.delete_webhook(drop_pending_updates=True)
    await app.initialize()
    await app.start()
    await app.run_polling()
    await app.idle()  # 👈 THIS KEEPS THE BOT RUNNING FOREVER

if __name__ == "__main__":
    asyncio.run(run_bot())
