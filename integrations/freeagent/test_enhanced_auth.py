#!/usr/bin/env python3
"""
Test script for enhanced FreeAgent authentication system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import FreeAgentConfig
from freeagent_client import FreeAgentClient
from invoice_subagent import InvoiceSubAgent

def test_enhanced_authentication():
    """Test the enhanced authentication system."""
    print("🧪 Testing Enhanced FreeAgent Authentication System")
    print("=" * 60)
    
    # Load configuration
    config = FreeAgentConfig()
    
    if not config.is_configured():
        print("❌ FreeAgent not configured. Run setup first.")
        return False
    
    # Create client and subagent
    try:
        client_id, client_secret = config.get_client_credentials()
        client = FreeAgentClient(
            client_id=client_id,
            client_secret=client_secret,
            sandbox=config.is_sandbox()
        )
        print("✅ Client created with credentials from config")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    # Load tokens from config
    access_token, refresh_token = config.get_tokens()
    if access_token and refresh_token:
        client.set_tokens(access_token, refresh_token)
        print("✅ Tokens loaded from configuration")
    else:
        print("❌ No tokens found in configuration")
        return False
    
    # Create subagent
    subagent = InvoiceSubAgent(client)
    
    # Test 1: Check authentication status
    print("\n🔍 Test 1: Check Authentication Status")
    auth_status = subagent.check_authentication_status()
    print(f"Status: {'✅ Success' if auth_status['success'] else '❌ Failed'}")
    if auth_status['success']:
        data = auth_status['data']
        print(f"   Access Token: {'✅' if data['has_access_token'] else '❌'}")
        print(f"   Refresh Token: {'✅' if data['has_refresh_token'] else '❌'}")
        print(f"   Token Expired: {'❌' if data['is_expired'] else '✅'}")
        print(f"   API Accessible: {'✅' if data['api_accessible'] else '❌'}")
        if data['token_expires_at']:
            print(f"   Expires At: {data['token_expires_at']}")
    else:
        print(f"   Error: {auth_status['message']}")
    
    # Test 2: Try a simple command that requires authentication
    print("\n📋 Test 2: List Invoices (Authentication Required)")
    result = subagent.process_command("list invoices")
    print(f"Status: {'✅ Success' if result['success'] else '❌ Failed'}")
    print(f"Message: {result['message']}")
    
    if result['success'] and 'data' in result:
        print(f"   Found {len(result['data'])} invoices")
    elif not result['success']:
        print(f"   Error Type: {result.get('error_type', 'unknown')}")
        if result.get('setup_command'):
            print(f"   Run: {result['setup_command']}")
    
    # Test 3: Manual token refresh if needed
    if not result['success'] and 'token' in result.get('message', '').lower():
        print("\n🔄 Test 3: Manual Token Refresh")
        refresh_result = subagent.attempt_token_refresh()
        print(f"Status: {'✅ Success' if refresh_result['success'] else '❌ Failed'}")
        print(f"Message: {refresh_result['message']}")
        
        if refresh_result['success']:
            # Retry the command
            print("\n🔄 Retrying List Invoices After Refresh")
            retry_result = subagent.process_command("list invoices")
            print(f"Status: {'✅ Success' if retry_result['success'] else '❌ Failed'}")
            print(f"Message: {retry_result['message']}")
    
    # Test 4: ICBC invoice creation test (should work with authentication)
    print("\n💰 Test 4: ICBC Invoice Creation Test")
    icbc_result = subagent.process_command("create ICBC invoice for August 2025 21 days")
    print(f"Status: {'✅ Success' if icbc_result['success'] else '❌ Failed'}")
    print(f"Message: {icbc_result['message']}")
    
    if icbc_result['success'] and 'data' in icbc_result:
        calc = icbc_result['data'].get('calculation', {})
        print(f"   Days: {calc.get('days', 'N/A')}")
        print(f"   Rate: £{calc.get('daily_rate', 'N/A')}")
        print(f"   Total: £{calc.get('total_amount', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("🎯 Enhanced Authentication Test Complete!")
    
    return True

if __name__ == "__main__":
    try:
        test_enhanced_authentication()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()