# Location Integration System

## Project Overview
Comprehensive location intelligence system using Owntracks for continuous location logging and analysis. Provides movement pattern insights, commute optimization, and location-based analytics with intelligent recognition of 15+ regular locations and automatic activity pattern detection.

## System Architecture (Updated Oct 2025)

### Self-Hosted Owntracks Platform
- **Service URL**: https://owntracks.gavinslater.co.uk/
- **API Endpoint**: `/api/0/locations`
- **Authentication**: HTTP Basic (no credentials required - open access)
- **User Identifier**: `gavin-iphone`
- **Device Identifier**: `a2ea00bc-9862-4efb-a6ab-f038e32beb4c`
- **Data Source**: Owntracks mobile app with continuous GPS logging
- **Architecture**: Self-hosted for complete privacy and data control

### Core Capabilities
- **Intelligent Location Recognition**: Automatically identifies 15+ known locations
- **Activity Pattern Detection**: Recognizes parkrun, dog walks, school runs, hospital visits
- **Velocity-Based Classification**: Distinguishes walking, running, cycling, driving
- **Historical Queries**: "Where was I on [date]?" with detailed timeline
- **Time Analysis**: Duration spent at specific locations with context
- **Pattern Recognition**: Daily routines, commute patterns, family commitments

### Enhanced Intelligence Features (NEW)
- **Known Locations Database** (`known_locations.json`):
  - Home (Esher), Office (Gresham Street), Transport hubs (Esher/Waterloo stations)
  - Kingston Hospital (medical appointments)
  - Bushy Park parkrun, Esher Common parkrun, Black Pond dog walking
  - Kimberly's School, Wimbledon Greyhound Welfare (Hersham)
  - University of Bath, Bath Skyline parkrun

- **Activity Pattern Recognition** (`regular-activities.json`):
  - Parkrun participation (Saturday 9am, cycling to Bushy Park 5.7km)
  - Dog walking with Roxy (evening walks to Black Pond/Esher Common)
  - School runs (morning drop-offs for Kimberly, 7:45-8:00am)
  - Medical appointments (Kingston Hospital for family healthcare)
  - Duke of Edinburgh volunteering (Sunday mornings with Kimberly)
  - Office commute (3 days/week: Mon/Tue/Thu typical)
  - University visits (Bath for Zachary)

- **Travel Mode Detection** (velocity-based):
  - Stationary: <1 m/s
  - Walking: 0.5-2 m/s (2-7 km/h)
  - Running: 2-4 m/s (7-14 km/h)
  - Cycling: 4-8 m/s (14-30 km/h)
  - Driving: >8 m/s (>30 km/h)

## Work Schedule Integration

### Current Work Pattern Context
- **Office Schedule**: 3 days in London office, typically Mon/Tue/Thu (flexible)
- **WFH Schedule**: 2 days work from home, usually Wed/Fri
- **Commute Route**: Esher → London Waterloo (6:52am train typical)
- **Office Location**: ICBC Standard Bank, Gresham Street, London (7:50am arrival target)
- **Return Journey**: 6-6:30pm finish, flexible return timing

### Schedule Optimization Features
- **Commute Analysis**: Travel time optimization and pattern identification
- **Office Day Planning**: Optimal office day selection based on calendar and meetings
- **WFH Efficiency**: Home productivity time analysis (correlates with low step count)
- **Schedule Flexibility**: Data-driven insights for schedule adjustments

## Technical Implementation

### Python Environment Setup
**Note**: This system works with system Python3 (dependencies typically already installed globally).

```bash
# Navigate to location integration directory
cd /Users/gavinslater/projects/life/integrations/location

# Run analysis directly with system Python3 (works without venv)
python3 analyze_date_enhanced.py YYYY-MM-DD

# Optional: Use virtual environment if preferred
# source location-env/bin/activate  # If venv exists
# pip install requests python-dateutil
```

**Important Notes**:
- System Python3 works fine (dependencies usually pre-installed)
- Virtual environment (`location-env`) is optional, not required
- Location Agent (.claude/agents/location-agent.md) uses this system
- Required dependencies: `requests`, `python-dateutil`

### Primary Analysis Script

**`analyze_date_enhanced.py`** - Intelligent location analysis with pattern recognition

```bash
# Usage (with virtual environment activated)
python3 analyze_date_enhanced.py YYYY-MM-DD

# Example
python3 analyze_date_enhanced.py 2025-10-10
```

