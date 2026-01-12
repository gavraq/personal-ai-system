#!/bin/bash

# Fabric API Test Script
# Tests Fabric API endpoints to verify service is working

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
# Default: Docker network internal access (use this from other containers)
# For local testing: export FABRIC_API_URL=http://localhost:8085
# For Pi testing: export FABRIC_API_URL=http://192.168.5.190:8085
API_URL="${FABRIC_API_URL:-http://fabric-api:8080}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Load API key from .env
if [ -f "$SCRIPT_DIR/.env" ]; then
    source "$SCRIPT_DIR/.env"
fi

if [ -z "$FABRIC_API_KEY" ]; then
    echo -e "${RED}ERROR: FABRIC_API_KEY not set${NC}"
    echo "Either set it in .env or export it as an environment variable"
    exit 1
fi

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Fabric API Test Suite${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "Testing API at: $API_URL"
echo ""

# Test 1: List patterns
echo -e "${YELLOW}Test 1: List Available Patterns${NC}"
response=$(curl -s -w "\n%{http_code}" "$API_URL/patterns/names")
http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "200" ]; then
    pattern_count=$(echo "$body" | jq -r '. | length' 2>/dev/null || echo "0")
    echo -e "${GREEN}✓ PASS${NC} - Retrieved $pattern_count patterns"
    echo "Sample patterns:"
    echo "$body" | jq -r '.[:5][]' 2>/dev/null | sed 's/^/  - /'
else
    echo -e "${RED}✗ FAIL${NC} - HTTP $http_code"
    echo "$body"
fi
echo ""

# Test 2: Get pattern details
echo -e "${YELLOW}Test 2: Get Pattern Details (extract_wisdom)${NC}"
response=$(curl -s -w "\n%{http_code}" "$API_URL/patterns/extract_wisdom")
http_code=$(echo "$response" | tail -n 1)

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Pattern details retrieved"
else
    echo -e "${RED}✗ FAIL${NC} - HTTP $http_code"
fi
echo ""

# Test 3: Execute simple pattern
echo -e "${YELLOW}Test 3: Execute Pattern (summarize)${NC}"
response=$(curl -s -w "\n%{http_code}" \
    -X POST "$API_URL/api/chat" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $FABRIC_API_KEY" \
    -d '{
        "model": "summarize",
        "stream": false,
        "messages": [
            {
                "role": "user",
                "content": "Artificial intelligence is rapidly advancing. Machine learning models can now understand and generate human-like text, recognize images, and make complex decisions. This technology has applications in healthcare, finance, transportation, and many other fields."
            }
        ]
    }')

http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "200" ]; then
    content=$(echo "$body" | jq -r '.choices[0].message.content' 2>/dev/null)
    if [ ! -z "$content" ] && [ "$content" != "null" ]; then
        echo -e "${GREEN}✓ PASS${NC} - Pattern executed successfully"
        echo "Summary output:"
        echo "$content" | head -c 200
        echo "..."
    else
        echo -e "${RED}✗ FAIL${NC} - No content in response"
        echo "$body" | jq '.'
    fi
else
    echo -e "${RED}✗ FAIL${NC} - HTTP $http_code"
    echo "$body"
fi
echo ""

# Test 4: Test custom pattern (if available)
echo -e "${YELLOW}Test 4: Check Custom Patterns${NC}"
custom_patterns=("daily-reflection" "weekly-review" "risk-agents-content")
found_custom=0

for pattern in "${custom_patterns[@]}"; do
    if echo "$body" | jq -r '.[]' 2>/dev/null | grep -q "^$pattern$"; then
        echo -e "${GREEN}✓${NC} Custom pattern found: $pattern"
        found_custom=$((found_custom + 1))
    fi
done

if [ $found_custom -gt 0 ]; then
    echo -e "${GREEN}✓ PASS${NC} - $found_custom custom pattern(s) available"
else
    echo -e "${YELLOW}⚠ WARN${NC} - No custom patterns found (may not be loaded yet)"
fi
echo ""

# Test 5: Authentication test
echo -e "${YELLOW}Test 5: Authentication Test (should fail without API key)${NC}"
response=$(curl -s -w "\n%{http_code}" \
    -X POST "$API_URL/api/chat" \
    -H "Content-Type: application/json" \
    -d '{
        "model": "summarize",
        "messages": [{"role": "user", "content": "test"}]
    }')

http_code=$(echo "$response" | tail -n 1)

if [ "$http_code" = "401" ] || [ "$http_code" = "403" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Authentication correctly enforced"
elif [ "$http_code" = "200" ]; then
    echo -e "${YELLOW}⚠ WARN${NC} - API responding without authentication (may not be configured)"
else
    echo -e "${YELLOW}⚠ INFO${NC} - Unexpected response: HTTP $http_code"
fi
echo ""

# Summary
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Test Summary${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "Fabric API is $([ "$http_code" = "200" ] && echo -e "${GREEN}operational${NC}" || echo -e "${YELLOW}partially operational${NC}")"
echo ""
echo "If tests passed, Fabric is ready for Content Processor Agent integration"
echo ""
