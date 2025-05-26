#x_listener.py
import os
import random
import tweepy
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

fart_responses = [
    "Sniff sniff... yep, that chart reeks. 💨📉",
    "Just crop-dusted your portfolio. You're welcome. 🐶💩",
    "I only sniff the finest degens. You're one of 'em. 💨",
    "That contract? Smells like a rug dipped in farts. 🧻🚨",
    "Barking at this one 'cause it smells bullish... or is that just methane?",
    "Your wallet stinks. Let's keep it that way. 💸💨",
    "I detect traces of utility... and flatulence.",
    "Fartdog here. You rang? Smells... speculative. 🐕💥",
    "This tweet smells like 100x or 100 tears. No in-between. 💨📉📈",
    "I farted. But your token farted first."
]

class FartdogResponder(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        if tweet.in_reply_to_user_id is not None or tweet.author_id == self.me.id:
            return

        username = tweet.author_id
        response = random.choice(fart_responses)

        try:
            self.client.create_tweet(
                text=f"@{tweet.author.username} {response}",
                in_reply_to_tweet_id=tweet.id
            )
            print(f"💨 Replied to @{tweet.author.username}")
        except Exception as e:
            print(f"Failed to reply: {e}")

    def on_connect(self):
        print("🐾 Fartdog connected to Twitter.")

def main():
    client = tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET
    )

    me = client.get_me().data
    stream = FartdogResponder(BEARER_TOKEN)
    stream.client = client
    stream.me = me

    rules = stream.get_rules().data
    if rules:
        rule_ids = [rule.id for rule in rules]
        stream.delete_rules(rule_ids)

    stream.add_rules(tweepy.StreamRule("@Fartdog_bot"))
    stream.filter(tweet_fields=["author_id", "in_reply_to_user_id"])

if __name__ == "__main__":
    main()
