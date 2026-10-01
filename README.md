# India Weather September: Telemetry Command Center 🌦️📊🐍

A high-performance, analytical data pipeline and dashboard engineered to automate weather data ingestion, model regional weather extremes across India, evaluate statistical correlations, and benchmark severe wind/storm hazards.

---

## 🎨 Design & Aesthetic
* **Theme:** Dark mode (`#121212` canvas) meticulously designed for operations-center environments.
* **Accents:** High-contrast neon cyan (`#00E5FF`) to highlight critical data points, telemetry readings, and visual hierarchies.
* **Custom Formatting:** Utilized custom DAX string formatting measures to append explicit unit suffixes (`°C`) directly onto data labels for glanceable clarity.

---

## 🛠️ Tech Stack & Architecture
* **Ingestion & Pipeline Layer:** Python (Modular architecture featuring `config.py`, `database.py`, and `main.py`).
* **Database Layer:** PostgreSQL (Custom analytical SQL views for data modeling, extreme filtering, correlation, and wind benchmarking).
* **Visualization Layer:** Power BI Desktop (`Weather_Project.pbix` featuring dot/lollipop plots, scatter correlation plots, and clustered column comparisons).

---

## 📂 Repository Structure
```text
India_Weather_September/
├── assets/
│   ├── Page 1.png                <-- Overview & Temperature Extremes dashboard view
│   └── Page 2.png                <-- Wind Storm & Correlation telemetry view
├── database/
│   ├── vw_highest_temperature.sql
│   ├── vw_lowest_temperatures.sql
│   ├── vw_weather_extremes.sql
│   ├── vw_wind_storm_correlation.sql
│   └── vw_wind_temp_correlation.sql
├── report/
│   └── Weather_Project.pbix      <-- Power BI report file
├── src/
│   ├── config.py                 <-- Environment & connection variables
│   ├── database.py               <-- PostgreSQL connection & helper functions
│   └── main.py                   <-- Pipeline orchestration script
└── README.md
