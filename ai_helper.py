import os
from dotenv import load_dotenv
import google.generativeai as genai
import duckdb
import json

# ==============================
# 1️⃣ Load API Key and Configure
# ==============================
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize model
model = genai.GenerativeModel("models/gemini-2.5-flash")

# Path to DuckDB database
DB_PATH = "samarth.db"


# ==============================
# 2️⃣ Query database
# ==============================
def fetch_data_from_db(query):
    """Run an SQL query on the local DuckDB database and return results."""
    try:
        con = duckdb.connect(DB_PATH)
        result = con.execute(query).fetchall()
        con.close()
        return result
    except Exception as e:
        return f"❌ Database Error: {e}"


# ==============================
# 3️⃣ Ask Gemini to create SQL
# ==============================
def query_with_reasoning(user_question):
    """
    Take user's natural question, ask Gemini to generate SQL,
    execute it, and return result + explanation.
    """
    prompt = f"""
You are a data analyst working with a DuckDB database named samarth.db.

Here is the database schema:

TABLE: crop_market_prices
Columns: state, district, market, commodity, variety, grade, arrival_date, min_price, max_price, modal_price

TABLE: rainfall
Columns: state, district, month, year, rainfall_amount

TABLE: crop_prod
Columns: (production related — state, district, crop, season, area, production, year, etc.)

⚠️ Important instructions:
- Always use the exact table names above (for crop price queries use `crop_market_prices`).
- Use valid DuckDB SQL syntax.
- Return your answer strictly in this JSON format:
{{
  "sql_query": "<SQL query>",
  "explanation": "<short natural explanation>"
}}

Now, write an SQL query to answer this user question:
"{user_question}"
"""

    # Generate the structured response
    response = model.generate_content(prompt).text

    # Try to parse JSON safely
    try:
        # Clean code fences if present
        if "```" in response:
            response = response.split("```")[-2].replace("json", "").strip()
        parsed = json.loads(response)

        sql_query = parsed.get("sql_query", "")
        explanation = parsed.get("explanation", "")

        # Fix common table name errors
        if "crop_data" in sql_query:
            sql_query = sql_query.replace("crop_data", "crop_market_prices")

        # Execute the SQL query
        result = fetch_data_from_db(sql_query)

        return {
            "sql_query": sql_query,
            "explanation": explanation,
            "result": result
        }

    except Exception as e:
        return {
            "error": f"❌ Failed to parse model output: {e}",
            "raw_output": response
        }
