"""
FreeAgent API Client for invoicing operations.
Handles OAuth authentication and API requests to FreeAgent.
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
from urllib.parse import urlencode
try:
    from .exceptions import handle_api_errors, rate_limit, retry_on_rate_limit, AuthenticationError
except ImportError:
    from exceptions import handle_api_errors, rate_limit, retry_on_rate_limit, AuthenticationError


class FreeAgentClient:
    """Client for interacting with FreeAgent API with OAuth authentication."""
    
    def __init__(self, client_id: str, client_secret: str, sandbox: bool = True):
        self.client_id = client_id
        self.client_secret = client_secret
        self.sandbox = sandbox
        self.base_url = "https://api.sandbox.freeagent.com/v2" if sandbox else "https://api.freeagent.com/v2"
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        
    def set_tokens(self, access_token: str, refresh_token: str, expires_in: int = 3600):
        """Set OAuth tokens manually."""
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
        
    def get_authorization_url(self, redirect_uri: str, state: str = None) -> str:
        """Generate OAuth authorization URL."""
        auth_url = "https://api.freeagent.com/v2/approve_app"
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': redirect_uri
        }
        if state:
            params['state'] = state
        return f"{auth_url}?{urlencode(params)}"
        
    def exchange_code_for_tokens(self, authorization_code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access tokens."""
        token_url = "https://api.freeagent.com/v2/token_endpoint"
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': authorization_code,
            'redirect_uri': redirect_uri
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self.set_tokens(
            token_data['access_token'],
            token_data['refresh_token'],
            token_data.get('expires_in', 3600)
        )
        return token_data
        
    def refresh_access_token(self) -> Dict[str, Any]:
        """Refresh the access token using refresh token."""
        if not self.refresh_token:
            raise ValueError("No refresh token available")
            
        token_url = "https://api.freeagent.com/v2/token_endpoint"
        data = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self.set_tokens(
            token_data['access_token'],
            token_data['refresh_token'],
            token_data.get('expires_in', 3600)
        )
        
        # Save refreshed tokens back to config automatically
        try:
            try:
                from .config import FreeAgentConfig
            except ImportError:
                from config import FreeAgentConfig
            
            config = FreeAgentConfig()
            config.save_tokens(token_data['access_token'], token_data['refresh_token'])
            print("✅ Tokens automatically refreshed and saved")
        except Exception as e:
            print(f"Warning: Could not save refreshed tokens: {e}")
        
        return token_data
        
    def _ensure_valid_token(self):
        """Ensure we have a valid access token, refresh if necessary."""
        if not self.access_token:
            raise AuthenticationError("No access token available. Please authenticate first.")
            
        if self.token_expires_at and datetime.now() >= self.token_expires_at - timedelta(minutes=5):
            self.refresh_access_token()
            
    @handle_api_errors
    @rate_limit(calls_per_minute=60)
    @retry_on_rate_limit(max_retries=3)
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, retry_auth: bool = True) -> requests.Response:
        """Make authenticated request to FreeAgent API with automatic re-authentication."""
        self._ensure_valid_token()
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response.raise_for_status()
            return response
            
        except requests.exceptions.HTTPError as e:
            # If we get a 401 Unauthorized and haven't already retried auth, try refreshing token
            if e.response.status_code == 401 and retry_auth and self.refresh_token:
                print("🔄 Access token expired, attempting automatic refresh...")
                try:
                    self.refresh_access_token()
                    print("✅ Token refreshed successfully, retrying request...")
                    # Retry the request once with new token (prevent infinite recursion)
                    return self._make_request(method, endpoint, data, params, retry_auth=False)
                except Exception as refresh_error:
                    print(f"❌ Token refresh failed: {refresh_error}")
                    # Fall through to raise the original authentication error
            
            # Re-raise the original error
            raise e
        
    def get_company_info(self) -> Dict[str, Any]:
        """Get company information."""
        response = self._make_request('GET', '/company')
        return response.json()
        
    def test_connection(self) -> bool:
        """Test if the API connection is working."""
        try:
            self.get_company_info()
            return True
        except Exception:
            return False
    
    def check_authentication_status(self) -> Dict[str, Any]:
        """Check authentication status and provide detailed information."""
        status = {
            'has_access_token': bool(self.access_token),
            'has_refresh_token': bool(self.refresh_token),
            'token_expires_at': self.token_expires_at.isoformat() if self.token_expires_at else None,
            'is_expired': False,
            'expires_soon': False,
            'api_accessible': False,
            'needs_refresh': False,
            'needs_reauth': False
        }
        
        if self.token_expires_at:
            now = datetime.now()
            status['is_expired'] = now >= self.token_expires_at
            status['expires_soon'] = now >= self.token_expires_at - timedelta(minutes=5)
            status['needs_refresh'] = status['is_expired'] or status['expires_soon']
        
        # Test API access
        try:
            if self.access_token:
                self.get_company_info()
                status['api_accessible'] = True
        except AuthenticationError:
            status['needs_refresh'] = True
            if not self.refresh_token:
                status['needs_reauth'] = True
        except Exception:
            pass
        
        return status
    
    def ensure_authenticated(self) -> bool:
        """Ensure we're properly authenticated, attempting refresh if needed."""
        status = self.check_authentication_status()
        
        if not status['has_access_token']:
            raise AuthenticationError("No access token available. Please authenticate first.")
        
        if status['needs_refresh'] and status['has_refresh_token']:
            try:
                print("🔄 Refreshing expired tokens...")
                self.refresh_access_token()
                print("✅ Tokens refreshed successfully")
                return True
            except Exception as e:
                print(f"❌ Token refresh failed: {e}")
                raise AuthenticationError("Token refresh failed. Please re-authenticate.")
        
        if status['needs_reauth']:
            raise AuthenticationError("Re-authentication required. Please run setup again.")
        
        if not status['api_accessible']:
            raise AuthenticationError("API not accessible. Please check authentication.")
        
        return True