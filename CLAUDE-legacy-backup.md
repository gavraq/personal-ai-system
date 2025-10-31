# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is Gavin's personal Life project repository, now architected as a comprehensive **Personal Consultant System** with specialized sub-agents that manage all aspects of his life coordination.

### Personal Consultant Architecture

The system operates through a master **Personal Consultant** that orchestrates **8 specialized sub-agents**:

1. **Personal Consultant** (`personal-consultant`) - Master orchestrator and strategic life coordinator
2. **Daily Brief Agent** (`daily-brief-agent`) - AI-powered news curation and current events analysis  
3. **FreeAgent Invoice Agent** (`freeagent-invoice-agent`) - Financial management and invoice operations
4. **Job Search Agent** (`job-search-agent`) - AI career transition specialist and opportunity identification
5. **Email Management Agent** (`email-management-agent`) - ✅ Email and calendar management using Gmail MCP server integration (Connected)
6. **Interactive CV Website Agent** (`interactive-cv-website-agent`) - Modern web development for portfolio website creation
7. **Knowledge Manager Agent** (`knowledge-manager-agent`) - Obsidian vault integration for personal knowledge management
8. **Location Agent** (`location-agent`) - Owntracks geolocation data analysis and travel pattern insights
9. **Health Agent** (`health-agent`) - Health and fitness data integration with quantified self analytics

### Legacy Python Systems (Now Sub-Agent Integrated)

1. **Daily Brief System** - AI-powered news curation that analyzes personal files for interests and delivers relevant news
2. **FreeAgent Sub-Agent** - Natural language interface for FreeAgent invoice management API

## Project Structure

```
/Users/gavinslater/projects/Life/
├── .claude/agents/                   # Claude Code Sub-Agent System
│   ├── personal-consultant.md       # Master orchestrator and life coordinator
│   ├── daily-brief-agent.md         # News curation and current events
│   ├── freeagent-invoice-agent.md   # Financial management specialist
│   ├── job-search-agent.md          # AI career transition specialist
│   ├── email-management-agent.md    # ✅ Email and calendar management (Gmail MCP)
│   ├── interactive-cv-website-agent.md # Modern web development for portfolio website
│   ├── knowledge-manager-agent.md   # Obsidian vault integration and knowledge management
│   └── location-agent.md             # Owntracks geolocation data analysis
├── sub-agent-framework/             # Framework for creating new sub-agents
│   ├── README.md                    # Sub-agent creation guidelines
│   └── sub-agent-template.md        # Template for new agents
├── linkedin-integration/            # Enhanced LinkedIn profile and job search system  
│   ├── linkedin_api_client.py       # Official LinkedIn API integration
│   ├── linkedin_apify_client.py     # NEW: Comprehensive Apify scraping integration
│   ├── linkedin_profile_manager.py  # LinkedIn profile management and optimization
│   ├── linkedin_job_searcher.py     # Enhanced job search with multiple access methods
│   ├── test_apify_integration.py    # NEW: Comprehensive Apify integration test suite
│   ├── APIFY_SETUP_GUIDE.md        # NEW: Complete Apify platform setup guide
│   ├── gavin_linkedin_profile.json  # LinkedIn profile data (auto-generated)
│   ├── venv/                        # Python virtual environment with Apify client
│   └── apify_data/                  # NEW: Directory for scraped LinkedIn data
│   └── linkedin_job_search_history.json # Job search history (auto-generated)
├── daily_brief.py                   # Legacy: Main integration for /daily-brief command
├── run_daily_brief.py               # Legacy: Alternative runner (less used)
├── daily-brief-system/              # Legacy: Core daily brief system
│   ├── daily_brief_simple.py        # Production system with web tools
│   ├── interest_analyzer.py         # Analyzes personal files for interests  
│   ├── news_curator.py              # Searches and curates current news
│   ├── daily_brief.py              # Core system orchestration
│   ├── demo_daily_brief.py         # Testing without web tools
│   ├── daily_brief.sh              # Shell wrapper (explains usage)
│   └── venv/                       # Python virtual environment
├── freeagent_subagent/             # Legacy: FreeAgent API integration
│   ├── invoice_subagent.py         # Natural language interface
│   ├── invoice_manager.py          # Invoice CRUD operations  
│   ├── freeagent_client.py         # Low-level API client
│   ├── config.py                   # Configuration management
│   ├── cli.py                      # Command-line interface
│   └── venv/                       # Python virtual environment
├── health-integration/             # NEW: Health and fitness data integration system
│   ├── health-service/             # Node.js microservice for health data APIs
│   │   ├── src/                    # Source code (Express.js server, parkrun client, database)
│   │   ├── data/                   # SQLite database storage
│   │   ├── package.json            # Node.js dependencies (parkrun.js v1.3.1)
│   │   └── README.md               # Service documentation and API reference
│   ├── python-client/              # Python client wrapper for health service
│   └── README.md                   # Complete health integration system documentation
├── Gavin Background.md              # Comprehensive personal profile (KEY REFERENCE)
├── daily-brief-*.md                # Generated daily briefs (output files)
└── *.md files                      # Personal notes and documentation
```

