# Phase 7: Browser Testing (Claude Browser Tool)

**Features**: feat-29, feat-30, feat-31, feat-32, feat-33
**Priority**: P3 - Verification
**Depends on**: All previous phases complete

> **⚠️ IMPORTANT: Manual Testing Phase**
>
> This phase requires the **Claude Browser Tool Chrome Extension** for interactive browser testing.
> CLI-based agents cannot perform these tasks - they require a human with:
> - A Chrome browser with Claude Browser Tool installed
> - Docker services running locally
> - Access to the test environment at localhost:3000/8000
>
> **To start the environment:**
> ```bash
> cd /Users/gavinslater/projects/life/family-office-files
> docker compose up -d
> ```
>
> **To create test users (after services are up):**
> ```bash
> # Run from backend container or with proper Python environment
> python -c "from app.core.security import get_password_hash; print(get_password_hash('testpassword123'))"
> # Then insert users into PostgreSQL
> ```

## Pre-requisites
- [x] All phases 1-6 complete (verified: Phases 1-6 have all core tasks complete, only deferred/optional items remain)
- [ ] Docker services running *(requires manual: `docker compose up -d`)*
- [ ] Claude Browser Tool extension installed *(requires Chrome browser with extension)*
- [ ] Test user accounts created (admin, partner, viewer) *(requires database seeding)*

## Test Environment Setup

- [ ] Ensure frontend running at `http://localhost:3000`
- [ ] Ensure backend running at `http://localhost:8000`
- [ ] Seed database with test data:
  - 3 users (admin@test.com, partner@test.com, viewer@test.com)
  - 2 deals with files
  - Agent run history
- [ ] Document test credentials in `.env.test`

## 7.1 Browser Test: Dashboard Loads (feat-29)

**Using Claude Browser Tool:**

- [ ] Navigate to `http://localhost:3000`
- [ ] Verify login page or dashboard loads (depending on auth state)
- [ ] Check browser console for JavaScript errors (should be none)
- [ ] Verify page load time < 3 seconds
- [ ] Take screenshot for verification
- [ ] Test responsive: resize to mobile width, verify layout adapts
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-29 passing`

## 7.2 Browser Test: Login Flow (feat-30)

**Using Claude Browser Tool:**

- [ ] Navigate to `http://localhost:3000/login`
- [ ] Verify login form is visible with email and password fields
- [ ] Enter email: `admin@test.com`
- [ ] Enter password: `testpassword123`
- [ ] Click "Sign In" button
- [ ] Verify redirect to `/dashboard`
- [ ] Verify user name displayed in header
- [ ] Verify deal cards are visible
- [ ] Test invalid login: wrong password shows error message
- [ ] Test logout: click logout, verify redirect to login
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-30 passing`

## 7.3 Browser Test: Create Deal Flow (feat-31)

**Using Claude Browser Tool:**

- [ ] Login as admin user
- [ ] Navigate to dashboard
- [ ] Click "Create Deal" button
- [ ] Verify modal opens with form
- [ ] Enter title: "Test Deal from Browser"
- [ ] Enter description: "Created via Claude Browser Tool test"
- [ ] Click "Create" button
- [ ] Verify modal closes
- [ ] Verify new deal card appears on dashboard
- [ ] Click the new deal card
- [ ] Verify deal detail page loads with correct title
- [ ] Verify deal status shows "Draft"
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-31 passing`

## 7.4 Browser Test: Drive Picker Flow (feat-32)

**Using Claude Browser Tool:**

- [ ] Login as user with Google Drive connected
- [ ] Navigate to a deal detail page
- [ ] Click "Link from Drive" button
- [ ] Verify Google Picker modal opens
- [ ] (Note: May need to mock for automated test, or use real Drive)
- [ ] Select a file in the picker
- [ ] Click "Select" button
- [ ] Verify picker closes
- [ ] Verify file appears in deal's file list
- [ ] Verify file shows Drive icon indicator
- [ ] Click file to test preview
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-32 passing`

## 7.5 Browser Test: Agent Interaction (feat-33)

**Using Claude Browser Tool:**

- [ ] Login and navigate to a deal detail page
- [ ] Click "Agents" tab or open agent panel
- [ ] Select "Market Research" agent
- [ ] Enter query: "Tech sector investment trends"
- [ ] Click "Submit" or press Enter
- [ ] Verify loading indicator appears
- [ ] Wait for response (may take 10-30 seconds)
- [ ] Verify response displays with structured output
- [ ] Verify response includes sections: overview, trends, opportunities
- [ ] Refresh page
- [ ] Verify previous query and response still visible in history
- [ ] Test Document Analysis agent with a file
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-33 passing`

## 7.6 Role-Based UI Testing

**Using Claude Browser Tool:**

- [ ] Login as Viewer (viewer@test.com)
- [ ] Verify "Create Deal" button is NOT visible
- [ ] Verify "Upload File" button is NOT visible
- [ ] Verify can view deal details (read-only)
- [ ] Verify can run agents (read operation)
- [ ] Login as Partner (partner@test.com)
- [ ] Verify "Create Deal" button IS visible
- [ ] Verify "Upload File" button IS visible
- [ ] Verify can create and edit deals assigned to them
- [ ] Login as Admin (admin@test.com)
- [ ] Verify can access Users management
- [ ] Verify can access Audit Log

## 7.7 End-to-End Scenario Test

**Complete workflow using Claude Browser Tool:**

1. [ ] Login as Admin
2. [ ] Create new deal "E2E Test Deal"
3. [ ] Add Partner user as deal member
4. [ ] Upload a test PDF file
5. [ ] Run Document Analysis agent on the file
6. [ ] Verify analysis results display
7. [ ] Change deal status to Active
8. [ ] Logout
9. [ ] Login as Partner
10. [ ] Verify can see "E2E Test Deal"
11. [ ] Verify can see uploaded file and analysis
12. [ ] Run Market Research agent
13. [ ] Verify results display
14. [ ] Logout
15. [ ] Login as Viewer
16. [ ] Verify cannot upload to the deal
17. [ ] Verify can view files and agent results

## Phase 7 Completion

- [ ] All 5 features (feat-29 through feat-33) marked as passing
- [ ] All browser tests pass via Claude Browser Tool
- [ ] End-to-end scenario completes successfully
- [ ] Screenshots captured for documentation
- [ ] Run `bun .claude/skills/CORE/Tools/FeatureRegistry.ts verify family-office-files` to confirm

## Final Verification

- [ ] Run full registry verification:
  ```bash
  bun .claude/skills/CORE/Tools/FeatureRegistry.ts verify family-office-files
  ```
- [ ] Confirm output shows: "✅ ALL FEATURES PASSING - Ready for completion"
- [ ] All 35 features in passing state
- [ ] Platform ready for demo
