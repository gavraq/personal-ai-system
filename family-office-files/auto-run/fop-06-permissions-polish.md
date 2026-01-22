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

- [x] Implement global error handler in FastAPI ✓ Created backend/app/core/exceptions.py with AppException, ErrorCode enum, and handler registration
- [x] Consistent error response format: {error, message, details} ✓ ErrorResponse Pydantic model + custom exception classes
- [x] Handle: 400 (validation), 401 (auth), 403 (permission), 404 (not found), 500 (server) ✓ All HTTP codes mapped to ErrorCode enum with appropriate handlers
- [x] Frontend error boundary component ✓ Created components/error/ErrorBoundary.tsx with retry and home navigation
- [x] Toast notifications for errors ✓ Created components/ui/toast.tsx with ToastProvider and useToast hook (success/error/warning/info variants)
- [x] Retry logic for transient failures ✓ Created lib/errors.ts with withRetry() exponential backoff for transient errors (500, 502, 503, 504, 429)

## 6.6 Performance & Optimization

- [x] Add database indexes for common queries ✓ Created alembic/versions/002_add_performance_indexes.py with 13 new indexes: deal_members.user_id, file_shares.shared_with, audit_log.actor_id/action, activity.actor_id/action, agent_runs.user_id, deals.updated_at, alerts.user_id/deal_id/is_active, alert_matches.alert_id/notified
- [x] Implement pagination on all list endpoints ✓ All list endpoints now have pagination: deals, files, shared files, activity, audit, users, agent runs, alerts, alert matches. Added pagination to DealMemberListResponse and AlertMatchListResponse schemas. Added page/page_size params to GET /api/deals/{deal_id}/members. Tests added in test_deals.py::TestDealMembersPagination.
- [x] Add Redis caching for frequently accessed data ✓ Created backend/app/core/cache.py with functions for user caching (cache_user, get_cached_user, invalidate_user_cache), deal caching (cache_deal, get_cached_deal, invalidate_deal_cache), and deal membership caching (cache_deal_membership, get_cached_deal_membership, invalidate_deal_membership_cache). Integrated with deps.py for user lookups and permissions.py for membership lookups. Added cache invalidation to deals.py (add/remove member) and users.py (role change). Tests in tests/test_cache.py covering all cache functions and integration.
- [x] Optimize N+1 queries with eager loading ✓ Added joinedload() to deals.py (list_deal_members), files.py (list_shared_files), agents.py (list_agent_runs, get_agent_run, list_deal_agent_runs), activity.py (list_activity, list_deal_activity). Created batch query get_deals_with_file_counts() for deal file counts. Refactored response functions to accept pre-loaded data. Tests added in tests/test_eager_loading.py.
- [x] Add API response compression ✓ Added GZipMiddleware to FastAPI app with minimum_size=500 bytes threshold. Middleware compresses API responses larger than 500 bytes to reduce bandwidth. Tests added in tests/test_compression.py covering middleware registration, configuration, and endpoint behavior.

## 6.7 Documentation

- [x] Create `README.md` with setup instructions ✓ Created comprehensive README.md with: Quick Start guide, Local Development instructions for backend/frontend, Testing commands, Project Structure, API Endpoints reference, Roles & Permissions matrix, Environment Variables documentation, and Features overview
- [x] Document API endpoints in OpenAPI (FastAPI auto-generates) ✓ Enhanced FastAPI app with comprehensive OpenAPI documentation: API description with markdown (features, authentication, roles, error format), 8 tag groups with descriptions (auth, users, deals, files, activity, agents, audit, integrations), contact/license info, all 40 endpoints documented with docstrings. Access at /docs (Swagger UI), /redoc, or /openapi.json
- [x] Create `DEPLOYMENT.md` for production deployment ✓ Comprehensive guide covering Docker, Kubernetes, GCP/AWS deployments, SSL/TLS, monitoring, backup/recovery, and security hardening
- [x] Document environment variables ✓ Created comprehensive ENV_VARIABLES.md with: Quick Setup, Backend Variables (Database, JWT, Redis, GCS, Google OAuth, Anthropic), Frontend Variables (including newly discovered NEXT_PUBLIC_GOOGLE_CLIENT_ID/GOOGLE_API_KEY), Docker Variables, Security Best Practices, Environment-Specific Configuration (dev/staging/prod), Troubleshooting guide, and Summary Table. Also updated .env.example with missing frontend Google variables.
- [x] Add inline code comments for complex logic ✓ Added comprehensive inline comments to 9 backend core/router files covering: permissions.py (role hierarchy resolution, cache-with-fallback pattern, dual role mapping), cache.py (Redis SCAN cursor patterns, dual-cache indexes, TTL strategies, performance warnings), security.py (jti/iat token fields, two-level blacklist checking), token_blacklist.py (fail-open security trade-off, TTL lifetime reasoning), deps.py (cache paradox explanation, factory pattern with closures), files.py (three-level access check chain, file share permission levels, N+1 prevention), deals.py (batch query optimization, authorization-driven query branching, status state machine, change tracking), users.py (last-admin safety guard, dual cache invalidation), storage.py (lazy client init, path traversal prevention, HTTP Content-Disposition headers)

## Phase 6 Completion

- [ ] All 4 features (feat-19, feat-20, feat-21, feat-22) marked as passing
- [ ] Complete permission system working
- [ ] Audit log functional
- [ ] Error handling robust
- [ ] Documentation complete
- [ ] Run `bun .claude/skills/CORE/Tools/FeatureRegistry.ts verify family-office-files` to confirm
