# Health Integration System

## Project Overview
Comprehensive health and fitness data integration system providing quantified self analytics through:
- **Parkrun Integration**: Official parkrun.org API for running performance tracking
- **Apple Health Auto Export**: Automated 30-minute sync of 150+ health metrics and 70+ workout types
- **Future Integrations**: Fitbit, Strava, Garmin Connect (planned)

Built around Node.js microservice architecture with Python client wrapper for seamless agent integration. **Apple Health Auto Export fully implemented October 2025**.

## System Architecture

### Multi-Platform Design
- **Active Integrations**:
  - **Parkrun.org**: 273+ total results, 31 runs in 2025 via parkrun.js API
  - **Apple Health Auto Export**: Automated sync via iOS app webhook (implemented Oct 2025)
- **Future Platforms**: Fitbit, Strava, Garmin Connect (planned)
- **Architecture**: Node.js microservice with Python client wrapper
- **Data Storage**: SQLite database with automated import tracking
- **Sync Frequency**:
  - Apple Health: 30-minute automated background sync
  - Parkrun: Weekly updates after Saturday events

### Project Structure
```
health-integration/
├── CLAUDE.md                      # Technical documentation
├── README.md                      # User documentation
├── apple-health-auto-export-setup.md  # Setup guide
├── device-priority-guidelines.md  # Query patterns for device filtering
├── file-audit.md                  # Directory cleanup audit (Oct 11, 2025)
├── health-service/                # Node.js microservice
│   ├── src/                       # Source code
│   │   ├── health-api.js         # Express.js server & REST API
│   │   ├── health-database.js    # SQLite database class
│   │   ├── logger.js             # Winston logging
│   │   └── parkrun-client.js     # Parkrun API client
│   ├── data/                      # Database storage
│   │   └── health.db             # Main database (1.7GB, 5.3M records)
│   ├── logs/                      # Service logs
│   │   ├── error.log             # Error logging
│   │   └── health-service.log    # Service logging
│   ├── package.json               # Dependencies (parkrun.js v1.3.1)
│   ├── .env                       # Environment configuration
│   ├── health-api-fix-summary.md  # Oct 11 API fix documentation
│   └── README.md                  # Service documentation
├── python-client/                 # Optional Python wrapper
│   ├── health_data_client.py     # REST API wrapper class
│   ├── __init__.py
│   └── venv/                      # Python virtual environment
└── scripts/                       # Utility scripts
    └── rebuild_health_database.py  # Database rebuild tool
```

## Apple Health Auto Export Integration (NEW - Oct 2025)

### Implementation Details
- **App**: Health Auto Export - JSON+CSV (iOS App Store)
- **Method**: Automated REST API webhook to local health service
- **Endpoint**: `POST /api/apple-health/auto-export`
- **Format**: JSON payload with metrics and workouts arrays
- **Sync Cadence**: 30 minutes (up to 48 syncs/day)
- **Background Sync**: Enabled (runs when device unlocked)

### Metrics Tracked (Core + Additional)
**Core Metrics**:
- Steps, Heart Rate, Active Energy Burned
- Walking + Running Distance, Body Weight

**Additional Metrics**:
- Sleep Analysis, Resting Heart Rate
- Exercise Minutes, Flights Climbed, VO2 Max

**Workouts**: 70+ workout types (Running, Walking, Cycling, Strength, etc.)

### Data Flow
```
iPhone Health App
    ↓ (automated 30-min sync)
Health Auto Export App
    ↓ (HTTP POST with JSON)
localhost:3001/api/apple-health/auto-export
    ↓ (process & store)
SQLite Database (health.db)
    ↓ (query & analyze)
Health Agent / Python Analysis
```

### Storage Schema
- **Import Tracking**: `apple_health_auto_export` table
  - Import timestamp, metrics/workouts counts, full JSON payload
  - Success/error status, import statistics
