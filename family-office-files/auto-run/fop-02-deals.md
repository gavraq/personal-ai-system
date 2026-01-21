# Phase 2: Deal/Transaction Management

**Features**: feat-9, feat-10, feat-11, feat-12
**Priority**: P1/P2 - Core platform functionality
**Depends on**: Phase 1 (Auth + Database)

## Pre-requisites
- [ ] Phase 1 complete (all auth features passing)
- [ ] Docker services running

## 2.1 Create Deal (feat-9)

- [ ] Create `backend/app/models/deal.py` with Deal SQLAlchemy model
- [ ] Create `backend/app/models/deal_member.py` with DealMember model
- [ ] Create `backend/app/schemas/deal.py` with Pydantic schemas
- [ ] Create `backend/app/routers/deals.py` with CRUD endpoints
- [ ] Implement POST `/api/deals` - create deal (admin/partner only)
- [ ] Auto-assign creator as deal member
- [ ] Generate UUID for deal ID
- [ ] Default status: 'draft'
- [ ] Test: Create deal with valid data returns 201
- [ ] Test: Create deal without title returns 400
- [ ] Test: Viewer cannot create deal (403)
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-9 passing`

## 2.2 Edit Deal Metadata (feat-10)

- [ ] Implement PUT `/api/deals/{deal_id}` endpoint
- [ ] Allow updating: title, description, status
- [ ] Verify user is deal member or admin
- [ ] Add updated_at timestamp on change
- [ ] Create audit log entry for changes
- [ ] Test: Edit deal title persists on refresh
- [ ] Test: Non-member cannot edit (403)
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-10 passing`

## 2.3 Deal Permissions (feat-11)

- [ ] Implement POST `/api/deals/{deal_id}/members` - add member
- [ ] Implement DELETE `/api/deals/{deal_id}/members/{user_id}` - remove member
- [ ] Implement GET `/api/deals/{deal_id}/members` - list members
- [ ] Support optional role_override per deal member
- [ ] Filter GET `/api/deals` to only return user's accessible deals
- [ ] Admin can access all deals regardless of membership
- [ ] Test: Add member grants deal access
- [ ] Test: Remove member revokes access
- [ ] Test: Non-member cannot access deal (403)
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-11 passing`

## 2.4 Deal Status Workflow (feat-12)

- [ ] Define status enum: draft, active, closed
- [ ] Implement status transition validation (draft→active→closed)
- [ ] Closed deals become read-only (no uploads, no edits)
- [ ] Track status history in audit_log
- [ ] Test: Change status from Draft to Active
- [ ] Test: Upload to Closed deal returns 403
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-12 passing`

## 2.5 Deal Frontend UI

- [ ] Create `frontend/app/deals/page.tsx` - deal listing
- [ ] Create `frontend/app/deals/[id]/page.tsx` - deal detail
- [ ] Create `frontend/components/deals/DealCard.tsx` - deal card component
- [ ] Create `frontend/components/deals/CreateDealModal.tsx` - create form
- [ ] Create `frontend/components/deals/EditDealModal.tsx` - edit form
- [ ] Create `frontend/components/deals/MemberManager.tsx` - manage members
- [ ] Add deal status badge with color coding
- [ ] Test: Deal cards display on listing page
- [ ] Test: Create deal modal works end-to-end
- [ ] Test: Edit deal updates in real-time

## Phase 2 Completion

- [ ] All 4 features (feat-9, feat-10, feat-11, feat-12) marked as passing
- [ ] Can create, edit, and manage deals via UI
- [ ] Deal permissions working (members only see assigned deals)
- [ ] Status workflow enforced
- [ ] Run `bun .claude/skills/CORE/Tools/FeatureRegistry.ts verify family-office-files` to confirm
