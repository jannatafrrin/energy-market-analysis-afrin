"""
Staging layer: reads raw power/emissions CSVs, computes carbon intensity,
renames columns for clarity, and loads the result into the
stg_carbon_intensity table in the local SQLite database.
"""

import sqlite3
import pandas as pd

DB_PATH = "data/energy_analytics.db"
RAW_FILES = [
    "data/raw/nsw1_sample_1week.csv",
    "data/raw/sa1_sample_1week.csv",
]


def load_staging():
    # Read and combine both regions' raw CSVs into one DataFrame
    df = pd.concat([pd.read_csv(f) for f in RAW_FILES], ignore_index=True)

    # Rename columns to be self-documenting (units in the name)
    df = df.rename(columns={"power": "power_mw", "emissions": "emissions_tco2"})

    # Carbon intensity = tonnes CO2 emitted per MWh of energy generated.
    # power_mw is an average rate over the 30-min interval, so energy (MWh)
    # = power_mw * 0.5 hours. Dividing emissions by that gives tCO2/MWh.
    df["carbon_intensity"] = df["emissions_tco2"] / (df["power_mw"] * 0.5)

    conn = sqlite3.connect(DB_PATH)
    df.to_sql("stg_carbon_intensity", conn, if_exists="replace", index=False)
    conn.close()

    print(f"Loaded {len(df)} rows into stg_carbon_intensity")
    print(df.head())


if __name__ == "__main__":
    load_staging()