- **Individual Metrics**: `health_metrics` table
  - Each data point stored separately for querying
  - Metric type, source, date, value, unit
- **Sync Logging**: `health_sync_log` table
  - Track all sync operations and errors

### API Endpoints (New)
```javascript
// Auto Export webhook (receives data from iOS app)
POST /api/apple-health/auto-export
  → { data: { metrics: [...], workouts: [...] } }
  ← { success: true, importId, metricsStored, workoutsStored }

// Get import statistics
GET /api/apple-health/auto-export/stats
  ← { total_imports, total_metrics, successful_imports, last_import }

// Get recent imports
GET /api/apple-health/auto-export/recent?days=7
  ← [ { import_timestamp, metrics_count, workouts_count, status } ]
```

### Setup Requirements
1. Install Health Auto Export app from App Store
2. Purchase Premium (or use 7-day free trial)
3. Create REST API automation pointing to Mac's local IP
4. Configure 30-minute sync cadence
5. Select desired health metrics and workouts
6. Enable background sync
7. Health service must be running on port 3001

**Detailed setup guide**: See `APPLE_HEALTH_AUTO_EXPORT_SETUP.md`

### Benefits Over Previous Implementation
- ✅ **Automated**: No manual shortcuts trigger required
- ✅ **Reliable**: Professional-grade app vs. unreliable Shortcuts
- ✅ **Fresh Data**: 30-minute sync vs. manual updates
- ✅ **Comprehensive**: 150+ metrics vs. limited manual export
- ✅ **Background Sync**: Automatic when unlocked
- ✅ **No Maintenance**: Set-and-forget operation

## Parkrun Integration

### Data Sources & Metrics
- **Official Data**: Parkrun.org results via parkrun.js v1.3.1 library
- **Performance Metrics**: Times, positions, age grades, personal bests
- **Consistency Tracking**: Weekly participation patterns, venue analysis
- **Trend Analysis**: Performance progression over time, seasonal patterns

### Key Statistics (2025)
- **Total Parkruns**: 273+ lifetime results
- **2025 Activity**: 31 confirmed runs completed
- **Performance Range**: Track times, age grade improvements
- **Venue Analysis**: Multi-location performance comparison
- **Consistency**: Weekly Saturday participation tracking

### Data Processing Pipeline
1. **API Integration**: Real-time parkrun.org data via parkrun.js
2. **Local Caching**: SQLite database for performance and offline access
3. **Performance Analysis**: Trend calculation, personal best tracking
4. **Venue Intelligence**: Location-based performance analysis
5. **Consistency Monitoring**: Participation pattern recognition

## Technical Implementation

### Node.js Health Service
- **Framework**: Express.js server with RESTful API endpoints
- **Library**: parkrun.js v1.3.1 for official parkrun.org integration
- **Database**: SQLite for local data caching and performance
- **Endpoints**: `/parkrun/*` for various data queries and analytics

### Service Endpoints
```javascript
// Parkrun endpoints
GET /api/parkrun/profile         // Parkrun profile information
GET /api/parkrun/results         // All parkrun results (limit, offset)
GET /api/parkrun/results/:year   // Year-specific results (e.g., /api/parkrun/results/2025)
GET /api/parkrun/stats           // Performance statistics
POST /api/parkrun/sync           // Trigger parkrun data sync

// Apple Health metrics endpoints (Oct 11, 2025: Fixed to use direct database queries)
GET /api/apple-health/metrics/:type?days=30&limit=100
  // Supported types: steps, heart-rate, active-energy, walking-distance,
  //   body-weight, exercise-minutes, flights-climbed, resting-heart-rate, hrv, sleep

// Apple Health summary endpoints
GET /api/apple-health/summary?days=7     // Comprehensive health summary
GET /api/apple-health/daily/:date        // Daily health data (YYYY-MM-DD)

// Apple Health Auto Export endpoints
POST /api/apple-health/auto-export       // Webhook for Health Auto Export app
GET /api/apple-health/auto-export/stats  // Import statistics
GET /api/apple-health/auto-export/recent?days=7  // Recent imports

// General health endpoints
GET /api/health/summary?period=30        // Multi-source health summary
GET /health                              // Service health check
```

