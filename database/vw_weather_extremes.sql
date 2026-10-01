CREATE OR REPLACE VIEW vw_weather_extremes_detailed AS
WITH RankedWeather AS (
    SELECT 
        z.state_name,
        z.city_name,
        t.temperature_c,
        t.wind_speed_ms,
        t.humidity_pct,
        t.timestamp,
        ROW_NUMBER() OVER (ORDER BY t.temperature_c ASC) as min_temp_rank,
        ROW_NUMBER() OVER (ORDER BY t.temperature_c DESC) as max_temp_rank,
        ROW_NUMBER() OVER (ORDER BY t.wind_speed_ms DESC) as max_wind_rank,
        ROW_NUMBER() OVER (ORDER BY t.wind_speed_ms ASC) as min_wind_rank
    FROM fact_weather_telemetry t
    JOIN dim_zones z ON t.zone_id = z.zone_id
    WHERE t.timestamp IS NOT NULL
)
SELECT 
    'Lowest Temperature' AS metric_type,
    state_name,
    city_name,
    temperature_c AS value,
    timestamp
FROM RankedWeather WHERE min_temp_rank = 1

UNION ALL

SELECT 
    'Highest Temperature' AS metric_type,
    state_name,
    city_name,
    temperature_c AS value,
    timestamp
FROM RankedWeather WHERE max_temp_rank = 1

UNION ALL

SELECT 
    'Peak Wind Speed' AS metric_type,
    state_name,
    city_name,
    wind_speed_ms AS value,
    timestamp
FROM RankedWeather WHERE max_wind_rank = 1

UNION ALL

SELECT 
    'Slowest Wind Speed' AS metric_type,
    state_name,
    city_name,
    wind_speed_ms AS value,
    timestamp
FROM RankedWeather WHERE min_wind_rank = 1;