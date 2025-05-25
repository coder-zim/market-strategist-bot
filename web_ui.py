# web_ui.py
from fastapi import FastAPI, Request
from price_fetcher import fetch_token_data

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to Fartdog.org. Sniff a contract at /sniff"}

@app.get("/sniff")
async def sniff(chain: str, address: str):
    data = fetch_token_data(chain, address)
    if not data:
        return {"error": "Unable to sniff that contract."}
    return data
