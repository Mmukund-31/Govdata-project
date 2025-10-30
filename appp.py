import duckdb
import re
import json

# Connect to database
con = duckdb.connect("samarth.db")

# Helper: Find all matching subdivisions for a state


def get_matching_subdivisions(state):
    subs = con.execute(
        "SELECT DISTINCT lower(subdivision) FROM rainfall").fetchall()
    state = state.lower().strip()
    matches = [s[0] for s in subs if state in s[0]]  # partial match
    return matches if matches else [state]

# Helper: Intent detection


def detect_intent(question):
    q = question.lower()

    if "rainfall" in q and "compare" in q:
        return "compare_rainfall"
    if "rainfall" in q:
        return "rainfall_info"
    if "top" in q and "crop" in q:
        return "top_crops"
    if "highest" in q and "production" in q:
        return "highest_production"
    return "unknown"

# Main function


def answer_question(question):
    intent = detect_intent(question)
    print(f"\nIntent detected: {intent}")

    # Extract states, years, etc.
    states = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', question)
    year_match = re.search(r'\b(20\d{2})\b', question)
    year = int(year_match.group(1)) if year_match else None
    N_match = re.search(r'top\s*(\d+)', question.lower())
    N = int(N_match.group(1)) if N_match else 3
    crop_match = re.search(
        r'\b(rice|wheat|maize|sugarcane|cotton|millet|paddy)\b', question.lower())
    crop = crop_match.group(1) if crop_match else None

    sql = None
    result = None

    # ---------------- Rainfall Comparison ----------------
    if intent == "compare_rainfall":
        all_matches = []
        for st in states:
            all_matches.extend(get_matching_subdivisions(st))

        placeholders = ", ".join([f"'{m}'" for m in all_matches])
        sql = f"""
            WITH selected_years AS (
                SELECT year
                FROM rainfall
                WHERE lower(subdivision) IN ({placeholders})
                GROUP BY year
                ORDER BY year DESC
                LIMIT {N}
            ),
            state_agg AS (
                SELECT
                    CASE
                        {" ".join([f"WHEN lower(subdivision) LIKE '%{st.lower()}%' THEN '{st}'" for st in states])}
                        ELSE lower(subdivision)
                    END AS state,
                    year,
                    AVG(COALESCE(annual, jan+feb+mar+apr+may+jun+jul+aug+sep+oct+nov+dec)) AS rainfall
                FROM rainfall
                WHERE lower(subdivision) IN ({placeholders})
                GROUP BY 1,2
            )
            SELECT state, AVG(rainfall) AS avg_annual_rainfall
            FROM state_agg
            WHERE year IN (SELECT year FROM selected_years)
            GROUP BY state;
        """

    # ---------------- Top Crops ----------------
    elif intent == "top_crops":
        state = states[0] if states else "Karnataka"
        year_filter = f"AND year = {year}" if year else ""
        sql = f"""
            SELECT crop, SUM(production_tonnes) AS total_production
            FROM crop_prod
            WHERE lower(state_name) = '{state.lower()}' {year_filter}
            GROUP BY crop
            ORDER BY total_production DESC
            LIMIT {N};
        """

    # ---------------- Highest Production District ----------------
    elif intent == "highest_production":
        state = states[0] if states else "Karnataka"
        year_filter = f"AND year = {year}" if year else ""
        crop_filter = f"AND lower(crop) = '{crop}'" if crop else ""
        sql = f"""
            SELECT district_name, SUM(production_tonnes) AS total_production
            FROM crop_prod
            WHERE lower(state_name) = '{state.lower()}' {year_filter} {crop_filter}
            GROUP BY district_name
            ORDER BY total_production DESC
            LIMIT 5;
        """

    # ---------------- Execute SQL ----------------
    if sql:
        try:
            result = con.execute(sql).df()
        except Exception as e:
            return f"SQL execution failed: {e}\n\n{sql}"

    if result is None or result.empty:
        return "No data found for the given query."

    return result.to_string(index=False)


# ---------------- CLI Interface ----------------
if __name__ == "__main__":
    print("Project Samarth — Local Rule-Based Q&A (Phase 1)")
    print("Ask natural language questions about agriculture and rainfall. This runs fully offline — no external APIs.\n")

    while True:
        q = input("\nAsk a question (or type 'exit'): ").strip()
        if q.lower() in ["exit", "quit"]:
            break
        print("\nAnswer:")
        print(answer_question(q))
