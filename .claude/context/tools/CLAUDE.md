# Tools-First Protocol

## Core Principle: TOOLS FIRST, ALWAYS
Before any custom solution, leverage existing integrations and specialized sub-agents.

## 🤖 Available Sub-Agents Portfolio

### Master Orchestration
- **Personal Consultant** (`personal-consultant`) - Central life coordination and goal alignment
  - **Capabilities**: Strategic guidance, multi-agent coordination, progress tracking
  - **Usage**: Master orchestrator for complex, multi-domain requests

### Communication & Knowledge
- **Email Management Agent** (`email-management-agent`) - Gmail MCP integration
  - **Tools**: Gmail MCP server, calendar coordination
  - **Usage**: Email processing, meeting scheduling, communication optimization
- **Knowledge Manager Agent** (`knowledge-manager-agent`) - Obsidian integration
  - **Tools**: Obsidian MCP, daily note creation, cross-referencing
  - **Usage**: Information storage, retrieval, daily journaling
- **Daily Journal Agent** (`daily-journal-agent`) - Daily planning and reflection orchestration
  - **Tools**: Multi-agent coordination, pattern learning, quantified self integration
  - **Usage**: Morning planning briefing, evening reflection capture, habit tracking
  - **Commands**: `/daily-journal-morning`, `/daily-journal-evening`
- **GTD Task Manager Agent** (`gtd-task-manager-agent`) - Getting Things Done task management
  - **Tools**: Obsidian MCP, Tasks plugin integration, daily note Actions sections
  - **Usage**: Task creation, completion tracking, GTD context organization, capture processing

### Financial & Career
- **FreeAgent Invoice Agent** (`freeagent-invoice-agent`) - Financial operations
  - **Tools**: FreeAgent API with OAuth automation
  - **Usage**: Invoice management, payment tracking, ICBC automation
- **Job Search Agent** (`job-search-agent`) - AI career transition specialist
  - **Tools**: LinkedIn API, Apify scraper, profile optimization
  - **Usage**: Job opportunities, career development, LinkedIn management

### Health & Location
- **Health Agent** (`health-agent`) - Quantified self tracking
  - **Tools**: Parkrun API, health microservice, performance analytics
  - **Usage**: Fitness tracking, parkrun analysis, health optimization
- **Location Agent** (`location-agent`) - Movement intelligence
  - **Tools**: Owntracks API, pattern analysis, travel optimization
  - **Usage**: Location history, commute analysis, time-at-location insights

### Development & Content
- **Interactive CV Website Agent** (`interactive-cv-website-agent`) - Portfolio development
  - **Tools**: React/Next.js, modern web development
  - **Usage**: CV website updates, project showcases, technical portfolio
- **Daily Brief Agent** (`daily-brief-agent`) - News curation
  - **Tools**: WebSearch, interest analysis, relevance scoring
  - **Usage**: Personalized news briefing, industry insights

## 🔄 Primary Integration Stack

### API Integrations (Tools-First Priority)
1. **Gmail MCP** → Email/calendar operations (✅ Connected)
2. **FreeAgent API** → Financial management (✅ OAuth enhanced)
3. **LinkedIn API** → Career development (✅ Developer app)
4. **Parkrun API** → Health/fitness tracking (✅ Node.js service)
5. **Owntracks API** → Location intelligence (✅ Self-hosted)
6. **Obsidian MCP** → Knowledge management (✅ Available)

### Agent Selection Logic
- **Communication**: Email Management Agent → Gmail MCP → Manual
- **Financial**: FreeAgent Invoice Agent → FreeAgent API → Manual
- **Career & Job Search**: **ALWAYS** use Job Search Agent → LinkedIn API + Apify → Web search
- **Health**: Health Agent → Parkrun API → Manual tracking
- **Location**: Location Agent → Owntracks API → Manual analysis
- **Knowledge**: Knowledge Manager Agent → Obsidian MCP → File system
- **Tasks & GTD**: GTD Task Manager Agent → Obsidian MCP → Manual task management
- **Content**: Daily Brief Agent → WebSearch → Manual curation
- **Development**: Interactive CV Website Agent → Claude Code tools

### Job Search Priority
**CRITICAL**: For ANY job search, career development, application, or LinkedIn-related requests, ALWAYS use the Job Search Agent (`job-search-agent`) as the first action. This includes:
- Job applications and cover letters
- CV/resume reviews and optimization
- LinkedIn profile updates
- Career transition planning
- Salary negotiation and market analysis
- Interview preparation
- Professional networking strategies

### Task Management Priority
**CRITICAL**: For ANY task-related requests (creating, completing, organizing, reviewing tasks), ALWAYS use the GTD Task Manager Agent (`gtd-task-manager-agent`) instead of the Knowledge Manager Agent. This includes:
- Creating new tasks/todos
- Marking tasks as complete
- Task organization and context assignment
- GTD capture processing
- Task review and planning

## 🔧 Integration Contexts
- **Gmail**: `gmail-mcp-context.md`
- **FreeAgent**: `freeagent-api-context.md`
- **LinkedIn**: `linkedin-api-context.md`
- **Health APIs**: `parkrun-api-context.md`
- **Location**: `location-integration-context.md`

## 📁 Detailed Implementation References
- **Agent Definitions**: `/.claude/agents/[agent-name].md`
- **Project Integration**: `/[project-folder]/README.md` or `/[project-folder]/CLAUDE.md`
- **API Documentation**: Project-specific directories contain full implementation details

---
*Load full project contexts only when specific queries require detailed implementation knowledge*