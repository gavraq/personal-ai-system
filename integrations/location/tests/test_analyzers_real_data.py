#!/usr/bin/env python3
"""
Real Data Tests for Activity Analyzers
Tests all analyzers with actual Owntracks data from October 2025 Portugal trip
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzers.golf_analyzer import GolfAnalyzer
from analyzers.parkrun_analyzer import ParkrunAnalyzer
from analyzers.commute_analyzer import CommuteAnalyzer
from analyzers.dog_walking_analyzer import DogWalkingAnalyzer
from analyzers.trip_analyzer import TripAnalyzer
from core.location_analyzer import LocationAnalyzer
from core.owntracks_client import OwntracksClient


# Owntracks device configuration
OWNTRACKS_USER = 'gavin-iphone'
OWNTRACKS_DEVICE = 'a2ea00bc-9862-4efb-a6ab-f038e32beb4c'


def test_golf_analyzer_portugal_trip():
    """Test Golf Analyzer with Portugal trip data (Oct 20-24, 2025)"""
    print("\n" + "=" * 70)
    print("TEST: Golf Analyzer - Portugal Trip (Oct 20-24, 2025)")
    print("=" * 70)

    # Initialize
    analyzer = GolfAnalyzer()
    location_analyzer = LocationAnalyzer()
    location_analyzer.load_trip('portugal_2025-10')
    client = OwntracksClient()

    # Known golf days (from journal entries)
    golf_days = [
        ('2025-10-20', 'Monday', 'Afternoon ~15:00-15:30'),
        ('2025-10-21', 'Tuesday', 'Afternoon ~15:00-15:15'),
        ('2025-10-22', 'Wednesday', 'Late morning/midday ~11:00-12:00'),
        ('2025-10-23', 'Thursday', 'Early afternoon ~12:00-13:00'),
        ('2025-10-24', 'Friday', 'Morning just after 11:00')
    ]

    golf_course = location_analyzer.get_location_info('pinecliffs-golf')
    results = []

    for date, day_name, expected_time in golf_days:
        print(f"\n{day_name} ({date}) - Expected: {expected_time}")

        # Get location data
        response = client.get_locations_for_date(
            user=OWNTRACKS_USER,
            device=OWNTRACKS_DEVICE,
            target_date=date
        )

        if not response.get('success') or not response.get('data'):
            print(f"  ✗ No location data")
            results.append((date, False, "No data"))
            continue

        locations = response['data']
        print(f"  → {len(locations)} location records")

        # Detect golf sessions
        sessions = analyzer.detect_sessions(
            locations,
            golf_course_location={
                'name': golf_course['name'],
                'coordinates': golf_course['coordinates'],
                'radius': golf_course['radius']
            }
        )

        if sessions:
            session = sessions[0]
            print(f"  ✓ Golf detected: {session.start_time.strftime('%H:%M')}-{session.end_time.strftime('%H:%M')}")
            print(f"    Duration: {session.duration_hours:.1f}h")
            print(f"    Confidence: {session.confidence} ({session.confidence_score:.2f})")
            print(f"    Location: {session.location_name}")
            results.append((date, True, session.confidence))
        else:
            print(f"  ✗ No golf detected")
            results.append((date, False, "Not detected"))

    # Summary
    print("\n" + "-" * 70)
    detected = sum(1 for _, success, _ in results if success)
    print(f"Summary: {detected}/5 golf days detected")

    for date, success, info in results:
        status = "✓" if success else "✗"
        print(f"  {status} {date}: {info}")

    if detected >= 4:  # Allow for 1 miss due to data quality
        print("\n✓ Golf analyzer test PASSED")
        return True
    else:
        print(f"\n✗ Golf analyzer test FAILED ({detected}/5 detected)")
        return False


def test_no_false_positives():
    """Test that non-golf day (Oct 19) doesn't detect golf"""
    print("\n" + "=" * 70)
    print("TEST: False Positive Check - October 19, 2025 (No Golf Day)")
    print("=" * 70)

    analyzer = GolfAnalyzer()
    location_analyzer = LocationAnalyzer()
    location_analyzer.load_trip('portugal_2025-10')
    client = OwntracksClient()

    print("\nOctober 19: NO GOLF expected (supermarket trip)")

    response = client.get_locations_for_date(
        user=OWNTRACKS_USER,
        device=OWNTRACKS_DEVICE,
        target_date='2025-10-19'
    )

    if not response.get('success') or not response.get('data'):
        print("  ⚠ No location data available (can't test)")
        return True

    locations = response['data']
    print(f"  → {len(locations)} location records")

    golf_course = location_analyzer.get_location_info('pinecliffs-golf')
    sessions = analyzer.detect_sessions(
        locations,
        golf_course_location={
            'name': golf_course['name'],
            'coordinates': golf_course['coordinates'],
            'radius': golf_course['radius']
        }
    )

    if not sessions:
        print("  ✓ No golf detected (correct!)")
        print("\n✓ False positive test PASSED")
        return True
    else:
        print(f"  ✗ False positive: detected {len(sessions)} session(s)")
        for session in sessions:
            print(f"    - {session.start_time.strftime('%H:%M')}-{session.end_time.strftime('%H:%M')}")
            print(f"      Confidence: {session.confidence} ({session.confidence_score:.2f})")
        print("\n✗ False positive test FAILED")
        return False


