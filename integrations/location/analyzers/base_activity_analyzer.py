"""
Base Activity Analyzer
Abstract base class for all specialized activity analyzers.

Provides common interface and shared functionality for activity detection.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@dataclass
class ActivitySession:
    """
    Represents a detected activity session

    All activity analyzers should return sessions in this format
    """
    activity_type: str  # 'golf', 'parkrun', 'dog_walking', 'commute', etc.
    start_time: datetime
    end_time: datetime
    duration_hours: float
    location_name: str
    location_coords: Tuple[float, float]
    confidence: str  # 'HIGH', 'MEDIUM', 'LOW', 'CONFIRMED'
    confidence_score: float  # 0.0-1.0
    details: Dict  # Activity-specific metadata

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'activity_type': self.activity_type,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_hours': round(self.duration_hours, 2),
            'location': {
                'name': self.location_name,
                'coordinates': self.location_coords
            },
            'confidence': self.confidence,
            'confidence_score': round(self.confidence_score, 2),
            'details': self.details
        }


class BaseActivityAnalyzer(ABC):
    """
    Abstract base class for activity analyzers

    All specialized analyzers (Golf, Parkrun, DogWalking, etc.) should extend this class
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize base analyzer

        Args:
            config_path: Path to analysis_config.json file
        """
        self.config = self._load_config(config_path)
        self.activity_type = self._get_activity_type()
        self.activity_config = self.config.get('activity_analyzers', {}).get(self.activity_type, {})
        self.enabled = self.activity_config.get('enabled', True)

        # Initialize LocationAnalyzer for location-related operations
        try:
            from core.location_analyzer import LocationAnalyzer
            self.location_analyzer = LocationAnalyzer()
        except ImportError:
            # LocationAnalyzer not available - some features may be limited
            self.location_analyzer = None

    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load analysis configuration"""
        if config_path is None:
            # Default to config/analysis_config.json relative to this file
            config_path = Path(__file__).parent.parent / 'config' / 'analysis_config.json'

        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return empty config if file doesn't exist
            return {}

    @abstractmethod
    def _get_activity_type(self) -> str:
        """
        Return the activity type string

        Returns:
            Activity type (e.g., 'golf', 'parkrun', 'dog_walking')
        """
        pass

    @abstractmethod
    def detect_sessions(self, locations: List[Dict], **kwargs) -> List[ActivitySession]:
        """
        Detect activity sessions from location data

        Args:
            locations: List of location records from Owntracks
            **kwargs: Activity-specific parameters (e.g., golf_course_location)

        Returns:
            List of detected activity sessions
        """
        pass

    def get_confidence_label(self, score: float) -> str:
        """
        Convert confidence score to label

        Args:
            score: Confidence score (0.0-1.0)

        Returns:
            Confidence label ('HIGH', 'MEDIUM', 'LOW')
        """
        thresholds = self.config.get('confidence_thresholds', {
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4
        })

        if score >= thresholds['high']:
            return 'HIGH'
        elif score >= thresholds['medium']:
            return 'MEDIUM'
        else:
            return 'LOW'

    def get_velocity_classification(self, velocity_mps: float) -> str:
        """
        Classify velocity into category

        Args:
            velocity_mps: Velocity in meters per second

        Returns:
            Velocity category ('stationary', 'walking', 'running', 'cycling', 'driving', 'flying')
        """
        velocity_config = self.config.get('velocity_classification', {})

        for category, params in velocity_config.items():
            min_vel = params.get('min_mps', 0)
            max_vel = params.get('max_mps', float('inf'))

            if min_vel <= velocity_mps < max_vel:
                return category

        return 'unknown'

    def get_location_radius(self, location_type: str) -> float:
        """
        Get appropriate radius for location type

        Args:
            location_type: Type of location (e.g., 'golf_course', 'park', 'home')

        Returns:
            Radius in meters
        """
        location_config = self.config.get('location_matching', {})
        category_radii = location_config.get('category_specific_radius', {})

        return category_radii.get(
            location_type,
            location_config.get('default_radius_meters', 100)
        )

    def get_gap_tolerance(self) -> int:
        """
        Get session clustering gap tolerance for this activity

        Returns:
            Gap tolerance in minutes
        """
        clustering = self.config.get('session_clustering', {})
        activity_gaps = clustering.get('activity_specific_gaps', {})

        return activity_gaps.get(
            self.activity_type,
            clustering.get('default_gap_tolerance_minutes', 15)
        )

    def is_in_time_window(self, timestamp: datetime, window_key: str) -> bool:
        """
        Check if timestamp falls within a named time window

        Args:
            timestamp: Datetime to check
            window_key: Time window name ('morning', 'afternoon', 'evening', 'night')

        Returns:
            True if timestamp is in window
        """
        time_periods = self.config.get('time_periods', {})
        window = time_periods.get(window_key, {})

        if not window:
            return False

        # Parse time strings
        start_time = datetime.strptime(window['start'], '%H:%M').time()
        end_time = datetime.strptime(window['end'], '%H:%M').time()
        check_time = timestamp.time()

        # Handle windows that cross midnight
        if start_time < end_time:
            return start_time <= check_time < end_time
        else:  # Crosses midnight
            return check_time >= start_time or check_time < end_time

    def format_duration(self, duration_hours: float) -> str:
        """
        Format duration for human-readable output

        Args:
            duration_hours: Duration in hours

        Returns:
            Formatted string (e.g., "2h 30m")
        """
        hours = int(duration_hours)
        minutes = int((duration_hours - hours) * 60)

        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

    def get_config_value(self, key: str, default=None):
        """
        Get activity-specific configuration value

        Args:
            key: Configuration key
            default: Default value if not found

        Returns:
            Configuration value or default
        """
        return self.activity_config.get(key, default)

    def parse_timestamp(self, timestamp: Union[int, float, str]) -> Optional[datetime]:
        """
        Parse Owntracks timestamp to datetime object

        Args:
            timestamp: Unix timestamp (int/float) or ISO string

        Returns:
            datetime object or None if invalid
        """
        try:
            if isinstance(timestamp, (int, float)):
                return datetime.fromtimestamp(timestamp)
            elif isinstance(timestamp, str):
                # Try parsing ISO format
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return None

        except (ValueError, OSError):
            return None


def create_analyzer(analyzer_type: str, config_path: Optional[str] = None):
    """
    Factory function to create appropriate analyzer

    Args:
        analyzer_type: Type of analyzer ('golf', 'parkrun', etc.)
        config_path: Optional path to config file

    Returns:
        Analyzer instance
    """
    # Import here to avoid circular dependencies
    from .golf_analyzer import GolfAnalyzer

    analyzers = {
        'golf': GolfAnalyzer
    }

    analyzer_class = analyzers.get(analyzer_type)
    if analyzer_class is None:
        raise ValueError(f"Unknown analyzer type: {analyzer_type}")

    return analyzer_class(config_path)


if __name__ == "__main__":
    # Test configuration loading
    print("BaseActivityAnalyzer loaded successfully")
    print("Testing configuration access...")

    # This would be implemented by concrete subclass
    class TestAnalyzer(BaseActivityAnalyzer):
        def _get_activity_type(self) -> str:
            return 'golf'

        def detect_sessions(self, locations, **kwargs):
            return []

    analyzer = TestAnalyzer()
    print(f"Activity type: {analyzer.activity_type}")
    print(f"Enabled: {analyzer.enabled}")
    print(f"Gap tolerance: {analyzer.get_gap_tolerance()} minutes")
    print(f"Golf course radius: {analyzer.get_location_radius('golf_course')} meters")
    print("✓ BaseActivityAnalyzer working correctly")
