# Health Integration System

Comprehensive health and fitness data integration providing quantified self analytics through automated Apple Health sync and parkrun performance tracking.

## System Overview

**Production Status**: ✅ Fully operational (October 2025)

The health integration system combines:
- **Apple Health Auto Export**: Automated 30-minute sync of 19+ health metrics via iOS app webhook
- **Parkrun Integration**: Official parkrun.org API for running performance tracking (273+ lifetime results)
- **SQLite Database**: 5.3M+ health records from 2010-2025 with device-priority deduplication
- **Node.js Service**: RESTful API on localhost:3001 for data access and analysis

### Key Metrics
- **Total Records**: 5,300,724 unique health measurements (2010-2025)
- **Step Count**: 2.7M+ records from Apple Watch (primary) and iPhone (fallback)
- **Heart Rate**: 1.8M+ measurements including resting HR, HRV, and continuous monitoring
- **Body Measurements**: 6,896 weight readings from Withings scale
- **Workouts**: Running, cycling, strength training, and 70+ workout types
- **Sleep Analysis**: Comprehensive sleep tracking via Sleep Cycle integration

## Quick Start

### Start Health Service
```bash
cd /Users/gavinslater/projects/life/health-integration/health-service
npm start
# Service runs on localhost:3001
```

### Python Client Access
```python
from health_data_client import HealthClient

client = HealthClient()

# Get recent parkrun results
parkrun_stats = client.get_parkrun_stats()

# Get step count (Apple Watch priority)
steps = client.get_steps(date='2025-10-05')  # Returns 9,966 (not double-counted)

# Get weekly health summary
summary = client.get_health_summary(days=7)
```

### Health Service API
```bash
# Get parkrun statistics
curl http://localhost:3001/parkrun/stats

# Get Apple Health metrics
curl http://localhost:3001/api/apple-health/metrics/step_count?days=7

# Get recent workouts
curl http://localhost:3001/api/apple-health/workouts?days=30
```

## Architecture

```
Apple Health (iPhone/Watch)
    ↓ (30-min automated sync)
Health Auto Export App
    ↓ (REST API webhook)
localhost:3001/api/apple-health/auto-export
    ↓ (process & store)
SQLite Database (health.db)
    ↓ (query with device priority)
Health Agent Analysis
```

### Data Flow
1. **Apple Watch/iPhone**: Records health metrics continuously
2. **Auto Export App**: Syncs data every 30 minutes via background process
3. **Health Service**: Receives webhook POST, validates, stores in SQLite
4. **Database**: Applies unique constraint to prevent duplicates
5. **Python Client**: Queries with device-priority logic (Apple Watch > iPhone)
6. **Health Agent**: Analyzes trends, provides insights, tracks goals

## Apple Health Auto Export Integration

### Setup
- **App**: Health Auto Export - JSON+CSV (iOS App Store)
- **Subscription**: Premium ($2.99/month after 7-day trial)
- **Endpoint**: `POST http://192.168.5.235:3001/api/apple-health/auto-export`
- **Sync Frequency**: 30 minutes (48 syncs/day maximum)
- **Date Range**: "Since Last Sync" (prevents duplicates)
- **Background Sync**: Enabled (runs when device unlocked)

### Tracked Metrics (19+ Types)
**Activity & Movement**:
- Step Count, Walking/Running Distance, Flights Climbed
- Active Energy Burned, Exercise Minutes
- Walking Speed, Running Speed, Step Length

**Heart Health**:
- Heart Rate (continuous), Resting Heart Rate
- Heart Rate Variability (HRV), Walking Heart Rate Average
- Cardio Recovery (1-minute), VO2 Max

**Body Measurements**:
- Weight (Withings scale), Body Mass Index, Body Fat Percentage

**Sleep & Recovery**:
- Sleep Analysis (Sleep Cycle app integration)
- Stand Time, Stand Hour tracking

**Workouts**: 70+ types including Running, Cycling, Strength Training, Swimming, etc.

### Configuration Details
See `apple-health-auto-export-setup.md` for complete setup instructions.

## Parkrun Integration

### Features
- **Official API**: parkrun.js v1.3.1 library for parkrun.org data
- **Results**: 273+ lifetime parkrun results fully synchronized
- **2025 Activity**: 31 confirmed runs with detailed performance tracking
- **Metrics**: Times, positions, age grades, personal bests, venue analysis
- **Consistency**: Weekly participation patterns and trend analysis

### Parkrun Endpoints
```javascript
GET /parkrun/results       // All parkrun results
GET /parkrun/stats         // Performance statistics
GET /parkrun/venues        // Venue-specific analysis
GET /parkrun/trends        // Performance progression
GET /parkrun/2025          // 2025 specific results
GET /parkrun/consistency   // Participation patterns
```

## Database Schema

### health_metrics Table
```sql
CREATE TABLE health_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_type TEXT NOT NULL,           -- 'step_count', 'heart_rate', etc.
    metric_source TEXT NOT NULL,         -- 'health_export_complete', 'auto_export'
    metric_date TEXT NOT NULL,           -- ISO datetime when measured
    metric_value REAL,                   -- Numeric value
    metric_unit TEXT,                    -- 'count', 'count/min', 'kcal', etc.
    additional_data TEXT,                -- JSON: {"source": "Gavin's Apple Watch"}
    created_at TEXT NOT NULL,            -- When imported
    UNIQUE(metric_type, metric_source, metric_date, metric_value)  -- Deduplication
);
```

