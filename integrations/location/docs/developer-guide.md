# Location Analysis System - Developer Guide

**Version:** 2.0
**Last Updated:** November 2, 2025

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Adding a New Activity Analyzer](#adding-a-new-activity-analyzer)
3. [Testing](#testing)
4. [Configuration System](#configuration-system)
5. [Integration Points](#integration-points)
6. [Best Practices](#best-practices)

---

## Architecture Overview

### System Structure

```
integrations/location/
├── core/                          # Framework modules
│   ├── location_analyzer.py      # Location database management
│   ├── owntracks_client.py       # API client
│   └── location_cache.py         # Caching system
│
├── analyzers/                     # Activity detection
│   ├── base_activity_analyzer.py # Abstract base class
│   ├── golf_analyzer.py          # Golf detection
│   ├── parkrun_analyzer.py       # Parkrun detection
│   ├── commute_analyzer.py       # Commute detection
│   ├── dog_walking_analyzer.py   # Dog walking detection
│   ├── snowboarding_analyzer.py  # Snowboarding detection
│   └── trip_analyzer.py          # Multi-day coordination
│
├── config/                        # Configuration files
│   └── analysis_config.json      # All analyzer settings
│
├── locations/                     # Location databases
│   ├── base_locations.json       # UK base locations
│   └── trips/                    # Trip-specific locations
│
├── scripts/                       # User-facing tools
│   └── analyze_date.py           # Daily analysis script
│
└── docs/                          # Documentation
    ├── README.md                 # Overview
    ├── user-guide.md             # Usage guide
    └── developer-guide.md        # This file
```

### Core Components

#### 1. BaseActivityAnalyzer

**Purpose:** Abstract base class for all activity analyzers

**Key Features:**
- Configuration loading (`analysis_config.json`)
- Location database access via `LocationAnalyzer`
- Timestamp parsing utilities
- Confidence score calculation
- Standard velocity classification
- Session clustering with gap tolerance

**Location:** `analyzers/base_activity_analyzer.py`

#### 2. ActivitySession

**Purpose:** Standardized output format for all analyzers

**Structure:**
```python
@dataclass
class ActivitySession:
    activity_type: str              # 'golf', 'parkrun', etc.
    start_time: datetime
    end_time: datetime
    duration_hours: float
    location_name: str
    location_coords: Tuple[float, float]
    confidence: str                 # 'HIGH', 'MEDIUM', 'LOW', 'CONFIRMED'
    confidence_score: float         # 0.0-1.0
    details: Dict                   # Activity-specific metadata
```

#### 3. LocationAnalyzer

**Purpose:** Manage location databases and analysis utilities

**Key Features:**
- Load base locations from JSON
- Load trip-specific locations
- Time-at-location analysis
- Location proximity matching
- Geocoding services

**Location:** `core/location_analyzer.py`

---

## Adding a New Activity Analyzer

### Step-by-Step Guide

#### Step 1: Create Analyzer Class

Create new file: `analyzers/your_activity_analyzer.py`

```python
"""
Your Activity Analyzer
Specialized analyzer for detecting [activity] from location data.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
from geopy.distance import geodesic

from .base_activity_analyzer import BaseActivityAnalyzer, ActivitySession


@dataclass
class YourActivitySegment:
    """Represents a segment of your activity"""
    start_time: datetime
    end_time: datetime
    # Add activity-specific fields


class YourActivityAnalyzer(BaseActivityAnalyzer):
    """Analyzes location data to detect [your activity]"""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize analyzer"""
        super().__init__(config_path)
        self.logger = logging.getLogger(__name__)

        # Load configuration values
        self.some_threshold = self.get_config_value('some_threshold', 100)
        self.min_duration = self.get_config_value('min_duration_minutes', 10)
        # ... other config values

    def _get_activity_type(self) -> str:
        """Return the activity type string"""
        return 'your_activity'

    def detect_sessions(self, locations: List[Dict],
                       **kwargs) -> List[ActivitySession]:
        """
        Detect your activity sessions from location data

        Args:
            locations: List of location records from Owntracks
            **kwargs: Activity-specific parameters

        Returns:
            List of detected activity sessions
        """
        if not locations or not self.enabled:
            return []

        sessions = []

        # 1. Extract relevant segments from location data
        segments = self._extract_segments(locations)

        # 2. Cluster segments into sessions
        session_clusters = self._cluster_segments(segments)

        # 3. Analyze each session
        for cluster in session_clusters:
            session = self._analyze_session(cluster, kwargs)
            if session:
                sessions.append(session)

        return sessions

    def _extract_segments(self, locations: List[Dict]) -> List[YourActivitySegment]:
        """Extract activity-specific segments"""
        segments = []

        for i in range(len(locations) - 1):
            loc1 = locations[i]
            loc2 = locations[i + 1]

            # Parse timestamps using base class method
            time1 = self.parse_timestamp(loc1.get('tst'))
            time2 = self.parse_timestamp(loc2.get('tst'))

            if not time1 or not time2:
                continue

            # Extract coordinates
            coords1 = (loc1.get('lat'), loc1.get('lon'))
            coords2 = (loc2.get('lat'), loc2.get('lon'))

            if None in coords1 or None in coords2:
                continue

            # Calculate metrics
            distance = geodesic(coords1, coords2).meters
            duration = (time2 - time1).total_seconds()
            velocity = distance / duration if duration > 0 else 0

            # Create segment if matches activity criteria
            if self._is_activity_segment(velocity, duration):
                segment = YourActivitySegment(
                    start_time=time1,
                    end_time=time2,
                    # ... other fields
                )
                segments.append(segment)

        return segments

    def _is_activity_segment(self, velocity: float, duration: float) -> bool:
        """Check if segment matches activity criteria"""
        # Implement your activity-specific logic
        return True

    def _cluster_segments(self, segments: List[YourActivitySegment]) -> List[List[YourActivitySegment]]:
        """Cluster segments into sessions using gap tolerance"""
        if not segments:
            return []

        # Use base class gap tolerance
        gap_tolerance = self.get_gap_tolerance()
        gap_seconds = gap_tolerance * 60

        clusters = []
        current_cluster = [segments[0]]

        for segment in segments[1:]:
            prev_segment = current_cluster[-1]
            gap = (segment.start_time - prev_segment.end_time).total_seconds()

            if gap <= gap_seconds:
                current_cluster.append(segment)
            else:
                clusters.append(current_cluster)
                current_cluster = [segment]

        if current_cluster:
            clusters.append(current_cluster)

        return clusters

    def _analyze_session(self, cluster: List[YourActivitySegment],
                        kwargs: Dict) -> Optional[ActivitySession]:
        """Analyze a session cluster and create ActivitySession"""
        if not cluster:
            return None

        # Calculate session metrics
        start_time = cluster[0].start_time
        end_time = cluster[-1].end_time
        duration_hours = (end_time - start_time).total_seconds() / 3600

        # Check minimum duration
        if duration_hours < (self.min_duration / 60):
            return None

        # Calculate location
        avg_lat = sum(s.start_lat for s in cluster) / len(cluster)
        avg_lon = sum(s.start_lon for s in cluster) / len(cluster)
        location_coords = (avg_lat, avg_lon)

        # Determine location name
        location_name = self._get_location_name(location_coords, kwargs)

        # Calculate confidence
        confidence_score, score_details = self._calculate_confidence(
            cluster, location_name, kwargs
        )
        confidence_label = self.get_confidence_label(confidence_score)

        # Create session
        return ActivitySession(
            activity_type='your_activity',
            start_time=start_time,
            end_time=end_time,
            duration_hours=duration_hours,
            location_name=location_name,
            location_coords=location_coords,
            confidence=confidence_label,
            confidence_score=confidence_score,
            details={
                'num_segments': len(cluster),
                'confidence_breakdown': score_details,
                # ... other activity-specific details
            }
        )

    def _calculate_confidence(self, cluster: List[YourActivitySegment],
                             location_name: str,
                             kwargs: Dict) -> Tuple[float, Dict]:
        """Calculate multi-factor confidence score"""
        weights = self.get_config_value('confidence_weights', {
            'factor1': 40,
            'factor2': 30,
            'factor3': 20,
            'factor4': 10
        })

        scores = {}
        total_score = 0.0

        # Factor 1: Some criteria (40%)
        factor1_score = 1.0 if some_condition else 0.5
        scores['factor1'] = factor1_score
        total_score += factor1_score * (weights['factor1'] / 100)

        # Factor 2: Another criteria (30%)
        # ... implement scoring logic

        return total_score, scores


def create_your_activity_analyzer(config_path: Optional[str] = None):
    """Factory function"""
    return YourActivityAnalyzer(config_path)
```

#### Step 2: Add Configuration

Edit `config/analysis_config.json`:

```json
{
  "activity_analyzers": {
    "your_activity": {
      "enabled": true,
      "some_threshold": 100,
      "min_duration_minutes": 10,
      "max_duration_minutes": 120,
      "gap_tolerance_minutes": 10,
      "confidence_weights": {
        "factor1": 40,
        "factor2": 30,
        "factor3": 20,
        "factor4": 10
      }
    }
  }
}
```

#### Step 3: Integrate into TripAnalyzer

Edit `analyzers/trip_analyzer.py`:

```python
# Add import
from analyzers.your_activity_analyzer import YourActivityAnalyzer

# Add to __init__
self.your_activity_analyzer = YourActivityAnalyzer()

# Add detection method
def detect_your_activity(self, locations: List[Dict], date: str) -> List[ActivitySession]:
    """Detect your activity"""
    known_locations = self.location_analyzer.get_all_locations()

    sessions = self.your_activity_analyzer.detect_sessions(
        locations,
        known_locations=known_locations
    )

    for session in sessions:
        session.details['date'] = date

    return sessions

# Add to analyze_day() method
your_activities = self.detect_your_activity(locations, date)
activities.extend(your_activities)
```

#### Step 4: Add to Daily Analysis Script

Edit `scripts/analyze_date.py`:

```python
# Add import
from analyzers.your_activity_analyzer import YourActivityAnalyzer

# Add to analyze_date() function
your_activity_analyzer = YourActivityAnalyzer()

# Add analysis section
print("\n🎯 Analyzing [your activity] activities...")
your_sessions = your_activity_analyzer.detect_sessions(locations, known_locations)
if your_sessions:
    print(f"   ✓ Found {len(your_sessions)} [your activity](s)")
    all_activities.extend(your_sessions)
else:
    print("   - No [your activity] activities detected")

# Add display logic in summary
elif activity.activity_type == 'your_activity' and 'some_detail' in activity.details:
    print(f"   Detail: {activity.details['some_detail']}")
```

#### Step 5: Test

Create test script:

```python
import sys
sys.path.insert(0, '/path/to/integrations/location')

from analyzers.your_activity_analyzer import YourActivityAnalyzer

analyzer = YourActivityAnalyzer()
print(f"✓ {analyzer.activity_type} analyzer created")
print(f"✓ Enabled: {analyzer.enabled}")
print(f"✓ Configuration loaded")

# Test with sample data
test_locations = [...]  # Sample location data
sessions = analyzer.detect_sessions(test_locations)
print(f"✓ Detected {len(sessions)} sessions")
```

---

## Testing

### Unit Tests

Create `tests/test_your_activity_analyzer.py`:

```python
import unittest
from datetime import datetime
from analyzers.your_activity_analyzer import YourActivityAnalyzer


class TestYourActivityAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = YourActivityAnalyzer()

    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly"""
        self.assertEqual(self.analyzer.activity_type, 'your_activity')
        self.assertTrue(self.analyzer.enabled)

    def test_segment_extraction(self):
        """Test segment extraction logic"""
        locations = self._create_test_locations()
        segments = self.analyzer._extract_segments(locations)
        self.assertGreater(len(segments), 0)

    def test_confidence_calculation(self):
        """Test confidence scoring"""
        # ... test logic

    def _create_test_locations(self):
        """Helper to create test location data"""
        return [
            {
                'lat': 51.4, 'lon': -0.3,
                'tst': 1730000000,
                'alt': 50
            },
            # ... more test data
        ]


if __name__ == '__main__':
    unittest.main()
```

### Integration Tests

Test with TripAnalyzer:

```python
from analyzers.trip_analyzer import TripAnalyzer

analyzer = TripAnalyzer(trip_name='test_trip')
daily_summary = analyzer.analyze_day('2025-11-02')

# Check if your activity was detected
your_activities = [a for a in daily_summary.activities
                   if a.activity_type == 'your_activity']

assert len(your_activities) > 0, "Your activity should be detected"
```

---

## Configuration System

### Configuration Structure

**File:** `config/analysis_config.json`

```json
{
  "velocity_classification": {
    "stationary": {"min_mps": 0, "max_mps": 0.5},
    "walking": {"min_mps": 0.5, "max_mps": 2.5},
    "running": {"min_mps": 2.5, "max_mps": 5.0}
  },

  "session_clustering": {
    "default_gap_tolerance_minutes": 15,
    "activity_specific_gaps": {
      "golf": 20,
      "parkrun": 5
    }
  },

  "location_matching": {
    "default_radius_meters": 100,
    "category_specific_radius": {
      "golf_course": 500,
      "ski_resort": 2000
    }
  },

  "confidence_thresholds": {
    "high": 0.8,
    "medium": 0.6,
    "low": 0.4
  },

  "activity_analyzers": {
    "your_activity": {
      "enabled": true,
      "...": "..."
    }
  }
}
```

### Accessing Configuration

```python
# In your analyzer __init__
self.some_value = self.get_config_value('some_key', default_value)

# Get velocity classification
velocity_type = self.get_velocity_classification(velocity_mps)

# Get location radius
radius = self.get_location_radius('golf_course')

# Get gap tolerance
gap = self.get_gap_tolerance()  # Activity-specific or default

# Get confidence label
label = self.get_confidence_label(0.85)  # Returns 'HIGH'
```

---

## Integration Points

### 1. TripAnalyzer Integration

**Purpose:** Multi-day trip analysis

**Integration Points:**
- `__init__`: Initialize your analyzer
- `detect_your_activity()`: Detection method
- `analyze_day()`: Call your detection method

### 2. Daily Analysis Script

**Purpose:** Single-day analysis

**Integration Points:**
- Import your analyzer
- Initialize in `analyze_date()` function
- Add analysis section with emoji/output
- Add detail display in summary

### 3. Location Agent

**Purpose:** Claude agent integration

**Future Integration:**
- Add to LocationAgent class
- Expose via agent API
- Include in automated reports

---

## Best Practices

### 1. Naming Conventions

- **Analyzer Class:** `YourActivityAnalyzer`
- **Activity Type:** `'your_activity'` (lowercase, underscore-separated)
- **Config Section:** `"your_activity"` (matches activity type)
- **Factory Function:** `create_your_activity_analyzer()`

### 2. Configuration Design

- Use **sensible defaults** in code
- Make all thresholds **configurable**
- Include **confidence weights** for multi-factor scoring
- Document configuration options

### 3. Confidence Scoring

- Use **5 factors** for comprehensive assessment
- **Weight factors** by importance (total = 100%)
- Return **score breakdown** for debugging
- Map scores to labels: HIGH (≥0.8), MEDIUM (≥0.6), LOW (<0.6)

### 4. Error Handling

```python
# Handle missing data gracefully
if not locations or not self.enabled:
    return []

# Validate coordinates
if None in coords:
    continue

# Handle zero-duration segments
velocity = distance / duration if duration > 0 else 0
```

### 5. Documentation

- **Docstrings** for all public methods
- **Type hints** for parameters and returns
- **Example usage** in module docstring
- **Configuration schema** documented

### 6. Testing

- **Unit tests** for segment extraction
- **Integration tests** with TripAnalyzer
- **Sample data** in test fixtures
- **Edge cases** covered

---

## Common Patterns

### Pattern 1: Velocity-Based Detection

```python
def _is_activity_velocity(self, velocity_mps: float) -> bool:
    """Check if velocity matches activity"""
    return self.min_velocity <= velocity_mps <= self.max_velocity
```

### Pattern 2: Time Window Validation

```python
def _is_in_time_window(self, timestamp: datetime) -> bool:
    """Check if in expected time window"""
    time = timestamp.time()
    return self.start_time <= time <= self.end_time
```

### Pattern 3: Location Proximity

```python
def _find_nearby_location(self, coords: Tuple[float, float],
                         known_locations: Dict) -> Optional[str]:
    """Find nearest known location"""
    for loc_id, loc_info in known_locations.items():
        distance = geodesic(coords, loc_info['coordinates']).meters
        if distance <= loc_info['radius']:
            return loc_info['name']
    return None
```

### Pattern 4: Multi-Factor Confidence

```python
def _calculate_confidence(self, **factors) -> Tuple[float, Dict]:
    """Calculate weighted confidence score"""
    weights = self.get_config_value('confidence_weights', {...})
    scores = {}
    total = 0.0

    for factor_name, weight_pct in weights.items():
        factor_score = self._score_factor(factor_name, factors)
        scores[factor_name] = factor_score
        total += factor_score * (weight_pct / 100)

    return total, scores
```

---

## Performance Considerations

### 1. Caching

```python
# Cache expensive calculations
if not hasattr(self, '_cached_value'):
    self._cached_value = expensive_calculation()
return self._cached_value
```

### 2. Early Exit

```python
# Exit early if conditions not met
if len(locations) < 10:  # Need minimum data points
    return []

if not self.enabled:
    return []
```

### 3. Batch Processing

```python
# Process locations in batches
batch_size = 1000
for i in range(0, len(locations), batch_size):
    batch = locations[i:i+batch_size]
    process_batch(batch)
```

---

## Debugging Tips

### 1. Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. Print Intermediate Results

```python
self.logger.debug(f"Extracted {len(segments)} segments")
self.logger.debug(f"Confidence breakdown: {score_details}")
```

### 3. Validate Configuration

```python
print(f"Config loaded: {self.activity_config}")
print(f"Enabled: {self.enabled}")
print(f"Thresholds: min={self.min_value}, max={self.max_value}")
```

### 4. Test with Sample Data

Create small, known datasets to validate detection logic.

---

## Additional Resources

- **Base Class Reference:** `analyzers/base_activity_analyzer.py`
- **Example Analyzers:** `analyzers/golf_analyzer.py`, `analyzers/parkrun_analyzer.py`
- **Configuration Schema:** `config/analysis_config.json`
- **Complete Spec:** `docs/archive/research/analysis-improvements.md`

---

**Questions?** Check the user-guide.md for usage help or README.md for system overview.
