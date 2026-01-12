"""
Parkrun Activity Analyzer
Specialized analyzer for detecting parkrun (5km Saturday morning runs) from location data.

Uses velocity patterns, timing, and location matching to identify parkrun activities:
- Running velocity: 2.0-5.0 m/s (typical parkrun pace)
- Saturday morning timing: 08:00-11:00
- Duration: 16-45 minutes (based on typical parkrun times)
- Distance: 4.5-5.5km (allowing for GPS variance)
- Known parkrun locations from base_locations.json

Extends BaseActivityAnalyzer for configuration-driven behavior.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
from geopy.distance import geodesic

from .base_activity_analyzer import BaseActivityAnalyzer, ActivitySession


@dataclass
class VelocitySegment:
    """Represents a segment of movement with velocity"""
    start_time: datetime
    end_time: datetime
    start_coords: Tuple[float, float]
    end_coords: Tuple[float, float]
    velocity_mps: float  # meters per second
    distance_meters: float
    duration_seconds: float
    activity_type: str  # 'running', 'walking', 'stationary'


class ParkrunAnalyzer(BaseActivityAnalyzer):
    """Analyzes location data to detect and characterize parkrun activities"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize parkrun analyzer

        Args:
            config_path: Optional path to configuration file
        """
        super().__init__(config_path)
        self.logger = logging.getLogger(__name__)

        # Load configuration values
        velocity_range = self.get_config_value('velocity_range_mps', [2.0, 5.0])
        self.running_min = velocity_range[0]
        self.running_max = velocity_range[1]

        duration_range = self.get_config_value('duration_range_minutes', [16, 45])
        self.min_duration_minutes = duration_range[0]
        self.max_duration_minutes = duration_range[1]

        distance_range = self.get_config_value('distance_range_meters', [4500, 5500])
        self.min_distance = distance_range[0]
        self.max_distance = distance_range[1]

        self.expected_day = self.get_config_value('expected_day', 'Saturday')

        time_range = self.get_config_value('expected_time_range', ['08:00', '11:00'])
        self.start_time = datetime.strptime(time_range[0], '%H:%M').time()
        self.end_time = datetime.strptime(time_range[1], '%H:%M').time()

        self.session_gap_minutes = self.get_gap_tolerance()
        self.min_running_percentage = self.get_config_value('min_running_percentage', 60)

    def _get_activity_type(self) -> str:
        """Return the activity type string"""
        return 'parkrun'

    def calculate_velocity(self, point1: Tuple[float, float], point2: Tuple[float, float],
                          time1: datetime, time2: datetime) -> float:
        """
        Calculate velocity between two points in meters per second

        Args:
            point1: (lat, lon) tuple for start point
            point2: (lat, lon) tuple for end point
            time1: Timestamp of point1
            time2: Timestamp of point2

        Returns:
            Velocity in meters per second
        """
        distance_meters = geodesic(point1, point2).meters
        time_diff = (time2 - time1).total_seconds()

        if time_diff <= 0:
            return 0.0

        return distance_meters / time_diff

    def classify_velocity(self, velocity_mps: float) -> str:
        """
        Classify velocity into activity type

        Args:
            velocity_mps: Velocity in meters per second

        Returns:
            Activity type: 'stationary', 'walking', 'running', 'fast'
        """
        if velocity_mps < 0.5:
            return 'stationary'
        elif velocity_mps < 2.5:
            return 'walking'
        elif velocity_mps <= self.running_max:
            return 'running'
        else:
            return 'fast'

    def extract_velocity_segments(self, locations: List[Dict]) -> List[VelocitySegment]:
        """
        Extract velocity segments from location data

        Args:
            locations: List of location records

        Returns:
            List of velocity segments
        """
        segments = []

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
            velocity = self.calculate_velocity(coords1, coords2, time1, time2)
            distance = geodesic(coords1, coords2).meters
            duration = (time2 - time1).total_seconds()

            # Classify activity
            activity_type = self.classify_velocity(velocity)

            segment = VelocitySegment(
                start_time=time1,
                end_time=time2,
                start_coords=coords1,
                end_coords=coords2,
                velocity_mps=velocity,
                distance_meters=distance,
                duration_seconds=duration,
                activity_type=activity_type
            )

            segments.append(segment)

        return segments

    def cluster_sessions(self, segments: List[VelocitySegment]) -> List[List[VelocitySegment]]:
        """
        Cluster segments into sessions based on gap tolerance

        Args:
            segments: List of velocity segments

        Returns:
            List of segment clusters (each cluster is a potential session)
        """
        if not segments:
            return []

        clusters = []
        current_cluster = [segments[0]]

        for i in range(1, len(segments)):
            prev_segment = segments[i - 1]
            curr_segment = segments[i]

            # Calculate gap between segments
            gap_seconds = (curr_segment.start_time - prev_segment.end_time).total_seconds()
            gap_minutes = gap_seconds / 60

            if gap_minutes <= self.session_gap_minutes:
                current_cluster.append(curr_segment)
            else:
                # Gap too large - start new cluster
                if current_cluster:
                    clusters.append(current_cluster)
                current_cluster = [curr_segment]

        # Add final cluster
        if current_cluster:
            clusters.append(current_cluster)

        return clusters

    def calculate_confidence_score(self, session_segments: List[VelocitySegment],
                                   location_coords: Tuple[float, float],
                                   is_known_parkrun: bool,
                                   is_saturday_morning: bool) -> Tuple[float, Dict]:
        """
        Calculate confidence score for parkrun detection

        Args:
            session_segments: Segments in this session
            location_coords: Location coordinates
            is_known_parkrun: Is this a known parkrun location?
            is_saturday_morning: Is this Saturday morning?

        Returns:
            Tuple of (confidence_score, factors_dict)
        """
        factors = {}
        total_score = 0.0
        weights = self.get_config_value('confidence_weights', {
            'known_parkrun_location': 40,
            'saturday_morning': 20,
            'duration_match': 15,
            'distance_match': 15,
            'running_velocity_percentage': 10
        })

        # Factor 1: Known parkrun location (40 points)
        if is_known_parkrun:
            factors['known_parkrun_location'] = {
                'score': weights['known_parkrun_location'],
                'status': 'YES'
            }
            total_score += weights['known_parkrun_location']
        else:
            factors['known_parkrun_location'] = {
                'score': 0,
                'status': 'NO'
            }

        # Factor 2: Saturday morning (20 points)
        if is_saturday_morning:
            factors['saturday_morning'] = {
                'score': weights['saturday_morning'],
                'status': 'YES'
            }
            total_score += weights['saturday_morning']
        else:
            factors['saturday_morning'] = {
                'score': 0,
                'status': 'NO'
            }

        # Factor 3: Duration match (15 points)
        duration_minutes = sum(s.duration_seconds for s in session_segments) / 60
        duration_match = self.min_duration_minutes <= duration_minutes <= self.max_duration_minutes

        if duration_match:
            factors['duration_match'] = {
                'score': weights['duration_match'],
                'minutes': round(duration_minutes, 1),
                'match': 'YES'
            }
            total_score += weights['duration_match']
        else:
            factors['duration_match'] = {
                'score': 0,
                'minutes': round(duration_minutes, 1),
                'match': 'NO'
            }

        # Factor 4: Distance match (15 points)
        total_distance = sum(s.distance_meters for s in session_segments)
        distance_match = self.min_distance <= total_distance <= self.max_distance

        if distance_match:
            factors['distance_match'] = {
                'score': weights['distance_match'],
                'meters': round(total_distance, 0),
                'match': 'YES'
            }
            total_score += weights['distance_match']
        else:
            factors['distance_match'] = {
                'score': 0,
                'meters': round(total_distance, 0),
                'match': 'NO'
            }

        # Factor 5: Running velocity percentage (10 points)
        running_segments = [s for s in session_segments if s.activity_type == 'running']
        running_pct = (len(running_segments) / len(session_segments)) * 100 if session_segments else 0

        if running_pct >= self.min_running_percentage:
            factors['running_velocity_percentage'] = {
                'score': weights['running_velocity_percentage'],
                'percentage': round(running_pct, 1),
                'status': 'SUFFICIENT'
            }
            total_score += weights['running_velocity_percentage']
        else:
            factors['running_velocity_percentage'] = {
                'score': 0,
                'percentage': round(running_pct, 1),
                'status': 'INSUFFICIENT'
            }

        # Normalize to 0-1 scale
        confidence_score = total_score / 100

        return confidence_score, factors

    def detect_sessions(self, locations: List[Dict],
                       parkrun_location: Optional[Dict] = None) -> List[ActivitySession]:
        """
        Detect parkrun sessions from location data

        Args:
            locations: List of location records from Owntracks
            parkrun_location: Optional dict with 'name', 'coordinates', 'radius'

        Returns:
            List of detected parkrun sessions
        """
        if not locations:
            return []

        # Extract velocity segments
        segments = self.extract_velocity_segments(locations)
        if not segments:
            return []

        # Filter to running segments (parkrun is primarily running)
        running_segments = [s for s in segments
                           if s.activity_type in ['running', 'walking']]

        if not running_segments:
            return []

        # Cluster into sessions
        session_clusters = self.cluster_sessions(running_segments)

        # Analyze each session
        parkrun_sessions = []

        for session_segments in session_clusters:
            # Calculate session timing
            start_time = session_segments[0].start_time
            end_time = session_segments[-1].end_time
            duration_seconds = (end_time - start_time).total_seconds()
            duration_minutes = duration_seconds / 60
            duration_hours = duration_seconds / 3600

            # Filter by duration range
            if not (self.min_duration_minutes <= duration_minutes <= self.max_duration_minutes):
                continue

            # Calculate total distance
            total_distance = sum(s.distance_meters for s in session_segments)

            # Check if Saturday morning
            is_saturday = start_time.strftime('%A') == self.expected_day
            is_morning_time = self.start_time <= start_time.time() <= self.end_time
            is_saturday_morning = is_saturday and is_morning_time

            # Get location info
            if parkrun_location:
                location_name = parkrun_location['name']
                location_coords = parkrun_location['coordinates']
                is_known_parkrun = True
            else:
                # Use center of activity
                avg_lat = sum(s.start_coords[0] for s in session_segments) / len(session_segments)
                avg_lon = sum(s.start_coords[1] for s in session_segments) / len(session_segments)
                location_coords = (avg_lat, avg_lon)
                location_name = f"Location {location_coords[0]:.4f}, {location_coords[1]:.4f}"
                is_known_parkrun = False

            # Calculate confidence
            confidence_score, factors = self.calculate_confidence_score(
                session_segments, location_coords, is_known_parkrun, is_saturday_morning
            )

            # Get confidence label
            confidence_label = self.get_confidence_label(confidence_score)

            # Create activity session using base class structure
            session = ActivitySession(
                activity_type='parkrun',
                start_time=start_time,
                end_time=end_time,
                duration_hours=duration_hours,
                location_name=location_name,
                location_coords=location_coords,
                confidence=confidence_label,
                confidence_score=confidence_score,
                details={
                    'distance_meters': round(total_distance, 0),
                    'distance_km': round(total_distance / 1000, 2),
                    'duration_minutes': round(duration_minutes, 1),
                    'is_saturday': is_saturday,
                    'is_morning_time': is_morning_time,
                    'confidence_factors': factors,
                    'segment_count': len(session_segments)
                }
            )

            parkrun_sessions.append(session)

        return parkrun_sessions


def create_parkrun_analyzer(config_path: Optional[str] = None) -> ParkrunAnalyzer:
    """
    Factory function to create a ParkrunAnalyzer instance

    Args:
        config_path: Optional path to configuration file

    Returns:
        Configured ParkrunAnalyzer instance
    """
    return ParkrunAnalyzer(config_path)
