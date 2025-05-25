# tools.py

from typing import List
from langchain_core.tools import tool
from transformers import pipeline

generator = pipeline("text2text-generation", model="declare-lab/flan-alpaca-large")

QUESTIONS = [
    "Tell me about a moment in your life that made you feel proud.",
    "Describe a challenge you faced and how you overcame it.",
    "What’s a memory that still makes you smile today?",
    "Who is someone that deeply impacted your life?",
    "What advice would you give to your younger self?"
]

@tool
def ask_reflective_question(index: int) -> str:
    """Get a reflective question by index."""
    if 0 <= index < len(QUESTIONS):
        return QUESTIONS[index]
    return "Thank you for sharing your memories."

@tool
def rewrite_memoir_text(entry: str) -> str:
    """Rewrite a memory input as vivid memoir prose."""
    try:
        prompt = f"Rewrite this personal experience as an emotional and vivid memoir in 3–4 sentences:\n\n{entry}"
        result = generator(prompt, max_new_tokens=256, do_sample=False)
        return result[0]["generated_text"]
    except Exception as e:
        return f"(fallback) {entry}"

@tool
def compile_memoir(rewritten: List[str]) -> str:
    """Compile a list of rewritten memoir paragraphs into one story."""
    return "\n\n".join(rewritten)