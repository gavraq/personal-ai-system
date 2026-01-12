"""
Multi-Day Trip Analyzer
Analyzes entire trips to generate comprehensive activity summaries for journal entries.

Integrates:
- Phase 1: Dynamic Location Database Loading
- Phase 2: Golf Activity Analyzer
- Phase 4: Parkrun, Commute, Dog Walking, Snowboarding Analyzers
- Activity detection (golf, parkrun, commute, dog walking, snowboarding, supermarket, beach, airport, etc.)
- Daily summary generation
- Formatted output for Obsidian daily notes
"""

import json
from datetime import datetime, timedelta, time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
from pathlib import Path
import logging

from core.location_analyzer import LocationAnalyzer
from analyzers.golf_analyzer import GolfAnalyzer
from analyzers.parkrun_analyzer import ParkrunAnalyzer
from analyzers.commute_analyzer import CommuteAnalyzer
from analyzers.dog_walking_analyzer import DogWalkingAnalyzer
from analyzers.snowboarding_analyzer import SnowboardingAnalyzer
from core.owntracks_client import OwntracksClient
from analyzers.base_activity_analyzer import ActivitySession


@dataclass
class DailySummary:
    """Summary of activities for a single day"""
    date: str  # YYYY-MM-DD
    day_name: str  # Monday, Tuesday, etc.
    activities: List[ActivitySession]
    total_activities: int
    location_summary: str  # Human-readable summary

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'date': self.date,
            'day_name': self.day_name,
            'activities': [a.to_dict() for a in self.activities],
            'total_activities': self.total_activities,
            'location_summary': self.location_summary
        }


