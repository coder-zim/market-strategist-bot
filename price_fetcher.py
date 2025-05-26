# price_fetcher.py
import requests
from config import CONFIG
from chain_fallback import fallback_fetch

def parse_data(data, fallback=False):
    fart_note = data.get("fart_note", "") if fallback else ""
    return {
        "name": data.get("baseToken", {}).get("symbol", "Unknown") if not fallback else data.get("name", "Unknown"),
        "price": data.get("priceUsd", "Unknown") if not fallback else data.get("price", "0"),
        "volume": data.get("volume", {}).get("h24", "Unknown") if not fallback else data.get("volume", "0"),
        "liquidity": data.get("liquidity", {}).get("usd", "Unknown") if not fallback else data.get("liquidity", "0"),
        "fdv": data.get("fdv", "Unknown") if not fallback else data.get("fdv", "0"),
        "holders": data.get("holders", "Unknown") if fallback else "N/A",
        "lp_burned": "🔥" if not fallback and data.get("liquidity", {}).get("locked") else data.get("lp_burned", "💀"),
        "dex_link": f"https://dexscreener.com/{data.get('chainId')}/{data.get('pairAddress')}" if not fallback else data.get("dex_link", ""),
        "fart_note": fart_note
    }


def fetch_token_data(chain, contract):
    headers = CONFIG.get("DEFAULT_HEADERS", {})

    try:
        search_url = f"https://api.dexscreener.com/latest/dex/search/?q={contract}"
        r = requests.get(search_url, headers=headers)
        if r.status_code == 200:
            pairs = r.json().get("pairs", [])
            if pairs:
                filtered = [p for p in pairs if p.get("chainId") == chain]
                if filtered:
                    best = max(filtered, key=lambda x: x.get("liquidity", {}).get("usd", 0) or 0)
                    return parse_data(best)
                else:
                    best = max(pairs, key=lambda x: x.get("liquidity", {}).get("usd", 0) or 0)
                    return parse_data(best, fallback=True)
    except Exception as e:
        print("Dexscreener error:", e)

    # Fallback to chain API
    print(f"Dexscreener failed. Falling back to chain API for {chain}:{contract}")
    fallback_data = fallback_fetch(chain, contract)
    if fallback_data:
        return parse_data(fallback_data, fallback=True)

    return None
