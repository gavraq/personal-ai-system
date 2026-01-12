# Location Analysis System - User Guide

**Version:** 2.0
**Last Updated:** November 2, 2025

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Analyzing a Single Day](#analyzing-a-single-day)
3. [Analyzing Multi-Day Trips](#analyzing-multi-day-trips)
4. [Understanding Activity Types](#understanding-activity-types)
5. [Common Use Cases](#common-use-cases)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### What This System Does

The Location Analysis System automatically detects and analyzes your activities from GPS location data:

- **🏌️ Golf** - Rounds at golf courses with hole counts
- **🏃 Parkrun** - Saturday morning 5km runs
- **🚆 Commute** - Daily Esher ↔ London travel
- **🐕 Dog Walking** - Local walks around Esher
- **🏂 Snowboarding** - Ski resort sessions with lift rides and descents
- **✈️ Flights** - Air travel detection
- **📍 Location Visits** - Supermarkets, beaches, airports, etc.

### Prerequisites

1. **Owntracks Data:** Location tracking must be active on your device
2. **Python 3:** System requires Python 3.7+
3. **Configuration:** Known locations configured in `locations/base_locations.json`

---

## Analyzing a Single Day

### Basic Usage

```bash
cd /Users/gavinslater/projects/life/integrations/location
python3 scripts/analyze_date.py 2025-11-02
```

### Example Output

```
======================================================================
Location Analysis: Saturday, 2025-11-02
======================================================================

📍 Location Data: 1,234 points

🏌️  Analyzing golf activities...
   ✓ Found 1 golf session(s)

🏃 Analyzing parkrun activities...
   ✓ Found 1 parkrun(s)

🚆 Analyzing commute patterns...
   - No commute activities detected

🐕 Analyzing dog walking activities...
   - No dog walking activities detected

🏂 Analyzing snowboarding activities...
   - No snowboarding activities detected

======================================================================
Summary: 2 activities detected
======================================================================

1. PARKRUN
   Location: Bushy Park
   Time: 09:00 - 09:23 (23m)
   Confidence: HIGH (0.87)
   Distance: 5000m

2. GOLF
   Location: Pine Ridge Golf Course
   Time: 14:30 - 17:45 (3.3h)
   Confidence: HIGH (0.91)
   Holes: 18

======================================================================
✓ Analysis complete
======================================================================
```

### Options

```bash
# Enable verbose logging
python3 scripts/analyze_date.py 2025-11-02 --verbose

# Custom user/device
python3 scripts/analyze_date.py 2025-11-02 --user gavin --device iPhone

# Show help
python3 scripts/analyze_date.py --help
```

---

## Analyzing Multi-Day Trips

### Setup

1. **Create Trip Location File**

Create a JSON file in `locations/trips/` directory:

```bash
# Example: locations/trips/portugal_2025-10.json
{
  "name": "Portugal October 2025",
  "start_date": "2025-10-18",
  "end_date": "2025-10-24",
  "locations": {
    "pine-cliffs-resort": {
      "name": "Pine Cliffs Resort",
      "type": "resort",
      "coordinates": [37.0893, -8.0365],
      "radius": 300
    },
    "pine-cliffs-golf": {
      "name": "Pine Cliffs Golf Course",
      "type": "golf_course",
      "coordinates": [37.0895, -8.0380],
      "radius": 500
    }
  }
}
```

2. **Run Trip Analysis**

```python
from analyzers.trip_analyzer import TripAnalyzer

# Initialize with trip name
analyzer = TripAnalyzer(trip_name='portugal_2025-10')

# Analyze single day
daily_summary = analyzer.analyze_day('2025-10-19')

# Or analyze entire trip
trip_summary = analyzer.analyze_trip(
    start_date='2025-10-18',
    end_date='2025-10-24'
)
```

### Trip Analysis Output

The trip analyzer provides:
- Day-by-day activity breakdown
- Chronological timeline
- All activity types automatically detected
- Location visit tracking

---

## Understanding Activity Types

### Golf 🏌️

**Detected When:**
- Walking pace (1.0-2.5 m/s)
- Stationary periods at tee boxes/greens
- Duration 1-6 hours
- At known golf course location (optional)

**Output Details:**
- Number of holes played
- Duration per hole (if detectable)
- Course name
- Confidence score

**Configuration:**
```json
{
  "golf": {
    "walking_velocity_range_mps": [1.0, 2.5],
    "min_session_duration_hours": 1.0,
    "max_session_duration_hours": 6.0,
    "stationary_tolerance_pct": 15
  }
}
```

### Parkrun 🏃

**Detected When:**
- Saturday morning (08:00-11:00)
- Running velocity (2.0-5.0 m/s)
- Duration 16-45 minutes
- Distance approximately 5km
- At known parkrun location (optional)

**Output Details:**
- Distance covered
- Average pace
- Location name
- Confidence score

### Commute 🚆

**Detected When:**
- Weekday morning (06:00-10:00) or evening (16:00-20:00)
- Train velocity detected (10-40 m/s)
- Route: Esher → London or reverse
- Visits expected locations (home, station, office)

**Output Details:**
- Direction (to_office / from_office)
- Duration
- Route confidence
- Train segments detected

### Dog Walking 🐕

**Detected When:**
- Walking velocity (0.8-2.0 m/s)
- Within 2km of home
- Duration 10-90 minutes
- At known walking locations (optional)
- Includes stationary stops

**Output Details:**
- Distance walked
- Duration
- Location name
- Number of stops

### Snowboarding 🏂

**Detected When:**
- At known ski resort location
- Lift rides detected (uphill 1.5-6.0 m/s)
- Descents detected (downhill 5.0-20.0 m/s)
- Altitude changes significant (100m+)
- Minimum 2 runs

**Output Details:**
- Number of runs (lift + descent pairs)
- Total vertical meters
- Average descent velocity
- Session duration
- Resort name

---

## Common Use Cases

### Use Case 1: Saturday Parkrun Check

```bash
# Check if you did parkrun today
python3 scripts/analyze_date.py $(date +%Y-%m-%d)

# Check last Saturday
python3 scripts/analyze_date.py 2025-10-26
```

### Use Case 2: Golf Trip Analysis

```bash
# Create trip locations file
cat > locations/trips/algarve_2025-10.json << EOF
{
  "name": "Algarve Golf Trip",
  "start_date": "2025-10-18",
  "end_date": "2025-10-24",
  "locations": {
    "vale-do-lobo": {
      "name": "Vale do Lobo Golf Course",
      "type": "golf_course",
      "coordinates": [37.0634, -8.0721],
      "radius": 500
    }
  }
}
EOF

# Analyze trip
python3 << EOF
from analyzers.trip_analyzer import TripAnalyzer

analyzer = TripAnalyzer(trip_name='algarve_2025-10')
summary = analyzer.analyze_trip(
    start_date='2025-10-18',
    end_date='2025-10-24'
)

for day in summary:
    print(f"\n{day.day_name}, {day.date}")
    print(f"Activities: {day.total_activities}")
    for activity in day.activities:
        print(f"  - {activity.activity_type}: {activity.location_name}")
EOF
```

### Use Case 3: Weekly Activity Summary

```bash
# Analyze last 7 days
for i in {0..6}; do
    date=$(date -v-${i}d +%Y-%m-%d)
    echo "Analyzing $date..."
    python3 scripts/analyze_date.py $date
done
```

### Use Case 4: Commute Pattern Analysis

```bash
# Analyze weekdays for commute patterns
python3 scripts/analyze_date.py 2025-11-01  # Friday
# Check "COMMUTE" activities in output
```

---

## Troubleshooting

### No Location Data Available

**Problem:** Script reports "No location data available for this date"

**Solutions:**
1. Check Owntracks is recording data
2. Verify date format (YYYY-MM-DD)
3. Confirm Owntracks API is accessible
4. Check authentication credentials

### Activities Not Detected

**Problem:** Expected activities not showing in results

**Solutions:**

1. **Check Confidence Thresholds**
   - View configuration in `config/analysis_config.json`
   - Lower confidence thresholds if needed
   - Use `--verbose` flag to see detection details

2. **Verify Location Data Quality**
   - Check number of location points
   - Ensure GPS accuracy was good
   - Verify altitude data exists (for snowboarding)

3. **Check Known Locations**
   - Golf courses must be in location database
   - Parkrun venues must be configured
   - Ski resorts must be listed

### Incorrect Activity Classification

**Problem:** Activities detected but wrong type

**Solutions:**
1. Check velocity thresholds in configuration
2. Verify time windows (parkrun = Saturday morning)
3. Review location matching radius
4. Adjust confidence weights

### Script Errors

**Problem:** Python errors or import failures

**Solutions:**
1. Ensure you're in the correct directory
2. Check Python path: `sys.path` includes location directory
3. Verify all dependencies installed
4. Check file permissions

---

## Configuration Files

### Main Configuration

**File:** `config/analysis_config.json`

Contains all analyzer settings:
- Velocity thresholds
- Duration ranges
- Confidence weights
- Time windows
- Gap tolerances

### Known Locations

**Files:**
- `locations/base_locations.json` - UK locations (home, parkruns, etc.)
- `locations/trips/*.json` - Trip-specific locations

**Format:**
```json
{
  "location-id": {
    "name": "Display Name",
    "type": "golf_course|parkrun|resort|etc",
    "coordinates": [latitude, longitude],
    "radius": 500
  }
}
```

---

## Tips & Best Practices

### 1. Location Database Maintenance

- Add new golf courses after visiting
- Update parkrun locations when traveling
- Include ski resorts before winter trips
- Set appropriate radius values:
  - Home: 100m
  - Parkrun: 200m
  - Golf Course: 500m
  - Ski Resort: 2000m

### 2. Improving Detection Accuracy

- Ensure GPS is enabled during activities
- Keep location recording frequency high
- For snowboarding, ensure altitude is recorded
- Charge device before long activities

### 3. Analyzing Historical Data

- Works with any past date that has Owntracks data
- Great for filling in journal entries retrospectively
- Can validate memories of past trips

### 4. Privacy Considerations

- Location data is stored locally only
- No data sent to external services (except Owntracks API)
- Trip location files can be git-ignored if sensitive

---

## Getting Help

### Documentation

- **This Guide:** General usage and troubleshooting
- **developer-guide.md:** Extending the system
- **README.md:** System overview
- **analysis-improvements.md:** Complete technical specification

### Common Questions

**Q: Can I analyze locations outside the UK?**
A: Yes! Create a trip location file for anywhere.

**Q: Does it work without known locations?**
A: Yes, but confidence scores will be lower. Many activities (parkrun, commute) can still be detected.

**Q: How accurate is the detection?**
A: >90% accuracy for golf, parkrun when location data is good. Confidence scores indicate reliability.

**Q: Can I add new activity types?**
A: Yes! See developer-guide.md for extending the system.

---

## Quick Reference

### Essential Commands

```bash
# Analyze today
python3 scripts/analyze_date.py $(date +%Y-%m-%d)

# Analyze specific date
python3 scripts/analyze_date.py 2025-11-02

# Verbose output
python3 scripts/analyze_date.py 2025-11-02 --verbose

# Check configuration
cat config/analysis_config.json

# List known locations
cat locations/base_locations.json

# List trip locations
ls -l locations/trips/
```

### Key File Locations

```
integrations/location/
├── scripts/analyze_date.py          # Daily analysis tool
├── analyzers/trip_analyzer.py       # Multi-day analysis
├── config/analysis_config.json      # All settings
└── locations/
    ├── base_locations.json          # UK locations
    └── trips/                       # Trip-specific
```

---

**Need more help?** Check the developer-guide.md for technical details or analysis-improvements.md for the complete system specification.