class TripAnalyzer:
    """Analyzes multi-day trips to detect and summarize activities"""

    def __init__(self, trip_name: str, user: str = 'gavin', device: str = 'iPhone'):
        """
        Initialize trip analyzer

        Args:
            trip_name: Name of trip (e.g., 'portugal_2025-10')
            user: Owntracks username
            device: Owntracks device name
        """
        self.trip_name = trip_name
        self.user = user
        self.device = device
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.location_analyzer = LocationAnalyzer()
        self.location_analyzer.load_trip(trip_name)

        # Initialize all activity analyzers
        self.golf_analyzer = GolfAnalyzer()
        self.parkrun_analyzer = ParkrunAnalyzer()
        self.commute_analyzer = CommuteAnalyzer()
        self.dog_walking_analyzer = DogWalkingAnalyzer()
        self.snowboarding_analyzer = SnowboardingAnalyzer()

        self.owntracks_client = OwntracksClient()

        # Get trip info
        if hasattr(self.location_analyzer, 'trip_info'):
            self.trip_info = self.location_analyzer.trip_info
        else:
            self.trip_info = {'name': trip_name}

        self.logger.info(f"TripAnalyzer initialized for: {self.trip_info.get('name', trip_name)}")

    def get_locations_for_date(self, date: str) -> List[Dict]:
        """
        Get location data for a specific date

        Args:
            date: Date string in YYYY-MM-DD format

        Returns:
            List of location records
        """
        response = self.owntracks_client.get_locations(
            user=self.user,
            device=self.device,
            from_date=date,
            to_date=date
        )

        if not response.get('success'):
            self.logger.warning(f"Failed to get locations for {date}: {response.get('error')}")
            return []

        return response.get('data', [])

    def detect_location_visits(self, locations: List[Dict], date: str) -> List[ActivitySession]:
        """
        Detect visits to known locations

        Args:
            locations: List of location records
            date: Date string YYYY-MM-DD

        Returns:
            List of activity detections
        """
        activities = []

        # Get all trip locations (excluding golf courses - handled separately)
        trip_locations = {
            loc_id: loc_info
            for loc_id, loc_info in self.location_analyzer.trip_locations.items()
            if loc_info.get('type') != 'golf_course'
        }

        for loc_id, loc_info in trip_locations.items():
            # Analyze time at this location
            time_analysis = self.location_analyzer.analyze_time_at_location(
                locations,
                loc_info['coordinates'],
                loc_info['radius'],
                min_duration_minutes=5  # 5 minutes minimum
            )

            if time_analysis.get('visit_count', 0) > 0:
                # Create activity for each visit
                for visit in time_analysis.get('visits', []):
                    duration_hours = visit['duration_minutes'] / 60

                    # Map location type to activity type
                    activity_type = self._map_location_type_to_activity(loc_info['type'])

                    # Determine confidence
                    confidence = 'CONFIRMED' if duration_hours >= 0.5 else 'MEDIUM'

                    activity = ActivitySession(
                        activity_type=activity_type,
                        start_time=visit['start_time'],
                        end_time=visit['end_time'],
                        duration_hours=duration_hours,
                        location_name=loc_info['name'],
                        location_coords=loc_info['coordinates'],
                        confidence=confidence,
                        confidence_score=1.0 if confidence == 'CONFIRMED' else 0.7,
                        details={
                            'date': date,  # Store date in details instead
                            'location_type': loc_info['type'],
                            'duration_minutes': visit['duration_minutes']
                        }
                    )

                    activities.append(activity)

        return activities

    def _map_location_type_to_activity(self, location_type: str) -> str:
        """Map location type to activity type"""
        mapping = {
            'supermarket': 'supermarket',
            'beach': 'beach',
            'airport': 'airport',
            'marina': 'excursion',
            'town': 'excursion',
            'resort_area': 'excursion',
            'accommodation': 'resort',
            'golf_course': 'golf'
        }
        return mapping.get(location_type, 'activity')

    def detect_golf_activities(self, locations: List[Dict], date: str) -> List[ActivitySession]:
        """
        Detect golf activities for a day

        Args:
            locations: List of location records
            date: Date string YYYY-MM-DD

        Returns:
            List of golf activity sessions
        """
        # Get golf course location if available
        golf_course = None
        for loc_id, loc_info in self.location_analyzer.trip_locations.items():
            if loc_info.get('type') == 'golf_course':
                golf_course = {
                    'name': loc_info['name'],
                    'coordinates': loc_info['coordinates'],
                    'radius': loc_info['radius']
                }
                break

        # Detect golf sessions (returns List[ActivitySession])
        golf_sessions = self.golf_analyzer.detect_sessions(
            locations,
            golf_course_location=golf_course
        )

        # Add date to details for each session
        for session in golf_sessions:
            session.details['date'] = date

        return golf_sessions

    def detect_parkrun_activities(self, locations: List[Dict], date: str) -> List[ActivitySession]:
        """
        Detect parkrun activities (Saturday morning 5km runs)

        Args:
            locations: List of location records
            date: Date string YYYY-MM-DD

        Returns:
            List of parkrun activity sessions
        """
        # Get parkrun location if available
        parkrun_location = None
        for loc_id, loc_info in self.location_analyzer.get_all_locations().items():
            if loc_info.get('type') == 'parkrun':
                parkrun_location = {
                    'name': loc_info['name'],
                    'coordinates': loc_info['coordinates']
                }
                break

        # Detect parkrun sessions
        parkrun_sessions = self.parkrun_analyzer.detect_sessions(
            locations,
            parkrun_location=parkrun_location
        )

        for session in parkrun_sessions:
            session.details['date'] = date

        return parkrun_sessions

    def detect_commute_activities(self, locations: List[Dict], date: str) -> List[ActivitySession]:
        """
        Detect commute activities (Esher ↔ London)

        Args:
            locations: List of location records
            date: Date string YYYY-MM-DD

        Returns:
            List of commute activity sessions
        """
        # Get known locations for commute analysis
        known_locations = self.location_analyzer.get_all_locations()

        # Detect commute sessions
        commute_sessions = self.commute_analyzer.detect_sessions(
            locations,
            known_locations=known_locations
        )

        for session in commute_sessions:
            session.details['date'] = date

        return commute_sessions

    def detect_dog_walking_activities(self, locations: List[Dict], date: str) -> List[ActivitySession]:
        """
        Detect dog walking activities (local walks around Esher)

        Args:
            locations: List of location records
            date: Date string YYYY-MM-DD

        Returns:
            List of dog walking activity sessions
        """
        # Get known locations for dog walking analysis
        known_locations = self.location_analyzer.get_all_locations()

        # Detect dog walking sessions
        dog_walking_sessions = self.dog_walking_analyzer.detect_sessions(
            locations,
            known_locations=known_locations
        )

        for session in dog_walking_sessions:
            session.details['date'] = date

        return dog_walking_sessions

    def detect_snowboarding_activities(self, locations: List[Dict], date: str) -> List[ActivitySession]:
        """
        Detect snowboarding activities (ski resort sessions with altitude data)

        Args:
            locations: List of location records
            date: Date string YYYY-MM-DD

        Returns:
            List of snowboarding activity sessions
        """
        # Get known locations for snowboarding analysis
        known_locations = self.location_analyzer.get_all_locations()

        # Detect snowboarding sessions
        snowboarding_sessions = self.snowboarding_analyzer.detect_sessions(
            locations,
            known_locations=known_locations
        )

        for session in snowboarding_sessions:
            session.details['date'] = date

        return snowboarding_sessions

    def detect_flight(self, locations: List[Dict], date: str) -> Optional[ActivitySession]:
        """
        Detect flight activity (high altitude + high speed)

        Args:
            locations: List of location records
            date: Date string YYYY-MM-DD

        Returns:
            Flight activity session or None
        """
        if not locations:
            return None

        # Look for high altitude (>5000m) and high velocity (>200 m/s)
        flight_points = []
        for loc in locations:
            altitude = loc.get('alt', 0)
            velocity = loc.get('vel', 0)  # Velocity in km/h typically

            # Convert velocity to m/s if in km/h
            velocity_ms = velocity / 3.6 if velocity > 100 else velocity

            if altitude > 5000 and velocity_ms > 200:
                flight_points.append(loc)

        if len(flight_points) >= 10:  # At least 10 points indicate flight
            # Get flight start and end
            sorted_points = sorted(flight_points, key=lambda x: x.get('tst', 0))
            start_point = sorted_points[0]
            end_point = sorted_points[-1]

            start_time = datetime.fromtimestamp(start_point.get('tst', 0))
            end_time = datetime.fromtimestamp(end_point.get('tst', 0))
            duration_hours = (end_time - start_time).total_seconds() / 3600

            # Try to determine destination
            dest_coords = (end_point.get('lat'), end_point.get('lon'))
            dest_name = "Unknown destination"

            # Check if near known airport
            for loc_id, loc_info in self.location_analyzer.known_locations.items():
                if loc_info.get('type') == 'airport':
                    distance = self.location_analyzer.calculate_distance(
                        dest_coords,
                        loc_info['coordinates']
                    )
                    if distance <= 10000:  # Within 10km
                        dest_name = loc_info['name']
                        break

            activity = ActivitySession(
                activity_type='flight',
                start_time=start_time,
                end_time=end_time,
                duration_hours=duration_hours,
                location_name=dest_name,
                location_coords=dest_coords,
                confidence='CONFIRMED',
                confidence_score=1.0,
                details={
                    'date': date,
                    'max_altitude_m': max(p.get('alt', 0) for p in flight_points),
                    'flight_points': len(flight_points)
                }
            )

            return activity

        return None

    def analyze_day(self, date: str) -> DailySummary:
        """
        Analyze a single day of the trip

        Args:
            date: Date string in YYYY-MM-DD format

        Returns:
            Daily summary with detected activities
        """
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        day_name = date_obj.strftime('%A')

        self.logger.info(f"Analyzing {day_name} {date}")

        # Get location data
        locations = self.get_locations_for_date(date)

        if not locations:
            self.logger.warning(f"No location data for {date}")
            return DailySummary(
                date=date,
                day_name=day_name,
                activities=[],
                total_activities=0,
                location_summary="No location data available"
            )

        # Detect activities
        activities = []

        # 1. Check for flight
        flight = self.detect_flight(locations, date)
        if flight:
            activities.append(flight)

        # 2. Detect golf
        golf_activities = self.detect_golf_activities(locations, date)
        activities.extend(golf_activities)

        # 3. Detect parkrun (Saturday morning runs)
        parkrun_activities = self.detect_parkrun_activities(locations, date)
        activities.extend(parkrun_activities)

        # 4. Detect commute (if not on trip - typically UK-based)
        commute_activities = self.detect_commute_activities(locations, date)
        activities.extend(commute_activities)

        # 5. Detect dog walking (local walks)
        dog_walking_activities = self.detect_dog_walking_activities(locations, date)
        activities.extend(dog_walking_activities)

        # 6. Detect snowboarding (winter sports)
        snowboarding_activities = self.detect_snowboarding_activities(locations, date)
        activities.extend(snowboarding_activities)

        # 7. Detect location visits (supermarkets, beaches, etc.)
        location_activities = self.detect_location_visits(locations, date)
        activities.extend(location_activities)

        # Sort by start time
        activities.sort(key=lambda a: a.start_time)

        # Generate location summary
        location_summary = self._generate_location_summary(activities)

        return DailySummary(
            date=date,
            day_name=day_name,
            activities=activities,
            total_activities=len(activities),
            location_summary=location_summary
        )

    def _generate_location_summary(self, activities: List[ActivitySession]) -> str:
        """Generate human-readable location summary"""
        if not activities:
            return "No significant activities detected"

        summary_parts = []
        for activity in activities:
            time_range = f"{activity.start_time.strftime('%H:%M')}-{activity.end_time.strftime('%H:%M')}"
            summary_parts.append(f"{activity.activity_type.title()} at {activity.location_name} ({time_range})")

        return "; ".join(summary_parts)

    def analyze_trip(self, start_date: str, end_date: str) -> Dict:
        """
        Analyze entire trip from start to end date

        Args:
            start_date: Start date YYYY-MM-DD
            end_date: End date YYYY-MM-DD

        Returns:
            Complete trip analysis dictionary
        """
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')

        self.logger.info(f"Analyzing trip: {start_date} to {end_date}")

        daily_summaries = []
        current = start

        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            summary = self.analyze_day(date_str)
            daily_summaries.append(summary)
            current += timedelta(days=1)

        # Generate trip statistics
        total_activities = sum(s.total_activities for s in daily_summaries)
        activity_types = defaultdict(int)

        for summary in daily_summaries:
            for activity in summary.activities:
                activity_types[activity.activity_type] += 1

        trip_analysis = {
            'trip_info': self.trip_info,
            'analysis_period': {
                'start_date': start_date,
                'end_date': end_date,
                'days': (end - start).days + 1
            },
            'statistics': {
                'total_activities': total_activities,
                'activity_breakdown': dict(activity_types)
            },
            'daily_summaries': [s.to_dict() for s in daily_summaries]
        }

        return trip_analysis

    def format_for_daily_note(self, date: str, summary: DailySummary) -> str:
        """
        Format daily summary for Obsidian daily note

        Args:
            date: Date string YYYY-MM-DD
            summary: Daily summary object

        Returns:
            Markdown formatted text for daily note
        """
        lines = []
        lines.append(f"## Location Activities - {summary.day_name}")
        lines.append("")

        if not summary.activities:
            lines.append("*No significant activities detected*")
            return "\n".join(lines)

        for activity in summary.activities:
            # Format based on activity type
            if activity.activity_type == 'golf':
                lines.append(self._format_golf_activity(activity))
            elif activity.activity_type == 'flight':
                lines.append(self._format_flight_activity(activity))
            else:
                lines.append(self._format_general_activity(activity))

            lines.append("")

        return "\n".join(lines)

    def _format_golf_activity(self, activity: ActivitySession) -> str:
        """Format golf activity for daily note"""
        time_range = f"{activity.start_time.strftime('%H:%M')}-{activity.end_time.strftime('%H:%M')}"
        holes = activity.details.get('estimated_holes', '?')
        distance = activity.details.get('total_distance_km', 0)

        lines = []
        lines.append(f"**Golf at {activity.location_name}** ({time_range})")
        lines.append(f"- Duration: {activity.duration_hours:.1f} hours")
        lines.append(f"- Estimated holes: {holes}")
        lines.append(f"- Distance: {distance:.2f} km")
        lines.append(f"- Confidence: {activity.confidence}")

        return "\n".join(lines)

    def _format_flight_activity(self, activity: ActivitySession) -> str:
        """Format flight activity for daily note"""
        time_range = f"{activity.start_time.strftime('%H:%M')}-{activity.end_time.strftime('%H:%M')}"
        altitude = activity.details.get('max_altitude_m', 0)

        lines = []
        lines.append(f"**Flight to {activity.location_name}** ({time_range})")
        lines.append(f"- Duration: {activity.duration_hours:.1f} hours")
        lines.append(f"- Max altitude: {altitude:.0f}m ({altitude*3.28084:.0f} feet)")

        return "\n".join(lines)

    def _format_general_activity(self, activity: ActivitySession) -> str:
        """Format general activity for daily note"""
        time_range = f"{activity.start_time.strftime('%H:%M')}-{activity.end_time.strftime('%H:%M')}"

        lines = []
        lines.append(f"**{activity.activity_type.title()} - {activity.location_name}** ({time_range})")
        lines.append(f"- Duration: {activity.duration_hours:.1f} hours")

        return "\n".join(lines)


def create_trip_analyzer(trip_name: str) -> TripAnalyzer:
    """
    Factory function to create TripAnalyzer

    Args:
        trip_name: Name of trip JSON file (e.g., 'portugal_2025-10')

    Returns:
        Configured TripAnalyzer instance
    """
    return TripAnalyzer(trip_name)


if __name__ == "__main__":
    # Basic test
    print("Trip Analyzer module loaded successfully")
    print("\nUsage:")
    print("  analyzer = TripAnalyzer('portugal_2025-10')")
    print("  analysis = analyzer.analyze_trip('2025-10-18', '2025-10-25')")
