# Flask Weather Station

A Python Flask weather dashboard inspired by [pi-weather-station](https://github.com/elewin/pi-weather-station),
rebuilt with a Flask backend and a UI that keeps the same visual rhythm while
replacing the highlighted chart area with daily forecast blocks.

## Features

- Dark, full-screen weather dashboard layout
- Mapbox-powered map panel (static image)
- Live data via Tomorrow.io (ClimaCell v4) forecast API
- Daily forecast blocks with high/low, sunrise/sunset, condition
- Sample data fallback when API keys are missing
- Responsive layout for tablet and mobile widths

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

This app can run in sample mode, but live data requires:

- **Mapbox** (map tiles + geocoding): https://account.mapbox.com/
- **Tomorrow.io** (ClimaCell v4 weather API): https://www.tomorrow.io/

### 4. Set Environment Variables

Copy the template:

```bash
cp env_example.txt .env
```

Edit `.env` and provide your keys and defaults:

```env
MAPBOX_API_KEY=your_mapbox_key_here
TOMORROW_API_KEY=your_tomorrow_io_key_here
DEFAULT_LOCATION=Dallas, Texas
DEFAULT_LAT=32.7767
DEFAULT_LON=-96.7970
DEFAULT_TIMEZONE=America/Chicago
WEATHER_UNITS=imperial
MAP_ZOOM=8
SECRET_KEY=your-secret-key-here-change-this-in-production
```

### 5. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`.

## Usage

- The dashboard loads the default location.
- Add `?location=City, State` to the URL to override the location for a session.
- If API keys are missing, the UI shows sample forecast blocks.

## API Endpoints

- `GET /`: Main weather dashboard

## Testing

UI tests are configured with Selenium and pytest.

```bash
pip install -r requirements-dev.txt
pytest tests/
```

## Notes

- The Mapbox map uses a static image to keep the UI performant.
- Tomorrow.io data is normalized in the backend so the UI can stay simple.
- The daily blocks intentionally replace chart-based sections from the original UI.
