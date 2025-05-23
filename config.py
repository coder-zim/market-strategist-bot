# config.py

import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
    "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
    "MONGO_URI": os.getenv("MONGO_URI"),
    "WEBHOOK_URL": os.getenv("WEBHOOK_URL"),
    "ENVIRONMENT": os.getenv("ENVIRONMENT", "production"),
    "GOPLUS_BASE_URL": os.getenv("GOPLUS_BASE_URL"),
    "GOPLUS_APP_KEY": os.getenv("GOPLUS_APP_KEY"),
    "GOPLUS_APP_SECRET": os.getenv("GOPLUS_APP_SECRET"),
    "ETHERSCAN_API_KEY": os.getenv("ETHERSCAN_API_KEY"),
    "SOLSCAN_API_KEY": os.getenv("SOLSCAN_API_KEY"),
    "BASESCAN_API_KEY": os.getenv("BASESCAN_API_KEY"),
    "BIRDEYE_API_KEY": os.getenv("BIRDEYE_API_KEY"),
    "INFURA_URL": os.getenv("INFURA_URL"),
    "BITQUERY_API_KEY": os.getenv("BITQUERY_API_KEY"),
    "TWITTER_API_KEY": os.getenv("TWITTER_API_KEY"),
    "TWITTER_API_SECRET": os.getenv("TWITTER_API_SECRET"),
    "TWITTER_ACCESS_TOKEN": os.getenv("TWITTER_ACCESS_TOKEN"),
    "TWITTER_ACCESS_SECRET": os.getenv("TWITTER_ACCESS_SECRET"),
    "BOT_NAME": "Fartcat",
    "SUPPORTED_CHAINS": ["ethereum", "solana", "base", "sui", "abstract"],
    "FARTCAT_X_LAUNCH": os.getenv("FARTCAT_X_LAUNCH") == "true",
}