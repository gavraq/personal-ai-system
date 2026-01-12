# Location Analysis System - Quick Reference

**Version:** 2.0 | **Last Updated:** November 2, 2025

---

## Essential Commands

### Daily Analysis

```bash
# Analyze today
python3 scripts/analyze_date.py $(date +%Y-%m-%d)

# Analyze specific date
python3 scripts/analyze_date.py 2025-11-02

# Verbose output (debugging)
python3 scripts/analyze_date.py 2025-11-02 --verbose

# Custom user/device
python3 scripts/analyze_date.py 2025-11-02 --user gavin --device iPhone
```

### Trip Analysis

```python
from analyzers.trip_analyzer import TripAnalyzer

# Analyze single day
analyzer = TripAnalyzer(trip_name='portugal_2025-10')
summary = analyzer.analyze_day('2025-10-19')

# Analyze entire trip
trip_summary = analyzer.analyze_trip(
    start_date='2025-10-18',
    end_date='2025-10-24'
)
```

---

## Activity Types

| Type | Emoji | Detection Criteria |
|------|-------|-------------------|
| Golf | 🏌️ | Walking pace (1.0-2.5 m/s), stationary periods, 1-6 hours |
| Parkrun | 🏃 | Saturday 08:00-11:00, running pace (2.0-5.0 m/s), ~5km |
| Commute | 🚆 | Weekday morning/evening, train velocity (10-40 m/s) |
| Dog Walking | 🐕 | Walking pace (0.8-2.0 m/s), near home, 10-90 mins |
| Snowboarding | 🏂 | Ski resort, lift rides (uphill), descents (downhill), 100m+ altitude |
| Flight | ✈️ | High altitude (36,000+ ft), high speed (800+ km/h) |

---

## File Locations

```
integrations/location/
├── scripts/
│   └── analyze_date.py              # Daily analysis tool
│
├── analyzers/
│   ├── base_activity_analyzer.py    # Base class
│   ├── golf_analyzer.py             # Golf detection
│   ├── parkrun_analyzer.py          # Parkrun detection
│   ├── commute_analyzer.py          # Commute detection
│   ├── dog_walking_analyzer.py      # Dog walking detection
│   ├── snowboarding_analyzer.py     # Snowboarding detection
│   └── trip_analyzer.py             # Multi-day trips
│
├── config/
│   └── analysis_config.json         # All settings
│
└── locations/
    ├── base_locations.json          # UK locations
    └── trips/                       # Trip-specific
        └── trip_name.json
```

---

## Configuration

### View Current Config

```bash
cat config/analysis_config.json
```

### Common Settings

```json
{
  "activity_analyzers": {
    "golf": {
      "enabled": true,
      "walking_velocity_range_mps": [1.0, 2.5],
      "min_session_duration_hours": 1.0
    },
    "parkrun": {
      "enabled": true,
      "expected_day": "Saturday",
      "velocity_range_mps": [2.0, 5.0]
    }
  }
}
```

---

## Location Files

### Base Locations

**File:** `locations/base_locations.json`

```json
{
  "home-esher": {
    "name": "Home",
    "type": "home",
    "coordinates": [51.3695, -0.3670],
    "radius": 100
  },
  "bushy-park-parkrun": {
    "name": "Bushy Park Parkrun",
    "type": "parkrun",
    "coordinates": [51.4104, -0.3343],
    "radius": 200
  }
}
```

### Trip Locations

**File:** `locations/trips/portugal_2025-10.json`

```json
{
  "name": "Portugal October 2025",
  "start_date": "2025-10-18",
  "end_date": "2025-10-24",
  "locations": {
    "pine-cliffs-golf": {
      "name": "Pine Cliffs Golf Course",
      "type": "golf_course",
      "coordinates": [37.0895, -8.0380],
      "radius": 500
    }
  }
}
```

---

## Confidence Scores

| Label | Score Range | Meaning |
|-------|-------------|---------|
| CONFIRMED | 1.0 | Manually verified or exact match |
| HIGH | 0.8 - 1.0 | Strong evidence across multiple factors |
| MEDIUM | 0.6 - 0.8 | Good match but some uncertainty |
| LOW | < 0.6 | Possible match, needs review |

### Factors

Most analyzers use 5 weighted factors:
1. Known location match (30-40%)
2. Timing/schedule match (15-25%)
3. Velocity patterns (15-25%)
4. Duration reasonable (10-15%)
5. Activity-specific criteria (5-10%)

---

## Velocity Classification

| Activity | Min (m/s) | Max (m/s) | km/h | mph |
|----------|-----------|-----------|------|-----|
| Stationary | 0.0 | 0.5 | 0-1.8 | 0-1.1 |
| Walking | 0.5 | 2.5 | 1.8-9.0 | 1.1-5.6 |
| Running | 2.5 | 5.0 | 9.0-18.0 | 5.6-11.2 |
| Cycling | 3.0 | 8.0 | 10.8-28.8 | 6.7-17.9 |
| Train | 10.0 | 40.0 | 36.0-144.0 | 22.4-89.5 |
| Driving | 5.0 | 35.0 | 18.0-126.0 | 11.2-78.3 |
| Flying | 100.0 | 300.0 | 360-1080 | 224-671 |

