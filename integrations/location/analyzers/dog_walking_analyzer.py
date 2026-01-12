"""
Dog Walking Activity Analyzer
Specialized analyzer for detecting local dog walking activities from location data.

Detects dog walks around Esher:
- Walking velocity: 0.8-2.0 m/s (leisurely walking pace)
- Near home proximity: Within 2km of home
- Duration: 10-90 minutes typical
- Known locations: Esher Common, Molesey Heath, Claremont Gardens
- Multiple stops (stationary periods for dog activities)

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
    velocity_mps: float
    distance_meters: float
    duration_seconds: float
    activity_type: str  # 'walking', 'stationary'


class DogWalkingAnalyzer(BaseActivityAnalyzer):
    """Analyzes location data to detect and characterize dog walking activities"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize dog walking analyzer

        Args:
            config_path: Optional path to configuration file
        """
        super().__init__(config_path)
        self.logger = logging.getLogger(__name__)

        # Load configuration values
        velocity_range = self.get_config_value('velocity_range_mps', [0.8, 2.0])
        self.walking_min = velocity_range[0]
        self.walking_max = velocity_range[1]

        self.min_duration_minutes = self.get_config_value('min_duration_minutes', 10)
        self.max_duration_minutes = self.get_config_value('max_duration_minutes', 90)

        self.expected_locations = self.get_config_value('expected_locations',
            ['esher-common', 'black-pond-esher', 'molesey-heath', 'claremont-landscape-garden'])

        self.home_proximity_meters = self.get_config_value('home_proximity_meters', 2000)
        self.stationary_tolerance_pct = self.get_config_value('stationary_tolerance_pct', 30)
        self.session_gap_minutes = self.get_gap_tolerance()

        # Home coordinates will be loaded when needed
        self._home_coords = None

    def _get_activity_type(self) -> str:
        """Return the activity type string"""
        return 'dog_walking'

    def _get_home_coords(self, known_locations: Dict) -> Optional[Tuple[float, float]]:
        """Get home coordinates from known locations"""
        if self._home_coords is not None:
            return self._home_coords

        if 'home-esher' in known_locations:
            self._home_coords = known_locations['home-esher']['coordinates']

        return self._home_coords

    def calculate_velocity(self, point1: Tuple[float, float], point2: Tuple[float, float],
                          time1: datetime, time2: datetime) -> float:
        """Calculate velocity between two points in meters per second"""
        distance_meters = geodesic(point1, point2).meters
        time_diff = (time2 - time1).total_seconds()

        if time_diff <= 0:
            return 0.0

        return distance_meters / time_diff

    def classify_velocity(self, velocity_mps: float) -> str:
        """Classify velocity into activity type"""
        if velocity_mps < 0.5:
            return 'stationary'
        elif self.walking_min <= velocity_mps <= self.walking_max:
            return 'walking'
        else:
            return 'fast'  # Too fast for dog walking

    def extract_velocity_segments(self, locations: List[Dict]) -> List[VelocitySegment]:
        """Extract velocity segments from location data"""
        segments = []

        for i in range(len(locations) - 1):
            loc1 = locations[i]
            loc2 = locations[i + 1]

            coords1 = (loc1.get('lat'), loc1.get('lon'))
            coords2 = (loc2.get('lat'), loc2.get('lon'))

            if None in coords1 or None in coords2:
                continue

            time1 = self.parse_timestamp(loc1.get('tst'))
            time2 = self.parse_timestamp(loc2.get('tst'))

            if not time1 or not time2:
                continue

            velocity = self.calculate_velocity(coords1, coords2, time1, time2)
            distance = geodesic(coords1, coords2).meters
            duration = (time2 - time1).total_seconds()

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
        """Cluster segments into sessions based on gap tolerance"""
        if not segments:
            return []

        clusters = []
        current_cluster = [segments[0]]

        for i in range(1, len(segments)):
            prev_segment = segments[i - 1]
            curr_segment = segments[i]

            gap_minutes = (curr_segment.start_time - prev_segment.end_time).total_seconds() / 60

            if gap_minutes <= self.session_gap_minutes:
                current_cluster.append(curr_segment)
            else:
                if current_cluster:
                    clusters.append(current_cluster)
                current_cluster = [curr_segment]

        if current_cluster:
            clusters.append(current_cluster)

        return clusters

    def is_near_home(self, coords: Tuple[float, float], known_locations: Dict) -> bool:
        """Check if coordinates are near home"""
        home_coords = self._get_home_coords(known_locations)
        if not home_coords:
            return False

        distance = geodesic(home_coords, coords).meters
        return distance <= self.home_proximity_meters

    def is_known_walking_location(self, coords: Tuple[float, float],
                                  known_locations: Dict) -> Optional[str]:
        """Check if coordinates are at a known dog walking location"""
        for loc_id in self.expected_locations:
            if loc_id not in known_locations:
                continue

            loc_info = known_locations[loc_id]
            distance = geodesic(coords, loc_info['coordinates']).meters

            if distance <= loc_info.get('radius', 100):
                return loc_info['name']

        return None

    def calculate_confidence_score(self, session_segments: List[VelocitySegment],
                                   location_coords: Tuple[float, float],
                                   known_location_name: Optional[str],
                                   is_near_home: bool) -> Tuple[float, Dict]:
        """Calculate confidence score for dog walking detection"""
        factors = {}
        total_score = 0.0
        weights = self.get_config_value('confidence_weights', {
            'near_home': 30,
            'known_walking_location': 25,
            'walking_velocity': 20,
            'duration_reasonable': 15,
            'stationary_stops': 10
        })

        # Factor 1: Near home (30 points)
        if is_near_home:
            factors['near_home'] = {'score': weights['near_home'], 'status': 'YES'}
            total_score += weights['near_home']
        else:
            factors['near_home'] = {'score': 0, 'status': 'NO'}

        # Factor 2: Known walking location (25 points)
        if known_location_name:
            factors['known_walking_location'] = {
                'score': weights['known_walking_location'],
                'location': known_location_name,
                'status': 'YES'
            }
            total_score += weights['known_walking_location']
        else:
            factors['known_walking_location'] = {'score': 0, 'status': 'NO'}

        # Factor 3: Walking velocity (20 points)
        walking_segments = [s for s in session_segments if s.activity_type == 'walking']
        walking_pct = (len(walking_segments) / len(session_segments)) * 100 if session_segments else 0

        if walking_pct >= 50:  # At least 50% walking
            factors['walking_velocity'] = {
                'score': weights['walking_velocity'],
                'percentage': round(walking_pct, 1),
                'status': 'SUFFICIENT'
            }
            total_score += weights['walking_velocity']
        else:
            factors['walking_velocity'] = {
                'score': 0,
                'percentage': round(walking_pct, 1),
                'status': 'INSUFFICIENT'
            }

        # Factor 4: Duration reasonable (15 points)
        duration_minutes = sum(s.duration_seconds for s in session_segments) / 60
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

        # Factor 5: Stationary stops (10 points)
        stationary_segments = [s for s in session_segments if s.activity_type == 'stationary']
        stationary_pct = (len(stationary_segments) / len(session_segments)) * 100 if session_segments else 0

        # Dog walks have some stationary periods (sniffing, bathroom breaks)
        if 10 <= stationary_pct <= self.stationary_tolerance_pct:
            factors['stationary_stops'] = {
                'score': weights['stationary_stops'],
                'percentage': round(stationary_pct, 1),
                'status': 'APPROPRIATE'
            }
            total_score += weights['stationary_stops']
        else:
            factors['stationary_stops'] = {
                'score': 0,
                'percentage': round(stationary_pct, 1),
                'status': 'INAPPROPRIATE'
            }

        # Normalize to 0-1 scale
        confidence_score = total_score / 100

        return confidence_score, factors

    def detect_sessions(self, locations: List[Dict],
                       known_locations: Optional[Dict] = None) -> List[ActivitySession]:
        """
        Detect dog walking sessions from location data

        Args:
            locations: List of location records from Owntracks
            known_locations: Optional dict of known locations

        Returns:
            List of detected dog walking sessions
        """
        if not locations:
            return []

        # Use location analyzer's known locations if not provided
        if known_locations is None:
            known_locations = self.location_analyzer.get_all_locations()

        # Extract velocity segments
        segments = self.extract_velocity_segments(locations)
        if not segments:
            return []

        # Filter to walking/stationary segments (dog walking pace)
        walking_segments = [s for s in segments
                           if s.activity_type in ['walking', 'stationary']]

        if not walking_segments:
            return []

        # PRE-FILTER: Only keep segments at known dog walking locations
        # This prevents including house movements and focuses on actual walks
        filtered_segments = []
        for seg in walking_segments:
            coords = seg.start_coords
            # ONLY include segments at known walking locations (e.g., Esher Common, Black Pond)
            # Do NOT include generic "near home" segments as those capture house movements
            if self.is_known_walking_location(coords, known_locations):
                filtered_segments.append(seg)

        if not filtered_segments:
            return []

        # Cluster into sessions
        session_clusters = self.cluster_sessions(filtered_segments)

        # Analyze each session
        dog_walking_sessions = []

        for session_segments in session_clusters:
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

            # Get center of activity
            avg_lat = sum(s.start_coords[0] for s in session_segments) / len(session_segments)
            avg_lon = sum(s.start_coords[1] for s in session_segments) / len(session_segments)
            location_coords = (avg_lat, avg_lon)

            # Check if near home
            near_home = self.is_near_home(location_coords, known_locations)

            # Check if at known walking location
            known_location_name = self.is_known_walking_location(location_coords, known_locations)

            # Determine location name
            if known_location_name:
                location_name = known_location_name
            elif near_home:
                location_name = "Near home (Esher)"
            else:
                location_name = f"Location {location_coords[0]:.4f}, {location_coords[1]:.4f}"

            # Calculate confidence
            confidence_score, factors = self.calculate_confidence_score(
                session_segments, location_coords, known_location_name, near_home
            )

            # Get confidence label
            confidence_label = self.get_confidence_label(confidence_score)

            # Create activity session
            session = ActivitySession(
                activity_type='dog_walking',
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
                    'near_home': near_home,
                    'known_location': known_location_name is not None,
                    'confidence_factors': factors,
                    'segment_count': len(session_segments)
                }
            )

            dog_walking_sessions.append(session)

        return dog_walking_sessions


def create_dog_walking_analyzer(config_path: Optional[str] = None) -> DogWalkingAnalyzer:
    """
    Factory function to create a DogWalkingAnalyzer instance

    Args:
        config_path: Optional path to configuration file

    Returns:
        Configured DogWalkingAnalyzer instance
    """
    return DogWalkingAnalyzer(config_path)
