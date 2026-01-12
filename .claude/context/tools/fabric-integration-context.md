# Fabric AI Integration - UFC Context

## Overview

**Fabric** is an open-source AI augmentation framework providing 233+ battle-tested patterns for content processing, integrated into Gavin's Personal AI Infrastructure as a REST API service.

**Status**: ✅ Deployed and Operational
**Deployment**: Raspberry Pi (192.168.5.190) via Docker
**Access**:
- Internal (Docker): `http://fabric-api:8080`
- Pi Local: `http://192.168.5.190:8085`
- External: `https://fabric.gavinslater.co.uk` ✅ SSL enabled

## Purpose & Value

### Core Capabilities
- **Content Processing**: YouTube→Obsidian, articles→summaries, podcasts→insights
- **Pattern Library**: 233+ community-proven prompts (extraction, analysis, summarization, writing)
- **Custom Workflows**: GTD-aligned daily/weekly reviews, risk-agents.com content curation
- **Multi-Provider**: Anthropic, OpenAI, Google (fallback resilience)

### Integration Value
1. **Time Savings**: 50% reduction in content processing time (YouTube 20min→2min)
2. **Quality Improvement**: Standardized, consistent content extraction vs ad-hoc prompts
3. **Knowledge Enhancement**: Better structured Obsidian notes with actionable insights
4. **Career Development**: Demonstrable AI integration expertise for portfolio

## Architecture

```
Content Request
    ↓
Personal Consultant (YOU)
    ↓
Content Processor Agent (Task delegation)
    ↓
Fabric API (pattern execution)
    ↓
Structured Output (markdown)
    ↓
Knowledge Manager → Obsidian
```

## When to Use Fabric

### DO Use Fabric For:
- ✅ YouTube video/podcast transcript processing
- ✅ Article summarization and wisdom extraction
- ✅ Content quality scoring (Daily Brief)
- ✅ Writing improvement (CV, cover letters, blog posts)
- ✅ Daily reflections (GTD-aligned pattern)
- ✅ Weekly reviews (strategic insights pattern)
- ✅ AI safety content curation (risk-agents.com)

### DON'T Use Fabric For:
- ❌ Simple text transformations (use native capabilities)
- ❌ Real-time conversational tasks (use direct LLM)
- ❌ Integration-specific operations (Gmail, FreeAgent, LinkedIn)
- ❌ Quick one-off questions not needing specialized patterns

## Agent Coordination

### Primary Agent: Content Processor
**File**: `/.claude/agents/content-processor-agent.md`

**Delegation Pattern**:
```markdown
Task → content-processor-agent → "Process YouTube video: [URL]"
Task → content-processor-agent → "Summarize article: [URL] for Obsidian"
Task → content-processor-agent → "Generate daily reflection from today's data"
```

**NEVER**:
- Call Fabric API directly via Bash/curl (breaks abstraction)
- Reimplement patterns manually (use existing community patterns)
- Bypass Content Processor for Fabric tasks

### Enhanced Agents

| Agent | Enhancement | Integration Point |
|-------|-------------|-------------------|
| Knowledge Manager | Fabric preprocessing | Before Obsidian storage |
| Daily Brief | Content quality scoring | Article filtering via `rate_content` |
| Job Search | CV/writing optimization | `improve_writing` pattern |
| Daily Journal | Reflection processing | `daily-reflection` custom pattern |
| Weekly Review | Strategic insights | `weekly-review` custom pattern |

## Available Patterns

### Community Patterns (233+)

**Content Extraction** (Most Used):
- `extract_wisdom` - Insights, quotes, ideas from videos/podcasts
- `extract_article_wisdom` - Article-specific extraction
- `extract_recommendations` - Action items
- `extract_ideas` - Novel concepts

**Analysis**:
- `analyze_claims` - Fact-checking, claim validation
- `rate_content` - Quality scoring (1-10)
- `analyze_prose` - Writing style analysis

**Summarization**:
- `summarize` - General summarization
- `summarize_paper` - Academic papers
- `create_summary` - Structured summaries

