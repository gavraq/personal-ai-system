# Personal AI System - Migration Plan

**Date**: October 31, 2025
**Status**: Ready for Execution
**Goal**: Transform `/Users/gavinslater/projects/life/` into `gavraq/personal-ai-system` with proper microservices architecture

---

## Executive Summary

This migration creates a clean separation between:
- **System Configuration** (personal-ai-system git repo) - UFC context, integrations, orchestration
- **Standalone Services** (separate git repos) - health-service, claude-agent-server, interactive-cv-website
- **External Services** (third-party repos) - owntracks location service

**Critical Fix**: Establishes shared Docker network to enable service-to-service communication (currently blocking health agent).

---

## Target Architecture

```
/Users/gavinslater/projects/life/              # Git: gavraq/personal-ai-system
├── .claude/                                    # UFC Context (single source of truth)
│   ├── context/                               # Always-loaded context
│   │   ├── profile/
│   │   │   ├── core-identity.md
│   │   │   └── goals-objectives.md
│   │   ├── active-projects/                   # 8 project summaries
│   │   │   ├── ai-coding-projects.md
│   │   │   ├── job-search.md
│   │   │   ├── finances-context.md
│   │   │   ├── health-context.md
│   │   │   ├── cv-website-development.md
│   │   │   ├── location-tracking-context.md
│   │   │   ├── daily-journal-context.md
│   │   │   └── gtd-task-management.md
│   │   └── tools/                             # Complete tools portfolio
│   │       ├── CLAUDE.md
│   │       ├── gmail-mcp-context.md
│   │       ├── freeagent-api-context.md
│   │       ├── linkedin-api-context.md
│   │       ├── parkrun-api-context.md
│   │       └── location-integration-context.md
│   ├── agents/                                # Full agent definitions (10 agents)
│   │   ├── personal-consultant.md
│   │   ├── email-management-agent.md
│   │   ├── freeagent-invoice-agent.md
│   │   ├── job-search-agent.md
│   │   ├── health-agent.md
│   │   ├── location-agent.md
│   │   ├── interactive-cv-website-agent.md
│   │   ├── knowledge-manager-agent.md
│   │   ├── daily-brief-agent.md
│   │   └── gtd-task-manager-agent.md
│   └── commands/                              # Simple repeatable tasks
│       ├── daily-brief.md
│       ├── daily-note.md
│       ├── daily-journal-morning.md
│       └── daily-journal-evening.md
├── CLAUDE.md                                   # Master system documentation
├── README.md                                   # System overview
├── MIGRATION-PLAN.md                           # This file
├── docker-compose.yml                          # Master orchestration (Pi only)
├── .gitignore                                  # Exclude services/
├── integrations/                               # Integration implementations
│   ├── health/                                # Health data integration
│   │   ├── CLAUDE.md                          # Technical docs
│   │   ├── README.md                          # User docs
│   │   ├── python-client/                     # REST API wrapper
│   │   │   ├── health_data_client.py
│   │   │   └── __init__.py
│   │   ├── scripts/
│   │   │   └── rebuild_health_database.py
│   │   ├── apple-health-auto-export-setup.md
│   │   └── device-priority-guidelines.md
│   ├── location/                              # Location tracking integration
│   │   ├── CLAUDE.md
│   │   ├── README.md
│   │   ├── python-client/
│   │   │   ├── owntracks_client.py
│   │   │   └── __init__.py
│   │   └── docs/
│   │       ├── API.md
│   │       ├── SETUP.md
│   │       └── QUERIES.md
│   ├── freeagent/                             # Financial integration
│   │   ├── CLAUDE.md
│   │   ├── README.md
│   │   ├── oauth_test.py
│   │   ├── generate_invoice_test.py
│   │   ├── .env.template
│   │   └── docs/
│   ├── linkedin/                              # Career development integration
│   │   ├── CLAUDE.md
│   │   ├── README.md
│   │   ├── linkedin-actor-enhanced.js
│   │   └── docs/
│   ├── gmail-calendar/                        # Email/calendar MCP server
│   │   ├── CLAUDE.md
│   │   ├── README.md
│   │   ├── .accounts.json
│   │   ├── credentials/
│   │   └── docs/
│   ├── daily-brief/                           # News curation integration
│   │   ├── CLAUDE.md
│   │   ├── README.md
│   │   └── docs/
│   │       └── API.md
│   └── personal-knowledge/                    # Knowledge management
│       └── obsidian/                          # Obsidian vault integration
│           ├── CLAUDE.md
│           ├── README.md
│           └── docs/
└── services/                                   # ❌ EXCLUDED FROM GIT
    ├── health-service/                        # Git: gavraq/health-service
    │   ├── src/
    │   ├── data/
    │   ├── logs/
    │   ├── package.json
    │   └── docker-compose.yml
    ├── claude-agent-server/                   # Git: gavraq/claude-agent-server
    │   ├── src/
    │   ├── dist/
    │   ├── package.json
    │   └── docker-compose.yml
    ├── interactive-cv-website/                # Git: gavraq/interactive-cv-website
    │   ├── src/
    │   ├── package.json
    │   └── vercel.json
    └── location-service/                      # Git: owntracks/docker-recorder
        └── owntracks/                         # External repo (not ours)
```

