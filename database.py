# database.py

import logging
import datetime
import random
from pymongo import MongoClient
from config import CONFIG

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = MongoClient(CONFIG["MONGO_URI"])
        self.db = self.client.get_database("swarmhq")
        self.contracts = self.db.contracts
        self.interactions = self.db.interactions
        self.logs = self.db.logs
        self.personality = self.db.personality

    def save_contract_data(self, address, chain, data):
        try:
            self.contracts.update_one(
                {"address": address, "chain": chain},
                {
                    "$set": {
                        "address": address,
                        "chain": chain,
                        "data": data,
                        "last_updated": datetime.datetime.utcnow(),
                    },
                    "$inc": {"query_count": 1},
                },
                upsert=True,
            )
            logger.info(f"Saved contract data for {address} on {chain}")
        except Exception as e:
            logger.error(f"Error saving contract data: {e}")

    def get_contract_data(self, address, chain):
        try:
            return self.contracts.find_one({"address": address, "chain": chain})
        except Exception as e:
            logger.error(f"Error fetching contract data: {e}")
            return None

    def log_interaction(self, user_id, command, address=None):
        try:
            self.interactions.insert_one({
                "user_id": user_id,
                "command": command,
                "address": address,
                "timestamp": datetime.datetime.utcnow(),
            })
        except Exception as e:
            logger.error(f"Error logging interaction: {e}")

    def log_query(self, agent_name, question, response):
        try:
            self.logs.insert_one({
                "agent_name": agent_name,
                "question": question,
                "response": response,
                "timestamp": datetime.datetime.utcnow(),
            })
        except Exception as e:
            logger.error(f"Error logging query: {e}")

    def get_popular_contracts(self, limit=5):
        try:
            return list(
                self.contracts.find()
                .sort("query_count", -1)
                .limit(limit)
            )
        except Exception as e:
            logger.error(f"Error fetching popular contracts: {e}")
            return []

    def add_personality(self, type, value, context="general", phrases=None):
        try:
            doc = {
                "type": type,
                "value": value,
                "context": context,
                "timestamp": datetime.datetime.utcnow()
            }
            if phrases:
                doc["phrases"] = phrases
            self.personality.insert_one(doc)
            logger.info(f"Added personality {type}: {value}")
        except Exception as e:
            logger.error(f"Error adding personality: {e}")

    def get_personality(self, type, context="general"):
        try:
            items = list(self.personality.find({"type": type, "context": context}))
            return random.choice(items) if items else None
        except Exception as e:
            logger.error(f"Error fetching personality: {e}")
            return None