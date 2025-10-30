import duckdb
con = duckdb.connect('samarth_data.duckdb')
print(con.execute("DESCRIBE crop_production;").fetchdf())
