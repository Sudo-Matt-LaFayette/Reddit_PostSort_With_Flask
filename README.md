# Flask Weather Station

A Python Flask weather dashboard inspired by the UI of
https://github.com/elewin/pi-weather-station, rebuilt to run on a simple
Flask stack. The layout mirrors the original: a large map panel on the left,
current conditions on the right, and a weekly outlook displayed as daily
blocks (high/low, sunrise/sunset, and condition) instead of charts.

## Features

- Map panel with Mapbox static tiles
- Location search + unit toggle (imperial/metric)
- Current conditions with key stats (precip, wind, humidity)
- Daily forecast cards for the next 7 days
- Sample-data fallback when API keys are missing
- Clean, dark UI tuned for a wall display

## Setup Instructions

### 1. Create Virtual Environment (Recommended)

```bash
python -m venv venv
```

**Activate the virtual environment:**

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

### 3. Configure API Keys

1. Copy `env_example.txt` to `.env`
2. Add your Mapbox and Tomorrow.io keys

Mapbox token:
- https://account.mapbox.com/access-tokens/

Tomorrow.io key:
- https://app.tomorrow.io/development/keys

### 4. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Environment Variables

| Variable | Description | Example |
| --- | --- | --- |
| `MAPBOX_ACCESS_TOKEN` | Mapbox access token | `pk.XXXX` |
| `TOMORROW_API_KEY` | Tomorrow.io API key | `abcdef123456` |
| `DEFAULT_LOCATION` | Default search location | `Dallas, Texas` |
| `DEFAULT_UNITS` | `imperial` or `metric` | `imperial` |
| `DEFAULT_LAT` | Default latitude | `32.7767` |
| `DEFAULT_LON` | Default longitude | `-96.7970` |
| `WEATHER_USE_SAMPLE` | Force sample data mode | `false` |
| `WEATHER_CACHE_SECONDS` | Cache TTL for API calls | `600` |
| `SECRET_KEY` | Flask secret key | `change-me` |

## Usage

1. Enter a city, state, or ZIP in the location box
2. Choose imperial (F) or metric (C) units
3. Click **Update** to refresh the dashboard

If API keys are missing or unavailable, the UI will show sample data and a
status banner explaining how to enable live forecasts.

## Testing

UI tests run with Selenium and pytest. Sample mode is forced in tests to keep
the suite offline and deterministic.

```bash
pip install -r requirements-dev.txt
pytest tests/
```

## Project Notes

- The weather API integration uses Tomorrow.io v4 timelines.
- The map panel uses Mapbox static tiles to keep the client lightweight.
- Forecast charts from the original project were replaced by daily blocks
  as requested (high/low, sunrise/sunset, and condition).

## License

This project is open source and available under the MIT License.
