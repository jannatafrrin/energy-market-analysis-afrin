"""
Sets up the local SQLite database for the energy analytics project.
Run this once to create the .db file. Safe to re-run — sqlite3.connect()
creates the file only if it doesn't already exist; it won't overwrite
existing data.
"""

import sqlite3
import os

DB_PATH = "data/energy_analytics.db"


def setup_database():
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    print(f"Connected to database at {DB_PATH}")

    conn.close()
    print("Connection closed. Database file ready.")


if __name__ == "__main__":
    setup_database()
