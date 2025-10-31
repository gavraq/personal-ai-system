#!/usr/bin/env python3
"""
Manual GSuite MCP Re-authentication Script v2
Forces fresh authorization to get refresh token and uses mcp-gsuite format.
"""

import json
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime, timedelta

# Configuration
GAUTH_FILE = Path.home() / "mcp-gsuite-test/credentials/.gauth.json"
TOKEN_FILE = Path.home() / "mcp-gsuite-test/credentials/.oauth2.gavin.n.slater@gmail.com.json"
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.readonly'
]

def main():
    print("🔐 GSuite MCP Re-authentication v2")
    print("=" * 50)

    # Load client config
    print(f"📂 Loading OAuth client config from: {GAUTH_FILE}")
    with open(GAUTH_FILE, 'r') as f:
        client_config = json.load(f)

    # Create flow with access_type=offline to force refresh token
    print("🌐 Starting OAuth flow...")
    print("⚠️  Note: You may need to revoke previous authorization at:")
    print("   https://myaccount.google.com/permissions")
    print()

    flow = InstalledAppFlow.from_client_config(
        client_config,
        SCOPES
    )

    # Run local server for OAuth callback
    print("🚀 Opening browser for authentication...")
    print("   Please sign in with: gavin.n.slater@gmail.com")
    print("   Grant the requested permissions")
    print()

    # Force prompt to ensure we get refresh token
    creds = flow.run_local_server(
        port=4100,
        open_browser=True,
        access_type='offline',
        prompt='consent'  # Force consent screen to get refresh token
    )

    # Check if we got a refresh token
    if not creds.refresh_token:
        print("⚠️  Warning: No refresh token received!")
        print("   This may be because you've already authorized this app.")
        print("   Please:")
        print("   1. Visit: https://myaccount.google.com/permissions")
        print("   2. Find and revoke access for this app")
        print("   3. Run this script again")
        exit(1)

    # Save credentials in mcp-gsuite format
    print("✅ Authentication successful!")
    print(f"💾 Saving tokens to: {TOKEN_FILE}")

    # Calculate expiry timestamp
    expiry = datetime.now() + timedelta(seconds=creds.expiry.timestamp() - datetime.now().timestamp())

    # Use mcp-gsuite expected format
    token_data = {
        'access_token': creds.token,
        'expires_in': 3599,
        'refresh_token': creds.refresh_token,
        'scope': ' '.join(SCOPES),
        'token_type': 'Bearer',
        'refresh_token_expires_in': 604799,  # 7 days
        'token_expiry': expiry.isoformat() + 'Z'
    }

    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f, indent=2)

    print("✅ Tokens saved successfully!")
    print(f"   Access token expires: {expiry.isoformat()}")
    print(f"   Refresh token valid for: 7 days")
    print()
    print("🎉 Re-authentication complete!")
    print("   Your GSuite MCP integration is now restored.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Authentication cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
