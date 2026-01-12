# Fabric Integration - AI Assistant Guide

This document provides context for AI assistants (Claude Code) working with Gavin's Fabric integration.

## Integration Purpose

Fabric provides 233+ battle-tested AI patterns for content processing, enabling Gavin's Personal AI Infrastructure to:

1. **Process Content Efficiently**: YouTube videos, articles, podcasts → structured notes
2. **Enhance Agent Capabilities**: Add pattern-based processing to existing agents
3. **Standardize AI Interactions**: Use community-proven prompts vs ad-hoc approaches
4. **Scale Content Workflows**: Automated extraction, summarization, analysis

## Architecture Overview

### Service Deployment

```
Raspberry Pi (192.168.5.190)
└── Docker Container: fabric-api
    ├── Image: fabric-proxy:latest (custom build)
    ├── Port: 8085 (host) → 8080 (container)
    ├── Network: personal-ai
    ├── External: fabric.gavinslater.co.uk (NGINX proxy)
    ├── Web UI: Pattern browser at /
    └── API: Pattern retrieval (X-API-Key required)
```

### Integration Flow

```
Option 1: Web Browser
    fabric.gavinslater.co.uk → Browse/Search → View Pattern

Option 2: Slash Command (Recommended)
    /fabric [pattern] [input]
        ↓
    Fetch pattern from API
        ↓
    Execute locally with Claude Code (Max subscription)
        ↓
    Structured Output

Option 3: Programmatic API
    GET /patterns/{name} → Pattern content → Local execution
```

## Agent Coordination

### When to Use Fabric

**DO use Fabric for:**
- YouTube video/podcast processing
- Article summarization and wisdom extraction
- Content quality scoring (Daily Brief)
- Writing improvement (CV, cover letters, blog posts)
- Complex content analysis requiring specialized prompts
- Extracting structured data from unstructured text

**DON'T use Fabric for:**
- Simple text transformations (use native capabilities)
- Real-time conversational tasks
- Tasks requiring live context (use direct LLM calls)
- Integration-specific logic (Gmail, FreeAgent, etc.)

### Delegation Pattern

**Primary Agent**: Content Processor Agent (`content-processor-agent`)

Use the Task tool to delegate:

```markdown
Task → content-processor-agent → "Process YouTube video: [URL] using extract_wisdom pattern"
Task → content-processor-agent → "Summarize article: [URL] for Obsidian storage"
Task → content-processor-agent → "Improve CV section: [text] targeting AI roles"
```

**DO NOT**:
- Call Fabric API directly via Bash/curl (breaks abstraction)
- Reimplement pattern logic manually (use existing patterns)
- Bypass Content Processor for Fabric tasks (maintain clean boundaries)

## Available Patterns

### Content Extraction (Most Used)

| Pattern | Input | Output | Use Case |
|---------|-------|--------|----------|
| `extract_wisdom` | Video/podcast transcript | Insights, quotes, ideas | YouTube → Obsidian |
| `extract_article_wisdom` | Article text/URL | Key insights, actionable items | Web content processing |
| `extract_recommendations` | Analysis/report | Action items | Strategic planning |
| `extract_ideas` | Brainstorm/discussion | Novel concepts | Idea capture |

### Analysis

| Pattern | Input | Output | Use Case |
|---------|-------|--------|----------|
| `analyze_claims` | Article/statement | Fact-check, claim validation | News verification |
| `analyze_prose` | Writing sample | Style analysis | Writing improvement |
| `rate_content` | Article/content | Quality score (1-10) | Daily Brief filtering |

### Summarization

| Pattern | Input | Output | Use Case |
|---------|-------|--------|----------|
| `summarize` | Long text | Concise summary | General summarization |
| `summarize_paper` | Academic paper | Structured summary | Research processing |
| `create_summary` | Content | Formatted summary | Report generation |

### Writing Enhancement

