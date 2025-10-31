"""
Health Data Client - Python wrapper for the Health Data Service
Provides a clean Python interface to access health and fitness data
from the Node.js microservice.
"""

import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class HealthDataClient:
    """Python client for the Health Data Service API"""
    
    def __init__(self, base_url: str = "http://localhost:3001", timeout: int = 30):
        """
        Initialize the health data client
        
        Args:
            base_url: Base URL of the health data service
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'HealthDataClient-Python/1.0'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request to the health service
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            HealthServiceError: If the service returns an error
            ConnectionError: If unable to connect to service
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('success', False):
                raise HealthServiceError(data.get('error', 'Unknown error'))
                
            return data.get('data', {})
            
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Unable to connect to health service at {self.base_url}. "
                "Make sure the Node.js service is running."
            )
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Request to {url} timed out after {self.timeout} seconds")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise HealthServiceError(f"Endpoint not found: {endpoint}")
            elif e.response.status_code == 500:
                try:
                    error_data = e.response.json()
                    raise HealthServiceError(error_data.get('error', 'Internal server error'))
                except json.JSONDecodeError:
                    raise HealthServiceError("Internal server error")
            else:
                raise HealthServiceError(f"HTTP {e.response.status_code}: {e.response.reason}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if the health service is running and healthy
        
        Returns:
            Service health status information
        """
        return self._make_request('GET', '/health')
    
    def is_healthy(self) -> bool:
        """
        Quick check if the service is healthy
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            health = self.health_check()
            return health.get('status') == 'healthy'
        except Exception:
            return False
    
    # Parkrun methods
    def get_parkrun_profile(self) -> Dict[str, Any]:
        """
        Get parkrun profile information
        
        Returns:
            Parkrun profile data
        """
        return self._make_request('GET', '/api/parkrun/profile')
    
    def get_parkrun_results(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get parkrun results history
        
        Args:
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of parkrun results
        """
        params = {'limit': limit, 'offset': offset}
        return self._make_request('GET', '/api/parkrun/results', params=params)
    
    def get_parkrun_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive parkrun statistics
        
        Returns:
            Parkrun statistics and performance analysis
        """
        return self._make_request('GET', '/api/parkrun/stats')
    
    def sync_parkrun_data(self) -> Dict[str, Any]:
        """
        Trigger a sync of parkrun data from the API
        
        Returns:
            Sync result information
        """
        return self._make_request('POST', '/api/parkrun/sync')
    
    def get_parkrun_results_for_year(self, year: int) -> Dict[str, Any]:
        """
        Get parkrun results for a specific year
        
        Args:
            year: The year to get results for (e.g., 2025, 2024)
            
        Returns:
            Year-specific parkrun data with total runs and individual results
        """
        return self._make_request('GET', f'/api/parkrun/results/{year}')
    
    # General health data methods
    def get_health_summary(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive health summary for a period
        
        Args:
            period_days: Number of days to include in summary
            
        Returns:
            Health summary data from all connected sources
        """
        params = {'period': period_days}
        return self._make_request('GET', '/api/health/summary', params=params)
    
    # Convenience methods
    def get_recent_parkrun_activity(self, days: int = 30) -> Dict[str, Any]:
        """
        Get recent parkrun activity summary
        
        Args:
            days: Number of days to look back
            
        Returns:
            Recent parkrun activity summary
        """
        try:
            summary = self.get_health_summary(days)
            return summary.get('parkrun', {})
        except Exception as e:
            logger.error(f"Failed to get recent parkrun activity: {e}")
            return {'error': str(e)}
    
    def get_personal_bests(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get personal best runs
        
        Args:
            limit: Maximum number of PBs to return
            
        Returns:
            List of personal best runs
        """
        try:
            results = self.get_parkrun_results(limit=100)  # Get more results to find PBs
            pbs = [result for result in results if result.get('isPersonalBest', False)]
            return pbs[:limit]
        except Exception as e:
            logger.error(f"Failed to get personal bests: {e}")
            return []
    
    def get_venue_performance(self) -> Dict[str, Any]:
        """
        Get performance analysis by parkrun venue
        
        Returns:
            Venue performance statistics
        """
        try:
            stats = self.get_parkrun_statistics()
            return stats.get('venues', {})
        except Exception as e:
            logger.error(f"Failed to get venue performance: {e}")
            return {}
    
    def get_performance_trends(self, period_days: int = 90) -> Dict[str, Any]:
        """
        Analyze performance trends over time
        
        Args:
            period_days: Period for trend analysis
            
        Returns:
            Performance trend analysis
        """
        try:
            # Get recent results
            results = self.get_parkrun_results(limit=50)
            
            # Filter to period
            cutoff_date = datetime.now() - timedelta(days=period_days)
            period_results = [
                result for result in results 
                if datetime.fromisoformat(result.get('runDate', '').replace('Z', '')) >= cutoff_date
            ]
            
            if not period_results:
                return {'error': 'No results in specified period'}
            
            # Calculate trends
            times = []
            positions = []
            age_grades = []
            
            for result in period_results:
                if result.get('finishTime') and result['finishTime'] != 'Unknown':
                    # Convert time to seconds for analysis
                    time_parts = result['finishTime'].split(':')
                    if len(time_parts) == 2:
                        seconds = int(time_parts[0]) * 60 + int(time_parts[1])
                        times.append(seconds)
                
                if result.get('position'):
                    positions.append(result['position'])
                
                if result.get('ageGrade'):
                    age_grades.append(result['ageGrade'])
            
            trends = {
                'period_days': period_days,
                'total_runs': len(period_results),
                'personal_bests': len([r for r in period_results if r.get('isPersonalBest')]),
                'time_trend': {
                    'average_seconds': sum(times) / len(times) if times else None,
                    'best_seconds': min(times) if times else None,
                    'improvement': None  # Could calculate trend line here
                },
                'position_trend': {
                    'average_position': sum(positions) / len(positions) if positions else None,
                    'best_position': min(positions) if positions else None
                },
                'age_grade_trend': {
                    'average_age_grade': sum(age_grades) / len(age_grades) if age_grades else None,
                    'best_age_grade': max(age_grades) if age_grades else None
                }
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to analyze performance trends: {e}")
            return {'error': str(e)}


class HealthServiceError(Exception):
    """Exception raised when the health service returns an error"""
    pass


def create_health_client(base_url: str = None) -> HealthDataClient:
    """
    Factory function to create a health data client
    
    Args:
        base_url: Optional base URL override
        
    Returns:
        Configured HealthDataClient instance
    """
    if base_url is None:
        base_url = "http://localhost:3001"
    
    client = HealthDataClient(base_url)
    
    # Test connection
    if not client.is_healthy():
        logger.warning(
            f"Health service at {base_url} is not responding. "
            "Make sure the Node.js service is running: cd health-integration/health-service && npm start"
        )
    
    return client


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create client and test connection
    client = create_health_client()
    
    try:
        # Test health check
        health = client.health_check()
        print("Service Health:", json.dumps(health, indent=2))
        
        # Test parkrun data
        profile = client.get_parkrun_profile()
        print("Parkrun Profile:", json.dumps(profile, indent=2))
        
        # Get recent results
        results = client.get_parkrun_results(limit=5)
        print(f"Recent Results ({len(results)} found):", json.dumps(results, indent=2))
        
    except Exception as e:
        print(f"Error testing health client: {e}")