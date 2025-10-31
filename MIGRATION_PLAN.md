# Migration Plan: From Standalone Integrations to Unified Agent Server

## Current State vs. New Architecture

### What You Have Now

**Standalone Integration Projects:**
```
/Users/gavinslater/projects/life/
├── freeagent_subagent/          # Python-based FreeAgent integration
├── linkedin-integration/         # LinkedIn API integration
├── health-integration/           # Parkrun API integration
├── location-integration/         # Owntracks integration
└── interactive-cv-website/       # Next.js website (Vercel)
```

**Agent Definitions (Working):**
```
.claude/agents/
├── daily-brief-agent.md
├── daily-journal-agent.md
├── email-management-agent.md
├── freeagent-invoice-agent.md
├── gtd-task-manager-agent.md
├── health-agent.md
├── horizons-reviewer-agent.md
├── interactive-cv-website-agent.md
├── job-search-agent.md
├── knowledge-manager-agent.md
├── location-agent.md
├── personal-consultant.md
├── project-setup-review-agent.md
└── weekly-review-agent.md
```

### What Changes with New Architecture

**New Addition (Not Replacement):**
```
/Users/gavinslater/projects/life/
├── claude-agent-server/          # NEW: Unified agent server
├── freeagent_subagent/          # KEEP: Still used by agent
├── linkedin-integration/         # KEEP: Still used by agent
├── health-integration/           # KEEP: Still used by agent
├── location-integration/         # KEEP: Still used by agent
└── interactive-cv-website/       # MODIFIED: Add agent mode toggle
```

## ⚠️ Important: Nothing Gets Deleted!

### What Stays Exactly As-Is

✅ **All agent definitions** in `.claude/agents/` - These are **essential** and will be loaded by the agent server

✅ **All integration projects** (`freeagent_subagent`, `linkedin-integration`, `health-integration`, `location-integration`) - These contain the **implementation logic** that agents use

✅ **All UFC context files** in `.claude/context/` - These provide the system awareness

✅ **All project files** in the life directory - These are mounted read-only for reference

### What Gets Added (No Deletions)

➕ **New `claude-agent-server/` directory** - The WebSocket server

➕ **New files in `interactive-cv-website/`**:
- `src/lib/agent-client.ts` (new file)
- `src/app/api/agent/token/route.ts` (new file)
- `src/components/ChatInterface.tsx` (modified - adds agent mode)
- `.env.example` (modified - adds agent variables)

### What Gets Modified

📝 **interactive-cv-website/src/components/ChatInterface.tsx**
- **What changes:** Adds agent mode toggle and WebSocket client
- **What stays:** All existing Anthropic API functionality
- **Impact:** Users can now choose between API mode (current) and Agent mode (new)

📝 **interactive-cv-website/.env**
- **What's added:**
  - `NEXT_PUBLIC_AGENT_WS_URL=wss://agent.gavinslater.com/ws`
  - `JWT_SECRET=<shared-secret>`
- **What stays:** All existing environment variables

## Why Nothing Gets Deleted

### 1. Integration Projects Are Still Needed

The standalone integration projects (`freeagent_subagent`, etc.) contain the **actual implementation code**:

```
When agent invokes "freeagent-invoice-agent":
    ↓
Claude Agent SDK looks up .claude/agents/freeagent-invoice-agent.md
    ↓
Agent definition may reference code in /projects/freeagent_subagent/
    ↓
Integration code executes via agent tools
```

**Example:** The FreeAgent agent might use:
- Python code from `/freeagent_subagent/` for OAuth flows
- API wrapper functions from `config.py` and `exceptions.py`
- Environment variables from the integration's `.env`

### 2. Agent Definitions Load These Projects

Look at any agent definition:

```markdown
---
name: freeagent-invoice-agent
tools: Read, Write, Bash, WebFetch, Glob, Grep
---

# System Prompt

When working with FreeAgent:
1. Use the Python client in /projects/freeagent_subagent/
2. Read credentials from /projects/freeagent_subagent/.env
3. Execute via: `python /projects/freeagent_subagent/main.py`
```

The integration projects are **mounted into the Docker container** at `/projects:ro` (read-only).

### 3. Dual-Mode Architecture

The new system supports **both modes**:

| Feature | API Mode (Current) | Agent Mode (New) |
|---------|-------------------|------------------|
| Backend | Anthropic API via Vercel | Claude Agent SDK on home server |
| Context | Basic system prompt | Full UFC context |
| Tools | None | All MCP servers + specialized agents |
| Integrations | None | FreeAgent, LinkedIn, Health, Location, etc. |
| Persistence | Vercel Postgres | Vercel Postgres |