| Pattern | Input | Output | Use Case |
|---------|-------|--------|----------|
| `improve_writing` | Draft text | Enhanced version | CV, cover letters |
| `create_essay_plan` | Topic/outline | Essay structure | Blog post planning |
| `write_essay` | Plan/topic | Full essay | Content generation |

### Custom Patterns (Gavin-Specific)

| Pattern | Input | Output | Use Case |
|---------|-------|--------|----------|
| `daily-reflection` | Daily data bundle | GTD-aligned insights | Daily journal |
| `weekly-review` | Week data bundle | Strategic review | Weekly planning |
| `risk-agents-content` | AI safety content | Blog curation analysis | risk-agents.com |

## API Integration

### Endpoints

**Base URLs:**
- Internal (Docker Network): `http://fabric-api:8080`
- Raspberry Pi Local: `http://192.168.5.190:8085`
- External: `https://fabric.gavinslater.co.uk`

**Web UI Endpoints (No Auth):**
- `GET /` - Pattern browser with search
- `GET /view/{pattern_name}` - Pattern detail view
- `GET /health` - Service health check

**API Endpoints (Require X-API-Key):**
- `GET /patterns` - List all pattern names
- `GET /patterns/{name}` - Get pattern content
- `POST /sync` - Sync patterns from GitHub
- `POST /youtube/transcript` - Extract YouTube transcript

### Authentication

API endpoints require API key header:

```bash
-H "X-API-Key: ${FABRIC_API_KEY}"
```

