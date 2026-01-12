#!/usr/bin/env python3
"""Debug Oct 22 golf detection."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.owntracks_client import OwntracksClient
from analyzers.golf_analyzer import GolfAnalyzer
from datetime import datetime
import json

# Initialize
client = OwntracksClient()
golf_analyzer = GolfAnalyzer()

# Get locations for Oct 22 (2025!)
date = "2025-10-22"
device_id = "a2ea00bc-9862-4efb-a6ab-f038e32beb4c"

print(f"Analyzing {date}...")
result = client.get_locations_for_date(
    user="gavin-iphone",
    device=device_id,
    target_date=date
)

locations = result.get('data', [])
print(f"Total locations: {len(locations)}")
if len(locations) > 0:
    print(f"First location time: {locations[0].get('timestamp', 'N/A')}")
    print(f"Last location time: {locations[-1].get('timestamp', 'N/A')}")

# Load golf course configuration for Portugal
import json
from pathlib import Path

trips_dir = Path(__file__).parent.parent / "locations" / "trips"
portugal_trip = trips_dir / "portugal_2025-10.json"

golf_course = None
if portugal_trip.exists():
    with open(portugal_trip) as f:
        trip_data = json.load(f)
        # Find Pine Cliffs golf course
        for loc in trip_data.get('locations', []):
            if 'golf' in loc.get('activities', []) or 'golf' in loc.get('type', '').lower():
                golf_course = {
                    'name': loc['name'],
                    'coordinates': (loc['coordinates']['lat'], loc['coordinates']['lon']),
                    'radius': loc['radius']
                }
                print(f"Using golf course: {golf_course['name']}")
                break

# Detect golf sessions
sessions = golf_analyzer.detect_sessions(locations, golf_course)

print(f"\nDetected {len(sessions)} golf session(s):")
print("\nCompare with actual golf time from Owntracks screenshot:")
print("  Actual: 10:40-13:05 UTC (from screenshot URL)")
print()

for i, session in enumerate(sessions, 1):
    print(f"Session {i}:")
    start_str = session.start_time.strftime("%H:%M") if hasattr(session.start_time, 'strftime') else str(session.start_time)
    end_str = session.end_time.strftime("%H:%M") if hasattr(session.end_time, 'strftime') else str(session.end_time)
    print(f"  Detected: {start_str}-{end_str} UTC")
    print(f"  Duration: {session.duration_hours:.1f}h")
    print(f"  Confidence: {session.confidence}")
    print()