**Writing**:
- `improve_writing` - Enhancement for CV, blog, emails
- `create_essay_plan` - Outline generation
- `write_essay` - Full content generation

### Custom Patterns (Gavin-Specific)

**daily-reflection**:
- **Input**: Location, health, calendar, tasks, notes
- **Output**: GTD-aligned productivity assessment, goal alignment, insights, tomorrow's priorities
- **Use Case**: Automated daily review for Obsidian daily notes

**weekly-review**:
- **Input**: Week's daily reflections + aggregated metrics
- **Output**: Strategic review across GTD horizons, patterns, priorities
- **Use Case**: David Allen 12-step weekly review automation

**risk-agents-content**:
- **Input**: AI safety/risk article, paper, or video content
- **Output**: Relevance score, key insights, blog post potential, title suggestions
- **Use Case**: Content curation for risk-agents.com blog

## API Access

### Endpoints

**Base URLs**:
- Internal (Docker Network): `http://fabric-api:8080` (use from other containers)
- Raspberry Pi Local: `http://192.168.5.190:8085` (host machine access)
- External: `https://fabric.gavinslater.co.uk` (public access - SSL enabled)

**Port Mapping**: Container port 8080 → Host port 8085

**Authentication**: `X-API-Key: ${FABRIC_API_KEY}` header required

**Key Endpoints**:
- `GET /patterns/names` - List 233+ patterns
- `POST /api/chat` - Execute pattern (Ollama-compatible)
- `POST /youtube/transcript` - Extract YouTube transcript
- `GET /patterns/:name` - Pattern details

### Example Usage

```bash
# Execute pattern
curl -X POST http://fabric-api:8080/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${FABRIC_API_KEY}" \
  -d '{
    "model": "extract_wisdom",
    "stream": false,
    "messages": [{"role": "user", "content": "content here"}]
  }'
```

## Workflow Examples

### YouTube → Obsidian
1. User: "Save this AI safety talk: [YouTube URL]"
2. YOU → Content Processor Agent
3. Content Processor → Fabric: extract transcript + extract_wisdom
4. Content Processor → Knowledge Manager: Store formatted note
5. Result: `Notes/Videos/[title].md` with insights

### Daily Brief Quality Scoring
1. Daily Brief: Fetch articles
2. Daily Brief → Content Processor: Rate each article
3. Content Processor → Fabric: `rate_content` pattern
4. Content Processor → Daily Brief: Scores + justifications
5. Result: Top-scored articles in briefing

### CV Optimization
1. User: "Optimize CV summary for AI Engineer role"
2. YOU → Job Search Agent
3. Job Search → Content Processor: improve_writing + job context
4. Content Processor → Fabric: Execute pattern
5. Result: Enhanced CV section shown as diff

## Deployment

### Infrastructure
- **Location**: Raspberry Pi (192.168.5.190)
- **Docker Image**: `kayvan/fabric:latest` (ARM64 compatible)
- **Network**: `personal-ai` (dynamic IP, accessible via hostname)
- **Port**: 8085 (host) → 8080 (container)
- **Reverse Proxy**: NGINX at `fabric.gavinslater.co.uk`
- **Resources**: 512MB RAM limit, auto-restart enabled

### Configuration
- **Default Vendor**: Anthropic
- **Default Model**: claude-sonnet-4-5-20250929
- **Pattern Updates**: Auto-sync from official repository
- **Session Cleanup**: 30-day retention policy

### Health Monitoring
```bash
# Check service health
curl http://fabric-api:8080/patterns/names

# Container status
docker ps --filter "name=fabric-api"

# Resource usage
docker stats fabric-api
```

## File Locations

### Integration Files
```
/integrations/fabric/
├── docker-compose.yml       # Service definition
├── .env                     # API keys (gitignored)
├── README.md                # Setup and usage guide
├── CLAUDE.md                # AI assistant integration guide
├── config/                  # Fabric configuration (auto-generated)
├── custom-patterns/         # Gavin-specific patterns
│   ├── daily-reflection/
│   ├── weekly-review/
│   └── risk-agents-content/
└── logs/                    # Service logs
```

