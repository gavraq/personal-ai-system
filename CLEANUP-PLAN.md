# Life Project Cleanup Plan

**Date**: January 12, 2026
**Status**: Planning Phase
**Goal**: Remove agent server and risk-agents-app while retaining file upload functionality

---

## Executive Summary

This plan outlines the cleanup of the Life project to:
1. Remove the claude-agent-server from Docker orchestration
2. Remove the risk-agents-app directory
3. Keep the file upload functionality on the interactive-cv-website
4. Archive/remove outdated migration documentation
5. Update documentation to reflect the simplified architecture

---

## Current State Analysis

### What EXISTS and Needs REVIEW

#### Documentation Files (Migration Era)
| File | Lines | Purpose | Recommendation |
|------|-------|---------|----------------|
| `MIGRATION_PLAN.md` | 981 | Original microservices migration plan | **DELETE** - Historical, migration complete |
| `MIGRATION-PLAN.md` | 886 | Duplicate/newer migration plan | **DELETE** - Historical, migration complete |
| `AGENT_INTEGRATION.md` | 575 | Agent server deployment guide | **DELETE** - Agent server being removed |
| `ARCHITECTURE_COMPARISON.md` | 482 | Before/after architecture comparison | **DELETE** - Historical |
| `COMPREHENSIVE_ARCHITECTURE_PLAN.md` | 1578 | Full architecture planning doc | **DELETE** - Historical |
| `risk-agents-app-implementation-plan.md` | 1790 | Risk agents app development plan | **DELETE** - App being removed |
| `NETWORK_CONFIGURATION.md` | ~400 | Network setup documentation | **REVIEW** - May have useful reference info |

#### Services Directory
| Service | Status | Action |
|---------|--------|--------|
| `services/claude-agent-server/` | Running | **REMOVE** from docker-compose, **KEEP** directory for now |
| `services/health-service/` | Running | **KEEP** - Active production service |
| `services/interactive-cv-website/` | Running (Vercel) | **MODIFY** - Remove agent mode, keep file upload |
| `services/energy-service/` | Development | **KEEP** - Active development |
| `services/thames-water-service/` | Running | **KEEP** - Active production service |
| `services/streamscope/` | Development | **KEEP** - Active development |

#### Risk Agents App
| Directory | Size | Action |
|-----------|------|--------|
| `risk-agents-app/` | ~2.5MB (69 docs) | **ARCHIVE** then **DELETE** |
| `risk-agents-app/backend/` | Full Python backend | Part of archive |
| `risk-agents-app/frontend/` | Full Next.js frontend | Part of archive |
| `risk-agents-app/docs/` | 7 learning modules | Part of archive |

---

## Phase 1: Documentation Cleanup

### 1.1 Files to DELETE (Obsolete Migration Docs)

```bash
# Migration-era documentation - no longer needed
/Users/gavinslater/projects/life/MIGRATION_PLAN.md
/Users/gavinslater/projects/life/MIGRATION-PLAN.md
/Users/gavinslater/projects/life/AGENT_INTEGRATION.md
/Users/gavinslater/projects/life/ARCHITECTURE_COMPARISON.md
/Users/gavinslater/projects/life/COMPREHENSIVE_ARCHITECTURE_PLAN.md
/Users/gavinslater/projects/life/risk-agents-app-implementation-plan.md
```

### 1.2 Files to REVIEW

```bash
# May contain useful network reference info
/Users/gavinslater/projects/life/NETWORK_CONFIGURATION.md
```

---

## Phase 2: Remove Agent Server from Docker

### 2.1 Update docker-compose.yml

**Remove** the `claude-agent-server` service block (lines 83-148):
- Service definition
- Port mappings (3002)
- Volume mounts for UFC context
- Environment variables (ANTHROPIC_API_KEY, JWT_SECRET)
- Network assignment (172.20.0.20)
- Health checks
- Dependency from nginx service

**Update** nginx service:
- Remove `claude-agent-server` from `depends_on`
- Update comments to reflect removed service

**Update** header comments:
- Remove reference to claude-agent-server in services list
- Update external URLs section

### 2.2 Update NGINX Configuration

