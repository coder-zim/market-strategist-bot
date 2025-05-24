#data_fetcher.py
import logging
import requests
from database import Database
from anthropic_assistant import get_anthropic_summary
from config import CONFIG
from moralis_fetcher import MoralisFetcher

logger = logging.getLogger(__name__)
moralis = MoralisFetcher()

def fetch_goplus_risk(chain, address):
    try:
        if chain.lower() in ["solana", "sui"]:
            return None, f"GoPlus not available for {chain}"
        chain_map = {"ethereum": "1", "base": "8453", "abstract": "1"}
        chain_id = chain_map.get(chain.lower())
        if not chain_id:
            return None, f"Unsupported chain: {chain}"
        token = CONFIG["GOPLUS_APP_KEY"]
        url = f"https://api.gopluslabs.io/api/v1/token_security/{chain_id}?contract_addresses={address}"
        headers = {"accept": "application/json"}
        res = requests.get(url, headers=headers, timeout=10)
        if not res.ok:
            return None, "API error"
        json_data = res.json()
        data = json_data.get("result", {}).get(address.lower())
        return data, None if data else (None, "No GoPlus data")
    except Exception as e:
        return None, str(e)

def rank_chart_health(liquidity, volume, fdv):
    score = 0
    if liquidity >= 50000:
        score += 1
    if volume >= 25000:
        score += 1
    if fdv <= 10_000_000:
        score += 1
    if score == 3:
        return "🟢"
    elif score == 2:
        return "🟡"
    return "🔴"

def rank_holders(count):
    if count >= 1000:
        return "🟢"
    elif count >= 500:
        return "🟡"
    return "🔴"

def rank_lp_status(is_burned):
    return "🔥" if is_burned else "☠️"

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
        logger.warning(f"FETCH STARTED FOR: {chain} - {address}")
        cached = self.db.get_contract_data(address, chain)
        if cached and "data" in cached:
            logger.info(f"Using cached data for {address} on {chain}")
            return cached["data"]

        try:
            # Step 1: Search first to get correct pairAddress
            search_url = f"https://api.dexscreener.com/latest/dex/search/?q={address}"
            res = requests.get(search_url, timeout=10)
            data = res.json()
            pairs = data.get("pairs", [])
            pair = None
            for p in pairs:
                if address.lower() in (p.get("pairAddress", "").lower(), p.get("baseToken", {}).get("address", "").lower()):
                    pair = p
                    break

            if not pair:
                return "❌ Token not found on Dexscreener."

            pair_address = pair["pairAddress"]
            chart_chain = pair.get("chainId", chain).lower()
            url = f"https://api.dexscreener.com/latest/dex/pairs/{chart_chain}/{pair_address}"
            res = requests.get(url, timeout=10)
            data = res.json()
            pair = data.get("pair")

            if not pair:
                return "❌ Token not found on Dexscreener."

            name = f"{pair['baseToken']['name']} ${pair['baseToken']['symbol']}"
            price = pair.get("priceUsd", "N/A")
            liquidity_val = pair.get('liquidity', {}).get('usd', 0)
            volume_val = pair.get('volume', {}).get('h24', 0)
            fdv_val = int(pair.get('fdv') or pair.get('marketCap', 0))
            liquidity = f"${int(liquidity_val):,}"
            volume = f"${int(volume_val):,}"
            fdv = f"${fdv_val:,}"
            lp_raw = pair.get("liquidityLocked")
            lp_locked = rank_lp_status(lp_raw is True)
            chart_url = f"https://dexscreener.com/{chart_chain}/{pair_address}"

            health = rank_chart_health(liquidity_val, volume_val, fdv_val)
            holders = 0
            holder_score = rank_holders(holders)

            goplus_data, _ = fetch_goplus_risk(chain, address)
            risk_summary = "💀 Extremely risky: No GoPlus data" if not goplus_data else "🔒 Risk data present"

            short_summary = get_anthropic_summary(address, chain)[:200]
            catchphrase = self.db.get_personality("catchphrase", "general")
            catchphrase_text = catchphrase["value"] if catchphrase else "Might be alpha, might be dognip!"

            result = (
                f"<b>Contract:</b>\n<code>{address}</code>\n\n"
                f"<b>{name}</b>\n"
                f"<b>Price:</b> ${price}\n"
                f"<b>Volume:</b> {volume} | <b>Liquidity:</b> {liquidity} | <b>LP:</b> {lp_locked}\n"
                f"<b>FDV:</b> {fdv}\n\n"
                f"<b>FART REPORT 💨</b>\n"
                f"Chart Health: {health}\n"
                f"Holders: {holder_score} ({holders})\n"
                f"Risk Analysis: See below\n"
                f"LP: {lp_locked}\n"
                f"Age: 🔴 (0d)\n\n"
                f"<b>🔬 Fartdog Security Check</b>\n\n"
                f"Risk Summary:\n{risk_summary}\n\n"
                f"🧠 More Tools:\n"
                f"• Dexscreener Chart ({chart_url})\n"
                f"• TokenSniffer (https://tokensniffer.com/token/{chain}/{address})\n"
                f"• Bubblemaps (https://app.bubblemaps.io/?token={address})\n\n"
                f"🐾 Fartdog's Hot Take:\n{short_summary}\n\n"
                f"😹 {catchphrase_text}"
            )

            self.db.save_contract_data(address, chain, result)
            return result
        except Exception as e:
            logger.exception("❌ Error in fetch_basic_info")
            return f"⚠️ Failed to fetch token info: {e}"

    def process(self, question, chain):
        result = self.fetch_basic_info(question, chain)
        result = result.replace("<b>", "").replace("</b>", "").replace("<code>", "`").replace("</code>", "`")
        catchphrase = self.db.get_personality("catchphrase", "general")
        catchphrase_text = catchphrase["value"] if catchphrase else "Might be alpha, might be dognip!"
        return {"summary": f"{result} 🐶 {catchphrase_text}"}