### Agent & Context Files
```
/.claude/agents/content-processor-agent.md    # Agent definition
/.claude/context/tools/fabric-integration-context.md  # This file
```

## Integration Guidelines

### Tools-First Protocol
1. **Content processing tasks** → Always delegate to Content Processor Agent
2. **Pattern execution** → Content Processor handles API calls
3. **Knowledge storage** → Delegate to Knowledge Manager (not direct Write)
4. **Task creation** → Extract action items → GTD Task Manager

### Error Handling
- **API unavailable**: Fall back to direct LLM with similar prompt
- **Pattern not found**: List available patterns, suggest closest match
- **Authentication failure**: Check FABRIC_API_KEY, notify user
- **Timeout**: Retry with exponential backoff (max 3 attempts)

### Quality Standards
- ✅ Always format output for Obsidian (frontmatter, markdown, tags)
- ✅ Preserve source attribution (URLs, authors, dates)
- ✅ Add context via metadata (pattern used, processing date)
- ✅ Create logical file paths (by type: Videos/, Articles/, AI Safety/)
- ✅ Link to related notes when applicable

## Success Metrics

### Technical
- API response time: < 2s (95th percentile)
- Pattern execution success: > 98%
- Service uptime: > 99.5%
- Memory usage: < 512MB steady

### Usage
- Patterns executed per week: Track volume
- Most used patterns: Optimize workflows
- Content processed: YouTube, articles, documents
- Custom pattern adoption: Evidence of value

### Value
- Time saved: Target 50% reduction
- Notes created: Volume via Fabric
- Blog frequency: 2x increase (risk-agents.com)
- Quality improvement: User feedback

## Quick Reference

### Common Tasks

**Process YouTube Video**:
```markdown
Task → content-processor-agent → "Process YouTube: [URL] using extract_wisdom"
```

**Summarize Article**:
```markdown
Task → content-processor-agent → "Summarize article: [URL] for Obsidian storage"
```

**Daily Reflection**:
```markdown
Task → content-processor-agent → "Generate daily reflection for today"
```

**Rate Article Quality**:
```markdown
Task → content-processor-agent → "Rate this article: [URL]"
```

**Optimize Writing**:
```markdown
Task → content-processor-agent → "Improve this text: [content]"
```

### Pattern Selection Logic

| Content Type | Recommended Pattern | Output |
|--------------|-------------------|--------|
| YouTube video | `extract_wisdom` | Insights, quotes, ideas |
| Web article | `extract_article_wisdom` | Key insights |
| News article | `rate_content` or `analyze_claims` | Score or fact-check |
| Writing draft | `improve_writing` | Enhanced version |
| Long document | `summarize` | Concise summary |
| Daily data | `daily-reflection` (custom) | GTD-aligned review |
| Week data | `weekly-review` (custom) | Strategic insights |
| AI safety content | `risk-agents-content` (custom) | Blog potential |

## Resources

### Documentation
- Setup Guide: `/integrations/fabric/README.md`
- AI Assistant Guide: `/integrations/fabric/CLAUDE.md`
- Agent Definition: `/.claude/agents/content-processor-agent.md`

### External Links
- Fabric Repository: https://github.com/danielmiessler/fabric
- Pattern Library: https://github.com/danielmiessler/fabric/tree/main/patterns
- Docker Images: https://hub.docker.com/r/kayvan/fabric

### Support
- Check service health: `curl http://fabric-api:8080/patterns/names`
- View logs: `docker-compose -f /integrations/fabric/docker-compose.yml logs`
- Pattern list: `curl http://fabric-api:8080/patterns/names | jq`

---

**Key Takeaway**: Fabric adds powerful, standardized content processing to Gavin's Personal AI Infrastructure. Always delegate to Content Processor Agent, leverage community patterns, and maintain tools-first discipline for maximum value.
