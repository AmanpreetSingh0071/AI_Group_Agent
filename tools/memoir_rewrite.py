from langchain_core.tools import tool
from groq import Groq
import os

client = Groq(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

@tool
def rewrite_memoir_text(entry: str) -> str:
    """Rewrite a memory input as vivid memoir prose using Groq."""
    try:
        prompt = f"Rewrite this personal experience as an emotional and vivid memoir in 3–4 sentences:\n\n{entry}"
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=256
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return f"(fallback) {entry}"