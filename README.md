# Personal AI System

**Version**: 1.0
**Status**: Production Ready
**Owner**: Gavin Slater
**Repository**: https://github.com/gavraq/personal-ai-system

---

## Overview

A comprehensive microservices-based Personal AI Infrastructure leveraging Claude AI with Universal File Context (UFC) for intelligent, goal-aligned personal assistance across productivity, health, career, and life optimization domains.

### Key Features

- **🧠 Universal File Context (UFC)**: Complete system awareness with GTD methodology integration
- **🎪 15 Specialized AI Agents**: Gmail/Calendar, health, location, finances, job search, content processing, and more
- **🛠️ Plug-and-Play Architecture**: Independent microservices with standardized integrations
- **📊 Quantified Self**: Health tracking, movement patterns, productivity analytics
- **🌐 Multi-Access**: Mac local, Web UI, Future mobile (Telegram)
- **🔐 Secure**: JWT authentication, OAuth2 integrations, environment-based secrets

---

## Architecture

### System Components

```
Personal AI System (This Repository)
├── UFC Context (.claude/)             # System intelligence and agent definitions
├── Integrations (integrations/)       # Service connectors and API wrappers
├── Services (services/)               # Microservices (excluded from git)
└── Orchestration (docker-compose.yml) # Master service coordination
```

### Microservices