**Users can switch between modes** with the toggle button!

## Architecture Visualization

### Before (Current)

```
User → Vercel (interactive-cv-website) → Anthropic API
        ↓
    Vercel Postgres (persistence)
    Vercel Blob (documents)
```

**Limitations:**
- ❌ No UFC context
- ❌ No MCP servers
- ❌ No specialized agents
- ❌ No access to integrations

### After (New - Dual Mode)

**API Mode (Still Available):**
```
User → Vercel → Anthropic API (same as before)
```

**Agent Mode (New Option):**
```
User → Vercel → WebSocket → NGINX → Docker Container
                                         ↓
                                    Claude Agent SDK
                                         ↓
                            ┌────────────┼────────────┐
                            ↓            ↓            ↓
                    UFC Context    MCP Servers   Integration Projects
                    (.claude/)     (Obsidian,    (freeagent_subagent/,
                                    Gmail, etc.)  linkedin-integration/, etc.)
```

## File Changes Summary

### Files to Create (8 new files)

```
claude-agent-server/
├── Dockerfile                           # NEW
├── docker-compose.yml                   # NEW
├── package.json                         # NEW
├── tsconfig.json                        # NEW
├── .env.example                         # NEW
├── .gitignore                           # NEW
├── README.md                            # NEW
└── src/
    ├── server.ts                        # NEW
    ├── logger.ts                        # NEW
    ├── auth-middleware.ts               # NEW
    ├── ufc-loader.ts                    # NEW
    └── agent-handler.ts                 # NEW

interactive-cv-website/
└── src/
    ├── lib/
    │   └── agent-client.ts              # NEW
    └── app/api/agent/token/
        └── route.ts                     # NEW

AGENT_INTEGRATION.md                     # NEW (deployment guide)
MIGRATION_PLAN.md                        # NEW (this file)
```

### Files to Modify (2 modifications)

```
interactive-cv-website/
├── src/components/ChatInterface.tsx     # MODIFY: Add agent mode toggle
└── .env.example                         # MODIFY: Add agent variables
```

### Files to Keep (Everything Else)

```
✅ .claude/agents/*.md                   # All 14 agent definitions
✅ .claude/context/**                    # All UFC context files
✅ .claude/commands/*.md                 # All slash commands
✅ freeagent_subagent/**                 # FreeAgent integration
✅ linkedin-integration/**               # LinkedIn integration
✅ health-integration/**                 # Parkrun integration
✅ location-integration/**               # Owntracks integration
✅ interactive-cv-website/**             # All other website files
```

## Volume Mounts in Docker

The Docker container mounts existing directories **read-only**:

```yaml
volumes:
  # UFC context - used by agent for system awareness
  - /home/gavin/projects/life/.claude/context:/ufc:ro

  # Agent definitions - used to invoke specialized agents
  - /home/gavin/projects/life/.claude:/claude-config:ro

  # Integration projects - used by agents for implementation
  - /home/gavin/projects/life:/projects:ro

  # Obsidian vault - used for knowledge management
  - /home/gavin/Library/.../GavinsiCloudVault:/vault:rw

  # Documents - used for document storage
  - /home/gavin/claude-documents:/documents:rw
```

**Key Point:** The agent server **reads from** your existing projects. It doesn't replace them.

## Testing Both Modes

After deployment, you can test both:

### Test API Mode (Current Functionality)

1. Visit https://www.gavinslater.com
2. Log in
3. Go to Personal Space
4. Ensure toggle shows **"API Mode"** (default)
5. Send a message
6. Response comes from Anthropic API (as before)

### Test Agent Mode (New Functionality)

1. Click the toggle to switch to **"Agent Mode"**
2. Wait for **"● Connected"** (green dot)
3. Send a message
4. Response comes from home server with full UFC context
5. Ask: "What are my active projects?" → Should know from UFC
6. Ask: "What documents do I have?" → Should list from Vercel Blob

## Migration Steps (No Data Loss)

### Phase 1: Setup (No Impact on Current System)

```bash
# Copy new agent server to home server
cd /home/gavin/projects/life
git pull  # Or scp the claude-agent-server directory

# Install dependencies
cd claude-agent-server
npm install

# Configure environment
cp .env.example .env
nano .env  # Set JWT_SECRET
```

**Impact:** None - new directory, doesn't affect existing system

