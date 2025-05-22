# telegram_bot.py

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, CallbackQueryHandler, filters)
from telegram.constants import ParseMode
from data_fetcher import DataFetcher
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise EnvironmentError("❌ TELEGRAM_BOT_TOKEN not found in .env file")

agent = DataFetcher()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

user_sessions = {}

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "😼 I’m Fartcat — your chain-sniffin’, chart-roastin’, fart-droppin’ AI feline.\n\n"
        "💩 Use /start to sniff a contract.\n"
        "❓ Available commands:\n"
        "/start /help /meow /rugcheck"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = user_sessions.get(user_id, {"chain": None, "expecting_address": False})

    if session["expecting_address"] and session["chain"]:
        chain = session["chain"]
        address = update.message.text.strip()
        session["address"] = address

        full = agent.fetch_all_reports(address, chain)

        keyboard = [
            [InlineKeyboardButton(f"🐾 Chain: {chain.upper()}", callback_data="change_chain")],
            [InlineKeyboardButton("📈 Chart", url=f"https://dexscreener.com/{chain}/{address}")],
            [InlineKeyboardButton("❌ Exit", callback_data="exit")]
        ]

        clickable_ca = f"<a href=\"tg://copy?text={address}\">{address}</a>"
        full_msg = f"<b>Contract:</b> {clickable_ca}\n\n{full}"

        await update.message.reply_text(full_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    else:
        await update.message.reply_text("😿 You didn’t pick a chain. Type /start before I knock over your portfolio.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data.startswith("chain_"):
        chain = data.split("_")[1]
        user_sessions[user_id] = {"chain": chain, "expecting_address": True}
        await query.edit_message_text(f"✅ You picked {chain.upper()}.\n😽 Now toss me a contract address to sniff.")
    elif data == "change_chain":
        keyboard = [
            [InlineKeyboardButton("Ethereum 🧅", callback_data="chain_ethereum")],
            [InlineKeyboardButton("Solana 🐬", callback_data="chain_solana")],
            [InlineKeyboardButton("SUI 🧪", callback_data="chain_sui")],
            [InlineKeyboardButton("Base 🧻", callback_data="chain_base")],
            [InlineKeyboardButton("Abstract 🧠", callback_data="chain_abstract")]
        ]
        await query.edit_message_text("🔁 Pick a different chain:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "exit":
        user_sessions.pop(user_id, None)
        await query.edit_message_text("👃 Smell ya later! Type /start if you wanna sniff again.")
    elif data == "noop":
        await query.answer("😾 You already picked a chain. Just send the contract.", show_alert=False)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == "__main__":
    main()