## Key Components

### Personal Consultant Sub-Agent System

The repository now operates primarily through Claude Code's sub-agent system located in `.claude/agents/`. Each sub-agent is a specialized AI assistant with specific expertise:

#### Master Agent: Personal Consultant (`personal-consultant`)
- **Role**: Central orchestrator and strategic life coordinator
- **Capabilities**: Delegates to specialized agents, provides strategic guidance, tracks goals
- **Integration**: Coordinates all other sub-agents and synthesizes results
- **Tools**: Task (for sub-agent delegation), WebSearch, WebFetch, Read, Write, Glob, Grep, Bash

#### Daily Brief Agent (`daily-brief-agent`) 
- **Role**: Personalized news curation and current events analysis
- **Capabilities**: Analyzes personal files for interests, searches current news, scores relevance
- **Integration**: Uses existing daily-brief-system/ Python components
- **Tools**: WebSearch, WebFetch, Read, Glob, Grep, Bash

#### FreeAgent Invoice Agent (`freeagent-invoice-agent`)
- **Role**: Financial management and invoice operations specialist  
- **Capabilities**: Natural language invoice management, ICBC automation, payment tracking, 🆕 enhanced OAuth re-authentication
- **Authentication**: 🆕 Automatic token refresh, seamless recovery, zero-downtime authentication management
- **Integration**: Uses existing freeagent_subagent/ Python package with enhanced authentication system
- **Tools**: Read, Write, Bash

#### Job Search Agent (`job-search-agent`)
- **Role**: AI career transition specialist with LinkedIn integration
- **Capabilities**: LinkedIn profile optimization, AI job search, profile-job matching, application tracking
- **Integration**: NEW agent focused on Gavin's AI career transition with LinkedIn profile management

#### Email Management Agent (`email-management-agent`)
- **Role**: Personal email and calendar management using Gmail MCP server integration
- **Capabilities**: Email organization, response drafting, meeting scheduling, calendar optimization, communication intelligence
- **Integration**: **NEW** agent using MCP Gmail server for comprehensive digital communication management
- **Tools**: mcp_* (Gmail MCP server), Read, Write

#### Interactive CV Website Agent (`interactive-cv-website-agent`)
- **Role**: Modern web development specialist for creating and maintaining Gavin's interactive portfolio website
- **Capabilities**: React/Next.js development, responsive design, project showcases, SEO optimization
- **Key Focus**: Showcasing 8-bit computer project (Ben Eater inspired) and technical skills for AI career transition
- **Technology Stack**: React 18, Next.js 14, TypeScript, Tailwind CSS, Framer Motion
- **Features**: Expandable sections, interactive timeline, project galleries, performance optimization
- **Integration**: Syncs with Job Search Agent for career-aligned content updates
- **Tools**: Read, Write, Bash

#### Knowledge Manager Agent (`knowledge-manager-agent`) 
- **Role**: Personal knowledge management specialist for Obsidian vault integration
- **Capabilities**: Information storage/retrieval, daily note creation, tag management, cross-referencing
- **Vault Location**: `/Users/gavinslater/Library/Mobile Documents/iCloud~md~obsidian/Documents/GavinsiCloudVault`
- **Features**: `/daily-note` command, YAML frontmatter, wikilinks, standardized templates
- **Integration**: Captures insights from other agents and research activities
- **Tools**: mcp_obsidian_* tools, Read, Write

