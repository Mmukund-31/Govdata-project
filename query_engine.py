import duckdb


def answer_query(query):
    con = duckdb.connect("samarth.db")
    query = query.lower()

    if "top" in query and "crop" in query and "karnataka" in query:
        # Example: Top 5 crops in Karnataka in 2020
        sql = """
            SELECT commodity AS crop, COUNT(*) AS count
            FROM crop_market_prices
            WHERE lower(state) LIKE '%karnataka%'
            GROUP BY crop
            ORDER BY count DESC
            LIMIT 5;
        """
        result = con.execute(sql).fetchdf()
        print(result)

    elif "rainfall" in query and "compare" in query:
        # Example: Compare rainfall in Karnataka and Tamil Nadu
        sql = """
            SELECT subdivision, AVG(annual) AS avg_annual_rainfall
            FROM rainfall
            WHERE lower(subdivision) LIKE '%karnataka%'
               OR lower(subdivision) LIKE '%tamil nadu%'
            GROUP BY subdivision
            ORDER BY avg_annual_rainfall DESC;
        """
        result = con.execute(sql).fetchdf()
        print(result)

    else:
        print("❓ Sorry, I don't understand that question yet.")

    con.close()


if __name__ == "__main__":
    print("Welcome to Project Samarth Q&A Interface!")
    print("Ask something like:")
    print("  - Top 5 crops in Karnataka in 2020")
    print("  - Compare rainfall in Karnataka and Tamil Nadu")
    print("\n")

    q = input("Your question: ")
    answer_query(q)