---

## Migration Phases

### Phase 1: Preparation (Mac) ✅ SAFE TO EXECUTE

**Objective**: Organize integrations, create .gitignore, prepare for git init

#### Step 1.1: Create Integrations Directory Structure

```bash
cd /Users/gavinslater/projects/life/

# Create integrations structure
mkdir -p integrations/health
mkdir -p integrations/location
mkdir -p integrations/freeagent
mkdir -p integrations/linkedin
mkdir -p integrations/gmail-calendar
mkdir -p integrations/daily-brief
mkdir -p integrations/personal-knowledge/obsidian

# Create services directory (will be excluded from git)
mkdir -p services
```

#### Step 1.2: Move Integration Files

```bash
# Health Integration
mv health-integration/* integrations/health/
rmdir health-integration

# Location Integration
mv location-integration/* integrations/location/
rmdir location-integration

# FreeAgent Integration (rename from freeagent_subagent)
mv freeagent_subagent/* integrations/freeagent/
rmdir freeagent_subagent

# LinkedIn Integration
mv linkedin-integration/* integrations/linkedin/
rmdir linkedin-integration

# Gmail Calendar MCP (rename from mcp-gsuite-test)
mv mcp-gsuite-test/* integrations/gmail-calendar/
rmdir mcp-gsuite-test

# Daily Brief Integration
mv daily-brief-system/* integrations/daily-brief/
rmdir daily-brief-system

# Personal Knowledge (Obsidian)
# Note: Obsidian vault stays on Mac, integration code only
echo "# Personal Knowledge Service - Obsidian Integration" > integrations/personal-knowledge/obsidian/README.md
```

#### Step 1.3: Consolidate UFC Context

```bash
# Remove duplicate life-context directory (keep .claude/ as single source of truth)
rm -rf life-context

# Verify .claude/ structure
ls -la .claude/context/
ls -la .claude/agents/
ls -la .claude/commands/
```

#### Step 1.4: Move Service Repositories

```bash
# Move existing service directories to services/
mv health-service services/
mv claude-agent-server services/
mv interactive-cv-website services/

# Note: location-service (owntracks) is external, not moved here
```

#### Step 1.5: Create .gitignore

```bash
cat > .gitignore << 'EOF'
# Service Repositories (separate git repos)
services/

# Sensitive Credentials
.env
.env.local
.gauth.json
.accounts.json
.oauth2.*.json
credentials/

# Python
venv/
__pycache__/
*.pyc
*.pyo

# Node.js
node_modules/
npm-debug.log

# Database Files
*.db
*.sqlite

# OS Files
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Temporary Files
tmp/
temp/
EOF
```

#### Step 1.6: Update Master Documentation

**Update CLAUDE.md** to reflect new structure:

```bash
# Edit CLAUDE.md to update all paths from old structure to new
# Example replacements:
# - health-integration/ → integrations/health/
# - location-integration/ → integrations/location/
# - freeagent_subagent/ → integrations/freeagent/
# - life-context/.claude/ → .claude/
```

---

### Phase 2: Git Repository Setup (Mac) ✅ SAFE TO EXECUTE

**Objective**: Initialize personal-ai-system as git repository

#### Step 2.1: Initialize Git Repository

```bash
cd /Users/gavinslater/projects/life/

# Initialize git
git init

# Add all files (services/ excluded by .gitignore)
git add .

# Create initial commit
git commit -m "Initial commit: Personal AI System v1.0

- UFC context system (.claude/)
- 7 integrations (health, location, freeagent, linkedin, gmail-calendar, daily-brief, personal-knowledge)
- Master orchestration (docker-compose.yml)
- Comprehensive documentation

Services (excluded from repo):
- health-service (gavraq/health-service)
- claude-agent-server (gavraq/claude-agent-server)
- interactive-cv-website (gavraq/interactive-cv-website)
- location-service (owntracks/docker-recorder)

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

#### Step 2.2: Create GitHub Repository

```bash
# Create GitHub repo (requires gh CLI)
gh repo create gavraq/personal-ai-system \
  --public \
  --description "Personal AI Infrastructure - UFC context, integrations, and orchestration" \
  --source=. \
  --remote=origin