### Phase 2: Deploy Agent Server (Still No Impact)

```bash
# Build and run container
docker-compose up -d --build

# Authenticate Claude CLI
docker exec -it claude-agent-server claude auth login

# Verify health
curl http://localhost:8090/health
```

**Impact:** None - agent server running locally, not yet connected to web UI

### Phase 3: Configure NGINX (Still No Impact)

- Create proxy host for `agent.gavinslater.com`
- Point to `localhost:8090`
- Enable WebSockets
- Request SSL certificate

**Impact:** None - proxy exists but web UI doesn't use it yet

### Phase 4: Update Vercel (Additive Changes Only)

```bash
# Add environment variables in Vercel dashboard
NEXT_PUBLIC_AGENT_WS_URL=wss://agent.gavinslater.com/ws
JWT_SECRET=<same-as-home-server>

# Deploy updated code
cd interactive-cv-website
git add .
git commit -m "Add agent mode support"
git push
```

**Impact:**
- ✅ API mode still works (default)
- ✅ Agent mode now available (optional)
- ✅ Users choose via toggle

### Phase 5: Test and Verify

```bash
# Test API mode (should work as before)
# Test agent mode (new functionality)
# Switch between modes (should be seamless)
```

## Rollback Plan (If Needed)

If something goes wrong, rollback is simple:

### Option 1: Keep Using API Mode

Just don't toggle to Agent Mode. The API mode is unchanged.

### Option 2: Disable Agent Mode in UI

In `ChatInterface.tsx`, hide the toggle button:

```tsx
{/* Temporarily disable agent mode */}
{false && (
  <button onClick={() => setUseAgentMode(!useAgentMode)}>
    Agent Mode
  </button>
)}
```

### Option 3: Stop Agent Server

```bash
docker-compose down
```

This stops the agent server but doesn't affect the web UI or API mode.

### Option 4: Full Rollback

```bash
# Revert code changes
cd interactive-cv-website
git revert <commit-hash>
git push

# Remove agent server
cd ../claude-agent-server
docker-compose down
cd ..
rm -rf claude-agent-server
```

**Data Safety:** No data loss because:
- Conversations stored in Vercel Postgres (unchanged)
- Documents stored in Vercel Blob (unchanged)
- Agent definitions still in `.claude/agents/` (unchanged)
- Integration projects still in place (unchanged)

## Summary: What's Actually Changing

### ✅ What Stays the Same

- All agent definitions work as before
- All integration projects remain functional
- Web UI appearance (except new toggle button)
- API mode functionality (unchanged)
- Data persistence (Vercel Postgres + Blob)
- Authentication (NextAuth)

### ➕ What's Being Added

- Agent server in Docker container
- WebSocket communication
- Full UFC context loading
- Agent mode toggle in UI
- JWT token generation
- NGINX proxy configuration

### 📝 What's Being Modified

- ChatInterface component (adds toggle and WebSocket)
- Environment variables (adds agent URL and JWT secret)

### ❌ What's Being Removed

**Nothing!** This is purely additive.

## Decision Points

Before proceeding, confirm:

1. ✅ **Keep all integration projects** - They're needed by agents
2. ✅ **Keep all agent definitions** - They're loaded by agent server
3. ✅ **Keep UFC context** - It's mounted into container
4. ✅ **Add agent server** - New capability, doesn't replace anything
5. ✅ **Modify web UI** - Adds toggle, preserves existing functionality

## Questions to Consider

### "Can I delete the integration projects since agents will handle them?"

**No.** The agents **use** the integration projects. They don't replace them.

Example: `freeagent-invoice-agent` needs the Python code in `freeagent_subagent/` to:
- Authenticate with FreeAgent OAuth
- Make API calls
- Parse responses
- Handle errors

### "Will API mode stop working?"

**No.** API mode is the **default** and remains unchanged. Agent mode is opt-in.

### "What if the agent server goes down?"

Users simply use API mode (the toggle will show connection failed). No data loss.

### "Do I need to migrate data?"

**No.** Conversations and documents are already in Vercel Postgres/Blob. Both modes use the same database.

### "Can I gradually test agent mode?"

**Yes.** You control when to toggle agent mode. API mode always available.

## Next Steps

Ready to proceed? Follow the deployment guide in [AGENT_INTEGRATION.md](file:///Users/gavinslater/projects/life/AGENT_INTEGRATION.md).

**Remember:** Nothing gets deleted. Everything stays in place. Agent server is **additive**, not **replacement**.
