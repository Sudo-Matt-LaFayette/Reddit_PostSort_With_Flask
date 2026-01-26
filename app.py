import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me")

DEFAULT_LOCATION = os.environ.get("DEFAULT_LOCATION", "Dallas, Texas")
DEFAULT_LAT = os.environ.get("DEFAULT_LAT", "32.7767")
DEFAULT_LON = os.environ.get("DEFAULT_LON", "-96.7970")
DEFAULT_TIMEZONE = os.environ.get("DEFAULT_TIMEZONE", "America/Chicago")
DEFAULT_UNITS = os.environ.get("WEATHER_UNITS", "imperial").lower()
DEFAULT_ZOOM = os.environ.get("MAP_ZOOM", "8")

WEATHER_CODE_MAP = {
    1000: ("Clear", "fa-sun"),
    1001: ("Cloudy", "fa-cloud"),
    1100: ("Mostly Clear", "fa-cloud-sun"),
    1101: ("Partly Cloudy", "fa-cloud-sun"),
    1102: ("Mostly Cloudy", "fa-cloud"),
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
    8000: ("Thunderstorm", "fa-bolt"),
}


def parse_iso_datetime(value):
    if not value:
        return None
    try:
        if value.endswith("Z"):
            value = value.replace("Z", "+00:00")
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def get_timezone(tz_name):
    try:
        return ZoneInfo(tz_name)
    except Exception:
        return timezone.utc


def format_time(dt, tz):
    if not dt:
        return "--"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz).strftime("%I:%M %p").lstrip("0")


def format_day_label(dt, tz):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz).strftime("%a")


def format_date_label(dt, tz):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz).strftime("%b %d").replace(" 0", " ")


def weather_description(code):
    if code is None:
        return "Unknown", "fa-cloud"
    return WEATHER_CODE_MAP.get(code, ("Unknown", "fa-cloud"))


def parse_float(value, fallback):
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def resolve_location(query, mapbox_token):
    fallback_lat = parse_float(DEFAULT_LAT, 32.7767)
    fallback_lon = parse_float(DEFAULT_LON, -96.7970)
    location_name = query or DEFAULT_LOCATION

    if not mapbox_token:
        return {
            "name": location_name,
            "lat": fallback_lat,
            "lon": fallback_lon,
            "source": "default",
        }

    try:
        geocode_url = (
            "https://api.mapbox.com/geocoding/v5/mapbox.places/"
            f"{requests.utils.quote(location_name)}.json"
        )
        response = requests.get(
            geocode_url,
            params={"access_token": mapbox_token, "limit": 1},
            timeout=8,
        )
        response.raise_for_status()
        payload = response.json()
        features = payload.get("features", [])
        if features:
            feature = features[0]
            lon, lat = feature.get("center", [fallback_lon, fallback_lat])
            name = feature.get("place_name", location_name)
            return {"name": name, "lat": lat, "lon": lon, "source": "mapbox"}
    except requests.RequestException:
        pass

    return {
        "name": location_name,
        "lat": fallback_lat,
        "lon": fallback_lon,
        "source": "default",
    }


def build_map_image_url(lat, lon, mapbox_token):
    if not mapbox_token:
        return None
    zoom = parse_float(DEFAULT_ZOOM, 8.0)
    size = "1280x960"
    return (
        "https://api.mapbox.com/styles/v1/mapbox/dark-v11/static/"
        f"{lon},{lat},{zoom},0/{size}"
        f"?access_token={mapbox_token}"
    )


