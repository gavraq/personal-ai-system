# Phase 2: Deal/Transaction Management

**Features**: feat-9, feat-10, feat-11, feat-12
**Priority**: P1/P2 - Core platform functionality
**Depends on**: Phase 1 (Auth + Database)

## Pre-requisites
- [x] Phase 1 complete (all auth features passing) ✅ Verified auth endpoints work (register, login, JWT tokens)
- [x] Docker services running ✅ Backend, DB, Redis all running

## 2.1 Create Deal (feat-9)

- [x] Create `backend/app/models/deal.py` with Deal SQLAlchemy model ✅ Already existed, fixed enum handling
- [x] Create `backend/app/models/deal_member.py` with DealMember model ✅ Already existed in deal.py
- [x] Create `backend/app/schemas/deal.py` with Pydantic schemas ✅ Created with DealCreate, DealUpdate, DealResponse, etc.
- [x] Create `backend/app/routers/deals.py` with CRUD endpoints ✅ Created with all endpoints
- [x] Implement POST `/api/deals` - create deal (admin/partner only) ✅ Verified via curl
- [x] Auto-assign creator as deal member ✅ Verified via GET /api/deals/{id}/members
- [x] Generate UUID for deal ID ✅ UUID generated automatically
- [x] Default status: 'draft' ✅ Confirmed in response
- [x] Test: Create deal with valid data returns 201 ✅ Test written + API verified
- [x] Test: Create deal without title returns 400 ✅ Returns 422 (Pydantic validation)
- [x] Test: Viewer cannot create deal (403) ✅ Test written + API verified
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-9 passing`

## 2.2 Edit Deal Metadata (feat-10)

- [x] Implement PUT `/api/deals/{deal_id}` endpoint ✅ Implemented
- [x] Allow updating: title, description, status ✅ All three supported
- [x] Verify user is deal member or admin ✅ Access check implemented
- [x] Add updated_at timestamp on change ✅ Model has onupdate=datetime.utcnow
- [ ] Create audit log entry for changes (deferred - requires audit log implementation)
- [x] Test: Edit deal title persists on refresh ✅ Test written
- [x] Test: Non-member cannot edit (403) ✅ Test written
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-10 passing`

## 2.3 Deal Permissions (feat-11)

- [x] Implement POST `/api/deals/{deal_id}/members` - add member ✅ Implemented
- [x] Implement DELETE `/api/deals/{deal_id}/members/{user_id}` - remove member ✅ Implemented
- [x] Implement GET `/api/deals/{deal_id}/members` - list members ✅ Implemented + verified via curl
- [x] Support optional role_override per deal member ✅ Implemented in schema and model
- [x] Filter GET `/api/deals` to only return user's accessible deals ✅ Implemented with membership check
- [x] Admin can access all deals regardless of membership ✅ Implemented via UserRole.ADMIN check
- [x] Test: Add member grants deal access ✅ Test written
- [x] Test: Remove member revokes access ✅ Test written
- [x] Test: Non-member cannot access deal (403) ✅ Test written
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-11 passing`

## 2.4 Deal Status Workflow (feat-12)

- [x] Define status enum: draft, active, closed ✅ DealStatus enum in model + DealStatusEnum in schemas
- [x] Implement status transition validation (draft→active→closed) ✅ Implemented in update_deal
- [x] Closed deals become read-only (no uploads, no edits) ✅ Implemented check in update_deal
- [ ] Track status history in audit_log (deferred - requires audit log implementation)
- [x] Test: Change status from Draft to Active ✅ Test written
- [ ] Test: Upload to Closed deal returns 403 (deferred - requires file upload implementation)
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
