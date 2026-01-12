#!/usr/bin/env python3
"""Test dog walk detection for Oct 26."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.owntracks_client import OwntracksClient
from analyzers.dog_walking_analyzer import DogWalkingAnalyzer
from core.location_analyzer import LocationAnalyzer
from datetime import datetime

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

# Test dog walking detection
known_locations = analyzer.get_all_locations()
print(f"Known locations loaded: {len(known_locations)}")

# Check if esher-common is loaded
if 'esher-common' in known_locations:
    ec = known_locations['esher-common']
    print(f"Esher Common: {ec['coordinates']}, radius: {ec['radius']}m")
print()

# Extract velocity segments first to see what we're working with
segments = dog_analyzer.extract_velocity_segments(locations)
print(f"Total velocity segments: {len(segments)}")

walking_segments = [s for s in segments if s.activity_type in ['walking', 'stationary']]
print(f"Walking/stationary segments: {len(walking_segments)}")

if walking_segments:
    # Show segments around the 11:38-12:13 time
    target_segments = [s for s in walking_segments
                       if s.start_time.hour == 11 and s.start_time.minute >= 38 or
                          s.start_time.hour == 12 and s.start_time.minute <= 13]
    print(f"\nWalking segments during 11:38-12:13: {len(target_segments)}")
    if target_segments:
        print(f"  First: {target_segments[0].start_time.strftime('%H:%M:%S')}")
        print(f"  Last: {target_segments[-1].start_time.strftime('%H:%M:%S')}")

# Apply the pre-filter that detect_sessions uses
filtered_segments = []
for seg in walking_segments:
    coords = seg.start_coords
    # ONLY include segments at known walking locations (matches updated code)
    is_known = dog_analyzer.is_known_walking_location(coords, known_locations)
    if is_known:
        filtered_segments.append(seg)

print(f"\nFiltered segments (at known walking locations ONLY): {len(filtered_segments)}")

# Cluster the filtered segments
if filtered_segments:
    session_clusters = dog_analyzer.cluster_sessions(filtered_segments)
    print(f"Session clusters formed from filtered segments: {len(session_clusters)}")
    for i, cluster in enumerate(session_clusters[:5]):
        start = cluster[0].start_time
        end = cluster[-1].end_time
        duration_min = (end - start).total_seconds() / 60
        print(f"  Cluster {i+1}: {start.strftime('%H:%M')}-{end.strftime('%H:%M')} ({duration_min:.0f} min, {len(cluster)} segments)")

sessions = dog_analyzer.detect_sessions(locations, known_locations)
print(f"\nDog walking sessions detected: {len(sessions)}")

for i, session in enumerate(sessions, 1):
    print(f"\nSession {i}:")
    print(f"  Time: {session.start_time.strftime('%H:%M')}-{session.end_time.strftime('%H:%M')}")
    print(f"  Duration: {session.duration_hours:.1f}h ({session.duration_hours*60:.0f} min)")
    print(f"  Confidence: {session.confidence}")
    if hasattr(session, 'metadata') and 'location_name' in session.metadata:
        print(f"  Location: {session.metadata['location_name']}")

print("\n" + "="*60)
print("EXPECTED: Dog walk at Black Pond 11:38-12:13 (35 min)")
print("="*60)
