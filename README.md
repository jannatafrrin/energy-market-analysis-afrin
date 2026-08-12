# NEM Carbon Intensity Analytics

## 1. Business Problem
How can market participants, policymakers, or large energy users track and
reduce carbon intensity in the National Electricity Market (NEM) without
increasing system costs?

Carbon intensity in the NEM varies dramatically by region and hour. This
project identifies which regions spike most, which fuel types are
responsible, and when — giving retailers and policymakers a data-driven
basis for intervention.

**Core questions:**
- How does carbon intensity change over time by NEM region?
- Which fuel types drive carbon intensity spikes?
- Are there system-level patterns (e.g. high demand → higher emissions)?
- Can we identify low-carbon dispatch windows?
- How does aggregation reduce query cost while preserving insight?

## 2. Dataset Source
_To be filled in once dataset is selected (AEMO / OpenNEM)._

## 3. Data Pipeline Architecture
Raw → Staging → Analytics (star schema), following AEMO's dispatch/emissions
data structure.

```
raw_generation_dispatch, raw_prices, raw_demand, raw_emissions
        ↓
stg_generation_dispatch, stg_prices, stg_units
        ↓
fact_hourly_generation, fact_daily_emissions, fact_regional_energy_summary
dim_generator, dim_region, dim_fuel_type
```

## 4. SQL Techniques Used
_To be filled in as the project develops (joins, CTEs, window functions,
etc. — each tied to a specific business question)._

## 5. Key Insights
_To be filled in after analysis._

## 6. Business Recommendations
_To be filled in after analysis._

---
### Repo structure
```
energy-market-analytics-project/
├── README.md
├── data/sample_data/
├── sql/
│   ├── staging_queries.sql
│   ├── warehouse_creation.sql
│   └── analytical_queries.sql
├── python/data_pipeline.py
├── dashboards/screenshots/
└── documentation/business_problem.md
```
