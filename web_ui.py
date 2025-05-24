from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram_bot import TelegramBot
from data_fetcher import DataFetcher
from config import CONFIG

app = FastAPI()
agent = DataFetcher()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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
    except Exception as e:
        summary = f"Error processing request: {str(e)}"
    return templates.TemplateResponse("index.html", {
        "request": request,
        "question": question,
        "response": summary
    })