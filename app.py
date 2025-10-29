import streamlit as st
from ai_helper import query_with_reasoning
import pandas as pd

# --- Page Config ---
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
    _(Powered by Gemini + DuckDB + Real Government Data)_  
    """
)

# --- Input box ---
user_question = st.text_input(
    "🧠 Ask your question:",
    placeholder="e.g. Compare rainfall in Maharashtra and Gujarat over the last 5 years"
)

# --- When user submits ---
if user_question:
    with st.spinner("🔍 Thinking... querying datasets..."):
        response = query_with_reasoning(user_question)

    # --- Error Handling ---
    if "error" in response:
        st.error(f"❌ Error: {response['error']}")
    else:
        # --- Display AI’s reasoning ---
        st.subheader("🧠 AI Reasoning")
        st.info(response.get("explanation", "No explanation available."))

        # --- SQL Query ---
        st.subheader("🧾 SQL Query Used")
        st.code(response.get("sql_query", "No query generated"), language="sql")

        # --- Result Display ---
        st.subheader("📊 Query Result")
        result = response.get("result")

        if result:
            # Handle single-value or multi-row results
            if isinstance(result, list):
                if isinstance(result[0], tuple):
                    # Convert tuple list to DataFrame for table display
                    df = pd.DataFrame(result)
                    st.table(df.head())
                else:
                    st.success(f"✅ Result: {result[0]}")
            else:
                st.success(f"✅ Result: {result}")
        else:
            st.warning("⚠️ No results returned from the database.")
else:
    st.markdown(
        "💡 Try asking: *'Which district in Punjab had the highest rainfall last year?'*")

# --- Footer ---
st.markdown("---")
st.caption("Developed for Project Samarth Challenge — by Mukund Mekala 💡")
