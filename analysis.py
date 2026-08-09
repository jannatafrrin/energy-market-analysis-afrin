import pandas as pd

# Load the NEM SCADA data
file_path = "/Users/afrin/nem-data/data/unit-scada/2024-01/clean.parquet"

df = pd.read_parquet(file_path)

# Convert MW to MWh
df["MWh"] = df["SCADAVALUE"] * (5/60)

print(df[["SETTLEMENTDATE","DUID","MWh"]].head())

# Optional: keep only the columns you need
df = df[[
    "interval-start",
    "DUID",
    "SCADAVALUE",
    "frequency_minutes",
    "MWh"
]]
# Aggregate total MWh by generator
generation = df.groupby("DUID")["MWh"].sum()

# Show top 10 generators
print(generation.sort_values(ascending=False).head(10))
# Check columns
print(df.columns)