**Features**:
- Automatic location identification (15+ known locations)
- Activity pattern recognition (parkrun, dog walks, school runs, hospital visits)
- Velocity-based travel mode classification
- Day type classification (Office Day / WFH Day)
- Time distribution analysis with percentages
- Pattern checkmarks (✓ Parkrun ✓ School drop-off ✓ Hospital visit ✓ Dog walk)

**Example Output**:
```
TIMELINE:
--------------------------------------------------------------------------------
07:43-07:51: Kimberly school drop-off (6m)
11:30-12:27: Kingston Hospital (Ryan dermatology appointment) (57m)
17:11-17:58: Black Pond dog walk with Roxy (15m)

TIME AT LOCATIONS:
--------------------------------------------------------------------------------
Home: 20h 56m (88%)
Kingston Hospital: 57m (4%)
Travel (driving): 1h 8m (5%)

DAY TYPE & PATTERN RECOGNITION:
--------------------------------------------------------------------------------
✓ WFH Day
✓ School drop-off (Kimberly)
✓ Kingston Hospital visit
✓ Dog walk with Roxy
```

### Fallback Script

**`analyze_date.py`** - Basic location analysis without enhanced intelligence (simpler fallback)

### Owntracks API Integration

**`owntracks_client.py`** - Core API client

**Critical API Method**:
```python
def get_locations_for_date(self, user: str, device: str, target_date: str) -> Dict:
    """
    Get all locations for a specific date

    Args:
        user: 'gavin-iphone'
        device: 'a2ea00bc-9862-4efb-a6ab-f038e32beb4c'
        target_date: 'YYYY-MM-DD'

    Returns:
        {'success': True, 'data': [...location points...], 'count': 4795}
    """
```

**IMPORTANT**: Use `get_locations_for_date()` for historical queries, NOT `get_locations()` (which only returns recent data).

### Intelligence Data Files

**`known_locations.json`** - Location database with coordinates and recognition radius
- Organized by category: home, work, health, fitness, family, university
- Each location includes: name, lat/lon coordinates, radius (meters), category, description
- Used by `analyze_date_enhanced.py` for automatic location identification

**`regular-activities.json`** - Activity pattern database
- Recurring activities: parkrun, dog walking, office commute, Duke of Edinburgh volunteering
- Family commitments: school runs, medical appointments, university visits
- Each activity includes: schedule, participants, locations, duration, context
- Used for pattern recognition and activity correlation

## Agent Integration

### Location Agent Configuration
Located at: `/.claude/agents/location-agent.md`

**Execution Protocol**:
1. Navigate to `/Users/gavinslater/projects/life/integrations/location/` directory
2. Run `python3 analyze_date_enhanced.py YYYY-MM-DD` (system Python3)
3. Parse output for timeline, time distribution, pattern recognition

**User/Device Credentials** (configured in agent):
- **OWNTRACKS_USER**: `gavin-iphone`
- **OWNTRACKS_DEVICE**: `a2ea00bc-9862-4efb-a6ab-f038e32beb4c`

### Daily Journal Integration

The location-agent is used by:
- **Morning workflow** (`/daily-journal-morning`): Completes yesterday's location data with full timeline
- **Evening workflow** (`/daily-journal-evening`): Provides evening-only location snapshot

**Workflow**:
1. Morning: Retrieve complete yesterday location data (tracking finished overnight)
2. Parse enhanced output (recognized locations, activity patterns)
3. Update daily note with meaningful timeline (e.g., "Kingston Hospital (Ryan dermatology)" not "Unknown location")
4. Add pattern recognition notes (✓ WFH Day ✓ School drop-off ✓ Dog walk)

### Common Usage Patterns
- **"Where was I on [date]?"** → Timeline with recognized location names
- **"Analyze my commute this week"** → Office vs WFH pattern analysis
- **"Dog walking frequency?"** → Black Pond visits detected automatically
- **"Hospital visits?"** → Kingston Hospital visits recognized
- **"Parkrun locations?"** → Bushy Park vs Esher Common identification with cycling detection

## Data Privacy & Security

### Self-Hosted Benefits
- **Complete Data Ownership**: All location data stored on personal infrastructure
- **Privacy Protection**: No third-party access to location information
- **Custom Retention**: Configurable data retention policies (currently ~3 weeks visible)
- **Access Control**: Open access to personal Owntracks instance (no external exposure)

