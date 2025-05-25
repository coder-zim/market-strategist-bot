# telegram_bot.py
from telegram.ext import ApplicationBuilder
from fartdog_handler import get_conversation_handler
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def main():
    print("✅ Starting Fartdog bot...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(get_conversation_handler())

    await app.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())
