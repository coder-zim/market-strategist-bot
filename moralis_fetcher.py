# moralis_fetcher.py
import requests
import logging
from config import CONFIG

logger = logging.getLogger(__name__)

MORALIS_API_KEY = CONFIG.get("MORALIS_API_KEY")
MORALIS_EVM_BASE = "https://deep-index.moralis.io/api/v2.2"
MORALIS_SOL_BASE = "https://solana-gateway.moralis.io"

HEADERS = {
    "accept": "application/json",
    "X-API-Key": MORALIS_API_KEY
}

def get_token_price_evm(address, chain="eth"):
    try:
        url = f"{MORALIS_EVM_BASE}/erc20/{address}/price?chain={chain}"
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        return res.json(), None
    except Exception as e:
        logger.error(f"Moralis EVM price fetch failed: {e}")
        return None, str(e)

def get_token_holders_evm(address, chain="eth"):
    try:
        url = f"{MORALIS_EVM_BASE}/erc20/{address}/holders?chain={chain}"
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        return res.json(), None
    except Exception as e:
        logger.error(f"Moralis EVM holders fetch failed: {e}")
        return None, str(e)

def get_token_price_solana(address, network="mainnet"):
    try:
        url = f"{MORALIS_SOL_BASE}/token/{network}/{address}/price"
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        return res.json(), None
    except Exception as e:
        logger.error(f"Moralis Solana price fetch failed: {e}")
        return None, str(e)

def get_token_holder_stats_solana(address):
    try:
        url = f"{MORALIS_SOL_BASE}/token/mainnet/holders/{address}"
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        return res.json(), None
    except Exception as e:
        logger.error(f"Moralis Solana holder stats fetch failed: {e}")
        return None, str(e)
