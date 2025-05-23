# webhook.py
import logging
import threading
import asyncio
import uvicorn
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram_bot import TelegramBot
from config import CONFIG

logger = logging.getLogger(__name__)
app = FastAPI()

async def setup_application():
    bot = TelegramBot()
    application = (
        ApplicationBuilder()
        .token(CONFIG["TELEGRAM_BOT_TOKEN"])
        .build()
    )
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("fart", bot.fart))
    application.add_handler(CommandHandler("price", bot.price))
    application.add_handler(CommandHandler("hot", bot.hot))
    return application

@app.on_event("startup")
async def on_startup():
    app.state.application = await setup_application()
    if CONFIG["ENVIRONMENT"] == "production":
        webhook_url = f"{CONFIG['WEBHOOK_URL']}/webhook"
        await app.state.application.bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to {webhook_url}")
    else:
        def run_bot():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(app.state.application.initialize())
            loop.run_until_complete(app.state.application.start())
            loop.run_forever()
        threading.Thread(target=run_bot).start()

@app.on_event("shutdown")
async def on_shutdown():
    if CONFIG["ENVIRONMENT"] != "production":
        await app.state.application.shutdown()

@app.post("/webhook")
async def webhook(request: Request):
    if CONFIG["ENVIRONMENT"] != "production":
        return {"status": "ignored", "message": "Webhook ignored in local mode"}
    update = await request.json()
    update = Update.de_json(update, app.state.application.bot)
    await app.state.application.process_update(update)
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
