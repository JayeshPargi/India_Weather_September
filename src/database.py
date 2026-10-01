import psycopg2
from config import DB_CONFIG


def get_db_connection():
    """Establishes and returns a PostgreSQL connection."""
    return psycopg2.connect(**DB_CONFIG)


def upsert_zones(cursor, grid_data):
    """Syncs the dimension zones to ensure cities and coordinates are up to date."""
    print("Syncing dimension zones in PostgreSQL...")
    for zone in grid_data:
        cursor.execute(
            """
            INSERT INTO dim_zones (state_name, zone_code, city_name, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (state_name, zone_code) 
            DO UPDATE SET city_name = EXCLUDED.city_name, 
                          latitude = EXCLUDED.latitude, 
                          longitude = EXCLUDED.longitude;
        """,
            (
                zone["state"],
                zone["zone"],
                zone["city"],
                zone["lat"],
                zone["lon"],
            ),
        )


def insert_weather_telemetry(cursor, weather_results):
    """Inserts processed time-series weather records into the fact table."""
    print(f"Inserting {len(weather_results)} telemetry records...")
    inserted_count = 0

    for item in weather_results:
        cursor.execute(
            """
            INSERT INTO fact_weather_telemetry 
            (zone_id, timestamp, temperature_c, humidity_pct, wind_speed_ms, cloud_cover_pct)
            SELECT zone_id, %s, %s, %s, %s, %s
            FROM dim_zones
            WHERE state_name = %s AND zone_code = %s;
        """,
            (
                item["timestamp"],
                item["temperature"],
                item["humidity"],
                item["wind_speed"],
                item["cloud_cover"],
                item["state"],
                item["zone"],
            ),
        )
        inserted_count += 1

    print(f"Successfully loaded {inserted_count} rows.")