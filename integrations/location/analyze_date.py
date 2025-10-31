#!/usr/bin/env python3
"""
Analyze location data for a specific date using get_locations_for_date API
"""

import sys
from datetime import datetime
from owntracks_client import OwntracksClient

def format_duration(seconds):
    """Format duration in seconds to human readable format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate approximate distance in meters between two coordinates"""
    lat_diff = abs(lat1 - lat2)
    lon_diff = abs(lon1 - lon2)
    return ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111000

def analyze_date(date_str):
    """Analyze location data for a specific date"""

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

        # Define key locations
        home_lat, home_lon = 51.365647, -0.361388  # Esher home
        esher_station_lat, esher_station_lon = 51.3707, -0.3638  # Esher station
        waterloo_lat, waterloo_lon = 51.5031, -0.1132  # London Waterloo
        office_lat, office_lon = 51.5155, -0.0922  # Gresham Street office

        # Track time at locations
        location_periods = []
        current_location = None
        current_start = None

        for loc in locations:
            timestamp = datetime.fromtimestamp(loc['tst'])
            lat = loc.get('lat', 0)
            lon = loc.get('lon', 0)

            # Determine location
            location_name = None
            if calculate_distance(lat, lon, home_lat, home_lon) < 100:
                location_name = "Home"
            elif calculate_distance(lat, lon, office_lat, office_lon) < 200:
                location_name = "Office"
            elif calculate_distance(lat, lon, esher_station_lat, esher_station_lon) < 150:
                location_name = "Esher Station"
            elif calculate_distance(lat, lon, waterloo_lat, waterloo_lon) < 300:
                location_name = "Waterloo Station"
            elif loc.get('vel', 0) > 5:  # Moving fast (>5 m/s)
                location_name = "Travel"

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
                print(f"{period['start'].strftime('%H:%M')} - {period['end'].strftime('%H:%M')}: "
                      f"{period['location'] or 'Unknown'} ({format_duration(period['duration'])})")

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

        # Day type
        print("\nDAY TYPE:")
        print("-" * 80)
        if "Office" in location_totals:
            print("Office Day")
            print(f"- Office time: {format_duration(location_totals['Office'])}")
        else:
            print("WFH Day")
            print(f"- Home time: {format_duration(location_totals.get('Home', 0))}")

        return 0

    except Exception as e:
        print(f"Error analyzing location data: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: analyze_date.py YYYY-MM-DD")
        sys.exit(1)

    date_str = sys.argv[1]
    sys.exit(analyze_date(date_str))
