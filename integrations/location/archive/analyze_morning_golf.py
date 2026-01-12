#!/usr/bin/env python3
"""
Focused golf analysis for morning period (7am-11am)
"""

import sys
import json
import math
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
    """Calculate distance in meters using Haversine formula"""
    R = 6371000  # Earth radius in meters

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

def analyze_morning_golf(date_str):
    """Analyze morning period (7am-11am) for golf activity"""

    # Configuration
    base_url = "https://owntracks.gavinslater.co.uk"
    user = 'gavin-iphone'
    device = 'a2ea00bc-9862-4efb-a6ab-f038e32beb4c'

    # Initialize client
    client = OwntracksClient(base_url)

    print(f"Analyzing MORNING GOLF ACTIVITY for {date_str} (07:00-11:00)")
    print("=" * 80)

    try:
        # Get locations for specific date
        result = client.get_locations_for_date(user, device, date_str)

        if not result or 'data' not in result:
            print(f"No data returned for {date_str}")
            return 1

        locations = result['data']
        locations.sort(key=lambda x: x.get('tst', 0))

        # Filter to morning period (7am-11am)
        morning_locations = []
        for loc in locations:
            timestamp = datetime.fromtimestamp(loc['tst'])
            if 7 <= timestamp.hour < 11:
                morning_locations.append(loc)

        print(f"Morning location points (7am-11am): {len(morning_locations)}\n")

        if not morning_locations:
            print("No morning data found")
            return 1

        # Analyze specific area around Pine Cliffs golf coordinates
        # Pine Cliffs Golf Course approximate area: 37.0892, -8.3480 (this is the general resort area)
        # Let's look at actual coordinates from the data

        print("MORNING ACTIVITY SUMMARY:")
        print("-" * 80)

        # Get coordinate ranges
        lats = [loc.get('lat', 0) for loc in morning_locations]
        lons = [loc.get('lon', 0) for loc in morning_locations]

        print(f"Latitude range: {min(lats):.6f} to {max(lats):.6f}")
        print(f"Longitude range: {min(lons):.6f} to {max(lons):.6f}")
        print(f"Center point: {sum(lats)/len(lats):.6f}, {sum(lons)/len(lons):.6f}\n")

        # Look for periods of activity
        print("MORNING TIMELINE (detailed):")
        print("-" * 80)

        activity_start = None
        last_time = None
        last_lat = None
        last_lon = None

        for loc in morning_locations:
            timestamp = datetime.fromtimestamp(loc['tst'])
            lat = loc.get('lat', 0)
            lon = loc.get('lon', 0)
            vel = loc.get('vel', 0)
            vel_kmh = vel * 3.6

            # Detect activity changes
            if last_time:
                time_gap = (timestamp - last_time).total_seconds()
                if time_gap > 300:  # 5 minute gap
                    print(f"\n--- {format_duration(time_gap)} gap ---\n")

            # Classify activity
            if vel < 0.5:
                status = "STATIONARY"
            elif vel < 2.5:
                status = "WALKING/GOLF"
                if not activity_start:
                    activity_start = timestamp
            elif vel < 4:
                status = "RUNNING"
            else:
                status = f"VEHICLE ({vel_kmh:.1f} km/h)"
                activity_start = None

            # Calculate distance from last point
            dist_from_last = 0
            if last_lat and last_lon:
                dist_from_last = calculate_distance(last_lat, last_lon, lat, lon)

            print(f"{timestamp.strftime('%H:%M:%S')} | {status:15} | "
                  f"Vel: {vel:4.1f} m/s ({vel_kmh:5.1f} km/h) | "
                  f"Pos: {lat:.6f}, {lon:.6f} | "
                  f"Move: {dist_from_last:4.0f}m")

            last_time = timestamp
            last_lat = lat
            last_lon = lon

        # Velocity analysis
        print("\n" + "=" * 80)
        print("MORNING VELOCITY ANALYSIS:")
        print("-" * 80)

        velocity_buckets = {
            'Stationary': 0,
            'Walking/Golf pace': 0,
            'Running': 0,
            'Vehicle': 0
        }

        for loc in morning_locations:
            vel = loc.get('vel', 0)
            if vel < 0.5:
                velocity_buckets['Stationary'] += 1
            elif vel < 2.5:
                velocity_buckets['Walking/Golf pace'] += 1
            elif vel < 4:
                velocity_buckets['Running'] += 1
            else:
                velocity_buckets['Vehicle'] += 1

        total = len(morning_locations)
        for category, count in velocity_buckets.items():
            percentage = (count / total) * 100 if total > 0 else 0
            print(f"{category:20}: {count:4} points ({percentage:5.1f}%)")

        # Golf likelihood assessment
        print("\n" + "=" * 80)
        print("GOLF ACTIVITY ASSESSMENT:")
        print("-" * 80)

        walking_pct = (velocity_buckets['Walking/Golf pace'] / total) * 100 if total > 0 else 0
        stationary_pct = (velocity_buckets['Stationary'] / total) * 100 if total > 0 else 0

        if walking_pct > 5 and stationary_pct > 10:
            print("LIKELY GOLF ACTIVITY")
            print(f"- Significant walking activity: {walking_pct:.1f}%")
            print(f"- Stationary periods (tee boxes/greens): {stationary_pct:.1f}%")
        elif walking_pct > 2:
            print("POSSIBLE GOLF OR WALKING ACTIVITY")
            print(f"- Some walking detected: {walking_pct:.1f}%")
        else:
            print("UNLIKELY GOLF ACTIVITY")
            print(f"- Very little walking/golf pace movement: {walking_pct:.1f}%")
            print(f"- Data suggests: mostly stationary or in vehicle")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: analyze_morning_golf.py YYYY-MM-DD")
        sys.exit(1)

    date_str = sys.argv[1]
    sys.exit(analyze_morning_golf(date_str))