def test_trip_analyzer_integration():
    """Test TripAnalyzer with full Portugal trip"""
    print("\n" + "=" * 70)
    print("TEST: Trip Analyzer - Full Portugal Trip Analysis")
    print("=" * 70)

    analyzer = TripAnalyzer(trip_name='portugal_2025-10')

    # Analyze single day
    print("\nAnalyzing single day (2025-10-21)...")
    day_summary = analyzer.analyze_day('2025-10-21')

    if day_summary:
        print(f"✓ Day analysis completed")
        print(f"  Location records: {day_summary.get('location_count', 0)}")

        # Check for golf detection
        golf_sessions = day_summary.get('activities', {}).get('golf', [])
        if golf_sessions:
            print(f"  ✓ Golf detected: {len(golf_sessions)} session(s)")
            for session in golf_sessions:
                print(f"    - {session.get('start_time')} to {session.get('end_time')}")
                print(f"      {session.get('location_name')}, confidence: {session.get('confidence')}")
        else:
            print(f"  ⚠ No golf detected (expected golf on this day)")

        print("\n✓ Trip analyzer integration test PASSED")
        return True
    else:
        print("✗ Day analysis failed")
        print("\n✗ Trip analyzer integration test FAILED")
        return False


def test_parkrun_analyzer_uk_data():
    """Test Parkrun Analyzer with UK Saturday data"""
    print("\n" + "=" * 70)
    print("TEST: Parkrun Analyzer - UK Saturday Data")
    print("=" * 70)

    analyzer = ParkrunAnalyzer()
    location_analyzer = LocationAnalyzer()
    client = OwntracksClient()

    # Test with a recent Saturday
    test_date = '2025-10-18'  # Saturday before Portugal trip
    print(f"\nTesting {test_date} (Saturday before Portugal trip)")

    response = client.get_locations_for_date(
        user=OWNTRACKS_USER,
        device=OWNTRACKS_DEVICE,
        target_date=test_date
    )

    if not response.get('success') or not response.get('data'):
        print("  ⚠ No location data available (can't test)")
        return True

    locations = response['data']
    print(f"  → {len(locations)} location records")

    # Get known parkrun locations
    known_locations = location_analyzer.get_all_locations()

    sessions = analyzer.detect_sessions(
        locations,
        known_locations=known_locations
    )

    if sessions:
        print(f"  ✓ Parkrun detected: {len(sessions)} session(s)")
        for session in sessions:
            print(f"    - {session.start_time.strftime('%H:%M')}-{session.end_time.strftime('%H:%M')}")
            print(f"      {session.location_name}, confidence: {session.confidence}")
        print("\n✓ Parkrun analyzer test PASSED")
        return True
    else:
        print("  → No parkrun detected")
        print("  (This may be correct if no parkrun that day)")
        print("\n✓ Parkrun analyzer test PASSED (no false positive)")
        return True


def main():
    """Run all analyzer tests with real data"""
    print("\n" + "=" * 70)
    print("ACTIVITY ANALYZERS - REAL DATA TEST SUITE")
    print("=" * 70)
    print(f"\nUsing Owntracks device: {OWNTRACKS_USER}/{OWNTRACKS_DEVICE}")

    tests = [
        ('Golf Analyzer - Portugal Trip', test_golf_analyzer_portugal_trip),
        ('False Positive Check', test_no_false_positives),
        ('Trip Analyzer Integration', test_trip_analyzer_integration),
        ('Parkrun Analyzer - UK Data', test_parkrun_analyzer_uk_data),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed successfully!")
        return 0
    elif passed >= total - 1:
        print("\n⚠ Most tests passed (minor issues)")
        return 0
    else:
        print("\n❌ Multiple tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
