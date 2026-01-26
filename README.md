# Flask Weather Station

A Python Flask weather app modeled after the UI of
https://github.com/elewin/pi-weather-station. The layout mirrors the original
map + info panel design, with one key change: the chart area is replaced by
daily forecast blocks that show high/low, sunrise/sunset, and condition.

## Features

- Map view with click-to-update location (Leaflet, Mapbox optional)
- Current conditions with temperature, wind, cloud cover, humidity, precip
- 7-day forecast blocks with sunrise/sunset and conditions
- Clock and sunrise/sunset display
- Sample-data fallback when live weather is unavailable
- Responsive layout for smaller viewports

## Setup

### 1. Create Virtual Environment (Recommended)

```bash
python -m venv venv
```

Activate the virtual environment:

Windows PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```

Windows Command Prompt:
```cmd
venv\Scripts\activate.bat
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy the example environment file and update the values:

Windows PowerShell:
```powershell
Copy-Item "env_example.txt" ".env"
```

Windows Command Prompt:
```cmd
copy env_example.txt .env
```

Key settings:

- `MAPBOX_ACCESS_TOKEN` (optional) for Mapbox tiles and styling
- `LOCATIONIQ_API_KEY` (optional) for reverse geocoding city names
- `DEFAULT_LOCATION_NAME`, `DEFAULT_LAT`, `DEFAULT_LON` for the initial map location
- `WEATHER_UNITS` set to `imperial` or `metric`
- `WEATHER_MODE` set to `auto` (live + fallback) or `sample` (offline demo)

### 4. Run the Application

```bash
python app.py
```

Open http://localhost:5000 in your browser.

## Weather Data Sources

This app uses Open-Meteo for live weather because it does not require an API
key and is reliable for demos. The design is intentionally aligned with the
Pi Weather Station layout, and Mapbox tiles are supported if you provide a
token. If the live weather API is unavailable, the app falls back to sample
data to keep the UI functional.

## API Endpoints

- `GET /` - Main weather station UI
- `GET /api/weather?lat=<lat>&lon=<lon>` - JSON weather payload

## Testing

UI tests are in `tests/` and use Selenium.

```bash
pytest tests/ -v
```

## Project Documentation

- `SETUP_DECISIONS_LOG.md` - Detailed reasoning behind setup decisions
- `DEVELOPMENT_LOG.md` - Running record of prompts and changes

## License

MIT License (same licensing approach as the original inspiration).
