import pandas as pd

du_summary = pd.read_csv(
    "du-detail-summary.csv",
    skiprows=1  # skip the metadata row
)

# Drop unwanted columns if they exist
du_summary = du_summary.loc[:, ~du_summary.columns.str.contains('^I$')]

du_summary = du_summary[[
    "DUID",
    "DISPATCHTYPE",
    "REGIONID"
]]

print(du_summary.head())

print(du_summary.head())
print(du_summary.columns)