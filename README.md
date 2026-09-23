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
Raw data (data_pipeline.py)
→ OpenElectricity API, secondary_grouping=fueltech_group
→ 5-min → 30-min resample, battery charge/discharge collapsed
→ data/raw/{region}_sample_1week.csv
↓
Staging layer (load_staging.py)
→ SQLite (data/energy_analytics.db)
→ stg_carbon_intensity: adds carbon_intensity = emissions / (power * 0.5)
→ divide-by-zero guarded, verified via check_carbon_intensity.py
↓
Analysis (run_query.py + sql/*.sql)
→ Documented, reusable .sql files run against the staging table


Full rationale for every architectural decision — including debugging
detours (API auth issues, response format discovery, a weighted-average
bug) — is logged in `PROJECT_LOG.md`.

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

## Business Recommendations

- NSW1's overnight hours (01:00-03:00) are the most reliable low-carbon
  dispatch window for shifting flexible demand.
- SA1 offers consistently low-carbon dispatch across nearly all hours,
  making it a stronger candidate for renewable-heavy load-shifting programs.
- The midday intensity peak in NSW1 warrants further investigation against demand data to confirm as demand-driven. It suggests targeted
  demand-response programs during afternoon peak hours could meaningfully
  reduce emissions.

## Repository Structure
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
│ ├── setup_database.py
│ ├── load_staging.py
│ ├── run_query.py # Reusable .sql file runner
│ └── check_carbon_intensity.py
└── sql/
├── fueltype_carbon_intensity_ranking.sql
├── top_fueltype_per_region.sql
├── least_dirty_fueltype_per_region.sql
├── carbon_intensity_by_hour_nsw1.sql
└── lowest_carbon_windows_per_region.sql

## Next Steps

- Pull DEMAND metric to directly test the demand-correlation hypothesis
  behind the midday carbon intensity peak
- Extend to full 12-month range for seasonal pattern analysis
- Build a Tableau/Power BI dashboard on top of the analytical queries above