**API Fix (October 11, 2025)**: Health metrics endpoints now use direct SQLite queries via HealthDatabase class instead of Python subprocess calls. See `health-api-fix-summary.md` for details.

### Python Client Wrapper (Optional)
The `python-client/` directory contains an optional Python wrapper (`health_data_client.py`) that provides a clean Python interface to the REST API.

**Status**: Optional - Health service can be accessed directly via curl/bash commands or HTTP requests.

```python
# Optional: Python client for agent integration
from health_data_client import HealthDataClient

client = HealthDataClient(base_url='http://localhost:3001')
results = client.get_parkrun_results(limit=5)
stats = client.get_parkrun_statistics()
summary = client.get_health_summary(days=7)
```

**Note**: Health-agent typically uses direct curl commands to the REST API rather than the Python client.

## Health Service Architecture

### Performance Characteristics
- **Data Freshness**: Real-time API access with intelligent caching
- **Response Time**: Sub-second queries via SQLite caching
- **Reliability**: Offline capability with cached data
- **Scalability**: Designed for multi-platform expansion

### Data Storage Strategy
- **SQLite Database**: Local storage for performance and offline access
- **API Caching**: Intelligent refresh based on data freshness needs
- **Backup Strategy**: Regular database exports for data preservation
- **Privacy**: All health data stored locally, no external data sharing

## Quantified Self Integration

### Current Tracking Capabilities
- **Parkrun Performance**: Comprehensive running analytics
- **Consistency Metrics**: Weekly participation tracking
- **Progress Monitoring**: Personal best progression and goal tracking
- **Venue Optimization**: Performance analysis across different locations

### Health Goals Integration
- **Weight Management**: Target 175→170 lbs (tracked separately)
- **Fitness Consistency**: Maintain weekly parkrun participation
- **Performance Improvement**: Age grade and time improvement tracking
- **Lifestyle Integration**: Saturday morning routine optimization

### Analytics Features
```json
{
  "lifetime_stats": {
    "total_parkruns": 273,
    "pb_time": "22:34",
    "best_age_grade": "65.2%",
    "favorite_venue": "Bushy Park"
  },
  "2025_performance": {
    "runs_completed": 31,
    "average_time": "24:15",
    "consistency_rate": "96%",
    "improvement_trend": "+2.3% age grade"
  }
}
```

## Agent Integration

### Health Agent Integration
- **Primary Agent**: Health Agent (`health-agent`)
- **Query Types**: Performance trends, participation analysis, goal tracking
- **Context Awareness**: Weight goals, fitness objectives, schedule integration
- **Output Format**: Structured data for quantified self analysis

### Common Usage Patterns
- **"How's my parkrun performance trending?"** → Performance analysis with trends
- **"What's my parkrun PB progression?"** → Personal best tracking over time
- **"Which parkrun venues do I perform best at?"** → Venue-based analytics
- **"Show my parkrun statistics for this year"** → 2025 comprehensive report
- **"How consistent is my running schedule?"** → Participation pattern analysis

### Integration with Life Systems
- **Schedule Coordination**: Saturday morning parkrun integration
- **Location Analysis**: Venue selection based on travel patterns
- **Goal Tracking**: Fitness objectives within broader life goals
- **Progress Reporting**: Quantified self dashboard integration

## Future Platform Expansion

### Planned Integrations
1. **Apple Health**: iPhone health data integration
2. **Fitbit**: Comprehensive activity and sleep tracking
3. **Strava**: Social fitness platform and route analysis
4. **Garmin Connect**: Advanced fitness device integration
5. **MyFitnessPal**: Nutrition and diet tracking
6. **Withings Scale**: Weight and body composition data

