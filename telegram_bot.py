# telegram_bot.py
import logging
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    ContextTypes
)
from telegram.constants import ParseMode
from data_fetcher import DataFetcher
from database import Database
from config import CONFIG
from x_poster import XPoster

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.agent = DataFetcher()
        self.db = Database()
        self.x_poster = XPoster()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        self.db.log_interaction(user_id, "start")
        fun_fact = self.db.get_personality("fun_fact", "intro")
        fun_fact_text = fun_fact["value"] if fun_fact else "Fartdog’s nose is locked on your wallet. Let’s sniff some contracts!"
        await update.message.reply_text(
            f"GOOD BOY! 🐶\n"
            f"{fun_fact_text}\n\n"
            "👇 Here’s where I sniff around:\n\n"
            "• Ethereum 🧠\n"
            "• Solana 💊\n"
            "• SUI 💦\n"
            "• Base 🔵\n"
            "• Abstract 🧪\n\n"
            "Enter /fart followed by a contract address and I’ll fetch the alpha. 🦴\n"
            "💨 I might help. I might just lift a leg on it. No promises."
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        self.db.log_interaction(user_id, "help")
        await update.message.reply_text(
            f"📜 How to Use {CONFIG['BOT_NAME']}\n\n"
            "• /fart <contract> - Analyze a contract address\n"
            "  Example: /fart 0xabc123...\n\n"
            f"✅ Supported chains: {', '.join(CONFIG['SUPPORTED_CHAINS'])}\n\n"
            "🐾 What you get:\n"
            "• Price, Volume, Liquidity, FDV\n"
            "• Chart Health 🟢 🟡 🔴\n"
            "• LP Status 🔥 (burned), ☠️ (not locked)\n"
            "• Holders 🟢 (1000+), 🟡 (500+), 🔴 (<500)\n"
            "• Age & Risk 🔬\n"
            "• Quick hot take + links\n\n"
            "If I say 'Still in the kennel'... your token’s too fresh 🧻",
            parse_mode=ParseMode.HTML
        )

    async def fart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not context.args:
            self.db.log_interaction(user_id, "fart", None)
            await update.message.reply_text("❗ Usage: /fart <contract address>")
            return
        address = context.args[0].strip()
        self.db.log_interaction(user_id, "fart", address)
        chain = self.agent.guess_chain(address)
        if not chain:
            await update.message.reply_text("🐾 Couldn't guess the chain. Try another contract.")
            return
        result = self.agent.fetch_basic_info(address, chain)
        await update.message.reply_text(result, parse_mode=ParseMode.HTML, disable_web_page_preview=False)
        if CONFIG["FARTDOG_X_LAUNCH"]:
            self.x_poster.post_report(address, chain, result)

    async def price(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not context.args:
            self.db.log_interaction(user_id, "price", None)
            await update.message.reply_text("❗ Usage: /price <ticker>")
            return
        ticker = context.args[0].strip()
        self.db.log_interaction(user_id, "price", ticker)
        await update.message.reply_text(f"Fetching price for {ticker}... (feature not implemented)")

    async def hot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        self.db.log_interaction(user_id, "hot")
        popular = self.db.get_popular_contracts()
        if not popular:
            await update.message.reply_text("🐕 No hot contracts yet. Keep sniffing!")
            return
        response = "<b>🔥 Hottest Contracts:</b>\n\n"
        for contract in popular:
            response += f"• {contract['address']} ({contract['chain'].title()}): Queried {contract['query_count']} times\n"
        response += "\nUse /fart <contract> to sniff one!"
        await update.message.reply_text(response, parse_mode=ParseMode.HTML)

if __name__ == "__main__":
    import asyncio
    from telegram.ext import ApplicationBuilder

    print("🐶 Fartdog bot is now sniffing contracts on Telegram...")

    app = ApplicationBuilder().token(CONFIG["TELEGRAM_BOT_TOKEN"]).build()

    bot = TelegramBot()
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("help", bot.help_command))
    app.add_handler(CommandHandler("fart", bot.fart))
    app.add_handler(CommandHandler("price", bot.price))
    app.add_handler(CommandHandler("hot", bot.hot))

    app.run_polling()
