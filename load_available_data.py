import duckdb
import pandas as pd
import os

# === Configuration ===
DB_FILE = "samarth_data.duckdb"
DATA_DIR = "."

FILES = {
    "crop_production": os.path.join(DATA_DIR, "crop_production_sample.csv"),
    "rainfall_data": os.path.join(DATA_DIR, "rainfall_data.csv"),
    # optional
    "crop_market_prices": os.path.join(DATA_DIR, "crop_market_prices_sample.csv"),
}

# === Connect to persistent DuckDB file ===
con = duckdb.connect(DB_FILE)
print(f"🔗 Connected to DuckDB database: {DB_FILE}\n")

# === Load available CSVs ===
for table_name, csv_path in FILES.items():
    if os.path.exists(csv_path):
        print(f"📥 Loading '{table_name}' from: {csv_path}")
        df = pd.read_csv(csv_path)

        # Normalize text columns for better matching in queries
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.strip().str.lower()

        # Create or replace table
        con.execute(
            f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")
        print(
            f"✅ Created table '{table_name}' with {len(df)} rows and {len(df.columns)} columns.\n")
    else:
        print(f"⚠️ File not found for '{table_name}', skipping...\n")

# === Show all tables ===
print("📊 Tables in DuckDB now:")
print(con.execute("SHOW TABLES;").fetchdf(), "\n")

# === Quick preview of each table ===
for name in ["crop_production", "rainfall_data", "crop_market_prices"]:
    try:
        print(f"🔍 Preview of {name}:")
        print(con.execute(f"SELECT * FROM {name} LIMIT 5;").fetchdf(), "\n")
    except Exception as e:
        print(f"❌ Could not preview {name}: {e}\n")

con.close()
print("💾 All available data loaded successfully into DuckDB!\n")