# Push to GitHub
git push -u origin main
```

---

### Phase 3: Docker Network Fix (Pi) 🚨 CRITICAL

**Objective**: Enable service-to-service communication with shared Docker network

**Current Issue**: Services on isolated networks cannot communicate:
- `health-service` on `health-service_health-network`
- `claude-agent-server` on `claude-agent-server_claude-network`

#### Step 3.1: Create Shared Network on Pi

```bash
# SSH to Pi
ssh pi@192.168.5.190

# Create shared network
docker network create personal-ai

# Verify network created
docker network ls | grep personal-ai
```

#### Step 3.2: Update Health Service Docker Compose

```bash
# Edit health-service docker-compose.yml
nano ~/docker/health-service/docker-compose.yml
```

**Update to:**

```yaml
version: '3.8'

services:
  health-service:
    build: .
    container_name: health-service
    restart: unless-stopped
    ports:
      - "3001:3001"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - .env:/app/.env
    environment:
      - NODE_ENV=production
      - PORT=3001
    networks:
      - personal-ai

networks:
  personal-ai:
    external: true
```

#### Step 3.3: Update Claude Agent Server Docker Compose

```bash
# Edit claude-agent-server docker-compose.yml
nano ~/docker/claude-agent-server/docker-compose.yml
```

**Update to:**

```yaml
version: '3.8'

services:
  claude-agent-server:
    build: .
    container_name: claude-agent-server
    restart: unless-stopped
    ports:
      - "3002:3002"
    volumes:
      - ../personal-ai-system/.claude/context:/ufc:ro
      - ../personal-ai-system/.claude:/claude-config:ro
    environment:
      - NODE_ENV=production
      - PORT=3002
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - JWT_SECRET=${JWT_SECRET}
      - HEALTH_SERVICE_URL=http://health-service:3001
      - LOCATION_SERVICE_URL=http://owntracks-api:8083
    networks:
      - personal-ai

networks:
  personal-ai:
    external: true
```

#### Step 3.4: Rebuild and Restart Services

```bash
# Stop existing services
cd ~/docker/health-service && docker-compose down
cd ~/docker/claude-agent-server && docker-compose down

# Rebuild (picks up new network config)
cd ~/docker/health-service && docker-compose build
cd ~/docker/claude-agent-server && docker-compose build

# Start with new network
cd ~/docker/health-service && docker-compose up -d
cd ~/docker/claude-agent-server && docker-compose up -d

# Verify connectivity
docker exec claude-agent-server ping -c 3 health-service
docker exec claude-agent-server curl http://health-service:3001/health
```

**Expected Result**: Ping succeeds, health endpoint returns JSON response

---

### Phase 4: Deploy to Pi (Pi) ✅ SAFE TO EXECUTE

**Objective**: Clone personal-ai-system to Pi, update service configurations

#### Step 4.1: Clone Repository to Pi

```bash
# SSH to Pi
ssh pi@192.168.5.190

# Clone personal-ai-system
cd ~/docker
git clone https://github.com/gavraq/personal-ai-system.git

# Verify structure
ls -la ~/docker/personal-ai-system/.claude/
ls -la ~/docker/personal-ai-system/integrations/
```

#### Step 4.2: Set Up Auto-Sync (Cron Job)

```bash
# Edit crontab
crontab -e

# Add auto-sync job (every 15 minutes)
# Add this line:
*/15 * * * * cd ~/docker/personal-ai-system && git pull origin main >> ~/logs/personal-ai-sync.log 2>&1
```

#### Step 4.3: Update Volume Mounts (Already Done in Phase 3)

Volume mounts already updated in Phase 3.3:
```yaml
volumes:
  - ../personal-ai-system/.claude/context:/ufc:ro
  - ../personal-ai-system/.claude:/claude-config:ro
```

---

### Phase 5: Update Documentation (Mac) ✅ SAFE TO EXECUTE

**Objective**: Update all documentation to reflect new architecture

#### Step 5.1: Update Health Agent Definition

```bash
# Edit health-agent.md
vim /Users/gavinslater/projects/life/.claude/agents/health-agent.md
```

**Update Python client initialization section:**

```python
# Environment-aware service URL
import os

