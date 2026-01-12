"""
Location Agent Main Module
Coordinates Owntracks integration, location analysis, and caching for Gavin's location intelligence.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
try:
    from .core.owntracks_client import OwntracksClient, create_owntracks_client
    from .core.location_analyzer import LocationAnalyzer, create_location_analyzer
    from .core.location_cache import LocationCache, create_location_cache
except ImportError:
    # Fallback for direct execution
    from core.owntracks_client import OwntracksClient, create_owntracks_client
    from core.location_analyzer import LocationAnalyzer, create_location_analyzer
    from core.location_cache import LocationCache, create_location_cache


class LocationAgent:
    """Main Location Agent coordinator for Gavin's location intelligence"""
    
    def __init__(self, owntracks_username: str = None, owntracks_password: str = None,
                 gavin_user: str = None, gavin_device: str = None,
                 cache_dir: str = None, cache_max_age_hours: int = 24):
        """
        Initialize Location Agent
        
        Args:
            owntracks_username: HTTP Basic auth username (will try environment if None)
            owntracks_password: HTTP Basic auth password (will try environment if None) 
            gavin_user: Owntracks data user ID (e.g., 'gavin-iphone')
            gavin_device: Owntracks device ID (e.g., 'a2ea00bc-9862-4efb-a6ab-f038e32beb4c')
            cache_dir: Cache directory path
            cache_max_age_hours: Maximum age for cached data
        """
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Get HTTP Basic auth credentials from environment if not provided
        self.auth_username = owntracks_username or os.getenv('OWNTRACKS_AUTH_USERNAME')
        self.auth_password = owntracks_password or os.getenv('OWNTRACKS_AUTH_PASSWORD')
        
        if not self.auth_username or not self.auth_password:
            self.logger.info("No HTTP Basic auth configured - will try open access. Set OWNTRACKS_AUTH_USERNAME and OWNTRACKS_AUTH_PASSWORD if authentication is required.")
        
        # Initialize components
        self.owntracks = create_owntracks_client(self.auth_username, self.auth_password)
        self.analyzer = create_location_analyzer()
        self.cache = create_location_cache(cache_dir, cache_max_age_hours)
        
        # Gavin's data identifiers - can be configured or auto-detected
        self.gavin_user = gavin_user or os.getenv('OWNTRACKS_USER', 'gavin-iphone')
        self.gavin_device = gavin_device or os.getenv('OWNTRACKS_DEVICE', 'a2ea00bc-9862-4efb-a6ab-f038e32beb4c')
        self.detected_devices = None
    
    def _detect_gavin_device(self) -> Optional[str]:
        """Detect Gavin's primary device from available devices"""
        if self.detected_devices is None:
            devices_result = self.owntracks.get_user_devices(self.gavin_user)
            if devices_result['success']:
                self.detected_devices = devices_result['data']
                self.logger.info(f"Detected devices: {self.detected_devices}")
                
                # Try to find the most active device
                if isinstance(self.detected_devices, list) and self.detected_devices:
                    self.gavin_device = self.detected_devices[0]  # Use first device as default
                elif isinstance(self.detected_devices, dict):
                    # If it's a dict, look for 'results' key first
                    if 'results' in self.detected_devices and self.detected_devices['results']:
                        devices = self.detected_devices['results']
                        if isinstance(devices, list) and devices:
                            self.gavin_device = devices[0]
                    else:
                        # Fall back to using dict keys as device names
                        devices = list(self.detected_devices.keys())
                        if devices:
                            self.gavin_device = devices[0]
            else:
                self.logger.error(f"Failed to detect devices: {devices_result.get('error')}")
        
        return self.gavin_device
    
    def _get_locations_with_cache(self, user: str, device: str,
                                 from_date: Optional[str] = None,
                                 to_date: Optional[str] = None) -> Dict:
        """
        Get locations with intelligent caching
        
        Args:
            user: Username
            device: Device name
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary with location data and metadata
        """
        # Try cache first
        cached_locations = self.cache.get_cached_locations(user, device, from_date, to_date)
        if cached_locations:
            self.logger.info(f"Using cached location data ({len(cached_locations)} records)")
            return {
                'success': True,
                'data': cached_locations,
                'count': len(cached_locations),
                'source': 'cache'
            }
        
        # Fetch from API
        result = self.owntracks.get_locations(user, device, from_date, to_date)
        
        if result['success'] and result['data']:
            # Cache the results
            self.cache.cache_locations(user, device, result['data'], from_date, to_date)
            result['source'] = 'api'
            self.logger.info(f"Fetched and cached {len(result['data'])} location records")
        
        return result
    
    def test_connection(self) -> Dict:
        """Test connection to Owntracks and detect devices"""
        connection_test = self.owntracks.test_connection()
        
        if connection_test['success']:
            # Try to detect devices
            device = self._detect_gavin_device()
            if device:
                connection_test['detected_device'] = device
                connection_test['user'] = self.gavin_user
            else:
                connection_test['warning'] = 'Could not detect primary device'
        
        return connection_test
    
    def where_was_i(self, target_date: str, target_time: str = None) -> Dict:
        """
        Answer "where was I" questions for specific date/time
        
        Args:
            target_date: Date in YYYY-MM-DD format
            target_time: Optional time in HH:MM format
            
        Returns:
            Dictionary with location information
        """
        device = self.gavin_device or self._detect_gavin_device()
        if not device:
            return {'error': 'Could not detect Gavin device. Please configure device name.'}
        
        # Get locations for the target date using a small range (next day) since exact date queries fail
        try:
            target_dt = datetime.strptime(target_date, '%Y-%m-%d')
            next_day = (target_dt + timedelta(days=1)).strftime('%Y-%m-%d')
        except ValueError:
            return {'error': f'Invalid date format: {target_date}. Use YYYY-MM-DD format.'}
        
        locations_result = self._get_locations_with_cache(
            self.gavin_user, device, target_date, next_day
        )
        
        if not locations_result['success']:
            return {'error': f'Failed to retrieve location data: {locations_result.get("error")}'}
        
        locations = locations_result['data']
        if not locations:
            return {'error': f'No location data found for {target_date}'}
        
        if target_time:
            # Find location at specific time
            try:
                target_datetime = datetime.strptime(f"{target_date} {target_time}", "%Y-%m-%d %H:%M")
                location_at_time = self.analyzer.find_location_at_time(locations, target_datetime)
                
                if location_at_time:
                    return {
                        'success': True,
                        'query': f"Where was I on {target_date} at {target_time}?",
                        'answer': {
                            'timestamp': location_at_time['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                            'coordinates': location_at_time['coordinates'],
                            'address': location_at_time['address'],
                            'time_difference_minutes': round(location_at_time['time_difference_minutes'], 1)
                        },
                        'source': locations_result['source']
                    }
                else:
                    return {
                        'success': False,
                        'error': f'No location data found near {target_time} on {target_date}'
                    }
            except ValueError as e:
                return {'error': f'Invalid time format: {e}'}
        else:
            # Analyze the entire day
            try:
                target_datetime = datetime.strptime(target_date, "%Y-%m-%d")
                daily_analysis = self.analyzer.analyze_daily_pattern(locations, target_datetime)
                
                if 'error' in daily_analysis:
                    return daily_analysis
                
                return {
                    'success': True,
                    'query': f"Where was I on {target_date}?",
                    'answer': daily_analysis,
                    'source': locations_result['source']
                }
            except ValueError as e:
                return {'error': f'Invalid date format: {e}'}
    
    def analyze_time_at_location(self, location_name: str, 
                                from_date: str = None, to_date: str = None,
                                radius_meters: int = 100) -> Dict:
        """
        Analyze time spent at a specific location
        
        Args:
            location_name: Name of location ('home', 'office', 'esher_station' or coordinates)
            from_date: Start date (YYYY-MM-DD, default: last 7 days)
            to_date: End date (YYYY-MM-DD, default: today)
            radius_meters: Radius to consider as "at location"
            
        Returns:
            Dictionary with time analysis
        """
        device = self.gavin_device or self._detect_gavin_device()
        if not device:
            return {'error': 'Could not detect Gavin device. Please configure device name.'}
        
        # Set default date range
        if not to_date:
            to_date = datetime.now().strftime('%Y-%m-%d')
        if not from_date:
            from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Get target coordinates
        target_coords = None
        if location_name.lower() in self.analyzer.known_locations:
            location_info = self.analyzer.known_locations[location_name.lower()]
            target_coords = location_info['coordinates']
            radius_meters = location_info.get('radius', radius_meters)
        else:
            # Try parsing as coordinates
            try:
                if ',' in location_name:
                    lat_str, lon_str = location_name.split(',')
                    target_coords = (float(lat_str.strip()), float(lon_str.strip()))
            except ValueError:
                return {'error': f'Unknown location "{location_name}". Use coordinates (lat,lon) or known locations: {list(self.analyzer.known_locations.keys())}'}
        
        if not target_coords:
            return {'error': f'Could not determine coordinates for location "{location_name}"'}
        
        # Get location data
        locations_result = self._get_locations_with_cache(
            self.gavin_user, device, from_date, to_date
        )
        
        if not locations_result['success']:
            return {'error': f'Failed to retrieve location data: {locations_result.get("error")}'}
        
        # Analyze time at location
        time_analysis = self.analyzer.analyze_time_at_location(
            locations_result['data'], target_coords, radius_meters
        )
        
        return {
            'success': True,
            'query': f"Time spent at {location_name} from {from_date} to {to_date}",
            'analysis': time_analysis,
            'location_name': location_name,
            'coordinates': target_coords,
            'source': locations_result['source']
        }
    
    def analyze_commute_pattern(self, days: int = 30) -> Dict:
        """
        Analyze Gavin's commute patterns
        
        Args:
            days: Number of recent days to analyze
            
        Returns:
            Dictionary with commute analysis
        """
        device = self.gavin_device or self._detect_gavin_device()
        if not device:
            return {'error': 'Could not detect Gavin device. Please configure device name.'}
        
        # Get recent location data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        locations_result = self._get_locations_with_cache(
            self.gavin_user, device, 
            start_date.strftime('%Y-%m-%d'), 
            end_date.strftime('%Y-%m-%d')
        )
        
        if not locations_result['success']:
            return {'error': f'Failed to retrieve location data: {locations_result.get("error")}'}
        
        # Analyze commute patterns
        commute_analysis = self.analyzer.detect_commute_pattern(locations_result['data'], days)
        
        return {
            'success': True,
            'query': f"Commute pattern analysis for past {days} days",
            'analysis': commute_analysis,
            'source': locations_result['source']
        }
    
    def analyze_date(self, target_date: str) -> Dict:
        """
        Analyze a full day's location data and activities

        Args:
            target_date: Date to analyze (YYYY-MM-DD format)

        Returns:
            Dictionary with daily pattern analysis including activities
        """
        device = self.gavin_device or self._detect_gavin_device()
        if not device:
            return {'error': 'Could not detect Gavin device. Please configure device name.'}

        # Parse date
        try:
            date_obj = datetime.strptime(target_date, '%Y-%m-%d')
        except ValueError:
            return {'error': f'Invalid date format: {target_date}. Use YYYY-MM-DD'}

        # Get location data for the date
        # Note: API uses exclusive end date, so we need next day to include the target date
        next_day = (date_obj + timedelta(days=1)).strftime('%Y-%m-%d')
        locations_result = self._get_locations_with_cache(
            self.gavin_user, device, target_date, next_day
        )

        if not locations_result['success']:
            return {'error': f'Failed to retrieve location data: {locations_result.get("error")}'}

        # Analyze daily pattern
        daily_analysis = self.analyzer.analyze_daily_pattern(
            locations_result['data'], date_obj
        )

        return {
            'success': True,
            'date': target_date,
            'day_of_week': date_obj.strftime('%A'),
            'analysis': daily_analysis,
            'location_count': len(locations_result['data']),
            'source': locations_result.get('source', 'unknown')
        }

    def get_frequent_locations(self, days: int = 30, min_visits: int = 3) -> Dict:
        """
        Identify frequently visited locations

        Args:
            days: Number of recent days to analyze
            min_visits: Minimum visits to consider frequent

        Returns:
            Dictionary with frequent locations
        """
        device = self.gavin_device or self._detect_gavin_device()
        if not device:
            return {'error': 'Could not detect Gavin device. Please configure device name.'}

        # Get recent location data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        locations_result = self._get_locations_with_cache(
            self.gavin_user, device,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

        if not locations_result['success']:
            return {'error': f'Failed to retrieve location data: {locations_result.get("error")}'}

        # Identify frequent locations
        frequent_locations = self.analyzer.identify_frequent_locations(
            locations_result['data'], min_visits
        )

        return {
            'success': True,
            'query': f"Frequent locations in past {days} days (min {min_visits} visits)",
            'locations': frequent_locations,
            'source': locations_result['source']
        }
    
    def get_current_location(self) -> Dict:
        """Get Gavin's current/last known location"""
        device = self.gavin_device or self._detect_gavin_device()
        if not device:
            return {'error': 'Could not detect Gavin device. Please configure device name.'}
        
        self.logger.info(f"Using device: configured='{self.gavin_device}', final='{device}'")
        self.logger.info(f"Getting last position for user='{self.gavin_user}', device='{device}'")
        result = self.owntracks.get_last_position(self.gavin_user, device)
        self.logger.info(f"Last position result: {result}")
        
        if result['success'] and result['data']:
            location_data = result['data']
            if isinstance(location_data, list) and location_data:
                location_data = location_data[0]
            
            coords = self.analyzer.extract_coordinates(location_data)
            timestamp = self.analyzer.parse_timestamp(location_data.get('tst'))
            
            return {
                'success': True,
                'current_location': {
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S') if timestamp else None,
                    'coordinates': coords,
                    'address': self.analyzer.geocode_location(coords) if coords else None,
                    'accuracy': location_data.get('acc'),
                    'raw_data': location_data
                }
            }
        elif result['success'] and not result['data']:
            return {
                'success': False,
                'error': f"No location data found for user='{self.gavin_user}', device='{device}'"
            }
        
        return result
    
    def get_cache_status(self) -> Dict:
        """Get cache status and statistics"""
        return self.cache.get_cache_status()
    
    def clear_cache(self, older_than_hours: int = None) -> Dict:
        """Clear cached data"""
        return self.cache.clear_cache(older_than_hours)


