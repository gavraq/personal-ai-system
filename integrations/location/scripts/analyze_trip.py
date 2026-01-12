#!/usr/bin/env python3
"""
Command-Line Interface for Trip Analyzer
Usage: python3 analyze_trip.py START_DATE END_DATE --trip TRIP_NAME [OPTIONS]

Examples:
  python3 analyze_trip.py 2025-10-18 2025-10-25 --trip portugal_2025-10
  python3 analyze_trip.py 2025-10-18 2025-10-25 --trip portugal_2025-10 --output json
  python3 analyze_trip.py 2025-10-20 2025-10-20 --trip portugal_2025-10 --format daily-note
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzers.trip_analyzer import TripAnalyzer


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Analyze multi-day trips to detect and summarize activities',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze full Portugal trip
  %(prog)s 2025-10-18 2025-10-25 --trip portugal_2025-10

  # Analyze single day
  %(prog)s 2025-10-20 2025-10-20 --trip portugal_2025-10

  # Output as JSON
  %(prog)s 2025-10-18 2025-10-25 --trip portugal_2025-10 --output json

  # Format for daily note
  %(prog)s 2025-10-20 2025-10-20 --trip portugal_2025-10 --format daily-note

  # Save to file
  %(prog)s 2025-10-18 2025-10-25 --trip portugal_2025-10 --save analysis.json
        """
    )

    parser.add_argument(
        'start_date',
        type=str,
        help='Start date in YYYY-MM-DD format'
    )

    parser.add_argument(
        'end_date',
        type=str,
        help='End date in YYYY-MM-DD format'
    )

    parser.add_argument(
        '--trip',
        type=str,
        required=True,
        help='Trip name (e.g., portugal_2025-10)'
    )

    parser.add_argument(
        '--output',
        type=str,
        choices=['summary', 'json', 'detailed'],
        default='summary',
        help='Output format (default: summary)'
    )

    parser.add_argument(
        '--format',
        type=str,
        choices=['daily-note', 'markdown'],
        help='Format output for daily notes or markdown'
    )

    parser.add_argument(
        '--save',
        type=str,
        metavar='FILE',
        help='Save output to file'
    )

    parser.add_argument(
        '--user',
        type=str,
        default='gavin',
        help='Owntracks username (default: gavin)'
    )

    parser.add_argument(
        '--device',
        type=str,
        default='iPhone',
        help='Owntracks device name (default: iPhone)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    return parser.parse_args()


def validate_date(date_str: str) -> bool:
    """Validate date string format"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def print_summary_output(analysis: dict):
    """Print summary output format"""
    print("\n" + "=" * 70)
    print(f"TRIP ANALYSIS: {analysis['trip_info'].get('name', 'Unknown Trip')}")
    print("=" * 70)

    period = analysis['analysis_period']
    print(f"\nPeriod: {period['start_date']} to {period['end_date']} ({period['days']} days)")

    stats = analysis['statistics']
    print(f"\nTotal Activities: {stats['total_activities']}")
    print("\nActivity Breakdown:")
    for activity_type, count in sorted(stats['activity_breakdown'].items()):
        print(f"  {activity_type.title()}: {count}")

    print("\n" + "-" * 70)
    print("DAILY SUMMARIES")
    print("-" * 70)

    for day_summary in analysis['daily_summaries']:
        print(f"\n{day_summary['day_name']}, {day_summary['date']}")
        print(f"Activities: {day_summary['total_activities']}")

        if day_summary['activities']:
            for activity in day_summary['activities']:
                start_time = datetime.fromisoformat(activity['start_time']).strftime('%H:%M')
                end_time = datetime.fromisoformat(activity['end_time']).strftime('%H:%M')
                print(f"  • {activity['activity_type'].title()}: {activity['location']['name']}")
                print(f"    Time: {start_time}-{end_time} ({activity['duration_hours']:.1f}h)")
                print(f"    Confidence: {activity['confidence']}")
        else:
            print("  No significant activities detected")


def print_detailed_output(analysis: dict):
    """Print detailed output with full activity information"""
    print_summary_output(analysis)

    print("\n" + "=" * 70)
    print("DETAILED ACTIVITY INFORMATION")
    print("=" * 70)

    for day_summary in analysis['daily_summaries']:
        if not day_summary['activities']:
            continue

        print(f"\n{day_summary['day_name']}, {day_summary['date']}")
        print("-" * 70)

        for i, activity in enumerate(day_summary['activities'], 1):
            print(f"\nActivity {i}: {activity['activity_type'].title()}")
            print(f"  Location: {activity['location']['name']}")
            print(f"  Coordinates: {activity['location']['coordinates']}")
            start_time = datetime.fromisoformat(activity['start_time']).strftime('%H:%M:%S')
            end_time = datetime.fromisoformat(activity['end_time']).strftime('%H:%M:%S')
            print(f"  Time: {start_time} - {end_time}")
            print(f"  Duration: {activity['duration_hours']:.2f} hours")
            print(f"  Confidence: {activity['confidence']}")

            if activity['details']:
                print(f"  Details:")
                for key, value in activity['details'].items():
                    if key != 'confidence_factors':  # Skip complex nested structure
                        print(f"    {key}: {value}")


def print_daily_note_format(analysis: dict, analyzer: TripAnalyzer):
    """Print output formatted for daily notes"""
    for day_summary_dict in analysis['daily_summaries']:
        # Convert dict back to DailySummary object structure
        from analyzers.trip_analyzer import DailySummary
        from analyzers.base_activity_analyzer import ActivitySession

        activities = []
        for act_dict in day_summary_dict['activities']:
            activity = ActivitySession(
                activity_type=act_dict['activity_type'],
                start_time=datetime.fromisoformat(act_dict['start_time']),
                end_time=datetime.fromisoformat(act_dict['end_time']),
                duration_hours=act_dict['duration_hours'],
                location_name=act_dict['location']['name'],
                location_coords=tuple(act_dict['location']['coordinates']),
                confidence=act_dict['confidence'],
                confidence_score=act_dict.get('confidence_score', 0.5),
                details=act_dict['details']
            )
            activities.append(activity)

        summary = DailySummary(
            date=day_summary_dict['date'],
            day_name=day_summary_dict['day_name'],
            activities=activities,
            total_activities=day_summary_dict['total_activities'],
            location_summary=day_summary_dict['location_summary']
        )

        formatted = analyzer.format_for_daily_note(day_summary_dict['date'], summary)
        print("\n" + "=" * 70)
        print(f"DAILY NOTE: {day_summary_dict['date']}")
        print("=" * 70)
        print(formatted)
        print()


def main():
    """Main entry point"""
    args = parse_arguments()

    # Validate dates
    if not validate_date(args.start_date):
        print(f"Error: Invalid start date '{args.start_date}'. Use YYYY-MM-DD format.", file=sys.stderr)
        return 1

    if not validate_date(args.end_date):
        print(f"Error: Invalid end date '{args.end_date}'. Use YYYY-MM-DD format.", file=sys.stderr)
        return 1

    # Check date order
    start = datetime.strptime(args.start_date, '%Y-%m-%d')
    end = datetime.strptime(args.end_date, '%Y-%m-%d')

    if end < start:
        print(f"Error: End date must be after start date.", file=sys.stderr)
        return 1

    # Initialize analyzer
    try:
        print(f"Initializing trip analyzer for '{args.trip}'...", file=sys.stderr)
        analyzer = TripAnalyzer(args.trip, user=args.user, device=args.device)
    except Exception as e:
        print(f"Error initializing analyzer: {e}", file=sys.stderr)
        return 1

    # Analyze trip
    try:
        print(f"Analyzing trip from {args.start_date} to {args.end_date}...", file=sys.stderr)
        analysis = analyzer.analyze_trip(args.start_date, args.end_date)
    except Exception as e:
        print(f"Error analyzing trip: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

    # Output results
    output_text = None

    if args.format == 'daily-note':
        print_daily_note_format(analysis, analyzer)
    elif args.output == 'json':
        output_text = json.dumps(analysis, indent=2)
        print(output_text)
    elif args.output == 'detailed':
        print_detailed_output(analysis)
    else:  # summary
        print_summary_output(analysis)

    # Save to file if requested
    if args.save:
        try:
            output_path = Path(args.save)

            if args.output == 'json' or output_path.suffix == '.json':
                with open(output_path, 'w') as f:
                    json.dump(analysis, f, indent=2)
            else:
                # Save whatever was printed
                if output_text is None:
                    print(f"Warning: Cannot save non-JSON output to file in current implementation", file=sys.stderr)
                else:
                    with open(output_path, 'w') as f:
                        f.write(output_text)

            print(f"\n✓ Saved to {output_path}", file=sys.stderr)

        except Exception as e:
            print(f"Error saving to file: {e}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
