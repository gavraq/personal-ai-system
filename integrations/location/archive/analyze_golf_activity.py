#!/usr/bin/env python3
"""
Golf activity analyzer - looks for golf course visits and golf play patterns
"""

import sys
import json
import math
from datetime import datetime, timedelta
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

def analyze_golf_activity(date_str, golf_course_lat=None, golf_course_lon=None, course_radius=500):
    """
    Analyze location data for golf activity patterns

    Args:
        date_str: Date in YYYY-MM-DD format
        golf_course_lat: Latitude of golf course (optional)
        golf_course_lon: Longitude of golf course (optional)
        course_radius: Search radius in meters (default 500m)
    """

    # Configuration
    base_url = "https://owntracks.gavinslater.co.uk"
    user = 'gavin-iphone'
    device = 'a2ea00bc-9862-4efb-a6ab-f038e32beb4c'

    # Initialize client
    client = OwntracksClient(base_url)

    print(f"Analyzing golf activity for {date_str}")
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

        # Calculate center point of all locations (likely resort center)
        avg_lat = sum(loc.get('lat', 0) for loc in locations) / len(locations)
        avg_lon = sum(loc.get('lon', 0) for loc in locations) / len(locations)

        print(f"Location Center Point (likely resort): {avg_lat:.6f}, {avg_lon:.6f}\n")

        # Analyze movement patterns
        print("DETAILED TIMELINE WITH MOVEMENT ANALYSIS:")
        print("-" * 80)

        golf_periods = []
        current_period_start = None
        current_period_locations = []

        for i, loc in enumerate(locations):
            timestamp = datetime.fromtimestamp(loc['tst'])
            lat = loc.get('lat', 0)
            lon = loc.get('lon', 0)
            vel = loc.get('vel', 0)  # velocity in m/s

            # Calculate distance from center
            dist_from_center = calculate_distance(avg_lat, avg_lon, lat, lon)

            # Golf play velocity range: 0.5-2 m/s (walking between shots)
            # with stationary periods at tee boxes/greens
            is_golf_velocity = 0.5 <= vel <= 2.5 or vel < 0.5

            # Check if potentially at golf course (if coordinates provided)
            at_golf_course = False
            if golf_course_lat and golf_course_lon:
                dist_from_course = calculate_distance(lat, lon, golf_course_lat, golf_course_lon)
                at_golf_course = dist_from_course < course_radius

            # Print every 10th point to avoid overwhelming output
            if i % 10 == 0 or is_golf_velocity:
                vel_kmh = vel * 3.6
                status = ""
                if vel < 0.5:
                    status = "STATIONARY (tee box/green?)"
                elif 0.5 <= vel <= 2.5:
                    status = "WALKING (golf pace)"
                elif vel > 4:
                    status = "CYCLING/DRIVING"
                else:
                    status = "Normal walking"

                print(f"{timestamp.strftime('%H:%M:%S')} | "
                      f"Lat: {lat:.6f}, Lon: {lon:.6f} | "
                      f"Vel: {vel:.1f} m/s ({vel_kmh:.1f} km/h) | "
                      f"{status}")

                if at_golf_course:
                    print(f"    → AT GOLF COURSE (within {course_radius}m)")

            # Track golf-like periods (walking pace or stationary, away from center)
            if is_golf_velocity and dist_from_center > 100:  # More than 100m from resort center
                if not current_period_start:
                    current_period_start = timestamp
                current_period_locations.append(loc)
            else:
                if current_period_start and len(current_period_locations) > 5:
                    # End of potential golf period
                    duration = (timestamp - current_period_start).total_seconds()
                    if duration > 600:  # At least 10 minutes
                        golf_periods.append({
                            'start': current_period_start,
                            'end': timestamp,
                            'duration': duration,
                            'locations': current_period_locations
                        })
                current_period_start = None
                current_period_locations = []

        # Summary of potential golf periods
        print("\n" + "=" * 80)
        print("POTENTIAL GOLF ACTIVITY PERIODS:")
        print("-" * 80)

        if golf_periods:
            for i, period in enumerate(golf_periods, 1):
                print(f"\nPeriod {i}:")
                print(f"  Time: {period['start'].strftime('%H:%M')} - {period['end'].strftime('%H:%M')}")
                print(f"  Duration: {format_duration(period['duration'])}")
                print(f"  Location points: {len(period['locations'])}")

                # Calculate average velocity during period
                avg_vel = sum(loc.get('vel', 0) for loc in period['locations']) / len(period['locations'])
                avg_vel_kmh = avg_vel * 3.6
                print(f"  Average velocity: {avg_vel:.1f} m/s ({avg_vel_kmh:.1f} km/h)")

                # Calculate distance covered
                total_distance = 0
                for j in range(len(period['locations']) - 1):
                    loc1 = period['locations'][j]
                    loc2 = period['locations'][j + 1]
                    total_distance += calculate_distance(
                        loc1.get('lat', 0), loc1.get('lon', 0),
                        loc2.get('lat', 0), loc2.get('lon', 0)
                    )
                print(f"  Distance covered: {total_distance:.0f} meters")

                # Get coordinate bounds
                lats = [loc.get('lat', 0) for loc in period['locations']]
                lons = [loc.get('lon', 0) for loc in period['locations']]
                print(f"  Latitude range: {min(lats):.6f} to {max(lats):.6f}")
                print(f"  Longitude range: {min(lons):.6f} to {max(lons):.6f}")
                print(f"  Area center: {sum(lats)/len(lats):.6f}, {sum(lons)/len(lons):.6f}")

                # Assess likelihood of golf
                likelihood = "UNKNOWN"
                if 1200 < period['duration'] < 10800:  # 20 min - 3 hours
                    if 0.8 <= avg_vel <= 2.0:  # Golf walking pace
                        if 500 < total_distance < 3000:  # Reasonable distance for 9 holes
                            likelihood = "HIGH - likely golf activity"
                        else:
                            likelihood = "MEDIUM - walking pace but unusual distance"
                    else:
                        likelihood = "LOW - velocity not consistent with golf"
                else:
                    likelihood = "LOW - duration not typical for golf"

                print(f"  Golf likelihood: {likelihood}")
        else:
            print("No potential golf activity periods detected")
            print("\nThis could mean:")
            print("- No golf was played")
            print("- GPS was turned off during golf")
            print("- Activity was classified differently (e.g., running)")

        # Velocity distribution analysis
        print("\n" + "=" * 80)
        print("VELOCITY DISTRIBUTION:")
        print("-" * 80)

        velocity_buckets = {
            'Stationary (<0.5 m/s)': 0,
            'Walking/Golf pace (0.5-2.5 m/s)': 0,
            'Running (2.5-4 m/s)': 0,
            'Cycling (4-8 m/s)': 0,
            'Driving (>8 m/s)': 0
        }

        for loc in locations:
            vel = loc.get('vel', 0)
            if vel < 0.5:
                velocity_buckets['Stationary (<0.5 m/s)'] += 1
            elif vel < 2.5:
                velocity_buckets['Walking/Golf pace (0.5-2.5 m/s)'] += 1
            elif vel < 4:
                velocity_buckets['Running (2.5-4 m/s)'] += 1
            elif vel < 8:
                velocity_buckets['Cycling (4-8 m/s)'] += 1
            else:
                velocity_buckets['Driving (>8 m/s)'] += 1

        for category, count in velocity_buckets.items():
            percentage = (count / len(locations)) * 100
            print(f"{category}: {count} points ({percentage:.1f}%)")

        return 0

    except Exception as e:
        print(f"Error analyzing golf activity: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: analyze_golf_activity.py YYYY-MM-DD [golf_lat] [golf_lon] [radius_meters]")
        print("Example: analyze_golf_activity.py 2025-10-19 37.0892 -8.3480 500")
        sys.exit(1)

    date_str = sys.argv[1]
    golf_lat = float(sys.argv[2]) if len(sys.argv) > 2 else None
    golf_lon = float(sys.argv[3]) if len(sys.argv) > 3 else None
    radius = int(sys.argv[4]) if len(sys.argv) > 4 else 500

    sys.exit(analyze_golf_activity(date_str, golf_lat, golf_lon, radius))
