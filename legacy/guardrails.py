# guardrails.py
import logging
from config import CONFIG

logger = logging.getLogger(__name__)


def calculate_risk_score(goplus_data):
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


def generate_risk_summary(score, flags):
    if score == 3:
        return "✅ No major red flags. Smart contract appears healthy."
    if score == 2:
        return f"⚠️ Minor concerns: {', '.join(flags)}"
    if score == 1:
        return f"🚨 Risky contract: {', '.join(flags)}"
    return f"💀 Extremely risky: {', '.join(flags)}"


def compose_fart_report(address, chain, goplus_data, goplus_score, goplus_flags, chart_url):
    goplus_summary = generate_risk_summary(goplus_score, goplus_flags)
    report = f"""
<b>🔬 Fartcat Security Check</b>

<b>Risk Summary:</b>
{goplus_summary}

<b>🧠 More Tools:</b>
• <a href=\"{chart_url}\">Dexscreener Chart</a>
    """
    return report.strip()
