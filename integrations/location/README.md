# Location Integration System

Personal location intelligence using Owntracks geolocation data for Gavin's Life Management System.

## Overview

The Location Agent provides intelligent analysis of Gavin's movement patterns, travel history, and location-based insights using data from his private Owntracks instance at `https://owntracks.gavinslater.co.uk/`.

## Components

### Core Files

- **`location_agent.py`** - Main coordinator that orchestrates all location intelligence
- **`owntracks_client.py`** - API client for communicating with Owntracks Recorder
- **`location_analyzer.py`** - Analysis engine for processing location data into insights
- **`location_cache.py`** - Local caching system for performance and offline capability

### Configuration

- **`requirements.txt`** - Python dependencies
- **`test_location_agent.py`** - Comprehensive test suite
- **`venv/`** - Python virtual environment

## Quick Start

### 1. Environment Setup

```bash
cd location-integration
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Device Identifiers

Set your Owntracks device identifiers:

```bash
export OWNTRACKS_USER='gavin-iphone'
export OWNTRACKS_DEVICE='a2ea00bc-9862-4efb-a6ab-f038e32beb4c'
```

### 3. Quick Test (No Authentication)

```bash
python quick_test.py
```

### 4. Add Authentication (Optional)

If your Owntracks requires HTTP Basic auth, also set:

```bash
export OWNTRACKS_AUTH_USERNAME='your_http_auth_username'
export OWNTRACKS_AUTH_PASSWORD='your_http_auth_password'
```

See `CONFIGURATION.md` for detailed setup instructions.

### 4. Basic Usage

```python
from location_agent import create_location_agent

# Create agent
agent = create_location_agent()

# Test connection
connection = agent.test_connection()
print(f"Connection: {connection}")

# Get current location
current = agent.get_current_location()
print(f"Current location: {current}")

# Where was I yesterday?
result = agent.where_was_i('2025-01-19')
print(f"Yesterday's locations: {result}")

# Analyze time at office
office_time = agent.analyze_time_at_location('office', from_date='2025-01-13', to_date='2025-01-19')
print(f"Office time this week: {office_time}")
```

## Features

### Location History Queries
- "Where was I on [date]?"
- "What was my location at [time] on [date]?"
- Find location at specific date/time

### Time-at-Location Analysis
- Calculate time spent at specific locations
- Analyze office vs home time
- Track regular locations (home, office, station)

### Travel Pattern Analysis
- Detect commute patterns
- Identify frequent locations
- Analyze daily movement patterns

### Intelligent Caching
- Local cache for improved performance
- Automatic cache management
- Offline capability with cached data

## Sub-Agent Integration

The Location Agent integrates with Gavin's Personal Consultant system:

### Activation Triggers
- "Where was I on [date]?"
- "How long did I spend at [location]?"
- "What's my commute pattern?"
- "Where do I spend most of my time?"
- "Analyze my travel patterns"
- "Time spent at office vs home"

### Sample Interactions

```
User: "Where was I yesterday afternoon around 3pm?"

Location Agent: "At 3:00pm yesterday, you were at ICBC Standard Bank offices in London.
- Duration at location: 2:15pm - 6:25pm (4 hours 10 minutes)
- Context: Tuesday office day (part of your 3-day office schedule)"
```

```
User: "How often do I actually make it to the office?"

Location Agent: "Office attendance analysis for the past 4 weeks:
- Office Presence: 9 out of 12 scheduled office days (75%)
- Average office time per day: 8 hours 45 minutes
- Insight: Slightly below planned 3-day schedule due to occasional WFH flexibility"
```

## Known Locations

The system automatically recognizes these important locations:

- **Home**: Esher, Surrey (auto-detected from data)
- **Office**: ICBC Standard Bank, London
- **Esher Station**: Railway station for commute

Additional locations can be added by coordinates or will be auto-detected from usage patterns.

## Privacy & Security

- **Local Processing**: All analysis happens locally
- **No External Sharing**: Location data never shared with external services
- **Secure API**: HTTPS connection to private Owntracks instance
- **Configurable Retention**: User-controlled cache retention

## API Reference

### LocationAgent Class

#### Core Methods

- `test_connection()` - Test Owntracks connection and detect devices
- `where_was_i(date, time=None)` - Location history query
- `analyze_time_at_location(location, from_date, to_date)` - Time analysis
- `analyze_commute_pattern(days=30)` - Commute pattern analysis
- `get_frequent_locations(days=30)` - Identify frequent locations
- `get_current_location()` - Current/last known location

#### Cache Management

- `get_cache_status()` - Cache status and statistics
- `clear_cache(older_than_hours=None)` - Clear cached data

### Sample Output Formats

```python
# Where was I query
{
    'success': True,
    'query': 'Where was I on 2025-01-19?',
    'answer': {
        'date': '2025-01-19',
        'location_count': 45,
        'first_location': {'time': '07:15', 'coordinates': (51.3712, -0.3648)},
        'last_location': {'time': '19:30', 'coordinates': (51.3712, -0.3648)},
        'time_at_known_locations': {
            'office': {'total_hours': 8.5, 'visit_count': 1},
            'home': {'total_hours': 12.3, 'visit_count': 2}
        }
    }
}
```

## Error Handling

The system gracefully handles:
- **API Unavailability**: Uses cached data when Owntracks is unreachable
- **Network Issues**: Automatic retry with exponential backoff
- **Invalid Dates**: Clear error messages for invalid input
- **Missing Data**: Informative responses when no data available

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check `OWNTRACKS_USERNAME` and `OWNTRACKS_PASSWORD` environment variables
   - Verify Owntracks instance is accessible at `https://owntracks.gavinslater.co.uk/`
   - Test connection manually: `curl https://owntracks.gavinslater.co.uk/api/0/monitor`

2. **No Device Detected**
   - Ensure device is publishing to Owntracks
   - Check device name in Owntracks interface
   - Manually specify device name if needed

3. **No Location Data**
   - Verify date range has recorded data
   - Check Owntracks Recorder is storing data properly
   - Ensure sufficient location history exists

### Testing

Run the comprehensive test suite:

```bash
python test_location_agent.py
```

This tests all components and provides detailed diagnostics.

## Integration with Personal Consultant

The Location Agent is automatically available through the Personal Consultant system. When users ask location-related questions, the Personal Consultant will:

1. Recognize location intent
2. Delegate to Location Agent
3. Process results
4. Provide strategic context

No direct interaction with Location Agent required - it works seamlessly through natural language queries to the Personal Consultant.

## Future Enhancements

Planned improvements:
- **Geofencing**: Automatic detection of common locations
- **Calendar Integration**: Cross-reference with meeting locations
- **Predictive Analytics**: Suggest optimal meeting locations
- **Family Coordination**: Track family member pickups and activities
- **Health Correlation**: Link location patterns with fitness data