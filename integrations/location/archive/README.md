# Location Analysis Ad-Hoc Scripts Archive

**Archive Date**: November 1, 2025
**Purpose**: Preserve ad-hoc scripts created during Portugal trip analysis for reference and regression testing

---

## Why These Scripts Are Archived

During the **Portugal family trip (October 18-24, 2025)**, the existing `location_analyzer.py` proved insufficient for analyzing trip-specific activities. This resulted in creating **5 specialized ad-hoc scripts** to handle:

1. **Golf activity detection** - Walking pace patterns + stationary periods at tee boxes
2. **Time-period filtering** - Morning vs afternoon golf sessions
3. **Venue-specific recognition** - Pine Cliffs Resort, Pingo Doce supermarket, Armação de Pêra beach
4. **Iterative corrections** - Timing adjustments based on actual trip schedule

These scripts contain **valuable domain knowledge** about:
- Golf velocity patterns (0.5-2.5 m/s walking, <0.5 m/s stationary)
- Stationary period detection (5-30 second pauses)
- Session clustering (15-minute gap tolerance)
- Likelihood scoring algorithms
- Portugal-specific location coordinates

---

## Archive Contents

### `analyze_golf_activity.py` (9.9KB)
**Purpose**: Detect and analyze golf activity patterns using velocity and location data

**Key Features**:
- Golf velocity detection: 0.5-2.5 m/s or stationary (<0.5 m/s)
- Stationary period identification (tee boxes/greens)
- Session clustering (minimum 10 minutes, max 3 hours)
- Distance calculation for session validation
- Golf likelihood assessment (HIGH/MEDIUM/LOW)
- Velocity distribution analysis

**Domain Knowledge**:
```python
# Golf play velocity range: 0.5-2 m/s (walking between shots)
# with stationary periods at tee boxes/greens
is_golf_velocity = 0.5 <= vel <= 2.5 or vel < 0.5

# Golf likelihood assessment
if 1200 < duration < 10800:  # 20 min - 3 hours
    if 0.8 <= avg_vel <= 2.0:  # Golf walking pace
        if 500 < total_distance < 3000:  # 9 holes distance
            likelihood = "HIGH - likely golf activity"
```

**Usage Example**:
```bash
python3 analyze_golf_activity.py 2025-10-19 37.0892 -8.3480 500
# Args: date, golf_course_lat, golf_course_lon, radius_meters
```

**Value for Future**:
- Reference implementation for `GolfAnalyzer` class
- Validated velocity thresholds
- Proven session clustering logic

---

### `analyze_morning_golf.py` (6.5KB)
**Purpose**: Focused analysis of morning period (7am-11am) for golf activity detection

**Key Features**:
- Time period filtering: 7am-11am
- Detailed timeline with movement classification
- Velocity analysis by time period
- Golf activity likelihood assessment
- Gap detection (5+ minute periods)

**Domain Knowledge**:
```python
# Filter to morning period (7am-11am)
morning_locations = []
for loc in locations:
    timestamp = datetime.fromtimestamp(loc['tst'])
    if 7 <= timestamp.hour < 11:
        morning_locations.append(loc)

# Activity classification
if vel < 0.5:
    status = "STATIONARY"
elif vel < 2.5:
    status = "WALKING/GOLF"
elif vel < 4:
    status = "RUNNING"
else:
    status = f"VEHICLE ({vel_kmh:.1f} km/h)"
```

**Why It Was Needed**:
- Initial analysis showed golf sessions but timing was unclear
- Needed to isolate morning vs afternoon activity
- Validate if golf was played before noon or after

**Value for Future**:
- Reference for time-period filtering implementation
- Demonstrates importance of temporal context

---

### `analyze_golf_corrected.py` (5.7KB)
**Purpose**: Corrected golf analysis after discovering afternoon timing (not morning)

**Key Changes from Original**:
- Adjusted expected golf times to afternoon (15:00-18:00)
- Refined velocity thresholds based on actual data
- Improved session clustering logic

**Why Multiple Versions**:
- Initial assumption: Golf was in morning (7am-11am)
- Data revealed: Golf actually afternoon (3pm-6pm)
- Required iteration to match actual trip schedule

**Value for Future**:
- Demonstrates need for configurable time expectations
- Shows importance of validating assumptions against data

---

### `analyze_portugal_trip.py` (7.1KB)
**Purpose**: Comprehensive Portugal trip analysis with specific location recognition

**Key Features**:
- Portugal-specific location database (5 key locations)
- Haversine distance calculation
- Hourly activity summary
- Golf velocity classification (3-20 km/h)
- Location visit tracking with duration

**Portugal Locations Database**:
```python
PORTUGAL_LOCATIONS = {
    "Pine Cliffs Golf": {
        "lat": 37.093, "lon": -8.175, "radius": 300,
        "description": "Pine Cliffs Golf Course - 9 holes"
    },
    "Pingo Doce Vilamoura": {
        "lat": 37.1040, "lon": -8.1266, "radius": 150,
        "description": "Pingo Doce supermarket near Vilamoura"
    },
    "Armação de Pêra Beach": {
        "lat": 37.0999, "lon": -8.3551, "radius": 200,
        "description": "Armação de Pêra beach excursion"
    },
    "Faro Airport": {
        "lat": 37.0147, "lon": -7.9658, "radius": 500,
        "description": "Faro Airport (FAO)"
    },
    "Vila Vita Parc": {
        "lat": 37.0890, "lon": -8.1920, "radius": 200,
        "description": "Vila Vita Parc Resort (accommodation)"
    }
}
```

