-- Business question: does demand correlate with carbon intensity)
    SELECT ci.region, ci.interval, ci.avg_total_carbon_intensity, d.demand_mw
    FROM (
        SELECT region, (total_emissions/(total_power * 0.5)) AS avg_total_carbon_intensity,interval
        FROM (
            SELECT
                region, interval,
                SUM(power_mw) AS total_power, SUM(emissions_tco2) AS total_emissions
            FROM stg_carbon_intensity
            GROUP BY region,interval
        ) AS tier1
    ) AS ci
JOIN stg_demand AS d 
    ON ci.region = d.region
    AND ci.interval = d.interval;
