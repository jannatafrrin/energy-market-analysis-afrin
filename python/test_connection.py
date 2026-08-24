from datetime import datetime, timedelta
import pandas as pd
from openelectricity import OEClient
from openelectricity.types import DataMetric

end_date = datetime(2026, 8, 17)
start_date = end_date - timedelta(days=1)

with OEClient() as client:
    response = client.get_network_data(
        network_code="NEM",
        metrics=[DataMetric.POWER],
        interval="5m",
        date_start=start_date,
        date_end=end_date,
        primary_grouping="network_region",
    )

    rows = []
    for metric_series in response.data:        # one per metric (just "power" here)
        for series in metric_series.results:    # one per region
            _, region = series.name.split("_", 1)
            for point in series.data:
                dt, value = point.root
                rows.append({"interval": dt, "region": region, "power": value})

    df = pd.DataFrame(rows)
    print(df["region"].unique())
    print(df[df["region"] == "NSW1"].head())