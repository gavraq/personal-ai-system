"""
Location Analyzer
Processes and analyzes location data from Owntracks to provide insights and patterns.
"""

import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
from collections import defaultdict, Counter
import logging
from geopy.distance import geodesic
from geopy.geocoders import Nominatim


class LocationAnalyzer:
    """Analyzes location data to provide insights and patterns"""
    
    def __init__(self):
        """Initialize the location analyzer"""
        self.logger = logging.getLogger(__name__)
        self.geocoder = Nominatim(user_agent="GavinLocationAgent/1.0")
        
        # Known important locations for Gavin
        self.known_locations = {
            'home': {
                'name': 'Home (Esher)',
                'coordinates': None,  # Will be detected from data
                'radius': 100  # meters
            },
            'office': {
                'name': 'ICBC Standard Bank (London)',
                'coordinates': (51.5074, -0.1278),  # Approximate London coordinates
                'radius': 200  # meters
            },
            'esher_station': {
                'name': 'Esher Railway Station',
                'coordinates': (51.3712, -0.3648),  # Esher station coordinates
                'radius': 100  # meters
            }
        }
    
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
    
    def parse_timestamp(self, timestamp: Union[int, str]) -> Optional[datetime]:
        """
        Parse Owntracks timestamp to datetime object
        
        Args:
            timestamp: Unix timestamp (int) or ISO string
            
        Returns:
            datetime object or None if invalid
        """
        try:
            if isinstance(timestamp, int):
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
        
        return pattern
    
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