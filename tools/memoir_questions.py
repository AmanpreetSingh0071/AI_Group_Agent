from langchain_core.tools import tool

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