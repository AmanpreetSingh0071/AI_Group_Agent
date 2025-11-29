from langchain.agents import initialize_agent, AgentType
from langchain_groq import ChatGroq
from tools.memoir_rewrite import rewrite_memoir_text
from tools.memoir_compile import compile_memoir
from tools.memoir_questions import ask_reflective_question

# --- Robust Tool import fallback ---
try:
    from langchain.tools import Tool
except Exception:
    try:
        from langchain.agents import Tool
    except Exception:
        from dataclasses import dataclass
        from typing import Any, Callable, Optional

        @dataclass
        class Tool:
            name: str
            func: Callable[..., Any]
            description: Optional[str] = None

            def __call__(self, *args, **kwargs) -> Any:
                return self.func(*args, **kwargs)
# -----------------------------------

import os
import streamlit as st

os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

# ✅ Groq-compatible OpenAI client for LangChain
llm = ChatGroq(
    model_name="llama3-8b-8192",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7
)

# ✅ Define tools with LangChain-compatible Tool wrappers
tools = [
    Tool(
        name="Ask Reflective Question",
        func=lambda x: ask_reflective_question.invoke({"index": int(x)}),
        description="Asks a reflective question by index. Input must be an integer index."
    ),
    Tool(
        name="Rewrite Memoir",
        func=lambda x: rewrite_memoir_text.invoke(x),
        description="Rewrite a user's input into a vivid memoir paragraph."
    ),
    Tool(
        name="Compile Memoir",
        func=lambda x: compile_memoir.invoke({"rewritten": [x] if isinstance(x, str) else x}),
        description="Compile a list of rewritten memoir paragraphs into a final story. Input must be a list of strings."
    )
]

# ✅ Initialize agent
# ===== Initialize agent (robust to differing langchain signatures) =====
try:
    # Preferred: pass agent type if supported (older langchain)
    memoir_agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
    )
except TypeError as e:
    # Some langchain versions (create_agent/create_react_agent) don't accept `agent` kw.
    # Fall back to calling initialize_agent with a simpler signature.
    # Try to preserve kwargs where possible.
    try:
        memoir_agent = initialize_agent(tools, llm, verbose=True, handle_parsing_errors=True)
    except TypeError:
        # Last-resort: try positional call (tools, llm)
        memoir_agent = initialize_agent(tools, llm)
# =========================================================================