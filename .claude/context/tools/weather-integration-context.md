# Weather Integration Context

## Overview
Weather data for daily journal notes via Met Office DataHub API.

## Integration Details
- **Service**: Met Office Weather DataHub
- **API**: Site Specific (hourly forecast)
- **Account**: gavin@slaters.uk.com
- **Free Tier**: 360 calls/day
- **Location**: Claygate, Surrey (51.36, -0.35)

## Usage
Invoke via weather skill when creating daily notes:
```
Skill: weather
```

Returns formatted weather for daily note Weather section.

## Configuration
- API key stored in `.env` as `METOFFICE_API_KEY`
- Skill definition: `.claude/skills/weather/SKILL.md`

## Data Available
- Temperature (°C)
- Weather conditions (clear, cloudy, rain, etc.)
- Wind speed and direction
- Humidity
- Precipitation probability

## Error Handling
Weather is non-critical. If unavailable, note "Weather data unavailable" and continue.
