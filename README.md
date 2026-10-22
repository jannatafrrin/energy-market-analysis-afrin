# NEM Carbon Intensity Analytics

An end-to-end SQL/data engineering project analyzing carbon intensity in
Australia's National Electricity Market (NEM), comparing coal-heavy NSW1
against renewables-heavy SA1.

## Business Problem

How can market participants, policymakers, or large energy users track and
reduce carbon intensity in the NEM without increasing system costs?

Carbon intensity varies dramatically by region, hour, and fuel type. This
project identifies which regions and fuel types drive the highest emissions,
when the cleanest dispatch windows occur, and builds the SQL foundation to
support that kind of intervention — giving retailers and policymakers a
data-driven basis for decisions like shifting flexible demand to low-carbon
hours.

**Core questions:**
- How does carbon intensity change over time by NEM region?
- Which fuel types drive carbon intensity spikes?
- Are there system-level patterns (e.g. high demand → higher emissions)?
- Can we identify low-carbon dispatch windows?
- How does aggregation reduce query cost while preserving insight?

## Dataset

- **Source:** [OpenElectricity API](https://openelectricity.org.au/) (formerly
  OpenNEM), via the official `openelectricity` Python client
- **Scope:** NSW1 and SA1 regions, 1 week (2026-08-10 to 2026-08-17),
  30-minute intervals, 9 fuel types (coal, gas, wind, solar, hydro, battery,
  bioenergy, distillate, pumps)
- **Metrics:** POWER (MW) and EMISSIONS (tCO2), pulled at 5-minute native
  resolution and resampled to 30-minute (power averaged, emissions summed —
  see rationale in PROJECT_LOG.md)
- **Why NSW1/SA1:** coal-heavy vs. renewables-heavy contrast makes
  comparisons meaningful for the analytical questions this project answers

## Pipeline Architecture

```
Raw data (data_pipeline.py)
    → OpenElectricity API, secondary_grouping=fueltech_group
    → 5-min → 30-min resample, battery charge/discharge collapsed
    → data/raw/{region}_sample_1week.csv

Raw demand (demand_pipeline.py)
    → OpenElectricity API, get_market(), MarketMetric.DEMAND
    → 5-min → 30-min resample (mean) — avoids a known API aggregation bug
    → data/raw/{region}_demand_1week.csv
        ↓
Staging layer (load_staging.py, load_demand_staging.py)
    → SQLite (data/energy_analytics.db)
    → stg_carbon_intensity: adds carbon_intensity = emissions / (power * 0.5)
    → stg_demand: demand_mw, kept as a separate table (no fueltech dimension)
        ↓
Analysis (run_query.py + sql/*.sql)
    → Documented, reusable .sql files run against the staging tables
```

## SQL Techniques Used

- `GROUP BY` aggregation across multiple grouping keys (region, fuel type, hour)
- `HAVING` to filter aggregated groups (excluding zero-emission fuel types
  from a "least-dirty" ranking)
- Window functions: `RANK() OVER (PARTITION BY ... ORDER BY ...)` to find
  top/bottom N per region in a single query
- Multi-layer subqueries (up to 3 levels) to sequence aggregation → derived
  calculation → ranking, since each step depends on the previous step's
  fully-resolved result
- Date/time extraction (`strftime`) to find hour-of-day patterns from
  interval timestamps
- `JOIN` with a multi-column `ON` condition (region AND interval), to
  correctly match two separate staging tables without cross-pairing
  unrelated regions at the same timestamp
- Manually implemented the Pearson correlation coefficient formula in SQL
  (SQLite has no built-in `CORR()`), using three layers of nested
  subqueries to sequence aggregation → derived calculation → final ratio

## Key Insights

1. **Coal dominates NSW1's carbon intensity** (0.89 tCO2/MWh average),
   roughly 8x bioenergy and infinitely above zero-emission sources. SA1 has no coal in its generation mix at all — its highest emitter is gas
   (0.48 tCO2/MWh).
2. **Carbon intensity peaks midday** — NSW1 is lowest
   overnight (~0.32-0.36) and peaks around 1pm (~0.68), likely driven by
   afternoon demand outweighing solar's downward effect  which is a lead for future investigation against demand data.
3. **SA1 is roughly 10x cleaner than NSW1 even at its worst ranked hour** —
   SA1's 3 lowest-carbon hours average 0.033-0.037 tCO2/MWh, versus NSW1's 0.32-0.33.
4. **A pre-computed per-row ratio (carbon_intensity) is only valid at the
   grain it was calculated at** — an early attempt to average it directly
   across fuel types produced a flat, physically implausible ~0.17 result
   for every hour. Fixed by recalculating from summed totals
   (sum emissions ÷ sum power) rather than averaging pre-computed ratios.
5. **Demand correlates with carbon intensity, moderately — more so in
   NSW1 (r = 0.43) than SA1 (r = 0.28).** NSW1's coal/gas-dependent grid
   tracks demand fairly directly; SA1's weaker correlation reflects solar
   dominating its intensity regardless of exact demand level (near-zero
   at midday almost independent of demand).

## Business Recommendations

- NSW1's overnight hours (01:00-03:00) are the most reliable low-carbon
  dispatch window for shifting flexible demand.
- SA1 offers consistently low-carbon dispatch across nearly all hours,
  making it a stronger candidate for renewable-heavy load-shifting programs.
- The midday intensity peak in NSW1 warrants further investigation against demand data to confirm as demand-driven. It suggests targeted
  demand-response programs during afternoon peak hours could meaningfully
  reduce emissions.
- The moderate demand-carbon intensity correlation in NSW1 (r = 0.43)
  supports targeted demand-response programs during high-demand periods
  as a viable emissions-reduction lever; SA1's weaker correlation (r = 0.28)
  suggests renewable availability, not demand timing, is the dominant
  lever there.

## Repository Structure

```
energy-market-analysis-afrin/
├── PROJECT_LOG.md # Full decision log + debugging journey
├── README.md
├── data/
│ ├── raw/ # Git-ignored, regenerable via data_pipeline.py
│ ├── sample_data/ # Small committed samples for portfolio visibility
│ └── energy_analytics.db # Git-ignored SQLite database
├── python/
│ └── data_pipeline.py # API pull, resample, save to raw/
├── scripts/
│   ├── setup_database.py
│   ├── load_staging.py
│   ├── load_demand_staging.py
│   ├── run_query.py
│   └── check_carbon_intensity.py
└── sql/
    ├── fueltype_carbon_intensity_ranking.sql
    ├── top_fueltype_per_region.sql
    ├── least_dirty_fueltype_per_region.sql
    ├── carbon_intensity_by_hour_nsw1.sql
    ├── lowest_carbon_windows_per_region.sql
    ├── demand_correlation.sql
    └── demand_carbon_correlation.sql
    ```

## Next Steps

- Extend to a longer date range (currently testing 60 days, scaling toward
  a full 12-month pull) for seasonal pattern analysis
- Build a Tableau/Power BI dashboard on top of the analytical queries above