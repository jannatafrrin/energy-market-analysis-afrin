SELECT
    region,
    (n * sum_xy - sum_x * sum_y)
    / SQRT((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y))
    AS r
FROM (
    -- LAYER 2: the six aggregates, grouped by region
    SELECT
        region,
        COUNT(*) AS n,
        SUM(demand_mw) AS sum_x,
        SUM(avg_total_carbon_intensity) AS sum_y,
        SUM(demand_mw * avg_total_carbon_intensity) AS sum_xy,
        SUM(demand_mw * demand_mw) AS sum_x2,
        SUM(avg_total_carbon_intensity * avg_total_carbon_intensity) AS sum_y2
    FROM (
        -- LAYER 1: your original working demand_correlation.sql, unchanged
        SELECT ci.region, ci.interval, ci.avg_total_carbon_intensity, d.demand_mw
        FROM (
            SELECT region, (total_emissions/(total_power * 0.5)) AS avg_total_carbon_intensity, interval
            FROM (
                SELECT
                    region, interval,
                    SUM(power_mw) AS total_power, SUM(emissions_tco2) AS total_emissions
                FROM stg_carbon_intensity
                GROUP BY region, interval
            ) AS tier1
        ) AS ci
        JOIN stg_demand AS d
            ON ci.region = d.region
            AND ci.interval = d.interval
    ) AS joined
    GROUP BY region
) AS level1;