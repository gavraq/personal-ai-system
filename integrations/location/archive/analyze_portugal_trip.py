#!/usr/bin/env python3
"""
Detailed location analysis for Portugal trip (Oct 19-24, 2025)
Identifies specific locations: golf course, supermarket, beach, airport
"""

import sys
from datetime import datetime
from owntracks_client import OwntracksClient
import math

# Known Portugal locations
PORTUGAL_LOCATIONS = {
    "Pine Cliffs Golf": {
        "lat": 37.093,
        "lon": -8.175,
        "radius": 300,  # meters
        "description": "Pine Cliffs Golf Course - 9 holes"
    },
    "Pingo Doce Vilamoura": {
        "lat": 37.1040,
        "lon": -8.1266,
        "radius": 150,
        "description": "Pingo Doce supermarket near Vilamoura"
    },
    "Armação de Pêra Beach": {
        "lat": 37.0999,
        "lon": -8.3551,
        "radius": 200,
        "description": "Armação de Pêra beach excursion"
    },
    "Faro Airport": {
        "lat": 37.0147,
        "lon": -7.9658,
        "radius": 500,
        "description": "Faro Airport (FAO)"
    },
    "Vila Vita Parc": {
        "lat": 37.0890,
        "lon": -8.1920,
        "radius": 200,
        "description": "Vila Vita Parc Resort (accommodation)"
    }
}

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in meters"""
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

def classify_velocity(vel):
    """Classify movement mode based on velocity"""
    if vel is None or vel < 1:
        return "Stationary"
    elif vel < 2:
        return "Walking"
    elif vel < 4:
        return "Running"
    elif vel < 8:
        return "Cycling"
    else:
        return "Driving"

def identify_location(lat, lon):
    """Identify which known location this point is near"""
    for name, loc in PORTUGAL_LOCATIONS.items():
        distance = haversine_distance(lat, lon, loc["lat"], loc["lon"])
        if distance <= loc["radius"]:
            return name, distance
    return None, None

def format_time(timestamp):
    """Convert Unix timestamp to HH:MM format in local Portugal time"""
    try:
        # Handle both integer and string timestamps
        if isinstance(timestamp, str):
            timestamp = int(timestamp)
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime('%H:%M')
    except:
        return str(timestamp)

def calculate_duration(start_ts, end_ts):
    """Calculate duration between two timestamps"""
    try:
        if isinstance(start_ts, str):
            start_ts = int(start_ts)
        if isinstance(end_ts, str):
            end_ts = int(end_ts)
        duration_seconds = end_ts - start_ts
        hours = duration_seconds // 3600
        minutes = (duration_seconds % 3600) // 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    except:
        return "?"

def analyze_day(date_str):
    """Analyze location data for a specific date"""
    print(f"\n{'='*80}")
    print(f"PORTUGAL TRIP ANALYSIS: {date_str}")
    print(f"{'='*80}\n")

    # Initialize client
    client = OwntracksClient()

    # Fetch data
    user = "gavin-iphone"
    device = "a2ea00bc-9862-4efb-a6ab-f038e32beb4c"

    result = client.get_locations_for_date(user, device, date_str)

    if not result['success']:
        print(f"Error: {result.get('error', 'Unknown error')}")
        return

    locations = result['data']
    if not locations:
        print("No location data available for this date")
        return

    print(f"Retrieved {len(locations)} location points\n")

    # Analyze locations - group consecutive points at same location
    location_visits = []
    current_location = None
    current_start = None
    current_end = None

    for point in locations:
        lat = point.get('lat')
        lon = point.get('lon')
        timestamp = point.get('tst')
        vel = point.get('vel', 0)

        if lat is None or lon is None:
            continue

        # Identify location
        loc_name, distance = identify_location(lat, lon)

        if loc_name:
            if current_location == loc_name:
                # Continue current visit
                current_end = timestamp
            else:
                # Save previous visit
                if current_location:
                    location_visits.append({
                        'location': current_location,
                        'start': current_start,
                        'end': current_end,
                        'start_time': format_time(current_start),
                        'end_time': format_time(current_end),
                        'duration': calculate_duration(current_start, current_end)
                    })

                # Start new visit
                current_location = loc_name
                current_start = timestamp
                current_end = timestamp
        else:
            # Save current visit if moving away from a location
            if current_location:
                location_visits.append({
                    'location': current_location,
                    'start': current_start,
                    'end': current_end,
                    'start_time': format_time(current_start),
                    'end_time': format_time(current_end),
                    'duration': calculate_duration(current_start, current_end)
                })
                current_location = None

    # Save final visit
    if current_location:
        location_visits.append({
            'location': current_location,
            'start': current_start,
            'end': current_end,
            'start_time': format_time(current_start),
            'end_time': format_time(current_end),
            'duration': calculate_duration(current_start, current_end)
        })

    # Print timeline
    print("TIMELINE:")
    print("-" * 80)

    if location_visits:
        for visit in location_visits:
            print(f"{visit['start_time']}-{visit['end_time']}: {visit['location']} ({visit['duration']})")
    else:
        print("No recognized locations visited")

    # Print location summary
    print(f"\n{'='*80}")
    print("LOCATION SUMMARY:")
    print("-" * 80)

    # Group by location name
    location_totals = {}
    for visit in location_visits:
        loc = visit['location']
        if loc not in location_totals:
            location_totals[loc] = []
        location_totals[loc].append(visit)

    for loc_name in sorted(location_totals.keys()):
        visits = location_totals[loc_name]
        print(f"\n{loc_name}:")
        print(f"  Description: {PORTUGAL_LOCATIONS[loc_name]['description']}")
        print(f"  Number of visits: {len(visits)}")
        for i, v in enumerate(visits, 1):
            print(f"    Visit {i}: {v['start_time']}-{v['end_time']} ({v['duration']})")

    print()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 analyze_portugal_trip.py YYYY-MM-DD")
        sys.exit(1)

    date = sys.argv[1]
    analyze_day(date)
