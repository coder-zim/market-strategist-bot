# webhook.py
import logging
import asyncio
import uvicorn
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram_bot import TelegramBot
from config import CONFIG

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

# if __name__ == "__main__":
#     if CONFIG["ENVIRONMENT"] == "production":
#         uvicorn.run("webhook:app", host="0.0.0.0", port=8000)
#     else:
#         asyncio.run(app.bot.delete_webhook(drop_pending_updates=True))
#         asyncio.run(application.run_polling())