### Indexes
- `idx_health_metrics_type` - Fast metric type filtering
- `idx_health_metrics_date` - Date range queries
- `idx_health_metrics_source` - Device source filtering
- `idx_health_metrics_type_date` - Combined metric/date queries

## Device Priority System

**Critical**: Always filter by device source to avoid double-counting when both Apple Watch and iPhone record the same metric.

### Priority Hierarchy
1. **Apple Watch** - Most accurate for activity metrics (steps, heart rate, exercise)
2. **Withings Scale** - Body measurements (weight, BMI, body fat)
3. **Sleep Cycle** - Sleep analysis
4. **iPhone** - Fallback when Apple Watch not available

### Example Query (Device Priority)
```sql
-- Get step count from Apple Watch only (avoid double-counting)
SELECT SUM(metric_value) as total_steps
FROM health_metrics
WHERE metric_type = 'step_count'
AND metric_date >= '2025-10-05 00:00:00'
AND metric_date < '2025-10-06 00:00:00'
AND additional_data LIKE '%Apple Watch%';  -- Priority device
```

### Verification
- October 5, 2025: Apple Watch 9,966 steps ✅ (iPhone 8,542 ignored)
- October 4, 2025: Apple Watch 19,951 steps ✅ (iPhone 24,239 ignored)

See `device-priority-guidelines.md` for comprehensive querying patterns.

## Python Client

### Installation
```bash
cd /Users/gavinslater/projects/life/health-integration/python-client
# Virtual environment managed by health service
```

### Usage
```python
from health_data_client import HealthClient

client = HealthClient(base_url='http://localhost:3001')

# Parkrun statistics
stats = client.get_parkrun_stats()
print(f"Total parkruns: {stats['total_runs']}")
print(f"2025 runs: {stats['runs_2025']}")

# Health metrics with device priority
steps_today = client.get_metric_with_priority(
    metric_type='step_count',
    date_start='2025-10-06 00:00:00',
    date_end='2025-10-07 00:00:00'
)
print(f"Steps: {steps_today['value']} from {steps_today['source']}")

# Weekly summary
summary = client.get_health_summary(days=7)
print(f"Avg daily steps: {summary['avg_steps']:,.0f}")
print(f"Avg heart rate: {summary['avg_heart_rate']:.1f} bpm")
```

## Health Service API

### Core Endpoints

#### Parkrun
```bash
# Get all statistics
GET /parkrun/stats

# Get 2025 results
GET /parkrun/2025

# Get performance trends
GET /parkrun/trends
```

#### Apple Health Metrics
```bash
# Get specific metric
GET /api/apple-health/metrics/{metric_type}?days=30&limit=100

# Available metrics:
# - step_count
# - heart_rate
# - active_energy
# - walking_running_distance
# - weight_body_mass
# - sleep_analysis
# - resting_heart_rate
# - heart_rate_variability
# - flights_climbed
# - vo2_max
```

#### Auto Export Webhook
```bash
# Receive data from iOS app (POST only)
POST /api/apple-health/auto-export
Content-Type: application/json

{
  "data": {
    "metrics": [...],
    "workouts": [...]
  }
}
```

#### Import Statistics
```bash
# Get Auto Export import stats
GET /api/apple-health/auto-export/stats

# Get recent imports
GET /api/apple-health/auto-export/recent?days=7
```

## Data Management

### Database Rebuild
Use when you need to rebuild the entire database from a fresh Apple Health export:

```bash
cd /Users/gavinslater/projects/life/health-integration/scripts

# Create fresh Apple Health export on iPhone:
# Settings → Privacy & Security → Health → Export All Health Data
# AirDrop export.zip to Mac, unzip to apple_health_export_new/

# Run rebuild script
python3 rebuild_health_database.py

# Expected output:
# - Processes 5.3M+ records
# - Excludes family members' data (Raquel's devices)
# - Applies deduplication via UNIQUE constraint
# - Imports 2010-2025 data in ~20 minutes
```

### Backup Strategy
```bash
# Backup current database
cp health-service/data/health.db health-service/data/health.db.backup

# Check database size
ls -lh health-service/data/health.db
# Expected: ~450MB for 5.3M records
```

## Quantified Self Integration

### Health Goals Tracking
- **Weight Management**: Target 175→170 lbs (tracked via Withings)
- **Activity Consistency**: 10,000+ steps daily average
- **Parkrun Participation**: Weekly Saturday morning routine
- **Heart Health**: Monitor resting HR trends and HRV
- **Sleep Quality**: Track sleep duration and consistency

### Analytics Capabilities
- **Performance Trends**: Week-over-week, month-over-month comparisons
- **Correlation Analysis**: Health metrics vs. activity patterns
- **Goal Progress**: Visual tracking of targets (steps, weight, exercise)
- **Anomaly Detection**: Identify unusual patterns or concerning trends
- **Parkrun Optimization**: Correlate performance with training metrics