---

## Location Types & Radii

| Type | Default Radius | Use Case |
|------|----------------|----------|
| home | 100m | Home location |
| work | 150m | Office location |
| station | 100m | Train stations |
| parkrun | 200m | Parkrun venues |
| park | 400m | Parks/commons |
| golf_course | 500m | Golf courses |
| airport | 1000m | Airports |
| ski_resort | 2000m | Ski resorts |
| supermarket | 100m | Shops |
| beach | 200m | Beaches |
| resort | 300m | Hotels/resorts |

---

## Common Tasks

### Add New Golf Course

1. Get coordinates (Google Maps)
2. Add to appropriate location file:

```json
{
  "your-golf-course": {
    "name": "Your Golf Course Name",
    "type": "golf_course",
    "coordinates": [51.4567, -0.1234],
    "radius": 500
  }
}
```

### Create Trip Location File

```bash
# Create file
cat > locations/trips/your_trip_name.json << EOF
{
  "name": "Trip Display Name",
  "start_date": "2025-MM-DD",
  "end_date": "2025-MM-DD",
  "locations": {}
}
EOF
```

### Check Last Week's Activities

```bash
# Loop through last 7 days
for i in {0..6}; do
    date=$(date -v-${i}d +%Y-%m-%d)
    echo "=== $date ==="
    python3 scripts/analyze_date.py $date | grep "✓ Found"
done
```

### Find Parkrun Days

```bash
# Check Saturdays for parkrun
python3 scripts/analyze_date.py 2025-10-26 | grep -A 5 "parkrun"
```

---

## Troubleshooting

### No Location Data

```bash
# Check Owntracks API
curl -u username:password https://owntracks.gavinslater.co.uk/api/0/locations

# Check date format
python3 scripts/analyze_date.py 2025-11-02  # Correct: YYYY-MM-DD
```

### Activity Not Detected

```bash
# Use verbose mode to see detection details
python3 scripts/analyze_date.py 2025-11-02 --verbose

# Check configuration
cat config/analysis_config.json | grep -A 10 "golf"

# View raw location count
python3 scripts/analyze_date.py 2025-11-02 | grep "Location Data"
```

### Low Confidence Scores

1. Add known location to database
2. Check velocity thresholds match activity
3. Verify time windows are correct
4. Review confidence weight configuration

---

## Python API

### Import Analyzers

```python
from analyzers.golf_analyzer import GolfAnalyzer
from analyzers.parkrun_analyzer import ParkrunAnalyzer
from analyzers.commute_analyzer import CommuteAnalyzer
from analyzers.dog_walking_analyzer import DogWalkingAnalyzer
from analyzers.snowboarding_analyzer import SnowboardingAnalyzer
```

### Basic Usage

```python
# Initialize
analyzer = GolfAnalyzer()

# Detect sessions
sessions = analyzer.detect_sessions(
    locations,
    golf_course_location={'name': 'Course', 'coordinates': (51.4, -0.3)}
)

# Process results
for session in sessions:
    print(f"{session.activity_type}: {session.location_name}")
    print(f"  Duration: {session.duration_hours:.1f}h")
    print(f"  Confidence: {session.confidence} ({session.confidence_score:.2f})")
```

### Get Location Data

```python
from core.owntracks_client import OwntracksClient

client = OwntracksClient()
response = client.get_locations(
    user='gavin',
    device='iPhone',
    from_date='2025-11-01',
    to_date='2025-11-01'
)

locations = response.get('data', [])
```

---

## Environment Variables

```bash
# Owntracks API authentication
export OWNTRACKS_AUTH_USERNAME="your_username"
export OWNTRACKS_AUTH_PASSWORD="your_password"

# Default user/device
export OWNTRACKS_USER="gavin"
export OWNTRACKS_DEVICE="iPhone"
```

---

## Documentation

| File | Purpose |
|------|---------|
| **user-guide.md** | Comprehensive usage guide |
| **developer-guide.md** | Extending the system |
| **quick-reference.md** | This file - quick lookup |
| **README.md** | System overview |
| **analysis-improvements.md** | Complete technical spec (archive) |

---

## Getting Help

```bash
# Script help
python3 scripts/analyze_date.py --help

# Check system status
ls -l analyzers/*.py

# View configuration
cat config/analysis_config.json

# Check documentation
ls -l docs/
```

---

## Key Directories

```bash
# View analyzers
ls -l analyzers/

# View configuration
cat config/analysis_config.json

# View base locations
cat locations/base_locations.json

# View trip locations
ls -l locations/trips/

# View scripts
ls -l scripts/

# View documentation
ls -l docs/
```

---

**Need more details?** See user-guide.md for comprehensive usage or developer-guide.md for extending the system.
