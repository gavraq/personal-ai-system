#!/bin/bash
# Check OAuth token expiry for Gmail MCP

TOKEN_FILE="/Users/gavinslater/mcp-gsuite-test/credentials/.oauth2.gavin.n.slater@gmail.com.json"

if [ ! -f "$TOKEN_FILE" ]; then
    echo "❌ OAuth token file not found - needs authentication"
    exit 1
fi

# Extract token expiry (if present)
EXPIRY=$(cat "$TOKEN_FILE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('token_expiry', 'N/A'))")

if [ "$EXPIRY" = "N/A" ] || [ "$EXPIRY" = "null" ]; then
    echo "⚠️  No expiry date found in token"
    exit 0
fi

# Convert expiry to timestamp and compare with current time
EXPIRY_TS=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$EXPIRY" "+%s" 2>/dev/null)
CURRENT_TS=$(date "+%s")

if [ $? -ne 0 ]; then
    echo "⚠️  Could not parse expiry date: $EXPIRY"
    exit 0
fi

HOURS_REMAINING=$(( ($EXPIRY_TS - $CURRENT_TS) / 3600 ))

if [ $HOURS_REMAINING -lt 0 ]; then
    echo "❌ Token expired $((-$HOURS_REMAINING)) hours ago"
    exit 1
elif [ $HOURS_REMAINING -lt 24 ]; then
    echo "⚠️  Token expires in $HOURS_REMAINING hours"
    exit 0
else
    DAYS_REMAINING=$(( $HOURS_REMAINING / 24 ))
    echo "✅ Token valid for $DAYS_REMAINING days"
    exit 0
fi
