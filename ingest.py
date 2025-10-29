import pandas as pd
import duckdb

# 1️⃣ Load Market Price (Crop Data)
print("Loading crop/market price data...")
crop_df = pd.read_csv("sample_data/crop_production_sample.csv")

# Clean column names
crop_df.columns = crop_df.columns.str.strip().str.lower().str.replace(" ", "_")

# Just to confirm what we have
print("Crop columns:", crop_df.columns.tolist())

# Select relevant columns
expected_cols = [
    "state", "district", "market", "commodity", "variety",
    "grade", "arrival_date", "min_price", "max_price", "modal_price"
]
crop_df = crop_df[[col for col in crop_df.columns if col in expected_cols]]

print("Crop data shape:", crop_df.shape)

# 2️⃣ Load Rainfall Data
print("Loading rainfall data...")
rain_df = pd.read_csv("sample_data/rainfall_data.csv")

rain_df.columns = rain_df.columns.str.strip().str.lower().str.replace(" ", "_")

expected_cols_rain = [
    "subdivision", "year", "jan", "feb", "mar", "apr", "may", "jun",
    "jul", "aug", "sep", "oct", "nov", "dec", "annual"
]
rain_df = rain_df[[
    col for col in rain_df.columns if col in expected_cols_rain]]

print("Rainfall data shape:", rain_df.shape)

# 3️⃣ Connect to DuckDB
con = duckdb.connect("samarth.db")

# 4️⃣ Store data into tables
print("Storing data into local database...")
con.execute("DROP TABLE IF EXISTS crop_market_prices;")
con.execute("CREATE TABLE crop_market_prices AS SELECT * FROM crop_df;")

con.execute("DROP TABLE IF EXISTS rainfall;")
con.execute("CREATE TABLE rainfall AS SELECT * FROM rain_df;")

print("✅ Data successfully stored into samarth.db")

# 5️⃣ Quick test query
result = con.execute(
    "SELECT COUNT(*) AS total_rows FROM crop_market_prices;").fetchdf()
print("Crop rows in DB:", result.iloc[0]['total_rows'])

con.close()
