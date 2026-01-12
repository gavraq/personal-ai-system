"""
Snowboarding Activity Analyzer
Specialized analyzer for detecting snowboarding sessions from location data.

Detects snowboarding activities at ski resorts:
- Lift rides: Uphill movement at 1.5-6.0 m/s with positive altitude change
- Descents: Downhill movement at 5.0-20.0 m/s with negative altitude change
- Mountain location: Proximity to known ski resorts
- Session duration: 1-10 hours typical
- Run counting: Minimum 2 runs to qualify as session

Key features:
- Altitude-based lift/descent detection
- Velocity pattern analysis
- Known resort location matching
- Run statistics (lifts, descents, vertical meters)

Extends BaseActivityAnalyzer for configuration-driven behavior.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
from geopy.distance import geodesic
import math

from .base_activity_analyzer import BaseActivityAnalyzer, ActivitySession


@dataclass
class MovementSegment:
    """Represents a segment of movement with velocity and altitude"""
    start_time: datetime
    end_time: datetime
    start_coords: Tuple[float, float]  # (lat, lon)
    end_coords: Tuple[float, float]
    start_altitude: Optional[float]  # meters
    end_altitude: Optional[float]
    velocity_mps: float
    distance_meters: float
    altitude_change: float  # positive = uphill, negative = downhill
    duration_seconds: float
    movement_type: str  # 'lift', 'descent', 'stationary', 'flat'


@dataclass
class SnowboardRun:
    """Represents a single snowboard run (lift + descent)"""
    lift_start: datetime
    descent_end: datetime
    vertical_meters: float
    lift_duration_seconds: float
    descent_duration_seconds: float
    avg_descent_velocity: float
    lift_segments: List[MovementSegment]
    descent_segments: List[MovementSegment]


class SnowboardingAnalyzer(BaseActivityAnalyzer):
    """Analyzes location data to detect and characterize snowboarding activities"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize snowboarding analyzer

        Args:
            config_path: Optional path to configuration file
        """
        super().__init__(config_path)
        self.logger = logging.getLogger(__name__)

        # Load configuration values
        lift_velocity = self.get_config_value('lift_velocity_range_mps', [1.5, 6.0])
        self.lift_velocity_min = lift_velocity[0]
        self.lift_velocity_max = lift_velocity[1]

        descent_velocity = self.get_config_value('descent_velocity_range_mps', [5.0, 20.0])
        self.descent_velocity_min = descent_velocity[0]
        self.descent_velocity_max = descent_velocity[1]

        self.min_altitude_change = self.get_config_value('min_altitude_change_meters', 100)
        self.min_session_duration_hours = self.get_config_value('min_session_duration_hours', 1.0)
        self.max_session_duration_hours = self.get_config_value('max_session_duration_hours', 10.0)

        self.lift_angle_threshold = self.get_config_value('lift_detection_angle_threshold', 15)
        self.descent_angle_threshold = self.get_config_value('descent_detection_angle_threshold', -10)

        self.session_gap_minutes = self.get_gap_tolerance()
        self.min_runs = self.get_config_value('min_runs_for_session', 2)

        self.expected_locations = self.get_config_value('expected_locations',
            ['whistler-blackcomb', 'big-white', 'sun-peaks', 'morzine-avoriaz', 'kitzbuhel'])

    def _get_activity_type(self) -> str:
        """Return the activity type string"""
        return 'snowboarding'

    def calculate_slope_angle(self, altitude_change: float, distance_meters: float) -> float:
        """
        Calculate slope angle in degrees

        Args:
            altitude_change: Vertical change in meters (positive = uphill)
            distance_meters: Horizontal distance in meters

        Returns:
            Angle in degrees (positive = uphill, negative = downhill)
        """
        if distance_meters == 0:
            return 0.0

        # Calculate angle using arctan
        angle_radians = math.atan(altitude_change / distance_meters)
        angle_degrees = math.degrees(angle_radians)

        return angle_degrees

    def calculate_velocity(self, point1: Tuple[float, float], point2: Tuple[float, float],
                          time1: datetime, time2: datetime) -> float:
        """
        Calculate velocity between two points in meters per second

        Args:
            point1: (lat, lon) tuple
            point2: (lat, lon) tuple
            time1: Timestamp of first point
            time2: Timestamp of second point

        Returns:
            Velocity in meters per second
        """
        distance_meters = geodesic(point1, point2).meters
        time_diff = (time2 - time1).total_seconds()

        if time_diff == 0:
            return 0.0

        return distance_meters / time_diff

    def classify_movement(self, segment: MovementSegment) -> str:
        """
        Classify movement type based on velocity, altitude change, and slope

        Args:
            segment: MovementSegment to classify

        Returns:
            Movement type: 'lift', 'descent', 'stationary', 'flat'
        """
        # Calculate slope angle
        slope_angle = self.calculate_slope_angle(
            segment.altitude_change,
            segment.distance_meters
        )

        # Stationary: very low velocity
        if segment.velocity_mps < 0.5:
            return 'stationary'

        # Lift: uphill movement with moderate velocity
        if (slope_angle >= self.lift_angle_threshold and
            self.lift_velocity_min <= segment.velocity_mps <= self.lift_velocity_max):
            return 'lift'

        # Descent: downhill movement with high velocity
        if (slope_angle <= self.descent_angle_threshold and
            segment.velocity_mps >= self.descent_velocity_min):
            return 'descent'

        # Everything else is flat/transition
        return 'flat'

    def extract_movement_segments(self, locations: List[Dict]) -> List[MovementSegment]:
        """
        Extract movement segments with altitude data from location records

        Args:
            locations: List of location records

        Returns:
            List of movement segments with altitude changes
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

            # Extract altitude (if available)
            alt1 = loc1.get('alt')
            alt2 = loc2.get('alt')

            # Calculate velocity and distance
            velocity = self.calculate_velocity(coords1, coords2, time1, time2)
            distance = geodesic(coords1, coords2).meters
            duration = (time2 - time1).total_seconds()

            # Calculate altitude change
            altitude_change = 0.0
            if alt1 is not None and alt2 is not None:
                altitude_change = alt2 - alt1

            segment = MovementSegment(
                start_time=time1,
                end_time=time2,
                start_coords=coords1,
                end_coords=coords2,
                start_altitude=alt1,
                end_altitude=alt2,
                velocity_mps=velocity,
                distance_meters=distance,
                altitude_change=altitude_change,
                duration_seconds=duration,
                movement_type='unknown'  # Will be classified next
            )

            # Classify movement type
            segment.movement_type = self.classify_movement(segment)

            segments.append(segment)

        return segments

    def identify_runs(self, segments: List[MovementSegment]) -> List[SnowboardRun]:
        """
        Identify complete snowboard runs (lift + descent pairs)

        Args:
            segments: List of classified movement segments

        Returns:
            List of complete runs
        """
        runs = []
        current_lift_segments = []
        current_descent_segments = []
        in_lift = False
        in_descent = False

        for segment in segments:
            if segment.movement_type == 'lift':
                if in_descent:
                    # Save previous run if we have both lift and descent
                    if current_lift_segments and current_descent_segments:
                        run = self._create_run(current_lift_segments, current_descent_segments)
                        if run:
                            runs.append(run)
                    current_descent_segments = []
                    in_descent = False

                current_lift_segments.append(segment)
                in_lift = True

            elif segment.movement_type == 'descent':
                if not in_lift:
                    # Descent without lift - possible mid-run data gap
                    current_descent_segments.append(segment)
                else:
                    current_descent_segments.append(segment)
                    in_descent = True

            elif segment.movement_type == 'stationary':
                # Stationary might indicate end of run
                if in_descent and current_lift_segments and current_descent_segments:
                    run = self._create_run(current_lift_segments, current_descent_segments)
                    if run:
                        runs.append(run)
                    current_lift_segments = []
                    current_descent_segments = []
                    in_lift = False
                    in_descent = False

        # Handle final run
        if current_lift_segments and current_descent_segments:
            run = self._create_run(current_lift_segments, current_descent_segments)
            if run:
                runs.append(run)

        return runs

    def _create_run(self, lift_segments: List[MovementSegment],
                    descent_segments: List[MovementSegment]) -> Optional[SnowboardRun]:
        """
        Create a SnowboardRun from lift and descent segments

        Args:
            lift_segments: Lift movement segments
            descent_segments: Descent movement segments

        Returns:
            SnowboardRun or None if invalid
        """
        if not lift_segments or not descent_segments:
            return None

        # Calculate vertical meters (from lift segments)
        vertical_meters = sum(s.altitude_change for s in lift_segments if s.altitude_change > 0)

        if vertical_meters < self.min_altitude_change:
            return None

        # Calculate durations
        lift_duration = sum(s.duration_seconds for s in lift_segments)
        descent_duration = sum(s.duration_seconds for s in descent_segments)

        # Calculate average descent velocity
        avg_descent_velocity = sum(s.velocity_mps for s in descent_segments) / len(descent_segments)

        return SnowboardRun(
            lift_start=lift_segments[0].start_time,
            descent_end=descent_segments[-1].end_time,
            vertical_meters=vertical_meters,
            lift_duration_seconds=lift_duration,
            descent_duration_seconds=descent_duration,
            avg_descent_velocity=avg_descent_velocity,
            lift_segments=lift_segments,
            descent_segments=descent_segments
        )

    def is_at_resort(self, coords: Tuple[float, float],
                     known_locations: Dict) -> Optional[str]:
        """
        Check if coordinates are at a known ski resort

        Args:
            coords: (lat, lon) tuple
            known_locations: Dictionary of known locations

        Returns:
            Resort name if at resort, None otherwise
        """
        for location_id in self.expected_locations:
            if location_id not in known_locations:
                continue

            location = known_locations[location_id]
            location_coords = location.get('coordinates')

            if not location_coords:
                continue

            # Use large radius for ski resorts (they're big!)
            resort_radius = self.get_location_radius('ski_resort')
            distance = geodesic(coords, location_coords).meters

            if distance <= resort_radius:
                return location.get('name', location_id)

        return None

    def calculate_confidence(self, runs: List[SnowboardRun],
                            resort_name: Optional[str],
                            session_duration_hours: float) -> Tuple[float, Dict]:
        """
        Calculate confidence score for snowboarding session

        Args:
            runs: List of detected runs
            resort_name: Name of resort if at known location
            session_duration_hours: Total session duration

        Returns:
            Tuple of (confidence_score, scoring_details)
        """
        weights = self.get_config_value('confidence_weights', {
            'known_resort_location': 35,
            'lift_rides_detected': 25,
            'descent_velocity_patterns': 20,
            'altitude_changes': 15,
            'duration_reasonable': 5
        })

        scores = {}
        total_score = 0.0

        # Factor 1: Known resort location (35%)
        resort_score = 1.0 if resort_name else 0.3
        scores['known_resort_location'] = resort_score
        total_score += resort_score * (weights['known_resort_location'] / 100)

        # Factor 2: Lift rides detected (25%)
        num_runs = len(runs)
        lift_score = min(1.0, num_runs / 10)  # 10+ runs = perfect score
        scores['lift_rides_detected'] = lift_score
        total_score += lift_score * (weights['lift_rides_detected'] / 100)

        # Factor 3: Descent velocity patterns (20%)
        if runs:
            avg_descent_velocity = sum(r.avg_descent_velocity for r in runs) / len(runs)
            # Expect 8-15 m/s average descent velocity
            if 8.0 <= avg_descent_velocity <= 15.0:
                velocity_score = 1.0
            elif 5.0 <= avg_descent_velocity < 8.0 or 15.0 < avg_descent_velocity <= 20.0:
                velocity_score = 0.7
            else:
                velocity_score = 0.3
        else:
            velocity_score = 0.0

        scores['descent_velocity_patterns'] = velocity_score
        total_score += velocity_score * (weights['descent_velocity_patterns'] / 100)

        # Factor 4: Altitude changes (15%)
        if runs:
            total_vertical = sum(r.vertical_meters for r in runs)
            # Expect 1000-5000m vertical in a session
            altitude_score = min(1.0, total_vertical / 3000)
        else:
            altitude_score = 0.0

        scores['altitude_changes'] = altitude_score
        total_score += altitude_score * (weights['altitude_changes'] / 100)

        # Factor 5: Duration reasonable (5%)
        if self.min_session_duration_hours <= session_duration_hours <= self.max_session_duration_hours:
            duration_score = 1.0
        elif session_duration_hours < self.min_session_duration_hours:
            duration_score = 0.5
        else:
            duration_score = 0.7  # Long day is okay

        scores['duration_reasonable'] = duration_score
        total_score += duration_score * (weights['duration_reasonable'] / 100)

        return total_score, scores

    def detect_sessions(self, locations: List[Dict],
                       known_locations: Optional[Dict] = None) -> List[ActivitySession]:
        """
        Detect snowboarding sessions from location data

        Args:
            locations: List of location records from Owntracks
            known_locations: Dictionary of known locations

        Returns:
            List of detected snowboarding sessions
        """
        if not locations or not self.enabled:
            return []

        if known_locations is None:
            known_locations = self.location_analyzer.get_all_locations() if self.location_analyzer else {}

        sessions = []

        # Extract movement segments with altitude data
        segments = self.extract_movement_segments(locations)

        if not segments:
            return []

        # Identify complete runs (lift + descent)
        runs = self.identify_runs(segments)

        if len(runs) < self.min_runs:
            self.logger.debug(f"Insufficient runs detected: {len(runs)} < {self.min_runs}")
            return []

        # Group runs into sessions (same day, reasonable gaps)
        session_runs = self._cluster_runs_into_sessions(runs)

        for run_cluster in session_runs:
            if not run_cluster:
                continue

            # Get session time range
            start_time = run_cluster[0].lift_start
            end_time = run_cluster[-1].descent_end
            duration_hours = (end_time - start_time).total_seconds() / 3600

            # Check duration
            if duration_hours < self.min_session_duration_hours:
                continue

            # Get location (check first lift segment)
            first_coords = run_cluster[0].lift_segments[0].start_coords
            resort_name = self.is_at_resort(first_coords, known_locations)

            # Calculate statistics
            total_vertical = sum(r.vertical_meters for r in run_cluster)
            num_runs = len(run_cluster)
            avg_descent_velocity = sum(r.avg_descent_velocity for r in run_cluster) / num_runs

            # Calculate confidence
            confidence_score, scoring_details = self.calculate_confidence(
                run_cluster, resort_name, duration_hours
            )
            confidence_label = self.get_confidence_label(confidence_score)

            # Create session
            session = ActivitySession(
                activity_type='snowboarding',
                start_time=start_time,
                end_time=end_time,
                duration_hours=duration_hours,
                location_name=resort_name or 'Unknown Resort',
                location_coords=first_coords,
                confidence=confidence_label,
                confidence_score=confidence_score,
                details={
                    'num_runs': num_runs,
                    'total_vertical_meters': round(total_vertical, 1),
                    'avg_descent_velocity_mps': round(avg_descent_velocity, 2),
                    'resort_name': resort_name,
                    'confidence_breakdown': scoring_details
                }
            )

            sessions.append(session)

        return sessions

    def _cluster_runs_into_sessions(self, runs: List[SnowboardRun]) -> List[List[SnowboardRun]]:
        """
        Cluster runs into sessions based on time gaps

        Args:
            runs: List of runs to cluster

        Returns:
            List of run clusters (each cluster is a session)
        """
        if not runs:
            return []

        # Sort runs by start time
        sorted_runs = sorted(runs, key=lambda r: r.lift_start)

        clusters = []
        current_cluster = [sorted_runs[0]]

        for i in range(1, len(sorted_runs)):
            run = sorted_runs[i]
            prev_run = sorted_runs[i - 1]

            # Calculate gap between runs
            gap_seconds = (run.lift_start - prev_run.descent_end).total_seconds()
            gap_minutes = gap_seconds / 60

            if gap_minutes <= self.session_gap_minutes:
                # Continue current cluster
                current_cluster.append(run)
            else:
                # Start new cluster
                clusters.append(current_cluster)
                current_cluster = [run]

        # Add final cluster
        if current_cluster:
            clusters.append(current_cluster)

        return clusters


