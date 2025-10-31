#!/usr/bin/env python3
"""
Enhanced location analysis using known_locations.json and regular-activities.json
"""

import sys
import json
import math
from datetime import datetime
from owntracks_client import OwntracksClient

def load_known_locations():
    """Load known locations from JSON file"""
    try:
        with open('known_locations.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def load_regular_activities():
    """Load regular activities from JSON file"""
    try:
        with open('regular-activities.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def format_duration(seconds):
    """Format duration in seconds to human readable format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in meters using Haversine formula"""
    R = 6371000  # Earth radius in meters

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

def identify_location(lat, lon, vel, known_locations):
    """Identify location from coordinates using known_locations.json"""
    # Check home first
    if 'home' in known_locations:
        home = known_locations['home']
        if calculate_distance(lat, lon, home['lat'], home['lon']) < home['radius']:
            return 'Home'

    # Check work locations
    if 'work' in known_locations:
        for key, loc in known_locations['work'].items():
            if calculate_distance(lat, lon, loc['lat'], loc['lon']) < loc['radius']:
                return loc['name']

    # Check health locations
    if 'health' in known_locations:
        for key, loc in known_locations['health'].items():
            if calculate_distance(lat, lon, loc['lat'], loc['lon']) < loc['radius']:
                return loc['name']

    # Check fitness locations
    if 'fitness' in known_locations:
        for key, loc in known_locations['fitness'].items():
            if calculate_distance(lat, lon, loc['lat'], loc['lon']) < loc['radius']:
                return loc['name']

    # Check family locations
    if 'family' in known_locations:
        for key, loc in known_locations['family'].items():
            if calculate_distance(lat, lon, loc['lat'], loc['lon']) < loc['radius']:
                return loc['name']

    # Classify by velocity if no known location matches
    if vel < 1:
        return None  # Stationary but unknown
    elif 2 <= vel <= 4:
        return 'Running'
    elif vel > 4:
        return 'Cycling/Driving'
    else:
        return 'Walking'

def classify_travel_mode(vel):
    """Classify travel mode based on velocity"""
    if vel < 1:
        return 'Stationary'
    elif vel < 2:
        return 'Walking'
    elif vel < 4:
        return 'Running'
    elif vel < 8:
        return 'Cycling'
    else:
        return 'Driving'

def analyze_date(date_str):
    """Analyze location data for a specific date with enhanced intelligence"""

    # Load location intelligence
    known_locations = load_known_locations()
    regular_activities = load_regular_activities()

    # Configuration
    base_url = "https://owntracks.gavinslater.co.uk"
    user = 'gavin-iphone'
    device = 'a2ea00bc-9862-4efb-a6ab-f038e32beb4c'

    # Initialize client
    client = OwntracksClient(base_url)

    print(f"Analyzing location data for {date_str}")
    print("=" * 80)

    try:
        # Get locations for specific date
        result = client.get_locations_for_date(user, device, date_str)

        if not result or 'data' not in result:
            print(f"No data returned for {date_str}")
            return 1

        locations = result['data']
        print(f"Retrieved {len(locations)} location points\n")

        if not locations:
            print(f"No location data found for {date_str}")
            return 1

        # Sort by timestamp
        locations.sort(key=lambda x: x.get('tst', 0))

        # Track time at locations
        location_periods = []
        current_location = None
        current_start = None

        for loc in locations:
            timestamp = datetime.fromtimestamp(loc['tst'])
            lat = loc.get('lat', 0)
            lon = loc.get('lon', 0)
            vel = loc.get('vel', 0)

            # Identify location using intelligence
            location_name = identify_location(lat, lon, vel, known_locations)

            # Track location changes
            if location_name != current_location:
                if current_location and current_start:
                    location_periods.append({
                        'location': current_location,
                        'start': current_start,
                        'end': timestamp,
                        'duration': (timestamp - current_start).total_seconds()
                    })
                current_location = location_name
                current_start = timestamp

        # Add final period
        if current_location and current_start:
            location_periods.append({
                'location': current_location,
                'start': current_start,
                'end': datetime.fromtimestamp(locations[-1]['tst']),
                'duration': (datetime.fromtimestamp(locations[-1]['tst']) - current_start).total_seconds()
            })

        # Consolidate adjacent periods at same location
        consolidated = []
        for period in location_periods:
            if consolidated and consolidated[-1]['location'] == period['location']:
                consolidated[-1]['end'] = period['end']
                consolidated[-1]['duration'] += period['duration']
            else:
                consolidated.append(period)

        # Generate timeline
        print("\nTIMELINE:")
        print("-" * 80)
        for period in consolidated:
            if period['duration'] > 300:  # Only show periods longer than 5 minutes
                loc_name = period['location'] or 'Unknown location'
                print(f"{period['start'].strftime('%H:%M')} - {period['end'].strftime('%H:%M')}: "
                      f"{loc_name} ({format_duration(period['duration'])})")

        # Time summary
        print("\nTIME AT LOCATIONS:")
        print("-" * 80)
        location_totals = {}
        for period in consolidated:
            loc = period['location']
            if loc:
                location_totals[loc] = location_totals.get(loc, 0) + period['duration']

        total_tracked = sum(location_totals.values())
        for loc in sorted(location_totals.keys()):
            duration = location_totals[loc]
            percentage = (duration / total_tracked * 100) if total_tracked > 0 else 0
            print(f"{loc}: {format_duration(duration)} ({percentage:.0f}%)")

        # Movement summary
        print("\nMOVEMENT SUMMARY:")
        print("-" * 80)
        first_time = datetime.fromtimestamp(locations[0]['tst'])
        last_time = datetime.fromtimestamp(locations[-1]['tst'])
        span = (last_time - first_time).total_seconds()

        print(f"First location: {first_time.strftime('%H:%M:%S')}")
        print(f"Last location: {last_time.strftime('%H:%M:%S')}")
        print(f"Tracking span: {format_duration(span)}")
        print(f"Location points: {len(locations):,}")

        # Day type classification
        print("\nDAY TYPE & PATTERN RECOGNITION:")
        print("-" * 80)

        patterns_identified = []

        # Check for office day
        if 'ICBC Standard Bank Office' in location_totals:
            office_time = location_totals['ICBC Standard Bank Office']
            patterns_identified.append(f"Office Day - {format_duration(office_time)} at office")
        elif 'Home' in location_totals and location_totals['Home'] > 18000:  # >5 hours
            patterns_identified.append("WFH Day")

        # Check for parkrun
        for loc in location_totals:
            if 'parkrun' in loc.lower():
                patterns_identified.append(f"Parkrun: {loc}")

        # Check for dog walking
        if 'Black Pond' in location_totals or 'Esher Common' in location_totals:
            patterns_identified.append("Dog walk with Roxy (Black Pond/Esher Common)")

        # Check for cycling
        cycling_detected = False
        for loc in locations:
            if loc.get('vel', 0) > 4:  # Cycling speed
                cycling_detected = True
                break
        if cycling_detected:
            patterns_identified.append("Cycling activity detected")

        # Check for school run
        if "Kimberly's School" in location_totals:
            patterns_identified.append("School drop-off (Kimberly)")

        # Check for hospital visit
        if 'Kingston Hospital' in location_totals:
            patterns_identified.append("Kingston Hospital visit")

        if patterns_identified:
            for pattern in patterns_identified:
                print(f"✓ {pattern}")
        else:
            print("Standard day - no special patterns identified")

        return 0

    except Exception as e:
        print(f"Error analyzing location data: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: analyze_date_enhanced.py YYYY-MM-DD")
        sys.exit(1)

    date_str = sys.argv[1]
    sys.exit(analyze_date(date_str))
