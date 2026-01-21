# Phase 4: Dashboard & Activity

**Features**: feat-5, feat-6, feat-7, feat-8
**Priority**: P2 - User experience
**Depends on**: Phase 3 (Files)

## Pre-requisites
- [ ] Phase 3 complete (files working)
- [ ] Deals and files populated for testing

## 4.1 Deal Overview Cards (feat-5)

- [ ] Create `frontend/app/dashboard/page.tsx` as main dashboard
- [ ] Create `frontend/components/dashboard/DealCard.tsx` component
- [ ] Display: title, status badge, file count, last activity date
- [ ] Filter cards by user's deal access permissions
- [ ] Click card navigates to `/deals/{id}`
- [ ] Status badge colors: draft=gray, active=green, closed=red
- [ ] Sort deals by last activity (most recent first)
- [ ] Test: Dashboard loads with all accessible deal cards
- [ ] Test: Click card navigates to deal detail
- [ ] Test: Only assigned deals visible (permission filtering)
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-5 passing`

## 4.2 Recent Activity Feed (feat-6)

- [ ] Create `backend/app/models/activity.py` with Activity model
- [ ] Log activities: file_upload, file_link, deal_create, deal_update, agent_run
- [ ] Implement GET `/api/activity` - paginated activity feed
- [ ] Filter by user's accessible deals
- [ ] Include: actor name, action type, target, timestamp
- [ ] Create `frontend/components/dashboard/ActivityFeed.tsx` component
- [ ] Show actor avatar, action description, relative timestamp
- [ ] Auto-refresh every 30 seconds or use WebSocket
- [ ] Test: Activity appears after file upload within 5s
- [ ] Test: Only shows activity from accessible deals
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-6 passing`

## 4.3 Agent Output Summaries (feat-7)

- [ ] Create `frontend/components/dashboard/AgentSummaryCard.tsx`
- [ ] Display latest agent result per agent type per deal
- [ ] Show: agent type icon, summary excerpt, timestamp
- [ ] Expandable to view full output in modal
- [ ] Quick re-run button on card
- [ ] Test: Agent summary displays after agent run
- [ ] Test: Expand shows full output
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-7 passing`

## 4.4 Quick Actions (feat-8)

- [ ] Create `frontend/components/dashboard/QuickActions.tsx` component
- [ ] "Create Deal" button - opens CreateDealModal (Admin/Partner)
- [ ] "Upload File" button - opens file picker with deal selector (Admin/Partner)
- [ ] "Run Agent" dropdown - agent type selector (all roles)
- [ ] Respect role permissions (hide buttons for unauthorized)
- [ ] Keyboard shortcuts: Cmd+N (new deal), Cmd+U (upload)
- [ ] Test: All buttons visible for Admin
- [ ] Test: Viewer only sees Run Agent
- [ ] Test: Create Deal opens modal
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-8 passing`

## 4.5 Dashboard Layout

- [ ] Create responsive grid layout: sidebar + main content
- [ ] Sidebar: navigation, user profile, quick stats
- [ ] Main: deal cards grid + activity feed sidebar
- [ ] Mobile responsive (cards stack, activity below)
- [ ] Header: logo, search, notifications, user menu
- [ ] Dark/light mode toggle (optional P3)

## Phase 4 Completion

- [ ] All 4 features (feat-5, feat-6, feat-7, feat-8) marked as passing
- [ ] Dashboard displays deal cards, activity feed, agent summaries
- [ ] Quick actions working with role-based visibility
- [ ] Responsive layout functional
- [ ] Run `bun .claude/skills/CORE/Tools/FeatureRegistry.ts verify family-office-files` to confirm
