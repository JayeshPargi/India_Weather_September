from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import psycopg2
import requests
from config import DB_CONFIG, INDIA_WEATHER_GRID


def fetch_zone_weather(zone_info: dict) -> tuple[dict, dict | None]:
  """Fetches historical hourly weather time-series data for a specific window

  from Open-Meteo Archive API.
  """
  lat = zone_info["lat"]
  lon = zone_info["lon"]
  # Using the Historical Archive API endpoint to backfill September data (Sept 1 - Sept 30)
  url = (
      f"https://archive-api.open-meteo.com/v1/archive?"
      f"latitude={lat}&longitude={lon}&"
      f"start_date=2026-09-01&end_date=2026-09-30&"
      f"hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,cloud_cover"
  )
  try:
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    data = response.json()
    return zone_info, data.get("hourly", {})
  except Exception as e:
    print(
        f"Error fetching historical data for {zone_info['state']} -"
        f" {zone_info['city']}: {e}"
    )
    return zone_info, None


def main():
  print(
      "Starting Historical Weather Ingestion Pipeline for September Storm"
      " Window (252 Zones)..."
  )

  # Connect to PostgreSQL database
  conn = psycopg2.connect(**DB_CONFIG)
  cursor = conn.cursor()

  zone_id_map = {}

  # 1. Sync dim_zones dimension table and cache zone IDs
  print("Syncing dim_zones with PostgreSQL...")
  for item in INDIA_WEATHER_GRID:
    cursor.execute(
        """
            INSERT INTO dim_zones (state_name, zone_code, city_name, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (state_name, zone_code) 
            DO UPDATE SET city_name = EXCLUDED.city_name, 
                          latitude = EXCLUDED.latitude, 
                          longitude = EXCLUDED.longitude
            RETURNING zone_id;
        """,
        (item["state"], item["zone"], item["city"], item["lat"], item["lon"]),
    )
    zone_id = cursor.fetchone()[0]
    zone_id_map[(item["state"], item["zone"])] = zone_id

  conn.commit()
  print(f"Successfully synced {len(zone_id_map)} zones in dim_zones.")

  # 2. Concurrently Fetch Historical Hourly Weather via ThreadPoolExecutor
  print(
      "Fetching historical hourly telemetry concurrently from Open-Meteo"
      " Archive API..."
  )
  telemetry_records = []

  with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {
        executor.submit(fetch_zone_weather, zone): zone
        for zone in INDIA_WEATHER_GRID
    }

    for future in as_completed(futures):
      zone_info, hourly_data = future.result()
      if not hourly_data:
        continue

      zone_id = zone_id_map.get((zone_info["state"], zone_info["zone"]))
      if not zone_id:
        continue

      times = hourly_data.get("time", [])
      temps = hourly_data.get("temperature_2m", [])
      humidities = hourly_data.get("relative_humidity_2m", [])
      winds = hourly_data.get("wind_speed_10m", [])
      clouds = hourly_data.get("cloud_cover", [])

      # Unpack the hourly records for this coordinate point across the month
      for t, temp, hum, wind, cloud in zip(
          times, temps, humidities, winds, clouds
      ):
        dt = datetime.fromisoformat(t)
        telemetry_records.append((zone_id, dt, temp, hum, wind, cloud))

  # 3. Batch Insert Hourly Telemetry into Fact Table
  print(
      f"Batch inserting {len(telemetry_records)} historical telemetry records"
      " into PostgreSQL..."
  )
  cursor.executemany(
      """
        INSERT INTO fact_weather_telemetry 
        (zone_id, timestamp, temperature_c, humidity_pct, wind_speed_ms, cloud_cover_pct)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (zone_id, timestamp) DO NOTHING;
    """,
      telemetry_records,
  )

  conn.commit()
  cursor.close()
  conn.close()
  print(
      "Pipeline Execution Complete! Historical September storm data loaded"
      " successfully."
  )


if __name__ == "__main__":
  main()