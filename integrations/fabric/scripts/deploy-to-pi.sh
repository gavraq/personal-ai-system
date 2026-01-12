#!/bin/bash

# Fabric Integration - Raspberry Pi Deployment Script
# Deploys Fabric service to Raspberry Pi (192.168.5.190)

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
PI_HOST="192.168.5.190"
PI_USER="pi"
PI_PASSWORD="raspberry"
REMOTE_DIR="~/docker/fabric"
LOCAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Fabric Deployment to Raspberry Pi${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""

# Step 1: Check local .env file exists
echo -e "${YELLOW}[1/7] Checking local .env configuration...${NC}"
if [ ! -f "$LOCAL_DIR/.env" ]; then
    echo -e "${RED}ERROR: .env file not found!${NC}"
    echo "Please create .env from .env.example and configure API keys"
    echo "  cp $LOCAL_DIR/.env.example $LOCAL_DIR/.env"
    echo "  nano $LOCAL_DIR/.env"
    exit 1
fi
echo -e "${GREEN}✓ .env file found${NC}"
echo ""

# Step 2: Verify required environment variables
echo -e "${YELLOW}[2/7] Verifying required environment variables...${NC}"
source "$LOCAL_DIR/.env"
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${RED}ERROR: ANTHROPIC_API_KEY not set in .env${NC}"
    exit 1
fi
if [ -z "$FABRIC_API_KEY" ]; then
    echo -e "${RED}ERROR: FABRIC_API_KEY not set in .env${NC}"
    echo "Generate one with: openssl rand -hex 32"
    exit 1
fi
echo -e "${GREEN}✓ Required API keys configured${NC}"
echo ""

# Step 3: Check connectivity to Raspberry Pi
echo -e "${YELLOW}[3/7] Testing Raspberry Pi connectivity...${NC}"
if ! sshpass -p "$PI_PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 "$PI_USER@$PI_HOST" "echo 'Connected'" > /dev/null 2>&1; then
    echo -e "${RED}ERROR: Cannot connect to Raspberry Pi at $PI_HOST${NC}"
    echo "Please check:"
    echo "  - Raspberry Pi is powered on"
    echo "  - IP address is correct (currently: $PI_HOST)"
    echo "  - Network connectivity"
    exit 1
fi
echo -e "${GREEN}✓ Connected to Raspberry Pi${NC}"
echo ""

# Step 4: Create remote directory structure
echo -e "${YELLOW}[4/7] Creating remote directory structure...${NC}"
sshpass -p "$PI_PASSWORD" ssh "$PI_USER@$PI_HOST" << 'EOF'
mkdir -p ~/docker/fabric/{config,custom-patterns,logs}
mkdir -p ~/docker/fabric/custom-patterns/{daily-reflection,weekly-review,risk-agents-content}
echo "✓ Directories created"
EOF
echo ""

# Step 5: Copy files to Raspberry Pi
echo -e "${YELLOW}[5/7] Copying files to Raspberry Pi...${NC}"

# Copy docker-compose.yml
echo "  - docker-compose.yml"
sshpass -p "$PI_PASSWORD" scp -q "$LOCAL_DIR/docker-compose.yml" "$PI_USER@$PI_HOST:$REMOTE_DIR/"

# Copy .env (contains secrets)
echo "  - .env (API keys)"
sshpass -p "$PI_PASSWORD" scp -q "$LOCAL_DIR/.env" "$PI_USER@$PI_HOST:$REMOTE_DIR/"

# Copy custom patterns
echo "  - Custom patterns"
sshpass -p "$PI_PASSWORD" scp -q -r "$LOCAL_DIR/custom-patterns/." "$PI_USER@$PI_HOST:$REMOTE_DIR/custom-patterns/"

# Copy README
echo "  - README.md"
sshpass -p "$PI_PASSWORD" scp -q "$LOCAL_DIR/README.md" "$PI_USER@$PI_HOST:$REMOTE_DIR/"

echo -e "${GREEN}✓ Files copied${NC}"
echo ""

# Step 6: Run Fabric setup (download patterns)
echo -e "${YELLOW}[6/7] Running Fabric setup (downloading patterns)...${NC}"
echo "This may take a minute..."
sshpass -p "$PI_PASSWORD" ssh "$PI_USER@$PI_HOST" << EOF
cd $REMOTE_DIR
docker-compose run --rm fabric-api --setup
echo "✓ Fabric setup complete"
EOF
echo ""

# Step 7: Start services
echo -e "${YELLOW}[7/7] Starting Fabric service...${NC}"
sshpass -p "$PI_PASSWORD" ssh "$PI_USER@$PI_HOST" << EOF
cd $REMOTE_DIR
docker-compose up -d
echo "✓ Service started"
EOF
echo ""

# Wait for service to be healthy
echo -e "${YELLOW}Waiting for service to be healthy...${NC}"
sleep 10

# Check service status
echo -e "${YELLOW}Checking service status...${NC}"
sshpass -p "$PI_PASSWORD" ssh "$PI_USER@$PI_HOST" << EOF
cd $REMOTE_DIR
echo ""
echo "Container Status:"
docker-compose ps
echo ""
echo "Recent Logs:"
docker-compose logs --tail=20 fabric-api
EOF
echo ""

# Test API endpoint
echo -e "${YELLOW}Testing API endpoint...${NC}"
sshpass -p "$PI_PASSWORD" ssh "$PI_USER@$PI_HOST" << EOF
if curl -s http://localhost:8085/patterns/names > /dev/null 2>&1; then
    echo "✓ API responding"
    pattern_count=\$(curl -s http://localhost:8085/patterns/names | grep -o '"' | wc -l)
    echo "✓ Patterns available: ~\$((pattern_count / 2))"
else
    echo "✗ API not responding yet (may need more time to start)"
fi
EOF
echo ""

# Final summary
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "Fabric service deployed to Raspberry Pi"
echo ""
echo "Access Points:"
echo "  - Internal: http://fabric-api:8080 (Docker network - container internal port)"
echo "  - Raspberry Pi: http://192.168.5.190:8085"
echo "  - External: https://fabric.gavinslater.co.uk (after NGINX config)"
echo ""
echo "Next Steps:"
echo "  1. Configure NGINX reverse proxy for fabric.gavinslater.co.uk"
echo "  2. Test pattern execution:"
echo "     curl -H 'X-API-Key: \$FABRIC_API_KEY' http://192.168.5.190:8085/patterns/names"
echo "  3. Test from Content Processor Agent"
echo ""
echo "Monitoring:"
echo "  - Logs: ssh pi@$PI_HOST 'cd $REMOTE_DIR && docker-compose logs -f fabric-api'"
echo "  - Status: ssh pi@$PI_HOST 'cd $REMOTE_DIR && docker-compose ps'"
echo "  - Restart: ssh pi@$PI_HOST 'cd $REMOTE_DIR && docker-compose restart fabric-api'"
echo ""