#### Location Agent (`location-agent`)
- **Role**: Personal location intelligence using Owntracks geolocation data analysis
- **Capabilities**: Travel pattern analysis, time-at-location calculation, commute optimization, location history queries
- **Data Source**: https://owntracks.gavinslater.co.uk/ with API integration
- **Context**: 3-day office/2-day WFH schedule, Esher-London commute, Parkrun tracking
- **Features**: Movement pattern insights, geographic context for life events, travel optimization
- **Integration**: Provides location context for scheduling and lifestyle optimization
- **Tools**: WebFetch, Read, Write, Bash

#### Health Agent (`health-agent`)
- **Role**: Health and fitness data integration specialist with quantified self analytics
- **Capabilities**: Multi-platform health data aggregation, performance tracking, trend analysis, goal monitoring
- **Current Integration**: Parkrun.org (273+ results, 31 runs in 2025 confirmed)
- **Data Sources**: Parkrun results with dates, times, positions, age grades, personal bests
- **Architecture**: Node.js microservice (health-integration/health-service) with Python client wrapper
- **Features**: Real-time API access, SQLite caching, comprehensive performance statistics
- **Future Platforms**: Fitbit, Strava, Apple Health, Garmin Connect
- **Tools**: WebSearch, WebFetch, Read, Write, Bash

#### Job Search Agent (`job-search-agent`)
- **Role**: AI career transition specialist with LinkedIn integration
- **Capabilities**: LinkedIn profile optimization, AI job search, profile-job matching, application tracking
- **LinkedIn Features**: Profile analysis, job search, application tracking, optimization recommendations
- **Tools**: WebSearch, WebFetch, Read, Write, Glob, Bash

### Sub-Agent Usage Patterns

#### Primary Interaction Model
```
User Request → Personal Consultant → Sub-Agent(s) → Result Integration → Strategic Guidance
```

#### Common Delegation Scenarios
- **"What's happening in my field?"** → Daily Brief Agent
- **"Any outstanding invoices?"** → FreeAgent Invoice Agent  
- **"New AI job opportunities?"** → Job Search Agent (with LinkedIn integration)
- **"How's my LinkedIn profile for AI roles?"** → Job Search Agent (profile analysis)
- **"Find me LinkedIn jobs matching my background"** → Job Search Agent (LinkedIn search)
- **"Update my CV website"** → Interactive CV Website Agent (content updates and deployment)
- **"Add new project to my portfolio"** → Interactive CV Website Agent (project showcase creation)
- **"Create daily note"** → Knowledge Manager Agent (`/daily-note` command)
- **"Save this information"** → Knowledge Manager Agent (knowledge capture and organization)
- **"Where was I last Tuesday?"** → Location Agent (location history analysis)
- **"Analyze my commute patterns"** → Location Agent (travel pattern insights)
- **"Check my emails"** → Email Management Agent (email processing and summary)
- **"Schedule a meeting"** → Email Management Agent (calendar coordination)
- **"How many parkruns have I done this year?"** → Health Agent (2025 activity analysis)
- **"Show my parkrun performance trends"** → Health Agent (fitness analytics and insights)
- **"What's my recent fitness activity?"** → Health Agent (health data summary)
- **"Track my running progress"** → Health Agent (performance monitoring)
- **Complex multi-domain requests** → Multiple agents coordinated

### Legacy Python Systems (Sub-Agent Integrated)

#### Daily Brief System Architecture

**Main Integration**: `/Users/gavinslater/projects/Life/daily_brief.py` 
- Primary entry point for Claude Code `/daily-brief` command
- Imports from `daily-brief-system/daily_brief_simple.py`
- Requires Claude Code's WebSearch and WebFetch tools

**Core Components**:
- `InterestAnalyzer` - Scans 200+ personal files to identify interests and topics
- `NewsSearcher` - Searches current news (past 7 days only) from reputable sources
- `SimpleDailyBrief` - Main orchestration system with web tool integration

**Data Flow**:
1. Analyze personal files for interests (technology, business, locations)
2. Generate search terms from interest analysis 
3. Search web for recent news articles
4. Score articles for relevance (0.0-1.0)
5. Generate actionable suggestions for each relevant article
6. Format as comprehensive daily brief markdown

#### Email Management Agent Architecture

