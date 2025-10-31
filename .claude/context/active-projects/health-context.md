# Health & Fitness Context

## Current Status (October 2025)
- **Weight**: ~175 lbs (target: under 170 lbs via Withings scale tracking)
- **Primary Activity**: Weekly parkrun participation (273+ lifetime runs, 31 in 2025)
- **Integration**: Fully automated Apple Health Auto Export (30-min sync, 5.3M records)
- **Database**: Complete health history 2010-2025 with device-priority deduplication

## Health Integration System

### Apple Health Auto Export (Production)
- **Status**: ✅ Fully operational (Oct 2025)
- **Sync**: Automated 30-minute background sync via iOS app webhook
- **Metrics**: 19+ types including steps, heart rate, weight, sleep, workouts
- **Data Volume**: 5,300,724 unique health measurements
- **Device Priority**: Apple Watch > Withings > iPhone (prevents double-counting)

### Parkrun Integration
- **API**: Official parkrun.org via parkrun.js v1.3.1
- **Results**: 273+ lifetime runs with complete performance history
- **2025 Activity**: 31 confirmed runs with trends and venue analysis
- **Analytics**: Times, positions, age grades, personal bests, consistency patterns

### Data Infrastructure
- **Service**: Node.js microservice on localhost:3001
- **Database**: SQLite (health.db) with 5.3M records, 2010-2025 date range
- **Client**: Python wrapper for health agent integration
- **Privacy**: All data local, family members filtered (319 Raquel records excluded)

## Key Metrics Tracked

### Activity & Movement
- Step count (2.7M+ records from Apple Watch)
- Walking/running distance, flights climbed
- Active energy burned, exercise minutes
- Walking speed, running speed, step length

### Heart Health
- Continuous heart rate (1.8M+ measurements)
- Resting heart rate, heart rate variability (HRV)
- Walking heart rate average, cardio recovery
- VO2 Max tracking

### Body Measurements
- Weight (6,896 Withings readings)
- Body mass index, body fat percentage

### Sleep & Recovery
- Sleep analysis (Sleep Cycle integration)
- Stand time, stand hour tracking

### Workouts
- 70+ workout types (running, cycling, strength, swimming, etc.)
- Duration, distance, energy, heart rate zones

## Health Goals

### Weight Management
- **Current**: ~175 lbs
- **Target**: Under 170 lbs
- **Tracking**: Daily Withings scale measurements
- **Strategy**: Data-driven optimization, weeknight alcohol elimination

### Activity Consistency
- **Target**: 10,000+ steps daily average
- **Parkrun**: Weekly Saturday morning participation
- **Monitoring**: Apple Watch step tracking with priority filtering

### Heart Health
- Monitor resting HR trends and improvements
- Track HRV for recovery assessment
- Correlate with activity levels and sleep quality

### Sleep Quality
- Maintain consistent sleep duration
- Track sleep patterns via Sleep Cycle
- Weeknight alcohol elimination based on data analysis

## Quantified Self Approach

### Data-Driven Insights
- **Performance Trends**: Week-over-week, month-over-month comparisons
- **Correlation Analysis**: Health metrics vs. activity patterns
- **Goal Progress**: Visual tracking of targets (steps, weight, exercise)
- **Anomaly Detection**: Identify unusual patterns or concerning trends
- **Parkrun Optimization**: Correlate performance with training metrics

### Device Priority System
**Critical**: Always filter by device source to avoid double-counting
- **Apple Watch**: Primary for steps, heart rate, activity (most accurate)
- **Withings Scale**: Weight and body composition
- **Sleep Cycle**: Sleep analysis
- **iPhone**: Fallback only when Watch not available

### Verification Examples
- Oct 5, 2025: Apple Watch 9,966 steps ✅ (iPhone 8,542 ignored)
- Oct 4, 2025: Apple Watch 19,951 steps ✅ (iPhone 24,239 ignored)

## Agent Integration

### Health Agent Access
- **Agent**: `health-agent` sub-agent
- **Python Client**: `health_data_client.py`
- **API**: REST endpoints on localhost:3001
- **Capabilities**: Trends, insights, recommendations, goal tracking, anomaly detection

### Common Queries
- Daily health briefings with trend analysis
- Parkrun performance analysis and recommendations
- Weight tracking and goal progress monitoring
- Activity pattern recognition
- Health alerts (anomalies, achievements)
- Correlation with life events (travel, work schedule)

### Data Access Patterns
```python
# Example health agent usage
from health_data_client import HealthClient

client = HealthClient()

# Parkrun statistics
parkrun = client.get_parkrun_stats()

# Step count with device priority (Apple Watch only)
steps = client.get_metric_with_priority('step_count', date='2025-10-06')

# Weekly health summary
summary = client.get_health_summary(days=7)
```

## Current Focus

### Immediate Priorities
- **Maintain parkrun consistency**: Weekly Saturday attendance
- **Weight reduction**: Implement data-driven strategy to reach <170 lbs
- **Auto Export monitoring**: Ensure 30-min sync continues reliably

### Ongoing Tracking
- Monitor resting heart rate trends
- Track HRV for recovery optimization
- Analyze sleep quality patterns
- Correlate activity with parkrun performance

### Performance Optimization
- Identify best training patterns for parkrun improvement
- Optimize recovery between runs
- Balance activity levels with sleep quality
- Use age grade data to benchmark performance

## Technical Details

### Service Management
```bash
# Start health service
cd /Users/gavinslater/projects/life/health-integration/health-service
npm start  # Runs on localhost:3001

# Check service status
curl http://localhost:3001/health
```

### Database Management
- **Location**: `health-integration/health-service/data/health.db`
- **Size**: ~450MB for 5.3M records
- **Rebuild**: Use `scripts/rebuild_health_database.py` for fresh import
- **Backup**: Regular copies to health.db.backup

### Auto Export Configuration
- **App**: Health Auto Export - JSON+CSV (iOS App Store)
- **Subscription**: Premium ($2.99/month)
- **Endpoint**: `http://192.168.5.235:3001/api/apple-health/auto-export`
- **Sync**: Every 30 minutes with "Since Last Sync" date range
- **Background**: Enabled (runs when device unlocked)

## Documentation References

- **System README**: `/health-integration/README.md`
- **Setup Guide**: `/health-integration/apple-health-auto-export-setup.md`
- **Query Best Practices**: `/health-integration/device-priority-guidelines.md`
- **Project Context**: `/health-integration/CLAUDE.md`
- **Agent Definition**: `/.claude/agents/health-agent.md`

---

**Integration Status**: ✅ Production-ready with automated sync, comprehensive analytics, and 15 years of historical data

**Last Updated**: October 6, 2025
