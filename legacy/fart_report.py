# fart_report.py
from legacy.guardrails import fetch_goplus_risk, calculate_risk_score, fetch_bubblemaps_info, generate_risk_summary
from moralis_fetcher import get_token_holders_evm, get_token_holder_stats_solana
from config import CONFIG
import requests


def compose_fart_report(address, chain):
    # Determine chart URL
    chart_url = f"https://dexscreener.com/{chain}/{address}"

    # GoPlus Risk
    goplus_data, _ = fetch_goplus_risk(chain, address)
    goplus_score, goplus_flags = calculate_risk_score(goplus_data, chain, address)
    goplus_summary = generate_risk_summary(goplus_score, goplus_flags)

    # Bubblemaps Link
    bubble_link, _ = fetch_bubblemaps_info(address)

    # LP Status (naive fallback)
    lp_locked = "☠️"
    if goplus_data and goplus_data.get("holders"):
        try:
            lp_data = goplus_data.get("lp_holders", [])
            for lp in lp_data:
                if lp.get("tag", "").lower() in ["burn address", "dead address"]:
                    lp_locked = "🔥"
                    break
        except:
            pass

    # Holders
    holder_score = "🔴"
    holder_count = 0
    if chain == "solana":
        sol_holder_data, _ = get_token_holder_stats_solana(address)
        holder_count = sol_holder_data.get("numberOfHolders", 0) if sol_holder_data else 0
    else:
        evm_holder_data, _ = get_token_holders_evm(address, chain)
        holder_count = evm_holder_data.get("total", 0) if evm_holder_data else 0

    if holder_count >= 1000:
        holder_score = "🟢"
    elif holder_count >= 500:
        holder_score = "🟡"

    # Fart Report Block
    report = f"""
<b>🔬 Fartcat Security Check</b>

<b>Risk Summary:</b>
{goplus_summary}

<b>🧠 More Tools:</b>
• <a href="{chart_url}">Dexscreener Chart</a>
• <a href="https://app.bubblemaps.io/?token={address}">Bubblemaps</a>
"""

    extra = {
        "lp_locked": lp_locked,
        "holders": holder_count,
        "holder_score": holder_score,
        "goplus_score": goplus_score,
        "goplus_flags": goplus_flags,
    }

    return report.strip(), extra


def generate_full_fart_report(address, chain):
    # Dexscreener Basic Info
    url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}/{address}"
    res = requests.get(url, timeout=10)
    data = res.json()
    pair = data.get("pair")

    if not pair:
        search_url = f"https://api.dexscreener.com/latest/dex/search/?q={address}"
        res = requests.get(search_url, timeout=10)
        data = res.json()
        pairs = data.get("pairs", [])
        pair = next((p for p in pairs if p["chainId"].lower() == chain.lower()), pairs[0] if pairs else None)

    if not pair:
        return "❌ Token not found on Dexscreener."

    name = f"{pair['baseToken']['name']} ${pair['baseToken']['symbol']}"
    price = pair.get("priceUsd", "N/A")
    liquidity_val = pair.get('liquidity', {}).get('usd', 0)
    volume_val = pair.get('volume', {}).get('h24', 0)
    liquidity = f"${int(liquidity_val):,}"
    volume = f"${int(volume_val):,}"
    fdv = f"${int(pair.get('fdv') or pair.get('marketCap', 0)):,}"

    age_obj = pair.get("age") or {}
    age_days = age_obj.get("days", 0)
    age_str = age_obj.get("human", f"{age_days}d")
    age_score = "🟢" if age_days > 30 else "🟡" if age_days >= 7 else "🔴"

    launch = "🟢" if "pump.fun" in pair.get("url", "").lower() or age_days > 1 else "🔴"
    health = "🟢" if liquidity_val >= 10000 and volume_val >= 10000 else "🟡" if liquidity_val >= 2000 and volume_val >= 2000 else "🔴"

    chart_chain = pair.get("chainId", chain).lower()
    chart_url = f"https://dexscreener.com/{chart_chain}/{address}"

    report_block, extra = compose_fart_report(address, chain)

    # Anthropic
    from anthropic_assistant import get_anthropic_summary
    lore = get_anthropic_summary(address, chain)

    from database import Database
    db = Database()
    catchphrase = db.get_personality("catchphrase", "risky" if extra['goplus_score'] <= 1 else "general")
    catchphrase_text = catchphrase["value"] if catchphrase else "Might be alpha, might be catnip!"

    result = f"""
<b>Contract:</b>
<code>{address}</code>

<b>{name}</b>
<b>Price:</b> ${price}
<b>Volume:</b> {volume} | <b>Liquidity:</b> {liquidity} | <b>LP:</b> {extra['lp_locked']}
<b>FDV:</b> {fdv}

<b>FART REPORT 💨</b>
Launch: {launch}
Chart Health: {health}
Holders: {extra['holder_score']} ({extra['holders']:,})
Risk Analysis: See below
LP: {extra['lp_locked']}
Age: {age_score} ({age_str})

{report_block}

<b>🐾 {CONFIG['BOT_NAME']}'s Hot Take:</b>
{lore}

😹 {catchphrase_text}
"""
    return result.strip()