# For containerized environment (Pi/Docker):
base_url = os.getenv('HEALTH_SERVICE_URL', 'http://health-service:3001')

# For local Mac development:
# base_url = 'http://localhost:3001'

client = HealthClient(base_url=base_url)
```

#### Step 5.2: Update Integration Documentation

```bash
# Update health integration docs
vim /Users/gavinslater/projects/life/integrations/health/CLAUDE.md

# Update locations to reflect new paths:
# - Service: services/health-service/ (separate git repo)
# - Integration: integrations/health/ (part of personal-ai-system)
# - Python Client: integrations/health/python-client/
```

#### Step 5.3: Remove Obsolete Documentation

```bash
# Remove old audit files (from October cleanup)
rm /Users/gavinslater/projects/life/integrations/health/file-audit.md
rm /Users/gavinslater/projects/life/integrations/health/cleanup-summary.md

# Remove duplicate context files if any exist
find /Users/gavinslater/projects/life/integrations/ -name "*.md" -type f | grep -i context
# Review and remove duplicates
```

#### Step 5.4: Update Master CLAUDE.md

Already created comprehensive CLAUDE.md with UFC protocol. Verify it references:
- New integration paths
- Shared Docker network
- Environment variables for service URLs
- Microservices architecture

#### Step 5.5: Create Integration README Files

Create standardized README.md for each integration:

```bash
# Template for integration README.md
cat > /Users/gavinslater/projects/life/integrations/health/README.md << 'EOF'
# Health Integration

Apple Health + Parkrun data integration for quantified self tracking.

## Overview

Provides health data access to AI agents through Python client wrapper around the health-service REST API.

## Components

- **Python Client**: `python-client/health_data_client.py` - REST API wrapper
- **Service**: `../../services/health-service/` (separate git repo: gavraq/health-service)
- **Documentation**: `CLAUDE.md` - Technical implementation details

## Usage

### From Mac (Local Development)

```python
from integrations.health.python_client import HealthClient

client = HealthClient(base_url='http://localhost:3001')
summary = client.get_summary(days=7)
print(summary)
```

### From Docker Container (Production)

```python
import os
from integrations.health.python_client import HealthClient

# Uses HEALTH_SERVICE_URL environment variable
base_url = os.getenv('HEALTH_SERVICE_URL', 'http://health-service:3001')
client = HealthClient(base_url=base_url)
summary = client.get_summary(days=7)
print(summary)
```

## Setup

See [CLAUDE.md](CLAUDE.md) for detailed setup instructions.

## Service Architecture

This integration connects to the standalone health-service microservice running in Docker. The service provides:

- Apple Health data access (5.3M records)
- Parkrun results integration
- Aggregated health summaries
- Time-based queries

**Service Repository**: https://github.com/gavraq/health-service
EOF
```

Repeat similar README creation for other integrations.

---

### Phase 6: Verification (Mac + Pi) ✅ TESTING

**Objective**: Verify complete system functionality

#### Step 6.1: Verify Mac Structure

```bash
cd /Users/gavinslater/projects/life/

# Check git status (services/ should be excluded)
git status

# Verify UFC context structure
ls -la .claude/context/profile/
ls -la .claude/context/active-projects/
ls -la .claude/context/tools/

# Verify integrations
ls -la integrations/

# Verify services are excluded from git
ls -la services/
git check-ignore services/
# Should output: services/
```

#### Step 6.2: Verify Pi Deployment

```bash
# SSH to Pi
ssh pi@192.168.5.190

# Check personal-ai-system clone
ls -la ~/docker/personal-ai-system/.claude/
ls -la ~/docker/personal-ai-system/integrations/

# Check service status
docker ps | grep -E "(health-service|claude-agent-server)"

# Check network connectivity
docker network inspect personal-ai | grep -A 3 "health-service"
docker network inspect personal-ai | grep -A 3 "claude-agent-server"

# Test service communication
docker exec claude-agent-server curl http://health-service:3001/health
# Expected: {"status":"healthy","database":"connected","records":5300000}
```

#### Step 6.3: Test Health Agent End-to-End

**From Web UI** (https://gavinslater.com):

1. Log in with credentials
2. Ask health agent: "What was my step count yesterday?"
3. Verify response includes:
   - UFC context (mentions GTD system/goals)
   - Actual health data from service
   - Proper formatting and analysis

**Expected Log Output on Pi:**

```bash
# Check claude-agent-server logs
docker logs claude-agent-server --tail 50

