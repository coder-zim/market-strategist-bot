# data_fetcher.py
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

def rank_distribution(top_wallet_percent):
    if top_wallet_percent <= 5:
        return "🟢"
    elif top_wallet_percent <= 15:
        return "🟡"
    return "🔴"

def get_fart_score(chart, holders, lp, dist):
    flags = [chart, holders, dist]
    red_count = flags.count("🔴")
    if red_count >= 2:
        return "🔴 - DO NOT go in there! 🤮"
    elif "🔴" in flags:
        return "🟡 - Silent, but deadly 🐦‍🔥"
    return "🟢 - Smells like Rotten Eggs 😻"

def format_goplus_scores(data):
    if not data:
        return "❓ No contract analysis available."
    owner_percent = float(data.get("owner_percent", 100))
    slippage_mod = data.get("slippage_modifiable", "0")
    buy_tax = float(data.get("buy_tax", 0))
    sell_tax = float(data.get("sell_tax", 0))
    holders = int(data.get("holder_count", 0))

    owner_score = "🟢" if owner_percent <= 5 else "🟡" if owner_percent <= 15 else "🔴"
    tax_score = "🟢" if buy_tax <= 5 and sell_tax <= 5 else "🟡" if buy_tax <= 10 and sell_tax <= 10 else "🔴"
    slip_score = "🔴" if slippage_mod == "1" else "🟢"

    return (
        f"<b>Contract Analysis:</b>\n"
        f"• Owner %: {owner_score} ({owner_percent:.1f}%)\n"
        f"• Buy/Sell Tax: {tax_score} ({buy_tax:.1f}% / {sell_tax:.1f}%)\n"
        f"• Slippage Modifiable: {slip_score}\n"
        f"• Reported Holders: {holders:,}\n"
    )

def fallback_fart_report(pair):
    name = f"{pair['baseToken']['name']} ${pair['baseToken']['symbol']}"
    chart_url = f"https://dexscreener.com/{pair['chainId'].lower()}/{pair['pairAddress']}"
    return (
        f"<b>{name}</b>\n"
        f"📊 Token detected, but some data couldn't be sniffed.\n"
        f"🔗 <a href=\"{chart_url}\">Dexscreener Chart</a>\n"
        "💩 Fartcat couldn't get the full stench... maybe it's hiding something?\n"
        "Try again later or DYOR 👃"
    )

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
            if chain == "solana":
                metadata = moralis.get_sol_token_metadata(address) or {}
                price_data = moralis.get_sol_token_price(address) or {}
                holders_data = moralis.get_sol_token_holders(address) or {}
                name = metadata.get("name", "Unknown")
                symbol = metadata.get("symbol", "???")
                price = price_data.get("price", "N/A")
                holders = len(holders_data.get("result", []))
                holder_score = rank_holders(holders)
                health = "🟡"
                dist_score = "🟡"
                fart_score = get_fart_score(health, holder_score, "🟡", dist_score)
                chart_url = f"https://birdeye.so/token/{address}?chain=solana"
                summary = get_anthropic_summary(address, chain) if CONFIG["ANTHROPIC_API_KEY"] else "No hot take today, catnip ran out!"
                result = (
                    f"<b>Contract:</b>\n<code>{address}</code>\n\n"
                    f"<b>{name} ${symbol}</b>\n"
                    f"<b>Price:</b> ${price}\n\n"
                    f"<b>FART REPORT 💨</b>\n"
                    f"Chart Health: {health}\n"
                    f"Holders: {holder_score} ({holders:,})\n"
                    f"Distribution: {dist_score}\n"
                    f"Fart-Score: {fart_score}\n"
                    f"Link: <a href=\"{chart_url}\">Birdeye</a>\n\n"
                    f"<b>🐾 {CONFIG['BOT_NAME']}'s Hot Take:</b>\n{summary}\n\n"
                    f"😹 Might be alpha, might be catnip!"
                )
                self.db.save_contract_data(address, chain, result)
                return result

            url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}/{address}"
            res = requests.get(url, timeout=10)
            data = res.json()
            pair = data.get("pair")
            if not pair:
                search_url = f"https://api.dexscreener.com/latest/dex/search/?q={address}"
                search_res = requests.get(search_url, timeout=10)
                data = search_res.json()
                pairs = data.get("pairs", [])
                pair = next((p for p in pairs if p["chainId"].lower() == chain.lower()), pairs[0] if pairs else None)
                if not pair:
                    result = fallback_fart_report(data.get("pairs", [{}])[0]) if data.get("pairs") else "❌ Token not found on Dexscreener."
                    self.db.save_contract_data(address, chain, result)
                    return result   

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
            chart_chain = pair.get("chainId", chain).lower()
            chart_url = f"https://dexscreener.com/{chart_chain}/{address}"
            health = rank_chart_health(liquidity_val, volume_val, fdv_val)
            dist_score = rank_distribution(float(pair.get("topHolderPercent", 100)))
            fart_score = get_fart_score(health, "🟡", lp_locked, dist_score)
            goplus_data, _ = fetch_goplus_risk(chain, address)
            goplus_report = format_goplus_scores(goplus_data)
            summary = get_anthropic_summary(address, chain) if CONFIG["ANTHROPIC_API_KEY"] else "No hot take today, catnip ran out!"
            catchphrase = self.db.get_personality("catchphrase", "risky" if fart_score.startswith("🔴") else "general")
            catchphrase_text = catchphrase["value"] if catchphrase else "Might be alpha, might be catnip!"

            result = (
                f"<b>Contract:</b>\n<code>{address}</code>\n\n"
                f"<b>{name}</b>\n"
                f"<b>Price:</b> ${price}\n"
                f"<b>Volume:</b> {volume} | <b>Liquidity:</b> {liquidity} | <b>LP:</b> {lp_locked}\n"
                f"<b>FDV:</b> {fdv}\n\n"
                f"<b>FART REPORT 💨</b>\n"
                f"Chart Health: {health}\n"
                f"Distribution: {dist_score}\n"
                f"Fart-Score: {fart_score}\n"
                f"{goplus_report}\n"
                f"Link: <a href=\"{chart_url}\">Dexscreener</a>\n\n"
                f"<b>🐾 {CONFIG['BOT_NAME']}'s Hot Take:</b>\n{summary}\n\n"
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
        return {"summary": f"{result}\n\n😹 {catchphrase_text}"}
