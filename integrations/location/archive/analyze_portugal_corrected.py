#!/usr/bin/env python3
"""
Analyze Portugal trip with corrected golf times and specific locations.
October 19-24, 2025 - Algarve family holiday
"""

from owntracks_client import OwntracksClient
from datetime import datetime, timedelta
import math

# Key locations
LOCATIONS = {
    'Pine Cliffs Resort': (37.088, -8.174),
    'Pine Cliffs Golf': (37.093, -8.175),
    'Pingo Doce Vilamoura': (37.1040, -8.1266),
    'Armação de Pêra': (37.0999, -8.3551),
    'Faro Airport': (37.014, -7.966),
}

def distance_km(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers."""
    R = 6371  # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2) * math.sin(dlat/2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon/2) * math.sin(dlon/2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def identify_location(lat, lon, radius_km=0.5):
    """Identify which known location this point is near."""
    for name, (loc_lat, loc_lon) in LOCATIONS.items():
        dist = distance_km(lat, lon, loc_lat, loc_lon)
        if dist <= radius_km:
            return name, dist
    return None, None

def is_golf_velocity(velocity_kmh):
    """Golf cart/walking pace is typically 5-15 km/h."""
    return 3 <= velocity_kmh <= 20

def analyze_day(client, date_str, golf_start_hour=None, golf_duration_hours=2.5):
    """Analyze a single day with focus on golf timing and specific locations."""
    print(f"\n{'='*80}")
    print(f"CORRECTED ANALYSIS: {date_str}")
    print(f"{'='*80}")

    # Get all location data for the day
    result = client.get_locations_for_date('gavin-iphone', 'a2ea00bc-9862-4efb-a6ab-f038e32beb4c', date_str)

    if not result.get('success'):
        print(f"No location data for {date_str}")
        return

    locations = result.get('data', [])
    print(f"Retrieved {len(locations)} location points\n")

    # Track visits to specific locations
    location_visits = {name: [] for name in LOCATIONS.keys()}
    golf_periods = []

    # Analyze each location point
    for loc in locations:
        lat = loc.get('lat')
        lon = loc.get('lon')
        tst = loc.get('tst')
        vel = loc.get('vel', 0)

        if not all([lat, lon, tst]):
            continue

        timestamp = datetime.fromtimestamp(tst)
        velocity_kmh = vel * 3.6  # Convert m/s to km/h

        # Check proximity to known locations
        location_name, distance = identify_location(lat, lon, radius_km=0.5)

        if location_name:
            location_visits[location_name].append({
                'time': timestamp,
                'distance': distance,
                'velocity': velocity_kmh
            })

        # Detect potential golf activity (at golf course with appropriate velocity)
        if location_name == 'Pine Cliffs Golf' and is_golf_velocity(velocity_kmh):
            golf_periods.append({
                'time': timestamp,
                'velocity': velocity_kmh
            })

    # Summarize location visits
    print("LOCATION VISITS:")
    print("-" * 80)
    for name, visits in location_visits.items():
        if visits:
            times = [v['time'] for v in visits]
            start = min(times)
            end = max(times)
            duration_mins = (end - start).total_seconds() / 60

            print(f"\n{name}:")
            print(f"  First visit: {start.strftime('%H:%M')}")
            print(f"  Last visit: {end.strftime('%H:%M')}")
            print(f"  Duration: {duration_mins:.0f} minutes")
            print(f"  Data points: {len(visits)}")

    # Analyze golf activity
    if golf_periods:
        print(f"\n\nGOLF ACTIVITY DETECTED:")
        print("-" * 80)

        # Group golf points into continuous periods
        golf_sessions = []
        current_session = [golf_periods[0]]

        for i in range(1, len(golf_periods)):
            time_gap = (golf_periods[i]['time'] - current_session[-1]['time']).total_seconds() / 60

            if time_gap <= 15:  # Points within 15 minutes are same session
                current_session.append(golf_periods[i])
            else:
                if len(current_session) >= 5:  # At least 5 points to count as session
                    golf_sessions.append(current_session)
                current_session = [golf_periods[i]]

        if len(current_session) >= 5:
            golf_sessions.append(current_session)

        for idx, session in enumerate(golf_sessions, 1):
            start_time = session[0]['time']
            end_time = session[-1]['time']
            duration_mins = (end_time - start_time).total_seconds() / 60
            avg_velocity = sum(p['velocity'] for p in session) / len(session)

            print(f"\nSession {idx}:")
            print(f"  Start: {start_time.strftime('%H:%M')}")
            print(f"  End: {end_time.strftime('%H:%M')}")
            print(f"  Duration: {duration_mins:.0f} minutes ({duration_mins/60:.1f} hours)")
            print(f"  Avg velocity: {avg_velocity:.1f} km/h")
            print(f"  Data points: {len(session)}")

            # Check if this matches expected golf time
            if golf_start_hour:
                expected_start = start_time.replace(hour=golf_start_hour, minute=0)
                time_diff = abs((start_time - expected_start).total_seconds() / 60)
                if time_diff <= 90:
                    print(f"  ✓ MATCHES expected golf time (~{golf_start_hour}:00)")
                else:
                    print(f"  ? Time difference from expected: {time_diff:.0f} minutes")

    # Show hourly summary
    print(f"\n\nHOURLY ACTIVITY SUMMARY:")
    print("-" * 80)

    hourly_locations = {}
    for loc in locations:
        tst = loc.get('tst')
        if not tst:
            continue

        timestamp = datetime.fromtimestamp(tst)
        hour = timestamp.hour

        if hour not in hourly_locations:
            hourly_locations[hour] = []

        lat = loc.get('lat')
        lon = loc.get('lon')
        if lat and lon:
            location_name, _ = identify_location(lat, lon, radius_km=0.5)
            if location_name:
                hourly_locations[hour].append(location_name)

    for hour in sorted(hourly_locations.keys()):
        locations_this_hour = hourly_locations[hour]
        unique_locations = list(set(locations_this_hour))

        if unique_locations:
            print(f"{hour:02d}:00 - {', '.join(unique_locations)} ({len(locations_this_hour)} points)")

def main():
    """Analyze each day of the Portugal trip with corrections."""
    client = OwntracksClient(
        base_url="https://owntracks.gavinslater.co.uk"
    )

    # Corrected schedule
    schedule = [
        ('2025-10-19', None, 'Sunday - NO GOLF, Pingo Doce supermarket visit'),
        ('2025-10-20', 15, 'Monday - Golf AFTERNOON ~15:30 (2-2.5 hours)'),
        ('2025-10-21', 15, 'Tuesday - Armação de Pêra beach midday, Golf AFTERNOON ~15:00-15:15'),
        ('2025-10-22', 11, 'Wednesday - Golf LATE MORNING/MIDDAY ~11:00-12:00'),
        ('2025-10-23', 12, 'Thursday - Golf EARLY AFTERNOON ~12:00-13:00, Faro Airport ~17:00'),
        ('2025-10-24', 11, 'Friday - Golf just after 11:00am'),
    ]

    for date_str, golf_hour, description in schedule:
        print(f"\n{description}")
        analyze_day(client, date_str, golf_start_hour=golf_hour)
        print("\n" + "="*80)

if __name__ == '__main__':
    main()
