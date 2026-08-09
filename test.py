import pandas as pd

file_path = "/Users/afrin/nem-data/data/unit-scada/2024-01/clean.parquet"

df = pd.read_parquet(file_path)

print(df.head())
print(df.columns)
print(df.shape)
