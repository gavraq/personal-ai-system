"""
FreeAgent Sub-Agent - A Python library for managing FreeAgent invoices.

This package provides a natural language interface for common FreeAgent
invoicing tasks through their API.
"""

from .freeagent_client import FreeAgentClient
from .invoice_manager import InvoiceManager  
from .invoice_subagent import InvoiceSubAgent
from .config import FreeAgentConfig, ConfigHelper
from .exceptions import (
    FreeAgentError,
    AuthenticationError, 
    AuthorizationError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    APIError
)

__version__ = "1.0.0"
__author__ = "Gavin Slater"

__all__ = [
    'FreeAgentClient',
    'InvoiceManager',
    'InvoiceSubAgent', 
    'FreeAgentConfig',
    'ConfigHelper',
    'FreeAgentError',
    'AuthenticationError',
    'AuthorizationError', 
    'RateLimitError',
    'ValidationError',
    'NotFoundError',
    'APIError'
]


def create_subagent(config: FreeAgentConfig = None) -> InvoiceSubAgent:
    """
    Convenience function to create a configured InvoiceSubAgent.
    
    Args:
        config: Optional FreeAgentConfig instance. If not provided,
                will create one from environment/config file.
                
    Returns:
        Configured InvoiceSubAgent instance
        
    Raises:
        ValueError: If configuration is incomplete
    """
    if config is None:
        config = FreeAgentConfig()
        
    if not config.is_configured():
        raise ValueError(
            "FreeAgent not configured. Please set up your credentials first. "
            "Use ConfigHelper.setup_interactive() or set environment variables."
        )
        
    client_id, client_secret = config.get_client_credentials()
    client = FreeAgentClient(
        client_id=client_id,
        client_secret=client_secret,
        sandbox=config.is_sandbox()
    )
    
    # Set tokens if available
    access_token, refresh_token = config.get_tokens()
    if access_token and refresh_token:
        client.set_tokens(access_token, refresh_token)
        
    return InvoiceSubAgent(client)