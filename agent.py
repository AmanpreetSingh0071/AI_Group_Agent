from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from tools.memoir_rewrite import rewrite_memoir_text
from tools.memoir_compile import compile_memoir
from tools.memoir_questions import ask_reflective_question
from langchain.agents import Tool
import os
from dotenv import load_dotenv

load_dotenv()

# ✅ Groq-compatible OpenAI client for LangChain
llm = ChatOpenAI(
    model_name="llama3-8b-8192",
    openai_api_base="https://api.groq.com/openai/v1",
    openai_api_key=os.getenv("GROQ_API_KEY"),
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
memoir_agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)