| Service | Purpose | Repository | Port |
|---------|---------|------------|------|
| **claude-agent-server** | AI agent orchestration with UFC | [gavraq/claude-agent-server](https://github.com/gavraq/claude-agent-server) | 3002 |
| **health-service** | Apple Health + Parkrun data | [gavraq/health-service](https://github.com/gavraq/health-service) | 3001 |
| **interactive-cv-website** | Portfolio and web UI | [gavraq/interactive-cv-website](https://github.com/gavraq/interactive-cv-website) | Vercel |
| **location-service** | Owntracks geolocation | [owntracks/docker-recorder](https://github.com/owntracks/docker-recorder) | 8083 |

### Integrations

| Integration | Purpose | Type |
|-------------|---------|------|
| **health** | Apple Health + Parkrun access | Python REST wrapper |
| **location** | Owntracks movement analysis | Python REST wrapper |
| **freeagent** | Financial management (Bright Slate) | Python OAuth2 API |
| **linkedin** | Job search + content posting | LinkedIn API + WebSearch |
| **gmail-calendar** | Email + calendar management | MCP server |
| **daily-brief** | Personalized news curation | Web API integration |
| **fabric** | AI content processing patterns | REST API (233+ patterns) |
| **observability** | Multi-agent monitoring | Custom event collector |

---

## Quick Start

### Prerequisites

- **Mac**: For local development and UFC context management
- **Raspberry Pi**: For hosting containerized services
- **GitHub Account**: Access to service repositories
- **Anthropic API Key**: For Claude AI access
- **Docker**: For containerization (Pi only)

### Installation

#### 1. Clone Repository (Mac)

```bash
cd ~/projects/
git clone https://github.com/gavraq/personal-ai-system.git life
cd life
```

#### 2. Set Up Services Directory (Mac)

```bash
# Clone service repositories
mkdir -p services
cd services

git clone https://github.com/gavraq/health-service.git
git clone https://github.com/gavraq/claude-agent-server.git
git clone https://github.com/gavraq/interactive-cv-website.git

cd ..
```

#### 3. Configure Environment Variables (Mac)

```bash
# Create .env file (not committed to git)
cat > .env << 'EOF'
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-xxx

# JWT Secret (for WebSocket authentication)
JWT_SECRET=your-secure-random-string

# Service URLs (Mac local development)
HEALTH_SERVICE_URL=http://localhost:3001
LOCATION_SERVICE_URL=http://localhost:8083
EOF
```

#### 4. Deploy to Pi

```bash
# SSH to Pi
ssh pi@192.168.5.190

# Clone personal-ai-system
cd ~/docker
git clone https://github.com/gavraq/personal-ai-system.git

# Clone services
cd personal-ai-system/services
git clone https://github.com/gavraq/health-service.git
git clone https://github.com/gavraq/claude-agent-server.git
# Note: interactive-cv-website deployed on Vercel, not Pi

# Copy .env file from Mac (secure transfer)
scp ~/projects/life/.env pi@192.168.5.190:~/docker/personal-ai-system/

# Start all services
cd ~/docker/personal-ai-system
docker-compose up -d

# Verify services running
docker-compose ps
```

#### 5. Set Up Auto-Sync (Pi)

```bash
# Edit crontab
crontab -e

# Add auto-sync job (every 15 minutes)
*/15 * * * * cd ~/docker/personal-ai-system && git pull origin main >> ~/logs/personal-ai-sync.log 2>&1
```

---

## Usage

### Accessing AI Agents

#### Via Web UI (Production)

1. Navigate to: https://gavinslater.com
2. Log in with credentials
3. Chat with specialized agents:
   - "Health agent: What was my step count yesterday?"
   - "Location agent: Where did I go this week?"
   - "FreeAgent agent: Create invoice for ICBC October"

#### Via Mac Local (Development)

```bash
# Start Claude Code
cd ~/projects/life
claude-code

# Interact with agents in terminal
> What's my health summary for the past week?
```

#### Via API (Programmatic)

```python
import requests

# Get JWT token
response = requests.post('https://agent.gavinslater.com/api/auth/token',
    json={'username': 'admin', 'password': 'your-password'})
token = response.json()['token']

# Send agent request
ws_url = f"wss://agent.gavinslater.com/ws?token={token}"
# Connect to WebSocket and send messages
```

### Using Integrations

#### Health Integration

```python
from integrations.health.python_client import HealthClient

# Mac local development
client = HealthClient(base_url='http://localhost:3001')

# Or containerized (Pi)
import os
base_url = os.getenv('HEALTH_SERVICE_URL', 'http://health-service:3001')
client = HealthClient(base_url=base_url)

# Get health summary
summary = client.get_summary(days=7)
print(f"Steps: {summary['steps']}")
print(f"Heart Rate: {summary['heart_rate_avg']} bpm")
```

#### Location Integration

```python
from integrations.location.python_client import OwntracksClient

client = OwntracksClient(base_url='http://localhost:8083')

# Get recent locations
locations = client.get_locations(user='gavin-iphone', hours=24)
for loc in locations:
    print(f"{loc['timestamp']}: {loc['lat']}, {loc['lon']} - {loc['address']}")
```

#### FreeAgent Integration

```python
from integrations.freeagent.freeagent_client import FreeAgentClient

client = FreeAgentClient()

# Create invoice
invoice = client.create_invoice(
    contact_id='12345',
    project_code='ICBC',
    description='October 2025 consulting',
    amount=5000.00,
    due_days=30
)
print(f"Invoice created: {invoice['url']}")
```

---

## UFC Context System

### What is UFC?

**Universal File Context (UFC)** is a curated set of markdown files providing complete system awareness to AI agents:

- Personal identity, values, challenges
- Current goals and GTD horizons
- Active projects and initiatives
- Available tools and integrations
- Agent definitions and capabilities

### UFC Structure

```
.claude/
├── context/                    # Always-loaded context (full system awareness)
│   ├── profile/               # Personal identity and goals
│   │   ├── personal-profile.md # WHO I AM: Identity, career, values, challenges
│   │   └── goals-objectives.md # WHAT I WANT: GTD horizons, Telos, priorities
│   ├── active-projects/       # All current initiatives (8 projects)
│   │   ├── ai-coding-projects.md
│   │   ├── career-development.md
│   │   ├── cv-website-development.md
│   │   ├── daily-journal-context.md
│   │   ├── finances-context.md
│   │   ├── gtd-task-management.md
│   │   ├── health-context.md
│   │   └── location-tracking-context.md
│   └── tools/                 # Complete tools + agents portfolio
│       ├── CLAUDE.md          # Sub-agent portfolio
│       ├── fabric-integration-context.md
│       ├── freeagent-api-context.md
│       ├── gmail-mcp-context.md
│       ├── linkedin-api-context.md
│       ├── location-integration-context.md
│       ├── observability-context.md
│       └── parkrun-api-context.md
├── agents/                     # Full agent definitions (15 agents)
│   ├── personal-consultant.md
│   ├── gmail-calendar-agent.md
│   ├── freeagent-invoice-agent.md
│   ├── job-search-agent.md
│   ├── health-agent.md
│   ├── location-agent.md
│   ├── interactive-cv-website-agent.md
│   ├── knowledge-manager-agent.md
│   ├── gtd-task-manager-agent.md
│   ├── daily-journal-agent.md
│   ├── daily-brief-agent.md
│   ├── content-processor-agent.md
│   ├── weekly-review-agent.md
│   ├── project-setup-review-agent.md
│   └── horizons-reviewer-agent.md
└── commands/                   # Simple repeatable tasks
    ├── daily-brief.md
    ├── daily-note.md
    ├── daily-journal-morning.md
    ├── daily-journal-evening.md
    └── youtube-transcript.md
```

### Context Loading Protocol

**Always Load** (Full System Awareness):
- Complete `.claude/context/` directory (~2 MB)
- Profile context (core identity, goals)
- Active projects (all 8 initiatives)
- Tools context (complete portfolio)

**Conditional Load** (Detailed Implementation):
- Agent definitions (`.claude/agents/`) - Only when specific queries require it
- Command implementations (`.claude/commands/`) - On demand

**Result**: 70% context efficiency - maintains complete intelligence while optimizing token usage.

---

## Specialized Agents

### Agent Portfolio

| Agent | Purpose | Tools |
|-------|---------|-------|
| **personal-consultant** | Master orchestrator with goal alignment | Task, Read, Write, WebSearch, WebFetch |
| **gmail-calendar-agent** | Gmail + Google Calendar management | Gmail MCP (18 tools), Calendar MCP (10+ tools) |
| **freeagent-invoice-agent** | Financial operations (invoicing, reporting) | FreeAgent API, Read, Write, WebFetch |
| **job-search-agent** | LinkedIn + AI career transition | LinkedIn API, WebSearch, WebFetch |
| **health-agent** | Parkrun + quantified self tracking | Health Service API, WebFetch |
| **location-agent** | Movement patterns and geolocation analysis | Owntracks API, WebFetch |
| **interactive-cv-website-agent** | Portfolio website development | Read, Write, Edit, Bash, WebFetch |
| **knowledge-manager-agent** | Obsidian vault integration | Read, Write, Edit, Glob, Grep |
| **gtd-task-manager-agent** | GTD task management | Read, Write, Edit, Bash, Glob, Grep |
| **daily-journal-agent** | Daily planning and reflection orchestration | Read, Write, Glob, Grep, WebFetch, Bash, Task |
| **daily-brief-agent** | Personalized news curation | WebSearch, WebFetch, Read, Glob, Grep, Bash |
| **content-processor-agent** | Fabric AI pattern processing | Bash, Read, Write, WebFetch |
| **weekly-review-agent** | GTD weekly reviews | Read, Write, Edit, Glob, Grep, Task |
| **project-setup-review-agent** | GTD project definition and review | Read, Write, Edit, Glob, Grep |
| **horizons-reviewer-agent** | Goals, vision, purpose clarification | Read, Write, Edit, Glob, Grep, Task |

### Using Agents

Agents are automatically invoked based on query context:

```bash
# Health queries → health-agent
"What was my Parkrun time last Saturday?"

# Location queries → location-agent
"Show me where I traveled this week"

# Financial queries → freeagent-invoice-agent
"Create an invoice for ICBC for October consulting"

# Job search queries → job-search-agent
"Find AI engineering roles in London"
```

---

## Development

### Local Development (Mac)

```bash
# Navigate to project
cd ~/projects/life

# Update UFC context
vim .claude/context/profile/goals-objectives.md

# Commit changes
git add .
git commit -m "Update: Q4 2025 goals"
git push origin main

# Pi auto-syncs within 15 minutes
```

### Service Development

Each service has its own git repository. See service-specific README files:

- [health-service/README.md](services/health-service/README.md)
- [claude-agent-server/README.md](services/claude-agent-server/README.md)
- [interactive-cv-website/README.md](services/interactive-cv-website/README.md)

### Integration Development

Integrations are part of this repository. Add new integrations to `integrations/` directory:

```bash
# Create new integration
mkdir -p integrations/my-integration
cd integrations/my-integration

# Create standard files
touch CLAUDE.md README.md
mkdir -p python-client docs

# Document integration
vim CLAUDE.md  # Technical implementation
vim README.md  # User documentation
```

---

## System Monitoring

### Health Checks

```bash
# Check all services
docker-compose ps

# Check specific service
docker-compose logs -f claude-agent-server

# Health endpoints
curl http://localhost:3001/health  # Health service
curl http://localhost:3002/health  # Agent server
```

### Service Connectivity

```bash
# Test internal Docker network connectivity
docker exec claude-agent-server curl http://health-service:3001/health
docker exec claude-agent-server curl http://owntracks-api:8083/api/0/version

# Expected: JSON responses from each service
```

### UFC Context Verification

```bash
# Check UFC context is mounted
docker exec claude-agent-server ls -la /ufc/

# Check agent logs for context loading
docker logs claude-agent-server | grep "UFC context loaded"
# Expected: "UFC context loaded: 8 projects, 6 tools, 10 agents"
```

---

## Deployment

### Production Deployment (Pi)

```bash
# SSH to Pi
ssh pi@192.168.5.190

# Navigate to system directory
cd ~/docker/personal-ai-system

# Pull latest changes
git pull origin main

# Rebuild and restart services
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Verify deployment
docker-compose ps
docker-compose logs -f
```

### Web UI Deployment (Vercel)

```bash
# From interactive-cv-website directory
cd services/interactive-cv-website

# Deploy to Vercel
vercel --prod

# Set environment variables in Vercel dashboard:
# - ADMIN_USERNAME
# - ADMIN_PASSWORD_HASH (base64 encoded)
# - AGENT_WS_URL=wss://agent.gavinslater.com/ws
# - NEXTAUTH_URL=https://gavinslater.com
# - NEXTAUTH_SECRET
```

---

## Backup and Recovery

### Database Backups

```bash
# Health database (1.7GB)
rsync -avz pi@192.168.5.190:~/docker/personal-ai-system/services/health-service/data/health.db \
    ~/backups/health-db/health-$(date +%Y%m%d).db

# Owntracks location data
rsync -avz pi@192.168.5.190:~/docker/personal-ai-system/services/location-service/owntracks/store/ \
    ~/backups/owntracks/
```

### UFC Context Backup

UFC context is automatically backed up via git:

```bash
# Mac: Push changes
cd ~/projects/life
git push origin main

# Pi: Auto-syncs every 15 minutes via cron
```

### Service Configuration Backup

```bash
# Backup all .env files
scp pi@192.168.5.190:~/docker/personal-ai-system/.env ~/backups/env/pi-env-$(date +%Y%m%d)
scp pi@192.168.5.190:~/docker/personal-ai-system/services/*/.env ~/backups/env/
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs [service-name]

# Check dependencies
docker-compose ps

# Rebuild service
docker-compose build --no-cache [service-name]
docker-compose up -d [service-name]
```

### Agent Not Responding

```bash
# Check agent server logs
docker logs claude-agent-server

# Verify UFC context loaded
docker exec claude-agent-server ls -la /ufc/

# Check service connectivity
docker exec claude-agent-server curl http://health-service:3001/health
```

### UFC Context Not Loading

```bash
# Verify volume mount
docker inspect claude-agent-server | grep -A 10 Mounts

# Check context files exist
ls -la ~/docker/personal-ai-system/.claude/context/

# Restart agent server
docker-compose restart claude-agent-server
```

---

## Security

### Secrets Management

- **Never commit**: `.env`, `.gauth.json`, `.accounts.json`, credentials files
- **Git-ignored**: All sensitive files excluded via `.gitignore`
- **Environment variables**: Use `.env` for local, Vercel dashboard for production
- **OAuth2 tokens**: Stored securely, never in code or git

### Authentication

- **Web UI**: NextAuth with bcrypt password hashing
- **WebSocket**: JWT token authentication
- **APIs**: OAuth2 for third-party services (FreeAgent, LinkedIn, Gmail)

### Network Security

- **Pi**: Behind home router NAT, only necessary ports exposed
- **SSL**: Let's Encrypt certificates via NGINX reverse proxy
- **Docker**: Services on isolated internal network, only external via NGINX

---

## Contributing

This is a personal project, but contributions to improve architecture or add features are welcome:

1. Fork repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m "Add: my feature"`
4. Push to branch: `git push origin feature/my-feature`
5. Create Pull Request

---

## Roadmap

### Q4 2025
- [ ] Complete migration to microservices architecture ✅ (October 2025)
- [ ] Implement master docker-compose orchestration
- [ ] Add comprehensive monitoring and alerting
- [ ] Telegram bot for mobile access

### Q1 2026
- [ ] Enhanced location intelligence (pattern detection)
- [ ] FreeAgent invoice automation improvements
- [ ] LinkedIn job search automation
- [ ] Personal knowledge graph visualization

### Q2 2026
- [ ] Voice interface (Whisper API)
- [ ] Strava + Fitbit health integrations
- [ ] Advanced GTD analytics dashboard
- [ ] AI-powered goal tracking and recommendations

---

## License

Private repository - All rights reserved.

**Owner**: Gavin Slater
**Contact**: Via GitHub issues

---

## Acknowledgments

- **Anthropic Claude**: For AI capabilities and Claude Code SDK
- **Owntracks**: For open-source location tracking
- **FreeAgent**: For accounting API
- **Parkrun**: For health data access

---

**Version**: 1.1
**Last Updated**: November 22, 2025
**Status**: Production Ready
**Repository**: https://github.com/gavraq/personal-ai-system