def fetch_weather_forecast(lat, lon, units, api_key):
    if not api_key:
        return None
    url = "https://api.tomorrow.io/v4/weather/forecast"
    params = {
        "location": f"{lat},{lon}",
        "units": units,
        "timesteps": "1h,1d",
        "fields": ",".join(
            [
                "temperature",
                "temperatureApparent",
                "temperatureMin",
                "temperatureMax",
                "humidity",
                "windSpeed",
                "precipitationProbability",
                "sunriseTime",
                "sunsetTime",
                "weatherCode",
            ]
        ),
        "apikey": api_key,
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def normalize_weather(api_data, location_name, tz_name, units):
    tz = get_timezone(tz_name)
    timelines = api_data.get("timelines", {})
    hourly = timelines.get("hourly", [])
    daily = timelines.get("daily", [])

    current_block = hourly[0] if hourly else {}
    current_values = current_block.get("values", {})
    current_time = parse_iso_datetime(current_block.get("time")) or datetime.now(tz)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)

    daily_cards = []
    for day in daily[:7]:
        day_time = parse_iso_datetime(day.get("time")) or datetime.now(tz)
        values = day.get("values", {})
        condition, icon = weather_description(values.get("weatherCode"))
        daily_cards.append(
            {
                "day": format_day_label(day_time, tz),
                "date": format_date_label(day_time, tz),
                "high": round(values.get("temperatureMax", 0)),
                "low": round(values.get("temperatureMin", 0)),
                "sunrise": format_time(
                    parse_iso_datetime(values.get("sunriseTime")), tz
                ),
                "sunset": format_time(
                    parse_iso_datetime(values.get("sunsetTime")), tz
                ),
                "condition": condition,
                "icon": icon,
            }
        )

    today = daily_cards[0] if daily_cards else {}
    condition, icon = weather_description(current_values.get("weatherCode"))
    return {
        "location": location_name,
        "time": current_time.astimezone(tz),
        "timezone": tz_name,
        "current": {
            "temperature": round(current_values.get("temperature", 0)),
            "feels_like": round(current_values.get("temperatureApparent", 0)),
            "humidity": round(current_values.get("humidity", 0)),
            "wind": round(current_values.get("windSpeed", 0)),
            "precip": round(current_values.get("precipitationProbability", 0)),
            "condition": condition,
            "icon": icon,
            "sunrise": today.get("sunrise", "--"),
            "sunset": today.get("sunset", "--"),
        },
        "daily": daily_cards,
        "units": units,
    }


def build_fallback_weather(location_name, tz_name, units):
    tz = get_timezone(tz_name)
    now = datetime.now(tz)
    base_temp = 86 if units == "imperial" else 30
    daily_cards = []
    conditions = [
        ("Clear", "fa-sun"),
        ("Partly Cloudy", "fa-cloud-sun"),
        ("Cloudy", "fa-cloud"),
        ("Light Rain", "fa-cloud-rain"),
        ("Thunderstorm", "fa-bolt"),
        ("Clear", "fa-sun"),
        ("Mostly Cloudy", "fa-cloud"),
    ]

    for i in range(7):
        day_time = now + timedelta(days=i)
        high = base_temp + (i % 3) * 2
        low = base_temp - 12 + (i % 2) * 2
        condition, icon = conditions[i % len(conditions)]
        sunrise = (day_time.replace(hour=6, minute=30, second=0) + timedelta(minutes=i))
        sunset = (day_time.replace(hour=19, minute=45, second=0) - timedelta(minutes=i))
        daily_cards.append(
            {
                "day": format_day_label(day_time, tz),
                "date": format_date_label(day_time, tz),
                "high": high,
                "low": low,
                "sunrise": format_time(sunrise, tz),
                "sunset": format_time(sunset, tz),
                "condition": condition,
                "icon": icon,
            }
        )

    current = daily_cards[0]
    return {
        "location": location_name,
        "time": now,
        "timezone": tz_name,
        "current": {
            "temperature": current["high"],
            "feels_like": current["high"] + 2,
            "humidity": 42,
            "wind": 8,
            "precip": 15,
            "condition": current["condition"],
            "icon": current["icon"],
            "sunrise": current["sunrise"],
            "sunset": current["sunset"],
        },
        "daily": daily_cards,
        "units": units,
    }


def unit_labels(units):
    if units == "metric":
        return {"temp": "C", "wind": "m/s"}
    return {"temp": "F", "wind": "mph"}


@app.route("/")
def index():
    location_query = request.args.get("location", "").strip() or DEFAULT_LOCATION
    units = request.args.get("units", DEFAULT_UNITS).lower()
    if units not in ("imperial", "metric"):
        units = DEFAULT_UNITS

    mapbox_token = os.environ.get("MAPBOX_API_KEY")
    weather_token = os.environ.get("TOMORROW_API_KEY")

    location = resolve_location(location_query, mapbox_token)
    map_image_url = build_map_image_url(
        location["lat"], location["lon"], mapbox_token
    )

    weather_data = None
    api_status = {
        "mapbox": bool(mapbox_token),
        "tomorrow": bool(weather_token),
        "fallback": False,
    }

    if weather_token:
        try:
            weather_data = fetch_weather_forecast(
                location["lat"], location["lon"], units, weather_token
            )
        except requests.RequestException:
            weather_data = None

    if weather_data:
        weather = normalize_weather(weather_data, location["name"], DEFAULT_TIMEZONE, units)
    else:
        api_status["fallback"] = True
        weather = build_fallback_weather(location["name"], DEFAULT_TIMEZONE, units)

    return render_template(
        "index.html",
        weather=weather,
        units=unit_labels(units),
        map_image_url=map_image_url,
        mapbox_token=mapbox_token,
        location_query=location_query,
        api_status=api_status,
    )


if __name__ == "__main__":
    app.run(debug=True)
