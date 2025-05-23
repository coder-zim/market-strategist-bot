# guardrails.py
import os
import requests
import logging
from dotenv import load_dotenv
load_dotenv()
import hashlib
import time
from config import CONFIG

logger = logging.getLogger(__name__)

_cached_token = None
_token_expiry = 0

GOPLUS_BASE_URL = os.getenv("GOPLUS_BASE_URL", "https://api.gopluslabs.io/api/v1/token_security")
TOKEN_SNIFFER_BASE = "https://tokensniffer.com/token"
LUNARCRUSH_BASE = "https://api.lunarcrush.com/v2"
BUBBLEMAPS_PLACEHOLDER = "https://app.bubblemaps.io"


def get_goplus_token():
    global _cached_token, _token_expiry
    if _cached_token and time.time() < _token_expiry:
        return _cached_token

    try:
        app_key = CONFIG["GOPLUS_APP_KEY"]
        app_secret = CONFIG["GOPLUS_APP_SECRET"]
        ts = int(time.time())
        sign_input = f"{app_key}{ts}{app_secret}"
        sign = hashlib.sha1(sign_input.encode("utf-8")).hexdigest()

        payload = {
            "app_key": app_key,
            "sign": sign,
            "time": ts
        }

        res = requests.post("https://api.gopluslabs.io/api/v1/token", json=payload)
        token = res.json().get("data", {}).get("token")
        if token:
            _cached_token = token
            _token_expiry = time.time() + 3600
            return token
        else:
            logger.warning(f"Failed to retrieve GoPlus token: {res.text}")
            return None
    except Exception as e:
        logger.error(f"Error fetching GoPlus token: {e}")
        return None


def fetch_goplus_risk(chain, address):
    try:
        if chain.lower() in ["solana", "sui"]:
            logger.info(f"Skipping GoPlus for unsupported chain: {chain}")
            return None, f"GoPlus not available for {chain}"

        chain_map = {"ethereum": "1", "base": "8453", "abstract": "1"}
        chain_id = chain_map.get(chain.lower())
        if not chain_id:
            return None, f"Unsupported chain: {chain}"

        token = get_goplus_token()
        if not token:
            return None, "Unable to retrieve GoPlus token"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {token}"
        }

        url = f"https://api.gopluslabs.io/api/v1/token_security/{chain_id}?contract_addresses={address}"
        res = requests.get(url, headers=headers, timeout=10)
        logger.debug(f"GoPlus Response ({chain} - {address}): {res.text}")
        if not res.ok:
            return None, "API error"

        json_data = res.json()
        data = json_data.get("result", {}).get(address.lower())
        return data, None if data else (None, "No GoPlus data")
    except Exception as e:
        logger.exception("Exception during fetch_goplus_risk")
        return None, str(e)


def calculate_risk_score(goplus_data, chain, address):
    score = 3
    flags = []
    if not goplus_data:
        return 0, ["No GoPlus data"]
    if goplus_data.get("is_open_source") == "0":
        score -= 1
        flags.append("Not Open Source")
    if goplus_data.get("is_honeypot") == "1":
        score -= 1
        flags.append("Honeypot Risk")
    if goplus_data.get("can_take_back_ownership") == "1":
        score -= 1
        flags.append("Can Reclaim Ownership")
    return max(score, 0), flags


def fetch_token_sniffer_score(chain, address):
    if chain.lower() not in ["ethereum", "base"]:
        return None, "TokenSniffer supports only Ethereum and Base"
    try:
        url = f"https://api.tokensniffer.com/v1/token/{chain.lower()}/{address}"
        res = requests.get(url, timeout=10)
        if not res.ok:
            return None, "TokenSniffer fetch failed"
        data = res.json()
        score = data.get("score", 0)
        flags = data.get("indicators", [])
        return {"score": score, "flags": flags}, None
    except Exception as e:
        return None, str(e)


def fetch_lunarcrush_info(address):
    try:
        return {"engagement": "unknown", "rank": "unknown"}, None
    except Exception as e:
        return None, str(e)


def fetch_bubblemaps_info(address):
    try:
        return f"{BUBBLEMAPS_PLACEHOLDER}?token={address}", None
    except Exception as e:
        return None, str(e)


def generate_risk_summary(score, flags):
    if score == 3:
        return "✅ No major red flags. Smart contract appears healthy."
    if score == 2:
        return f"⚠️ Minor concerns: {', '.join(flags)}"
    if score == 1:
        return f"🚨 Risky contract: {', '.join(flags)}"
    return f"💀 Extremely risky: {', '.join(flags)}"


def compose_fart_report(address, chain, goplus, goplus_score, goplus_flags, sniff_data, bubble_link, chart_url):
    goplus_summary = generate_risk_summary(goplus_score, goplus_flags)
    sniffer_summary = ""
    if sniff_data:
        sniffer_summary = f"\n🧪 TokenSniffer Score: {sniff_data.get('score', 'N/A')}\n"
        indicators = sniff_data.get("flags", [])
        if indicators:
            sniffer_summary += f"🚩 Flags: {', '.join(indicators)}"

    report = f"""
<b>🔬 Fartcat Security Check</b>

<b>Risk Summary:</b>
{goplus_summary}

{sniffer_summary}

<b>🧠 More Tools:</b>
• <a href="{chart_url}">Dexscreener Chart</a>
• <a href="{TOKEN_SNIFFER_BASE}/{chain}/{address}">TokenSniffer</a>
• <a href="{bubble_link}">Bubblemaps</a>
"""
    return report.strip()
