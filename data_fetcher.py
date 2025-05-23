# data_fetcher.py
import logging
import requests
from fart_report import generate_full_fart_report
from database import Database
from config import CONFIG

logger = logging.getLogger(__name__)

class DataFetcher:
    def __init__(self):
        self.db = Database()
        self.name = CONFIG["BOT_NAME"]

    def guess_chain(self, address):
        if address.startswith("0x") and len(address) == 42:
            return "ethereum"
        if len(address) == 44 and not address.startswith("0x"):
            return "solana"
        if len(address) == 66 and address.startswith("0x"):
            return "base"
        if len(address) == 66 and not address.startswith("0x"):
            return "sui"
        if address.startswith("0x") and len(address) == 40:
            return "abstract"
        return None

    def fetch_basic_info(self, address, chain):
        cached = self.db.get_contract_data(address, chain)
        if cached and "data" in cached:
            logger.info(f"Using cached data for {address} on {chain}")
            return cached["data"]

        try:
            report = generate_full_fart_report(address, chain)
            self.db.save_contract_data(address, chain, report)
            return report
        except Exception as e:
            logger.exception("❌ Error in fetch_basic_info")
            result = f"⚠️ Failed to fetch token info: {e}"
            self.db.save_contract_data(address, chain, result)
            return result

    def process(self, question, chain):
        result = self.fetch_basic_info(question, chain)
        result = result.replace("<b>", "").replace("</b>", "").replace("<code>", "`").replace("</code>", "`")
        catchphrase = self.db.get_personality("catchphrase", "general")
        catchphrase_text = catchphrase["value"] if catchphrase else "Might be alpha, might be catnip!"
        result = f"{result}\n\n😹 {catchphrase_text}"
        return {"summary": result}