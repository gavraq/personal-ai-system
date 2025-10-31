"""
Custom exceptions and error handling for FreeAgent sub-agent.
"""

import time
import functools
from typing import Callable, Any
import requests


class FreeAgentError(Exception):
    """Base exception for FreeAgent API errors."""
    pass


class AuthenticationError(FreeAgentError):
    """Raised when authentication fails."""
    pass


class AuthorizationError(FreeAgentError):
    """Raised when user lacks permission for the requested action."""
    pass


class RateLimitError(FreeAgentError):
    """Raised when API rate limit is exceeded."""
    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after


class ValidationError(FreeAgentError):
    """Raised when request data is invalid."""
    pass


class NotFoundError(FreeAgentError):
    """Raised when requested resource is not found."""
    pass


class APIError(FreeAgentError):
    """General API error."""
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


def handle_api_errors(func: Callable) -> Callable:
    """
    Decorator to handle common API errors and convert them to custom exceptions.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            response = e.response
            status_code = response.status_code
            
            try:
                error_data = response.json()
                error_message = error_data.get('error', str(e))
            except:
                error_message = str(e)
            
            # Map HTTP status codes to custom exceptions
            if status_code == 401:
                raise AuthenticationError(f"Authentication failed: {error_message}")
            elif status_code == 403:
                raise AuthorizationError(f"Access denied: {error_message}")
            elif status_code == 404:
                raise NotFoundError(f"Resource not found: {error_message}")
            elif status_code == 422:
                raise ValidationError(f"Validation error: {error_message}")
            elif status_code == 429:
                # Extract retry-after header if available
                retry_after = response.headers.get('Retry-After')
                if retry_after:
                    retry_after = int(retry_after)
                raise RateLimitError(f"Rate limit exceeded: {error_message}", retry_after)
            else:
                raise APIError(f"API error: {error_message}", status_code, error_data)
                
        except requests.exceptions.ConnectionError:
            raise FreeAgentError("Connection error: Unable to connect to FreeAgent API")
        except requests.exceptions.Timeout:
            raise FreeAgentError("Timeout error: Request timed out")
        except requests.exceptions.RequestException as e:
            raise FreeAgentError(f"Request error: {str(e)}")
            
    return wrapper


def rate_limit(calls_per_minute: int = 60):
    """
    Decorator to implement rate limiting.
    
    Args:
        calls_per_minute: Maximum number of calls per minute
    """
    call_times = []
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            
            # Remove calls older than 1 minute
            call_times[:] = [t for t in call_times if now - t < 60]
            
            # Check if we've exceeded the rate limit
            if len(call_times) >= calls_per_minute:
                sleep_time = 60 - (now - call_times[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    # Remove old calls again after sleeping
                    now = time.time()
                    call_times[:] = [t for t in call_times if now - t < 60]
            
            # Record this call
            call_times.append(now)
            
            return func(*args, **kwargs)
            
        return wrapper
    return decorator


def retry_on_rate_limit(max_retries: int = 3, base_delay: float = 1.0):
    """
    Decorator to retry function on rate limit errors.
    
    Args:
        max_retries: Maximum number of retries
        base_delay: Base delay between retries (exponential backoff)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except RateLimitError as e:
                    if attempt == max_retries:
                        raise e
                    
                    # Use retry_after from the exception if available, otherwise exponential backoff
                    delay = e.retry_after if e.retry_after else base_delay * (2 ** attempt)
                    time.sleep(delay)
                    
        return wrapper
    return decorator