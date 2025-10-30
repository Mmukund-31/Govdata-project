from streamlit_lottie import st_lottie
import streamlit as st
import duckdb
import pandas as pd
import json
import requests
import plotly.express as px
from ai_helper import get_answer

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="🌾 Project Samarth — Smart Rural Insights",
    page_icon="🌿",
    layout="wide",
)

# ---------- LOTTIE HELPER ----------


def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None


# ---------- LOAD ANIMATIONS ----------
farmer_anim = load_lottieurl(
    "https://lottie.host/5bb4f8c7-0b2f-4584-b98b-farmer.json")
rain_anim = load_lottieurl(
    "https://lottie.host/86f61ee5-83d0-44a4-89de-rain.json")
crop_anim = load_lottieurl(
    "https://lottie.host/1ab3b9b5-2db5-4020-a2ef-crop.json")

# ---------- STYLING ----------
st.markdown(
    """
    <style>
        .stTextInput>div>div>input {
            background-color: #f9fff6;
            border-radius: 10px;
            border: 1px solid #b5dcb3;
            padding: 10px;
            font-size: 1rem;
        }
        div[data-testid="stSpinner"] > div {
            text-align:center;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- SIDEBAR ----------
st.sidebar.title("🌾 Project Samarth")
st.sidebar.markdown("### Empowering Rural Insights with Local AI 💾")
menu = st.sidebar.radio("📂 Navigate", ["Ask AI", "About"])
st.sidebar.markdown("---")
st.sidebar.info(
    "🧠 Runs 100% offline \n💧 Works with local crop & rainfall data")

# ---------- DATABASE ----------
con = duckdb.connect("samarth_data.duckdb")

# ---------- ASK AI ----------
if menu == "Ask AI":
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            """
            <h1 style='color:#2e7d32;'>🌿 Project Samarth — Smart Rural Q&A</h1>
            <p style='color:gray; font-size:1.1rem;'>
            Ask anything about <b>rainfall ☔</b> or <b>crop trends 🌾</b> — fully offline💾
            </p>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        if farmer_anim:
            st_lottie(farmer_anim, height=150, key="farmer")

    st.markdown("---")

    with st.expander("💡 Example Questions"):
        st.markdown("""
        - What is the **average price of tomato in Andhra Pradesh**?
        - Compare **rainfall in Kerala and Gujarat 2010**.
        - Show **top 5 crops in Andhra Pradesh**.
        - What’s the **average price of rice in Andhra Pradesh**?
        """)

    user_query = st.text_input("💬 Type your question below:")
    colA, colB = st.columns([4, 1])
    with colB:
        ask = st.button("🔍 Ask AI")

    if ask and user_query.strip():
        with st.spinner("🤖 Thinking..."):
            try:
                response = get_answer(user_query)
                st.success("✅ Answer:")
                st.markdown(
                    f"<div style='padding:15px; background-color:#f1f8e9; border-radius:10px; line-height:1.6;'>{response}</div>",
                    unsafe_allow_html=True,
                )

                q = user_query.lower()

                # ---------- RAINFALL VISUAL ----------
                if "rainfall" in q:
                    st.markdown("### 📈 Rainfall Trend (Sample Data)")
                    df = con.execute("""
                        SELECT subdivision, year, annual
                        FROM rainfall_data
                        WHERE year BETWEEN 2000 AND 2020
                        LIMIT 300
                    """).fetchdf()

                    fig = px.line(
                        df,
                        x="year",
                        y="annual",
                        color="subdivision",
                        title="Rainfall Trends Across Regions",
                        markers=True,
                    )
                    fig.update_layout(
                        title_font_color="#2e7d32",
                        plot_bgcolor="#f9fff6",
                        paper_bgcolor="#ffffff",
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    if rain_anim:
                        st_lottie(rain_anim, height=150, key="rain")

                # ---------- CROP PRICE VISUAL ----------
                elif "crop" in q or "price" in q:
                    st.markdown("### 🌾 Crop Price Comparison")
                    df = con.execute("""
                        SELECT commodity AS crop, AVG(modal_price) AS avg_price
                        FROM crop_production
                        GROUP BY commodity
                        ORDER BY avg_price DESC
                        LIMIT 10
                    """).fetchdf()

                    fig = px.bar(
                        df,
                        x="crop",
                        y="avg_price",
                        color="avg_price",
                        color_continuous_scale="Greens",
                        title="Top 10 Crops by Average Price",
                    )
                    fig.update_layout(
                        xaxis_title="Crop",
                        yaxis_title="Avg Price (₹)",
                        plot_bgcolor="#f9fff6",
                        paper_bgcolor="#ffffff",
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    if crop_anim:
                        st_lottie(crop_anim, height=150, key="crop")

            except Exception as e:
                st.error(f"⚠️ Error: {e}")

    elif ask:
        st.warning("Please enter a question before submitting.")

# ---------- ABOUT ----------
elif menu == "About":
    st.markdown(
        """
        <h2 style='color:#2e7d32;'>🌿 About Project Samarth</h2>
        <p style='font-size:1.1rem;'>
        <b>Project Samarth</b> is an AI-powered offline Q&A assistant built for 
        <b>agricultural intelligence and rural planning</b>.  
        It helps users explore data on rainfall, crops, and pricing directly from 
        local datasets using <b>DuckDB</b> — without needing internet or cloud AI.
        </p>
        <p>
        Built with ❤️ by Siri Reddy using <b>Streamlit</b> ⚡ + <b>DuckDB</b> 🦆 + <b>Python</b> 🐍
        </p>
        """,
        unsafe_allow_html=True,
    )
    if rain_anim:
        st_lottie(rain_anim, height=180, key="rain_info")

# ---------- FOOTER ----------
st.markdown(
    """
    <hr>
    <p style='text-align:center; color:gray;'>
    🌾 Built with ❤️ by <b>Siri Reddy</b>
    </p>
    """,
    unsafe_allow_html=True,
)
