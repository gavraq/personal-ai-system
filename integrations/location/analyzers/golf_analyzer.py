"""
Golf Activity Analyzer
Specialized analyzer for detecting and analyzing golf activities from location data.

Uses velocity patterns and session clustering to identify golf rounds:
- Walking velocity: 0.5-2.5 m/s (typical golf course walking pace)
- Stationary periods: <0.5 m/s (taking shots, waiting)
- Session clustering: 15-minute gap tolerance
- Likelihood scoring: HIGH/MEDIUM/LOW confidence

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
    activity_type: str  # 'walking', 'stationary', 'fast'


class GolfAnalyzer(BaseActivityAnalyzer):
    """Analyzes location data to detect and characterize golf activities"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize golf analyzer

        Args:
            config_path: Optional path to configuration file
        """
        super().__init__(config_path)
        self.logger = logging.getLogger(__name__)

        # Load configuration values (with fallbacks to original constants)
        self.stationary_max = self.get_config_value('stationary_threshold_mps', 0.5)
        velocity_range = self.get_config_value('velocity_range_mps', [0.5, 2.5])
        self.walking_min = velocity_range[0]
        self.walking_max = velocity_range[1]

        self.session_gap_minutes = self.get_gap_tolerance()  # From base class
        self.min_session_duration_minutes = self.get_config_value('min_session_duration_minutes', 60)

        # Golf course characteristics
        duration_9 = self.get_config_value('duration_range_hours', {}).get('9_holes', [1.5, 2.5])
        duration_18 = self.get_config_value('duration_range_hours', {}).get('18_holes', [3.0, 5.0])
        distance_9 = self.get_config_value('distance_range_meters', {}).get('9_holes', [3000, 5000])
        distance_18 = self.get_config_value('distance_range_meters', {}).get('18_holes', [6000, 10000])

        self.typical_9hole_duration = tuple(duration_9)
        self.typical_18hole_duration = tuple(duration_18)
        self.typical_9hole_distance = tuple(distance_9)
        self.typical_18hole_distance = tuple(distance_18)

        # Confidence weights from config
        weights = self.get_config_value('confidence_weights', {})
        self.weight_known_course = weights.get('known_golf_course', 40)
        self.weight_duration = weights.get('duration_match', 25)
        self.weight_distance = weights.get('distance_match', 20)
        self.weight_ratio = weights.get('walking_stationary_ratio', 10)
        self.weight_fast = weights.get('minimal_fast_segments', 5)

    def _get_activity_type(self) -> str:
        """Return activity type identifier"""
        return 'golf'

    def calculate_velocity(self, point1: Tuple[float, float],
                          point2: Tuple[float, float],
                          time1: datetime,
                          time2: datetime) -> float:
        """
        Calculate velocity between two points

        Args:
            point1: (lat, lon) of first point
            point2: (lat, lon) of second point
            time1: Timestamp of first point
            time2: Timestamp of second point

        Returns:
            Velocity in meters per second
        """
        distance = geodesic(point1, point2).meters
        duration_seconds = (time2 - time1).total_seconds()

        if duration_seconds == 0:
            return 0.0

        return distance / duration_seconds

    def classify_velocity(self, velocity_mps: float) -> str:
        """
        Classify velocity into activity type

        Args:
            velocity_mps: Velocity in meters per second

        Returns:
            Activity type: 'stationary', 'walking', 'fast'
        """
        if velocity_mps < self.stationary_max:
            return 'stationary'
        elif velocity_mps <= self.walking_max:
            return 'walking'
        else:
            return 'fast'  # Running, cycling, driving

    def extract_velocity_segments(self, locations: List[Dict]) -> List[VelocitySegment]:
        """
        Extract velocity segments from location data

        Args:
            locations: List of location records from Owntracks

        Returns:
            List of velocity segments
        """
        if len(locations) < 2:
            return []

        segments = []
        sorted_locs = sorted(locations, key=lambda x: x.get('tst', 0))

        for i in range(len(sorted_locs) - 1):
            loc1 = sorted_locs[i]
            loc2 = sorted_locs[i + 1]

            # Extract data
            coords1 = (loc1.get('lat'), loc1.get('lon'))
            coords2 = (loc2.get('lat'), loc2.get('lon'))
            time1 = datetime.fromtimestamp(loc1.get('tst', 0))
            time2 = datetime.fromtimestamp(loc2.get('tst', 0))

            # Calculate velocity
            velocity = self.calculate_velocity(coords1, coords2, time1, time2)
            distance = geodesic(coords1, coords2).meters
            duration = (time2 - time1).total_seconds()

            # Classify
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
        Cluster velocity segments into sessions based on time gaps

        Args:
            segments: List of velocity segments

        Returns:
            List of session clusters
        """
        if not segments:
            return []

        sessions = []
        current_session = [segments[0]]

        for i in range(1, len(segments)):
            prev_segment = segments[i - 1]
            curr_segment = segments[i]

            # Check time gap between segments
            gap_minutes = (curr_segment.start_time - prev_segment.end_time).total_seconds() / 60

            # Be strict about gaps - if segments are more than session_gap_minutes apart,
            # start a new session. For golf, we expect continuous activity.
            if gap_minutes <= self.session_gap_minutes:
                current_session.append(curr_segment)
            else:
                # Only save sessions with reasonable activity density
                if len(current_session) >= 3:  # At least 3 segments
                    sessions.append(current_session)
                current_session = [curr_segment]

        # Add final session if it has enough segments
        if current_session and len(current_session) >= 3:
            sessions.append(current_session)

        return sessions

    def calculate_confidence_score(self, session_segments: List[VelocitySegment],
                                   location_coords: Tuple[float, float],
                                   is_known_golf_course: bool) -> Tuple[float, Dict, str]:
        """
        Calculate confidence that a session is golf

        Args:
            session_segments: Segments in the session
            location_coords: Golf course coordinates
            is_known_golf_course: Whether location is a known golf course

        Returns:
            Tuple of (confidence_score, factors_dict, likelihood_label)
        """
        factors = {}
        score = 0.0
        max_score = 0.0

        # Calculate session statistics
        walking_segments = [s for s in session_segments if s.activity_type == 'walking']
        stationary_segments = [s for s in session_segments if s.activity_type == 'stationary']
        fast_segments = [s for s in session_segments if s.activity_type == 'fast']

        total_duration = sum(s.duration_seconds for s in session_segments) / 3600  # hours
        total_distance = sum(s.distance_meters for s in session_segments)

        walking_time = sum(s.duration_seconds for s in walking_segments) / 3600
        stationary_time = sum(s.duration_seconds for s in stationary_segments) / 3600

        # Factor 1: Known golf course location
        max_score += self.weight_known_course
        if is_known_golf_course:
            score += self.weight_known_course
            factors['known_golf_course'] = {'score': self.weight_known_course, 'status': 'YES'}
        else:
            factors['known_golf_course'] = {'score': 0, 'status': 'NO'}

        # Factor 2: Duration matches typical golf
        max_score += self.weight_duration
        duration_score = 0
        if self.typical_9hole_duration[0] <= total_duration <= self.typical_9hole_duration[1]:
            duration_score = self.weight_duration
            factors['duration'] = {'score': self.weight_duration, 'hours': total_duration, 'match': '9-hole'}
        elif self.typical_18hole_duration[0] <= total_duration <= self.typical_18hole_duration[1]:
            duration_score = self.weight_duration
            factors['duration'] = {'score': self.weight_duration, 'hours': total_duration, 'match': '18-hole'}
        elif self.typical_9hole_duration[0] <= total_duration <= self.typical_18hole_duration[1]:
            duration_score = 20
            factors['duration'] = {'score': 20, 'hours': total_duration, 'match': 'golf-range'}
        else:
            factors['duration'] = {'score': 0, 'hours': total_duration, 'match': 'outside-typical'}
        score += duration_score

        # Factor 3: Distance matches typical golf
        max_score += self.weight_distance
        distance_score = 0
        if self.typical_9hole_distance[0] <= total_distance <= self.typical_9hole_distance[1]:
            distance_score = self.weight_distance
            factors['distance'] = {'score': self.weight_distance, 'km': total_distance/1000, 'match': '9-hole'}
        elif self.typical_18hole_distance[0] <= total_distance <= self.typical_18hole_distance[1]:
            distance_score = self.weight_distance
            factors['distance'] = {'score': self.weight_distance, 'km': total_distance/1000, 'match': '18-hole'}
        elif self.typical_9hole_distance[0] <= total_distance <= self.typical_18hole_distance[1]:
            distance_score = 15
            factors['distance'] = {'score': 15, 'km': total_distance/1000, 'match': 'golf-range'}
        else:
            factors['distance'] = {'score': 0, 'km': total_distance/1000, 'match': 'outside-typical'}
        score += distance_score

        # Factor 4: Walking/stationary ratio
        max_score += self.weight_ratio
        if walking_time > 0 and stationary_time > 0:
            ratio = walking_time / (walking_time + stationary_time)
            if 0.5 <= ratio <= 0.9:
                ratio_score = self.weight_ratio
                factors['walking_stationary_ratio'] = {'score': self.weight_ratio, 'ratio': ratio, 'walking_pct': ratio*100}
            else:
                ratio_score = 5
                factors['walking_stationary_ratio'] = {'score': 5, 'ratio': ratio, 'walking_pct': ratio*100}
        else:
            ratio_score = 0
            factors['walking_stationary_ratio'] = {'score': 0, 'note': 'insufficient_data'}
        score += ratio_score

        # Factor 5: Minimal fast segments
        max_score += self.weight_fast
        fast_time = sum(s.duration_seconds for s in fast_segments) / 3600
        fast_pct = (fast_time / total_duration * 100) if total_duration > 0 else 0
        if fast_pct < 10:
            score += self.weight_fast
            factors['fast_segments'] = {'score': self.weight_fast, 'pct': fast_pct, 'status': 'minimal'}
        else:
            factors['fast_segments'] = {'score': 0, 'pct': fast_pct, 'status': 'excessive'}

        # Calculate final confidence
        confidence = score / max_score if max_score > 0 else 0.0

        # Determine likelihood label using base class method
        likelihood = self.get_confidence_label(confidence)

        return confidence, factors, likelihood

    def estimate_holes_played(self, duration_hours: float,
                             distance_meters: float) -> Optional[int]:
        """
        Estimate number of holes played (9 or 18)

        Args:
            duration_hours: Session duration in hours
            distance_meters: Total distance covered

        Returns:
            9 or 18, or None if unclear
        """
        # Check duration
        duration_match_9 = self.typical_9hole_duration[0] <= duration_hours <= self.typical_9hole_duration[1]
        duration_match_18 = self.typical_18hole_duration[0] <= duration_hours <= self.typical_18hole_duration[1]

        # Check distance
        distance_match_9 = self.typical_9hole_distance[0] <= distance_meters <= self.typical_9hole_distance[1]
        distance_match_18 = self.typical_18hole_distance[0] <= distance_meters <= self.typical_18hole_distance[1]

        # Both match 9 holes
        if duration_match_9 and distance_match_9:
            return 9

        # Both match 18 holes
        if duration_match_18 and distance_match_18:
            return 18

        # Duration suggests one, distance suggests another
        if duration_match_9 and not duration_match_18:
            return 9
        if duration_match_18 and not duration_match_9:
            return 18

        # Unclear
        return None

    def detect_sessions(self, locations: List[Dict],
                       golf_course_location: Optional[Dict] = None) -> List[ActivitySession]:
        """
        Detect golf sessions from location data (DENSITY-BASED VERSION)

        Key insight from map data: Golf creates dense tracking (3-5 locations/min) while
        sleeping/resort time creates sparse tracking (<1 location/min) - even at same location

        Approach:
        1. Filter to golf course proximity
        2. Find HIGH-DENSITY periods (≥3 locations/min in 30-min windows)
        3. Merge nearby high-density periods into sessions
        4. Validate duration, timing, and movement patterns
        """
        if not locations:
            return []

        # If we have a known golf course, filter to nearby locations
        if golf_course_location:
            nearby = []
            course_coords = tuple(golf_course_location['coordinates'])
            radius = golf_course_location['radius']

            for loc in locations:
                loc_coords = (loc.get('lat'), loc.get('lon'))
                distance = geodesic(course_coords, loc_coords).meters
                if distance <= radius:
                    nearby.append(loc)

            if not nearby:
                return []

            # Sort by time
            sorted_locs = sorted(nearby, key=lambda x: x.get('tst', 0))

            # Find continuous periods (gaps <30 minutes)
            # Then filter for high-density periods (actual golf activity)
            periods = []
            current = [sorted_locs[0]]

            for i in range(1, len(sorted_locs)):
                prev_time = datetime.fromtimestamp(current[-1].get('tst', 0))
                curr_time = datetime.fromtimestamp(sorted_locs[i].get('tst', 0))
                gap_min = (curr_time - prev_time).total_seconds() / 60

                if gap_min <= 30:  # Use 30-minute gaps based on real data analysis
                    current.append(sorted_locs[i])
                else:
                    if len(current) >= 50:  # Minimum locations for consideration
                        periods.append(current)
                    current = [sorted_locs[i]]

            if len(current) >= 50:
                periods.append(current)

            if not periods:
                return []

            # For each period, find continuous high-density sub-periods
            # Use a rolling density check: compute density for each location's surrounding hour
            high_density_periods = []

            for locs in periods:
                # Calculate rolling 1-hour density for each location
                densities = []
                ROLLING_WINDOW = 30 * 60  # 30-minute window (15 min before + 15 min after)

                for i, loc in enumerate(locs):
                    loc_time = loc.get('tst', 0)
                    window_start = loc_time - ROLLING_WINDOW / 2
                    window_end = loc_time + ROLLING_WINDOW / 2

                    # Count locations within window
                    count = sum(1 for l in locs if window_start <= l.get('tst', 0) <= window_end)
                    density = count / (ROLLING_WINDOW / 60)  # locations per minute

                    densities.append((loc, density))

                # Find continuous stretches where density ≥ 2.0 locations/min
                high_density_stretches = []
                current_stretch = []

                for loc, density in densities:
                    if density >= 2.0:
                        current_stretch.append(loc)
                    else:
                        if len(current_stretch) >= 100:  # Minimum size
                            high_density_stretches.append(current_stretch)
                        current_stretch = []

                if len(current_stretch) >= 100:
                    high_density_stretches.append(current_stretch)

                # Add valid stretches (2+ hours duration)
                for stretch in high_density_stretches:
                    start_time = datetime.fromtimestamp(stretch[0].get('tst', 0))
                    end_time = datetime.fromtimestamp(stretch[-1].get('tst', 0))
                    duration_h = (end_time - start_time).total_seconds() / 3600

                    if duration_h >= 2.0:  # Minimum golf duration
                        high_density_periods.append(stretch)

            if not high_density_periods:
                return []

            merged_periods = high_density_periods

            # Analyze each merged period
            sessions = []
            for locs in merged_periods:
                start = datetime.fromtimestamp(locs[0].get('tst', 0))
                end = datetime.fromtimestamp(locs[-1].get('tst', 0))
                duration_h = (end - start).total_seconds() / 3600

                # Golf rounds: 2-6 hours (real data: 2.4-3.0h), during day (6am-7pm start)
                # Key insight: Duration is the best discriminator vs supermarket trips (1.5h)
                if not (2.0 <= duration_h <= 6.0 and 6 <= start.hour <= 19):
                    continue

                # Verify overall density is still high
                # Real golf data: 2.6-3.9 locations/min
                density = len(locs) / (duration_h * 60) if duration_h > 0 else 0
                if density < 2.3:  # Slightly below minimum observed (2.57)
                    continue

                # Calculate velocity breakdown for confidence scoring
                # Real golf patterns:
                #   Stationary/slow (≤2.5): 16-30%
                #   Medium pace (2.5-5.0): 49-61%
                #   High speed (>5.0): 10-35%
                stationary_slow = sum(1 for loc in locs if loc.get('vel', 0) <= 2.5)
                medium_pace = sum(1 for loc in locs if 2.5 < loc.get('vel', 0) <= 5.0)
                high_speed = sum(1 for loc in locs if loc.get('vel', 0) > 5.0)

                stat_slow_ratio = stationary_slow / len(locs)
                medium_ratio = medium_pace / len(locs)
                high_ratio = high_speed / len(locs)

                # Set confidence based on how well it matches golf patterns
                # High confidence: Good density + typical velocity distribution
                if density >= 3.0 and 0.15 <= stat_slow_ratio <= 0.35 and 0.45 <= medium_ratio <= 0.65:
                    conf, score = 'HIGH', 0.90
                # Medium confidence: Acceptable density + reasonable velocity mix
                elif density >= 2.5 and stat_slow_ratio >= 0.10:
                    conf, score = 'MEDIUM', 0.75
                # Low confidence: Meets minimum thresholds
                else:
                    conf, score = 'LOW', 0.60

                session = ActivitySession(
                    activity_type='golf',
                    start_time=start,
                    end_time=end,
                    duration_hours=duration_h,
                    location_name=golf_course_location['name'],
                    location_coords=course_coords,
                    confidence=conf,
                    confidence_score=score,
                    details={
                        'location_records': len(locs),
                        'density_per_min': round(density, 1),
                        'stationary_slow_ratio': round(stat_slow_ratio, 2),
                        'medium_pace_ratio': round(medium_ratio, 2),
                        'high_speed_ratio': round(high_ratio, 2),
                        'estimated_holes': self.estimate_holes_played(duration_h, 0)
                    }
                )
                sessions.append(session)

            return sessions
        
        # No known course - use old velocity-based method
        segments = self.extract_velocity_segments(locations)
        golf_periods = self._find_golf_periods(segments)
        sessions = []
        for segs in golf_periods:
            s = self._analyze_golf_period(segs, None)
            if s:
                sessions.append(s)
        return sessions

    def _find_golf_periods(self, all_segments: List[VelocitySegment]) -> List[List[VelocitySegment]]:
        """
        Find continuous periods with golf-like activity patterns

        A golf period is a continuous stretch of golf-pace (walking/stationary) segments
        with very short gaps between them (max 10 minutes).

        Args:
            all_segments: All velocity segments including fast movement

        Returns:
            List of segment lists representing golf periods
        """
        if not all_segments:
            return []

        # Filter to only golf-pace segments
        golf_segments = [s for s in all_segments if s.activity_type in ['walking', 'stationary']]

        if not golf_segments:
            return []

        # Group into continuous periods (max 10 minute gap)
        max_gap_minutes = 10  # Much stricter than before
        periods = []
        current_period = [golf_segments[0]]

        for i in range(1, len(golf_segments)):
            prev_seg = golf_segments[i-1]
            curr_seg = golf_segments[i]

            gap = (curr_seg.start_time - prev_seg.end_time).total_seconds() / 60

            if gap <= max_gap_minutes:
                current_period.append(curr_seg)
            else:
                # Gap too large - check if current period is valid
                if self._is_valid_golf_period(current_period):
                    periods.append(current_period)
                current_period = [curr_seg]

        # Don't forget the last period
        if current_period and self._is_valid_golf_period(current_period):
            periods.append(current_period)

        return periods

    def _is_valid_golf_period(self, segments: List[VelocitySegment]) -> bool:
        """Check if a period of segments represents valid golf activity"""
        if len(segments) < 10:  # Need at least 10 segments
            return False

        start = segments[0].start_time
        end = segments[-1].end_time
        duration_hours = (end - start).total_seconds() / 3600

        # Golf rounds are 1-6 hours
        if duration_hours < 1.0 or duration_hours > 6.0:
            return False

        return True

    def _analyze_golf_period(self, session_segments: List[VelocitySegment],
                            golf_course_location: Optional[Dict]) -> Optional[ActivitySession]:
        """
        Analyze a golf period and create an ActivitySession

        Args:
            session_segments: Segments representing the golf period
            golf_course_location: Optional known golf course location

        Returns:
            ActivitySession or None if analysis fails
        """
        if not session_segments:
            return None

        # Calculate session timing
        start_time = session_segments[0].start_time
        end_time = session_segments[-1].end_time
        duration_seconds = (end_time - start_time).total_seconds()
        duration_hours = duration_seconds / 3600

        # Calculate total distance
        total_distance = sum(s.distance_meters for s in session_segments)

        # Get location info
        if golf_course_location:
            location_name = golf_course_location['name']
            location_coords = golf_course_location['coordinates']
            is_known_course = True
        else:
            # Use center of activity
            avg_lat = sum(s.start_coords[0] for s in session_segments) / len(session_segments)
            avg_lon = sum(s.start_coords[1] for s in session_segments) / len(session_segments)
            location_coords = (avg_lat, avg_lon)
            location_name = f"Location {location_coords[0]:.4f}, {location_coords[1]:.4f}"
            is_known_course = False

        # Calculate confidence
        confidence_score, factors, likelihood = self.calculate_confidence_score(
            session_segments, location_coords, is_known_course
        )

        # Estimate holes
        estimated_holes = self.estimate_holes_played(duration_hours, total_distance)

        # Separate walking and stationary segments
        walking_segments = [s for s in session_segments if s.activity_type == 'walking']
        stationary_segments = [s for s in session_segments if s.activity_type == 'stationary']

        # Create activity session using base class structure
        session = ActivitySession(
            activity_type='golf',
            start_time=start_time,
            end_time=end_time,
            duration_hours=duration_hours,
            location_name=location_name,
            location_coords=location_coords,
            confidence=likelihood,
            confidence_score=confidence_score,
            details={
                'estimated_holes': estimated_holes,
                'total_distance_km': round(total_distance / 1000, 2),
                'walking_segments': len(walking_segments),
                'stationary_segments': len(stationary_segments),
                'confidence_factors': factors
            }
        )

        return session


def create_golf_analyzer(config_path: Optional[str] = None) -> GolfAnalyzer:
    """
    Factory function to create a GolfAnalyzer instance

    Args:
        config_path: Optional path to configuration file

    Returns:
        Configured GolfAnalyzer instance
    """
    return GolfAnalyzer(config_path)


if __name__ == "__main__":
    # Basic test
    print("Golf Analyzer module loaded successfully")
    analyzer = create_golf_analyzer()
    print(f"Activity type: {analyzer.activity_type}")
    print(f"Enabled: {analyzer.enabled}")
    print(f"Velocity thresholds: walking {analyzer.walking_min}-{analyzer.walking_max} m/s, stationary <{analyzer.stationary_max} m/s")
    print(f"Session gap tolerance: {analyzer.session_gap_minutes} minutes")
    print(f"Configuration-driven: {analyzer.config is not None}")
