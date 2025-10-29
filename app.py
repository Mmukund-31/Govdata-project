import streamlit as st
from ai_helper import query_with_reasoning

st.set_page_config(
    page_title="Project Samarth - Intelligent Q&A System",
    page_icon="🌾",
    layout="wide",
)

# --- Title ---
st.title("🌾 Project Samarth")
st.markdown(
    """
    ### Intelligent Q&A System over Indian Government Data  
    Ask natural language questions about agriculture, rainfall, and policy trends.  
    _(Powered by Gemini + SQLite + Real Government Data)_
    """
)

# --- Input box ---
user_question = st.text_input(
    "🧠 Ask your question:", placeholder="e.g. Compare rainfall in Maharashtra and Gujarat over the last 5 years")

# --- When user submits ---
if user_question:
    with st.spinner("🔍 Thinking... querying datasets..."):
        response = query_with_reasoning(user_question)

    if "error" in response:
        st.error(f"❌ Error: {response['error']}")
    else:
        # --- Display answer ---
        st.subheader("💬 AI Answer")
        st.write(response["summary"])

        st.subheader("🧠 Gemini Reasoning")
        st.info(response["gemini_reasoning"])

        st.subheader("🧾 SQL Query Used")
        st.code(response["sql_query"], language="sql")

        st.subheader("📊 Result Preview (first few rows)")
        st.table(response["result_preview"])
else:
    st.markdown(
        "💡 Try asking: *'Which district in Punjab had highest rainfall last year?'*")

# --- Footer ---
st.markdown("---")
st.caption("Developed for Project Samarth Challenge — by Mukund Mekala 💡")
