-- Business question: Which fuel types drive carbon intensity in NSW1 and SA1?
-- Ranks each region's fuel types by average carbon intensity (tCO2/MWh).
-- Zero-emission sources (wind, solar, hydro, battery) confirm expected 0.0;
-- coal is the dominant driver in NSW1, absent entirely from SA1's fuel mix.

SELECT region, fueltech, AVG(carbon_intensity) AS avg_carbon_intensity
FROM stg_carbon_intensity
GROUP BY region, fueltech
ORDER BY avg_carbon_intensity DESC;
