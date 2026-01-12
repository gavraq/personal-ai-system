#!/bin/bash

# Fabric Patterns Update Script
# Updates community patterns from GitHub and reloads the service
# Usage: ./update-patterns.sh

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PI_HOST="192.168.5.190"
PI_USER="pi"
PI_PASSWORD="raspberry"
REMOTE_DIR="~/docker/fabric"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Fabric Patterns Update${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Check for sshpass
if ! command -v sshpass &> /dev/null; then
    echo -e "${RED}ERROR: sshpass not installed${NC}"
    echo "Install with: brew install hudochenkov/sshpass/sshpass"
    exit 1
fi

# Step 1: Check connectivity
echo -e "${YELLOW}[1/5] Testing Raspberry Pi connectivity...${NC}"
if ! sshpass -p "$PI_PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 "$PI_USER@$PI_HOST" "echo 'Connected'" > /dev/null 2>&1; then
    echo -e "${RED}ERROR: Cannot connect to Raspberry Pi at $PI_HOST${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Connected to Raspberry Pi${NC}"
echo ""

# Step 2: Get current pattern count
echo -e "${YELLOW}[2/5] Getting current pattern count...${NC}"
BEFORE_COUNT=$(sshpass -p "$PI_PASSWORD" ssh "$PI_USER@$PI_HOST" "sudo ls $REMOTE_DIR/config/patterns/ 2>/dev/null | wc -l")
echo -e "${GREEN}✓ Current patterns: $BEFORE_COUNT${NC}"
echo ""

# Step 3: Clone/update fabric repo and sync patterns
echo -e "${YELLOW}[3/5] Downloading latest patterns from GitHub...${NC}"
sshpass -p "$PI_PASSWORD" ssh "$PI_USER@$PI_HOST" << 'REMOTE_SCRIPT'
set -e

# Create temp directory with timestamp
TEMP_DIR="/tmp/fabric_update_$(date +%Y%m%d_%H%M%S)"
FABRIC_DIR=~/docker/fabric

echo "Cloning fabric repository..."
sudo git clone --depth=1 --quiet https://github.com/danielmiessler/fabric.git "$TEMP_DIR"

echo "Syncing patterns..."
sudo rsync -a --delete "$TEMP_DIR/data/patterns/" "$FABRIC_DIR/config/patterns/"

echo "Cleaning up..."
sudo rm -rf "$TEMP_DIR"

echo "Done"
REMOTE_SCRIPT
echo -e "${GREEN}✓ Patterns synced from GitHub${NC}"
echo ""

# Step 4: Restart container
echo -e "${YELLOW}[4/5] Restarting fabric service...${NC}"
sshpass -p "$PI_PASSWORD" ssh "$PI_USER@$PI_HOST" "cd $REMOTE_DIR && docker-compose restart fabric-api" > /dev/null 2>&1
sleep 5
echo -e "${GREEN}✓ Service restarted${NC}"
echo ""

# Step 5: Verify update
echo -e "${YELLOW}[5/5] Verifying update...${NC}"

# Get new pattern count from API
if [ -f "$LOCAL_DIR/.env" ]; then
    source "$LOCAL_DIR/.env"
    HEALTH=$(curl -s -H "X-API-Key: ${FABRIC_API_KEY}" "https://fabric.gavinslater.co.uk/health" 2>/dev/null)
    AFTER_COUNT=$(echo "$HEALTH" | grep -o '"patterns_loaded":[0-9]*' | grep -o '[0-9]*')

    if [ -n "$AFTER_COUNT" ]; then
        echo -e "${GREEN}✓ Service healthy${NC}"
        echo -e "${GREEN}✓ Patterns loaded: $AFTER_COUNT${NC}"
    else
        # Fallback to filesystem count
        AFTER_COUNT=$(sshpass -p "$PI_PASSWORD" ssh "$PI_USER@$PI_HOST" "sudo ls $REMOTE_DIR/config/patterns/ 2>/dev/null | wc -l")
        echo -e "${YELLOW}⚠ Could not verify via API, filesystem count: $AFTER_COUNT${NC}"
    fi
else
    AFTER_COUNT=$(sshpass -p "$PI_PASSWORD" ssh "$PI_USER@$PI_HOST" "sudo ls $REMOTE_DIR/config/patterns/ 2>/dev/null | wc -l")
    echo -e "${YELLOW}⚠ No .env file found, filesystem count: $AFTER_COUNT${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Update Complete${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""
echo -e "Patterns before: ${YELLOW}$BEFORE_COUNT${NC}"
echo -e "Patterns after:  ${GREEN}$AFTER_COUNT${NC}"

if [ "$BEFORE_COUNT" != "$AFTER_COUNT" ]; then
    DIFF=$((AFTER_COUNT - BEFORE_COUNT))
    if [ $DIFF -gt 0 ]; then
        echo -e "Change:          ${GREEN}+$DIFF new patterns${NC}"
    else
        echo -e "Change:          ${YELLOW}$DIFF patterns (some removed upstream)${NC}"
    fi
else
    echo -e "Change:          ${GREEN}No change (already up to date)${NC}"
fi
echo ""
echo -e "Service URL: ${BLUE}https://fabric.gavinslater.co.uk${NC}"
echo ""