Web UI endpoints (/, /view/*, /health) are public - no auth required.

API key stored in:
- Docker: Environment variable in container
- Local: `.env` file in `/integrations/fabric/`
- Slash command: Hardcoded in `/.claude/commands/fabric.md`

### Example API Calls

```bash
# List patterns
curl -H "X-API-Key: ${FABRIC_API_KEY}" \
  https://fabric.gavinslater.co.uk/patterns

# Get pattern content
curl -H "X-API-Key: ${FABRIC_API_KEY}" \
  https://fabric.gavinslater.co.uk/patterns/extract_wisdom

# Sync from GitHub
curl -X POST -H "X-API-Key: ${FABRIC_API_KEY}" \
  https://fabric.gavinslater.co.uk/sync
```

### Slash Command Usage (Recommended)

```bash
# In Claude Code
/fabric extract_wisdom [paste transcript here]
/fabric summarize [paste article here]
/fabric improve_writing [paste draft here]
```

The slash command handles API authentication automatically.

## Integration with Existing Agents

### Content Processor Agent (New)

**File**: `.claude/agents/content-processor-agent.md`

**Responsibilities:**
- Pattern selection based on content type
- Fabric API orchestration
- Output formatting for downstream agents
- Error handling and retries

**Usage:**
```
Task → content-processor-agent → "Process [CONTENT] with [PATTERN]"
```

### Knowledge Manager Agent (Enhanced)

**Integration Point**: Preprocessing before Obsidian storage

**Workflow:**
```
1. User: "Save YouTube video to Obsidian"
2. YOU → Content Processor: Extract wisdom
3. Content Processor → Fabric: execute pattern
4. Fabric → Content Processor: structured output
5. Content Processor → Knowledge Manager: formatted note
6. Knowledge Manager: Store in vault
```

### Daily Brief Agent (Enhanced)

**Integration Point**: Content quality scoring

**Workflow:**
```
1. Daily Brief: Fetch candidate articles (WebSearch)
2. Daily Brief → Content Processor: Rate each article
3. Content Processor → Fabric: rate_content pattern
4. Fabric → Content Processor: scores
5. Daily Brief: Filter and present top articles
```

### Job Search Agent (Enhanced)

**Integration Point**: CV and cover letter optimization

**Workflow:**
```
1. User: "Optimize my CV summary"
2. Job Search → Content Processor: improve_writing
3. Content Processor → Fabric: execute with job context
4. Fabric → Content Processor: improved text
5. Job Search: Update CV template
```

## Custom Pattern Development

### Pattern Structure

All patterns are markdown files in `custom-patterns/[pattern-name]/system.md`:

```markdown
# IDENTITY and PURPOSE
You are a [role] that helps [purpose].

# INPUT
The input will contain:
- [item 1]
- [item 2]

# OUTPUT
Extract and organize:

## SECTION 1
- [requirement]

## SECTION 2
- [requirement]

# OUTPUT FORMAT
Use markdown with [specific format requirements].
```

### Creating Custom Patterns

**Process:**
1. Identify workflow requiring specialized prompt
2. Create pattern directory: `custom-patterns/[name]/`
3. Write `system.md` following structure above
4. Test via API: `{"model": "pattern-name", "messages": [...]}`
5. Iterate based on output quality
6. Document in UFC context

**Examples Created:**
- `daily-reflection`: GTD-aligned daily review
- `weekly-review`: Strategic weekly insights
- `risk-agents-content`: Blog content curation

### Pattern Best Practices

1. **Clear Identity**: Define specific role and purpose
2. **Structured Input**: Specify expected input format
3. **Organized Output**: Use markdown sections consistently
4. **Action-Oriented**: Focus on insights, not just description
5. **Context-Aware**: Reference Gavin's GTD system, goals, metrics
6. **Quantified**: Request specific data/metrics when available

## Workflow Examples

### Example 1: YouTube to Obsidian

```
User: "I want to save this AI safety talk to Obsidian: [YouTube URL]"

YOU (Personal Consultant):
1. Recognize content processing task
2. Delegate to Content Processor Agent

Content Processor Agent:
1. Extract YouTube transcript via Fabric API
2. Execute extract_wisdom pattern
3. Format output as Obsidian markdown:
   - Frontmatter: title, source, date, tags
   - Summary section
   - Key insights bullets
   - Quotes section
   - Action items
4. Delegate to Knowledge Manager

Knowledge Manager:
1. Receive formatted note
2. Create file: Notes/Videos/[title].md
3. Update daily note with link
4. Confirm storage

Result: Structured note in vault, linked from daily note
```

### Example 2: Daily Brief with Quality Scoring

```
User: "Give me today's daily brief"

YOU (Personal Consultant):
1. Delegate to Daily Brief Agent

Daily Brief Agent:
1. Search for AI/tech news (past 7 days)
2. For each article:
   a. Delegate to Content Processor
   b. Content Processor → Fabric: rate_content
   c. Receive quality score (1-10)
3. Filter: Keep score >= 7
4. Rank by score
5. Format briefing with top 5 articles

Result: Higher quality, curated daily briefing
```

### Example 3: CV Optimization for Job Application

```
User: "Optimize my CV summary for this AI Engineer role: [job description]"

YOU (Personal Consultant):
1. Delegate to Job Search Agent

Job Search Agent:
1. Read current CV summary
2. Extract job requirements
3. Delegate to Content Processor:
   - Pattern: improve_writing
   - Input: CV summary
   - Variables: job_description, voice=professional
4. Receive improved text
5. Show diff to user
6. If approved, update CV template

Result: Optimized CV section aligned with job requirements
```

## Error Handling

### Common Issues

**Pattern Not Found:**
- Check pattern name: `curl http://fabric-api:8080/patterns/names`
- Verify custom pattern exists in `custom-patterns/`
- Check spelling and case sensitivity

**API Authentication Failed:**
- Verify FABRIC_API_KEY environment variable
- Check X-API-Key header in request
- Test with known-good key

**Pattern Execution Timeout:**
- Use streaming mode for long content
- Split large inputs into chunks
- Increase timeout in agent configuration

**AI Provider Rate Limit:**
- Implement exponential backoff
- Fall back to secondary provider
- Queue requests and batch process

### Graceful Degradation

If Fabric unavailable:
1. Log error with details
2. Fall back to direct LLM call with similar prompt
3. Notify user of degraded mode
4. Continue workflow without blocking

## Monitoring and Maintenance

### Health Checks

Verify Fabric service health:
```bash
curl http://fabric-api:8080/patterns/names
```

Expected: JSON array of 233+ pattern names

### Pattern Updates

Update patterns from GitHub using the dedicated script:
```bash
# From Mac - updates patterns on Pi and restarts service
./integrations/fabric/scripts/update-patterns.sh
```

**Note:** The `/sync` API endpoint is non-functional because patterns are volume-mounted from the Pi host, not cloned inside the container. Use the update script instead.

### Session Cleanup

Sessions accumulate over time. Monitor storage:
```bash
du -sh /integrations/fabric/config/sessions/
```

Cleanup policy: 30 days retention (automated)

### Performance Monitoring

Track metrics:
- API response time (target: < 2s p95)
- Pattern execution success rate (target: > 98%)
- Memory usage (target: < 512MB)
- Request volume

## Security Considerations

### API Key Management

- Never log API keys in plain text
- Rotate FABRIC_API_KEY periodically
- Use environment variables, not hardcoded values
- Access control via Docker network isolation

### Input Validation

- Sanitize user inputs before Fabric API calls
- Validate URLs before YouTube transcript extraction
- Limit input size to prevent resource exhaustion
- Filter sensitive data before pattern execution

### Output Handling

- Review AI-generated content before storage
- Preserve source attribution
- Handle PII appropriately
- Validate markdown formatting

## Resources

### Documentation

- Integration README: `/integrations/fabric/README.md`
- Custom Patterns: `/integrations/fabric/custom-patterns/`
- UFC Context: `/.claude/context/tools/fabric-integration-context.md`
- Agent Definition: `/.claude/agents/content-processor-agent.md`

### External Links

- Fabric GitHub: https://github.com/danielmiessler/fabric
- Pattern Library: https://github.com/danielmiessler/fabric/tree/main/patterns
- API Documentation: Fabric repository docs
- Docker Images: https://hub.docker.com/r/kayvan/fabric

## Critical Constraints

1. **ALWAYS delegate to Content Processor Agent** - Don't call Fabric API directly
2. **NEVER reimplement patterns manually** - Use existing community patterns
3. **ALWAYS preserve source attribution** - Track content origin
4. **NEVER bypass authentication** - Include X-API-Key header
5. **ALWAYS format for Obsidian** - Follow markdown conventions
6. **NEVER store raw API responses** - Process and structure output
7. **ALWAYS handle errors gracefully** - Implement fallback workflows

## Success Factors

### Technical Success

- ✅ Fabric service healthy and responsive
- ✅ Pattern execution success rate > 98%
- ✅ API latency < 2s (p95)
- ✅ Clean agent delegation boundaries
- ✅ Proper error handling throughout

### Workflow Success

- ✅ YouTube → Obsidian in < 5 minutes
- ✅ Daily Brief quality improved (user feedback)
- ✅ CV optimization measurably better
- ✅ Custom patterns actively used
- ✅ Integration feels seamless to user

### Strategic Success

- ✅ Time saved on content processing (50% target)
- ✅ More content consumed and retained
- ✅ Better Obsidian note quality
- ✅ Increased blog publishing cadence
- ✅ Demonstrable AI integration expertise

## Questions and Clarifications

When working with this integration, ask yourself:

1. **Is Fabric the right tool?** (vs native LLM capabilities)
2. **Which pattern best fits this task?** (check pattern library)
3. **Should I use existing or create custom pattern?**
4. **Am I properly delegating to Content Processor?**
5. **Is error handling comprehensive?**
6. **Will output integrate cleanly downstream?**

If uncertain, consult:
- UFC context for integration guidelines
- Pattern library for capabilities
- Agent definitions for responsibilities
- User for preferences and priorities

---

**Remember**: Fabric is a tools-first integration. Leverage battle-tested community patterns rather than reinventing prompts. Maintain clean agent boundaries and delegation patterns. Focus on seamless user experience and quantified value delivery.
