from telegram.ext import ApplicationBuilder, CommandHandler
from telegram_bot import TelegramBot
from config import CONFIG

def main():
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

    app.bot.delete_webhook(drop_pending_updates=True)
    app.run_polling(stop_signals=None)

if __name__ == "__main__":
    main()
