import requests
token = "7901149869:AAGcXpRyrh0r1WWTxOEDEjWY2nK6IJhX5qQ"
res = requests.get(f"https://api.telegram.org/bot{token}/deleteWebhook?drop_pending_updates=true")
print(res.json())