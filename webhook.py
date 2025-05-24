# webhook.py
import logging
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram_bot import TelegramBot
from config import CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot_instance = TelegramBot()

application = (
    ApplicationBuilder()
    .token(CONFIG["TELEGRAM_BOT_TOKEN"])
    .build()
)

application.add_handler(CommandHandler("start", bot_instance.start))
application.add_handler(CommandHandler("help", bot_instance.help_command))
application.add_handler(CommandHandler("fart", bot_instance.fart))
application.add_handler(CommandHandler("price", bot_instance.price))
application.add_handler(CommandHandler("hot", bot_instance.hot))

async def main():
    await application.bot.delete_webhook(drop_pending_updates=True)
    await application.initialize()
    await application.start()
    await application.run_polling()  # 👈 this is the critical line that keeps it running

if __name__ == "__main__":
    asyncio.run(main())