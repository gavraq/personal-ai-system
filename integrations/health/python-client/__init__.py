"""
Health Data Client Package

Python wrapper for the Health Data Service providing access to:
- Parkrun data and statistics
- Future fitness platform integrations (Fitbit, Strava, etc.)
- Health analytics and trend analysis
"""

from .health_data_client import HealthDataClient, HealthServiceError, create_health_client

__version__ = "1.0.0"
__author__ = "Gavin Slater"

__all__ = [
    'HealthDataClient',
    'HealthServiceError', 
    'create_health_client'
]