def create_location_agent(auth_username: str = None, auth_password: str = None,
                         gavin_user: str = None, gavin_device: str = None) -> LocationAgent:
    """
    Factory function to create a LocationAgent instance
    
    Args:
        auth_username: HTTP Basic auth username  
        auth_password: HTTP Basic auth password
        gavin_user: Owntracks data user ID (e.g., 'gavin-iphone')
        gavin_device: Owntracks device ID (e.g., 'a2ea00bc-9862-4efb-a6ab-f038e32beb4c')
        
    Returns:
        Configured LocationAgent instance
    """
    return LocationAgent(auth_username, auth_password, gavin_user, gavin_device)


if __name__ == "__main__":
    import sys
    import argparse

    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Location Agent - Analyze Gavin\'s location data and activities',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Analyze a specific date
  python3 location_agent.py --analyze-date 2025-10-27

  # Get current location
  python3 location_agent.py --current

  # Test connection
  python3 location_agent.py --test

  # Analyze commute patterns
  python3 location_agent.py --commute-pattern --days 30
        '''
    )

    parser.add_argument('--analyze-date', type=str, metavar='YYYY-MM-DD',
                        help='Analyze location data and activities for a specific date')
    parser.add_argument('--current', action='store_true',
                        help='Get current/last known location')
    parser.add_argument('--test', action='store_true',
                        help='Test Owntracks connection')
    parser.add_argument('--commute-pattern', action='store_true',
                        help='Analyze commute patterns')
    parser.add_argument('--days', type=int, default=30,
                        help='Number of days to analyze (default: 30)')
    parser.add_argument('--cache-status', action='store_true',
                        help='Show cache status')

    args = parser.parse_args()

    # Create agent
    agent = create_location_agent()

    # Handle commands
    if args.test or (not any([args.analyze_date, args.current, args.commute_pattern, args.cache_status])):
        # Default: test connection
        print("Testing Owntracks connection...")
        connection = agent.test_connection()
        print(f"Connection: {connection}")

        if not connection['success']:
            print("Connection failed. Please check credentials and network.")
            sys.exit(1)

        if agent.gavin_device:
            print(f"\nUsing device: {agent.gavin_device}")
            print("\nLocation Agent ready!")
            print("Use --help for available commands")
        else:
            print("No device detected. Cannot run location queries.")

    elif args.analyze_date:
        print(f"Analyzing date: {args.analyze_date}")
        result = agent.analyze_date(args.analyze_date)

        if result.get('success'):
            print(f"\n=== {result['date']} ({result['day_of_week']}) ===")
            print(f"Location points: {result['location_count']}")
            print(f"Data source: {result['source']}")
            print()

            analysis = result['analysis']
            print(f"Day type: {analysis.get('day_type', 'unknown')}")
            print(f"Primary location: {analysis.get('primary_location', 'unknown')}")

            # Display timeline
            timeline = analysis.get('timeline', [])
            if timeline:
                print(f"\nTimeline ({len(timeline)} segments):")
                for segment in timeline:
                    duration = segment.get('duration_minutes', 0)
                    duration_str = f"{duration}m" if duration < 60 else f"{duration // 60}h {duration % 60}m"
                    print(f"  {segment['start_time']}-{segment['end_time']}: {segment['location_name']} ({duration_str})")

            # Display detected activities
            activities = analysis.get('detected_activities', [])
            if activities:
                print(f"\nDetected activities: {len(activities)}")
                for activity in activities:
                    activity_type = activity.get('activity_type', activity.get('type', 'unknown'))
                    print(f"\n  {activity_type.upper()}:")
                    print(f"    Time: {activity['start_time']} - {activity['end_time']}")
                    print(f"    Duration: {activity.get('duration_hours', 0):.2f}h")
                    if activity.get('venue'):
                        print(f"    Venue: {activity['venue']}")
                    if activity.get('confidence'):
                        conf = activity['confidence']
                        if isinstance(conf, (int, float)):
                            print(f"    Confidence: {conf:.2f}")
                        else:
                            print(f"    Confidence: {conf}")
            else:
                print("\nNo specific activities detected")
        else:
            print(f"Error: {result.get('error')}")
            sys.exit(1)

    elif args.current:
        result = agent.get_current_location()
        if result.get('success'):
            print(json.dumps(result, indent=2, default=str))
        else:
            print(f"Error: {result.get('error')}")
            sys.exit(1)

    elif args.commute_pattern:
        print(f"Analyzing commute patterns for past {args.days} days...")
        result = agent.analyze_commute_pattern(args.days)
        if result.get('success'):
            print(json.dumps(result, indent=2, default=str))
        else:
            print(f"Error: {result.get('error')}")
            sys.exit(1)

    elif args.cache_status:
        status = agent.get_cache_status()
        print(json.dumps(status, indent=2, default=str))