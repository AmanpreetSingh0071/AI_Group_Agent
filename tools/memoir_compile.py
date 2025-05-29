from typing import List
from langchain_core.tools import tool

@tool
def compile_memoir(rewritten: List[str]) -> str:
    """Compile a list of rewritten memoir paragraphs into one story."""
    return "\n\n".join(rewritten)