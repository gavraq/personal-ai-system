#!/usr/bin/env python3
"""Test activity detection integration in LocationAnalyzer."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from location_agent import LocationAgent
from datetime import datetime

# Initialize agent
agent = LocationAgent()

# Test with Oct 20, 2025 (we know this has golf)
test_date = "2025-10-20"
print(f"Testing activity detection for {test_date}...")
print("=" * 60)

result = agent.where_was_i(test_date)

if result['success']:
    pattern = result['answer']

    print(f"\nLocation Count: {pattern['location_count']}")

    # Debug: check known locations
    print(f"\nKnown locations loaded: {len(agent.analyzer.known_locations)}")
    golf_courses = [loc for loc_id, loc in agent.analyzer.known_locations.items()
                    if 'golf' in loc.get('activities', []) or 'golf' in loc.get('type', '').lower()]
    print(f"Golf courses found: {len(golf_courses)}")
    if golf_courses:
        for course in golf_courses:
            print(f"  - {course['name']}")

    print(f"\nDetected Activities:")

    if 'detected_activities' in pattern and pattern['detected_activities']:
        for activity in pattern['detected_activities']:
            print(f"\n  {activity['activity_type'].upper()}:")
            print(f"    Time: {activity['start_time']}-{activity['end_time']}")
            print(f"    Duration: {activity['duration_hours']}h")
            print(f"    Confidence: {activity['confidence']}")
            if 'venue' in activity:
                print(f"    Venue: {activity['venue']}")
            if 'runs' in activity:
                print(f"    Runs: {activity['runs']}")
            if 'vertical_meters' in activity:
                print(f"    Vertical: {activity['vertical_meters']}m")
    else:
        print("  No activities detected")
else:
    print(f"Error: {result.get('error', 'Unknown error')}")
