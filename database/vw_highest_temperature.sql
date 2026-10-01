CREATE OR REPLACE VIEW vw_highest_temperatures AS
WITH city_max_temps AS (
    SELECT 
        z.state_name,
        z.city_name,
        t.timestamp,
        t.temperature_c,
        t.wind_speed_ms,
        ROW_NUMBER() OVER (PARTITION BY z.state_name, z.city_name ORDER BY t.temperature_c DESC) AS city_rank
    FROM dim_zones z
    JOIN fact_weather_telemetry t ON z.zone_id = t.zone_id
    WHERE t.timestamp IS NOT NULL
)
SELECT 
    state_name,
    city_name,
    timestamp AS highest_temp_timestamp,
    temperature_c,
    wind_speed_ms
FROM city_max_temps
WHERE city_rank = 1
ORDER BY temperature_c DESC
LIMIT 25;