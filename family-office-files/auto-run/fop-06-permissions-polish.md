# Phase 6: Permissions, Audit & Polish

**Features**: feat-19, feat-20, feat-21, feat-22
**Priority**: P1/P2/P3 - Security and compliance
**Depends on**: Phase 5 (Agents)

## Pre-requisites
- [ ] Phase 5 complete (agents working)
- [ ] Multiple test users with different roles created

## 6.1 Role-Based Access Control (feat-19)

- [ ] Audit all API endpoints for role enforcement
- [ ] Create `backend/app/core/permissions.py` with role checking utilities
- [ ] Implement role hierarchy: Admin > Partner > Viewer
- [ ] Create role-based route decorators
- [ ] Verify UI elements hidden based on role
- [ ] Document permission matrix in README
- [ ] Test: Viewer API restrictions (403 on write operations)
- [ ] Test: UI reflects role (buttons hidden/disabled)
- [ ] Test: Admin can do everything
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-19 passing`

## 6.2 Deal-Level Permissions (feat-20)

- [ ] Verify deal membership checks on all deal endpoints
- [ ] Implement deal-level role override (e.g., Partner on one deal, Viewer on another)
- [ ] Admin bypass for all deals
- [ ] Test: Unassigned user cannot access deal (403)
- [ ] Test: Admin can access all deals
- [ ] Test: Deal-level role override works
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-20 passing`

## 6.3 File-Level Permissions (feat-21)

- [ ] Implement file_shares table for cross-FO sharing
- [ ] Implement POST `/api/files/{file_id}/share` - share with user
- [ ] Implement DELETE `/api/files/{file_id}/share/{user_id}` - revoke share
- [ ] Check file_shares before allowing file access
- [ ] Share permission levels: view, download, edit
- [ ] Test: Share file with external user grants access
- [ ] Test: Revoke share removes access
- [ ] Test: Shared files visible in recipient's file list
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-21 passing`

## 6.4 Permission Audit Log (feat-22)

- [ ] Create `backend/app/core/audit.py` for audit logging
- [ ] Log all permission changes: role changes, deal membership, file shares
- [ ] Audit entry: actor_id, action, entity_type, entity_id, old_value, new_value, timestamp
- [ ] Make audit entries immutable (no UPDATE/DELETE)
- [ ] Implement GET `/api/audit` - paginated audit log (Admin only)
- [ ] Create `frontend/app/admin/audit/page.tsx` for viewing audit log
- [ ] Filter by: action type, actor, entity, date range
- [ ] Test: Role change creates audit entry
- [ ] Test: Audit log visible to Admins
- [ ] Test: Audit entries cannot be modified
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-22 passing`

## 6.5 Error Handling & Edge Cases

- [ ] Implement global error handler in FastAPI
- [ ] Consistent error response format: {error, message, details}
- [ ] Handle: 400 (validation), 401 (auth), 403 (permission), 404 (not found), 500 (server)
- [ ] Frontend error boundary component
- [ ] Toast notifications for errors
- [ ] Retry logic for transient failures

## 6.6 Performance & Optimization

- [ ] Add database indexes for common queries
- [ ] Implement pagination on all list endpoints
- [ ] Add Redis caching for frequently accessed data
- [ ] Optimize N+1 queries with eager loading
- [ ] Add API response compression

## 6.7 Documentation

- [ ] Create `README.md` with setup instructions
- [ ] Document API endpoints in OpenAPI (FastAPI auto-generates)
- [ ] Create `DEPLOYMENT.md` for production deployment
- [ ] Document environment variables
- [ ] Add inline code comments for complex logic

## Phase 6 Completion

- [ ] All 4 features (feat-19, feat-20, feat-21, feat-22) marked as passing
- [ ] Complete permission system working
- [ ] Audit log functional
- [ ] Error handling robust
- [ ] Documentation complete
- [ ] Run `bun .claude/skills/CORE/Tools/FeatureRegistry.ts verify family-office-files` to confirm
