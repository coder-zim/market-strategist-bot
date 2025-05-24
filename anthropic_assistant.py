#anthropic_assistant.py
import os
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def get_anthropic_summary(address, chain):
    try:
        prompt = f"You're a witty blockchain watchdog. Give a short, humorous one-liner about this contract on {chain.title()}: {address}. Take the role of a talking dog who has a reputation for farting as a super power.  Make humor about this and be original and only give a response that is 1 or 2 sentences long."
        msg = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=50,
            temperature=0.8,
            system="You are Fartdog, a crypto watchdog with a nose for risk and a bark full of sass.",
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text
    except Exception as e:
        return f"No data found, and Anthropic failed: {str(e)}"