#!/usr/bin/env python3
"""
Rebuild Health Database from Fresh Apple Health Export
Imports all data from 2018-2025 with proper deduplication
"""

import xml.etree.ElementTree as ET
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# Configuration
EXPORT_XML = "/Users/gavinslater/projects/life/apple_health_export_new/export.xml"
DATABASE_PATH = "/Users/gavinslater/projects/life/health-integration/health-service/data/health.db"

# Metric mapping from HealthKit types to our names
METRIC_MAPPING = {
    'HKQuantityTypeIdentifierActiveEnergyBurned': 'active_energy',
    'HKQuantityTypeIdentifierAppleExerciseTime': 'apple_exercise_time',
    'HKQuantityTypeIdentifierAppleStandTime': 'apple_stand_time',
    'HKCategoryTypeIdentifierAppleStandHour': 'apple_stand_hour',
    'HKQuantityTypeIdentifierBasalEnergyBurned': 'basal_energy_burned',
    'HKQuantityTypeIdentifierBodyMass': 'weight_body_mass',
    'HKQuantityTypeIdentifierBodyMassIndex': 'body_mass_index',
    'HKQuantityTypeIdentifierBodyFatPercentage': 'body_fat_percentage',
    'HKQuantityTypeIdentifierFlightsClimbed': 'flights_climbed',
    'HKQuantityTypeIdentifierHeartRate': 'heart_rate',
    'HKQuantityTypeIdentifierHeartRateVariabilitySDNN': 'heart_rate_variability',
    'HKQuantityTypeIdentifierPhysicalEffort': 'physical_effort',
    'HKQuantityTypeIdentifierRestingHeartRate': 'resting_heart_rate',
    'HKCategoryTypeIdentifierSleepAnalysis': 'sleep_analysis',
    'HKQuantityTypeIdentifierStepCount': 'step_count',
    'HKQuantityTypeIdentifierVO2Max': 'vo2_max',
    'HKQuantityTypeIdentifierWalkingHeartRateAverage': 'walking_heart_rate_average',
    'HKQuantityTypeIdentifierDistanceWalkingRunning': 'walking_running_distance',
    'HKQuantityTypeIdentifierRunningSpeed': 'running_speed',
    'HKQuantityTypeIdentifierWalkingSpeed': 'walking_speed',
    'HKQuantityTypeIdentifierWalkingStepLength': 'walking_step_length',
    'HKQuantityTypeIdentifierHeartRateRecoveryOneMinute': 'cardio_recovery',
}

# Device filter - only import from Gavin's devices
ALLOWED_SOURCES = [
    "Gavin's Apple Watch",
    "Gavin's iPhone 14",
    "Gavin's iPhone Xs Max",
    "Gavins iPhone 6s+",
    "Gavins iPhone Xs Max",
    "Withings",
    "Sleep Cycle",
    "Arc Timeline",
    "Runkeeper",
    "Headspace",
    "Health Import",
    "Health",
    "Ember",
    "Clock"
]

def parse_date(date_str):
    """Parse date string to datetime object"""
    try:
        return datetime.strptime(date_str[:19], "%Y-%m-%d %H:%M:%S")
    except Exception:
        return None

def get_metric_name(hk_type):
    """Convert HealthKit type to our metric name"""
    return METRIC_MAPPING.get(hk_type)

