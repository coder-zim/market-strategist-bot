# web_ui.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram_bot import TelegramBot
from data_fetcher import DataFetcher
from database import Database
from config import CONFIG

app = FastAPI()
agent = DataFetcher()
db = Database()

bot = TelegramBot()
telegram_app = (
    ApplicationBuilder()
    .token(CONFIG["TELEGRAM_BOT_TOKEN"])
    .build()
)
telegram_app.add_handler(CommandHandler("start", bot.start))
telegram_app.add_handler(CommandHandler("help", bot.help_command))
telegram_app.add_handler(CommandHandler("fart", bot.fart))
telegram_app.add_handler(CommandHandler("price", bot.price))
telegram_app.add_handler(CommandHandler("hot", bot.hot))

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup_event():
    if CONFIG["ENVIRONMENT"] == "production":
        webhook_url = f"{CONFIG['WEBHOOK_URL']}/webhook"
        await telegram_app.bot.set_webhook(webhook_url)
    else:
        import threading
        import asyncio
        def run_bot():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(telegram_app.initialize())
            telegram_app.run_polling()
            loop.run_forever()
        threading.Thread(target=run_bot).start()

@app.on_event("shutdown")
async def shutdown_event():
    if CONFIG["ENVIRONMENT"] != "production":
        await telegram_app.shutdown()

@app.post("/webhook")
async def webhook(request: Request):
    if CONFIG["ENVIRONMENT"] != "production":
        return {"status": "ignored", "message": "Webhook ignored in local mode"}
    update = await request.json()
    update = Update.de_json(update, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ask", response_class=HTMLResponse)
async def ask(request: Request, question: str = Form(...), chain: str = Form(...)):
    try:
        response = agent.process(question, chain)
        summary = response["summary"]
        db.log_query(agent_name=agent.name, question=f"{chain} - {question}", response=summary)
    except Exception as e:
        summary = f"Error processing request: {str(e)}"
        db.log_query(agent_name=agent.name, question=f"{chain} - {question}", response=summary)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "question": question,
        "response": summary
    })
