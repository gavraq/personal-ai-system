# Phase 5: Research Agents

**Features**: feat-27, feat-23, feat-24, feat-25, feat-26, feat-28
**Priority**: P1/P2/P3 - AI capabilities
**Depends on**: Phase 4 (Dashboard)

## Pre-requisites
- [ ] Phase 4 complete (dashboard working)
- [ ] Anthropic API key configured
- [ ] Files uploaded for document analysis testing

## 5.1 Agent Delegation Framework (feat-27)

- [ ] Create `backend/app/agents/base.py` with BaseAgent abstract class
- [ ] Define AgentInput, AgentOutput, AgentStatus schemas
- [ ] Implement async execution pattern with status polling
- [ ] Create `backend/app/models/agent_run.py` for tracking runs
- [ ] Create `backend/app/models/agent_message.py` for chat history
- [ ] Implement POST `/api/agents/{agent_type}/run` - start agent
- [ ] Implement GET `/api/agents/runs/{run_id}` - get status/result
- [ ] Implement GET `/api/agents/runs/{run_id}/messages` - get chat history
- [ ] Store results in agent_runs table with deal association
- [ ] Error handling with retry logic (max 3 attempts)
- [ ] Test: Agent async execution returns run_id
- [ ] Test: Status polling shows progress then completion
- [ ] Test: Error handling works gracefully
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-27 passing`

## 5.2 Market Research Agent (feat-23)

- [ ] Create `backend/app/agents/market_research.py`
- [ ] Input: company name, sector, or market query
- [ ] Output structure: market_overview, trends, competitors, opportunities, risks
- [ ] Use Claude API for analysis
- [ ] Include web search for current data (optional: Tavily/SerpAPI)
- [ ] Cite sources in output
- [ ] Save results to deal's agent_runs
- [ ] Test: Query "Tech sector trends 2024" returns structured analysis
- [ ] Test: Results include source citations
- [ ] Test: Results persist and are retrievable
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-23 passing`

## 5.3 Document Analysis Agent (feat-24)

- [ ] Create `backend/app/agents/document_analysis.py`
- [ ] Input: file_id reference
- [ ] Support: PDF, DOCX, TXT, images (OCR)
- [ ] For Drive files: fetch via Drive API
- [ ] For GCS files: download from signed URL
- [ ] Output structure: summary, key_points, entities, recommendations
- [ ] Use Claude vision for images/scanned PDFs
- [ ] Link results to source file
- [ ] Test: Analyze PDF returns summary and key points
- [ ] Test: Analyze Drive file works
- [ ] Test: Results linked to file
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-24 passing`

## 5.4 Due Diligence Agent (feat-25)

- [ ] Create `backend/app/agents/due_diligence.py`
- [ ] Input: entity_name, entity_type (company/person/transaction)
- [ ] Output structure: overview, financials, leadership, news, risk_flags, sources
- [ ] Use web search for current information
- [ ] Highlight risk flags with severity levels
- [ ] Include regulatory/legal considerations
- [ ] Test: Query company returns structured report
- [ ] Test: Risk flags displayed with severity
- [ ] Test: Sources cited
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-25 passing`

## 5.5 News & Alerts Agent (feat-26)

- [ ] Create `backend/app/agents/news_alerts.py`
- [ ] Create `backend/app/models/alert.py` for alert configuration
- [ ] Implement POST `/api/agents/alerts` - create alert
- [ ] Implement GET `/api/agents/alerts` - list user's alerts
- [ ] Implement DELETE `/api/agents/alerts/{alert_id}` - remove alert
- [ ] Alert config: keywords, entities, frequency (daily/weekly)
- [ ] Background job to check news sources (Celery or APScheduler)
- [ ] Generate notification when match found
- [ ] Store alert matches in database
- [ ] Test: Create alert saves configuration
- [ ] Test: Alert triggers on keyword match
- [ ] Test: Notification received
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-26 passing`

## 5.6 Agent Chat UI (feat-28)

- [ ] Create `frontend/components/agents/AgentChat.tsx` component
- [ ] Chat-style message interface with user/agent messages
- [ ] Agent type selector (Market, Document, Due Diligence, News)
- [ ] Message history per agent per deal
- [ ] Streaming responses using Server-Sent Events
- [ ] Quick prompt suggestions based on agent type
- [ ] Loading indicator during agent processing
- [ ] Copy/export results functionality
- [ ] Test: Send message, receive response
- [ ] Test: Message history persists on refresh
- [ ] Test: Streaming displays incrementally
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-28 passing`

## 5.7 Agent Integration with Deal Page

- [ ] Add agent panel to deal detail page
- [ ] Tab interface for each agent type
- [ ] Context-aware prompts (pre-fill deal name, file list)
- [ ] "Analyze this file" quick action on file list items
- [ ] Agent results appear in activity feed

## Phase 5 Completion

- [ ] All 6 features (feat-27, feat-23, feat-24, feat-25, feat-26, feat-28) marked as passing
- [ ] All 4 agent types functional
- [ ] Chat UI working with streaming
- [ ] Results persist and display on dashboard
- [ ] Run `bun .claude/skills/CORE/Tools/FeatureRegistry.ts verify family-office-files` to confirm
