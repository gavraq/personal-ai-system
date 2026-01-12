"""
Location Cache
Provides local caching for Owntracks location data to improve performance and enable offline access.
"""

import json
import os
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import hashlib
import logging


class LocationCache:
    """Local cache for location data with intelligent expiration and management"""
    
    def __init__(self, cache_dir: str = None, max_age_hours: int = 24):
        """
        Initialize location cache
        
        Args:
            cache_dir: Directory to store cache files (default: ~/.cache/location_agent)
            max_age_hours: Maximum age of cached data before considered stale
        """
        if cache_dir is None:
            cache_dir = os.path.expanduser("~/.cache/location_agent")
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_age_hours = max_age_hours
        self.logger = logging.getLogger(__name__)
        
        # Cache file paths
        self.locations_cache_file = self.cache_dir / "locations_cache.pkl"
        self.metadata_cache_file = self.cache_dir / "cache_metadata.json"
        self.analysis_cache_file = self.cache_dir / "analysis_cache.pkl"
        
        # Load existing metadata
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load cache metadata from disk"""
        if self.metadata_cache_file.exists():
            try:
                with open(self.metadata_cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load cache metadata: {e}")
        
        return {
            'last_updated': None,
            'cached_queries': {},
            'total_locations': 0,
            'date_range': {'start': None, 'end': None}
        }
    
    def _save_metadata(self):
        """Save cache metadata to disk"""
        try:
            with open(self.metadata_cache_file, 'w') as f:
                json.dump(self.metadata, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to save cache metadata: {e}")
    
    def _generate_cache_key(self, user: str, device: str, 
                           from_date: str = None, to_date: str = None) -> str:
        """Generate a unique cache key for a query"""
        key_parts = [user, device, from_date or '', to_date or '']
        key_string = '|'.join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def is_cache_fresh(self, cache_key: str = None) -> bool:
        """
        Check if cached data is still fresh
        
        Args:
            cache_key: Specific cache key to check (None for general freshness)
            
        Returns:
            True if cache is fresh
        """
        if cache_key and cache_key in self.metadata['cached_queries']:
            cached_time_str = self.metadata['cached_queries'][cache_key]['timestamp']
            cached_time = datetime.fromisoformat(cached_time_str)
        elif self.metadata['last_updated']:
            cached_time = datetime.fromisoformat(self.metadata['last_updated'])
        else:
            return False
        
        age_hours = (datetime.now() - cached_time).total_seconds() / 3600
        return age_hours < self.max_age_hours
    
    def cache_locations(self, user: str, device: str, locations: List[Dict],
                       from_date: str = None, to_date: str = None) -> bool:
        """
        Cache location data
        
        Args:
            user: Username
            device: Device name
            locations: List of location records
            from_date: Start date of query
            to_date: End date of query
            
        Returns:
            True if caching successful
        """
        try:
            cache_key = self._generate_cache_key(user, device, from_date, to_date)
            
            # Load existing cache or create new
            cached_data = {}
            if self.locations_cache_file.exists():
                try:
                    with open(self.locations_cache_file, 'rb') as f:
                        cached_data = pickle.load(f)
                except Exception as e:
                    self.logger.warning(f"Failed to load existing cache: {e}")
                    cached_data = {}
            
            # Add new data
            cached_data[cache_key] = {
                'user': user,
                'device': device,
                'from_date': from_date,
                'to_date': to_date,
                'locations': locations,
                'cached_at': datetime.now().isoformat(),
                'location_count': len(locations)
            }
            
            # Save updated cache
            with open(self.locations_cache_file, 'wb') as f:
                pickle.dump(cached_data, f)
            
            # Update metadata
            self.metadata['cached_queries'][cache_key] = {
                'user': user,
                'device': device,
                'timestamp': datetime.now().isoformat(),
                'location_count': len(locations),
                'from_date': from_date,
                'to_date': to_date
            }
            self.metadata['last_updated'] = datetime.now().isoformat()
            self.metadata['total_locations'] = sum(
                q['location_count'] for q in self.metadata['cached_queries'].values()
            )
            
            # Update date range
            if locations:
                dates = [loc.get('tst') for loc in locations if loc.get('tst')]
                if dates:
                    min_date = min(dates)
                    max_date = max(dates)
                    
                    if self.metadata['date_range']['start'] is None:
                        self.metadata['date_range']['start'] = min_date
                        self.metadata['date_range']['end'] = max_date
                    else:
                        self.metadata['date_range']['start'] = min(
                            self.metadata['date_range']['start'], min_date
                        )
                        self.metadata['date_range']['end'] = max(
                            self.metadata['date_range']['end'], max_date
                        )
            
            self._save_metadata()
            self.logger.info(f"Cached {len(locations)} locations for key {cache_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cache locations: {e}")
            return False
    
    def get_cached_locations(self, user: str, device: str,
                            from_date: str = None, to_date: str = None) -> Optional[List[Dict]]:
        """
        Retrieve cached location data
        
        Args:
            user: Username
            device: Device name
            from_date: Start date of query
            to_date: End date of query
            
        Returns:
            List of cached location records or None if not found/stale
        """
        cache_key = self._generate_cache_key(user, device, from_date, to_date)
        
        # Check if cache exists and is fresh
        if not self.is_cache_fresh(cache_key):
            return None
        
        if not self.locations_cache_file.exists():
            return None
        
        try:
            with open(self.locations_cache_file, 'rb') as f:
                cached_data = pickle.load(f)
            
            if cache_key in cached_data:
                cached_entry = cached_data[cache_key]
                self.logger.info(f"Retrieved {len(cached_entry['locations'])} cached locations")
                return cached_entry['locations']
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve cached locations: {e}")
        
        return None
    
    def cache_analysis(self, analysis_key: str, analysis_result: Any) -> bool:
        """
        Cache analysis results
        
        Args:
            analysis_key: Unique key for the analysis
            analysis_result: Analysis result to cache
            
        Returns:
            True if caching successful
        """
        try:
            # Load existing analysis cache
            cached_analyses = {}
            if self.analysis_cache_file.exists():
                try:
                    with open(self.analysis_cache_file, 'rb') as f:
                        cached_analyses = pickle.load(f)
                except Exception as e:
                    self.logger.warning(f"Failed to load existing analysis cache: {e}")
                    cached_analyses = {}
            
            # Add new analysis
            cached_analyses[analysis_key] = {
                'result': analysis_result,
                'cached_at': datetime.now().isoformat()
            }
            
            # Save updated cache
            with open(self.analysis_cache_file, 'wb') as f:
                pickle.dump(cached_analyses, f)
            
            self.logger.info(f"Cached analysis result for key {analysis_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cache analysis: {e}")
            return False
    
    def get_cached_analysis(self, analysis_key: str) -> Optional[Any]:
        """
        Retrieve cached analysis result
        
        Args:
            analysis_key: Unique key for the analysis
            
        Returns:
            Cached analysis result or None if not found/stale
        """
        if not self.analysis_cache_file.exists():
            return None
        
        try:
            with open(self.analysis_cache_file, 'rb') as f:
                cached_analyses = pickle.load(f)
            
            if analysis_key in cached_analyses:
                cached_entry = cached_analyses[analysis_key]
                cached_time = datetime.fromisoformat(cached_entry['cached_at'])
                age_hours = (datetime.now() - cached_time).total_seconds() / 3600
                
                if age_hours < self.max_age_hours:
                    self.logger.info(f"Retrieved cached analysis for key {analysis_key}")
                    return cached_entry['result']
                else:
                    self.logger.info(f"Cached analysis for key {analysis_key} is stale")
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve cached analysis: {e}")
        
        return None
    
    def clear_cache(self, older_than_hours: int = None) -> Dict:
        """
        Clear cached data
        
        Args:
            older_than_hours: Only clear data older than this many hours (None = clear all)
            
        Returns:
            Dictionary with cleanup statistics
        """
        stats = {
            'locations_cleared': 0,
            'analyses_cleared': 0,
            'files_removed': []
        }
        
        if older_than_hours is None:
            # Clear everything
            for cache_file in [self.locations_cache_file, self.analysis_cache_file, self.metadata_cache_file]:
                if cache_file.exists():
                    cache_file.unlink()
                    stats['files_removed'].append(str(cache_file))
            
            self.metadata = {
                'last_updated': None,
                'cached_queries': {},
                'total_locations': 0,
                'date_range': {'start': None, 'end': None}
            }
            stats['locations_cleared'] = 'all'
            stats['analyses_cleared'] = 'all'
            
        else:
            # Selective cleanup
            cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
            
            # Clean location cache
            if self.locations_cache_file.exists():
                try:
                    with open(self.locations_cache_file, 'rb') as f:
                        cached_data = pickle.load(f)
                    
                    updated_data = {}
                    for key, entry in cached_data.items():
                        cached_time = datetime.fromisoformat(entry['cached_at'])
                        if cached_time >= cutoff_time:
                            updated_data[key] = entry
                        else:
                            stats['locations_cleared'] += entry['location_count']
                    
                    with open(self.locations_cache_file, 'wb') as f:
                        pickle.dump(updated_data, f)
                        
                except Exception as e:
                    self.logger.error(f"Failed to clean location cache: {e}")
            
            # Clean analysis cache
            if self.analysis_cache_file.exists():
                try:
                    with open(self.analysis_cache_file, 'rb') as f:
                        cached_analyses = pickle.load(f)
                    
                    updated_analyses = {}
                    for key, entry in cached_analyses.items():
                        cached_time = datetime.fromisoformat(entry['cached_at'])
                        if cached_time >= cutoff_time:
                            updated_analyses[key] = entry
                        else:
                            stats['analyses_cleared'] += 1
                    
                    with open(self.analysis_cache_file, 'wb') as f:
                        pickle.dump(updated_analyses, f)
                        
                except Exception as e:
                    self.logger.error(f"Failed to clean analysis cache: {e}")
            
            # Update metadata
            updated_queries = {}
            for key, query in self.metadata['cached_queries'].items():
                cached_time = datetime.fromisoformat(query['timestamp'])
                if cached_time >= cutoff_time:
                    updated_queries[key] = query
            
            self.metadata['cached_queries'] = updated_queries
            self.metadata['total_locations'] = sum(
                q['location_count'] for q in updated_queries.values()
            )
            self._save_metadata()
        
        self.logger.info(f"Cache cleanup completed: {stats}")
        return stats
    
    def get_cache_status(self) -> Dict:
        """
        Get current cache status and statistics
        
        Returns:
            Dictionary with cache status information
        """
        status = {
            'cache_directory': str(self.cache_dir),
            'cache_fresh': self.is_cache_fresh(),
            'max_age_hours': self.max_age_hours,
            'metadata': self.metadata.copy(),
            'file_sizes': {},
            'cache_files_exist': {}
        }
        
        # Check file existence and sizes
        for cache_file, name in [
            (self.locations_cache_file, 'locations_cache'),
            (self.metadata_cache_file, 'metadata_cache'),
            (self.analysis_cache_file, 'analysis_cache')
        ]:
            status['cache_files_exist'][name] = cache_file.exists()
            if cache_file.exists():
                status['file_sizes'][name] = cache_file.stat().st_size
            else:
                status['file_sizes'][name] = 0
        
        return status


def create_location_cache(cache_dir: str = None, max_age_hours: int = 24) -> LocationCache:
    """
    Factory function to create a LocationCache instance
    
    Args:
        cache_dir: Directory to store cache files
        max_age_hours: Maximum age of cached data before considered stale
        
    Returns:
        Configured LocationCache instance
    """
    return LocationCache(cache_dir=cache_dir, max_age_hours=max_age_hours)


if __name__ == "__main__":
    # Example usage and testing
    cache = create_location_cache()
    
    print("Testing LocationCache...")
    
    # Test cache status
    status = cache.get_cache_status()
    print(f"Cache status: {json.dumps(status, indent=2, default=str)}")
    
    # Test caching mock data
    mock_locations = [
        {'lat': 51.3712, 'lon': -0.3648, 'tst': 1642680000},
        {'lat': 51.5074, 'lon': -0.1278, 'tst': 1642690000}
    ]
    
    success = cache.cache_locations('test_user', 'test_device', mock_locations)
    print(f"Caching test: {'Success' if success else 'Failed'}")
    
    # Test retrieval
    retrieved = cache.get_cached_locations('test_user', 'test_device')
    print(f"Retrieved {len(retrieved) if retrieved else 0} cached locations")
    
    print("\nLocationCache test completed!")