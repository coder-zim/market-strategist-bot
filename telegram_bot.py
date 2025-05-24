import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from data_fetcher import DataFetcher
from config import CONFIG

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='bot.log')
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.fetcher = DataFetcher()
        self.bot_name = CONFIG["BOT_NAME"]

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            f"🐶 {self.bot_name} is sniffing for scams! Send /fart <chain> <address> or /price <chain> <address>."
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Commands:\n/fart <chain> <address> - Get token risk report\n/price <chain> <address> - Get token price\nSupported chains: ethereum, solana, base, sui, abstract"
        )

    async def fart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if len(context.args) < 2:
            await update.message.reply_text("Usage: /fart <chain> <address>")
            return
        chain, address = context.args[0], context.args[1]
        if chain.lower() not in CONFIG["SUPPORTED_CHAINS"]:
            await update.message.reply_text(f"Unsupported chain. Use: {', '.join(CONFIG['SUPPORTED_CHAINS'])}")
            return
        try:
            result = self.fetcher.process(address, chain)["summary"]
            await update.message.reply_text(result, parse_mode="HTML", disable_web_page_preview=True)
        except Exception as e:
            logger.error(f"Error in /fart: {e}")
            await update.message.reply_text(f"⚠️ Error sniffing {address}: {str(e)}")

    async def price(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if len(context.args) < 2:
            await update.message.reply_text("Usage: /price <chain> <address>")
            return
        chain, address = context.args[0], context.args[1]
        if chain.lower() not in CONFIG["SUPPORTED_CHAINS"]:
            await update.message.reply_text(f"Unsupported chain. Use: {', '.join(CONFIG['SUPPORTED_CHAINS'])}")
            return
        try:
            result = self.fetcher.fetch_basic_info(address, chain)
            await update.message.reply_text(result, parse_mode="HTML", disable_web_page_preview=True)
        except Exception as e:
            logger.error(f"Error in /price: {e}")
            await update.message.reply_text(f"⚠️ Error fetching price for {address}: {str(e)}")

def main():
    app = ApplicationBuilder().token(CONFIG["TELEGRAM_BOT_TOKEN"]).build()
    bot = TelegramBot()
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("help", bot.help_command))
    app.add_handler(CommandHandler("fart", bot.fart))
    app.add_handler(CommandHandler("price", bot.price))
    logger.info("Starting bot polling...")
    app.run_polling()

if __name__ == "__main__":
    main()