### Example Insights
```python
# Weekly health report
client = HealthClient()
summary = client.get_weekly_report()

print(f"""
Weekly Health Summary:
- Avg Steps: {summary['avg_steps']:,.0f} (Goal: 10,000)
- Avg Heart Rate: {summary['avg_hr']:.1f} bpm
- Resting HR: {summary['resting_hr']:.1f} bpm
- Parkruns: {summary['parkruns_completed']}
- Weight Trend: {summary['weight_change']:.1f} lbs
""")
```

## Troubleshooting

### Health Service Not Running
```bash
# Check service status
curl http://localhost:3001/health

# View service logs
cd /Users/gavinslater/projects/life/health-integration/health-service
tail -f logs/health-service.log

# Restart service
npm start
```

### Auto Export Not Syncing
1. **Check iPhone Connection**: Verify iPhone on same WiFi as Mac (192.168.5.x)
2. **Test Endpoint**: Open `http://192.168.5.235:3001/health` in iPhone Safari
3. **Check Auto Export Settings**:
   - Date Range: "Since Last Sync" (not "Default")
   - Interval: 30 minutes
   - Background Sync: Enabled
4. **View Import Logs**: `GET /api/apple-health/auto-export/recent`

### Database Queries Slow
```bash
# Verify indexes exist
sqlite3 health.db ".schema health_metrics"

# Check record count
sqlite3 health.db "SELECT COUNT(*) FROM health_metrics;"

# Optimize database
sqlite3 health.db "VACUUM;"
```

### Double-Counting Issues
Always use device-priority queries. See `device-priority-guidelines.md` for:
- SQL query patterns with device filtering
- Python helper functions
- Metric-specific device priorities

## Files Overview

```
health-integration/
├── health-service/              # Node.js microservice
│   ├── src/
│   │   ├── health-api.js       # API endpoints (parkrun + Apple Health)
│   │   ├── health-database.js  # SQLite database management
│   │   ├── parkrun-client.js   # Parkrun.js integration
│   │   └── logger.js           # Winston logging
│   ├── data/
│   │   └── health.db           # Main database (5.3M records)
│   ├── logs/                   # Service logs
│   ├── package.json
│   └── README.md
├── python-client/
│   ├── health_data_client.py   # Python client for agents
│   └── __init__.py
├── scripts/
│   └── rebuild_health_database.py  # Database rebuild from export
├── apple-health-auto-export-setup.md  # iOS app setup guide
├── device-priority-guidelines.md      # Query best practices
├── CLAUDE.md                   # Project-level context
└── README.md                   # This file
```

## Security & Privacy

### Data Protection
- **Local Storage**: All health data remains on your Mac
- **No Cloud Sync**: Database never transmitted externally
- **Network Access**: Health service bound to localhost + local network only
- **Device Filtering**: Excludes family members' data (319 records from Raquel's devices filtered out)

### Authentication
- **Auto Export Webhook**: Currently no authentication (local network only)
- **Future**: Consider adding API key for webhook endpoint

## Performance

### Database Statistics
- **Size**: ~450MB for 5.3M records
- **Date Range**: 2010-08-31 to 2025-10-06 (15 years)
- **Query Speed**: <1 second for typical date range queries
- **Import Speed**: ~20 minutes for complete rebuild from XML export

### Auto Export Efficiency
- **Sync Frequency**: Every 30 minutes (48 syncs/day max)
- **Data Volume**: ~50-200 records per sync (varies by activity)
- **Network Impact**: Minimal (~10KB per sync)
- **Battery Impact**: Negligible (background sync when unlocked)

## Health Agent Integration

The health agent accesses this system via:

1. **Python Client**: `health_data_client.py` for programmatic access
2. **Direct API**: REST endpoints for specific queries
3. **Device Priority**: Automatic handling of multi-device metrics
4. **Goal Tracking**: Integrated with Gavin's quantified self objectives

### Agent Capabilities
- Daily health briefings with trends
- Parkrun performance analysis and recommendations
- Weight tracking and goal progress
- Activity pattern recognition
- Health alert generation (anomalies, achievements)
- Correlation with other life events (travel, work schedule)

## Maintenance

### Weekly Tasks
- Monitor Auto Export sync success rate
- Review logs for errors or anomalies
- Verify database size within expected range

### Monthly Tasks
- Analyze parkrun performance trends
- Review health goal progress (weight, steps, consistency)
- Check for Auto Export app updates

### Quarterly Tasks
- Consider full database backup
- Review and optimize slow queries
- Update metric tracking based on new health goals

## Future Enhancements

### Planned Features
- Strava integration for detailed workout analysis
- Fitbit sync for additional data sources
- Automated health insights generation
- Integration with calendar for activity correlation
- Advanced analytics dashboard

### Under Consideration
- Garmin Connect integration
- MyFitnessPal nutrition tracking
- Oura Ring sleep analysis
- Apple Health trend notifications

---

**Status**: Production-ready system with 5.3M health records, automated sync, and comprehensive analytics.

**Last Updated**: October 6, 2025