**Gmail MCP Integration**: ✅ **Connected and Operational**
- **Status**: Fully integrated with both Claude Desktop and Claude Code via mcp-gsuite server
- **Capabilities**: Email processing, response management, calendar coordination, meeting scheduling
- **Access Method**: Gmail MCP tools available through mcp-gsuite server in both environments
- **Usage**: Delegate through Personal Consultant for email and calendar tasks (works in both Claude Desktop and Claude Code)

**Core Functions**:
- Email organization and prioritization (work, personal, AI career opportunities)
- Response drafting in Gavin's professional voice and style
- Calendar management considering 3-day office/2-day WFH schedule
- Meeting coordination and conflict resolution
- Communication intelligence and analytics

**Integration Triggers**:
- "Check my emails" → Email processing and summary
- "Schedule a meeting" → Calendar coordination and invite management  
- "What's on my calendar?" → Schedule review and optimization
- "Draft email response" → Professional response generation
- "Any urgent emails?" → Priority email identification

### FreeAgent Sub-Agent Architecture

**Layered Design**:
- `InvoiceSubAgent` - Natural language command processing (high-level)
- `InvoiceManager` - Invoice CRUD operations (mid-level) 
- `FreeAgentClient` - HTTP API client with OAuth (low-level)
- `FreeAgentConfig` - Configuration and credential management

**Natural Language Processing**: Regex patterns for commands like:
- "list invoices", "show overdue invoices", "total outstanding"
- "create ICBC invoice for July 2025 14 days" (automated invoice creation)

**Production Ready**: Successfully tested with real ICBC Standard Bank production account, handles OAuth token refresh automatically.

## Development Commands

### Daily Brief System

**Primary Usage** (in Claude Code environment):
```python
from daily_brief import daily_brief
result = daily_brief()
print(result)
```