### Data Security Measures
- **Encrypted Storage**: Location data encrypted at rest
- **Secure Transmission**: HTTPS-only API communication
- **Local Processing**: All analysis performed locally via Python scripts
- **No External Services**: Geocoding and analysis done without external API calls

## File Structure

**Location**: `/Users/gavinslater/projects/life/integrations/location/`

```
integrations/location/
├── __init__.py                      # Python package marker
├── owntracks_client.py              # Core Owntracks API client
├── location_analyzer.py             # Location analysis logic (used by location_agent.py)
├── location_cache.py                # Caching system (used by location_agent.py)
├── location_agent.py                # Python class-based coordinator (NOT used by Claude Code agent)
├── analyze_date_enhanced.py         # PRIMARY: Intelligent analysis script ✅
├── analyze_date.py                  # FALLBACK: Basic analysis script
├── known_locations.json             # Location database (15+ locations)
├── regular-activities.json          # Activity pattern database
├── requirements.txt                 # Python dependencies
├── CLAUDE.md                        # This file - technical documentation
└── README.md                        # User-facing documentation
```

**Notes**:
- **System Python3**: Works without virtual environment (dependencies pre-installed)
- **location_agent.py**: Well-structured Python class for programmatic access, NOT currently used by Claude Code agent (which executes bash scripts directly). Kept for potential future use.
- **No cleanup needed**: Documentation current and accurate as of Oct 2025

## Analytics Examples

### Office Day Detection
```
Timeline:
07:00-07:43: Home
07:43-07:51: Esher Station (commute start)
07:51-08:05: London Waterloo (train arrival)
08:05-08:15: Walking to office
08:15-17:30: ICBC Standard Bank Office
17:30-18:45: Commute home

Pattern: ✓ Office Day (9h 15m office time)
```

### WFH Day with Activities
```
Timeline:
07:43-07:51: Kimberly school drop-off
11:30-12:27: Kingston Hospital (Ryan dermatology)
17:11-17:58: Black Pond dog walk with Roxy
Home time: 20h 56m (88%)

Pattern: ✓ WFH Day ✓ School drop-off ✓ Hospital visit ✓ Dog walk
```

### Saturday Parkrun
```
Timeline:
08:30-08:49: Cycling to parkrun (5.7km)
08:49-09:47: Bushy Park parkrun (58m including pre/post)
09:47-10:05: Cycling home

Pattern: ✓ Parkrun: Bushy Park ✓ Cycling activity detected
```

## Troubleshooting

### Common Issues

**Issue**: Location-agent returns "No location data available"
- **Cause**: Using wrong API method (`get_locations()` instead of `get_locations_for_date()`)
- **Solution**: Ensure agent uses `analyze_date_enhanced.py` which uses correct API

**Issue**: Locations showing as "Unknown" or "Travel"
- **Cause**: Location not in `known_locations.json`
- **Solution**: Add new location with coordinates and radius to database

**Issue**: Virtual environment not found
- **Cause**: Wrong directory or environment not created
- **Solution**: Navigate to `/location-integration/` and verify `location-env/` exists

**Issue**: Pattern not recognized
- **Cause**: Activity not in `regular-activities.json` or coordinates don't match
- **Solution**: Update activity database with correct location coordinates and patterns

### Data Quality

- **Typical Data Volume**: 3,000-5,000 location points per day
- **Tracking Span**: Usually 23-24 hours per day
- **Resolution**: ~10-30 second intervals during movement
- **Accuracy**: ±10-50 meters depending on GPS conditions

## Performance

- **API Response**: <1 second for single-day queries
- **Analysis Time**: 2-5 seconds for enhanced pattern recognition
- **Cache**: Locations cached for 3-4 weeks
- **Battery Impact**: Minimal (optimized Owntracks logging)

## Future Enhancements

- [ ] Automatic detection of new frequent locations (auto-add to known_locations.json)
- [ ] Weekly/monthly pattern reports
- [ ] Commute efficiency scoring
- [ ] Integration with calendar for meeting location optimization
- [ ] Geocoding integration for human-readable addresses
- [ ] Offline capability with cached data

---

**Last Updated**: October 31, 2025
**System Status**: ✅ Fully operational with enhanced intelligence
**Primary Script**: `analyze_date_enhanced.py` (system Python3, no venv required)
**Directory**: `/Users/gavinslater/projects/life/integrations/location/`
**Known Locations**: 15+ recognized locations
**Activity Patterns**: 8 major activity types recognized
