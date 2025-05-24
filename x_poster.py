import logging
import tweepy
import re
from config import CONFIG

logger = logging.getLogger(__name__)

class XPoster:
    def __init__(self):
        self.api = None
        self.client = None
        if CONFIG.get("FARTDOG_X_LAUNCH") and CONFIG.get("TWITTER_API_KEY"):
            auth = tweepy.OAuth1UserHandler(
                CONFIG["TWITTER_API_KEY"],
                CONFIG["TWITTER_API_SECRET"],
                CONFIG["TWITTER_ACCESS_TOKEN"],
                CONFIG["TWITTER_ACCESS_SECRET"],
            )
            self.api = tweepy.API(auth)
            self.client = tweepy.Client(
                bearer_token=CONFIG.get("TWITTER_BEARER_TOKEN"),
                consumer_key=CONFIG["TWITTER_API_KEY"],
                consumer_secret=CONFIG["TWITTER_API_SECRET"],
                access_token=CONFIG["TWITTER_ACCESS_TOKEN"],
                access_token_secret=CONFIG["TWITTER_ACCESS_SECRET"],
            )
            logger.info("X integration initialized")
        else:
            logger.info("X integration disabled")

    def post_report(self, address, chain, report):
        if not self.api or not CONFIG.get("FARTDOG_X_LAUNCH"):
            logger.info("X posting skipped (disabled or not configured)")
            return
        try:
            clean_text = re.sub(r'<[^>]+>', '', report)
            summary = f"{CONFIG['BOT_NAME']} sniffed {address} on {chain.title()}! 💨\n{clean_text[:200]}...\nSniff it: https://t.me/fartdog_bot"
            self.api.update_status(summary)
            logger.info(f"Posted to X for {address} on {chain}")
        except Exception as e:
            logger.error(f"Error posting to X: {e}")