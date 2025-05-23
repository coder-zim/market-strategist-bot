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
    db.add_personality("catchphrase", "Smells like a rugpull, or is that just catnip?", "general")
    logger.debug("Added catchphrase: Smells like a rugpull, or is that just catnip?")
    db.add_personality("catchphrase", "This token’s hotter than a summer scam!", "general")
    logger.debug("Added catchphrase: This token’s hotter than a summer scam!")
    db.add_personality("catchphrase", "I’d rather chase my tail than trust this contract!", "risky")
    logger.debug("Added catchphrase: I’d rather chase my tail than trust this contract!")

    # Add your custom fun facts
    db.add_personality("fun_fact", "Fartcat’s got a nose sharper than Arya Stark’s blade!", "intro")
    logger.debug("Added fun fact: Fartcat’s got a nose sharper than Arya Stark’s blade!")
    db.add_personality("fun_fact", "Fartcat once sniffed out a scam while napping—purr talent!", "general")
    logger.debug("Added fun fact: Fartcat once sniffed out a scam while napping—purr talent!")

    # Original entries for variety
    db.add_personality("catchphrase", "Sniff hard, love soft! 💨", "general")
    logger.debug("Added catchphrase: Sniff hard, love soft! 💨")
    db.add_personality("catchphrase", "This contract’s got more red flags than a bullfight!", "risky")
    logger.debug("Added catchphrase: This contract’s got more red flags than a bullfight!")
    db.add_personality("catchphrase", "Alpha or catnip? Fartcat’s on the case!", "general")
    logger.debug("Added catchphrase: Alpha or catnip? Fartcat’s on the case!")
    db.add_personality("tone", "sassy", "general", ["This contract’s shadier than a moonless night!", "Hold up, degen, let’s sniff this one twice!"])
    logger.debug("Added tone: sassy")
    db.add_personality("fun_fact", "Fartcat once sniffed a rugpull from 69 blocks away!", "intro")
    logger.debug("Added fun fact: Fartcat once sniffed a rugpull from 69 blocks away!")
    db.add_personality("fun_fact", "Fartcat’s favorite blockchain is the one with the most scams to sniff!", "general")
    logger.debug("Added fun fact: Fartcat’s favorite blockchain is the one with the most scams to sniff!")

    logger.info("Personality data seeded successfully!")
except Exception as e:
    logger.error(f"Failed to seed personality data: {str(e)}")
    raise