# data_fetcher.py
import logging
import requests
import random
from guardrails import (
    fetch_goplus_risk,
    calculate_risk_score,
    fetch_bubblemaps_info,
    compose_fart_report
)
from database import Database
from anthropic_assistant import get_anthropic_summary
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
            url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}/{address}"
            res = requests.get(url, timeout=10)
            data = res.json()
            pair = data.get("pair")

            if not pair:
                logger.info(f"\U0001F4E6 Dexscreener raw response for {chain} / {address}: {data}")
                search_url = f"https://api.dexscreener.com/latest/dex/search/?q={address}"
                search_res = requests.get(search_url, timeout=10)
                data = search_res.json()
                logger.info(f"\U0001F50D Dexscreener fallback search for {address}: {data}")
                pairs = data.get("pairs", [])
                pair = next((p for p in pairs if p["chainId"].lower() == chain.lower()), pairs[0] if pairs else None)

            if not pair:
                result = "\u274c Token not found on Dexscreener."
                self.db.save_contract_data(address, chain, result)
                return result

            name = f"{pair['baseToken']['name']} ${pair['baseToken']['symbol']}"
            price = pair.get("priceUsd", "N/A")
            liquidity_val = pair.get('liquidity', {}).get('usd', 0)
            volume_val = pair.get('volume', {}).get('h24', 0)
            liquidity = f"${int(liquidity_val):,}"
            volume = f"${int(volume_val):,}"
            fdv = f"${int(pair.get('fdv') or pair.get('marketCap', 0)):,}"
            lp_raw = pair.get("liquidityLocked")
            lp_locked = "🔥" if lp_raw is True else "☠️"

            age_obj = pair.get("age") or {}
            age_days = age_obj.get("days", 0)
            age_str = age_obj.get("human", f"{age_days}d")
            age_score = "🟢" if age_days > 30 else "🟡" if age_days >= 7 else "🔴"

            holders = int(pair.get("holders") or 0)
            holder_score = "🟢" if holders >= 1000 else "🟡" if holders >= 500 else "🔴"

            chart_chain = pair.get("chainId", chain).lower()
            chart_url = f"https://dexscreener.com/{chart_chain}/{address}"

            health = "🟢" if liquidity_val >= 10000 and volume_val >= 10000 else "🟡" if liquidity_val >= 2000 and volume_val >= 2000 else "🔴"
            launch = "🟢" if "pump.fun" in pair.get("url", "").lower() or age_days > 1 else "🔴"

            goplus_data, _ = fetch_goplus_risk(chain, address)
            goplus_score, goplus_flags = calculate_risk_score(goplus_data, chain, address)
            bubble_link, _ = fetch_bubblemaps_info(address)
            fart_report = compose_fart_report(address, chain, goplus_data, goplus_score, goplus_flags, None, bubble_link, chart_url)

            anthropic_summary = get_anthropic_summary(address, chain) if CONFIG["ANTHROPIC_API_KEY"] else "No hot take today, catnip ran out!"
            catchphrase = self.db.get_personality("catchphrase", "risky" if goplus_score <= 1 else "general")
            catchphrase_text = catchphrase["value"] if catchphrase else "Might be alpha, might be catnip!"

            result = (
                f"<b>Contract:</b>\n<code>{address}</code>\n\n"
                f"<b>{name}</b>\n"
                f"<b>Price:</b> ${price}\n"
                f"<b>Volume:</b> {volume} | <b>Liquidity:</b> {liquidity} | <b>LP:</b> {lp_locked}\n"
                f"<b>FDV:</b> {fdv}\n\n"
                f"<b>FART REPORT 💨</b>\n"
                f"Launch: {launch}\n"
                f"Chart Health: {health}\n"
                f"Holders: {holder_score} ({holders:,})\n"
                f"Risk Analysis: See below\n"
                f"LP: {lp_locked}\n"
                f"Age: {age_score} ({age_str})\n\n"
                f"{fart_report}\n\n"
                f"<b>🐾 {CONFIG['BOT_NAME']}'s Hot Take:</b>\n{anthropic_summary}\n\n"
                f"😹 {catchphrase_text}"
            )

            self.db.save_contract_data(address, chain, result)
            return result

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
