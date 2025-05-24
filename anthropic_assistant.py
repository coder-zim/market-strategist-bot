import os
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def get_anthropic_summary(address, chain):
    try:
        prompt = f"You're a witty blockchain watchdog. Give a 1 to 2 sentence long, humorous response about this memecoin contract on {chain.title()}: {address}."
        msg = client.messages.create(
            model="claude-3.5-sonnet",
            max_tokens=50,
            temperature=0.8,
            system="You are Fartdog, a crypto watchdog with a nose for risk and a bark full of sass.",
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text
    except Exception as e:
        return f"No data found: Anthropic-ball-drop {str(e)}"