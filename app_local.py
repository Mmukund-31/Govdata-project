import streamlit as st
from ai_helper import get_answer

# ---------------------- PAGE SETUP ----------------------
st.set_page_config(page_title="Project Samarth — Local AI Q&A",
                   page_icon="🌾", layout="centered")

# ---------------------- HEADER ----------------------
st.markdown(
    """
    <h1 style='text-align:center; color:#2e7d32;'>🌾 Project Samarth — Local AI Q&A</h1>
    <p style='text-align:center; color:gray;'>
        Ask questions about rainfall or crop trends — runs 100% offline using DuckDB 💾
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

# ---------------------- INPUT AREA ----------------------
user_query = st.text_input("💬 Ask your question:")

if st.button("🔍 Get Answer"):
    if user_query.strip():
        with st.spinner("🤖 Thinking..."):
            response = get_answer(user_query)
        st.markdown("### ✅ Answer:")
        st.markdown(response)
    else:
        st.warning("⚠️ Please enter a question first!")

# ---------------------- FOOTER ----------------------
st.markdown(
    """
    <hr>
    <p style='text-align:center; color:gray;'>
        Built with ❤️ | Runs locally on DuckDB 🦆
    </p>
    """,
    unsafe_allow_html=True
)
