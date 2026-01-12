#!/usr/bin/env python3
"""
Test script for dynamic location database loading
Tests the new JSON-based location loading functionality
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.location_analyzer import LocationAnalyzer


def test_base_locations():
    """Test loading base UK locations"""
    print("=" * 70)
    print("TEST 1: Loading Base UK Locations")
    print("=" * 70)

    analyzer = LocationAnalyzer()

    base_locs = analyzer.base_locations
    print(f"\n✓ Loaded {len(base_locs)} base locations")

    # Display some key locations
    key_locations = ['home-esher', 'bushy-parkrun', 'icbc-office-london', 'heathrow-airport']
    for loc_id in key_locations:
        if loc_id in base_locs:
            loc = base_locs[loc_id]
            print(f"\n  {loc['name']}:")
            print(f"    Coordinates: {loc['coordinates']}")
            print(f"    Radius: {loc['radius']}m")
            print(f"    Type: {loc['type']}")
            if loc['tags']:
                print(f"    Tags: {', '.join(loc['tags'])}")

    print("\n✓ Base locations test passed")
    return True


def test_trip_locations():
    """Test loading Portugal trip locations"""
    print("\n" + "=" * 70)
    print("TEST 2: Loading Portugal Trip Locations")
    print("=" * 70)

    # Load with trip - use correct path from project root
    trips_dir = Path(__file__).parent.parent / "locations" / "trips"
    trip_path = trips_dir / "portugal_2025-10.json"

    analyzer = LocationAnalyzer(trip_locations_path=trip_path)

    trip_locs = analyzer.trip_locations
    print(f"\n✓ Loaded {len(trip_locs)} trip locations")

    # Display trip info
    if hasattr(analyzer, 'trip_info'):
        print(f"\nTrip Information:")
        print(f"  Name: {analyzer.trip_info['name']}")
        print(f"  Dates: {analyzer.trip_info['dates']['start']} to {analyzer.trip_info['dates']['end']}")
        print(f"  Timezone: {analyzer.trip_info['timezone']}")

    # Display key trip locations
    key_trip_locs = ['pinecliffs-resort', 'pinecliffs-golf', 'pingo-doce-vilamoura', 'faro-airport']
    for loc_id in key_trip_locs:
        if loc_id in trip_locs:
            loc = trip_locs[loc_id]
            print(f"\n  {loc['name']}:")
            print(f"    Coordinates: {loc['coordinates']}")
            print(f"    Radius: {loc['radius']}m")
            print(f"    Type: {loc['type']}")
            if loc.get('venue_type'):
                print(f"    Venue Type: {loc['venue_type']}")
            if loc.get('activities'):
                print(f"    Activities: {', '.join(loc['activities'])}")

    print("\n✓ Trip locations test passed")
    return True


def test_combined_locations():
    """Test combined base + trip locations"""
    print("\n" + "=" * 70)
    print("TEST 3: Combined Base + Trip Locations")
    print("=" * 70)

    trips_dir = Path(__file__).parent.parent / "locations" / "trips"
    trip_path = trips_dir / "portugal_2025-10.json"

    analyzer = LocationAnalyzer(trip_locations_path=trip_path)

    all_locs = analyzer.get_all_locations()
    base_count = len(analyzer.base_locations)
    trip_count = len(analyzer.trip_locations)
    total_count = len(all_locs)

    print(f"\n✓ Base locations: {base_count}")
    print(f"✓ Trip locations: {trip_count}")
    print(f"✓ Total combined: {total_count}")

    # Verify key locations from both databases are accessible
    test_locations = {
        'home-esher': 'base',
        'pinecliffs-golf': 'trip',
        'bushy-parkrun': 'base',
        'faro-airport': 'trip'
    }

    print("\nVerifying mixed location access:")
    for loc_id, source in test_locations.items():
        loc_info = analyzer.get_location_info(loc_id)
        if loc_info:
            print(f"  ✓ {loc_info['name']} ({source})")
        else:
            print(f"  ✗ {loc_id} NOT FOUND")
            return False

    print("\n✓ Combined locations test passed")
    return True


def test_load_trip_method():
    """Test the load_trip() convenience method"""
    print("\n" + "=" * 70)
    print("TEST 4: load_trip() Convenience Method")
    print("=" * 70)

    # Start with base locations only
    analyzer = LocationAnalyzer()
    print(f"\nInitial state: {len(analyzer.known_locations)} locations")

    # Load trip using convenience method
    analyzer.load_trip('portugal_2025-10')
    print(f"After load_trip(): {len(analyzer.known_locations)} locations")

    # Verify trip locations are now available
    trip_test_loc = analyzer.get_location_info('pinecliffs-resort')
    if trip_test_loc:
        print(f"\n✓ Trip location accessible: {trip_test_loc['name']}")
        print(f"  Coordinates: {trip_test_loc['coordinates']}")
    else:
        print("\n✗ Trip location NOT accessible")
        return False

    print("\n✓ load_trip() method test passed")
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("DYNAMIC LOCATION DATABASE LOADING - TEST SUITE")
    print("=" * 70)

    tests = [
        ('Base Locations', test_base_locations),
        ('Trip Locations', test_trip_locations),
        ('Combined Locations', test_combined_locations),
        ('load_trip() Method', test_load_trip_method)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} FAILED with exception: {e}")
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
    else:
        print("\n❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