def create_snowboarding_analyzer(config_path: Optional[str] = None) -> SnowboardingAnalyzer:
    """
    Factory function to create SnowboardingAnalyzer

    Args:
        config_path: Optional path to config file

    Returns:
        SnowboardingAnalyzer instance
    """
    return SnowboardingAnalyzer(config_path)


if __name__ == "__main__":
    # Test analyzer creation
    print("=" * 60)
    print("SNOWBOARDING ANALYZER TEST")
    print("=" * 60)

    analyzer = SnowboardingAnalyzer()
    print(f"✓ SnowboardingAnalyzer created")
    print(f"✓ Activity type: {analyzer.activity_type}")
    print(f"✓ Enabled: {analyzer.enabled}")
    print(f"✓ Lift velocity range: {analyzer.lift_velocity_min}-{analyzer.lift_velocity_max} m/s")
    print(f"✓ Descent velocity range: {analyzer.descent_velocity_min}-{analyzer.descent_velocity_max} m/s")
    print(f"✓ Min altitude change: {analyzer.min_altitude_change} meters")
    print(f"✓ Session duration range: {analyzer.min_session_duration_hours}-{analyzer.max_session_duration_hours} hours")
    print(f"✓ Expected resorts: {len(analyzer.expected_locations)}")
    print(f"✓ Min runs per session: {analyzer.min_runs}")
    print("✓ SnowboardingAnalyzer ready for use")
