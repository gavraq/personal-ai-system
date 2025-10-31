#!/usr/bin/env python3
"""
GSuite MCP Token Expiry Monitor
Checks OAuth token expiry and sends notifications when re-authentication is needed.

Usage:
    python3 check-gsuite-token.py              # Check and display status
    python3 check-gsuite-token.py --notify     # Check and send macOS notification if expiring soon
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

# Configuration
TOKEN_FILE = Path.home() / "mcp-gsuite-test/credentials/.oauth2.gavin.n.slater@gmail.com.json"
WARNING_DAYS = 2  # Warn when token expires in less than 2 days


def load_token_data():
    """Load OAuth token data from file."""
    try:
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Token file not found at {TOKEN_FILE}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in token file")
        sys.exit(1)


def parse_expiry(token_data):
    """Parse token expiry timestamp."""
    expiry_str = token_data.get('token_expiry')
    if not expiry_str:
        print("❌ Error: No token_expiry field found")
        sys.exit(1)

    # Handle both ISO format with Z and +00:00
    expiry_str = expiry_str.replace('Z', '+00:00')
    return datetime.fromisoformat(expiry_str)


def get_token_status(expiry):
    """Determine token status and return status info."""
    now = datetime.now(expiry.tzinfo)
    time_remaining = expiry - now

    days_remaining = time_remaining.days
    hours_remaining = time_remaining.seconds // 3600
    minutes_remaining = (time_remaining.seconds % 3600) // 60

    is_expired = now > expiry
    is_expiring_soon = time_remaining < timedelta(days=WARNING_DAYS) and not is_expired

    return {
        'expiry': expiry,
        'now': now,
        'time_remaining': time_remaining,
        'days_remaining': days_remaining,
        'hours_remaining': hours_remaining,
        'minutes_remaining': minutes_remaining,
        'is_expired': is_expired,
        'is_expiring_soon': is_expiring_soon,
    }


def format_time_remaining(status):
    """Format time remaining in human-readable form."""
    if status['is_expired']:
        return "EXPIRED"

    days = status['days_remaining']
    hours = status['hours_remaining']
    minutes = status['minutes_remaining']

    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0 or (days == 0 and minutes > 0):
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if days == 0 and hours < 6:  # Only show minutes if less than 6 hours
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")

    return ", ".join(parts) if parts else "less than 1 minute"


def send_notification(title, message, sound=True):
    """Send macOS notification using osascript."""
    try:
        script = f'display notification "{message}" with title "{title}"'
        if sound:
            script += ' sound name "Glass"'

        subprocess.run(
            ['osascript', '-e', script],
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Warning: Could not send notification")
        return False


def print_status(status, verbose=True):
    """Print token status to console."""
    if status['is_expired']:
        print("🔴 GSuite Token Status: EXPIRED")
        print(f"   Expired: {status['expiry'].strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print()
        print("⚠️  ACTION REQUIRED: Re-authenticate immediately")
        print("   Run: cd ~/mcp-gsuite-test && uvx mcp-gsuite --gauth-file ./credentials/.gauth.json")
        return

    if status['is_expiring_soon']:
        print(f"🟡 GSuite Token Status: EXPIRING SOON")
        print(f"   Expires in: {format_time_remaining(status)}")
        print(f"   Expiry time: {status['expiry'].strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print()
        print("⚠️  RECOMMENDED: Re-authenticate soon to avoid disruption")
        print("   Run: cd ~/mcp-gsuite-test && uvx mcp-gsuite --gauth-file ./credentials/.gauth.json")
        return

    print("✅ GSuite Token Status: VALID")
    print(f"   Expires in: {format_time_remaining(status)}")

    if verbose:
        print(f"   Expiry time: {status['expiry'].strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"   Current time: {status['now'].strftime('%Y-%m-%d %H:%M:%S %Z')}")


def main():
    """Main entry point."""
    # Parse arguments
    notify = '--notify' in sys.argv
    quiet = '--quiet' in sys.argv

    # Load and check token
    token_data = load_token_data()
    expiry = parse_expiry(token_data)
    status = get_token_status(expiry)

    # Print status (unless quiet mode)
    if not quiet:
        print_status(status, verbose=not notify)

    # Send notification if requested
    if notify:
        if status['is_expired']:
            send_notification(
                "GSuite Token Expired",
                "Your GSuite MCP token has expired. Re-authenticate now to restore email access.",
                sound=True
            )
        elif status['is_expiring_soon']:
            send_notification(
                "GSuite Token Expiring Soon",
                f"Your GSuite MCP token expires in {format_time_remaining(status)}. Re-authenticate to avoid disruption.",
                sound=True
            )
        elif not quiet:
            print(f"\nℹ️  No notification sent (token valid for {format_time_remaining(status)})")

    # Exit with appropriate code
    if status['is_expired']:
        sys.exit(2)  # Expired
    elif status['is_expiring_soon']:
        sys.exit(1)  # Warning
    else:
        sys.exit(0)  # OK


if __name__ == '__main__':
    main()
