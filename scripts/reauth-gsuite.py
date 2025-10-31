#!/usr/bin/env python3
"""
Manual GSuite MCP Re-authentication Script
Opens browser for OAuth flow and saves tokens.
"""

import json
import webbrowser
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Configuration
GAUTH_FILE = Path.home() / "mcp-gsuite-test/credentials/.gauth.json"
TOKEN_FILE = Path.home() / "mcp-gsuite-test/credentials/.oauth2.gavin.n.slater@gmail.com.json"
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.readonly'
]

def main():
    print("🔐 GSuite MCP Re-authentication")
    print("=" * 50)

    # Load client config
    print(f"📂 Loading OAuth client config from: {GAUTH_FILE}")
    with open(GAUTH_FILE, 'r') as f:
        client_config = json.load(f)

    # Create flow
    print("🌐 Starting OAuth flow...")
    flow = InstalledAppFlow.from_client_config(
        client_config,
        SCOPES,
        redirect_uri='http://localhost:4100/code'
    )

    # Run local server for OAuth callback
    print("🚀 Opening browser for authentication...")
    print("   Please sign in with: gavin.n.slater@gmail.com")
    print("   Grant the requested permissions")
    print()

    creds = flow.run_local_server(port=4100, open_browser=True)

    # Save credentials
    print("✅ Authentication successful!")
    print(f"💾 Saving tokens to: {TOKEN_FILE}")

    token_data = {
        'access_token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes,
        'expiry': creds.expiry.isoformat() if creds.expiry else None
    }

    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f, indent=2)

    print("✅ Tokens saved successfully!")
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
        exit(1)
