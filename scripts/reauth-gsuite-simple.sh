#!/bin/bash
# Simple re-authentication wrapper for mcp-gsuite
# This uses the exact same method as the MCP server

cd /Users/gavinslater/mcp-gsuite-test

echo "🔐 GSuite MCP Re-authentication"
echo "================================================"
echo ""
echo "Starting authentication flow..."
echo "Browser should open automatically."
echo ""
echo "Please:"
echo "  1. Sign in with: gavin.n.slater@gmail.com"
echo "  2. Grant the requested permissions"
echo "  3. Wait for success message"
echo ""

# Use uvx with explicit environment to ensure browser opens
export BROWSER=open
uvx mcp-gsuite --gauth-file ./credentials/.gauth.json

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Re-authentication complete!"
    echo "   Your GSuite MCP integration is restored."
else
    echo ""
    echo "❌ Re-authentication failed."
    echo "   Please try again or check the error messages above."
    exit 1
fi
