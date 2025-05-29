from typing import TypedDict, List, Optional  # ⬅️ ADD THIS
from langgraph.graph import StateGraph, END
from tools import ask_reflective_question, rewrite_memoir_text, compile_memoir

# ⬅️ DEFINE THE EXPECTED STATE STRUCTURE
class MemoirState(TypedDict):
    step: int
    user_inputs: List[str]
    rewritten: List[str]
    current_input: str
    current_question: Optional[str]
    final_story: Optional[str]

def ask_node(state: dict) -> dict:
    step = state.get("step", 0)
    question = ask_reflective_question.invoke({"index": step})
    state["current_question"] = question
    return state

def receive_node(state: dict) -> dict:
    answer = state.get("current_input", "").strip()
    if not answer:
        return state  # Don't process empty input
    state.setdefault("user_inputs", []).append(answer)
    return state

def rewrite_node(state: dict) -> dict:
    inputs = state.get("user_inputs", [])
    if not inputs:
        return state

    last = inputs[-1].strip()
    if not last:
        return state  # Don't rewrite empty input

    rewritten = rewrite_memoir_text.invoke(last)
    state.setdefault("rewritten", []).append(rewritten)
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

# Build the graph
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

# OPTIONAL: Export SVG visualization for poster/report
# Optional Visualization Output
if __name__ == "__main__":
    try:
        gviz = graph.get_graph()
        gviz.draw_svg("memoir_graph.svg")
        print("✅ Saved SVG as memoir_graph.svg")
    except Exception as e:
        print(f"⚠️ Could not save SVG: {e}")