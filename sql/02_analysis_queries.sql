-- NRW air quality — the queries I ran in Athena
-- Mahmoud Khatab


-- How many readings do I have in total?  -> about 2.5M
SELECT COUNT(*) AS total_readings
FROM openaq_db.measurements;

-- How are the readings split across pollutants?
SELECT parameter, COUNT(*) AS n
FROM openaq_db.measurements
GROUP BY parameter
ORDER BY n DESC;

-- Average and peak level for each pollutant.
-- Values are stored as text, so I TRY_CAST them to numbers first
-- (TRY_CAST returns NULL for any junk value, which AVG just ignores).
SELECT parameter,
       ROUND(AVG(TRY_CAST(value AS DOUBLE)), 2) AS avg_value,
       ROUND(MAX(TRY_CAST(value AS DOUBLE)), 2) AS max_value,
       COUNT(*) AS n
FROM openaq_db.measurements
GROUP BY parameter
ORDER BY avg_value DESC;

-- This is the summary I exported to Tableau: the monthly average for
-- each station and pollutant, with the coordinates for the map.
-- I drop anything outside 0..2000 to get rid of negative readings and
-- obvious sensor spikes, and substr(datetime,1,7) keeps just "YYYY-MM".
SELECT
  location_id,
  location,
  CAST(lat AS DOUBLE) AS lat,
  CAST(lon AS DOUBLE) AS lon,
  parameter,
  substr(datetime, 1, 7) AS month,
  ROUND(AVG(TRY_CAST(value AS DOUBLE)), 2) AS avg_value,
  COUNT(*) AS n_readings
FROM openaq_db.measurements
WHERE TRY_CAST(value AS DOUBLE) BETWEEN 0 AND 2000
GROUP BY location_id, location, lat, lon, parameter, substr(datetime, 1, 7)
ORDER BY location_id, parameter, month;
