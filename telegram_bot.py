# telegram_bot.py

import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    ContextTypes
)
from telegram.constants import ParseMode
from data_fetcher import DataFetcher
from price_fetcher import get_price_summary
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
        fun_fact_text = fun_fact["value"] if fun_fact else "Fartcat’s got a nose for scams and a heart for degens!"
        await update.message.reply_text(
            f"😼 Yo, I’m {CONFIG['BOT_NAME']}.\n"
            f"{fun_fact_text}\n"
            "I sniff contracts, roast charts, and drop meme-worthy alpha.\n"
            "You degen, I judge. That’s the deal. 💩\n\n"
            "👇 Try these:\n"
            "/fart <contract> - Sniff a contract\n"
            "/price <ticker> - Check a coin’s price\n"
            "/hot - See trending contracts\n"
            "/help - Get the full scoop"
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        self.db.log_interaction(user_id, "help")
        await update.message.reply_text(
            f"📜 How to Use {CONFIG['BOT_NAME']}:\n\n"
            "• /fart <contract> - Analyze a contract address\n"
            "  Example: /fart 0xabc123...\n"
            "• /price <ticker> - Get coin price\n"
            "  Example: /price btc\n"
            "• /hot - See top trending contracts\n\n"
            f"✅ Supported chains: {', '.join(CONFIG['SUPPORTED_CHAINS'])}\n\n"
            "🐾 What you get:\n"
            "• Price, Volume, Liquidity, FDV\n"
            "• Launchpad vibes (e.g., Pump.fun)\n"
            "• Chart Health 🟢🟡🔴\n"
            "• LP Status (🔥 or ☠️)\n"
            "• Holder & Age Scores\n"
            "• Risk Analysis (GoPlus, TokenSniffer)\n"
            "• Meme-worthy hot takes 😹\n\n"
            "If I say 'Still in the litter box'... your stinker’s too fresh 🧻"
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
            await update.message.reply_text("😿 Couldn't guess the chain. Try another contract.")
            return
        result = self.agent.fetch_basic_info(address, chain)
        await update.message.reply_text(result, parse_mode=ParseMode.HTML, disable_web_page_preview=False)
        if CONFIG["FARTCAT_X_LAUNCH"]:
            self.x_poster.post_report(address, chain, result)

    async def price(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not context.args:
            self.db.log_interaction(user_id, "price", None)
            await update.message.reply_text("❗ Usage: /price <ticker>")
            return
        ticker = context.args[0].strip()
        self.db.log_interaction(user_id, "price", ticker)
        result = get_price_summary(ticker)
        if result:
            await update.message.reply_text(result)
        else:
            await update.message.reply_text("😿 Couldn't find that coin. Try another ticker.")

    async def hot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        self.db.log_interaction(user_id, "hot")
        popular = self.db.get_popular_contracts()
        if not popular:
            await update.message.reply_text("😿 No hot contracts yet. Keep sniffing!")
            return
        response = "<b>🔥 Hottest Contracts:</b>\n\n"
        for contract in popular:
            response += f"• {contract['address']} ({contract['chain'].title()}): Queried {contract['query_count']} times\n"
        response += "\nUse /fart <contract> to sniff one!"
        await update.message.reply_text(response, parse_mode=ParseMode.HTML)

if __name__ == "__main__":
    import asyncio
    from telegram.ext import ApplicationBuilder
    app = ApplicationBuilder().token(CONFIG["TELEGRAM_BOT_TOKEN"]).build()

    from telegram_bot import TelegramBot
    bot = TelegramBot()
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("help", bot.help_command))
    app.add_handler(CommandHandler("fart", bot.fart))
    app.add_handler(CommandHandler("price", bot.price))
    app.add_handler(CommandHandler("hot", bot.hot))

    print("Bot polling...")
    asyncio.run(app.run_polling())