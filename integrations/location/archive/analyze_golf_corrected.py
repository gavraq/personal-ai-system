#!/usr/bin/env python3
"""
Corrected Portugal trip analysis based on user-provided schedule
Focuses on actual golf times and key locations
"""

import sys
from datetime import datetime, time
from owntracks_client import OwntracksClient
import math

# Known Portugal locations
LOCATIONS = {
    "Pine Cliffs Golf": {"lat": 37.093, "lon": -8.175, "radius": 250},
    "Vila Vita Parc Resort": {"lat": 37.0890, "lon": -8.1920, "radius": 150},
    "Pingo Doce Vilamoura": {"lat": 37.1040, "lon": -8.1266, "radius": 100},
    "Armação de Pêra Beach": {"lat": 37.0999, "lon": -8.3551, "radius": 150},
    "Faro Airport": {"lat": 37.0147, "lon": -7.9658, "radius": 400}
}

# Expected golf times based on user correction
GOLF_SCHEDULE = {
    "2025-10-20": {"time": "15:30", "duration": "2-2.5 hours", "holes": 9},
    "2025-10-21": {"time": "15:00-15:15", "duration": "2-2.5 hours", "holes": 9},
    "2025-10-22": {"time": "11:00-12:00", "duration": "2-2.5 hours", "holes": 9},
    "2025-10-23": {"time": "12:00-13:00", "duration": "2-2.5 hours", "holes": 9},
    "2025-10-24": {"time": "11:00+", "duration": "2-2.5 hours", "holes": 9}
}

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi, delta_lambda = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def identify_location(lat, lon):
    for name, loc in LOCATIONS.items():
        if haversine_distance(lat, lon, loc["lat"], loc["lon"]) <= loc["radius"]:
            return name
    return None

def format_time(ts):
    return datetime.fromtimestamp(ts).strftime('%H:%M')

def analyze_date(date_str):
    print(f"\n{'='*80}")
    print(f"CORRECTED ANALYSIS: {date_str}")
    print(f"{'='*80}")

    client = OwntracksClient()
    result = client.get_locations_for_date('gavin-iphone', 'a2ea00bc-9862-4efb-a6ab-f038e32beb4c', date_str)

    if not result['success'] or not result['data']:
        print("No data available")
        return

    locations = result['data']
    print(f"\nTotal location points: {len(locations)}\n")

    # Build timeline of location visits
    visits = {}

    for point in locations:
        lat, lon, ts = point.get('lat'), point.get('lon'), point.get('tst')
        if not (lat and lon and ts):
            continue

        loc = identify_location(lat, lon)
        if loc:
            if loc not in visits:
                visits[loc] = []
            visits[loc].append(ts)

    # Condense visits into time ranges
    print("LOCATION TIMELINE:")
    print("-" * 80)

    for loc_name in sorted(visits.keys()):
        timestamps = sorted(visits[loc_name])
        if not timestamps:
            continue

        # Group into continuous visits (gap > 10 minutes = new visit)
        ranges = []
        start = timestamps[0]
        end = timestamps[0]

        for ts in timestamps[1:]:
            if ts - end <= 600:  # 10 minute gap tolerance
                end = ts
            else:
                ranges.append((start, end))
                start = ts
                end = ts
        ranges.append((start, end))

        # Print visits over 5 minutes
        for start, end in ranges:
            duration_min = (end - start) // 60
            if duration_min >= 5:
                start_dt = datetime.fromtimestamp(start)
                end_dt = datetime.fromtimestamp(end)
                hours = duration_min // 60
                mins = duration_min % 60
                dur_str = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"
                print(f"{start_dt.strftime('%H:%M')}-{end_dt.strftime('%H:%M')}: {loc_name} ({dur_str})")

    # Golf analysis for dates with expected rounds
    if date_str in GOLF_SCHEDULE:
        print(f"\n{'='*80}")
        print("GOLF ROUND ANALYSIS:")
        print("-" * 80)
        golf_info = GOLF_SCHEDULE[date_str]
        print(f"Expected: {golf_info['time']} ({golf_info['duration']}, {golf_info['holes']} holes)")

        if "Pine Cliffs Golf" in visits:
            timestamps = sorted(visits["Pine Cliffs Golf"])
            # Look for afternoon activity
            afternoon_times = [ts for ts in timestamps if 11 <= datetime.fromtimestamp(ts).hour < 19]

            if afternoon_times:
                # Find the main golf session
                start = afternoon_times[0]
                end = afternoon_times[-1]
                duration_min = (end - start) // 60
                hours = duration_min // 60
                mins = duration_min % 60

                print(f"Detected: {format_time(start)}-{format_time(end)} ({hours}h {mins}m)")
                print(f"Course location confirmed: Pine Cliffs Golf")

    # Special events
    if date_str == "2025-10-19":
        print(f"\n{'='*80}")
        print("SPECIAL NOTES: No golf - Supermarket trip to Pingo Doce")
    elif date_str == "2025-10-21":
        print(f"\n{'='*80}")
        print("SPECIAL NOTES: Midday excursion to Armação de Pêra beach before golf")
    elif date_str == "2025-10-23":
        print(f"\n{'='*80}")
        print("SPECIAL NOTES: Drive to Faro Airport ~17:00 (Kimberly's friend)")
        # Check for airport visit
        if "Faro Airport" in visits:
            timestamps = sorted(visits["Faro Airport"])
            if timestamps:
                print(f"Airport visit confirmed: {format_time(timestamps[0])}-{format_time(timestamps[-1])}")
        else:
            print("Note: Airport visit not detected in location data (may need radius adjustment)")

    print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_golf_corrected.py YYYY-MM-DD")
        sys.exit(1)

    date = sys.argv[1]
    analyze_date(date)
