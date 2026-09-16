"""
Runs a .sql file against the local SQLite database and prints the results
as a readable table. Usage: python3 scripts/run_query.py sql/some_query.sql
"""

import sqlite3
import sys
import pandas as pd

DB_PATH = "data/energy_analytics.db"


def run_query(sql_file_path):
    with open(sql_file_path, "r") as f:
        query = f.read()

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()

    print(f"Query: {sql_file_path}")
    print(f"Rows returned: {len(df)}\n")
    print(df.to_string(index=False))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/run_query.py <path_to_sql_file>")
        sys.exit(1)

    run_query(sys.argv[1])