#!/usr/bin/env python3
"""Debug location distribution for Oct 26."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.owntracks_client import OwntracksClient
from analyzers.dog_walking_analyzer import DogWalkingAnalyzer
from core.location_analyzer import LocationAnalyzer
from geopy.distance import geodesic

# Initialize
client = OwntracksClient()
analyzer = LocationAnalyzer()
dog_analyzer = DogWalkingAnalyzer()

# Get Oct 26 data
date = "2025-10-26"
result = client.get_locations_for_date('gavin-iphone', 'a2ea00bc-9862-4efb-a6ab-f038e32beb4c', date)
locations = result.get('data', [])

print(f"Total locations for {date}: {len(locations)}")
print()

# Get known locations
known_locations = analyzer.get_all_locations()
esher_common = known_locations['esher-common']
home_esher = known_locations['home-esher']

print(f"Esher Common: {esher_common['coordinates']}, radius: {esher_common['radius']}m")
print(f"Home: {home_esher['coordinates']}, radius: {home_esher['radius']}m")
print()

# Extract velocity segments
segments = dog_analyzer.extract_velocity_segments(locations)
walking_segments = [s for s in segments if s.activity_type in ['walking', 'stationary']]

print(f"Walking/stationary segments: {len(walking_segments)}")
print()

# Check how many segments are within Esher Common radius
ec_coords = esher_common['coordinates']
ec_radius = esher_common['radius']

within_ec = []
for seg in walking_segments:
    coords = seg.start_coords
    distance = geodesic(ec_coords, coords).meters
    if distance <= ec_radius:
        within_ec.append((seg, distance))

print(f"Segments within Esher Common radius ({ec_radius}m): {len(within_ec)}")
print()

# Group by time periods to see when segments are within EC
time_buckets = {}
for seg, distance in within_ec:
    hour = seg.start_time.hour
    if hour not in time_buckets:
        time_buckets[hour] = []
    time_buckets[hour].append(seg)

print("Distribution by hour:")
for hour in sorted(time_buckets.keys()):
    segs = time_buckets[hour]
    print(f"  Hour {hour:02d}: {len(segs)} segments")

    # Show first few segments for context
    if hour in [11, 12]:  # Focus on dog walk time
        for seg in segs[:5]:
            print(f"    {seg.start_time.strftime('%H:%M:%S')} - vel: {seg.velocity_mps:.2f} m/s, type: {seg.activity_type}")

print()

# Calculate distance from home for segments during dog walk time (11:38-12:13)
dog_walk_segments = [s for s in walking_segments
                     if s.start_time.hour == 11 and s.start_time.minute >= 38 or
                        s.start_time.hour == 12 and s.start_time.minute <= 13]

print(f"Segments during dog walk time (11:38-12:13): {len(dog_walk_segments)}")

if dog_walk_segments:
    # Check distances from Esher Common center
    for seg in dog_walk_segments[:10]:
        dist_ec = geodesic(ec_coords, seg.start_coords).meters
        dist_home = geodesic(home_esher['coordinates'], seg.start_coords).meters
        print(f"  {seg.start_time.strftime('%H:%M:%S')}: {dist_ec:.0f}m from EC, {dist_home:.0f}m from home, vel: {seg.velocity_mps:.2f} m/s")
