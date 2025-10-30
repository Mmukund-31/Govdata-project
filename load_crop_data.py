import duckdb

# Connect to your main DuckDB database
conn = duckdb.connect("samarth.db")

csv_path = "crop_production_sample.csv"

print("📥 Loading market price data into DuckDB from:", csv_path)

# Create a clean, structured table for crop market prices
conn.execute(f"""
CREATE OR REPLACE TABLE crop_market_prices AS
SELECT
    state,
    district,
    market,
    commodity AS crop,
    variety,
    grade,
    arrival_date,
    min_price,
    max_price,
    modal_price,
    LOWER(TRIM(state)) AS state_norm,
    LOWER(TRIM(district)) AS district_norm
FROM read_csv_auto('{csv_path}', header=True);
""")

print("✅ crop_market_prices table created successfully!\n")

print("📊 Summary:")
print(conn.execute("""
SELECT 
    COUNT(*) AS total_rows,
    COUNT(DISTINCT state) AS states,
    COUNT(DISTINCT district) AS districts,
    COUNT(DISTINCT crop) AS unique_crops
FROM crop_market_prices
""").fetchdf())

print("\n🔍 Sample rows:")
print(conn.execute("SELECT * FROM crop_market_prices LIMIT 5").fetchdf())

conn.close()