If `/config/nginx/` exists with proxy configurations:
- Remove `agent.gavinslater.com` proxy host configuration
- Keep other proxy hosts (health, location, water)

### 2.3 DNS/External Changes (Manual)

After deployment:
- Consider removing `agent.gavinslater.com` DNS record
- Or redirect to main site

---

## Phase 3: Modify Interactive CV Website

### 3.1 Personal Page Modification

**File**: `services/interactive-cv-website/src/app/personal/page.tsx`

**Current**: Shows both ChatInterface and DocumentUpload
**Target**: Show only DocumentUpload (full width)

```tsx
// BEFORE: Grid with 2:1 ratio
<div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-200px)]">
  <div className="lg:col-span-2 h-full">
    <ChatInterface />  // REMOVE
  </div>
  <div className="lg:col-span-1 h-full">
    <DocumentUpload />
  </div>
</div>

// AFTER: Full width DocumentUpload
<div className="h-[calc(100vh-200px)]">
  <DocumentUpload />
</div>
```

### 3.2 Files to REMOVE from Interactive CV Website

```
services/interactive-cv-website/src/
├── components/ChatInterface.tsx           # DELETE - Agent chat UI
├── lib/agent-client.ts                    # DELETE - Agent WebSocket client
├── app/api/agent/token/route.ts           # DELETE - JWT token generation
├── app/api/chat/route.ts                  # REVIEW - May be used for non-agent chat
├── app/api/conversations/route.ts         # REVIEW - May be used for persistence
├── app/api/conversations/[id]/messages/route.ts  # REVIEW - May be used
```

### 3.3 Files to KEEP (Document Upload)

```
services/interactive-cv-website/src/
├── components/DocumentUpload.tsx          # KEEP - File upload UI
├── app/api/documents/route.ts             # KEEP - Document CRUD
├── app/api/documents/[filename]/route.ts  # KEEP - File download
├── app/api/documents/save-metadata/route.ts  # KEEP - Metadata storage
├── app/api/upload/route.ts                # KEEP - File upload
├── app/api/upload-token/route.ts          # KEEP - Vercel Blob tokens
├── lib/db.ts                              # KEEP - Database utilities
├── lib/auth.ts                            # KEEP - Authentication
```

### 3.4 Environment Variables to Remove

From Vercel dashboard for interactive-cv-website:
- `NEXT_PUBLIC_AGENT_WS_URL` - No longer needed
- `JWT_SECRET` - No longer needed for agent auth (may still be used for NextAuth)

---

## Phase 4: Archive and Remove Risk Agents App

### 4.1 Archive Decision

**Option A**: Create git archive before deletion
```bash
cd /Users/gavinslater/projects/life
git archive --format=zip HEAD:risk-agents-app > risk-agents-app-archive-2026-01-12.zip
# Move to backup location
mv risk-agents-app-archive-2026-01-12.zip ~/backups/
```

