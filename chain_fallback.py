# chain_fallback.py
import os
import requests

BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")
BITQUERY_API_KEY = os.getenv("BITQUERY_API_KEY")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
BASESCAN_API_KEY = os.getenv("BASESCAN_API_KEY")
SOLSCAN_API_KEY = os.getenv("SOLSCAN_API_KEY")

HEADERS = {
    "accept": "application/json",
    "User-Agent": "Fartdog/1.0"
}

def fallback_fetch(chain, contract):
    if chain == "solana":
        return fetch_from_birdeye_solana(contract)
    elif chain == "sui":
        return fetch_from_birdeye_sui(contract)
    elif chain == "ethereum":
        return fetch_from_etherscan(contract)
    elif chain == "base":
        return fetch_from_basescan(contract)
    elif chain == "abstract":
        return {"name": "Unknown", "price": "0", "volume": "0", "liquidity": "0", "fdv": "0", "lp_burned": "☠️", "dex_link": "", "fart_note": "🌀 Abstract layer... results may vary."}
    return None

def fetch_from_birdeye_solana(contract):
    try:
        url = f"https://public-api.birdeye.so/public/token/{contract}"
        r = requests.get(url, headers={"X-API-KEY": BIRDEYE_API_KEY})
        data = r.json().get("data", {})
        return {
            "name": data.get("symbol", "Unknown"),
            "price": data.get("value", "0"),
            "volume": data.get("volume24hUsd", "0"),
            "liquidity": data.get("liquidity", "0"),
            "fdv": data.get("marketCap", "0"),
            "holders": data.get("holders", "N/A"),
            "lp_burned": "🔥",  # Assume burned for fallback
            "dex_link": f"https://birdeye.so/token/{contract}?chain=solana",
            "fart_note": "💨 Fetched with Birdeye for Solana"
        }
    except Exception as e:
        print("Birdeye Solana error:", e)
        return None


def fetch_from_birdeye_sui(contract):
    try:
        url = f"https://public-api.birdeye.so/public/token/{contract}?chain=sui"
        r = requests.get(url, headers={"X-API-KEY": BIRDEYE_API_KEY})
        data = r.json().get("data", {})
        return {
            "name": data.get("symbol", "Unknown"),
            "price": data.get("value", "0"),
            "volume": data.get("volume24hUsd", "0"),
            "liquidity": data.get("liquidity", "0"),
            "fdv": data.get("marketCap", "0"),
            "lp_burned": "🔥",
            "dex_link": f"https://birdeye.so/token/{contract}?chain=sui",
            "fart_note": "💨 Fetched with Birdeye for SUI"
        }
    except Exception as e:
        print("Birdeye SUI error:", e)
        return None

def fetch_from_etherscan(contract):
    try:
        url = f"https://api.etherscan.io/api?module=token&action=tokeninfo&contractaddress={contract}&apikey={ETHERSCAN_API_KEY}"
        r = requests.get(url, headers=HEADERS)
        data = r.json().get("result", {})
        deployer = get_deployer_info("ethereum", contract)
        return {
            "name": data.get("symbol", "Unknown"),
            "price": "0",
            "volume": "0",
            "liquidity": "0",
            "fdv": data.get("fully_diluted_market_cap", "0"),
            "lp_burned": "☠️",
            "dex_link": f"https://etherscan.io/token/{contract}",
            "fart_note": f"📦 Fetched with Etherscan | Deployer: {deployer}"
        }
    except Exception as e:
        print("Etherscan error:", e)
        return None

def fetch_from_basescan(contract):
    try:
        url = f"https://api.basescan.org/api?module=token&action=tokeninfo&contractaddress={contract}&apikey={BASESCAN_API_KEY}"
        r = requests.get(url, headers=HEADERS)
        data = r.json().get("result", {})
        deployer = get_deployer_info("base", contract)
        return {
            "name": data.get("symbol", "Unknown"),
            "price": "0",
            "volume": "0",
            "liquidity": "0",
            "fdv": data.get("fully_diluted_market_cap", "0"),
            "lp_burned": "☠️",
            "dex_link": f"https://basescan.org/token/{contract}",
            "fart_note": f"📦 Fetched with Basescan | Deployer: {deployer}"
        }
    except Exception as e:
        print("Basescan error:", e)
        return None

def get_deployer_info(chain, contract):
    try:
        query = {
            "query": """
            query ($network: EthereumNetwork!, $address: String!) {
              ethereum(network: $network) {
                smartContractCalls(
                  smartContractAddress: {is: $address}
                  smartContractMethod: {is: "constructor"}
                ) {
                  caller {
                    address
                  }
                  block {
                    timestamp {
                      time(format: "%Y-%m-%d")
                    }
                  }
                }
              }
            }
            """,
            "variables": {
                "network": chain,
                "address": contract
            }
        }
        r = requests.post("https://graphql.bitquery.io", json=query, headers={"X-API-KEY": BITQUERY_API_KEY})
        result = r.json()
        calls = result.get("data", {}).get("ethereum", {}).get("smartContractCalls", [])
        if calls:
            return f"{calls[0]['caller']['address']} on {calls[0]['block']['timestamp']['time']}"
    except Exception as e:
        print("Bitquery deployer fetch error:", e)
    return "unknown"
