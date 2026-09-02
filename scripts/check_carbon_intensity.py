"""
Diagnostic: check stg_carbon_intensity for null, infinite, or
physically implausible carbon intensity values.
"""

import sqlite3

conn = sqlite3.connect("data/energy_analytics.db")

cursor = conn.execute("""
    SELECT region, fueltech, COUNT(*)
    FROM stg_carbon_intensity
    WHERE carbon_intensity IS NULL
       OR carbon_intensity > 100
    GROUP BY region, fueltech
""")

rows = cursor.fetchall()
if rows:
    print("Found suspicious rows:")
    for row in rows:
        print(row)
else:
    print("No null or implausible carbon_intensity values found.")

conn.close()
