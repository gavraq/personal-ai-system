"""
Owntracks API Client
Handles communication with Gavin's Owntracks instance for location data retrieval.
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import logging
from urllib.parse import urljoin


class OwntracksClient:
    """Client for interacting with Owntracks Recorder API"""

    def __init__(self, base_url: str = "https://owntracks.gavinslater.co.uk",
                 username: str = None, password: str = None):
        """
        Initialize Owntracks client

        Args:
            base_url: Base URL of Owntracks instance
            username: Username for authentication
            password: Password for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api/0"
        self.username = username
        self.password = password
        self.session = requests.Session()

        # Set up logging first
        self.logger = logging.getLogger(__name__)

        # Set up authentication if provided (optional)
        if username and password:
            self.session.auth = (username, password)
            self.logger.info("Using HTTP Basic authentication")
        else:
            self.logger.info("No authentication configured - using open access")

        # Set up headers
        self.session.headers.update({
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'GavinLocationAgent/1.0'
        })

    def get_locations(self, user: str, device: str,
                     from_date: Optional[Union[str, datetime]] = None,
                     to_date: Optional[Union[str, datetime]] = None,
                     limit: Optional[int] = None,
                     format_type: str = "json") -> Dict:
        """
        Retrieve location history for a user and device

        Args:
            user: Username
            device: Device name
            from_date: Start date (YYYY-MM-DD format or datetime object)
            to_date: End date (YYYY-MM-DD format or datetime object)
            limit: Maximum number of records to return
            format_type: Response format (json, csv, geojson, xml, linestring)

        Returns:
            Dictionary containing location data and metadata
        """
        endpoint = f"{self.api_base}/locations"

        # Prepare data payload
        data = {
            'user': user,
            'device': device,
            'format': format_type
        }

        # Add optional parameters
        if from_date:
            if isinstance(from_date, datetime):
                data['from'] = from_date.strftime('%Y-%m-%d')
            else:
                data['from'] = from_date

        if to_date:
            if isinstance(to_date, datetime):
                data['to'] = to_date.strftime('%Y-%m-%d')
            else:
                data['to'] = to_date

        if limit:
            data['limit'] = limit

        try:
            response = self.session.post(endpoint, data=data)
            response.raise_for_status()

            if format_type == "json":
                response_data = response.json()

                # Extract actual location data from nested structure
                if isinstance(response_data, dict) and 'data' in response_data:
                    actual_locations = response_data['data']
                    count = response_data.get('count', len(actual_locations) if isinstance(actual_locations, list) else 1)
                else:
                    # Handle direct list responses (backward compatibility)
                    actual_locations = response_data
                    count = len(response_data) if isinstance(response_data, list) else 1

                return {
                    'success': True,
                    'data': actual_locations,
                    'count': count,
                    'query': data,
                    'raw_response': response_data  # Keep raw response for debugging
                }
            else:
                return {
                    'success': True,
                    'data': response.text,
                    'query': data
                }

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error retrieving locations: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': data
            }

    def get_last_position(self, user: str = None, device: str = None) -> Dict:
        """
        Get last known position(s)

        Args:
            user: Optional username filter
            device: Optional device filter

        Returns:
            Dictionary containing last position data
        """
        endpoint = f"{self.api_base}/last"

        data = {}
        if user:
            data['user'] = user
        if device:
            data['device'] = device

        try:
            if data:
                response = self.session.post(endpoint, data=data)
            else:
                response = self.session.get(endpoint)

            response.raise_for_status()

            return {
                'success': True,
                'data': response.json(),
                'query': data
            }

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error retrieving last position: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': data
            }

    def get_user_devices(self, user: str = None) -> Dict:
        """
        List users and their devices

        Args:
            user: Optional username to filter by

        Returns:
            Dictionary containing user/device information
        """
        endpoint = f"{self.api_base}/list"

        data = {}
        if user:
            data['user'] = user

        try:
            if data:
                response = self.session.post(endpoint, data=data)
            else:
                response = self.session.get(endpoint)

            response.raise_for_status()

            return {
                'success': True,
                'data': response.json(),
                'query': data
            }

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error retrieving user devices: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': data
            }

    def test_connection(self) -> Dict:
        """
        Test connection to Owntracks instance

        Returns:
            Dictionary indicating connection status
        """
        try:
            response = self.session.get(f"{self.api_base}/monitor")
            response.raise_for_status()

            return {
                'success': True,
                'status': 'Connected to Owntracks instance',
                'response_code': response.status_code
            }

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Connection test failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'status': 'Failed to connect to Owntracks instance'
            }

    def get_locations_for_date(self, user: str, device: str, target_date: Union[str, datetime]) -> Dict:
        """
        Get all locations for a specific date

        IMPORTANT: The Owntracks API treats the 'to' parameter as EXCLUSIVE (not inclusive).
        To retrieve a full day's data, this method automatically uses the NEXT day as the 'to' date.

        Example: For 2025-10-08 data:
          - from_date = '2025-10-08' (start from Oct 8 00:00:00)
          - to_date = '2025-10-09' (up to BUT NOT INCLUDING Oct 9 00:00:00)
          - Result: All data for Oct 8 from 00:00:00 to 23:59:59

        Args:
            user: Username
            device: Device name
            target_date: Date to query (YYYY-MM-DD format or datetime object)

        Returns:
            Dictionary containing location data for the specified date
        """
        if isinstance(target_date, datetime):
            date_str = target_date.strftime('%Y-%m-%d')
        else:
            date_str = target_date

        # CRITICAL: Use next day as 'to' date because Owntracks API uses exclusive endpoint
        # Using same date for both from/to returns ZERO records even if data exists
        try:
            target_dt = datetime.strptime(date_str, '%Y-%m-%d')
            next_day = (target_dt + timedelta(days=1)).strftime('%Y-%m-%d')

            self.logger.info(f"Retrieving full day data for {date_str} using from={date_str}, to={next_day} (exclusive endpoint)")

            return self.get_locations(
                user=user,
                device=device,
                from_date=date_str,
                to_date=next_day,  # Next day ensures we get all of target_date
                format_type="json"
            )
        except ValueError:
            return {
                'success': False,
                'error': f'Invalid date format: {date_str}. Use YYYY-MM-DD format.'
            }

    def get_recent_locations(self, user: str, device: str, hours: int = 24) -> Dict:
        """
        Get recent locations within the last N hours

        Args:
            user: Username
            device: Device name
            hours: Number of hours to look back

        Returns:
            Dictionary containing recent location data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=hours)

        return self.get_locations(
            user=user,
            device=device,
            from_date=start_date,
            to_date=end_date,
            format_type="json"
        )


def create_owntracks_client(username: str = None, password: str = None) -> OwntracksClient:
    """
    Factory function to create an Owntracks client

    Args:
        username: Owntracks username
        password: Owntracks password

    Returns:
        Configured OwntracksClient instance
    """
    return OwntracksClient(username=username, password=password)


if __name__ == "__main__":
    # Example usage and testing
    import os

    # Try to get credentials from environment variables
    username = os.getenv('OWNTRACKS_USERNAME')
    password = os.getenv('OWNTRACKS_PASSWORD')

    if username and password:
        client = create_owntracks_client(username, password)

        # Test connection
        print("Testing Owntracks connection...")
        result = client.test_connection()
        print(f"Connection test: {result}")

        # Get user devices
        print(f"\nRetrieving devices for user '{username}'...")
        devices = client.get_user_devices(username)
        print(f"Devices: {devices}")

        # Get last position
        print(f"\nRetrieving last position...")
        last_pos = client.get_last_position(username)
        print(f"Last position: {last_pos}")

    else:
        print("Please set OWNTRACKS_USERNAME and OWNTRACKS_PASSWORD environment variables for testing")
        print("Example usage:")
        print("export OWNTRACKS_USERNAME='your_username'")
        print("export OWNTRACKS_PASSWORD='your_password'")
        print("python owntracks_client.py")
