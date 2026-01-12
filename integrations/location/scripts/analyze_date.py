#!/usr/bin/env python3
"""
Daily Location Analysis Script
Analyzes a single day of location data using all Phase 4 specialized analyzers.

Usage:
    python3 analyze_date.py 2025-11-02
    python3 analyze_date.py 2025-11-02 --verbose
"""

import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.owntracks_client import OwntracksClient
from core.location_analyzer import LocationAnalyzer
from analyzers.golf_analyzer import GolfAnalyzer
from analyzers.parkrun_analyzer import ParkrunAnalyzer
from analyzers.commute_analyzer import CommuteAnalyzer
from analyzers.dog_walking_analyzer import DogWalkingAnalyzer
from analyzers.snowboarding_analyzer import SnowboardingAnalyzer


def setup_logging(verbose: bool = False):
    """Configure logging"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def analyze_date(date_str: str, user: str = 'gavin', device: str = 'iPhone', verbose: bool = False):
    """
    Analyze a single date using all available activity analyzers

    Args:
        date_str: Date in YYYY-MM-DD format
        user: Owntracks username
        device: Owntracks device name
        verbose: Enable verbose logging
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    # Validate date
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        day_name = date_obj.strftime('%A')
    except ValueError:
        logger.error(f"Invalid date format: {date_str}. Use YYYY-MM-DD")
        return 1

    logger.info(f"Analyzing {day_name}, {date_str}")
    print("=" * 70)
    print(f"Location Analysis: {day_name}, {date_str}")
    print("=" * 70)

    # Initialize components
    owntracks_client = OwntracksClient()
    location_analyzer = LocationAnalyzer()

    # Initialize all activity analyzers
    golf_analyzer = GolfAnalyzer()
    parkrun_analyzer = ParkrunAnalyzer()
    commute_analyzer = CommuteAnalyzer()
    dog_walking_analyzer = DogWalkingAnalyzer()
    snowboarding_analyzer = SnowboardingAnalyzer()

    # Get location data
    logger.info(f"Fetching location data for {date_str}...")
    response = owntracks_client.get_locations(
        user=user,
        device=device,
        from_date=date_str,
        to_date=date_str
    )

    if not response.get('success'):
        logger.error(f"Failed to get locations: {response.get('error')}")
        print(f"\n✗ Error: {response.get('error')}")
        return 1

    locations = response.get('data', [])
    logger.info(f"Retrieved {len(locations)} location points")

    if not locations:
        print("\n⚠️  No location data available for this date")
        return 0

    print(f"\n📍 Location Data: {len(locations)} points")

    # Get known locations
    known_locations = location_analyzer.get_all_locations()
    logger.info(f"Loaded {len(known_locations)} known locations")

    # Run all analyzers
    all_activities = []

    # 1. Golf
    print("\n🏌️  Analyzing golf activities...")
    golf_sessions = golf_analyzer.detect_sessions(locations)
    if golf_sessions:
        print(f"   ✓ Found {len(golf_sessions)} golf session(s)")
        all_activities.extend(golf_sessions)
    else:
        print("   - No golf activities detected")

    # 2. Parkrun
    print("\n🏃 Analyzing parkrun activities...")
    parkrun_sessions = parkrun_analyzer.detect_sessions(locations)
    if parkrun_sessions:
        print(f"   ✓ Found {len(parkrun_sessions)} parkrun(s)")
        all_activities.extend(parkrun_sessions)
    else:
        print("   - No parkrun activities detected")

    # 3. Commute
    print("\n🚆 Analyzing commute patterns...")
    commute_sessions = commute_analyzer.detect_sessions(locations, known_locations)
    if commute_sessions:
        print(f"   ✓ Found {len(commute_sessions)} commute(s)")
        all_activities.extend(commute_sessions)
    else:
        print("   - No commute activities detected")

    # 4. Dog Walking
    print("\n🐕 Analyzing dog walking activities...")
    dog_walking_sessions = dog_walking_analyzer.detect_sessions(locations, known_locations)
    if dog_walking_sessions:
        print(f"   ✓ Found {len(dog_walking_sessions)} dog walk(s)")
        all_activities.extend(dog_walking_sessions)
    else:
        print("   - No dog walking activities detected")

    # 5. Snowboarding
    print("\n🏂 Analyzing snowboarding activities...")
    snowboarding_sessions = snowboarding_analyzer.detect_sessions(locations, known_locations)
    if snowboarding_sessions:
        print(f"   ✓ Found {len(snowboarding_sessions)} snowboarding session(s)")
        all_activities.extend(snowboarding_sessions)
    else:
        print("   - No snowboarding activities detected")

    # Summary
    print("\n" + "=" * 70)
    print(f"Summary: {len(all_activities)} activit{'y' if len(all_activities) == 1 else 'ies'} detected")
    print("=" * 70)

    if all_activities:
        # Sort by start time
        all_activities.sort(key=lambda a: a.start_time)

        for i, activity in enumerate(all_activities, 1):
            duration_str = f"{activity.duration_hours:.1f}h" if activity.duration_hours >= 1 else f"{int(activity.duration_hours * 60)}m"

            print(f"\n{i}. {activity.activity_type.upper()}")
            print(f"   Location: {activity.location_name}")
            print(f"   Time: {activity.start_time.strftime('%H:%M')} - {activity.end_time.strftime('%H:%M')} ({duration_str})")
            print(f"   Confidence: {activity.confidence} ({activity.confidence_score:.2f})")

            # Activity-specific details
            if activity.activity_type == 'golf' and 'num_holes' in activity.details:
                print(f"   Holes: {activity.details['num_holes']}")
            elif activity.activity_type == 'parkrun' and 'distance_meters' in activity.details:
                print(f"   Distance: {activity.details['distance_meters']:.0f}m")
            elif activity.activity_type == 'commute' and 'direction' in activity.details:
                print(f"   Direction: {activity.details['direction']}")
            elif activity.activity_type == 'snowboarding' and 'num_runs' in activity.details:
                print(f"   Runs: {activity.details['num_runs']}, Vertical: {activity.details['total_vertical_meters']:.0f}m")
            elif activity.activity_type == 'dog_walking' and 'distance_meters' in activity.details:
                print(f"   Distance: {activity.details['distance_meters']:.0f}m")
    else:
        print("\nNo significant activities detected for this date.")

    print("\n" + "=" * 70)
    print("✓ Analysis complete")
    print("=" * 70)

    return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Analyze location data for a specific date using all activity analyzers'
    )
    parser.add_argument('date', help='Date to analyze (YYYY-MM-DD)')
    parser.add_argument('--user', default='gavin', help='Owntracks username (default: gavin)')
    parser.add_argument('--device', default='iPhone', help='Owntracks device (default: iPhone)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')

    args = parser.parse_args()

    try:
        return analyze_date(args.date, args.user, args.device, args.verbose)
    except KeyboardInterrupt:
        print("\n\nAnalysis cancelled by user")
        return 130
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n✗ Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
