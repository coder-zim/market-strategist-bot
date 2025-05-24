# webhook.py
import logging
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram_bot import TelegramBot
from config import CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    bot = TelegramBot()
    app = (
        ApplicationBuilder()
        .token(CONFIG["TELEGRAM_BOT_TOKEN"])
        .build()
    )

    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("help", bot.help_command))
    app.add_handler(CommandHandler("fart", bot.fart))
    app.add_handler(CommandHandler("price", bot.price))
    app.add_handler(CommandHandler("hot", bot.hot))

    await app.bot.delete_webhook(drop_pending_updates=True)
    await app.initialize()
    await app.start()
    
    print("✅ Bot is polling... waiting for updates...")
    while True:
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
