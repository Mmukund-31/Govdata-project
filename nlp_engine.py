# nlp_engine.py
import duckdb
import re
import pandas as pd

# Connect to DuckDB
con = duckdb.connect("samarth.db")

# -----------------------------------------------------
# Utility: Partial subdivision matching for rainfall
# -----------------------------------------------------


def get_matching_subdivisions(state):
    subs = con.execute(
        "SELECT DISTINCT lower(subdivision) FROM rainfall").fetchall()
    state = state.lower().strip()
    matches = [s[0] for s in subs if state in s[0]]
    return matches if matches else [state]


# -----------------------------------------------------
# Intent Detection and Query Planner
# -----------------------------------------------------
def plan_query(question):
    q = question.lower()
    intent = None

    if "compare" in q and "rainfall" in q:
        intent = "compare_rainfall"
    elif "rainfall" in q:
        intent = "rainfall_info"
    elif "top" in q and "crop" in q:
        intent = "top_crops"
    elif "highest" in q and "production" in q:
        intent = "highest_production"
    else:
        intent = "unknown"

    # Extract entities
    states = re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b", question)
    year_match = re.search(r"\b(20\d{2})\b", question)
    year = int(year_match.group(1)) if year_match else None
    N_match = re.search(r"top\s*(\d+)", question.lower())
    N = int(N_match.group(1)) if N_match else 3
    crop_match = re.search(
        r"\b(rice|wheat|maize|sugarcane|cotton|millet|paddy)\b", question.lower()
    )
    crop = crop_match.group(1) if crop_match else None

    sql = None

    # -------------------------------------------------
    # Query Templates
    # -------------------------------------------------
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

    return {
        "intent": intent,
        "states": states,
        "years": [year] if year else [],
        "N": N,
        "crop": crop,
        "sql": sql,
    }


# -----------------------------------------------------
# Execute SQL and Fetch
# -----------------------------------------------------
def run_plan_and_fetch(planner):
    try:
        df = con.execute(planner["sql"]).df()
        return {"dataframe": df}
    except Exception as e:
        return {"error": f"SQL execution failed: {e}"}


# -----------------------------------------------------
# Format Final Answer for Streamlit Display
# -----------------------------------------------------
def format_answer(result):
    if "error" in result:
        return {"text": result["error"]}

    df = result.get("dataframe", pd.DataFrame())

    if df.empty:
        return {"text": "No data found for this query."}

    # Convert table into readable text
    text = ""
    if "avg_annual_rainfall" in df.columns:
        text = "Average annual rainfall:\n\n" + "\n".join(
            [f"{r.state}: {r.avg_annual_rainfall:.2f}" for _, r in df.iterrows()]
        )
    elif "crop" in df.columns:
        text = "Top crops:\n\n" + "\n".join(
            [f"{r.crop}: {r.total_production:.2f}" for _, r in df.iterrows()]
        )
    elif "district_name" in df.columns:
        text = "Highest production districts:\n\n" + "\n".join(
            [f"{r.district_name}: {r.total_production:.2f}" for _, r in df.iterrows()]
        )
    else:
        text = "Results:\n\n" + df.to_string(index=False)

    return {"text": text, "dataframe": df}