**Virtual Environment Setup** (if needed):
```bash
cd daily-brief-system
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

**Testing without Web Tools**:
```bash
cd daily-brief-system
python3 demo_daily_brief.py
```

**Dependencies**: `requests`, `python-dateutil`, `beautifulsoup4`, `feedparser`

### FreeAgent Sub-Agent

**Primary Usage**:
```python
from freeagent_subagent import create_subagent
subagent = create_subagent()
result = subagent.process_command("show unpaid invoices")
print(result)
```

**CLI Interface**:
```bash
cd freeagent_subagent
python -m freeagent_subagent.cli "list invoices"
python -m freeagent_subagent.cli --setup  # Configuration wizard
```

**Virtual Environment**:
```bash
cd freeagent_subagent  
source venv/bin/activate
pip install -r requirements.txt
```

**Dependencies**: `requests` only

## Configuration & Authentication

### Daily Brief System
- **Analysis Paths**: Scans `/Users/gavinslater/projects/life`, Desktop, iCloud Obsidian vault, `.config`
- **File Types**: `.txt`, `.md`, `.py`, `.js`, `.json`, `.yaml`, `.csv`, `.log`
- **News Sources**: BBC, Reuters, Bloomberg, Financial Times, TechCrunch, The Guardian
- **No Authentication Required**: Uses public web search only

### FreeAgent Sub-Agent  
- **Credentials**: Uses existing "FreeAgent AI Agent" app (Client ID: `970GvhTqju_QFVpCf3vpLw`)
- **Config File**: `~/.config/freeagent/config.json`
- **OAuth Setup**: Automatic token refresh, production mode ready
- **Environment Variables**: `FREEAGENT_CLIENT_ID`, `FREEAGENT_CLIENT_SECRET`, etc.

### Email Management Sub-Agent
- **Gmail MCP Integration**: ✅ Connected in both Claude Desktop and Claude Code
- **Status**: Fully operational in both environments via mcp-gsuite server
- **Capabilities**: Email processing, calendar management, meeting scheduling
- **Usage**: Available through Personal Consultant delegation in both Claude Desktop and Claude Code
- **Configuration**: mcp-gsuite server configured with existing Google account credentials

## LinkedIn Integration System

The Job Search Agent includes comprehensive LinkedIn integration with multiple access methods:

### Enhanced LinkedIn Access Methods

#### 1. LinkedIn API Integration (Limited)
- **Official API**: Uses Gavin's registered LinkedIn Developer App
- **Capabilities**: Basic profile data via OpenID Connect, LinkedIn posting functionality
- **Status**: Working for posts, limited for profile data extraction
- **Best For**: LinkedIn posting and basic profile access

#### 2. **NEW: Apify Job Scraping Integration (Free)** 
- **Platform**: Uses Apify.com free LinkedIn job scraper
- **Capabilities**: LinkedIn job data extraction with detailed descriptions and requirements
- **Advantages**: Comprehensive job market analysis, skill frequency data, career insights
- **Legal Note**: Uses public job data scraping (legally gray area but lower risk)
- **Cost**: ~$0.01 per job search (~$0.65/month for typical usage)
- **Actor**: valig/linkedin-jobs-scraper (100% free)

#### 3. Fallback Web Search Integration
- **Method**: Uses Claude Code's WebSearch to find LinkedIn job postings
- **Benefits**: Completely respects LinkedIn's terms of service
- **Limitations**: Limited data extraction capability

### LinkedIn Profile Management
- **Profile Template**: Auto-generated based on Gavin's known background and career history
- **LinkedIn API Access**: Basic profile data via OpenID Connect, posting capability
- **Optimization Engine**: Provides specific suggestions for AI career transition based on job market analysis
- **Skills Tracking**: Manages technical and business skills relevant to AI roles
- **Progress Monitoring**: Tracks profile updates and optimization status
- **No Premium Scraping**: Profile scraping removed to avoid account risks and costs

### LinkedIn Job Search Capabilities  
- **Free Job Scraping**: **NEW** Comprehensive LinkedIn job data extraction via Apify free scraper
- **Market Intelligence**: **NEW** AI job market trends, skill frequency analysis, salary insights
- **Profile-Job Matching**: Analyzes job requirements against LinkedIn API profile data
- **Career Transition Insights**: **NEW** AI-powered analysis for Risk Management to AI transition
- **Application Tracking**: Monitors applications, follow-ups, and response rates
- **Cost-Effective**: ~$0.65/month for comprehensive job market intelligence
- **Fallback Web Search**: Uses Claude Code's WebSearch when Apify unavailable

### Key Features
- **Dual Access Methods**: LinkedIn API for profile data, Apify free scraper for jobs, web search fallback
- **Profile Optimization**: Uses LinkedIn API data combined with job market insights for profile optimization
- **Advanced Job Analytics**: **NEW** Comprehensive job market analysis with skill frequency data via free Apify scraper
- **Job Match Scoring**: Rates job opportunities (0-100%) against LinkedIn API profile data
- **Application Recommendations**: Provides specific guidance on application approach
- **Search History**: Maintains detailed records of searches and applications
- **Cost Effective**: **NEW** Only ~$0.65/month for comprehensive job market intelligence

### Implementation Files
- **`linkedin_api_client.py`**: **NEW** Official LinkedIn API integration with Gavin's credentials
- **`linkedin_apify_client.py`**: **NEW** Free Apify job scraper integration (profile scraping removed)
- **`linkedin_profile_manager.py`**: Profile data management and optimization recommendations
- **`linkedin_job_searcher.py`**: Enhanced job search functionality with multiple access methods
- **`test_apify_integration.py`**: **NEW** Comprehensive test suite for Apify integration
- **`APIFY_SETUP_GUIDE.md`**: **NEW** Complete setup guide for free Apify job scraping
- **Data Files**: JSON storage for profile data, job searches, and application tracking

### Sample LinkedIn Integration Outputs

#### LinkedIn Profile Analysis (API-Based)
```markdown
# LinkedIn Profile Analysis - Gavin Slater

## LinkedIn API Profile Data
- Name: Gavin Slater  
- Email: gavin@slaters.uk.com
- Person ID: jX975koQMc (for posting)
- LinkedIn URL: https://www.linkedin.com/in/gavinslater/
- API Access: Basic profile data, posting capability

## Profile Template (From LinkedIn Export)
- Headline: Head of Risk Infrastructure
- Location: Esher, England, United Kingdom  
- Current Position: Head of Risk Infrastructure at ICBC Standard Bank Plc (Feb 2021 - Present)
- Experience: 25+ years across Barclays Capital, Deutsche Bank, Nordea, Arthur Andersen
- Education: MBA (Warwick), Chartered Accountant
- Key Achievements: Led 300+ person teams, Co-founder Stream Financial, Digital transformation leader
- Skills: Strategy, Risk Management, Digital Transformation, Data Architecture, Team Leadership

