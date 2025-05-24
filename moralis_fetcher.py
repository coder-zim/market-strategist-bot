import requests
from config import CONFIG

MORALIS_API_KEY = CONFIG["MORALIS_API_KEY"]
HEADERS = {
    "accept": "application/json",
    "X-API-Key": MORALIS_API_KEY
}

class MoralisFetcher:
    def __init__(self):
        self.base_url_eth = "https://deep-index.moralis.io/api/v2.2"
        self.base_url_sol = "https://solana-gateway.moralis.io"

    def get_sol_token_metadata(self, address):
        url = f"{self.base_url_sol}/token/mainnet/{address}/metadata"
        res = requests.get(url, headers=HEADERS, timeout=10)
        if not res.ok:
            return None
        return res.json()

    def get_sol_token_price(self, address):
        url = f"{self.base_url_sol}/token/mainnet/{address}/price"
        res = requests.get(url, headers=HEADERS, timeout=10)
        if not res.ok:
            return None
        return res.json()

    def get_sol_token_holders(self, address):
        url = f"{self.base_url_sol}/token/mainnet/holders/{address}"
        res = requests.get(url, headers=HEADERS, timeout=10)
        if not res.ok:
            return None
        return res.json()

    def get_eth_token_holders(self, address):
        url = f"{self.base_url_eth}/erc20/{address}/holders"
        res = requests.get(url, headers=HEADERS, timeout=10)
        if not res.ok:
            return None
        return res.json()

    def get_eth_token_price(self, address):
        url = f"{self.base_url_eth}/erc20/{address}/price"
        res = requests.get(url, headers=HEADERS, timeout=10)
        if not res.ok:
            return None
        return res.json()

    def get_eth_token_metadata(self, address):
        url = f"{self.base_url_eth}/erc20/metadata"
        res = requests.post(url, headers=HEADERS, json={"addresses": [address]}, timeout=10)
        if not res.ok:
            return None
        data = res.json()
        return data[0] if isinstance(data, list) and data else None