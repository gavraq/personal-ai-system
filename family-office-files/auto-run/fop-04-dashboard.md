# Phase 4: Dashboard & Activity

**Features**: feat-5, feat-6, feat-7, feat-8
**Priority**: P2 - User experience
**Depends on**: Phase 3 (Files)

## Pre-requisites
- [x] Phase 3 complete (files working) ✓ All 6 features (feat-13 through feat-18) verified passing
- [x] Deals and files populated for testing ✓ Test infrastructure in place (test_deals.py, test_files.py)

## 4.1 Deal Overview Cards (feat-5)

- [x] Create `frontend/app/dashboard/page.tsx` as main dashboard ✓ Already exists with full implementation
- [x] Create `frontend/components/dashboard/DealCard.tsx` component ✓ Located at `frontend/components/deals/DealCard.tsx`
- [x] Display: title, status badge, file count, last activity date ✓ All fields displayed in DealCard component
- [x] Filter cards by user's deal access permissions ✓ Backend filters via DealMember join for non-admin users
- [x] Click card navigates to `/deals/{id}` ✓ Uses Next.js Link component with dynamic href
- [x] Status badge colors: draft=gray, active=green, closed=red ✓ StatusBadge.tsx has correct color mapping
- [x] Sort deals by last activity (most recent first) ✓ Backend orders by updated_at desc nullslast, then created_at desc
- [x] Test: Dashboard loads with all accessible deal cards ✓ test_dashboard_loads_with_deal_cards in test_deals.py
- [x] Test: Click card navigates to deal detail ✓ DealCard.test.tsx verifies Link href attribute
- [x] Test: Only assigned deals visible (permission filtering) ✓ test_only_assigned_deals_visible_for_viewer in test_deals.py
- [x] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-5 passing` ✓ Registry updated

## 4.2 Recent Activity Feed (feat-6)

- [x] Create `backend/app/models/activity.py` with Activity model ✓ Activity model already exists in `backend/app/models/audit.py`
- [x] Log activities: file_upload, file_link, deal_create, deal_update, agent_run ✓ Added `log_activity()` helper in activity.py, integrated into deals.py and files.py routers
- [x] Implement GET `/api/activity` - paginated activity feed ✓ `backend/app/routers/activity.py` with list and listForDeal endpoints
- [x] Filter by user's accessible deals ✓ `get_user_accessible_deal_ids()` filters by DealMember for non-admin users
- [x] Include: actor name, action type, target, timestamp ✓ ActivityResponse schema includes actor_email, action, details, created_at
- [x] Create `frontend/components/dashboard/ActivityFeed.tsx` component ✓ Full implementation with loading states, error handling, auto-refresh
- [x] Show actor avatar, action description, relative timestamp ✓ ActivityAvatar component, getActivityDescription(), formatRelativeTime()
- [x] Auto-refresh every 30 seconds or use WebSocket ✓ useEffect with setInterval at configurable refreshInterval (default 30s)
- [x] Test: Activity appears after file upload within 5s ✓ `test_activity_logged_on_file_upload` in test_activity.py
- [x] Test: Only shows activity from accessible deals ✓ `test_activity_feed_only_shows_accessible_deals` in test_activity.py
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
