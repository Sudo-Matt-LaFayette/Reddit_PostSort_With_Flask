from datetime import datetime, timedelta
import os
import time

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request


load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me")

DEFAULT_LOCATION = os.environ.get("DEFAULT_LOCATION", "Dallas, Texas")
DEFAULT_UNITS = os.environ.get("DEFAULT_UNITS", "imperial").lower()
DEFAULT_LAT = float(os.environ.get("DEFAULT_LAT", "32.7767"))
DEFAULT_LON = float(os.environ.get("DEFAULT_LON", "-96.7970"))

MAPBOX_ACCESS_TOKEN = os.environ.get("MAPBOX_ACCESS_TOKEN", "")
TOMORROW_API_KEY = os.environ.get("TOMORROW_API_KEY", "")
USE_SAMPLE_DATA = os.environ.get("WEATHER_USE_SAMPLE", "").lower() in ("1", "true", "yes")

WEATHER_CACHE_SECONDS = int(os.environ.get("WEATHER_CACHE_SECONDS", "600"))

UNIT_LABELS = {
    "imperial": {"temp": "F", "speed": "mph"},
    "metric": {"temp": "C", "speed": "m/s"},
}

WEATHER_CODE_MAP = {
    0: ("Unknown", "fa-circle-question"),
    1000: ("Clear", "fa-sun"),
    1100: ("Mostly Clear", "fa-cloud-sun"),
    1101: ("Partly Cloudy", "fa-cloud-sun"),
    1102: ("Mostly Cloudy", "fa-cloud"),
    1001: ("Cloudy", "fa-cloud"),
    2000: ("Fog", "fa-smog"),
    2100: ("Light Fog", "fa-smog"),
    4000: ("Drizzle", "fa-cloud-rain"),
    4001: ("Rain", "fa-cloud-showers-heavy"),
    4200: ("Light Rain", "fa-cloud-rain"),
    4201: ("Heavy Rain", "fa-cloud-showers-heavy"),
    5000: ("Snow", "fa-snowflake"),
    5001: ("Flurries", "fa-snowflake"),
    5100: ("Light Snow", "fa-snowflake"),
    5101: ("Heavy Snow", "fa-snowflake"),
    6000: ("Freezing Drizzle", "fa-icicles"),
    6001: ("Freezing Rain", "fa-icicles"),
    6200: ("Light Freezing Rain", "fa-icicles"),
    6201: ("Heavy Freezing Rain", "fa-icicles"),
    7000: ("Ice Pellets", "fa-icicles"),
    7101: ("Heavy Ice Pellets", "fa-icicles"),
    7102: ("Light Ice Pellets", "fa-icicles"),
    8000: ("Thunderstorm", "fa-cloud-bolt"),
}

_weather_cache = {}
_geocode_cache = {}


def normalize_units(units):
    if units in UNIT_LABELS:
        return units
    return DEFAULT_UNITS if DEFAULT_UNITS in UNIT_LABELS else "imperial"


def parse_iso_time(value):
    if not value:
        return None
    if value.endswith("Z"):
        value = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def format_time(dt):
    if not dt:
        return "--"
    return dt.strftime("%I:%M %p").lstrip("0")


def format_date(dt):
    if not dt:
        return "--"
    return dt.strftime("%A %B %d").replace(" 0", " ")


def wind_degrees_to_compass(degrees):
    if degrees is None:
        return ""
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = int((degrees + 22.5) / 45) % 8
    return directions[index]


def describe_weather(code):
    if code is None:
        return WEATHER_CODE_MAP[0]
    return WEATHER_CODE_MAP.get(int(code), WEATHER_CODE_MAP[0])


def build_map_url(lat, lon):
    if not MAPBOX_ACCESS_TOKEN or USE_SAMPLE_DATA:
        return None
    marker = f"pin-s+3fb5ff({lon},{lat})"
    return (
        "https://api.mapbox.com/styles/v1/mapbox/dark-v11/static/"
        f"{marker}/{lon},{lat},7,0,0/1200x800"
        f"?access_token={MAPBOX_ACCESS_TOKEN}"
    )


