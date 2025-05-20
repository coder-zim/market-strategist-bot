# telegram_bot.py
import os
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, CallbackQueryHandler, filters
)
from market_strategist import MarketStrategist
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise EnvironmentError("❌ TELEGRAM_BOT_TOKEN not found in .env file")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

agent = MarketStrategist()
user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("🐾 /start command triggered")
    user_id = update.effective_user.id
    user_sessions[user_id] = {"chain": None, "expecting_address": False}

    keyboard = [
        [InlineKeyboardButton("Ethereum 🧅", callback_data="chain_ethereum")],
        [InlineKeyboardButton("Solana 🐬", callback_data="chain_solana")],
        [InlineKeyboardButton("SUI 🧪", callback_data="chain_sui")],
        [InlineKeyboardButton("Base 🧻", callback_data="chain_base")],
        [InlineKeyboardButton("Abstract 🧠", callback_data="chain_abstract")]
    ]

    welcome = (
        "PURRR-FECTO! 🐱\n"
        "🐽 Sniff mode engaged.\n\n"
        "1️⃣ Pick a chain below: ⛓️\n"
        "2️⃣ Toss me a CA 📃\n\n"
        "Then I’ll do my thing. 🙀\n\n"
        "💨 I might help. I might just fart on it. No promises."
    )

    if update.message:
        await update.message.reply_text(welcome, reply_markup=InlineKeyboardMarkup(keyboard))
    elif update.callback_query:
        await update.callback_query.edit_message_text(welcome, reply_markup=InlineKeyboardMarkup(keyboard))

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    summary = (
        "🐈💨 *WHO IS FARTCAT?*\n\n"
        "I’m Fartcat – part feline, part blockchain bloodhound.\n"
        "When you drop a contract address, I dig into the data and cough up insights faster than a hairball.\n"
        "Sniffing rugs, roasting charts, and sometimes just leaving a stink behind... that's my game. 💩\n\n"
        "📍 *Token Details:*\n"
        "• 💩 Contract: `0xFARTCATFARTCATFARTCATFARTCAT` *(placeholder)*\n"
        "• 🗨️ Telegram: [@Fartcat_bot](https://t.me/Fartcat_bot)\n"
        "• 🐦 Twitter (𝕏): [@Fartcat_bot](https://x.com/Fartcat_bot)\n"
        "• 🌐 Website: https://fartcat.agent.com\n\n"
        "🛠️ *What I Can Do:*\n"
        "• /start – Activate sniff mode and pick a chain\n"
        "• /info – Who I am and how to use me\n"
        "• /help – Quick guide on sniffing\n"
        "• /exit – End the current session with me\n\n"
        "Just pick a chain, drop a contract, and I’ll do the dirty work.\n"
        "💨 No guarantees... just vibes."
    )

    await update.message.reply_text(summary, disable_web_page_preview=True)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data.startswith("chain_"):
        chain = data.split("_")[1]
        user_sessions[user_id] = {"chain": chain, "expecting_address": True}
        await query.edit_message_text(
            f"✅ You picked {chain.upper()}.\n😽 Now toss me a contract address to sniff."
        )
    elif data == "exit":
        user_sessions.pop(user_id, None)
        await query.edit_message_text("👃 Smell ya later! Type /start if you wanna sniff again.")
    elif data == "noop":
        await query.answer("😾 You already picked a chain. Just send the contract.", show_alert=False)

async def send_result_with_buttons(update: Update, chain, address, summary):
    keyboard = [
        [InlineKeyboardButton(f"🐾 Chain: {chain.upper()}", callback_data="noop")],
        [InlineKeyboardButton("📈 Sniff the Chart", url=f"https://dexscreener.com/{chain}/{address}")],
        [InlineKeyboardButton("❌ I'm Done Here", callback_data="exit")]
    ]
    footer = "\n\n👃 Wanna sniff more? Just drop another contract."
    await update.message.reply_text(summary + footer, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = user_sessions.get(user_id, {"chain": None, "expecting_address": False})

    if session["expecting_address"] and session["chain"]:
        chain = session["chain"]
        address = update.message.text.strip()
        result = agent.process(address, chain)
        await send_result_with_buttons(update, chain, address, fartcat_wrap(result["summary"]))
    else:
        await update.message.reply_text("😿 You didn’t pick a chain. Type /start before I knock over your portfolio.")

def fartcat_wrap(summary: str) -> str:
    tails = [
        "😼 This one’s spicy.",
        "💨 I smell a pump... or a dump.",
        "😹 Not financial advice, but I did bury this chart.",
        "🐾 Might be moon, might be mold.",
        "🚽 Litterbox-worthy. You decide."
    ]
    return f"{summary}\n\n{random.choice(tails)}"

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("help", info))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    logger.info("😼 Fartcat Bot is gassing up...")
    app.run_polling()

if __name__ == "__main__":
    main()