### Expansion Architecture
- **Modular Design**: Each platform as separate microservice module
- **Unified API**: Single Python client interface for all platforms
- **Data Aggregation**: Cross-platform analytics and insights
- **Privacy First**: Local data processing and storage priority

## Development Environment

### Service Setup
```bash
cd health-integration/health-service
npm install
npm start  # Starts Express server on localhost:3001
```

**Database Location**: `health-service/data/health.db` (1.7GB, 5.3M records)

### Python Client Setup
```bash
cd health-integration/python-client
pip install -r requirements.txt
```

### Dependencies
- **Node.js**: Express.js, parkrun.js v1.3.1, sqlite3
- **Python**: requests, json, datetime
- **Database**: SQLite for local data caching

## Data Privacy & Security

### Privacy Principles
- **Local Storage**: All health data stored locally on device
- **No External Sharing**: Health data never transmitted to external services
- **User Control**: Complete ownership and control over personal health data
- **Selective Sharing**: Only aggregated, anonymized insights shared if requested

### Security Measures
- **Database Encryption**: SQLite database with appropriate security
- **API Security**: Local-only health service access
- **Access Control**: Agent-based access with proper authentication
- **Data Retention**: Configurable data retention policies

## Performance Optimization

### Caching Strategy
- **Intelligent Refresh**: Update frequency based on data type and freshness needs
- **Offline Capability**: Full functionality with cached data
- **Performance Monitoring**: Query response time optimization
- **Memory Management**: Efficient data structure usage

### Analytics Performance
- **Pre-calculated Metrics**: Common analytics pre-computed for speed
- **Trend Analysis**: Efficient time-series calculation algorithms
- **Data Indexing**: Optimized database queries for fast retrieval
- **Response Caching**: Frequently requested data cached in memory

## Troubleshooting & Maintenance

### Common Issues
- **Service Connectivity**: Health service startup and connectivity verification
- **Data Freshness**: Parkrun API data update frequency
- **Performance Queries**: Complex analytics query optimization
- **Database Maintenance**: SQLite database cleanup and optimization

### Monitoring & Diagnostics
- **Health Checks**: Service availability and responsiveness monitoring
- **Data Quality**: Parkrun data consistency and completeness validation
- **Performance Metrics**: Query response time and system resource usage
- **Error Logging**: Comprehensive error tracking and resolution

This health integration system provides Gavin with comprehensive fitness tracking and analytics, specifically optimized for his quantified self approach and integrated with his broader Personal AI Infrastructure for holistic life management.

---

## System Status

**Last Updated**: October 13, 2025

**Recent Changes**:
- ✅ Fixed active energy unit conversion bug (kJ → kcal) in summary endpoint (Oct 13)
- ✅ Added sleep data support to metrics API (Oct 13) - was missing after Oct 11 refactoring
- ✅ Expanded supported metric types from 9 to 10 (added sleep)
- ✅ Fixed health metrics API to use direct database queries (Oct 11)
- ✅ Cleaned up directory (removed 5 obsolete files, ~20MB)
- ✅ Updated all documentation with current architecture

**Production Status**: ✅ Fully operational
- **Health Service**: Running on localhost:3001
- **Database**: health.db (1.7GB, 5.3M health records from 2010-2025)
- **Apple Health Sync**: Automated 30-minute sync via Health Auto Export app
- **Parkrun Integration**: 277 total parkruns, 31 completed in 2025
- **API Endpoints**: All tested and working

**Documentation**:
- `CLAUDE.md` - Technical documentation (this file)
- `README.md` - User documentation
- `apple-health-auto-export-setup.md` - Setup guide
- `device-priority-guidelines.md` - Query patterns
- `file-audit.md` - Directory cleanup audit
- `health-service/health-api-fix-summary.md` - Oct 11 API fix details