**Value for Future**:
- Template for trip-specific location databases
- Demonstrates need for temporary location sets
- Radius sizing guidance (supermarket: 150m, airport: 500m)

---

### `analyze_portugal_corrected.py` (7.3KB) - FINAL VERSION
**Purpose**: Final corrected analysis with accurate golf timing and comprehensive location tracking

**Key Improvements**:
- Corrected golf schedule per actual trip (Oct 20-24):
  - Oct 20 (Mon): Golf afternoon ~15:30
  - Oct 21 (Tue): Beach midday, Golf afternoon ~15:00-15:15
  - Oct 22 (Wed): Golf late morning/midday ~11:00-12:00
  - Oct 23 (Thu): Golf early afternoon ~12:00-13:00, Airport ~17:00
  - Oct 24 (Fri): Golf just after 11:00am

- Location visit analysis with time ranges
- Golf session clustering with 15-minute gap tolerance
- Hourly activity summary
- Validation against expected timing

**Critical Learning**:
```python
# Golf sessions grouped with gap tolerance
for i in range(1, len(golf_periods)):
    time_gap = (golf_periods[i]['time'] - current_session[-1]['time']).total_seconds() / 60

    if time_gap <= 15:  # Points within 15 minutes are same session
        current_session.append(golf_periods[i])
    else:
        if len(current_session) >= 5:  # At least 5 points to count
            golf_sessions.append(current_session)
        current_session = [golf_periods[i]]
```

**Value for Future**:
- **MOST IMPORTANT**: Use this version as reference for `GolfAnalyzer`
- Proven logic validated against actual trip data
- Demonstrates iterative refinement process

---

## How to Use This Archive

### For Reference During Implementation
When implementing the modular `GolfAnalyzer` class:

1. **Start with** `analyze_portugal_corrected.py` (most refined logic)
2. **Extract** velocity thresholds and session clustering logic
3. **Adapt** Portugal-specific code to generic analyzer
4. **Test** against Portugal trip data for regression validation

### For Regression Testing
```bash
# Test new GolfAnalyzer against known good results
python3 archive/analyze_portugal_corrected.py 2025-10-20
# Compare output with new analyzer:
python3 analyze_date_enhanced.py 2025-10-20 --enable-golf-analyzer
```

### For Learning Domain Knowledge
- Study velocity patterns unique to golf
- Understand stationary period detection
- Learn session clustering approaches
- See real-world location database structure

---

## Key Takeaways for Future System

### 1. Activity-Specific Analysis is Essential
Golf requires specialized detection beyond generic velocity classification:
- Walking pace (0.5-2.5 m/s) overlaps with normal walking
- Context matters: Same velocity at golf course ≠ same velocity at home
- Stationary periods are meaningful (tee boxes), not just noise

### 2. Temporal Filtering is Critical
- Morning golf (7am-11am) vs afternoon golf (3pm-6pm) analysis
- Time-of-day affects activity interpretation
- Need configurable time windows for analysis

### 3. Location Databases Must Be Extensible
- Trip-specific locations cannot be hardcoded
- Need mechanism to load temporary location sets
- Different venue types need different radius sizes

### 4. Iterative Refinement is Normal
- Initial assumptions may be wrong (morning vs afternoon golf)
- Data reveals actual patterns
- Configuration beats hardcoding for flexibility

### 5. Session Clustering Requires Domain Knowledge
- Gap tolerance (15 minutes for golf)
- Minimum session duration (20 minutes)
- Minimum data points (5+ for validity)
- Distance validation (500-3000m for 9 holes)

---

## Future Implementation Checklist

When building the improved location analysis system:

- [ ] Create `analyzers/golf_analyzer.py` using logic from `analyze_portugal_corrected.py`
- [ ] Implement time-period filtering (from `analyze_morning_golf.py`)
- [ ] Create trip location database template (from `analyze_portugal_trip.py` PORTUGAL_LOCATIONS)
- [ ] Add session clustering with gap tolerance (15-minute gap logic)
- [ ] Implement likelihood scoring (HIGH/MEDIUM/LOW assessment)
- [ ] Add velocity distribution analysis (stationary/walking/running percentages)
- [ ] Create `analyze_trip.py` for multi-day trip analysis
- [ ] Test new system against Portugal trip data (Oct 18-24, 2025)
- [ ] Validate: New system produces equivalent results to ad-hoc scripts

---

## Scripts NOT to Archive (Keep Active)

These scripts should remain in active use:
- ✅ `analyze_date_enhanced.py` - Primary daily analysis (works well)
- ✅ `analyze_date.py` - Simple fallback analysis
- ✅ `owntracks_client.py` - Core API client
- ✅ `location_analyzer.py` - Core analyzer (to be enhanced)
- ✅ `location_cache.py` - Caching system

---

## Contact & Questions

If implementing improvements and need context about these ad-hoc scripts:
- **Full Analysis**: See `ANALYSIS-IMPROVEMENTS.md` (comprehensive 15,000+ word analysis)
- **Quick Summary**: See `IMPROVEMENT-SUMMARY.md` (executive summary)
- **Trip Context**: Portugal family holiday Oct 18-24, 2025 (Algarve - Pine Cliffs area)
- **Golf Details**: 5 rounds of 9-hole golf at Pine Cliffs Golf Course

---

**Archive Status**: ✅ Complete
**Preservation Reason**: Domain knowledge + regression testing + implementation reference
**Safe to Delete?**: ❌ NO - Keep for future `GolfAnalyzer` implementation
**Expected Lifespan**: Permanent archive (valuable reference material)
