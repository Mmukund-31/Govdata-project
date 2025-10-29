import google.generativeai as genai
import os
from dotenv import load_dotenv
import sqlite3
import json

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize model
model = genai.GenerativeModel("models/gemini-2.5-flash")

DB_PATH = "samarth.db"


def run_sql_query(query):
    """Execute SQL query on samarth.db and return results as list of tuples."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0]
                   for desc in cursor.description] if cursor.description else []
        conn.close()
        return {"columns": columns, "rows": rows}
    except Exception as e:
        return {"error": str(e)}


def query_with_reasoning(user_question):
    """
    Full pipeline:
    1. Ask Gemini to generate SQL + explanation.
    2. Execute SQL on local DB.
    3. Ask Gemini to summarize the results.
    """
    prompt = f"""
    You are an expert data analyst working with an SQLite database named samarth.db.

    Tables available:
    1. crop_data(state, district, market, commodity, variety, grade, arrival_date, min_price, max_price, modal_price)
    2. rainfall_data(state, district, year, month, rainfall_amount)

    The user asks: "{user_question}"

    Generate a JSON response with:
    {{
      "sql_query": "...",
      "explanation": "..."
    }}
    """

    response = model.generate_content(prompt)
    text = response.text

    # Extract SQL and explanation
    try:
        data = json.loads(text)
        sql_query = data.get("sql_query", "")
        explanation = data.get("explanation", "")
    except:
        sql_query = None
        explanation = f"Couldn't parse Gemini output:\n{text}"

    if not sql_query:
        return {"error": "No valid SQL query generated", "raw_output": text}

    print(f"\n🧠 Gemini generated SQL:\n{sql_query}\n")

    # Step 2: Run SQL query on local DB
    db_result = run_sql_query(sql_query)
    if "error" in db_result:
        return {"error": db_result["error"], "sql_query": sql_query}

    # Step 3: Ask Gemini to summarize results
    if not db_result["rows"]:
        return {"answer": "No results found.", "sql_query": sql_query}

    summary_prompt = f"""
    User asked: "{user_question}"

    Here is the SQL result:
    Columns: {db_result['columns']}
    Rows: {db_result['rows'][:5]}  # only show first 5 rows

    Give a short, simple explanation in natural language.
    """
    summary = model.generate_content(summary_prompt).text

    return {
        "question": user_question,
        "sql_query": sql_query,
        "result_preview": db_result["rows"][:5],
        "summary": summary,
        "gemini_reasoning": explanation
    }