def resolve_location(query):
    cleaned = query.strip() if query else DEFAULT_LOCATION
    if USE_SAMPLE_DATA or not MAPBOX_ACCESS_TOKEN:
        return {"name": cleaned, "lat": DEFAULT_LAT, "lon": DEFAULT_LON, "source": "sample"}

    cache_key = cleaned.lower()
    cached = _geocode_cache.get(cache_key)
    if cached and time.time() - cached["timestamp"] < WEATHER_CACHE_SECONDS:
        return cached["data"]

    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{cleaned}.json"
    params = {"access_token": MAPBOX_ACCESS_TOKEN, "limit": 1}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        features = data.get("features", [])
        if not features:
            return {"name": cleaned, "lat": DEFAULT_LAT, "lon": DEFAULT_LON, "source": "fallback"}

        feature = features[0]
        lon, lat = feature["center"]
        location = {
            "name": feature.get("place_name", cleaned),
            "lat": float(lat),
            "lon": float(lon),
            "source": "mapbox",
        }
        _geocode_cache[cache_key] = {"timestamp": time.time(), "data": location}
        return location
    except (requests.RequestException, ValueError, KeyError):
        return {"name": cleaned, "lat": DEFAULT_LAT, "lon": DEFAULT_LON, "source": "fallback"}


def fetch_weather_timelines(lat, lon, units):
    url = "https://api.tomorrow.io/v4/timelines"
    params = {
        "location": f"{lat},{lon}",
        "fields": [
            "temperature",
            "temperatureApparent",
            "temperatureMin",
            "temperatureMax",
            "humidity",
            "windSpeed",
            "windDirection",
            "precipitationProbability",
            "weatherCode",
            "sunriseTime",
            "sunsetTime",
            "cloudCover",
        ],
        "timesteps": ["current", "1h", "1d"],
        "units": units,
        "timezone": "auto",
        "apikey": TOMORROW_API_KEY,
    }
    response = requests.get(url, params=params, timeout=12)
    response.raise_for_status()
    return response.json()


def build_view_from_api(location_label, lat, lon, units):
    payload = fetch_weather_timelines(lat, lon, units)
    timelines = {tl["timestep"]: tl["intervals"] for tl in payload["data"]["timelines"]}

    current_interval = timelines.get("current", [])
    daily_intervals = timelines.get("1d", [])

    current_values = current_interval[0]["values"] if current_interval else {}
    current_time = parse_iso_time(current_interval[0]["startTime"]) if current_interval else datetime.now()

    condition_label, condition_icon = describe_weather(current_values.get("weatherCode"))

    daily = []
    for interval in daily_intervals[:7]:
        values = interval.get("values", {})
        day_time = parse_iso_time(interval.get("startTime"))
        day_label, day_icon = describe_weather(values.get("weatherCode"))
        daily.append(
            {
                "day_name": day_time.strftime("%a") if day_time else "--",
                "date": day_time.strftime("%b %d") if day_time else "--",
                "high": round(values.get("temperatureMax", values.get("temperature", 0))),
                "low": round(values.get("temperatureMin", values.get("temperature", 0))),
                "sunrise": format_time(parse_iso_time(values.get("sunriseTime"))),
                "sunset": format_time(parse_iso_time(values.get("sunsetTime"))),
                "condition": day_label,
                "icon": day_icon,
                "precip": round(values.get("precipitationProbability", 0)),
            }
        )

    sunrise_today = daily[0]["sunrise"] if daily else "--"
    sunset_today = daily[0]["sunset"] if daily else "--"

    wind_speed = round(current_values.get("windSpeed", 0))
    wind_dir = wind_degrees_to_compass(current_values.get("windDirection"))
    humidity = round(current_values.get("humidity", 0))
    precip = round(current_values.get("precipitationProbability", 0))

    return {
        "location_name": payload.get("location", {}).get("name", location_label),
        "current_time": format_time(current_time),
        "current_date": format_date(current_time),
        "sunrise_today": sunrise_today,
        "sunset_today": sunset_today,
        "current": {
            "temperature": round(current_values.get("temperature", 0)),
            "feels_like": round(current_values.get("temperatureApparent", current_values.get("temperature", 0))),
            "condition": condition_label,
            "icon": condition_icon,
            "stats": [
                {"label": "Precip", "value": f"{precip}%", "icon": "fa-cloud-rain"},
                {
                    "label": "Wind",
                    "value": f"{wind_speed} {UNIT_LABELS[units]['speed']} {wind_dir}".strip(),
                    "icon": "fa-wind",
                },
                {"label": "Humidity", "value": f"{humidity}%", "icon": "fa-droplet"},
            ],
        },
        "daily": daily,
        "data_source": "api",
        "status_message": None,
    }


