# Location Analysis System - Improvement Summary

**Quick Reference Guide** | Full Details: [ANALYSIS-IMPROVEMENTS.md](./ANALYSIS-IMPROVEMENTS.md)

---

## Problem Statement

Portugal trip (Oct 18-24, 2025) required creating **5 ad-hoc Python scripts** because `location_analyzer.py` couldn't handle:
- Golf activity detection (walking pace + stationary periods at tee boxes)
- Flight detection (high altitude + speed)
- Specific venue recognition (Pine Cliffs Resort, Pingo Doce, Armação de Pêra)
- Time-specific analysis (morning vs afternoon golf)

---

## Root Causes (Top 5 Limitations)

### 1. Hardcoded Location Database
- Only 3 UK locations in code (Home, Office, Esher Station)
- Cannot add trip-specific locations without code changes
- No mechanism for temporary location sets

### 2. No Activity-Specific Analyzers
- Generic time-at-location only
- Missing: Golf, Parkrun, Dog Walking, Flight detection
- No domain-specific pattern recognition

### 3. No Time-Period Filtering
- Cannot analyze morning (7am-11am) vs afternoon (3pm-6pm)
- All analysis operates on full day

### 4. Limited Velocity Classification
- No altitude tracking (can't detect flights)
- No golf-specific patterns (walking pace + stationary)
- No configurable thresholds

### 5. No Venue/POI Recognition System
- Cannot handle complex venue types (airports, golf courses, resorts)
- No polygon-based boundaries (only circular radius)

---

## Solution Architecture (4 Key Changes)

### 1. Modular Activity Analyzers
```
BaseActivityAnalyzer (abstract class)
  ├── GolfAnalyzer (velocity: 0.5-2.5 m/s, stationary periods, 20min-3hr sessions)
  ├── ParkrunAnalyzer (Saturday 9am, running pace 2-4 m/s, 5km distance)
  ├── FlightAnalyzer (altitude + speed + airport proximity)
  └── DogWalkingAnalyzer (Black Pond route, evening timing)
```

### 2. Dynamic Location Databases
```
locations/
  ├── base_locations.json (permanent UK locations - 15+ already configured)
  ├── trips/
  │   ├── portugal_2025-10.json (Pine Cliffs, Pingo Doce, Faro Airport)
  │   └── usa_2025-12.json (future trips)
  └── auto_discovered.json (frequently visited unknowns)
```

### 3. Configuration-Driven Analysis
```json
{
  "activity_analyzers": {
    "golf": {
      "velocity_range": [0.5, 2.5],
      "min_session_minutes": 20,
      "expected_distance_range": [500, 3000]
    }
  }
}
```

### 4. Enhanced Core Capabilities
- Time-period filtering (by hour, date range, custom windows)
- Velocity statistics (mean, median, std dev, stationary %)
- Distance calculation (total meters covered)
- Pattern detection (stop-and-go, consistent speed)

---

## Recommended File Organization

### Current State (Flat Structure - Messy)
```
integrations/location/
├── location_analyzer.py (19KB - monolithic)
├── analyze_date_enhanced.py (9.5KB - works well)
├── analyze_golf_activity.py (9.9KB - ad-hoc)
├── analyze_morning_golf.py (6.5KB - ad-hoc)
├── analyze_portugal_trip.py (7.1KB - ad-hoc)
├── analyze_golf_corrected.py (5.7KB - ad-hoc)
└── analyze_portugal_corrected.py (7.3KB - ad-hoc)
```

### Proposed State (Organized Structure - Clean)
```
integrations/location/
├── core/ (framework)
│   ├── location_analyzer.py (enhanced base)
│   ├── velocity_classifier.py (centralized velocity logic)
│   ├── owntracks_client.py
│   └── location_cache.py
│
├── analyzers/ (specialized modules)
│   ├── base_activity_analyzer.py
│   ├── golf_analyzer.py
│   ├── parkrun_analyzer.py
│   └── dog_walking_analyzer.py
│
├── config/ (tunable parameters)
│   ├── analysis_config.json
│   └── velocity_thresholds.json
│
├── locations/ (location databases)
│   ├── base_locations.json
│   ├── regular_activities.json
│   └── trips/
│       └── portugal_2025-10.json
│
├── scripts/ (user-facing tools)
│   ├── analyze_date_enhanced.py (daily analysis)
│   ├── analyze_trip.py (multi-day trips)
│   └── discover_locations.py (find frequent unknowns)
│
└── archive/ (reference only)
    ├── README.md (explains purpose)
    ├── analyze_golf_activity.py (Portugal Oct 2025)
    ├── analyze_morning_golf.py
    ├── analyze_golf_corrected.py
    ├── analyze_portugal_trip.py
    └── analyze_portugal_corrected.py
```

---

## Priority Recommendations (Top 3)

### 1. Golf Activity Analyzer (HIGH PRIORITY)
**Why**: Recurring activity (Portugal trip, future golf trips)
**Effort**: 1 week (port logic from ad-hoc scripts)
**Impact**: Eliminates need for 3-4 future ad-hoc scripts

**Key Features**:
- Velocity pattern: 0.5-2.5 m/s walking, <0.5 m/s stationary
- Stationary detection: 5-30 second pauses at tee boxes
- Session duration: 20 minutes - 3 hours
- Distance validation: 500-3000m for 9 holes
- Likelihood scoring: HIGH/MEDIUM/LOW

### 2. Multi-Day Trip Analyzer (HIGH PRIORITY)
**Why**: Trips are common (Portugal, US Christmas, Bath visits)
**Effort**: 1 week
**Impact**: Single command for entire trip analysis

**Usage**:
```bash
python3 analyze_trip.py 2025-10-19 2025-10-24 --trip portugal_2025-10
```

**Features**:
- Load trip-specific location database
- Day-by-day timeline
- Trip summary (time at each location)
- Activity detection across days
- Travel day identification

### 3. Dynamic Location Database Loading (HIGH PRIORITY)
**Why**: Enables trip analysis without code changes
**Effort**: 3 days (refactor LocationAnalyzer.__init__)
**Impact**: Core capability for all future enhancements

**Implementation**:
```python
analyzer = LocationAnalyzer()
analyzer.load_trip_locations('portugal_2025-10')
analyzer.analyze_date('2025-10-19')
```

---

## Implementation Roadmap (6-8 Weeks)

### Phase 1: Foundation (Week 1-2)
- Create directory structure
- Archive ad-hoc scripts with README
- Refactor to load `base_locations.json`
- Add time-period filtering

### Phase 2: Golf Analysis (Week 3)
- Create `GolfAnalyzer` class
- Port logic from ad-hoc scripts
- Test with Portugal data
- Validate results

### Phase 3: Trip Analysis (Week 4)
- Create `analyze_trip.py`
- Implement trip location loading
- Auto-detect trip context
- Test with Portugal trip

### Phase 4: Additional Analyzers (Week 5-6)
- `ParkrunAnalyzer`
- `DogWalkingAnalyzer`
- `CommuteAnalyzer`
- Integration with `analyze_date_enhanced.py`

### Phase 5: Discovery & Optimization (Week 7-8)
- Auto-discovery of frequent locations
- Centralized velocity classification
- Unit tests
- Documentation updates

---

## Success Metrics

### Quantitative:
- ✅ **Ad-hoc Script Reduction**: 5 scripts (Portugal) → 0 scripts (future trips)
- ✅ **Analysis Time**: 2+ hours (creating scripts) → <5 minutes (using tools)
- ✅ **Activity Detection Accuracy**: >90% for golf, parkrun, dog walks
- ✅ **Location Coverage**: 3 locations → 15+ UK + trip-specific

### Qualitative:
- ✅ **Ease of Use**: Single command for trip analysis
- ✅ **Maintainability**: Modular design, clear separation
- ✅ **Extensibility**: New activities without core changes
- ✅ **Reusability**: Analyzers work across contexts

---

## Key Learnings from Portugal Trip

### What Worked Well:
1. **JSON-based location database** (`known_locations.json`) - excellent structure
2. **Enhanced daily analysis** (`analyze_date_enhanced.py`) - good pattern recognition
3. **Velocity classification** - accurate for basic activities
4. **Owntracks API** - reliable data source

### What Didn't Work:
1. **Hardcoded locations** - couldn't add Pine Cliffs, Pingo Doce
2. **No golf analyzer** - required custom velocity + stationary logic
3. **No time filtering** - needed separate morning/afternoon scripts
4. **Manual corrections** - timing errors required multiple script versions

### Critical Success Factors:
1. **Domain knowledge matters** - Golf has unique velocity patterns (0.5-2.5 m/s)
2. **Context is essential** - Same velocity means different things at golf course vs home
3. **Configuration beats hardcoding** - Parameters should be tunable
4. **Modularity enables reuse** - Activity analyzers work across different trips

---

## Research-Backed Best Practices

### Activity Recognition (Academic Studies):
- **Velocity + context**: 96-99% accuracy
- **Rule-based + ML hybrid**: Best for personal use
- **Activity-specific thresholds**: Golf (0.5-2.5 m/s) ≠ Running (2-4 m/s)

### POI Recognition (Commercial Systems):
- **Radius guidelines**: Small (50-100m), Medium (100-200m), Large (200-500m), Very Large (500-1000m+)
- **Centroid matching**: Works well for most cases (current approach valid)
- **Polygon geofencing**: Only needed for complex shapes (golf courses, parks)

### Temporal Patterns:
- **Session duration**: Minimum thresholds prevent false positives
- **Gap tolerance**: 5-15 minute gaps still same activity
- **Time-of-day context**: Parkrun (Saturday 9am), Golf (variable)

---

## Next Steps

1. **Review this summary** with full details in `ANALYSIS-IMPROVEMENTS.md`
2. **Prioritize phases** based on upcoming trips/needs
3. **Start with Phase 1** (foundation) - 1-2 weeks
4. **Archive ad-hoc scripts** with explanatory README
5. **Test incrementally** to avoid breaking existing workflows

---

**Full Analysis**: [ANALYSIS-IMPROVEMENTS.md](./ANALYSIS-IMPROVEMENTS.md) (15,000+ words)
**Status**: ✅ Complete and ready for implementation
**Estimated ROI**: 2+ hours saved per trip × 4-6 trips/year = 8-12 hours annually
