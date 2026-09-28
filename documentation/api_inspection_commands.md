# API Inspection Commands — Reference Cheatsheet

Reusable commands for exploring an unfamiliar API client library before
writing pipeline code against it. Copy the relevant block, adjust the
class/method/enum name, and run.

## 1. Inspect a method's full signature

Use when: you need to know what parameters a method accepts, their types,
and defaults — e.g. discovering `secondary_grouping` existed on
`get_network_data`, or that `get_market` takes `network_region` directly.

```bash
python3 -c "
from openelectricity import OEClient
import inspect
print(inspect.signature(OEClient.get_market))
"
```

## 2. List every value in an Enum

Use when: a parameter's type hint shows a custom Enum (not a plain
`Literal[...]` string) and you need the actual valid values — e.g. finding
`FueltechGroupType`'s 9 fuel categories, or `MarketMetric`'s full list
(DEMAND, PRICE, CURTAILMENT, etc). `typing.get_args()` only works on
`Literal` types — for an Enum, loop over its members instead.

```bash
python3 -c "
from openelectricity.types import MarketMetric
for member in MarketMetric:
    print(member.name, '=', member.value)
"
```

## 3. Small inspection pull — check real response structure/naming

Use when: you're about to add a new metric/parameter to the pipeline and
need to see the *actual* response format before writing parsing logic —
e.g. discovering the pipe-delimited `power_NSW1|coal` naming format after
adding `secondary_grouping`. Keep the date range small (1 day) and the
metric list short — this is a cheap probe, not a real data pull.

```bash
python3 -c "
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime, timedelta
from openelectricity import OEClient
from openelectricity.types import MarketMetric

end_date = datetime(2026, 8, 17)
start_date = end_date - timedelta(days=1)

with OEClient() as client:
    response = client.get_market(
        network_code='NEM',
        metrics=[MarketMetric.DEMAND],
        interval='5m',
        date_start=start_date,
        date_end=end_date,
        network_region='NSW1',
    )
    for metric_series in response.data:
        for series in metric_series.results[:3]:
            print(series.name)
            print(series.columns)
"
```

**Note:** `series.columns` often returns `unit_code=None` for market metrics
(unlike generation metrics, which do populate `unit=...`, e.g. `unit='t'`
for emissions). When the response gives no unit metadata, check the actual
API docs (docs.openelectricity.org.au) rather than assuming from the name —
this caught a real known bug in the `demand` metric's aggregation.