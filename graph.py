from langgraph.graph import StateGraph, END
from tools import ask_reflective_question, rewrite_memoir_text, compile_memoir

# Use plain dict for compatibility with LangGraph
# LangGraph may strip custom __init__, so MemoirState class won't persist defaults

def ask_node(state: dict) -> dict:
    question = ask_reflective_question.invoke({"index": state.get("step", 0)})
    state["current_question"] = question
    return state

def receive_node(state: dict) -> dict:
    answer = state.get("current_input", "")
    state.setdefault("user_inputs", []).append(answer)
    state["step"] = state.get("step", 0) + 1
    return state

def rewrite_node(state: dict) -> dict:
    inputs = state.get("user_inputs", [])
    if not inputs:
        return state  # Nothing to rewrite

    last = inputs[-1]
    rewritten = rewrite_memoir_text.invoke(last)
    state.setdefault("rewritten", []).append(rewritten)

    # ✅ Increment step here to move to next question
    state["step"] = state.get("step", 0) + 1
    return state

def should_continue(state: dict) -> str:
    if len(state.get("rewritten", [])) >= 5:
        return "compile"
    return "ask"

def compile_node(state: dict) -> dict:
    story = compile_memoir.invoke({"rewritten": state.get("rewritten", [])})
    state["final_story"] = story
    return state

# Build graph using plain dict state
builder = StateGraph(dict)
builder.add_node("ask", ask_node)
builder.add_node("receive", receive_node)
builder.add_node("rewrite", rewrite_node)
builder.add_node("compile", compile_node)

builder.set_entry_point("ask")
builder.add_edge("ask", "receive")
builder.add_edge("receive", "rewrite")
builder.add_conditional_edges("rewrite", should_continue, {
    "ask": "ask",
    "compile": "compile"
})
builder.add_edge("compile", END)

graph = builder.compile()