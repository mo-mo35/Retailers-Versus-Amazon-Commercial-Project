import duckdb
import pandas as pd
import os

con = duckdb.connect("dev.duckdb")

marts = [
    "mart_margin_trends",
    "mart_yoy_changes",
    "mart_resilience_scores"
]

os.makedirs("exports", exist_ok=True)

for mart in marts:
    df = con.execute(f"select * from main.{mart}").df()
    path = f"exports/{mart}.csv"
    df.to_csv(path, index=False)
    print(f"Exported {len(df)} rows to {path}")

con.close()
