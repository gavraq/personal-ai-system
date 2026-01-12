#!/usr/bin/env python3
"""
Met Office DataHub Weather Fetcher.

Fetches hourly forecast data and outputs formatted weather for daily notes.
Part of the weather skill for Claude Code.

Usage:
    python3 fetch_weather.py                          # Default: Claygate, Surrey
    python3 fetch_weather.py --location "Paris"       # Geocode any location
    python3 fetch_weather.py --lat 51.5 --lon -0.1    # Custom coordinates

Environment:
    METOFFICE_API_KEY - JWT token from Met Office DataHub (optional, reads from .env if not set)
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
import urllib.error
import urllib.parse

# Configuration
ENV_FILE = Path("/Users/gavinslater/projects/life/.env")

# Default location (Claygate, Surrey - home)
DEFAULT_LAT = 51.36
DEFAULT_LON = -0.35
DEFAULT_NAME = "Claygate"

# Weather code mapping (Met Office significantWeatherCode)
WEATHER_CODES = {
    0: "Clear night",
    1: "Sunny day",
    2: "Partly cloudy (night)",
    3: "Partly cloudy (day)",
    5: "Mist",
    6: "Fog",
    7: "Cloudy",
    8: "Overcast",
    9: "Light rain shower (night)",
    10: "Light rain shower (day)",
    11: "Drizzle",
    12: "Light rain",
    13: "Heavy rain shower (night)",
    14: "Heavy rain shower (day)",
    15: "Heavy rain",
    16: "Sleet shower (night)",
    17: "Sleet shower (day)",
    18: "Sleet",
    19: "Hail shower (night)",
    20: "Hail shower (day)",
    21: "Hail",
    22: "Light snow shower (night)",
    23: "Light snow shower (day)",
    24: "Light snow",
    25: "Heavy snow shower (night)",
    26: "Heavy snow shower (day)",
    27: "Heavy snow",
    28: "Thunder shower (night)",
    29: "Thunder shower (day)",
    30: "Thunder",
}


def degrees_to_compass(degrees: float) -> str:
    """Convert wind direction in degrees to compass direction."""
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = round(degrees / 45) % 8
    return directions[index]


def get_api_key() -> str | None:
    """Get API key from environment or .env file."""
    # First check environment variable
    api_key = os.environ.get("METOFFICE_API_KEY")
    if api_key:
        return api_key

    # Read from .env file
    if ENV_FILE.exists():
        with open(ENV_FILE) as f:
            for line in f:
                if line.startswith("METOFFICE_API_KEY="):
                    return line.split("=", 1)[1].strip()

    return None


def geocode_location(location: str) -> tuple[float, float, str] | None:
    """
    Geocode a location name to coordinates using OpenStreetMap Nominatim.
    Returns (lat, lon, display_name) or None if not found.
    """
    encoded = urllib.parse.quote(location)
    url = f"https://nominatim.openstreetmap.org/search?q={encoded}&format=json&limit=1"

    request = urllib.request.Request(url)
    # Nominatim requires a User-Agent
    request.add_header("User-Agent", "GavinWeatherSkill/1.0 (gavin@slaters.uk.com)")

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data and len(data) > 0:
                result = data[0]
                lat = float(result["lat"])
                lon = float(result["lon"])
                # Use a cleaner display name (first part before comma)
                display = result.get("display_name", location)
                # Take first meaningful part of the name
                parts = display.split(",")
                name = parts[0].strip()
                if len(parts) > 1:
                    # Add country/region for context if available
                    name = f"{parts[0].strip()}, {parts[-1].strip()}"
                return (lat, lon, name)
    except urllib.error.HTTPError as e:
        print(f"Geocoding HTTP Error: {e.code} - {e.reason}", file=sys.stderr)
    except urllib.error.URLError as e:
        print(f"Geocoding URL Error: {e.reason}", file=sys.stderr)
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Geocoding Parse Error: {e}", file=sys.stderr)

    return None


def fetch_weather(lat: float, lon: float) -> dict | None:
    """Fetch weather data from Met Office DataHub API."""
    api_key = get_api_key()
    if not api_key:
        print("Error: METOFFICE_API_KEY not found", file=sys.stderr)
        return None

    api_url = f"https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point/hourly?latitude={lat}&longitude={lon}"
    request = urllib.request.Request(api_url)
    request.add_header("apikey", api_key)

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}", file=sys.stderr)
        return None
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"JSON Error: {e}", file=sys.stderr)
        return None


def parse_current_weather(data: dict) -> dict | None:
    """Extract current hour's weather from the API response."""
    try:
        # Get timeseries data
        features = data.get("features", [])
        if not features:
            return None

        timeseries = features[0].get("properties", {}).get("timeSeries", [])
        if not timeseries:
            return None

        # Find current hour (first entry is usually current/next hour)
        now = datetime.now(timezone.utc)
        current = timeseries[0]

        # Try to find the closest hour
        for entry in timeseries:
            entry_time = datetime.fromisoformat(entry["time"].replace("Z", "+00:00"))
            if entry_time <= now:
                current = entry
            else:
                break

        # Extract weather data
        weather_code = current.get("significantWeatherCode", 7)
        temp = current.get("screenTemperature", 0)
        feels_like = current.get("feelsLikeTemperature", temp)
        wind_speed_ms = current.get("windSpeed10m", 0)
        wind_dir = current.get("windDirectionFrom10m", 0)
        humidity = current.get("screenRelativeHumidity", 0)
        precip_prob = current.get("probOfPrecipitation", 0)

        return {
            "conditions": WEATHER_CODES.get(weather_code, "Unknown"),
            "temperature": round(temp, 1),
            "feels_like": round(feels_like, 1),
            "wind_speed_kmh": round(wind_speed_ms * 3.6),
            "wind_direction": degrees_to_compass(wind_dir),
            "humidity": round(humidity),
            "precipitation_probability": round(precip_prob),
        }
    except (KeyError, IndexError, TypeError) as e:
        print(f"Parse Error: {e}", file=sys.stderr)
        return None


def generate_impact(weather: dict) -> str:
    """Generate contextual impact statement."""
    conditions = weather["conditions"].lower()
    precip = weather["precipitation_probability"]
    temp = weather["temperature"]

    # Check for wet conditions
    if "rain" in conditions or "drizzle" in conditions or "shower" in conditions:
        if "heavy" in conditions:
            return "Heavy rain expected - plan indoor activities."
        return "Wet conditions - bring umbrella if going out."

    if precip >= 70:
        return "High chance of rain - plan indoor activities."
    if precip >= 40:
        return "Chance of showers - check conditions before outdoor activities."

    # Check for snow/ice
    if "snow" in conditions or "sleet" in conditions or "hail" in conditions:
        return "Wintry conditions - take care outdoors."

    # Check for fog/mist
    if "fog" in conditions or "mist" in conditions:
        return "Reduced visibility - drive carefully if going out."

    # Temperature-based advice
    if temp < 5:
        return "Cold conditions - wrap up warm."
    if temp > 25:
        return "Warm day - stay hydrated."

    # Good weather
    if "sunny" in conditions or "clear" in conditions:
        return "Good conditions for outdoor activities."

    return "Typical conditions - no significant weather impact expected."


def format_output(weather: dict, location_name: str) -> str:
    """Format weather data for daily notes."""
    impact = generate_impact(weather)

    header = f"**Location**: {location_name}\n" if location_name != DEFAULT_NAME else ""

    return f"""{header}**Conditions**: {weather['conditions']}
**Temperature**: {weather['temperature']}°C (feels like {weather['feels_like']}°C)
**Wind**: {weather['wind_direction']} {weather['wind_speed_kmh']} km/h
**Humidity**: {weather['humidity']}%
**Precipitation**: {weather['precipitation_probability']}%

**Impact**: {impact}"""


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch weather from Met Office DataHub API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 fetch_weather.py                        # Claygate (default)
    python3 fetch_weather.py --location "Paris"    # Any location (geocoded)
    python3 fetch_weather.py --location "Tokyo"    # Works worldwide
    python3 fetch_weather.py --lat 51.5 --lon -0.1  # Custom coordinates
        """,
    )
    parser.add_argument(
        "--location", "-l",
        type=str,
        help="Location name to geocode (e.g., 'Paris', 'Tokyo', 'Sydney')",
    )
    parser.add_argument(
        "--lat",
        type=float,
        help="Latitude for custom location",
    )
    parser.add_argument(
        "--lon",
        type=float,
        help="Longitude for custom location",
    )
    parser.add_argument(
        "--name", "-n",
        type=str,
        help="Custom name for the location (used with --lat/--lon)",
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # Determine location
    lat = DEFAULT_LAT
    lon = DEFAULT_LON
    location_name = DEFAULT_NAME

    if args.location:
        # Geocode the location
        result = geocode_location(args.location)
        if result:
            lat, lon, location_name = result
        else:
            print(f"Could not find location: {args.location}", file=sys.stderr)
            return 1
    elif args.lat is not None and args.lon is not None:
        lat = args.lat
        lon = args.lon
        location_name = args.name if args.name else f"({lat}, {lon})"

    data = fetch_weather(lat, lon)
    if not data:
        print("Weather data unavailable")
        return 1

    weather = parse_current_weather(data)
    if not weather:
        print("Weather data unavailable - parse error")
        return 1

    print(format_output(weather, location_name))
    return 0


if __name__ == "__main__":
    sys.exit(main())