# Should show:
# [INFO] Processing agent request
# [INFO] Loading UFC context: 8 projects, 6 tools, 10 agents
# [INFO] Spawning Python SDK handler
# [INFO] System prompt length: 45000+ characters
# [INFO] Streaming response started
# [INFO] Response completed successfully
```

#### Step 6.4: Verify Location Service Integration

```bash
# Check owntracks is running
docker ps | grep owntracks

# Test location service connectivity from agent server
docker exec claude-agent-server curl http://owntracks-api:8083/api/0/last
# Expected: JSON with latest location data
```

---

## Rollback Plan

### If Issues Occur During Migration

#### Rollback from Phase 1 (Mac Structure Changes)

```bash
cd /Users/gavinslater/projects/life/

# Restore original structure from git
git checkout HEAD -- .

# Or manually restore from backup
cp -r ~/backup/life-before-migration/* .
```

#### Rollback from Phase 3 (Docker Network Changes)

```bash
# SSH to Pi
ssh pi@192.168.5.190

# Restore original docker-compose files
cd ~/docker/health-service
git checkout docker-compose.yml
docker-compose down && docker-compose up -d

cd ~/docker/claude-agent-server
git checkout docker-compose.yml
docker-compose down && docker-compose up -d

# Remove shared network (optional)
docker network rm personal-ai
```

---

## Post-Migration Cleanup

### Remove Obsolete Directories

```bash
# On Mac (after confirming migration successful)
cd /Users/gavinslater/projects/life/

# Already done in Phase 1, but verify no remnants:
rm -rf health-integration
rm -rf location-integration
rm -rf freeagent_subagent
rm -rf linkedin-integration
rm -rf mcp-gsuite-test
rm -rf daily-brief-system
rm -rf life-context
```

### Update Other Systems

1. **Update Mac Claude Code Config** (if referencing old paths):
   ```bash
   # No changes needed - .claude/ stays in same location
   ```

2. **Update Pi Cron Jobs** (if any reference old paths):
   ```bash
   crontab -e
   # Verify no references to ~/life-context
   ```

3. **Update Obsidian Vault References** (if any):
   - Vault location unchanged: `/Users/gavinslater/Library/Mobile Documents/iCloud~md~obsidian/Documents/GavinsiCloudVault/`
   - No action needed

---

## Architecture Benefits

### Before Migration

```
/Users/gavinslater/projects/life/
├── health-integration/          # Integration + docs
├── health-service/              # Service repo
├── location-integration/        # Integration + docs
├── freeagent_subagent/         # Integration + docs
├── linkedin-integration/        # Integration + docs
├── mcp-gsuite-test/            # MCP server
├── daily-brief-system/         # Integration
├── claude-agent-server/        # Service repo
├── interactive-cv-website/     # Service repo
├── life-context/.claude/       # Duplicate UFC context
└── .claude/                    # UFC context

Problems:
- ❌ Duplicate UFC context (life-context/.claude/ AND .claude/)
- ❌ Mixed integrations and services at root level
- ❌ Inconsistent naming (freeagent_subagent vs others)
- ❌ Services on isolated Docker networks (can't communicate)
- ❌ No git repository for system configuration
- ❌ Unclear what should be version-controlled vs excluded
```

### After Migration

```
/Users/gavinslater/projects/life/           # Git: gavraq/personal-ai-system
├── .claude/                                 # Single source of truth UFC context
├── integrations/                            # All integrations organized
│   ├── health/
│   ├── location/
│   ├── freeagent/
│   ├── linkedin/
│   ├── gmail-calendar/
│   ├── daily-brief/
│   └── personal-knowledge/obsidian/
├── services/                                # Separate repos (excluded from git)
│   ├── health-service/
│   ├── claude-agent-server/
│   ├── interactive-cv-website/
│   └── location-service/owntracks/
├── docker-compose.yml                       # Master orchestration
└── CLAUDE.md                                # Master documentation

Benefits:
- ✅ Single UFC context source (.claude/)
- ✅ Clear separation: integrations (in git) vs services (excluded)
- ✅ Consistent naming and structure
- ✅ Shared Docker network (services can communicate)
- ✅ Version-controlled system configuration
- ✅ Clear .gitignore for sensitive data
- ✅ Plug-and-play microservices architecture
- ✅ Multi-access support (Mac, Web, future Mobile)
```

---

## Success Criteria

### Phase 1 Success
- [ ] Integrations directory created with 7 subdirectories
- [ ] All integration files moved successfully
- [ ] Services directory created with 3 service repos moved
- [ ] life-context directory removed (duplicate eliminated)
- [ ] .gitignore created excluding services/
- [ ] CLAUDE.md updated with new paths

### Phase 2 Success
- [ ] Git repository initialized
- [ ] Initial commit created
- [ ] GitHub repo created: gavraq/personal-ai-system
- [ ] Code pushed to GitHub successfully
- [ ] Services directory confirmed excluded from git

### Phase 3 Success
- [ ] Shared Docker network `personal-ai` created
- [ ] health-service docker-compose.yml updated
- [ ] claude-agent-server docker-compose.yml updated
- [ ] Services restarted on shared network
- [ ] Connectivity test passes: `curl http://health-service:3001/health`

### Phase 4 Success
- [ ] personal-ai-system cloned to Pi at ~/docker/
- [ ] Auto-sync cron job configured (every 15 minutes)
- [ ] Volume mounts verified pointing to new location
- [ ] UFC context loading verified in logs (8 projects, 6 tools, 10 agents)

### Phase 5 Success
- [ ] health-agent.md updated with environment-aware URLs
- [ ] Integration README files created (all 7 integrations)
- [ ] Obsolete documentation removed (file-audit.md, cleanup-summary.md)
- [ ] Master CLAUDE.md reflects new architecture

### Phase 6 Success
- [ ] Mac structure verified with git status
- [ ] Pi deployment verified with docker ps
- [ ] Network connectivity confirmed between services
- [ ] Health agent end-to-end test passes via web UI
- [ ] UFC context appears in agent responses
- [ ] No errors in claude-agent-server logs

---

## Estimated Timeline

- **Phase 1** (Mac Preparation): 15 minutes
- **Phase 2** (Git Setup): 10 minutes
- **Phase 3** (Docker Network Fix): 20 minutes
- **Phase 4** (Pi Deployment): 15 minutes
- **Phase 5** (Documentation Update): 30 minutes
- **Phase 6** (Verification): 20 minutes

**Total Estimated Time**: ~2 hours

**Recommended Approach**: Execute phases sequentially with verification at each step. Do not proceed to next phase if current phase fails.

---

## Support and Troubleshooting

### Common Issues

**Issue 1: Services still can't communicate after network change**

```bash
# Verify both services are on personal-ai network
docker network inspect personal-ai

# Check for IP address assignment
docker inspect health-service | grep -A 10 Networks
docker inspect claude-agent-server | grep -A 10 Networks

# Test DNS resolution
docker exec claude-agent-server nslookup health-service
docker exec claude-agent-server ping health-service

# Check firewall rules (should not block internal Docker network)
sudo iptables -L -n | grep 172.
```

**Issue 2: UFC context not loading on Pi**

```bash
# Verify volume mount path exists
ls -la ~/docker/personal-ai-system/.claude/context/

# Check volume mount in container
docker exec claude-agent-server ls -la /ufc/

# Check logs for loading errors
docker logs claude-agent-server | grep -i "ufc\|context"
```

**Issue 3: Git sync not working on Pi**

```bash
# Check cron log
cat ~/logs/personal-ai-sync.log

# Test manual pull
cd ~/docker/personal-ai-system && git pull origin main

# Check cron is running
systemctl status cron

# Verify crontab entry
crontab -l | grep personal-ai
```

**Issue 4: Health agent returns localhost connection errors**

```bash
# Check if health-service is running
docker ps | grep health-service

# Check if HEALTH_SERVICE_URL env var is set in agent server
docker exec claude-agent-server env | grep HEALTH_SERVICE_URL

# If missing, add to docker-compose.yml environment section
```

---

## Next Steps After Migration

1. **Test All Agents**: Run through each specialized agent (email, freeagent, job-search, location, etc.)

2. **Performance Monitoring**: Set up monitoring for:
   - Docker container health
   - Service response times
   - UFC context loading times
   - Agent request success rates

3. **Backup Strategy**: Implement automated backups for:
   - health.db (1.7GB Apple Health data)
   - UFC context (.claude/ directory)
   - Agent conversation histories
   - Service configurations

4. **Mobile Access**: Begin Telegram bot development for mobile access to agents

5. **Documentation**: Complete README files for all 7 integrations with usage examples

6. **Master Orchestration**: Create comprehensive docker-compose.yml at root level to manage all services from single command

---

**Migration Plan Version**: 1.0
**Created**: October 31, 2025
**Author**: Claude Code
**Status**: Ready for Execution
