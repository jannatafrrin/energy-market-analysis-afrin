
-- Business question: Excluding zero-emission sources (wind, solar, hydro,
-- battery), which fuel type is the "least dirty" emitter in each region?
-- Uses HAVING to filter out zero-average groups before RANK() runs, so the
-- ranking only considers fuel types that genuinely emit carbon.

SELECT region, fueltech, avg_carbon_intensity, rank
FROM (
    SELECT
        region,
        fueltech,
        AVG(carbon_intensity) AS avg_carbon_intensity,
        RANK() OVER (PARTITION BY region ORDER BY AVG(carbon_intensity) ASC) AS rank
    
    FROM stg_carbon_intensity
    GROUP BY region, fueltech
    HAVING avg_carbon_intensity > 0
)
WHERE rank =1;
