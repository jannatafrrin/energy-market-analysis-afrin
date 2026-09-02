"""
Data pipeline: pulls raw AEMO/OpenNEM data, cleans it,
loads into raw/staging tables.
"""

from datetime import datetime, timedelta
import os
import pandas as pd
from openelectricity import OEClient
from openelectricity.types import DataMetric

from dotenv import load_dotenv
load_dotenv()

end_date = datetime(2026, 8, 17)
start_date = end_date - timedelta(days=7)

with OEClient() as client:
    response = client.get_network_data(
        network_code="NEM",
        metrics=[DataMetric.POWER, DataMetric.EMISSIONS],
        interval="5m",
        date_start=start_date,
        date_end=end_date,
        primary_grouping="network_region",
        secondary_grouping="fueltech_group",
    )

    rows = []
    for metric_series in response.data:
        for series in metric_series.results:
            metric_region, fueltech = series.name.split("|", 1)
            metric, region = metric_region.split("_", 1)
            if region not in ("NSW1", "SA1"):
                continue
            # Collapse battery charging/discharging into one category
            if fueltech.startswith("battery"):
                fueltech = "battery"
            for point in series.data:
                dt, value = point.root
                rows.append({
                    "interval": dt,
                    "region": region,
                    "fueltech": fueltech,
                    "metric": metric,
                    "value": value,
                })

    df = pd.DataFrame(rows)
    df_wide = df.pivot_table(
        index=["interval", "region", "fueltech"],
        columns="metric",
        values="value",
        aggfunc="sum",  # multiple raw rows (e.g. collapsed battery states) sum per interval
    ).reset_index()

df_resampled = (
    df_wide
    .set_index("interval")
    .groupby(["region", "fueltech"])
    .resample("30min")
    .agg({"power": "mean", "emissions": "sum"})
    .reset_index()
)

print(df_resampled.shape)
print(df_resampled.head(10))

os.makedirs("data/raw", exist_ok=True)

for region in ("NSW1", "SA1"):
    out_path = f"data/raw/{region.lower()}_sample_1week.csv"
    df_resampled[df_resampled["region"] == region].to_csv(out_path, index=False)
    print(f"Saved {out_path}")