import streamlit as st
from graph import graph

st.title("📘 AI Memoir Co-Writer")

# Initialize session state
if "graph_state" not in st.session_state:
    st.session_state.graph_state = {
        "step": 0,
        "user_inputs": [],
        "rewritten": [],
        "current_question": "Click Submit to begin."
    }

# Display current question
st.subheader("Question")
st.write(st.session_state.graph_state.get("current_question", ""))

# Input form
with st.form(key="memoir_form"):
    user_input = st.text_area("Your answer", height=150)
    submit = st.form_submit_button("Submit")

if submit and user_input.strip():
    st.session_state.graph_state["current_input"] = user_input.strip()
    result = graph.invoke(dict(st.session_state.graph_state), config={"entry_point": "receive"})
    st.session_state.graph_state.update(result)
    st.rerun()

# Show rewritten so far
if st.session_state.graph_state.get("rewritten"):
    st.subheader("Your Memoir So Far")
    for idx, para in enumerate(st.session_state.graph_state["rewritten"], 1):
        st.markdown(f"**Part {idx}:** {para}")

# Final story output
if "final_story" in st.session_state.graph_state:
    st.subheader("📖 Final Compiled Memoir")
    st.text_area("", st.session_state.graph_state["final_story"], height=300)
    st.download_button("Download Memoir", st.session_state.graph_state["final_story"], file_name="my_memoir.txt")

# Debug info
st.write("🛠 Debug:", st.session_state.graph_state)
