import pandas as pd

genunits = pd.read_csv("genunits.csv", skiprows=1)

genunits = genunits.loc[:, ~genunits.columns.str.contains('^I$')]

genunits = genunits[["DUID", "FUELTYPE"]]

print(genunits.head())
print(genunits.columns)