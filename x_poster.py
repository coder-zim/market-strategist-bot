# x_poster.py

import logging
import tweepy
import time
import threading
import re
from config import CONFIG

logger = logging.getLogger(__name__)

class XPoster:
    def __init__(self):
        self.api = None
        self.client = None
        if CONFIG["FARTCAT_X_LAUNCH"] and CONFIG["TWITTER_API_KEY"]:
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
            threading.Thread(target=self.start_mention_listener, daemon=True).start()
            logger.info("X integration initialized")
        else:
            logger.info("X integration disabled")

    def post_report(self, address, chain, report):
        if not self.api or not CONFIG["FARTCAT_X_LAUNCH"]:
            logger.info("X posting skipped (disabled or not configured)")
            return
        try:
            clean_text = re.sub(r'<[^>]+>', '', report)
            summary = f"{CONFIG['BOT_NAME']} sniffed {address} on {chain.title()}! 💨\n{clean_text[:200]}...\nSniff it: https://t.me/FartcatBot"
            self.api.update_status(summary)
            logger.info(f"Posted to X for {address} on {chain}")
        except Exception as e:
            logger.error(f"Error posting to X: {e}")

    def start_mention_listener(self):
        logger.info("🐦 Fartcat X listener is on standby for tags...")
        bot_username = "fartcat_bot"
        last_seen_id = None

        while True:
            try:
                bot_id = self.client.get_user(username=bot_username).data.id
                mentions = self.client.get_users_mentions(id=bot_id)
                if mentions.data:
                    for mention in reversed(mentions.data):
                        if last_seen_id is None or mention.id > last_seen_id:
                            text = mention.text.lower()
                            if "sniff" in text or "chart" in text:
                                reply = f"💨 Yo @{mention.author_id}, you rang? Fartcat’s sniffing charts soon. Stay tuned."
                                self.client.create_tweet(text=reply, in_reply_to_tweet_id=mention.id)
                                logger.info("🐾 Replied to a mention.")
                            last_seen_id = mention.id
            except Exception as e:
                logger.error(f"❌ Error during mention check: {e}")
            time.sleep(30)