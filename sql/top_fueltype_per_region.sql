
-- Business question: What is the single highest-carbon-intensity fuel type
-- in each region? Uses RANK() to identify the #1 emitter per region in one
-- query, rather than manually reading a sorted list -- this scales correctly
-- even if more regions were added later.

SELECT region, fueltech, avg_carbon_intensity, rank
FROM (
    SELECT
        region,
        fueltech,
        AVG(carbon_intensity) AS avg_carbon_intensity,
        RANK() OVER (PARTITION BY region ORDER BY AVG(carbon_intensity) DESC) AS rank
    FROM stg_carbon_intensity
    GROUP BY region, fueltech
)
WHERE rank = 1;
