# telegram_bot.py
import os
import asyncio
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder
from fartdog_handler import get_conversation_handler
import nest_asyncio

load_dotenv()
nest_asyncio.apply()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def main():
    print("✅ Starting Fartdog bot...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(get_conversation_handler())
    await app.run_polling()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