**Option B**: Just delete (it's in git history if needed)
```bash
rm -rf risk-agents-app/
```

**Recommendation**: Option B - git history preserves it

### 4.2 Remove Risk Agents App Directory

```bash
rm -rf /Users/gavinslater/projects/life/risk-agents-app/
```

---

## Phase 5: Update Main Documentation

### 5.1 Update CLAUDE.md

- Remove references to claude-agent-server
- Remove Agent Delegation Protocol sections
- Update Specialized Agents Portfolio (remove agent-server references)
- Update Conditional Loading section (remove agent-server paths)
- Simplify architecture description

### 5.2 Update README.md

- Remove claude-agent-server from Microservices table
- Remove agent.gavinslater.com from URLs
- Update Architecture section
- Remove Agent Mode references

### 5.3 Update .claude/context/tools/CLAUDE.md

- Remove agent-server related tool context
- Update available tools list

---

## Phase 6: Service Directory Cleanup (Optional)

### 6.1 Claude Agent Server Directory

**Decision needed**:
- **Option A**: Keep `services/claude-agent-server/` for potential future use
- **Option B**: Delete entirely

**Recommendation**: Option A (keep for now) - can revisit later

### 6.2 Daily Brief System

The `services/claude-agent-server/daily-brief-system/` contains useful news curation code.

**Decision needed**:
- Move to `integrations/daily-brief/` if keeping
- Or delete with claude-agent-server

---

## Implementation Order

### Step 1: Create Backup (Safety)
```bash
cd /Users/gavinslater/projects/life
git add -A
git commit -m "Checkpoint before cleanup: agent server and risk-agents removal"
```

### Step 2: Delete Obsolete Documentation
- Delete 6 migration-era markdown files
- Total: ~6,000+ lines of outdated docs

### Step 3: Update docker-compose.yml
- Remove claude-agent-server service
- Update nginx dependencies
- Update comments

### Step 4: Modify Interactive CV Website
- Update personal/page.tsx
- Remove ChatInterface.tsx
- Remove agent-client.ts
- Remove agent token route
- Review and potentially remove chat/conversations routes

### Step 5: Remove Risk Agents App
- Delete entire risk-agents-app/ directory

### Step 6: Update Main Documentation
- CLAUDE.md updates
- README.md updates
- Context file updates

### Step 7: Commit and Deploy
```bash
git add -A
git commit -m "feat: Remove agent server and risk-agents-app, simplify architecture

- Remove claude-agent-server from docker-compose
- Remove ChatInterface from personal space (keep DocumentUpload)
- Delete obsolete migration documentation
- Delete risk-agents-app directory
- Update documentation to reflect simplified architecture

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

git push origin main
```

### Step 8: Vercel Deployment
- Remove NEXT_PUBLIC_AGENT_WS_URL environment variable
- Redeploy interactive-cv-website

### Step 9: Pi Server Updates
- Pull latest docker-compose.yml
- Stop claude-agent-server container
- Remove from running containers

---

## Files Changed Summary

### DELETE (Documentation - 6 files, ~6,000 lines)
- MIGRATION_PLAN.md
- MIGRATION-PLAN.md
- AGENT_INTEGRATION.md
- ARCHITECTURE_COMPARISON.md
- COMPREHENSIVE_ARCHITECTURE_PLAN.md
- risk-agents-app-implementation-plan.md

### DELETE (Risk Agents App - entire directory)
- risk-agents-app/ (~2.5MB, 69 docs, full stack app)

### DELETE (Interactive CV Website - 3 files)
- src/components/ChatInterface.tsx
- src/lib/agent-client.ts
- src/app/api/agent/token/route.ts

### MODIFY (4 files)
- docker-compose.yml (remove claude-agent-server service)
- services/interactive-cv-website/src/app/personal/page.tsx
- CLAUDE.md (remove agent references)
- README.md (remove agent references)

### REVIEW (3 files - may need removal)
- services/interactive-cv-website/src/app/api/chat/route.ts
- services/interactive-cv-website/src/app/api/conversations/route.ts
- services/interactive-cv-website/src/app/api/conversations/[id]/messages/route.ts

---

## Rollback Plan

If issues arise:
```bash
# Revert to checkpoint
git revert HEAD

# Or restore specific files
git checkout HEAD~1 -- docker-compose.yml
git checkout HEAD~1 -- services/interactive-cv-website/
```

---

## Post-Cleanup Verification

### Checklist
- [ ] docker-compose.yml builds successfully
- [ ] Health service still accessible
- [ ] Thames water service still accessible
- [ ] Owntracks still accessible
- [ ] Interactive CV website deploys successfully
- [ ] Personal space shows DocumentUpload only
- [ ] File upload still works
- [ ] File download still works
- [ ] No broken links in documentation
- [ ] CLAUDE.md accurately reflects current architecture
- [ ] README.md accurately reflects current architecture

---

## Questions for User

1. **Risk Agents App**: Archive to zip file before deletion, or just delete (git history preserves it)?

2. **Claude Agent Server Directory**: Keep `services/claude-agent-server/` for potential future use, or delete entirely?

3. **Daily Brief System**: The news curation code in claude-agent-server - move to integrations/ or delete?

4. **Chat/Conversations APIs**: Are these used by anything other than the agent? Should they be removed too?

5. **NETWORK_CONFIGURATION.md**: Delete or keep for reference?

---

**Plan Version**: 1.0
**Created**: January 12, 2026
**Author**: Claude Opus 4.5
