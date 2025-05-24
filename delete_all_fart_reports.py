# delete_all_fart_reports.py

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["swarmhq"]

# Wipe both collections to reset bot memory
deleted_reports = db.fart_reports.delete_many({})
deleted_personality = db.personality.delete_many({})

print(f"Deleted {deleted_reports.deleted_count} documents from fart_reports.")
print(f"Deleted {deleted_personality.deleted_count} documents from personality.")
