"""
Location Analyzer
Processes and analyzes location data from Owntracks to provide insights and patterns.
"""

import json
import math
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
from collections import defaultdict, Counter
from pathlib import Path
import logging
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

# Import activity analyzers
try:
    from ..analyzers.golf_analyzer import GolfAnalyzer
    from ..analyzers.snowboarding_analyzer import SnowboardingAnalyzer
    from ..analyzers.parkrun_analyzer import ParkrunAnalyzer
    from ..analyzers.dog_walking_analyzer import DogWalkingAnalyzer
except ImportError:
    # Fallback for direct execution
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from analyzers.golf_analyzer import GolfAnalyzer
    from analyzers.snowboarding_analyzer import SnowboardingAnalyzer
    from analyzers.parkrun_analyzer import ParkrunAnalyzer
    from analyzers.dog_walking_analyzer import DogWalkingAnalyzer


class LocationAnalyzer:
    """Analyzes location data to provide insights and patterns"""

    def __init__(self, base_locations_path: Optional[str] = None,
                 trip_locations_path: Optional[str] = None):
        """
        Initialize the location analyzer

        Args:
            base_locations_path: Path to base locations JSON file (optional)
            trip_locations_path: Path to trip-specific locations JSON file (optional)
        """
        self.logger = logging.getLogger(__name__)
        self.geocoder = Nominatim(user_agent="GavinLocationAgent/1.0")

        # Default to locations directory (parent of core/)
        default_locations_dir = Path(__file__).parent.parent / "locations"

        # Initialize location databases
        self.base_locations = {}
        self.trip_locations = {}
        self.known_locations = {}  # Combined dictionary for backward compatibility

        # Load base locations
        if base_locations_path is None:
            base_locations_path = default_locations_dir / "base_locations.json"
        self._load_base_locations(base_locations_path)

        # Load trip locations if provided
        if trip_locations_path:
            self._load_trip_locations(trip_locations_path)

        # Activity analyzers (lazy initialization to avoid circular dependencies)
        self._golf_analyzer = None
        self._snowboarding_analyzer = None
        self._parkrun_analyzer = None
        self._dog_walking_analyzer = None

    @property
    def golf_analyzer(self):
        """Lazy load golf analyzer to avoid circular dependencies"""
        if self._golf_analyzer is None:
            self._golf_analyzer = GolfAnalyzer()
        return self._golf_analyzer

    @property
    def snowboarding_analyzer(self):
        """Lazy load snowboarding analyzer to avoid circular dependencies"""
        if self._snowboarding_analyzer is None:
            self._snowboarding_analyzer = SnowboardingAnalyzer()
        return self._snowboarding_analyzer

    @property
    def parkrun_analyzer(self):
        """Lazy load parkrun analyzer to avoid circular dependencies"""
        if self._parkrun_analyzer is None:
            self._parkrun_analyzer = ParkrunAnalyzer()
        return self._parkrun_analyzer

    @property
    def dog_walking_analyzer(self):
        """Lazy load dog walking analyzer to avoid circular dependencies"""
        if self._dog_walking_analyzer is None:
            self._dog_walking_analyzer = DogWalkingAnalyzer()
        return self._dog_walking_analyzer

    def _load_base_locations(self, path: Union[str, Path]):
        """
        Load base locations from JSON file

        Args:
            path: Path to base locations JSON file
        """
        path = Path(path)
        if not path.exists():
            self.logger.warning(f"Base locations file not found: {path}")
            return

        try:
            with open(path, 'r') as f:
                data = json.load(f)

            for location in data.get('locations', []):
                location_id = location['id']
                self.base_locations[location_id] = {
                    'name': location['name'],
                    'coordinates': (location['coordinates']['lat'],
                                  location['coordinates']['lon']),
                    'radius': location.get('radius', 100),
                    'type': location.get('type', 'unknown'),
                    'activities': location.get('activities', []),
                    'tags': location.get('tags', []),
                    'notes': location.get('notes', ''),
                    'timezone': location.get('timezone', data.get('timezone', 'UTC'))
                }

            # Update known_locations for backward compatibility
            self.known_locations.update(self.base_locations)

            self.logger.info(f"Loaded {len(self.base_locations)} base locations from {path}")

        except Exception as e:
            self.logger.error(f"Error loading base locations from {path}: {e}")

    def _load_trip_locations(self, path: Union[str, Path]):
        """
        Load trip-specific locations from JSON file

        Args:
            path: Path to trip locations JSON file
        """
        path = Path(path)
        if not path.exists():
            self.logger.warning(f"Trip locations file not found: {path}")
            return

        try:
            with open(path, 'r') as f:
                data = json.load(f)

            self.trip_info = {
                'name': data.get('trip_name', 'Unknown Trip'),
                'dates': data.get('trip_dates', {}),
                'timezone': data.get('timezone', 'UTC'),
                'description': data.get('description', '')
            }

            for location in data.get('locations', []):
                location_id = location['id']
                self.trip_locations[location_id] = {
                    'name': location['name'],
                    'coordinates': (location['coordinates']['lat'],
                                  location['coordinates']['lon']),
                    'radius': location.get('radius', 100),
                    'type': location.get('type', 'unknown'),
                    'venue_type': location.get('venue_type', ''),
                    'activities': location.get('activities', []),
                    'tags': location.get('tags', []),
                    'notes': location.get('notes', ''),
                    'venue_details': location.get('venue_details', {}),
                    'timezone': location.get('timezone', data.get('timezone', 'UTC'))
                }

            # Update known_locations with trip locations (trip locations take priority)
            self.known_locations.update(self.trip_locations)

            self.logger.info(f"Loaded {len(self.trip_locations)} trip locations from {path}")
            self.logger.info(f"Trip: {self.trip_info['name']} ({self.trip_info['dates'].get('start')} to {self.trip_info['dates'].get('end')})")

        except Exception as e:
            self.logger.error(f"Error loading trip locations from {path}: {e}")

    def load_trip(self, trip_name: str):
        """
        Load a specific trip's location database

        Args:
            trip_name: Name of trip JSON file (e.g., 'portugal_2025-10')
        """
        trips_dir = Path(__file__).parent.parent / "locations" / "trips"
        trip_path = trips_dir / f"{trip_name}.json"
        self._load_trip_locations(trip_path)

    def get_all_locations(self) -> Dict:
        """
        Get all loaded locations (base + trip)

        Returns:
            Dictionary of all known locations
        """
        return self.known_locations

    def get_location_info(self, location_id: str) -> Optional[Dict]:
        """
        Get information about a specific location

        Args:
            location_id: Location identifier

        Returns:
            Location information dictionary or None
        """
        return self.known_locations.get(location_id)
    
    def calculate_distance(self, point1: Tuple[float, float], 
                          point2: Tuple[float, float]) -> float:
        """
        Calculate distance between two geographic points
        
        Args:
            point1: (latitude, longitude) tuple
            point2: (latitude, longitude) tuple
            
        Returns:
            Distance in meters
        """
        return geodesic(point1, point2).meters
    
    def is_at_location(self, location_point: Tuple[float, float],
                      target_location: Tuple[float, float],
                      radius_meters: float = 100) -> bool:
        """
        Check if a location point is within radius of target location
        
        Args:
            location_point: (latitude, longitude) of point to check
            target_location: (latitude, longitude) of target
            radius_meters: Radius threshold in meters
            
        Returns:
            True if within radius
        """
        distance = self.calculate_distance(location_point, target_location)
        return distance <= radius_meters
    
    def extract_coordinates(self, location_data: Dict) -> Optional[Tuple[float, float]]:
        """
        Extract latitude/longitude from Owntracks location data
        
        Args:
            location_data: Single location record from Owntracks
            
        Returns:
            (latitude, longitude) tuple or None if invalid
        """
        try:
            lat = location_data.get('lat')
            lon = location_data.get('lon')
            
            if lat is not None and lon is not None:
                return (float(lat), float(lon))
            return None
            
        except (ValueError, TypeError):
            return None
    
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
    
    def analyze_time_at_location(self, locations: List[Dict],
                                target_coordinates: Tuple[float, float],
                                radius_meters: float = 100,
                                min_duration_minutes: int = 5) -> Dict:
        """
        Analyze time spent at a specific location
        
        Args:
            locations: List of location records from Owntracks
            target_coordinates: (latitude, longitude) of target location
            radius_meters: Radius to consider as "at location"
            min_duration_minutes: Minimum duration to count as a visit
            
        Returns:
            Dictionary with time analysis results
        """
        if not locations:
            return {'total_time': 0, 'visits': [], 'error': 'No location data provided'}
        
        visits = []
        current_visit = None
        total_time_seconds = 0
        
        # Sort locations by timestamp
        sorted_locations = sorted(locations, key=lambda x: x.get('tst', 0))
        
        for location in sorted_locations:
            coords = self.extract_coordinates(location)
            timestamp = self.parse_timestamp(location.get('tst'))
            
            if not coords or not timestamp:
                continue
            
            is_at_target = self.is_at_location(coords, target_coordinates, radius_meters)
            
            if is_at_target:
                if current_visit is None:
                    # Start of new visit
                    current_visit = {
                        'start_time': timestamp,
                        'end_time': timestamp,
                        'start_coords': coords,
                        'end_coords': coords
                    }
                else:
                    # Continue current visit
                    current_visit['end_time'] = timestamp
                    current_visit['end_coords'] = coords
            else:
                if current_visit is not None:
                    # End of current visit
                    duration = (current_visit['end_time'] - current_visit['start_time']).total_seconds()
                    
                    if duration >= min_duration_minutes * 60:
                        current_visit['duration_seconds'] = duration
                        current_visit['duration_minutes'] = duration / 60
                        visits.append(current_visit)
                        total_time_seconds += duration
                    
                    current_visit = None
        
        # Handle case where visit extends to end of data
        if current_visit is not None:
            duration = (current_visit['end_time'] - current_visit['start_time']).total_seconds()
            if duration >= min_duration_minutes * 60:
                current_visit['duration_seconds'] = duration
                current_visit['duration_minutes'] = duration / 60
                visits.append(current_visit)
                total_time_seconds += duration
        
        return {
            'target_location': target_coordinates,
            'radius_meters': radius_meters,
            'total_time_seconds': total_time_seconds,
            'total_time_hours': total_time_seconds / 3600,
            'visit_count': len(visits),
            'visits': visits,
            'average_visit_duration_minutes': (total_time_seconds / 60) / len(visits) if visits else 0
        }
    
    def identify_frequent_locations(self, locations: List[Dict],
                                   min_visits: int = 3,
                                   radius_meters: float = 100) -> List[Dict]:
        """
        Identify frequently visited locations from location data
        
        Args:
            locations: List of location records
            min_visits: Minimum number of visits to consider frequent
            radius_meters: Radius for clustering nearby points
            
        Returns:
            List of frequent locations with visit counts
        """
        if not locations:
            return []
        
        # Cluster nearby locations
        location_clusters = []
        
        for location in locations:
            coords = self.extract_coordinates(location)
            if not coords:
                continue
            
            # Find existing cluster or create new one
            added_to_cluster = False
            for cluster in location_clusters:
                if self.is_at_location(coords, cluster['center'], radius_meters):
                    cluster['points'].append(coords)
                    cluster['count'] += 1
                    # Update cluster center to centroid
                    avg_lat = sum(p[0] for p in cluster['points']) / len(cluster['points'])
                    avg_lon = sum(p[1] for p in cluster['points']) / len(cluster['points'])
                    cluster['center'] = (avg_lat, avg_lon)
                    added_to_cluster = True
                    break
            
            if not added_to_cluster:
                location_clusters.append({
                    'center': coords,
                    'points': [coords],
                    'count': 1
                })
        
        # Filter by minimum visits and sort by frequency
        frequent_locations = [
            cluster for cluster in location_clusters 
            if cluster['count'] >= min_visits
        ]
        frequent_locations.sort(key=lambda x: x['count'], reverse=True)
        
        # Add geocoding for top locations
        for location in frequent_locations[:10]:  # Only geocode top 10
            try:
                geocoded = self.geocoder.reverse(location['center'])
                location['address'] = geocoded.address if geocoded else 'Unknown'
            except Exception as e:
                location['address'] = 'Geocoding failed'
                self.logger.warning(f"Geocoding failed for {location['center']}: {e}")
        
        return frequent_locations
    
    def analyze_daily_pattern(self, locations: List[Dict], target_date: datetime) -> Dict:
        """
        Analyze location pattern for a specific day
        
        Args:
            locations: List of location records
            target_date: Date to analyze
            
        Returns:
            Dictionary with daily pattern analysis
        """
        # Filter locations for target date
        target_day_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        target_day_end = target_day_start + timedelta(days=1)
        
        day_locations = []
        for location in locations:
            # Skip if location is not a dict (sometimes API returns strings)
            if not isinstance(location, dict):
                continue
                
            timestamp = self.parse_timestamp(location.get('tst'))
            if timestamp and target_day_start <= timestamp < target_day_end:
                day_locations.append(location)
        
        if not day_locations:
            return {'error': f'No location data for {target_date.strftime("%Y-%m-%d")}'}
        
        # Sort by time
        day_locations.sort(key=lambda x: x.get('tst', 0))
        
        # Analyze pattern
        pattern = {
            'date': target_date.strftime('%Y-%m-%d'),
            'location_count': len(day_locations),
            'first_location': None,
            'last_location': None,
            'time_at_known_locations': {},
            'movement_summary': []
        }
        
        if day_locations:
            first_loc = day_locations[0]
            last_loc = day_locations[-1]
            
            pattern['first_location'] = {
                'time': self.parse_timestamp(first_loc.get('tst')).strftime('%H:%M'),
                'coordinates': self.extract_coordinates(first_loc)
            }
            
            pattern['last_location'] = {
                'time': self.parse_timestamp(last_loc.get('tst')).strftime('%H:%M'),
                'coordinates': self.extract_coordinates(last_loc)
            }
        
        # Analyze time at known locations
        for location_name, location_info in self.known_locations.items():
            if location_info['coordinates']:
                time_analysis = self.analyze_time_at_location(
                    day_locations,
                    location_info['coordinates'],
                    location_info['radius']
                )
                pattern['time_at_known_locations'][location_name] = {
                    'total_hours': round(time_analysis['total_time_hours'], 2),
                    'visit_count': time_analysis['visit_count'],
                    'visits': time_analysis['visits']
                }

        # Detect activities for this day
        pattern['detected_activities'] = self.detect_activities(day_locations, target_date)

        # Generate timeline with location names (including geocoded unknown locations)
        pattern['timeline'] = self._generate_daily_timeline(day_locations)

        # Compute primary location (where most time was spent - from known locations OR timeline)
        pattern['primary_location'] = self._compute_primary_location(
            pattern['time_at_known_locations'],
            pattern.get('timeline', [])
        )

        # Compute day type based on location patterns
        pattern['day_type'] = self._compute_day_type(
            pattern['time_at_known_locations'],
            target_date.weekday(),
            pattern['detected_activities']
        )

        return pattern

    def _generate_daily_timeline(self, day_locations: List[Dict],
                                   cluster_radius_meters: float = 150,
                                   min_stay_minutes: int = 5) -> List[Dict]:
        """
        Generate a timeline of location segments for the day using a cluster-first approach.

        Process:
        1. First pass: Cluster consecutive GPS points into stay segments (fast, no API calls)
        2. Second pass: Match clusters to known locations OR geocode cluster centroids only

        This dramatically reduces geocoding calls from 4000+ to typically 5-15 per day.

        Args:
            day_locations: Sorted list of location records for one day
            cluster_radius_meters: Radius to consider as same location (default 150m)
            min_stay_minutes: Minimum duration to include in timeline (default 5 min)

        Returns:
            List of timeline segments with location names and durations
        """
        if not day_locations:
            return []

        # PHASE 1: Cluster consecutive points into stay segments (no geocoding yet)
        raw_segments = []
        current_cluster = None

        for loc in day_locations:
            coords = self.extract_coordinates(loc)
            timestamp = self.parse_timestamp(loc.get('tst'))

            if not coords or not timestamp:
                continue

            if current_cluster is None:
                # Start first cluster
                current_cluster = {
                    'start_time': timestamp,
                    'end_time': timestamp,
                    'points': [coords],
                    'centroid': coords
                }
            else:
                # Check if this point is within cluster radius of current centroid
                if self.is_at_location(coords, current_cluster['centroid'], cluster_radius_meters):
                    # Extend current cluster
                    current_cluster['end_time'] = timestamp
                    current_cluster['points'].append(coords)
                    # Update centroid
                    avg_lat = sum(p[0] for p in current_cluster['points']) / len(current_cluster['points'])
                    avg_lon = sum(p[1] for p in current_cluster['points']) / len(current_cluster['points'])
                    current_cluster['centroid'] = (avg_lat, avg_lon)
                else:
                    # Save current cluster and start new one
                    duration_seconds = (current_cluster['end_time'] - current_cluster['start_time']).total_seconds()
                    if duration_seconds >= min_stay_minutes * 60:
                        raw_segments.append(current_cluster)

                    current_cluster = {
                        'start_time': timestamp,
                        'end_time': timestamp,
                        'points': [coords],
                        'centroid': coords
                    }

        # Don't forget last cluster
        if current_cluster:
            duration_seconds = (current_cluster['end_time'] - current_cluster['start_time']).total_seconds()
            if duration_seconds >= min_stay_minutes * 60:
                raw_segments.append(current_cluster)

        # PHASE 2: Name each cluster (known locations first, then geocode centroids only)
        timeline = []
        geocode_cache = {}

        for segment in raw_segments:
            centroid = segment['centroid']

            # Try to match to a known location first
            location_name = None
            location_type = None
            for loc_id, loc_info in self.known_locations.items():
                if self.is_at_location(centroid, loc_info['coordinates'], loc_info['radius']):
                    location_name = loc_info['name']
                    location_type = loc_info.get('type', 'unknown')
                    break

            # If no known location matched, geocode the centroid only
            if not location_name:
                # Round to 3 decimal places (~100m) for cache key
                cache_key = (round(centroid[0], 3), round(centroid[1], 3))
                if cache_key in geocode_cache:
                    location_name = geocode_cache[cache_key]
                else:
                    try:
                        geocoded = self.geocoder.reverse(centroid, timeout=5)
                        if geocoded:
                            address = geocoded.raw.get('address', {})
                            # Try to get a meaningful short name
                            location_name = (
                                address.get('amenity') or
                                address.get('building') or
                                address.get('road') or
                                address.get('suburb') or
                                address.get('city') or
                                address.get('town') or
                                address.get('village') or
                                'Unknown'
                            )
                            # Add area context if available
                            area = address.get('suburb') or address.get('city') or address.get('town')
                            if area and area != location_name:
                                location_name = f"{location_name}, {area}"
                        else:
                            location_name = f"Location ({centroid[0]:.3f}, {centroid[1]:.3f})"
                        geocode_cache[cache_key] = location_name
                    except Exception as e:
                        self.logger.debug(f"Geocoding failed for {centroid}: {e}")
                        location_name = f"Location ({centroid[0]:.3f}, {centroid[1]:.3f})"
                        geocode_cache[cache_key] = location_name
                location_type = 'geocoded'

            # Calculate duration and format times
            duration_seconds = (segment['end_time'] - segment['start_time']).total_seconds()

            timeline.append({
                'start_time': segment['start_time'].strftime('%H:%M'),
                'end_time': segment['end_time'].strftime('%H:%M'),
                'location_name': location_name,
                'location_type': location_type,
                'coordinates': centroid,
                'duration_minutes': round(duration_seconds / 60),
                'point_count': len(segment['points'])
            })

        # Merge consecutive segments at same location
        merged_timeline = []
        for segment in timeline:
            if merged_timeline and merged_timeline[-1]['location_name'] == segment['location_name']:
                # Merge with previous
                merged_timeline[-1]['end_time'] = segment['end_time']
                merged_timeline[-1]['duration_minutes'] += segment['duration_minutes']
                merged_timeline[-1]['point_count'] += segment['point_count']
            else:
                merged_timeline.append(segment)

        return merged_timeline

    def _compute_primary_location(self, time_at_known_locations: Dict,
                                    timeline: List[Dict] = None) -> str:
        """
        Determine the primary location based on where most time was spent.

        Args:
            time_at_known_locations: Dictionary of time spent at each known location
            timeline: Optional timeline segments with duration_minutes

        Returns:
            Name of primary location or 'Unknown'
        """
        max_hours = 0
        primary = 'Unknown'

        # First check known locations
        for loc_name, loc_data in time_at_known_locations.items():
            hours = loc_data.get('total_hours', 0)
            if hours > max_hours and hours >= 1.0:
                max_hours = hours
                primary = loc_name

        # If no known location found, check timeline segments (including geocoded)
        if primary == 'Unknown' and timeline:
            for segment in timeline:
                hours = segment.get('duration_minutes', 0) / 60
                if hours > max_hours and hours >= 1.0:
                    max_hours = hours
                    primary = segment.get('location_name', 'Unknown')

        return primary

    def _compute_day_type(self, time_at_known_locations: Dict,
                          weekday: int, detected_activities: List[Dict]) -> str:
        """
        Determine the type of day based on location patterns and activities.

        Args:
            time_at_known_locations: Dictionary of time spent at each known location
            weekday: Day of week (0=Monday, 6=Sunday)
            detected_activities: List of detected activities

        Returns:
            Day type string (e.g., 'work_office', 'work_wfh', 'weekend', 'travel', 'mixed')
        """
        # Extract hours at key locations
        home_hours = time_at_known_locations.get('home', {}).get('total_hours', 0)
        office_hours = time_at_known_locations.get('office', {}).get('total_hours', 0)

        # Check for detected activities
        has_parkrun = any(a.get('activity_type') == 'parkrun' for a in detected_activities)
        has_golf = any(a.get('activity_type') == 'golf' for a in detected_activities)
        has_dog_walk = any(a.get('activity_type') == 'dog_walking' for a in detected_activities)

        # Weekend logic
        is_weekend = weekday >= 5  # Saturday or Sunday

        if is_weekend:
            if has_parkrun:
                return 'weekend_parkrun'
            elif has_golf:
                return 'weekend_golf'
            elif home_hours > 6:
                return 'weekend_home'
            else:
                return 'weekend_out'

        # Weekday logic
        if office_hours >= 4:
            return 'work_office'
        elif home_hours >= 6:
            return 'work_wfh'
        elif office_hours > 0 and home_hours > 0:
            return 'work_mixed'
        elif has_golf:
            return 'golf_day'
        else:
            # Check if mostly travel/unknown
            total_known_hours = sum(
                loc.get('total_hours', 0) for loc in time_at_known_locations.values()
            )
            if total_known_hours < 4:
                return 'travel_day'
            return 'mixed'

    def _auto_load_trip_for_date(self, target_date: datetime):
        """
        Automatically load trip locations if the target date falls within a trip period

        Args:
            target_date: Date being analyzed
        """
        trips_dir = Path(__file__).parent.parent / "locations" / "trips"
        if not trips_dir.exists():
            return

        # Check all trip files
        for trip_file in trips_dir.glob("*.json"):
            try:
                with open(trip_file, 'r') as f:
                    trip_data = json.load(f)

                trip_dates = trip_data.get('trip_dates', {})
                if not trip_dates:
                    continue

                # Parse trip dates
                start_str = trip_dates.get('start')
                end_str = trip_dates.get('end')

                if start_str and end_str:
                    trip_start = datetime.strptime(start_str, '%Y-%m-%d').date()
                    trip_end = datetime.strptime(end_str, '%Y-%m-%d').date()
                    target_date_only = target_date.date()

                    # Check if target date falls within trip
                    if trip_start <= target_date_only <= trip_end:
                        self.logger.info(f"Auto-loading trip {trip_file.stem} for date {target_date_only}")
                        self._load_trip_locations(trip_file)
                        return  # Only load one trip

            except Exception as e:
                self.logger.debug(f"Error checking trip file {trip_file}: {e}")

    def detect_activities(self, locations: List[Dict], target_date: datetime) -> List[Dict]:
        """
        Detect activities (golf, snowboarding, parkrun, dog walking) from location data

        Args:
            locations: List of location records for the day
            target_date: Date being analyzed

        Returns:
            List of detected activities with details
        """
        detected = []

        if not locations:
            return detected

        # Auto-load trip locations if date falls within a trip
        self._auto_load_trip_for_date(target_date)

        # Find relevant golf courses from known locations
        golf_course = None
        for loc_id, loc_info in self.known_locations.items():
            if 'golf' in loc_info.get('activities', []) or 'golf' in loc_info.get('type', '').lower():
                golf_course = {
                    'name': loc_info['name'],
                    'coordinates': loc_info['coordinates'],
                    'radius': loc_info['radius']
                }
                break

        # Detect golf
        try:
            golf_sessions = self.golf_analyzer.detect_sessions(locations, golf_course)
            for session in golf_sessions:
                detected.append({
                    'activity_type': 'golf',
                    'start_time': session.start_time.strftime('%H:%M') if hasattr(session.start_time, 'strftime') else str(session.start_time),
                    'end_time': session.end_time.strftime('%H:%M') if hasattr(session.end_time, 'strftime') else str(session.end_time),
                    'duration_hours': round(session.duration_hours, 1),
                    'confidence': session.confidence,
                    'venue': golf_course['name'] if golf_course else 'Unknown golf course'
                })
        except Exception as e:
            self.logger.debug(f"Golf detection failed: {e}")

        # Detect snowboarding
        try:
            snowboarding_sessions = self.snowboarding_analyzer.detect_sessions(locations)
            for session in snowboarding_sessions:
                venue_name = 'Unknown ski resort'
                if hasattr(session, 'venue') and session.venue:
                    venue_name = session.venue.get('name', venue_name)

                detected.append({
                    'activity_type': 'snowboarding',
                    'start_time': session.start_time.strftime('%H:%M') if hasattr(session.start_time, 'strftime') else str(session.start_time),
                    'end_time': session.end_time.strftime('%H:%M') if hasattr(session.end_time, 'strftime') else str(session.end_time),
                    'duration_hours': round(session.duration_hours, 1),
                    'runs': getattr(session, 'run_count', 0),
                    'vertical_meters': getattr(session, 'total_vertical', 0),
                    'confidence': session.confidence,
                    'venue': venue_name
                })
        except Exception as e:
            self.logger.debug(f"Snowboarding detection failed: {e}")

        # Detect parkrun
        try:
            parkrun_sessions = self.parkrun_analyzer.detect_sessions(locations)
            for session in parkrun_sessions:
                venue_name = 'Unknown parkrun'
                if hasattr(session, 'venue') and session.venue:
                    venue_name = session.venue.get('name', venue_name)

                detected.append({
                    'activity_type': 'parkrun',
                    'start_time': session.start_time.strftime('%H:%M') if hasattr(session.start_time, 'strftime') else str(session.start_time),
                    'end_time': session.end_time.strftime('%H:%M') if hasattr(session.end_time, 'strftime') else str(session.end_time),
                    'duration_hours': round(session.duration_hours, 1),
                    'confidence': session.confidence,
                    'venue': venue_name
                })
        except Exception as e:
            self.logger.debug(f"Parkrun detection failed: {e}")

        # Detect dog walking
        try:
            dog_walk_sessions = self.dog_walking_analyzer.detect_sessions(locations)
            for session in dog_walk_sessions:
                detected.append({
                    'activity_type': 'dog_walking',
                    'start_time': session.start_time.strftime('%H:%M') if hasattr(session.start_time, 'strftime') else str(session.start_time),
                    'end_time': session.end_time.strftime('%H:%M') if hasattr(session.end_time, 'strftime') else str(session.end_time),
                    'duration_hours': round(session.duration_hours, 1),
                    'confidence': session.confidence
                })
        except Exception as e:
            self.logger.debug(f"Dog walking detection failed: {e}")

        # Sort by start time
        detected.sort(key=lambda x: x['start_time'])

        return detected

    def detect_commute_pattern(self, locations: List[Dict],
                              days_to_analyze: int = 30) -> Dict:
        """
        Detect Gavin's commute patterns
        
        Args:
            locations: List of location records
            days_to_analyze: Number of recent days to analyze
            
        Returns:
            Dictionary with commute pattern analysis
        """
        # Filter to recent days
        cutoff_date = datetime.now() - timedelta(days=days_to_analyze)
        recent_locations = [
            loc for loc in locations
            if self.parse_timestamp(loc.get('tst', 0)) and
               self.parse_timestamp(loc.get('tst', 0)) >= cutoff_date
        ]
        
        if not recent_locations:
            return {'error': 'No recent location data available'}
        
        # Group by date
        daily_patterns = defaultdict(list)
        for location in recent_locations:
            timestamp = self.parse_timestamp(location.get('tst'))
            if timestamp:
                date_key = timestamp.strftime('%Y-%m-%d')
                daily_patterns[date_key].append(location)
        
        # Analyze each day
        office_days = []
        home_days = []
        
        for date_str, day_locations in daily_patterns.items():
            day_analysis = self.analyze_daily_pattern(
                day_locations, 
                datetime.strptime(date_str, '%Y-%m-%d')
            )
            
            # Determine if it's an office day or home day
            office_time = day_analysis.get('time_at_known_locations', {}).get('office', {}).get('total_hours', 0)
            home_time = day_analysis.get('time_at_known_locations', {}).get('home', {}).get('total_hours', 0)
            
            day_info = {
                'date': date_str,
                'weekday': datetime.strptime(date_str, '%Y-%m-%d').strftime('%A'),
                'office_hours': office_time,
                'home_hours': home_time,
                'pattern': day_analysis
            }
            
            if office_time > 4:  # More than 4 hours at office
                office_days.append(day_info)
            elif home_time > 8:  # More than 8 hours at home (likely WFH)
                home_days.append(day_info)
        
        # Calculate statistics
        total_weekdays = len([d for d in daily_patterns.keys() 
                             if datetime.strptime(d, '%Y-%m-%d').weekday() < 5])
        
        commute_analysis = {
            'analysis_period_days': days_to_analyze,
            'total_weekdays': total_weekdays,
            'office_days': len(office_days),
            'home_days': len(home_days),
            'office_percentage': (len(office_days) / total_weekdays * 100) if total_weekdays > 0 else 0,
            'home_percentage': (len(home_days) / total_weekdays * 100) if total_weekdays > 0 else 0,
            'average_office_hours': sum(d['office_hours'] for d in office_days) / len(office_days) if office_days else 0,
            'office_day_details': office_days,
            'home_day_details': home_days
        }
        
        return commute_analysis
    
    def geocode_location(self, coordinates: Tuple[float, float]) -> str:
        """
        Convert coordinates to human-readable address
        
        Args:
            coordinates: (latitude, longitude) tuple
            
        Returns:
            Human-readable address string
        """
        try:
            location = self.geocoder.reverse(coordinates)
            return location.address if location else f"Unknown location {coordinates}"
        except Exception as e:
            self.logger.warning(f"Geocoding failed for {coordinates}: {e}")
            return f"Coordinates: {coordinates[0]:.4f}, {coordinates[1]:.4f}"
    
    def find_location_at_time(self, locations: List[Dict], 
                             target_time: datetime,
                             tolerance_minutes: int = 30) -> Optional[Dict]:
        """
        Find location at or near a specific time
        
        Args:
            locations: List of location records
            target_time: Time to search for
            tolerance_minutes: How many minutes before/after to search
            
        Returns:
            Closest location record or None
        """
        if not locations:
            return None
        
        closest_location = None
        min_time_diff = float('inf')
        
        for location in locations:
            timestamp = self.parse_timestamp(location.get('tst'))
            if not timestamp:
                continue
            
            time_diff = abs((timestamp - target_time).total_seconds())
            
            if time_diff < min_time_diff and time_diff <= tolerance_minutes * 60:
                min_time_diff = time_diff
                closest_location = location
        
        if closest_location:
            coords = self.extract_coordinates(closest_location)
            return {
                'timestamp': self.parse_timestamp(closest_location.get('tst')),
                'coordinates': coords,
                'address': self.geocode_location(coords) if coords else None,
                'time_difference_minutes': min_time_diff / 60,
                'raw_data': closest_location
            }
        
        return None

    def filter_by_time_period(self, locations: List[Dict],
                              period: str,
                              config_path: Optional[str] = None) -> List[Dict]:
        """
        Filter locations to only those within a specific time period

        Args:
            locations: List of location records
            period: Time period name ('morning', 'afternoon', 'evening', 'night')
            config_path: Optional path to analysis config (defaults to standard location)

        Returns:
            Filtered list of locations within the time period
        """
        # Load time periods from config
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'analysis_config.json'

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            time_periods = config.get('time_periods', {})
        except FileNotFoundError:
            self.logger.warning(f"Config file not found: {config_path}, using defaults")
            time_periods = {
                'morning': {'start': '06:00', 'end': '12:00'},
                'afternoon': {'start': '12:00', 'end': '18:00'},
                'evening': {'start': '18:00', 'end': '22:00'},
                'night': {'start': '22:00', 'end': '06:00'}
            }

        period_config = time_periods.get(period)
        if not period_config:
            self.logger.error(f"Unknown time period: {period}")
            return locations

        # Parse time window
        start_time = datetime.strptime(period_config['start'], '%H:%M').time()
        end_time = datetime.strptime(period_config['end'], '%H:%M').time()

        filtered = []
        for loc in locations:
            timestamp = self.parse_timestamp(loc.get('tst'))
            if not timestamp:
                continue

            loc_time = timestamp.time()

            # Handle periods that cross midnight
            if start_time < end_time:
                in_period = start_time <= loc_time < end_time
            else:  # Crosses midnight (e.g., night period)
                in_period = loc_time >= start_time or loc_time < end_time

            if in_period:
                filtered.append(loc)

        return filtered

    def filter_by_custom_time_range(self, locations: List[Dict],
                                    start_time: str,
                                    end_time: str) -> List[Dict]:
        """
        Filter locations to only those within a custom time range

        Args:
            locations: List of location records
            start_time: Start time in 'HH:MM' format
            end_time: End time in 'HH:MM' format

        Returns:
            Filtered list of locations within the time range
        """
        try:
            start = datetime.strptime(start_time, '%H:%M').time()
            end = datetime.strptime(end_time, '%H:%M').time()
        except ValueError as e:
            self.logger.error(f"Invalid time format: {e}")
            return locations

        filtered = []
        for loc in locations:
            timestamp = self.parse_timestamp(loc.get('tst'))
            if not timestamp:
                continue

            loc_time = timestamp.time()

            # Handle ranges that cross midnight
            if start < end:
                in_range = start <= loc_time < end
            else:
                in_range = loc_time >= start or loc_time < end

            if in_range:
                filtered.append(loc)

        return filtered

    def get_time_period_summary(self, locations: List[Dict],
                               config_path: Optional[str] = None) -> Dict:
        """
        Summarize location data by time period

        Args:
            locations: List of location records
            config_path: Optional path to analysis config

        Returns:
            Dictionary with counts and percentages for each time period
        """
        summary = {}
        total = len(locations)

        if total == 0:
            return summary

        for period in ['morning', 'afternoon', 'evening', 'night']:
            filtered = self.filter_by_time_period(locations, period, config_path)
            count = len(filtered)
            summary[period] = {
                'count': count,
                'percentage': round((count / total) * 100, 1) if total > 0 else 0
            }

        return summary


def create_location_analyzer() -> LocationAnalyzer:
    """
    Factory function to create a LocationAnalyzer instance
    
    Returns:
        Configured LocationAnalyzer instance
    """
    return LocationAnalyzer()


if __name__ == "__main__":
    # Example usage and testing
    analyzer = create_location_analyzer()
    
    # Test with mock data
    mock_locations = [
        {
            'lat': 51.3712,
            'lon': -0.3648,
            'tst': 1642680000,  # Mock timestamp
            'acc': 10
        },
        {
            'lat': 51.5074,
            'lon': -0.1278,
            'tst': 1642690000,
            'acc': 15
        }
    ]
    
    print("Testing LocationAnalyzer with mock data...")
    
    # Test coordinate extraction
    coords = analyzer.extract_coordinates(mock_locations[0])
    print(f"Extracted coordinates: {coords}")
    
    # Test distance calculation
    if len(mock_locations) >= 2:
        coords1 = analyzer.extract_coordinates(mock_locations[0])
        coords2 = analyzer.extract_coordinates(mock_locations[1])
        if coords1 and coords2:
            distance = analyzer.calculate_distance(coords1, coords2)
            print(f"Distance between points: {distance:.0f} meters")
    
    print("\nLocationAnalyzer test completed successfully!")