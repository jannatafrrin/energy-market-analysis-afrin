-- Business question: How does NSW1's carbon intensity vary by hour of day?
-- Extracts hour from the 30-min interval timestamp using strftime, so two
-- half-hourly readings (e.g. 00:00 and 00:30) collapse into one hour bucket.

SELECT region, (total_emissions/(total_power * 0.5)) AS avg_total_carbon_intensity,hourly_intervals
FROM (
    SELECT
        region,
        SUM(power_mw) AS total_power, SUM(emissions_tco2) AS total_emissions,
        strftime('%H', interval) AS hourly_intervals
    FROM stg_carbon_intensity
    GROUP BY region, hourly_intervals 

)
WHERE region = 'NSW1'
ORDER BY hourly_intervals;

