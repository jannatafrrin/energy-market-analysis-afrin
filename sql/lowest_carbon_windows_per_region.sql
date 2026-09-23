-- Business question: Which hours are the lowest-carbon-intensity dispatch
-- windows in each region? Ranks hourly carbon intensity per region using
-- RANK() and returns the top 3 cleanest hours per region.

SELECT region, hourly_intervals, avg_total_carbon_intensity, rank
FROM (
    SELECT region, hourly_intervals, avg_total_carbon_intensity,
    RANK() OVER (PARTITION BY region ORDER BY avg_total_carbon_intensity ASC) AS rank
    FROM (
        SELECT region, (total_emissions/(total_power * 0.5)) AS avg_total_carbon_intensity, hourly_intervals
        FROM (
            SELECT
                region,
                SUM(power_mw) AS total_power, SUM(emissions_tco2) AS total_emissions,
                strftime('%H', interval) AS hourly_intervals
            FROM stg_carbon_intensity
            GROUP BY region, hourly_intervals
        ) AS tier1
    ) AS tier2
) AS tier3
WHERE rank <= 3
ORDER BY region, rank;
