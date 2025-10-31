"""
Configuration management for FreeAgent sub-agent.
Handles loading credentials from environment variables and config files.
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class FreeAgentConfig:
    """Configuration manager for FreeAgent API credentials and settings."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._default_config_path()
        self.config = self._load_config()
        
    def _default_config_path(self) -> str:
        """Get default configuration file path."""
        home = Path.home()
        config_dir = home / '.config' / 'freeagent'
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir / 'config.json')
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file and environment variables."""
        config = {}
        
        # Try to load from file first
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")
                
        # Override with environment variables if present
        env_config = {
            'client_id': os.getenv('FREEAGENT_CLIENT_ID'),
            'client_secret': os.getenv('FREEAGENT_CLIENT_SECRET'),
            'access_token': os.getenv('FREEAGENT_ACCESS_TOKEN'),
            'refresh_token': os.getenv('FREEAGENT_REFRESH_TOKEN'),
            'sandbox': os.getenv('FREEAGENT_SANDBOX', '').lower() in ('true', '1', 'yes'),
            'redirect_uri': os.getenv('FREEAGENT_REDIRECT_URI', 'http://localhost:8080/callback')
        }
        
        # Update config with non-None environment values
        for key, value in env_config.items():
            if value is not None:
                config[key] = value
                
        return config
        
    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            # Ensure directory exists
            config_dir = Path(self.config_file).parent
            config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save config file {self.config_file}: {e}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
        
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value
        
    def get_client_credentials(self) -> tuple[str, str]:
        """Get client ID and secret for OAuth."""
        client_id = self.get('client_id')
        client_secret = self.get('client_secret')
        
        if not client_id or not client_secret:
            raise ValueError(
                "Client credentials not found. Please set FREEAGENT_CLIENT_ID and "
                "FREEAGENT_CLIENT_SECRET environment variables or configure them in the config file."
            )
            
        return client_id, client_secret
        
    def get_tokens(self) -> tuple[Optional[str], Optional[str]]:
        """Get access and refresh tokens."""
        return self.get('access_token'), self.get('refresh_token')
        
    def save_tokens(self, access_token: str, refresh_token: str) -> None:
        """Save OAuth tokens to configuration."""
        self.set('access_token', access_token)
        self.set('refresh_token', refresh_token)
        self.save_config()
        
    def is_sandbox(self) -> bool:
        """Check if sandbox mode is enabled."""
        return self.get('sandbox', True)  # Default to sandbox for safety
        
    def get_redirect_uri(self) -> str:
        """Get OAuth redirect URI."""
        return self.get('redirect_uri', 'http://localhost:8080/callback')
        
    def is_configured(self) -> bool:
        """Check if basic configuration is present."""
        try:
            self.get_client_credentials()
            return True
        except ValueError:
            return False
            
    def has_tokens(self) -> bool:
        """Check if OAuth tokens are available."""
        access_token, refresh_token = self.get_tokens()
        return bool(access_token and refresh_token)
        
    def get_summary(self) -> Dict[str, Any]:
        """Get configuration summary for debugging."""
        return {
            'config_file': self.config_file,
            'has_client_id': bool(self.get('client_id')),
            'has_client_secret': bool(self.get('client_secret')),
            'has_access_token': bool(self.get('access_token')),
            'has_refresh_token': bool(self.get('refresh_token')),
            'sandbox_mode': self.is_sandbox(),
            'redirect_uri': self.get_redirect_uri(),
            'is_configured': self.is_configured(),
            'has_tokens': self.has_tokens()
        }


class ConfigHelper:
    """Helper class for interactive configuration setup."""
    
    @staticmethod
    def setup_interactive() -> FreeAgentConfig:
        """Interactive setup for first-time configuration."""
        print("FreeAgent Sub-Agent Configuration Setup")
        print("=" * 40)
        
        config = FreeAgentConfig()
        
        if config.is_configured():
            print("Configuration already exists.")
            if input("Do you want to reconfigure? (y/n): ").lower() == 'y':
                config = FreeAgentConfig()  # Start fresh
            else:
                return config
                
        print("\nYou'll need to create a FreeAgent app first:")
        print("1. Go to https://dev.freeagent.com/")
        print("2. Create a new application")
        print("3. Note down your Client ID and Client Secret")
        print()
        
        client_id = input("Enter your FreeAgent Client ID: ").strip()
        client_secret = input("Enter your FreeAgent Client Secret: ").strip()
        
        use_sandbox = input("Use sandbox environment? (y/n, default: y): ").lower()
        sandbox = use_sandbox != 'n'
        
        redirect_uri = input("Enter redirect URI (default: http://localhost:8080/callback): ").strip()
        if not redirect_uri:
            redirect_uri = "http://localhost:8080/callback"
            
        config.set('client_id', client_id)
        config.set('client_secret', client_secret)
        config.set('sandbox', sandbox)
        config.set('redirect_uri', redirect_uri)
        
        config.save_config()
        
        print(f"\nConfiguration saved to: {config.config_file}")
        print("Next steps:")
        print("1. Run the OAuth authorization flow to get tokens")
        print("2. Start using the sub-agent!")
        
        return config
        
    @staticmethod
    def print_env_template():
        """Print environment variable template."""
        template = """
# FreeAgent API Configuration
export FREEAGENT_CLIENT_ID="your_client_id_here"
export FREEAGENT_CLIENT_SECRET="your_client_secret_here"
export FREEAGENT_ACCESS_TOKEN="your_access_token_here"  # Optional, can be set after OAuth
export FREEAGENT_REFRESH_TOKEN="your_refresh_token_here"  # Optional, can be set after OAuth
export FREEAGENT_SANDBOX="true"  # Use sandbox environment
export FREEAGENT_REDIRECT_URI="http://localhost:8080/callback"  # OAuth redirect URI
        """
        print("Environment Variables Template:")
        print(template)