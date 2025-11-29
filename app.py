import utils.compat
import streamlit as st
import os
from graph import graph, ask_node
from agent import memoir_agent  # ✅ Import the LangChain Agent

os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("📘 AI Memoir Co-Writer")

# 🔒 Hide GitHub icon, menu, and footer
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ✅ Initialize session state only once
if "graph_state" not in st.session_state:
    st.session_state.graph_state = {
        "step": 0,
        "user_inputs": [],
        "rewritten": [],
        "current_input": "",
        "current_question": None,
        "final_story": None
    }

# ✅ Only call 'ask' once if no question has been asked — safely
if st.session_state.graph_state["step"] == 0 and not st.session_state.graph_state["current_question"]:
    st.session_state.graph_state = ask_node(dict(st.session_state.graph_state))

# 🧠 Display current question
st.subheader("Reflective Question")
st.write(st.session_state.graph_state.get("current_question", ""))

# 📝 User input form
with st.form(key="memoir_form"):
    user_input = st.text_area("Your memory or experience", height=150)
    submit = st.form_submit_button("Submit")

# ➕ On Submit
if submit:
    user_input = user_input.strip()
    if user_input:
        st.session_state.graph_state["current_input"] = user_input
        result = graph.invoke(dict(st.session_state.graph_state), config={"entry_point": "receive"})
        st.session_state.graph_state.update(result)
        st.rerun()
    else:
        st.warning("⚠️ Please write your memory before clicking Submit.")

# ✨ Display rewritten parts
if st.session_state.graph_state.get("rewritten"):
    st.subheader("Your Memoir So Far")
    for idx, para in enumerate(st.session_state.graph_state["rewritten"], 1):
        st.markdown(f"**Part {idx}:** {para}")

# 📖 Final Memoir
if st.session_state.graph_state.get("final_story"):
    st.subheader("📖 Final Compiled Memoir")
    st.text_area("Your Memoir", st.session_state.graph_state["final_story"], height=300)
    st.download_button("📥 Download Memoir", st.session_state.graph_state["final_story"], file_name="my_memoir.txt")

# 🤖 LangChain Agent Assistant Section
st.markdown("---")
st.subheader("🧠 Talk to the Memoir Coach Agent")
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

agent_input = st.chat_input("Ask the memoir coach a question...")

if agent_input:
    st.session_state.chat_history.append({"role": "user", "content": agent_input})
    with st.chat_message("user"):
        st.markdown(agent_input)

    with st.chat_message("assistant"):
        with st.spinner("Memoir coach thinking..."):
            agent_response = memoir_agent.run(agent_input)
            st.markdown(agent_response)

    st.session_state.chat_history.append({"role": "assistant", "content": agent_response})
