from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from datetime import datetime, timedelta
from urllib import request as urlrequest
from urllib import parse as urlparse
import json
import os
import time

load_dotenv()

app = Flask(__name__)

DEFAULT_LOCATION_NAME = os.getenv("DEFAULT_LOCATION_NAME", "Dallas, Texas")
DEFAULT_LAT = float(os.getenv("DEFAULT_LAT", "32.7767"))
DEFAULT_LON = float(os.getenv("DEFAULT_LON", "-96.7970"))
WEATHER_UNITS = os.getenv("WEATHER_UNITS", "imperial").lower()
WEATHER_MODE = os.getenv("WEATHER_MODE", "auto").lower()
WEATHER_CACHE_TTL = int(os.getenv("WEATHER_CACHE_TTL", "600"))
MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN", "")
LOCATIONIQ_API_KEY = os.getenv("LOCATIONIQ_API_KEY", "")
DEFAULT_MAP_ZOOM = int(os.getenv("DEFAULT_MAP_ZOOM", "8"))

WEATHER_CACHE = {"timestamp": 0, "lat": None, "lon": None, "units": None, "data": None}


def normalize_units():
    units = WEATHER_UNITS if WEATHER_UNITS in ("imperial", "metric") else "imperial"
    temp_unit = "F" if units == "imperial" else "C"
    wind_unit = "mph" if units == "imperial" else "m/s"
    return units, temp_unit, wind_unit


def round_value(value):
    try:
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


def format_time_str(value):
    if not value:
        return ""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value
    return parsed.strftime("%I:%M %p").lstrip("0")


def format_day_label(value):
    if not value:
        return ""
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return value
    return parsed.strftime("%a")


def map_weather_code(code, is_day=True):
    if code is None:
        return "Unknown", "fa-cloud"
    if code == 0:
        return "Clear", "fa-sun" if is_day else "fa-moon"
    if code in (1, 2):
        return "Partly cloudy", "fa-cloud-sun" if is_day else "fa-cloud"
    if code == 3:
        return "Overcast", "fa-cloud"
    if code in (45, 48):
        return "Fog", "fa-smog"
    if code in (51, 53, 55, 56, 57):
        return "Drizzle", "fa-cloud-rain"
    if code in (61, 63, 65):
        return "Rain", "fa-cloud-showers-heavy"
    if code in (66, 67):
        return "Freezing rain", "fa-cloud-showers-heavy"
    if code in (71, 73, 75, 77):
        return "Snow", "fa-snowflake"
    if code in (80, 81, 82):
        return "Rain showers", "fa-cloud-showers-heavy"
    if code in (85, 86):
        return "Snow showers", "fa-snowflake"
    if code in (95, 96, 99):
        return "Thunderstorm", "fa-bolt"
    return "Unknown", "fa-cloud"


def fetch_json(url, timeout=3):
    with urlrequest.urlopen(url, timeout=timeout) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def get_location_name(lat, lon):
    if LOCATIONIQ_API_KEY:
        params = {
            "key": LOCATIONIQ_API_KEY,
            "lat": lat,
            "lon": lon,
            "format": "json",
        }
        url = f"https://us1.locationiq.com/v1/reverse.php?{urlparse.urlencode(params)}"
        try:
            payload = fetch_json(url, timeout=3)
            address = payload.get("address", {})
            city = address.get("city") or address.get("town") or address.get("village")
            state = address.get("state")
            country = address.get("country")
            if city and state:
                return f"{city}, {state}"
            if city and country:
                return f"{city}, {country}"
            display = payload.get("display_name")
            if display:
                return display.split(",")[0]
        except Exception:
            pass
    if abs(lat - DEFAULT_LAT) < 0.01 and abs(lon - DEFAULT_LON) < 0.01:
        return DEFAULT_LOCATION_NAME
    return f"{lat:.2f}, {lon:.2f}"


def build_weather_payload(lat, lon, current, daily, temp_unit, wind_unit):
    location_name = get_location_name(lat, lon)
    sun_times = {"sunrise": "", "sunset": ""}
    if daily:
        sun_times = {"sunrise": daily[0]["sunrise"], "sunset": daily[0]["sunset"]}
    return {
        "location": {"name": location_name, "lat": lat, "lon": lon},
        "current": current,
        "sun": sun_times,
        "daily": daily,
        "units": {"temp": temp_unit, "wind": wind_unit},
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }


def fetch_open_meteo(lat, lon):
    units, temp_unit, wind_unit = normalize_units()
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "hourly": "relativehumidity_2m,precipitation_probability,cloudcover",
        "daily": "temperature_2m_max,temperature_2m_min,sunrise,sunset,weathercode",
        "timezone": "auto",
        "temperature_unit": "fahrenheit" if units == "imperial" else "celsius",
        "windspeed_unit": "mph" if units == "imperial" else "ms",
    }
    url = f"https://api.open-meteo.com/v1/forecast?{urlparse.urlencode(params)}"
    payload = fetch_json(url, timeout=3)

    current_weather = payload.get("current_weather", {})
    current_time = current_weather.get("time")
    hourly = payload.get("hourly", {})
    hourly_times = hourly.get("time", [])
    try:
        hourly_idx = hourly_times.index(current_time) if current_time in hourly_times else 0
    except ValueError:
        hourly_idx = 0

    humidity = round_value(_safe_get(hourly.get("relativehumidity_2m"), hourly_idx))
    precip = round_value(_safe_get(hourly.get("precipitation_probability"), hourly_idx))
    cloud = round_value(_safe_get(hourly.get("cloudcover"), hourly_idx))
    is_day = current_weather.get("is_day", 1) == 1
    condition, icon = map_weather_code(current_weather.get("weathercode"), is_day=is_day)

    current = {
        "temp": round_value(current_weather.get("temperature")),
        "condition": condition,
        "icon": icon,
        "humidity": humidity,
        "precip_probability": precip,
        "cloud_cover": cloud,
        "wind_speed": round_value(current_weather.get("windspeed")),
        "wind_unit": wind_unit,
        "temp_unit": temp_unit,
    }

    daily_payload = payload.get("daily", {})
    daily = []
    for date, high, low, sunrise, sunset, code in zip(
        daily_payload.get("time", []),
        daily_payload.get("temperature_2m_max", []),
        daily_payload.get("temperature_2m_min", []),
        daily_payload.get("sunrise", []),
        daily_payload.get("sunset", []),
        daily_payload.get("weathercode", []),
    ):
        daily_condition, daily_icon = map_weather_code(code, is_day=True)
        daily.append(
            {
                "date": date,
                "day": format_day_label(date),
                "high": round_value(high),
                "low": round_value(low),
                "condition": daily_condition,
                "icon": daily_icon,
                "sunrise": format_time_str(sunrise),
                "sunset": format_time_str(sunset),
            }
        )

    weather_payload = build_weather_payload(lat, lon, current, daily, temp_unit, wind_unit)
    weather_payload["meta"] = {"source": "open-meteo", "mode": "live"}
    return weather_payload


def build_sample_weather(lat, lon):
    units, temp_unit, wind_unit = normalize_units()
    base_date = datetime.now()
    base_high = 95
    base_low = 75
    base_temp = 92
    base_wind = 8
    conditions = [
        ("Partly cloudy", "fa-cloud-sun"),
        ("Sunny", "fa-sun"),
        ("Overcast", "fa-cloud"),
        ("Rain showers", "fa-cloud-showers-heavy"),
        ("Clear", "fa-moon"),
        ("Thunderstorm", "fa-bolt"),
        ("Fog", "fa-smog"),
    ]

    def convert_temp(value):
        if units == "metric":
            return (value - 32) * 5 / 9
        return value

    def convert_speed(value):
        if units == "metric":
            return value * 0.44704
        return value

    daily = []
    for offset in range(7):
        date = base_date + timedelta(days=offset)
        condition, icon = conditions[offset % len(conditions)]
        sunrise_dt = date.replace(hour=6, minute=40) + timedelta(minutes=offset)
        sunset_dt = date.replace(hour=19, minute=55) - timedelta(minutes=offset)
        daily.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "day": date.strftime("%a"),
                "high": round_value(convert_temp(base_high - offset)),
                "low": round_value(convert_temp(base_low - offset)),
                "condition": condition,
                "icon": icon,
                "sunrise": sunrise_dt.strftime("%I:%M %p").lstrip("0"),
                "sunset": sunset_dt.strftime("%I:%M %p").lstrip("0"),
            }
        )

    current = {
        "temp": round_value(convert_temp(base_temp)),
        "condition": daily[0]["condition"],
        "icon": daily[0]["icon"],
        "humidity": 50,
        "precip_probability": 40,
        "cloud_cover": 35,
        "wind_speed": round_value(convert_speed(base_wind)),
        "wind_unit": wind_unit,
        "temp_unit": temp_unit,
    }

    weather_payload = build_weather_payload(lat, lon, current, daily, temp_unit, wind_unit)
    weather_payload["meta"] = {"source": "sample", "mode": "sample"}
    return weather_payload


def _safe_get(values, idx):
    if not values:
        return None
    if idx is None or idx < 0 or idx >= len(values):
        return values[0]
    return values[idx]


def get_weather_data(lat=None, lon=None):
    if lat is None:
        lat = DEFAULT_LAT
    if lon is None:
        lon = DEFAULT_LON

    cache_key = (round(lat, 4), round(lon, 4), WEATHER_UNITS)
    now = time.time()
    if (
        WEATHER_CACHE["data"]
        and WEATHER_CACHE["lat"] == cache_key[0]
        and WEATHER_CACHE["lon"] == cache_key[1]
        and WEATHER_CACHE["units"] == cache_key[2]
        and now - WEATHER_CACHE["timestamp"] < WEATHER_CACHE_TTL
    ):
        return WEATHER_CACHE["data"]

    weather_payload = None
    mode = WEATHER_MODE
    if mode == "sample":
        weather_payload = build_sample_weather(lat, lon)
    else:
        try:
            weather_payload = fetch_open_meteo(lat, lon)
        except Exception:
            weather_payload = build_sample_weather(lat, lon)

    WEATHER_CACHE.update(
        {
            "timestamp": now,
            "lat": cache_key[0],
            "lon": cache_key[1],
            "units": cache_key[2],
            "data": weather_payload,
        }
    )
    return weather_payload


@app.route("/")
def index():
    weather = get_weather_data()
    app_config = {
        "mapboxToken": MAPBOX_ACCESS_TOKEN,
        "mapZoom": DEFAULT_MAP_ZOOM,
        "mapStyle": "dark-v11",
    }
    return render_template("index.html", weather=weather, app_config=app_config)


@app.route("/api/weather")
def api_weather():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    weather = get_weather_data(lat=lat, lon=lon)
    return jsonify(weather)


if __name__ == "__main__":
    app.run(debug=True)
