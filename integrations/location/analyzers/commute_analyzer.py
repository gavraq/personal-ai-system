"""
Commute Activity Analyzer
Specialized analyzer for detecting daily commute patterns from location data.

Detects Gavin's typical commute pattern:
- Morning: Home (Esher) → Esher Station → Waterloo → Office (London)
- Evening: Office → Waterloo → Esher Station → Home
- Weekday timing: 06:00-10:00 (morning), 16:00-20:00 (evening)
- Train velocity detection: 10-40 m/s
- Known route locations validation

Extends BaseActivityAnalyzer for configuration-driven behavior.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
from geopy.distance import geodesic

from .base_activity_analyzer import BaseActivityAnalyzer, ActivitySession


@dataclass
class LocationVisit:
    """Represents a visit to a specific location during commute"""
    location_name: str
    location_coords: Tuple[float, float]
    arrival_time: datetime
    departure_time: datetime
    duration_seconds: float


class CommuteAnalyzer(BaseActivityAnalyzer):
    """Analyzes location data to detect and characterize commute activities"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize commute analyzer

        Args:
            config_path: Optional path to configuration file
        """
        super().__init__(config_path)
        self.logger = logging.getLogger(__name__)

        # Load configuration values
        self.expected_locations = self.get_config_value('expected_locations',
            ['home-esher', 'esher-station', 'waterloo-station', 'icbc-office-london'])

        self.expected_days = self.get_config_value('expected_days',
            ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])

        morning_window = self.get_config_value('morning_window', ['06:00', '10:00'])
        self.morning_start = datetime.strptime(morning_window[0], '%H:%M').time()
        self.morning_end = datetime.strptime(morning_window[1], '%H:%M').time()

        evening_window = self.get_config_value('evening_window', ['16:00', '20:00'])
        self.evening_start = datetime.strptime(evening_window[0], '%H:%M').time()
        self.evening_end = datetime.strptime(evening_window[1], '%H:%M').time()

        train_velocity = self.get_config_value('train_velocity_range_mps', [10.0, 40.0])
        self.train_velocity_min = train_velocity[0]
        self.train_velocity_max = train_velocity[1]

        walking_velocity = self.get_config_value('walking_velocity_range_mps', [0.5, 2.5])
        self.walking_min = walking_velocity[0]
        self.walking_max = walking_velocity[1]

        self.min_duration_minutes = self.get_config_value('min_commute_duration_minutes', 30)
        self.max_duration_minutes = self.get_config_value('max_commute_duration_minutes', 180)
        self.session_gap_minutes = self.get_gap_tolerance()

    def _get_activity_type(self) -> str:
        """Return the activity type string"""
        return 'commute'

    def identify_location_visits(self, locations: List[Dict],
                                 known_locations: Dict) -> List[LocationVisit]:
        """
        Identify visits to known locations during the time period

        Args:
            locations: List of location records
            known_locations: Dictionary of known locations

        Returns:
            List of location visits
        """
        visits = []

        for loc_id in self.expected_locations:
            if loc_id not in known_locations:
                continue

            loc_info = known_locations[loc_id]

            # Analyze time at this location
            time_analysis = self.location_analyzer.analyze_time_at_location(
                locations,
                loc_info['coordinates'],
                loc_info.get('radius', 100),
                min_duration_minutes=1  # Very short stays count for commute
            )

            if time_analysis.get('visit_count', 0) > 0:
                for visit in time_analysis.get('visits', []):
                    visit_obj = LocationVisit(
                        location_name=loc_info['name'],
                        location_coords=loc_info['coordinates'],
                        arrival_time=visit['start_time'],
                        departure_time=visit['end_time'],
                        duration_seconds=visit['duration_minutes'] * 60
                    )
                    visits.append(visit_obj)

        # Sort by arrival time
        visits.sort(key=lambda v: v.arrival_time)
        return visits

    def detect_train_segments(self, locations: List[Dict]) -> List[Dict]:
        """
        Detect train journey segments based on velocity

        Args:
            locations: List of location records

        Returns:
            List of train segment dicts
        """
        train_segments = []

        for i in range(len(locations) - 1):
            loc1 = locations[i]
            loc2 = locations[i + 1]

            # Extract coordinates
            coords1 = (loc1.get('lat'), loc1.get('lon'))
            coords2 = (loc2.get('lat'), loc2.get('lon'))

            if None in coords1 or None in coords2:
                continue

            # Extract timestamps
            time1 = self.parse_timestamp(loc1.get('tst'))
            time2 = self.parse_timestamp(loc2.get('tst'))

            if not time1 or not time2:
                continue

            # Calculate velocity
            distance = geodesic(coords1, coords2).meters
            duration = (time2 - time1).total_seconds()

            if duration <= 0:
                continue

            velocity = distance / duration

            # Check if train velocity
            if self.train_velocity_min <= velocity <= self.train_velocity_max:
                train_segments.append({
                    'start_time': time1,
                    'end_time': time2,
                    'velocity_mps': velocity,
                    'distance_meters': distance
                })

        return train_segments

    def classify_commute_direction(self, visits: List[LocationVisit],
                                   start_time: datetime) -> str:
        """
        Classify commute direction based on location sequence

        Args:
            visits: List of location visits
            start_time: Start time of commute

        Returns:
            Direction: 'to_office', 'from_office', or 'unknown'
        """
        if not visits:
            return 'unknown'

        # Check time of day
        start_hour = start_time.hour

        # Morning commute (to office)
        if 6 <= start_hour < 12:
            # Expected sequence: home → station → waterloo → office
            if len(visits) >= 2:
                first_loc = visits[0].location_name.lower()
                last_loc = visits[-1].location_name.lower()

                if 'esher' in first_loc or 'home' in first_loc:
                    if 'office' in last_loc or 'london' in last_loc or 'icbc' in last_loc:
                        return 'to_office'

        # Evening commute (from office)
        elif 16 <= start_hour < 22:
            # Expected sequence: office → waterloo → station → home
            if len(visits) >= 2:
                first_loc = visits[0].location_name.lower()
                last_loc = visits[-1].location_name.lower()

                if 'office' in first_loc or 'london' in first_loc or 'icbc' in first_loc:
                    if 'esher' in last_loc or 'home' in last_loc:
                        return 'from_office'

        return 'unknown'

    def calculate_confidence_score(self, visits: List[LocationVisit],
                                   train_segments: List[Dict],
                                   direction: str,
                                   is_weekday: bool,
                                   is_correct_time_window: bool,
                                   duration_minutes: float) -> Tuple[float, Dict]:
        """
        Calculate confidence score for commute detection

        Args:
            visits: Location visits during commute
            train_segments: Detected train segments
            direction: Commute direction
            is_weekday: Is this a weekday?
            is_correct_time_window: Is this in morning/evening window?
            duration_minutes: Total commute duration

        Returns:
            Tuple of (confidence_score, factors_dict)
        """
        factors = {}
        total_score = 0.0
        weights = self.get_config_value('confidence_weights', {
            'known_route_locations': 40,
            'weekday_timing': 20,
            'train_velocity_detected': 20,
            'duration_reasonable': 10,
            'direction_match': 10
        })

        # Factor 1: Known route locations (40 points)
        # Count how many expected locations were visited
        visited_location_names = [v.location_name.lower() for v in visits]
        expected_count = len(self.expected_locations)
        visited_count = sum(1 for exp_loc in self.expected_locations
                          if any(exp_loc.replace('-', ' ') in name or
                                exp_loc.replace('-', '') in name.replace(' ', '')
                                for name in visited_location_names))

        location_score = (visited_count / expected_count) * weights['known_route_locations']
        factors['known_route_locations'] = {
            'score': round(location_score, 1),
            'visited': visited_count,
            'expected': expected_count
        }
        total_score += location_score

        # Factor 2: Weekday timing (20 points)
        if is_weekday and is_correct_time_window:
            factors['weekday_timing'] = {
                'score': weights['weekday_timing'],
                'status': 'YES'
            }
            total_score += weights['weekday_timing']
        else:
            factors['weekday_timing'] = {
                'score': 0,
                'status': 'NO'
            }

        # Factor 3: Train velocity detected (20 points)
        if train_segments:
            factors['train_velocity_detected'] = {
                'score': weights['train_velocity_detected'],
                'segments': len(train_segments),
                'status': 'YES'
            }
            total_score += weights['train_velocity_detected']
        else:
            factors['train_velocity_detected'] = {
                'score': 0,
                'segments': 0,
                'status': 'NO'
            }

        # Factor 4: Duration reasonable (10 points)
        duration_reasonable = self.min_duration_minutes <= duration_minutes <= self.max_duration_minutes

        if duration_reasonable:
            factors['duration_reasonable'] = {
                'score': weights['duration_reasonable'],
                'minutes': round(duration_minutes, 1),
                'status': 'YES'
            }
            total_score += weights['duration_reasonable']
        else:
            factors['duration_reasonable'] = {
                'score': 0,
                'minutes': round(duration_minutes, 1),
                'status': 'NO'
            }

        # Factor 5: Direction match (10 points)
        if direction in ['to_office', 'from_office']:
            factors['direction_match'] = {
                'score': weights['direction_match'],
                'direction': direction,
                'status': 'YES'
            }
            total_score += weights['direction_match']
        else:
            factors['direction_match'] = {
                'score': 0,
                'direction': direction,
                'status': 'NO'
            }

        # Normalize to 0-1 scale
        confidence_score = total_score / 100

        return confidence_score, factors

    def detect_sessions(self, locations: List[Dict],
                       known_locations: Optional[Dict] = None) -> List[ActivitySession]:
        """
        Detect commute sessions from location data

        Args:
            locations: List of location records from Owntracks
            known_locations: Optional dict of known locations

        Returns:
            List of detected commute sessions
        """
        if not locations:
            return []

        # Use location analyzer's known locations if not provided
        if known_locations is None:
            known_locations = self.location_analyzer.get_all_locations()

        # Identify location visits
        visits = self.identify_location_visits(locations, known_locations)

        if len(visits) < 2:  # Need at least 2 locations for a commute
            return []

        # Detect train segments
        train_segments = self.detect_train_segments(locations)

        # Group visits into potential commutes
        commute_sessions = []

        # Look for morning and evening commutes
        for time_window in ['morning', 'evening']:
            # Filter locations by time window
            filtered_locs = self.location_analyzer.filter_by_time_period(
                locations,
                time_window
            )

            if not filtered_locs:
                continue

            # Get start and end times
            start_time = self.parse_timestamp(filtered_locs[0].get('tst'))
            end_time = self.parse_timestamp(filtered_locs[-1].get('tst'))

            if not start_time or not end_time:
                continue

            # Calculate duration
            duration_seconds = (end_time - start_time).total_seconds()
            duration_minutes = duration_seconds / 60
            duration_hours = duration_seconds / 3600

            # Filter by duration
            if not (self.min_duration_minutes <= duration_minutes <= self.max_duration_minutes):
                continue

            # Get visits in this window
            window_visits = [v for v in visits
                           if start_time <= v.arrival_time <= end_time]

            if len(window_visits) < 2:
                continue

            # Classify direction
            direction = self.classify_commute_direction(window_visits, start_time)

            # Check if weekday
            is_weekday = start_time.strftime('%A') in self.expected_days

            # Check if correct time window
            start_hour = start_time.hour
            is_correct_time_window = (
                (time_window == 'morning' and self.morning_start.hour <= start_hour < self.morning_end.hour) or
                (time_window == 'evening' and self.evening_start.hour <= start_hour < self.evening_end.hour)
            )

            # Calculate confidence
            confidence_score, factors = self.calculate_confidence_score(
                window_visits, train_segments, direction, is_weekday,
                is_correct_time_window, duration_minutes
            )

            # Get confidence label
            confidence_label = self.get_confidence_label(confidence_score)

            # Determine location name
            if direction == 'to_office':
                location_name = "Esher → London (Office)"
            elif direction == 'from_office':
                location_name = "London (Office) → Esher"
            else:
                location_name = "Commute (unknown direction)"

            # Use first and last visit coordinates
            start_coords = window_visits[0].location_coords
            end_coords = window_visits[-1].location_coords

            # Create activity session
            session = ActivitySession(
                activity_type='commute',
                start_time=start_time,
                end_time=end_time,
                duration_hours=duration_hours,
                location_name=location_name,
                location_coords=start_coords,  # Start location
                confidence=confidence_label,
                confidence_score=confidence_score,
                details={
                    'direction': direction,
                    'time_window': time_window,
                    'duration_minutes': round(duration_minutes, 1),
                    'locations_visited': len(window_visits),
                    'location_sequence': [v.location_name for v in window_visits],
                    'train_segments': len(train_segments),
                    'is_weekday': is_weekday,
                    'confidence_factors': factors,
                    'end_coords': end_coords
                }
            )

            commute_sessions.append(session)

        return commute_sessions


def create_commute_analyzer(config_path: Optional[str] = None) -> CommuteAnalyzer:
    """
    Factory function to create a CommuteAnalyzer instance

    Args:
        config_path: Optional path to configuration file

    Returns:
        Configured CommuteAnalyzer instance
    """
    return CommuteAnalyzer(config_path)
