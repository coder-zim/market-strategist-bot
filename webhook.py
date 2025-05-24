# webhook.py
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
from fastapi import FastAPI, Request
from config import CONFIG
from telegram_bot import TelegramBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

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

@app.post("/webhook")
async def webhook(request: Request):
    update = await request.json()
    update = Update.de_json(update, application.bot)
    await application.process_update(update)
    return {"status": "ok"}

if __name__ == "__main__":
    async def main():
        await application.bot.delete_webhook(drop_pending_updates=True)
        await application.initialize()
        await application.start()
        await application.run_polling()

    asyncio.run(main())
