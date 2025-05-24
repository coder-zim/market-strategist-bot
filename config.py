import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
    "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
    "TWITTER_API_KEY": os.getenv("TWITTER_API_KEY"),
    "TWITTER_API_SECRET": os.getenv("TWITTER_API_SECRET"),
    "TWITTER_ACCESS_TOKEN": os.getenv("TWITTER_ACCESS_TOKEN"),
    "TWITTER_ACCESS_SECRET": os.getenv("TWITTER_ACCESS_SECRET"),
    "MORALIS_API_KEY": os.getenv("MORALIS_API_KEY"),
    "BOT_NAME": "Fartdog",
    "SUPPORTED_CHAINS": ["ethereum", "solana", "base", "sui", "abstract"],
    "FARTDOG_X_LAUNCH": os.getenv("FARTDOG_X_LAUNCH") == "true",
}