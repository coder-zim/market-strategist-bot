import logging
import tweepy
import re
from config import CONFIG
from data_fetcher import DataFetcher

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='x_poster.log')
logger = logging.getLogger(__name__)

class XPoster:
    def __init__(self):
        self.api = None
        self.client = None
        self.fetcher = DataFetcher()
        if CONFIG.get("FARTDOG_X_LAUNCH") and CONFIG.get("TWITTER_API_KEY"):
            auth = tweepy.OAuth1UserHandler(
                CONFIG["TWITTER_API_KEY"],
                CONFIG["TWITTER_API_SECRET"],
                CONFIG["TWITTER_ACCESS_TOKEN"],
                CONFIG["TWITTER_ACCESS_SECRET"],
            )
            self.api = tweepy.API(auth)
            self.client = tweepy.Client(
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
            logger.info("X posting skipped")
            return
        try:
            clean_text = re.sub(r'<[^>]+>', '', report)
            summary = f"{CONFIG['BOT_NAME']} sniffed {address} on {chain.title()}! 💨\n{clean_text[:200]}...\nSniff it: https://t.me/fartdog_bot"
            self.client.create_tweet(text=summary)
            logger.info(f"Posted to X for {address} on {chain}")
        except Exception as e:
            logger.error(f"Error posting to X: {e}")

    def check_mentions(self):
        if not self.api or not CONFIG.get("FARTDOG_X_LAUNCH"):
            return
        try:
            mentions = self.api.mentions_timeline(count=10)
            for mention in mentions:
                text = mention.text.lower()
                for chain in CONFIG["SUPPORTED_CHAINS"]:
                    if chain in text:
                        words = text.split()
                        for word in words:
                            if self.fetcher.guess_chain(word):
                                logger.info(f"Processing mention: {word} on {chain}")
                                report = self.fetcher.process(word, chain)["summary"]
                                self.post_report(word, chain, report)
                                break
        except Exception as e:
            logger.error(f"Error checking X mentions: {e}")

def main():
    poster = XPoster()
    while True:
        poster.check_mentions()
        import time
        time.sleep(60)

if __name__ == "__main__":
    main()