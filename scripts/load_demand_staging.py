"""
Staging layer: reads raw demand CSVs,
renames columns for clarity, and loads the result into the
stg_demand table in the local SQLite database.
"""

import sqlite3
import pandas as pd

DB_PATH = "data/energy_analytics.db"
RAW_FILES = [
    "data/raw/nsw1_demand_1week.csv",
    "data/raw/sa1_demand_1week.csv",
]


def load_staging():
    # Read and combine both regions' raw CSVs into one DataFrame
    df = pd.concat([pd.read_csv(f) for f in RAW_FILES], ignore_index=True)

    # Rename columns to be self-documenting (units in the name)
    df = df.rename(columns={"demand": "demand_mw"})


    conn = sqlite3.connect(DB_PATH)
    df.to_sql("stg_demand", conn, if_exists="replace", index=False)
    conn.close()

    print(f"Loaded {len(df)} rows into stg_demand")
    print(df.head())


if __name__ == "__main__":
    load_staging()
    