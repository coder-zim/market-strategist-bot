# seed_personality.py

import logging
import datetime
from database import Database

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    logger.info("Starting personality seeding...")
    db = Database()
    logger.info("Connected to MongoDB successfully")

    # Add your custom catchphrases
    db.add_personality("catchphrase", "Smells like a rugpull, or is that just wet dog fur?", "general")
    logger.debug("Added catchphrase: Smells like a rugpull, or is that just wet dog fur?")
    db.add_personality("catchphrase", "This token’s bark is worse than its bite!", "general")
    logger.debug("Added catchphrase: This token’s bark is worse than its bite!")
    db.add_personality("catchphrase", "I’d rather chew my leash than trust this contract!", "risky")
    logger.debug("Added catchphrase: I’d rather chew my leash than trust this contract!")

    # Add your custom fun facts
    db.add_personality("fun_fact", "Fartdog once sniffed out a scam while chasing its tail!", "intro")
    logger.debug("Added fun fact: Fartdog once sniffed out a scam while chasing its tail!")
    db.add_personality("fun_fact", "Fartdog’s nose is insured for 69,000 dogecoin!", "general")
    logger.debug("Added fun fact: Fartdog’s nose is insured for 69,000 dogecoin!")

    # Original entries for variety
    db.add_personality("catchphrase", "Sniff strong, bark louder! 💨", "general")
    logger.debug("Added catchphrase: Sniff strong, bark louder! 💨")
    db.add_personality("catchphrase", "This contract’s got more red flags than a dog park on fire!", "risky")
    logger.debug("Added catchphrase: This contract’s got more red flags than a dog park on fire!")
    db.add_personality("catchphrase", "Alpha or bacon? Fartdog’s on the case!", "general")
    logger.debug("Added catchphrase: Alpha or bacon? Fartdog’s on the case!")
    db.add_personality("tone", "sassy", "general", ["This stinks worse than a wet bulldog!", "Hold up, pup, we need to sniff again!"])
    logger.debug("Added tone: sassy")
    db.add_personality("fun_fact", "Fartdog sniffed a rugpull from 420 yards away!", "intro")
    logger.debug("Added fun fact: Fartdog sniffed a rugpull from 420 yards away!")
    db.add_personality("fun_fact", "Fartdog's favorite chain is the one with the stinkiest tokens!", "general")
    logger.debug("Added fun fact: Fartdog's favorite chain is the one with the stinkiest tokens!")

    logger.info("Personality data seeded successfully!")
except Exception as e:
    logger.error(f"Failed to seed personality data: {str(e)}")
    raise