## AI Transition Readiness Analysis (Based on LinkedIn Export + Job Market Data)
- Current AI Readiness: 45% (significantly stronger than initially assessed)
- AI Skills Present: Python, Data Architecture, Digital Transformation, Risk Analytics
- Leadership Advantage: 300+ person team leadership, C-level strategy experience
- Unique Value Proposition: Risk Management + Digital Transformation (rare in AI field)
- Missing Technical Skills: TensorFlow, PyTorch, MLOps (from job scraping analysis)  
- Projected Improvement: 75% readiness after AI skill development

## Optimization Recommendations (Based on LinkedIn Export + Job Market Intelligence)
1. Update headline: "Head of Risk Infrastructure | AI & Risk Management Innovator | Digital Transformation Leader"
2. Emphasize unique combination: Senior leadership + Risk expertise + Digital transformation (rare in AI field)
3. Add AI learning journey section highlighting Python development and AI exploration
4. Leverage major bank experience (Barclays, Deutsche Bank) - highly valued in AI roles
5. Highlight data architecture and team leadership experience (300+ people)
6. Create LinkedIn content on "AI in Risk Management" to establish thought leadership
```

#### Enhanced Job Market Analysis (Apify Scraping)
```markdown
# AI Job Market Analysis - London

## Search Results Summary
- Total AI jobs found: 127 across 5 search terms
- Unique companies: 43 companies hiring
- Date range: Past 7 days

## Skill Frequency Analysis
- Python: 89% of jobs (highly valuable)
- Machine Learning: 76% of jobs (critical skill)
- TensorFlow: 54% of jobs (important framework)
- Risk Management: 23% of jobs (unique advantage)
- Financial Services: 31% of jobs (strong differentiator)

## Top Job Match
- **Position**: Senior AI Risk Analyst - Barclays
- **Match Score**: 87% (excellent fit)
- **Matching Skills**: Risk Management, Python, Financial Services
- **Missing Skills**: TensorFlow, MLOps  
- **Recommendation**: 🎯 Apply immediately - perfect risk+AI combination
- **Application Strategy**: Emphasize unique risk management + AI transition story

## Career Transition Insights
- Risk + AI combination appears in 23% of relevant postings
- Financial services AI roles growing (31% of matches)
- Python skills are essential (89% requirement rate)
- Your banking experience provides significant advantage
```

#### Market Intelligence Dashboard
```markdown  
# Weekly AI Job Intelligence Report

## New Opportunities This Week: 23 jobs
🎯 High Priority (3):
- Senior AI Risk Manager - HSBC (92% match)
- ML Engineer, Financial Services - Revolut (85% match)  
- AI Solutions Architect - Accenture (78% match)

## Market Trends
- Average salary: £95K-£120K for senior AI roles
- Remote work: 67% offer hybrid/remote options
- Top hiring companies: Barclays, HSBC, Revolut, JP Morgan

