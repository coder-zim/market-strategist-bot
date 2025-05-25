# fartdog_handler.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)
from price_fetcher import fetch_token_data

MENU = range(1)

CHAIN_OPTIONS = [
    ("Ethereum 🧠", "ethereum"),
    ("Solana 💊", "solana"),
    ("SUI 💦", "sui"),
    ("Base 🔵", "base"),
    ("Abstract 🧪", "abstract"),
]

def get_chain_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(name, callback_data=f"select_chain:{value}")]
        for name, value in CHAIN_OPTIONS
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("🔥 /start was triggered")
    await update.message.reply_text(
        "😼 Yo, I’m Fartdog.\nI sniff contracts and roast charts.\nYou degen, I judge. That’s the deal. 💩\n\nEnter /fart followed by a contract address to generate a Fart Report.\n👇 First, pick a chain:",
        reply_markup=get_chain_keyboard()
    )
    return MENU

async def handle_chain_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, chain = query.data.split(":")
    context.user_data["chain"] = chain
    await query.edit_message_text(
        text=f"✅ Sniff mode set to: {chain.title()}\n\nNow enter /fart followed by a contract address.\n👇",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"Chain: {chain.title()} 🔄", callback_data="switch_chain")]
        ])
    )
    return MENU

async def switch_chain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🐾 Pick a new chain to sniff:", reply_markup=get_chain_keyboard())
    return MENU

async def handle_fart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = context.user_data.get("chain")
    if not chain:
        await update.message.reply_text("👃 Pick a chain first using /start.")
        return MENU

    contract = " ".join(context.args).strip()
    if not contract:
        await update.message.reply_text("⚠️ Use: /fart <contract_address>")
        return MENU

    return await send_fart_report(update, context, contract, chain)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = context.user_data.get("chain")
    if not chain:
        await update.message.reply_text("🤨 You gotta pick a chain first. Try /start")
        return MENU

    contract = update.message.text.strip()
    return await send_fart_report(update, context, contract, chain)

async def send_fart_report(update: Update, context: ContextTypes.DEFAULT_TYPE, contract: str, chain: str):
    data = fetch_token_data(chain, contract)
    if not data:
        await update.message.reply_text("❌ Token not found on Dexscreener or fallback APIs.")
        return MENU

    if data.get("dex_link", "").lower().find(chain) == -1:
        await update.message.reply_text(f"💩 This token is not native to {chain.title()}.")
        return MENU

    reply = (
        f"{data['name']} on {chain.upper()}\n"
        f"💸 Price: ${data['price']}\n"
        f"📊 24h Volume: ${data['volume']}\n"
        f"💧 Liquidity: ${data['liquidity']} | LP: {data['lp_burned']}\n"
        f"📈 FDV: ${data['fdv']}\n"
        f"🔗 {data['dex_link']}\n\n"
        f"{data['fart_note']}\n"
        f"👃 Wanna sniff more? Use /fart <contract> again."
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Chain: {chain.title()} 🔄", callback_data="switch_chain")]
    ])
    await update.message.reply_text(reply, reply_markup=keyboard)
    return MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fartdog’s done sniffing for now. 🐾")
    return ConversationHandler.END

def get_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [
                CallbackQueryHandler(handle_chain_select, pattern="^select_chain:"),
                CallbackQueryHandler(switch_chain, pattern="^switch_chain$"),
                CommandHandler("fart", handle_fart),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text),
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )