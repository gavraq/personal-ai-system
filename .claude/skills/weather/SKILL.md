---
name: weather
description: Get current weather and forecast for Claygate, Surrey using Met Office DataHub API. Use when daily notes or briefings need weather data.
---

# Weather Skill

## Purpose
Fetch reliable weather data from Met Office DataHub API. Defaults to Claygate, Surrey but supports any location worldwide via geocoding.

## When to Use
- Creating daily notes (morning/evening)
- Any request needing current weather conditions
- Planning outdoor activities (dog walks, runs)
- Checking weather for travel destinations

## Prerequisites
- Met Office DataHub API key stored in `/Users/gavinslater/projects/life/.env`
- Python 3.x (standard library only, no external dependencies)

## Usage

### Default (Claygate - Home)
```bash
python3 /Users/gavinslater/projects/life/.claude/skills/weather/scripts/fetch_weather.py
```

### Any Location (Geocoded)
```bash
python3 /Users/gavinslater/projects/life/.claude/skills/weather/scripts/fetch_weather.py --location "Paris"
python3 /Users/gavinslater/projects/life/.claude/skills/weather/scripts/fetch_weather.py --location "Tokyo"
python3 /Users/gavinslater/projects/life/.claude/skills/weather/scripts/fetch_weather.py --location "Sydney, Australia"
python3 /Users/gavinslater/projects/life/.claude/skills/weather/scripts/fetch_weather.py --location "JFK Airport"
```

### Custom Coordinates
```bash
python3 /Users/gavinslater/projects/life/.claude/skills/weather/scripts/fetch_weather.py --lat 48.8566 --lon 2.3522 --name "Paris"
```

## How It Works
1. **Location Resolution**: Uses OpenStreetMap Nominatim API to geocode any location name to coordinates
2. **Weather Fetch**: Calls Met Office DataHub API with the coordinates
3. **Parse & Format**: Extracts current hour's weather and formats for daily notes

## Output Format

For default location (Claygate):
```markdown
**Conditions**: Light rain
**Temperature**: 10.8°C (feels like 9.6°C)
**Wind**: SE 10 km/h
**Humidity**: 98%
**Precipitation**: 64%

**Impact**: Wet conditions - bring umbrella if going out.
```

For other locations (includes location header):
```markdown
**Location**: Paris, France
**Conditions**: Heavy rain
**Temperature**: 12.7°C (feels like 10.8°C)
**Wind**: SW 16 km/h
**Humidity**: 92%
**Precipitation**: 98%

**Impact**: Heavy rain expected - plan indoor activities.
```

## Error Handling
- If geocoding fails: Outputs error and exits
- If weather API fails: Outputs "Weather data unavailable"
- If API key missing: Outputs error to stderr
- Weather is not critical - continue daily journal process without it

## Weather Code Reference
Met Office significantWeatherCode values (handled by script):
- 0-1: Clear/Sunny
- 2-3: Partly cloudy
- 5-6: Mist/Fog
- 7-8: Cloudy/Overcast
- 9-15: Rain (light to heavy)
- 16-18: Sleet
- 19-21: Hail
- 22-27: Snow (light to heavy)
- 28-30: Thunder

## Account
- Registered: gavin@slaters.uk.com
- Portal: https://datahub.metoffice.gov.uk/
- Plan: Site Specific (free tier - 360 calls/day)

## Files
- `SKILL.md` - This skill definition
- `scripts/fetch_weather.py` - Main weather fetching script (with geocoding)
