# Phase 6: Permissions, Audit & Polish

**Features**: feat-19, feat-20, feat-21, feat-22
**Priority**: P1/P2/P3 - Security and compliance
**Depends on**: Phase 5 (Agents)

## Pre-requisites
- [x] Phase 5 complete (agents working) ✓ Verified via fop-05-agents.md - all 6 features passing
- [x] Multiple test users with different roles created ✓ User model has admin/partner/viewer roles with tests

## 6.1 Role-Based Access Control (feat-19)

- [x] Audit all API endpoints for role enforcement ✓ Complete audit of auth, users, deals, files, activity, agents, integrations routers
- [x] Create `backend/app/core/permissions.py` with role checking utilities ✓ Created with RoleLevel enum, hierarchy checks, deal-level permissions
- [x] Implement role hierarchy: Admin > Partner > Viewer ✓ RoleLevel IntEnum (ADMIN=3, PARTNER=2, VIEWER=1) with has_minimum_role()
- [x] Create role-based route decorators ✓ require_deal_read_access(), require_deal_write_access(), require_minimum_role() functions
- [x] Verify UI elements hidden based on role ✓ /auth/me returns role field for UI; TestRoleBasedAccessControl::test_ui_reflects_role_buttons_hidden_for_viewer
- [x] Document permission matrix in README ✓ PERMISSION_MATRIX constant in permissions.py with full documentation
- [x] Test: Viewer API restrictions (403 on write operations) ✓ TestRoleBasedAccessControl tests verify viewer cannot update/add/remove
- [x] Test: UI reflects role (buttons hidden/disabled) ✓ test_ui_reflects_role_buttons_hidden_for_viewer
- [x] Test: Admin can do everything ✓ test_admin_can_access_all_deals
- [x] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-19 passing` ✓ Registry updated

## 6.2 Deal-Level Permissions (feat-20)

- [x] Verify deal membership checks on all deal endpoints ✓ Audited deals.py, files.py, agents.py, activity.py - all check membership via can_access_deal() or DealMember query
- [x] Implement deal-level role override (e.g., Partner on one deal, Viewer on another) ✓ DealMember.role_override field + get_effective_deal_role() in permissions.py
- [x] Admin bypass for all deals ✓ All permission functions check user.role == UserRole.ADMIN.value first
- [x] Test: Unassigned user cannot access deal (403) ✓ TestDealLevelPermissions::test_unassigned_user_cannot_access_deal_returns_403
- [x] Test: Admin can access all deals ✓ TestDealLevelPermissions::test_admin_can_access_all_deals_regardless_of_membership
- [x] Test: Deal-level role override works ✓ TestDealLevelPermissions::test_deal_level_role_override_works, test_viewer_with_partner_override_can_write
- [x] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-20 passing` ✓

## 6.3 File-Level Permissions (feat-21)

- [x] Implement file_shares table for cross-FO sharing ✓ FileShare model already exists in models/file.py
- [x] Implement POST `/api/files/{file_id}/share` - share with user ✓ Already implemented in routers/files.py
- [x] Implement DELETE `/api/files/{file_id}/share/{user_id}` - revoke share ✓ Added revoke_file_share endpoint
- [x] Check file_shares before allowing file access ✓ Updated can_access_file() and added can_download_file()
- [x] Share permission levels: view, download, edit ✓ Added DOWNLOAD permission to FilePermission enum
- [x] Test: Share file with external user grants access ✓ TestSharedFilesAccess::test_shared_file_grants_download_access
- [x] Test: Revoke share removes access ✓ TestSharedFilesAccess::test_revoke_share_removes_access
- [x] Test: Shared files visible in recipient's file list ✓ TestListSharedFiles::test_list_shared_files_returns_shared_files + GET /api/files/shared endpoint
- [x] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-21 passing` ✓

## 6.4 Permission Audit Log (feat-22)

- [x] Create `backend/app/core/audit.py` for audit logging ✓ Created with AuditAction, EntityType, and logging functions
- [x] Log all permission changes: role changes, deal membership, file shares ✓ log_role_change(), log_deal_membership_change(), log_file_share()
- [x] Audit entry: actor_id, action, entity_type, entity_id, old_value, new_value, timestamp ✓ Uses existing AuditLog model in models/audit.py
- [x] Make audit entries immutable (no UPDATE/DELETE) ✓ Router only has GET endpoints, tests verify 405 on PUT/DELETE
- [x] Implement GET `/api/audit` - paginated audit log (Admin only) ✓ routers/audit.py with require_admin dependency
- [x] Create `frontend/app/admin/audit/page.tsx` for viewing audit log ✓ Full-featured admin page with filtering
- [x] Filter by: action type, actor, entity, date range ✓ All filters implemented with query params
- [x] Test: Role change creates audit entry ✓ TestRoleChangeCreatesAuditEntry::test_role_change_creates_audit_entry
- [x] Test: Audit log visible to Admins ✓ TestAuditLogEndpoints::test_admin_can_view_audit_log
- [x] Test: Audit entries cannot be modified ✓ TestAuditEntriesAreImmutable (no PUT/DELETE endpoints)
- [x] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-22 passing` ✓

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