def build_sample_view(location_label, lat, lon, units, status_message):
    now = datetime.now()
    base_high = 92 if units == "imperial" else 33
    base_low = 76 if units == "imperial" else 24
    conditions = [
        {"label": "Partly Cloudy", "icon": "fa-cloud-sun", "precip": 20},
        {"label": "Sunny", "icon": "fa-sun", "precip": 5},
        {"label": "Cloudy", "icon": "fa-cloud", "precip": 15},
        {"label": "Light Rain", "icon": "fa-cloud-rain", "precip": 45},
        {"label": "Clear", "icon": "fa-sun", "precip": 0},
        {"label": "Mostly Cloudy", "icon": "fa-cloud", "precip": 25},
        {"label": "Thunderstorm", "icon": "fa-cloud-bolt", "precip": 60},
    ]

    daily = []
    for index in range(7):
        day_time = now + timedelta(days=index)
        condition = conditions[index % len(conditions)]
        high = base_high - index
        low = base_low - index
        sunrise = day_time.replace(hour=6, minute=28, second=0, microsecond=0)
        sunset = day_time.replace(hour=19, minute=58, second=0, microsecond=0)
        daily.append(
            {
                "day_name": day_time.strftime("%a"),
                "date": day_time.strftime("%b %d"),
                "high": round(high),
                "low": round(low),
                "sunrise": format_time(sunrise),
                "sunset": format_time(sunset),
                "condition": condition["label"],
                "icon": condition["icon"],
                "precip": condition["precip"],
            }
        )

    wind_speed = 8 if units == "imperial" else 4
    wind_dir = "SW"
    humidity = 52
    precip = daily[0]["precip"] if daily else 20

    return {
        "location_name": location_label,
        "current_time": format_time(now),
        "current_date": format_date(now),
        "sunrise_today": daily[0]["sunrise"] if daily else "--",
        "sunset_today": daily[0]["sunset"] if daily else "--",
        "current": {
            "temperature": round((daily[0]["high"] + daily[0]["low"]) / 2) if daily else base_high,
            "feels_like": round(base_high - 2),
            "condition": daily[0]["condition"] if daily else "Partly Cloudy",
            "icon": daily[0]["icon"] if daily else "fa-cloud-sun",
            "stats": [
                {"label": "Precip", "value": f"{precip}%", "icon": "fa-cloud-rain"},
                {
                    "label": "Wind",
                    "value": f"{wind_speed} {UNIT_LABELS[units]['speed']} {wind_dir}",
                    "icon": "fa-wind",
                },
                {"label": "Humidity", "value": f"{humidity}%", "icon": "fa-droplet"},
            ],
        },
        "daily": daily,
        "data_source": "sample",
        "status_message": status_message,
    }


def get_weather_view(location_label, lat, lon, units):
    cache_key = (round(lat, 3), round(lon, 3), units)
    cached = _weather_cache.get(cache_key)
    if cached and time.time() - cached["timestamp"] < WEATHER_CACHE_SECONDS:
        return cached["data"]

    if USE_SAMPLE_DATA or not TOMORROW_API_KEY:
        status = "Using sample data. Set TOMORROW_API_KEY for live forecasts."
        view = build_sample_view(location_label, lat, lon, units, status)
        _weather_cache[cache_key] = {"timestamp": time.time(), "data": view}
        return view

    try:
        view = build_view_from_api(location_label, lat, lon, units)
        _weather_cache[cache_key] = {"timestamp": time.time(), "data": view}
        return view
    except (requests.RequestException, KeyError, ValueError):
        status = "Live data unavailable. Showing sample forecast until the API responds."
        view = build_sample_view(location_label, lat, lon, units, status)
        _weather_cache[cache_key] = {"timestamp": time.time(), "data": view}
        return view


@app.route("/")
def index():
    location_query = request.args.get("location", "").strip()
    units = normalize_units(request.args.get("units", DEFAULT_UNITS))

    location = resolve_location(location_query)
    weather_view = get_weather_view(location["name"], location["lat"], location["lon"], units)

    return render_template(
        "index.html",
        location_query=location_query or location["name"],
        units=units,
        units_label=UNIT_LABELS[units],
        map_url=build_map_url(location["lat"], location["lon"]),
        location=location,
        **weather_view,
    )


if __name__ == "__main__":
    app.run(debug=True)
