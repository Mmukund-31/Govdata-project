import re
import duckdb
import pandas as pd

# Connect to the DuckDB database
con = duckdb.connect("samarth_data.duckdb")

# ---------------------- INTENT DETECTION ----------------------


def detect_intent(question: str):
    q = question.lower()
    if "rainfall" in q and ("average" in q or "mean" in q):
        return "average_rainfall"
    elif "compare" in q and "rainfall" in q:
        return "compare_rainfall"
    elif "highest" in q and "production" in q:
        return "highest_production"
    elif "top" in q and "crop" in q:
        return "top_crops"
    elif "price" in q and ("average" in q or "modal" in q):
        return "average_price"
    else:
        return "unknown"


# ---------------------- ANSWER GENERATION ----------------------
def answer_query(intent: str, question: str):
    q = question.lower()

    # 1️⃣ Average Rainfall
    if intent == "average_rainfall":
        match = re.search(r"rainfall in ([a-z\s&]+)\s+(\d{4})", q)
        if match:
            state, year = match.groups()
            df = con.execute(f"""
                SELECT ANNUAL FROM rainfall_data
                WHERE LOWER(SUBDIVISION) LIKE '%{state.strip()}%'
                AND YEAR = {year}
            """).fetchdf()

            if not df.empty:
                avg = df["ANNUAL"].mean()
                return f"🌧️ Average annual rainfall in {state.title()} ({year}) was **{avg:.2f} mm**."
            return "❌ No data found for the given state and year."
        return "⚠️ Please mention both the state and the year (e.g., 'Average rainfall in Kerala 2020')."

    # 2️⃣ Compare Rainfall
    elif intent == "compare_rainfall":
        match = re.search(
            r"compare rainfall in ([a-z\s&]+) and ([a-z\s&]+)\s+(\d{4})", q)
        if match:
            state1, state2, year = match.groups()
            data = []
            for s in [state1, state2]:
                df = con.execute(f"""
                    SELECT ANNUAL FROM rainfall_data
                    WHERE LOWER(SUBDIVISION) LIKE '%{s.strip()}%'
                    AND YEAR = {year}
                """).fetchdf()
                if not df.empty:
                    avg = df["ANNUAL"].mean()
                    data.append((s.title(), avg))
            if len(data) == 2:
                s1, r1 = data[0]
                s2, r2 = data[1]
                higher = s1 if r1 > r2 else s2
                return f"💧 In {year}, {higher} received more rainfall.\n→ {s1}: {r1:.2f} mm\n→ {s2}: {r2:.2f} mm"
            return "❌ Couldn’t find rainfall data for one or both states."
        return "⚠️ Please specify two states and a year (e.g., 'Compare rainfall in Kerala and Gujarat 2020')."

    # 3️⃣ Top Crops
    elif intent == "top_crops":
        match = re.search(r"top\s*(\d+)?\s*crops in ([a-z\s&]+)", q)
        if match:
            n = int(match.group(1)) if match.group(1) else 3
            state = match.group(2).strip()
            df = con.execute(f"""
                SELECT state, district, market, commodity AS crop,
                       AVG(modal_price) AS avg_price
                FROM crop_production
                WHERE LOWER(state) LIKE '%{state}%'
                GROUP BY state, district, market, commodity
                ORDER BY avg_price DESC
                LIMIT {n}
            """).fetchdf()

            if not df.empty:
                return df.to_markdown(index=False)
            return "❌ No crop data found for the specified state."
        return "⚠️ Please specify the state (e.g., 'Top 5 crops in Andhra Pradesh')."

    # 4️⃣ Highest Production (Proxy by Price)
    elif intent == "highest_production":
        match = re.search(r"highest .* in ([a-z\s&]+)\s*(\d{4})?", q)
        if match:
            state = match.group(1).strip()
            df = con.execute(f"""
                SELECT district, commodity AS crop, AVG(modal_price) AS avg_price
                FROM crop_production
                WHERE LOWER(state) LIKE '%{state}%'
                GROUP BY district, commodity
                ORDER BY avg_price DESC
                LIMIT 1
            """).fetchdf()

            if not df.empty:
                row = df.iloc[0]
                return f"🌾 In {state.title()}, {row['district']} district had the highest value crop: **{row['crop']}** (Avg Price ₹{row['avg_price']:.0f})."
            return "❌ No data found for that state."
        return "⚠️ Please specify the state (e.g., 'Which district in Tamil Nadu had highest production in 2020')."

    # 5️⃣ Average Price
    elif intent == "average_price":
        match = re.search(r"average price of ([a-z\s&]+) in ([a-z\s&]+)", q)
        if match:
            crop, state = match.groups()
            df = con.execute(f"""
                SELECT AVG(modal_price) AS avg_price
                FROM crop_production
                WHERE LOWER(state) LIKE '%{state.strip()}%'
                AND LOWER(commodity) LIKE '%{crop.strip()}%'
            """).fetchdf()

            if not df.empty and not pd.isna(df["avg_price"][0]):
                return f"💰 Average price of {crop.title()} in {state.title()} was ₹{df['avg_price'][0]:.0f}."
            return "❌ No price data found for that crop and state."
        return "⚠️ Please specify both crop and state (e.g., 'Average price of tomato in Maharashtra')."

    # 6️⃣ Unknown
    else:
        return "🤔 Sorry, I didn't understand that. Try asking about rainfall, crops, or prices."


# ---------------------- HELPER FUNCTION ----------------------
def get_answer(user_query: str):
    intent = detect_intent(user_query)
    return answer_query(intent, user_query)


# ---------------------- CLI MODE ----------------------
def run_cli():
    print("🌾 Project Samarth — Local Rule-Based Q&A (Phase 2)")
    print("Ask natural questions about crops or rainfall. Fully offline. Powered by DuckDB 💾\n\n")

    while True:
        question = input("\n💬 Enter your question (or type 'exit'): ")
        if question.lower() in ["exit", "quit", "bye"]:
            print("👋 Exiting Project Samarth. Stay smart and sustainable!")
            break
        intent = detect_intent(question)
        print(f"\n🧠 Intent detected: {intent}\n")
        answer = answer_query(intent, question)
        print(f"\n📝 Answer:\n{answer}\n")
        print("Built with ❤️ for Project Samarth | Runs fully offline using DuckDB 🦆\n")


if __name__ == "__main__":
    run_cli()