def rebuild_database():
    """Rebuild database from fresh export"""

    print("=" * 80)
    print("REBUILD HEALTH DATABASE FROM FRESH EXPORT")
    print("=" * 80)
    print(f"\nExport: {EXPORT_XML}")
    print(f"Database: {DATABASE_PATH}\n")

    # Connect to database
    print("Connecting to database...")
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Drop old table
    print("Dropping old health_metrics table...")
    cursor.execute("DROP TABLE IF EXISTS health_metrics")
    conn.commit()

    # Create new table with unique constraint
    print("Creating new health_metrics table with unique constraint...")
    cursor.execute('''
        CREATE TABLE health_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_type TEXT NOT NULL,
            metric_source TEXT NOT NULL,
            metric_date TEXT NOT NULL,
            metric_value REAL,
            metric_unit TEXT,
            additional_data TEXT,
            created_at TEXT NOT NULL,
            UNIQUE(metric_type, metric_source, metric_date, metric_value)
        )
    ''')

    # Create indexes
    print("Creating indexes...")
    cursor.execute("CREATE INDEX idx_health_metrics_type ON health_metrics(metric_type)")
    cursor.execute("CREATE INDEX idx_health_metrics_date ON health_metrics(metric_date)")
    cursor.execute("CREATE INDEX idx_health_metrics_source ON health_metrics(metric_source)")
    cursor.execute("CREATE INDEX idx_health_metrics_type_date ON health_metrics(metric_type, metric_date)")
    conn.commit()

    # Track statistics
    stats = {
        'total_processed': 0,
        'imported': 0,
        'skipped_metric': 0,
        'skipped_device': 0,
        'skipped_duplicate': 0,
        'errors': 0,
        'by_metric': {},
        'by_device': {}
    }

    print(f"\nParsing XML export...")
    print("This will take several minutes for 7 years of data...\n")

    # Parse XML incrementally
    context = ET.iterparse(EXPORT_XML, events=('end',))

    batch_size = 1000
    batch_records = []

    for event, elem in context:
        if elem.tag == 'Record':
            stats['total_processed'] += 1

            # Progress indicator
            if stats['total_processed'] % 100000 == 0:
                print(f"  Processed {stats['total_processed']:,} records, imported {stats['imported']:,}...")

            # Get record attributes
            record_type = elem.get('type', '')
            start_date_str = elem.get('startDate', '')
            value = elem.get('value', '')
            unit = elem.get('unit', '')
            source_name = elem.get('sourceName', 'Unknown')

            # Check if this is a metric we track
            metric_name = get_metric_name(record_type)
            if not metric_name:
                stats['skipped_metric'] += 1
                elem.clear()
                continue

            # Filter by device source
            if source_name not in ALLOWED_SOURCES:
                stats['skipped_device'] += 1
                stats['by_device'][source_name] = stats['by_device'].get(source_name, 0) + 1
                elem.clear()
                continue

            # Parse date
            date_obj = parse_date(start_date_str)
            if not date_obj:
                stats['errors'] += 1
                elem.clear()
                continue

            # Prepare record
            metric_date = start_date_str
            try:
                metric_value = float(value) if value else 0.0
            except ValueError:
                metric_value = 0.0

            # Track by metric
            if metric_name not in stats['by_metric']:
                stats['by_metric'][metric_name] = 0
            stats['by_metric'][metric_name] += 1

            batch_records.append((
                metric_name,
                'health_export_complete',  # Source identifier
                metric_date,
                metric_value,
                unit,
                f'{{"source": "{source_name}"}}',
                datetime.now().isoformat()
            ))

            # Insert in batches
            if len(batch_records) >= batch_size:
                try:
                    cursor.executemany('''
                        INSERT OR IGNORE INTO health_metrics
                        (metric_type, metric_source, metric_date, metric_value, metric_unit, additional_data, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', batch_records)
                    conn.commit()
                    stats['imported'] += len(batch_records)
                    batch_records = []
                except Exception as e:
                    print(f"\nError inserting batch: {e}")
                    stats['errors'] += len(batch_records)
                    batch_records = []

            elem.clear()

        # Handle Workout records
        elif elem.tag == 'Workout':
            stats['total_processed'] += 1

            start_date_str = elem.get('startDate', '')
            source_name = elem.get('sourceName', 'Unknown')

            # Filter by device
            if source_name not in ALLOWED_SOURCES:
                stats['skipped_device'] += 1
                elem.clear()
                continue

            date_obj = parse_date(start_date_str)
            if not date_obj:
                elem.clear()
                continue

            workout_type = elem.get('workoutActivityType', '').replace('HKWorkoutActivityType', '')
            duration = float(elem.get('duration', 0))
            distance = float(elem.get('totalDistance', 0))
            distance_unit = elem.get('totalDistanceUnit', 'km')
            energy = float(elem.get('totalEnergyBurned', 0))

            metric_name = f"workout_{workout_type}"

            if metric_name not in stats['by_metric']:
                stats['by_metric'][metric_name] = 0
            stats['by_metric'][metric_name] += 1

            batch_records.append((
                metric_name,
                'health_export_complete',
                start_date_str,
                duration,
                'seconds',
                f'{{"distance": {distance}, "distance_unit": "{distance_unit}", "energy": {energy}, "source": "{source_name}"}}',
                datetime.now().isoformat()
            ))

            elem.clear()

    # Insert remaining batch
    if batch_records:
        try:
            cursor.executemany('''
                INSERT OR IGNORE INTO health_metrics
                (metric_type, metric_source, metric_date, metric_value, metric_unit, additional_data, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', batch_records)
            conn.commit()
            stats['imported'] += len(batch_records)
        except Exception as e:
            print(f"\nError inserting final batch: {e}")
            stats['errors'] += len(batch_records)

    # Print results
    print("\n" + "=" * 80)
    print("IMPORT COMPLETE")
    print("=" * 80)
    print(f"\nTotal records processed: {stats['total_processed']:,}")
    print(f"Successfully imported: {stats['imported']:,}")
    print(f"Skipped (unsupported metric): {stats['skipped_metric']:,}")
    print(f"Skipped (filtered device): {stats['skipped_device']:,}")
    print(f"Errors: {stats['errors']:,}")

    if stats['by_device']:
        print(f"\n{'Filtered Devices':<40} {'Records Skipped':>20}")
        print("-" * 80)
        for device, count in sorted(stats['by_device'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"{device:<40} {count:>20,}")

    print(f"\n{'Metric':<40} {'Records Imported':>20}")
    print("-" * 80)
    for metric, count in sorted(stats['by_metric'].items(), key=lambda x: x[1], reverse=True):
        print(f"{metric:<40} {count:>20,}")

    # Verify database
    cursor.execute("SELECT COUNT(*) FROM health_metrics")
    final_count = cursor.fetchone()[0]

    cursor.execute("SELECT MIN(metric_date), MAX(metric_date) FROM health_metrics")
    date_range = cursor.fetchone()

    print(f"\n{'='*80}")
    print("DATABASE VERIFICATION")
    print("=" * 80)
    print(f"Final record count: {final_count:,}")
    print(f"Date range: {date_range[0]} to {date_range[1]}")
    print(f"\nDatabase rebuilt successfully!")
    print("=" * 80)

    conn.close()

if __name__ == '__main__':
    try:
        rebuild_database()
    except KeyboardInterrupt:
        print("\n\nImport cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
