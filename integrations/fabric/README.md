# Fabric AI Integration

AI augmentation framework providing 235+ battle-tested patterns for content processing, analysis, and transformation.

## Overview

[Fabric](https://github.com/danielmiessler/fabric) is an open-source framework for augmenting human capabilities through AI. This integration deploys a pattern library service at `fabric.gavinslater.co.uk` with a web-based pattern browser and REST API for programmatic access. Patterns are executed locally using Claude Code with your Max subscription.

### Key Capabilities

- **235+ AI Patterns**: Crowdsourced prompts for summarization, extraction, analysis, writing
- **Web Pattern Browser**: Explore, search, and view patterns at fabric.gavinslater.co.uk
- **REST API**: Pattern retrieval endpoints for programmatic access
- **Local LLM Execution**: Patterns executed via Claude Code using Max subscription
- **Custom Patterns**: Add Gavin-specific workflows
- **GitHub Sync**: Keep patterns updated from official repository

### Architecture

```
┌─────────────────────────────────────────────────┐
│  Pattern Library Service (Raspberry Pi)          │
│  fabric.gavinslater.co.uk                        │
│  ┌─────────────┐  ┌──────────────────┐          │
│  │ Web UI      │  │ REST API         │          │
│  │ Browse/     │  │ GET /patterns    │          │
│  │ Search      │  │ GET /patterns/{n}│          │
│  └─────────────┘  └──────────────────┘          │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  Local Execution (Claude Code + Max Plan)       │
│  /fabric [pattern] [input]                      │
│  Pattern as system prompt → LLM execution       │
└─────────────────────────────────────────────────┘
                      ↓
              Structured Output
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Access to `personal-ai` Docker network
- Anthropic API key (required)
- Raspberry Pi SSH access (for deployment)

### Setup Steps

1. **Clone and Configure**
   ```bash
   cd /Users/gavinslater/projects/life/integrations/fabric

   # Copy environment template
   cp .env.example .env

   # Edit .env with your API keys
   nano .env
   ```

2. **Generate Secure API Key**
   ```bash
   # Generate a secure Fabric API key
   openssl rand -hex 32

   # Add to .env as FABRIC_API_KEY
   ```

3. **Initial Setup (One-time)**
   ```bash
   # Run Fabric setup to download patterns
   docker-compose run --rm fabric-api --setup

   # This will:
   # - Download 233+ community patterns
   # - Create configuration structure
   # - Test AI provider connection
   ```

4. **Start Services**
   ```bash
   # Local testing
   docker-compose up -d

   # View logs
   docker-compose logs -f fabric-api

   # Check health
   curl http://localhost:8085/patterns/names
   ```

5. **Deploy to Raspberry Pi**
   ```bash
   # Use deployment script
   ./scripts/deploy-to-pi.sh

   # Or manually:
   sshpass -p 'raspberry' ssh pi@192.168.5.190 << 'EOF'
     cd ~/docker/fabric
     git pull
     docker-compose up -d
   EOF
   ```

## Usage

### Web Pattern Browser

Visit **https://fabric.gavinslater.co.uk** to:
- Browse all 235+ patterns with search and category filtering
- View pattern details and full system prompts
- Copy patterns to clipboard for use

**Features:**
- Real-time search filtering
- Category filters: Extract, Analyze, Create, Summarize, Improve, Write
- Pattern previews with purpose descriptions
- No authentication required for browsing

### Claude Code Slash Command

The `/fabric` slash command executes patterns locally using your Max subscription:

```bash
# Basic usage
/fabric [pattern-name] [input text]

# Examples
/fabric summarize [paste article text]
/fabric extract_wisdom [paste transcript]
/fabric improve_writing [paste draft]
```

The command:
1. Fetches the pattern from fabric.gavinslater.co.uk
2. Uses the pattern content as the system prompt
3. Executes locally with Claude Code (Max subscription)
4. Returns structured output

### REST API Endpoints

**Base URL (Internal)**: `http://fabric-api:8080`
**Base URL (Local)**: `http://192.168.5.190:8085`
**Base URL (External)**: `https://fabric.gavinslater.co.uk`

#### Web UI (No Auth Required)
```bash
# Pattern browser
GET /

# View specific pattern
GET /view/{pattern_name}

# Health check
GET /health
```

#### API Endpoints (Require X-API-Key header)
```bash
# List all patterns
curl -H "X-API-Key: ${FABRIC_API_KEY}" \
  https://fabric.gavinslater.co.uk/patterns

# Get pattern content
curl -H "X-API-Key: ${FABRIC_API_KEY}" \
  https://fabric.gavinslater.co.uk/patterns/extract_wisdom

# Sync patterns from GitHub
curl -X POST -H "X-API-Key: ${FABRIC_API_KEY}" \
  https://fabric.gavinslater.co.uk/sync

# Extract YouTube transcript
curl -X POST -H "X-API-Key: ${FABRIC_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://youtube.com/watch?v=VIDEO_ID"}' \
  https://fabric.gavinslater.co.uk/youtube/transcript
```

### Popular Patterns

| Pattern | Purpose | Use Case |
|---------|---------|----------|
| `extract_wisdom` | Extract insights, quotes, ideas | YouTube videos, podcasts |
| `summarize` | General summarization | Articles, documents |
| `analyze_claims` | Fact-check and claim analysis | News articles, research |
| `improve_writing` | Writing enhancement | CV, cover letters, blog posts |
| `rate_content` | Content quality scoring | Daily brief filtering |
| `extract_article_wisdom` | Article-specific extraction | Web content processing |
| `create_summary` | Structured summary | Meeting notes, reports |

### Custom Patterns

Gavin-specific patterns in `custom-patterns/`:

- **daily-reflection**: GTD-aligned daily review processing
- **weekly-review**: Strategic weekly insights generation
- **risk-agents-content**: Content curation for risk-agents.com blog

## Agent Integration

### Content Processor Agent

Primary agent for Fabric pattern orchestration:

```bash
# Via Claude Code
Task → content-processor-agent → "Process YouTube video: [URL]"
```

The agent handles:
- Pattern selection based on content type
- API authentication and error handling
- Output formatting for Obsidian
- Integration with Knowledge Manager

### Knowledge Manager Enhancement

Process content before storage:

```python
# Workflow example
1. User: "Save this YouTube video to Obsidian"
2. Content Processor: Extract wisdom via Fabric
3. Knowledge Manager: Store formatted note
4. Result: Structured note in vault
```

### Daily Brief Integration

Quality scoring for articles:

```python
# Workflow example
1. Daily Brief: Fetch candidate articles
2. Content Processor: Rate with Fabric
3. Daily Brief: Include top-scored articles
4. Result: Higher quality briefings
```

## Configuration

### Environment Variables

See `.env.example` for complete list. Key variables:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...
FABRIC_API_KEY=your-secure-key

# Optional
OPENAI_API_KEY=sk-...
DEFAULT_VENDOR=Anthropic
DEFAULT_MODEL=claude-sonnet-4-5-20250929
```

### Docker Network

Fabric joins the existing `personal-ai` network:

```yaml
networks:
  - personal-ai
```

**Note**: Static IP assignment has been removed to avoid conflicts with `docker-compose run` commands. The service is accessible via hostname `fabric-api` on the personal-ai network.

Verify network exists:
```bash
docker network inspect personal-ai
```

### Resource Limits

Recommended for Raspberry Pi:

```yaml
services:
  fabric-api:
    deploy:
      resources:
        limits:
          memory: 512M
```

## Monitoring

### Health Checks

```bash
# Docker health status
docker ps --filter "name=fabric-api"

# API health endpoint
curl http://fabric-api:8080/patterns/names

# Detailed status
docker-compose ps
docker-compose logs fabric-api --tail=50
```

### Logs

```bash
# Real-time logs
docker-compose logs -f fabric-api

# Log files
tail -f logs/fabric.log

# Docker logs
docker logs fabric-api --since 1h
```

### Resource Usage

```bash
# Container stats
docker stats fabric-api

# Disk usage
du -sh config/ custom-patterns/ logs/

# Pattern library size
du -sh config/patterns/
```

## Maintenance

### Pattern Updates

Update patterns from the official Fabric GitHub repository:

```bash
# Recommended: Use the update script (from your Mac)
./scripts/update-patterns.sh

# The script will:
# 1. Clone latest fabric repo to Pi
# 2. Sync patterns to config/patterns/
# 3. Restart the container
# 4. Verify the update
```

**Manual update (on Raspberry Pi):**
```bash
# Clone fabric repo
cd /tmp && sudo git clone --depth=1 https://github.com/danielmiessler/fabric.git fabric_update

# Sync patterns
sudo rsync -av --delete /tmp/fabric_update/data/patterns/ ~/docker/fabric/config/patterns/

# Restart service
cd ~/docker/fabric && docker-compose restart fabric-api

# Cleanup
sudo rm -rf /tmp/fabric_update
```

**Note:** The `/sync` API endpoint is not functional because patterns are volume-mounted from the host rather than cloned inside the container.

### Session Cleanup

Sessions accumulate over time. Clean up periodically:

```bash
# Remove sessions older than 30 days
find config/sessions/ -type f -mtime +30 -delete

# Clear all sessions
rm -rf config/sessions/*
```

### Backup Configuration

```bash
# Backup custom patterns and config
tar -czf fabric-backup-$(date +%Y%m%d).tar.gz \
  custom-patterns/ \
  config/.env \
  config/config.json

# Restore
tar -xzf fabric-backup-YYYYMMDD.tar.gz
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs fabric-api

# Common issues:
# 1. Network doesn't exist
docker network create personal-ai

# 2. Port conflict
lsof -i :8085

# 3. Missing .env file
cp .env.example .env && nano .env
```

### API Key Authentication Failing

```bash
# Verify API key is set
docker-compose exec fabric-api env | grep FABRIC_API_KEY

# Test with explicit key
curl -H "X-API-Key: your-key" http://fabric-api:8080/patterns/names
```

### Pattern Execution Errors

```bash
# Check AI provider keys
docker-compose exec fabric-api env | grep API_KEY

# Test Anthropic connection
curl -H "x-api-key: $ANTHROPIC_API_KEY" \
  https://api.anthropic.com/v1/messages \
  -d '{"model":"claude-3-haiku-20240307","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
```

### ARM64 Compatibility Issues

```bash
# Verify image architecture
docker image inspect kayvan/fabric:latest | grep Architecture

# Force ARM64 pull
docker pull --platform linux/arm64 kayvan/fabric:latest
```

## Development

### Creating Custom Patterns

1. Create pattern directory:
   ```bash
   mkdir -p custom-patterns/my-pattern
   ```

2. Write system prompt:
   ```bash
   nano custom-patterns/my-pattern/system.md
   ```

3. Use pattern structure:
   ```markdown
   # IDENTITY and PURPOSE
   You are a...

   # INPUT
   The input will contain...

   # OUTPUT
   Extract and organize...

   # OUTPUT FORMAT
   Use markdown...
   ```

4. Test pattern:
   ```bash
   curl -X POST http://fabric-api:8080/api/chat \
     -H "Content-Type: application/json" \
     -d '{"model": "my-pattern", "messages": [...]}'
   ```

### Testing

```bash
# Test with sample content
echo "Test content" | docker-compose exec -T fabric-api fabric -p summarize

# Test API endpoint
./scripts/test-fabric-api.sh

# Test agent integration
Task → content-processor-agent → "Test Fabric integration"
```

## External Resources

- [Fabric GitHub Repository](https://github.com/danielmiessler/fabric)
- [Official Documentation](https://github.com/danielmiessler/fabric/tree/main/docs)
- [Pattern Library](https://github.com/danielmiessler/fabric/tree/main/patterns)
- [Docker Hub Images](https://hub.docker.com/r/kayvan/fabric)

## Integration Points

| Component | Integration Type | Status |
|-----------|------------------|--------|
| Content Processor Agent | Primary orchestrator | ✅ Planned |
| Knowledge Manager | Pattern preprocessing | ✅ Planned |
| Daily Brief | Content quality scoring | ✅ Planned |
| Job Search | CV/writing optimization | ✅ Planned |
| Health Agent | Trend narrative generation | 🔄 Future |
| Weekly Review | Insight extraction | 🔄 Future |

## Performance

### Expected Metrics

- API response time: < 2s (95th percentile)
- Pattern execution success rate: > 98%
- Service uptime: > 99.5%
- Memory usage: < 512MB steady state

### Optimization Tips

1. Use streaming for long content
2. Cache frequently used patterns
3. Implement request rate limiting
4. Monitor AI provider quota usage
5. Clean up old sessions regularly

## Security

### Best Practices

- ✅ API key authentication enabled
- ✅ Environment variables not committed
- ✅ NGINX reverse proxy with SSL
- ✅ Docker network isolation
- ✅ Regular security updates
- ⚠️ Consider: Rate limiting at NGINX level
- ⚠️ Consider: API key rotation policy

### Access Control

- Internal: Any container on `personal-ai` network
- External: HTTPS via fabric.gavinslater.co.uk
- Authentication: X-API-Key header required

## License

Fabric is licensed under MIT. See [upstream repository](https://github.com/danielmiessler/fabric) for details.

## Support

For issues with this integration:
- Check troubleshooting section above
- Review logs: `docker-compose logs fabric-api`
- Test API connectivity and authentication
- Verify Raspberry Pi resource availability

For Fabric framework issues:
- [Official GitHub Issues](https://github.com/danielmiessler/fabric/issues)
- [Discord Community](https://discord.gg/fabric)
