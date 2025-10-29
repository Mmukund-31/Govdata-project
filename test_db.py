import duckdb

# Connect to the DuckDB file
con = duckdb.connect("samarth.db")

# List all tables
tables = con.execute("SHOW TABLES;").fetchall()
print("Tables:", tables)

# For example, describe the first table
if tables:
    table_name = tables[0][0]
    print(f"\nFirst table: {table_name}")
    print(con.execute(f"DESCRIBE {table_name};").fetchdf())

    # Show 5 rows
    print(f"\nSample data from {table_name}:")
    print(con.execute(f"SELECT * FROM {table_name} LIMIT 5;").fetchdf())