## Skill Development Priority
1. TensorFlow (76% of jobs) - High Impact
2. MLOps (54% of jobs) - Medium Impact  
3. AWS/Azure (43% of jobs) - Medium Impact
```

## Extensible Sub-Agent Framework

The system includes a comprehensive framework for adding new sub-agents easily:

### Framework Components
- **`sub-agent-framework/README.md`**: Complete guide for creating new sub-agents
- **`sub-agent-framework/sub-agent-template.md`**: Template with all required sections
- **Design Principles**: Single responsibility, Gavin-specific customization, proactive intelligence
- **Integration Patterns**: Clear delegation triggers and Personal Consultant coordination

### Creating New Sub-Agents
1. **Use Template**: Copy and customize `sub-agent-template.md`  
2. **Place in Directory**: Save as `.claude/agents/[agent-name].md`
3. **Update Personal Consultant**: Add to delegation logic and sub-agent roster
4. **Test Integration**: Verify proper coordination through master agent

### Planned Future Agents
Based on Gavin's comprehensive profile, valuable additional agents include:
- **Health & Fitness Agent**: Quantified self data, Parkrun tracking, weight management
- **Learning & Development Agent**: Python advancement, AI/ML education, certification tracking  
- **Content Creation Agent**: Blog planning, risk-agents.com development, social media strategy
- **Home & Lifestyle Agent**: Home automation, 3D printing projects, gadget research
- **Travel & Family Agent**: Trip planning, family coordination, US annual trips

## Current Agent Portfolio Status: **9 Active Sub-Agents**

**✅ Deployed & Operational (9)**:
1. **Personal Consultant** - Master orchestrator and life coordinator
2. **Daily Brief Agent** - AI-powered news curation with personal interest analysis
3. **FreeAgent Invoice Agent** - Financial management with ICBC automation and 🆕 enhanced OAuth re-authentication
4. **Job Search Agent** - LinkedIn integration with AI career transition focus
5. **Email Management Agent** - Gmail MCP server integration (fully connected)
6. **Interactive CV Website Agent** - Modern web development for portfolio showcase
7. **Knowledge Manager Agent** - Obsidian vault integration with `/daily-note` command
8. **Location Agent** - Owntracks geolocation analysis and travel optimization
9. **Health Agent** - Health and fitness data integration with parkrun.org (273+ results)

## Integration Notes

### Personal Consultant System Usage
The primary interface is through the master Personal Consultant, which:
- **Analyzes requests** and determines appropriate sub-agent delegation
- **Coordinates multiple agents** for complex, multi-domain queries
- **Synthesizes results** into strategic guidance and actionable recommendations
- **Tracks progress** toward Gavin's long-term goals and objectives
- **Provides proactive insights** based on integrated intelligence from all agents

### Legacy System Integration

#### Daily Brief Command Integration
The `/daily-brief` command in Claude Code uses:
- **Main file**: `/Users/gavinslater/projects/Life/daily_brief.py` 
- **Core system**: `daily-brief-system/daily_brief_simple.py`
- **Output**: Saves briefs to `/Users/gavinslater/projects/Life/daily-brief-YYYY-MM-DD.md`
- **Requirements**: Must run in Claude Code environment with WebSearch/WebFetch tools

### FreeAgent Production Integration
- **ICBC Automation**: Special handling for ICBC Standard Bank invoices
- **PO Detection**: Automatically finds PO numbers (PO32334) from historical invoices  
- **Rate Detection**: Uses £1,700/day rate from historical analysis
- **Sequence Management**: Maintains proper invoice numbering (016, 017, 018...)
- **Production Account**: BRIGHT SLATE LTD with 25+ invoices, £152K+ outstanding

## File Analysis Paths

### Interest Analysis (Daily Brief)
```python
default_paths = [
    "/Users/gavinslater/projects/life",      # This repository
    "/Users/gavinslater/Desktop",            # Current work files  
    "/Users/gavinslater/Library/Mobile Documents/iCloud~md~obsidian/Documents/GavinsiCloudVault",  # Obsidian notes
    "/Users/gavinslater/.config"             # Configuration files
]
```

### Key Interest Categories Detected
- **Technology**: python (238 mentions), api (222), docker (220), ai (143)
- **Business**: risk management, finance, consulting, audit  
- **Companies**: ICBC, Standard Bank, FreeAgent
- **Locations**: London, Surrey, New York

## Performance Characteristics

### Daily Brief Generation
- **Analysis Phase**: 30-60 seconds (processes 200+ files, 1M+ characters)
- **Curation Phase**: 2-4 minutes (10-12 web searches, 20-30 articles processed)  
- **Total Time**: 3-5 minutes for complete personalized brief
- **Output**: 10-15 relevant articles with 0.3+ relevance scores

### FreeAgent Operations  
- **Invoice Listing**: 1-2 seconds (with pagination)
- **Invoice Creation**: 2-3 seconds per invoice
- **OAuth Refresh**: Automatic, transparent to user
- **Rate Limiting**: 60 requests/minute with exponential backoff

## Testing Strategy

### Daily Brief System
- **No formal test suite** - uses demo system for validation
- **Demo Testing**: `python3 daily-brief-system/demo_daily_brief.py`
- **Integration Testing**: Run `/daily-brief` command in Claude Code
- **Validation**: Check generated briefs in daily-brief-*.md files

### FreeAgent Sub-Agent  
- **No formal test suite** - uses sandbox environment
- **Manual Testing**: CLI commands and natural language processing  
- **Production Validation**: Successfully created real invoices (ICBC 016-018)
- **OAuth Testing**: Token refresh cycles validated in production

## Error Handling & Troubleshooting

### Daily Brief Common Issues
- **"Web search tools not available"**: Must run in Claude Code environment, not standalone Python
- **"No relevant articles found"**: Lower `min_relevance` threshold or increase `max_articles`  
- **"Could not analyze interests"**: Check file permissions in analysis paths

### FreeAgent Common Issues
- **Authentication errors**: Use OAuth Playground for token setup
- **Rate limiting**: Built-in exponential backoff handles automatically
- **Invoice creation failures**: Check contact mapping and required fields

## Security Considerations

### Daily Brief System
- **Local Processing**: All file analysis happens locally, no upload to external services
- **Web Search Only**: Only search queries sent over network, not file contents
- **No Persistence**: No permanent storage of personal information  
- **Privacy First**: Your personal files never leave the machine

### FreeAgent Sub-Agent
- **OAuth Security**: Production-grade OAuth 2.0 implementation
- **Credential Storage**: Secure config file with automatic token refresh
- **API Rate Limiting**: Respects FreeAgent API limits and guidelines
- **Production Ready**: Handles real financial data with appropriate security

## Development Environment

### System Requirements
- **Python**: 3.9+ (currently using 3.13)
- **Platform**: macOS (Darwin 24.6.0) - paths may need adjustment for other platforms
- **Internet**: Required for news search and FreeAgent API calls
- **Claude Code**: Required for daily brief web tool integration

### IDE Integration
- **No specific IDE requirements** - standard Python development environment  
- **Virtual Environments**: Both systems include pre-configured venv directories
- **Dependencies**: Minimal - mostly standard library with requests, beautifulsoup4, feedparser

## Using the Personal Consultant System

### Primary Interface
The repository now operates through the **Personal Consultant sub-agent system**. To use:

1. **Activate Personal Consultant**: In Claude Code, the system should automatically recognize requests and delegate to the Personal Consultant
2. **Natural Language Requests**: Ask questions or give commands in natural language
3. **Multi-Domain Coordination**: The Personal Consultant will coordinate multiple sub-agents as needed
4. **Strategic Guidance**: Receive integrated insights aligned with Gavin's long-term goals

### Example Usage Patterns
- **"Good morning, what should I focus on today?"** → Personal Consultant coordinates daily brief, financial status, and strategic priorities
- **"Any new AI job opportunities on LinkedIn?"** → Job Search Agent searches LinkedIn with profile matching
- **"How ready is my LinkedIn profile for AI roles?"** → Job Search Agent analyzes profile and provides optimization plan
- **"What's my financial situation?"** → FreeAgent Invoice Agent provides comprehensive status
- **"What's happening in my field?"** → Daily Brief Agent curates relevant news and insights
- **"Analyze this LinkedIn job posting for me"** → Job Search Agent provides match score and application strategy
- **"Update my portfolio website with this new project"** → Interactive CV Website Agent creates project showcase and deploys updates
- **"Where did I spend most time last week?"** → Location Agent analyzes Owntracks data for time-at-location insights
- **"Create today's daily note"** → Knowledge Manager Agent generates standardized daily note in Obsidian vault
- **"Save this research for later"** → Knowledge Manager Agent organizes information with proper tags and cross-references
- **"What urgent emails do I have?"** → Email Management Agent processes Gmail and prioritizes responses
- **"Optimize my commute based on recent patterns"** → Location Agent provides travel optimization suggestions
- **"How's my fitness going this year?"** → Health Agent provides comprehensive 2025 parkrun statistics (31 runs confirmed)
- **"What's my parkrun performance trend?"** → Health Agent analyzes performance data across venues and time periods
- **"Track my health and fitness goals"** → Health Agent integrates multiple health data sources for holistic view

### Key Benefits
- **Holistic Life Management**: All aspects coordinated through single interface
- **Goal-Aligned Actions**: Every interaction connects to Gavin's broader objectives
- **Proactive Intelligence**: System anticipates needs and suggests optimizations
- **Extensible Architecture**: Easy to add new specialized agents as life needs evolve

This repository represents a comprehensive Personal Consultant system built specifically for Gavin's workflow, goals, and interests, designed to work seamlessly within the Claude Code sub-agent environment.