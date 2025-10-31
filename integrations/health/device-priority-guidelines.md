# Health Metrics Device Priority Guidelines

**Date**: October 6, 2025

---

## Overview

When querying health metrics from the health.db database, **multiple devices may record the same metric simultaneously**, leading to double-counting. This document provides guidelines for device prioritization to ensure accurate metric reporting.

---

## The Problem

### Example: Step Count Double-Counting

**October 5, 2025 Step Count**:
- ✅ **Apple Watch**: 9,966 steps (accurate - worn all day)
- ⚠️ **iPhone**: 8,542 steps (less accurate - in pocket/bag)
- ❌ **Combined Total**: 18,508 steps (INCORRECT - double count)
- ✅ **Expected**: 9,841 steps (user's actual activity)

**Root Cause**: Both Apple Watch and iPhone record steps independently when worn/carried simultaneously.

---

## Device Priority Hierarchy

### General Rule: **Apple Watch > iPhone > Third-Party Apps**

#### Priority 1: Apple Watch
- **Most Accurate** for activity metrics (steps, heart rate, exercise time)
- Worn directly on body, continuous sensor contact
- Priority device for: Steps, Heart Rate, Active Energy, Exercise Time, Flights Climbed

#### Priority 2: iPhone
- **Accurate** when Apple Watch not worn
- Useful for metrics not available on Watch (body measurements from Withings via Health app)
- Priority device for: Body Weight, BMI, Body Fat Percentage (when synced from Withings)

#### Priority 3: Third-Party Apps
- **Specific Use Cases** (Sleep Cycle for sleep, Withings for weight)
- Use when more specialized than Apple devices
- Priority for: Sleep Analysis (Sleep Cycle), Body Measurements (Withings direct)

---

## Query Patterns

### Pattern 1: Apple Watch First (Activity Metrics)

**Metrics**: Steps, Heart Rate, Active Energy, Exercise Time, Flights Climbed, Distance

```sql
-- Step Count Example
SELECT
    SUM(metric_value) as total_steps,
    COUNT(*) as record_count
FROM health_metrics
WHERE metric_type = 'step_count'
AND metric_date >= '2025-10-05 00:00:00'
AND metric_date < '2025-10-06 00:00:00'
AND additional_data LIKE '%Apple Watch%';  -- Priority device
```

**Results**: 9,966 steps (accurate ✅)

### Pattern 2: Withings First (Body Measurements)

**Metrics**: Weight, BMI, Body Fat Percentage

```sql
-- Body Weight Example
SELECT
    metric_value as weight,
    metric_date,
    metric_unit
FROM health_metrics
WHERE metric_type = 'weight_body_mass'
AND metric_date >= '2025-10-01 00:00:00'
AND additional_data LIKE '%Withings%'  -- Priority device for weight
ORDER BY metric_date DESC
LIMIT 7;
```

### Pattern 3: Sleep Cycle First (Sleep Analysis)

**Metrics**: Sleep Duration, Sleep Quality

```sql
-- Sleep Analysis Example
SELECT
    metric_value as sleep_minutes,
    metric_date,
    additional_data
FROM health_metrics
WHERE metric_type = 'sleep_analysis'
AND metric_date >= '2025-10-05 00:00:00'
AND additional_data LIKE '%Sleep Cycle%'  -- Priority app for sleep
ORDER BY metric_date;
```

### Pattern 4: Fallback Query (When Primary Device Missing)

```sql
-- Get steps with fallback to iPhone if Apple Watch not available
SELECT
    SUM(metric_value) as total_steps,
    MAX(CASE WHEN additional_data LIKE '%Apple Watch%' THEN 'Apple Watch' ELSE 'iPhone' END) as source
FROM health_metrics
WHERE metric_type = 'step_count'
AND metric_date >= '2025-10-05 00:00:00'
AND metric_date < '2025-10-06 00:00:00'
AND (
    additional_data LIKE '%Apple Watch%'
    OR (additional_data LIKE '%iPhone%' AND NOT EXISTS (
        SELECT 1 FROM health_metrics h2
        WHERE h2.metric_type = 'step_count'
        AND h2.metric_date >= '2025-10-05 00:00:00'
        AND h2.metric_date < '2025-10-06 00:00:00'
        AND h2.additional_data LIKE '%Apple Watch%'
    ))
);
```

---

## Metric-Specific Device Priority

| Metric Category | Priority 1 | Priority 2 | Priority 3 |
|-----------------|------------|------------|------------|
| **Steps** | Apple Watch | iPhone | - |
| **Heart Rate** | Apple Watch | Sleep Cycle (sleep) | - |
| **Active Energy** | Apple Watch | - | - |
| **Exercise Time** | Apple Watch | - | - |
| **Flights Climbed** | Apple Watch | iPhone | - |
| **Distance (Walking/Running)** | Apple Watch | iPhone | - |
| **Body Weight** | Withings | iPhone (synced) | - |
| **BMI** | Withings | iPhone (synced) | - |
| **Body Fat %** | Withings | - | - |
| **Sleep Analysis** | Sleep Cycle | Apple Watch | - |
| **Resting Heart Rate** | Apple Watch | - | - |
| **HRV** | Apple Watch | - | - |
| **VO2 Max** | Apple Watch | - | - |
| **Workouts** | Apple Watch | Third-party apps | iPhone |

---

## Python Helper Functions

### Recommended Implementation

```python
class HealthDataQuery:
    """Helper class for device-priority health queries"""

    DEVICE_PRIORITY = {
        'step_count': ['Apple Watch', 'iPhone'],
        'heart_rate': ['Apple Watch', 'Sleep Cycle'],
        'active_energy': ['Apple Watch'],
        'weight_body_mass': ['Withings', 'iPhone'],
        'sleep_analysis': ['Sleep Cycle', 'Apple Watch'],
        # ... add more as needed
    }

    @staticmethod
    def get_metric_with_priority(metric_type, date_start, date_end, db_path):
        """
        Query metric using device priority to avoid double-counting

        Args:
            metric_type: Type of metric (e.g., 'step_count')
            date_start: Start datetime (ISO format)
            date_end: End datetime (ISO format)
            db_path: Path to health.db

        Returns:
            dict: {value, source, record_count}
        """
        import sqlite3

        priority_devices = HealthDataQuery.DEVICE_PRIORITY.get(
            metric_type,
            ['Apple Watch', 'iPhone']  # Default priority
        )

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Try devices in priority order
        for device in priority_devices:
            query = """
                SELECT
                    SUM(metric_value) as total,
                    COUNT(*) as count
                FROM health_metrics
                WHERE metric_type = ?
                AND metric_date >= ?
                AND metric_date < ?
                AND additional_data LIKE ?
            """

            cursor.execute(query, (
                metric_type,
                date_start,
                date_end,
                f'%{device}%'
            ))

            result = cursor.fetchone()
            if result and result[0]:
                conn.close()
                return {
                    'value': result[0],
                    'source': device,
                    'record_count': result[1]
                }

        conn.close()
        return None
```

### Usage Example

```python
# Get step count with device priority
result = HealthDataQuery.get_metric_with_priority(
    metric_type='step_count',
    date_start='2025-10-05 00:00:00',
    date_end='2025-10-06 00:00:00',
    db_path='/path/to/health.db'
)

print(f"Steps: {result['value']} from {result['source']}")
# Output: Steps: 9966 from Apple Watch
```

---

## Future Enhancements

### Option 1: View/Table with Priority Logic

Create a database view that automatically applies device priority:

```sql
CREATE VIEW health_metrics_priority AS
SELECT DISTINCT ON (metric_type, DATE(metric_date))
    metric_type,
    metric_date,
    metric_value,
    metric_unit,
    additional_data,
    CASE
        WHEN additional_data LIKE '%Apple Watch%' THEN 1
        WHEN additional_data LIKE '%Withings%' AND metric_type LIKE 'weight%' THEN 1
        WHEN additional_data LIKE '%Sleep Cycle%' AND metric_type = 'sleep_analysis' THEN 1
        WHEN additional_data LIKE '%iPhone%' THEN 2
        ELSE 3
    END as device_priority
FROM health_metrics
ORDER BY metric_type, DATE(metric_date), device_priority ASC;
```

### Option 2: Import-Time Deduplication

Modify import script to only import from priority device when multiple sources exist:

```python
# In rebuild_health_database.py or import_gap_data.py
def should_import_record(metric_type, date, source, existing_sources):
    """
    Determine if record should be imported based on device priority

    Returns:
        bool: True if this source has priority for this metric/date
    """
    priority = DEVICE_PRIORITY.get(metric_type, ['Apple Watch', 'iPhone'])

    # Check if a higher priority source already exists for this metric/date
    for higher_priority_source in priority:
        if higher_priority_source in existing_sources:
            if source != higher_priority_source:
                return False  # Skip this record

    return True  # Import this record
```

### Option 3: Query Wrapper in Health Service

Update Node.js health service to automatically apply device priority:

```javascript
// In health-service/src/database.js
class HealthDatabase {
    async getMetricWithPriority(metricType, dateStart, dateEnd) {
        const devicePriority = this.getDevicePriority(metricType);

        for (const device of devicePriority) {
            const result = await this.db.get(`
                SELECT
                    SUM(metric_value) as total,
                    COUNT(*) as count
                FROM health_metrics
                WHERE metric_type = ?
                AND metric_date >= ?
                AND metric_date < ?
                AND additional_data LIKE ?
            `, [metricType, dateStart, dateEnd, `%${device}%`]);

            if (result && result.total) {
                return {
                    value: result.total,
                    source: device,
                    recordCount: result.count
                };
            }
        }

        return null;
    }
}
```

---

## Verification

### Current Database Status

**Step Count Verification (October 5, 2025)**:
- ✅ Apple Watch only: 9,966 steps (matches expected ~9,841)
- ❌ Combined (Watch + iPhone): 18,508 steps (double-counted)
- **Accuracy**: 98.7% when using Apple Watch priority

### Recommended Testing

```bash
# Test device priority for different metrics
sqlite3 health.db "
SELECT
    metric_type,
    SUM(CASE WHEN additional_data LIKE '%Apple Watch%' THEN metric_value ELSE 0 END) as watch_total,
    SUM(CASE WHEN additional_data LIKE '%iPhone%' THEN metric_value ELSE 0 END) as iphone_total,
    SUM(metric_value) as combined_total
FROM health_metrics
WHERE metric_date >= '2025-10-05 00:00:00'
AND metric_date < '2025-10-06 00:00:00'
AND metric_type IN ('step_count', 'active_energy', 'walking_running_distance')
GROUP BY metric_type;
"
```

---

## Conclusion

**Key Principle**: Always filter by device source when querying health metrics to avoid double-counting.

**Default Priority**: Apple Watch > iPhone > Third-Party Apps

**Implementation**: Use device filtering in SQL queries or implement helper functions for consistent device priority logic.

**Next Steps**: Consider implementing automated priority logic at query level or import level for seamless operation.
