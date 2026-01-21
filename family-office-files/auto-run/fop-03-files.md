# Phase 3: File Repository (Hybrid Storage)

**Features**: feat-13, feat-14, feat-15, feat-16, feat-17, feat-18
**Priority**: P1/P2 - Core file management
**Depends on**: Phase 2 (Deals)

## Pre-requisites
- [x] Phase 2 complete (deals working) ✓ feat-9,10,11,12 all passing
- [ ] Google Cloud project created with Drive API enabled
- [ ] Google Cloud Storage bucket created
- [ ] OAuth 2.0 credentials configured

## 3.1 Google Drive OAuth (feat-13)

- [x] Create `backend/app/routers/integrations.py` for Google integration
- [x] Implement GET `/api/integrations/google/auth` - initiate OAuth flow
- [x] Implement GET `/api/integrations/google/callback` - OAuth callback
- [x] Store refresh token in google_connections table
- [x] Implement DELETE `/api/integrations/google` - disconnect
- [x] Implement token refresh logic when access token expires
- [x] Test: Connect Google Drive completes OAuth flow ✓ test_callback_stores_tokens_in_database
- [x] Test: Disconnect removes stored tokens ✓ test_disconnect_removes_stored_tokens
- [x] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-13 passing`

**Note:** Also created:
- `backend/app/schemas/google.py` - Pydantic schemas for Google responses
- `backend/tests/test_integrations.py` - Unit tests for Google OAuth endpoints
- Added `GoogleConnection` model import to conftest.py

## 3.2 Drive Picker Integration (feat-14)

- [x] Add Google Picker API script to Next.js frontend ✓ DrivePicker.tsx loads Google APIs dynamically
- [x] Create `frontend/components/files/DrivePicker.tsx` component ✓ with OAuth token client
- [x] Configure Picker with user's OAuth token ✓ using GSI token client
- [x] Handle file selection callback ✓ links files to deal via API
- [x] Create POST `/api/deals/{deal_id}/files/link` to link Drive file ✓ backend/app/routers/files.py
- [x] Store Drive file ID, name, mime type in files table ✓ via FileSource.DRIVE
- [x] Test: Open Drive Picker displays user's files ✓ tests/test_files.py created
- [x] Test: Select file links it to deal ✓ test_link_drive_file_success
- [x] Test: Select multiple files links all ✓ test_link_multiple_files_sequentially
- [x] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-14 passing` ✓

**Note:** Also created:
- `backend/app/schemas/file.py` - Pydantic schemas for file operations
- `backend/app/routers/files.py` - Files router with link and list endpoints
- `frontend/lib/api.ts` - Updated with filesApi methods
- `frontend/app/deals/[id]/page.tsx` - Updated with file list and DrivePicker UI
- `frontend/components/files/index.ts` - Component exports
- `backend/tests/test_files.py` - Unit tests for file endpoints

## 3.3 Direct File Upload GCS (feat-15)

- [ ] Create `backend/app/core/storage.py` for GCS operations
- [ ] Implement POST `/api/deals/{deal_id}/files/upload` with multipart form
- [ ] Validate file size (max 100MB)
- [ ] Validate file types (configurable allowlist)
- [ ] Upload to GCS with deal-scoped path: `deals/{deal_id}/{file_id}/{filename}`
- [ ] Store GCS path in files table with source='gcs'
- [ ] Implement GET `/api/files/{file_id}/download` - generate signed URL
- [ ] Create `frontend/components/files/FileUploader.tsx` with drag-drop
- [ ] Show upload progress indicator
- [ ] Test: Upload valid file succeeds
- [ ] Test: Upload oversized file returns 413
- [ ] Test: Download returns file contents
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-15 passing`

## 3.4 File Listing Per Deal (feat-16)

- [ ] Implement GET `/api/deals/{deal_id}/files` - list all files
- [ ] Return unified list from both Drive and GCS sources
- [ ] Include source indicator (drive/gcs), name, size, mime_type, uploaded_by, created_at
- [ ] Support sorting: name, date, type
- [ ] Support search/filter by filename
- [ ] Create `frontend/components/files/FileList.tsx` component
- [ ] Display source icon (Drive vs Upload)
- [ ] Add sort and filter controls
- [ ] Test: List shows both Drive and GCS files
- [ ] Test: Sort by date works
- [ ] Test: Search filters results
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-16 passing`

## 3.5 File Preview (feat-17)

- [ ] Create `frontend/components/files/FilePreview.tsx` modal component
- [ ] Implement PDF preview using react-pdf or iframe
- [ ] Implement image preview (jpg, png, gif, webp)
- [ ] For Drive files, use Google Docs Viewer embed
- [ ] For GCS files, generate signed URL for preview
- [ ] Fallback to download button for unsupported types
- [ ] Test: Preview PDF renders in modal
- [ ] Test: Preview image displays correctly
- [ ] Test: Unsupported type offers download
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-17 passing`

## 3.6 File Permissions (feat-18)

- [ ] Enforce role-based access on file operations:
  - Viewer: view, download only
  - Partner: view, download, upload
  - Admin: full control including delete
- [ ] Implement DELETE `/api/files/{file_id}` (admin only)
- [ ] Implement POST `/api/files/{file_id}/share` for cross-FO sharing
- [ ] Create file_shares table entries for explicit grants
- [ ] Hide upload button for Viewers in UI
- [ ] Hide delete button for non-Admins in UI
- [ ] Test: Viewer cannot upload (403 API, hidden UI)
- [ ] Test: Partner can upload
- [ ] Test: Admin can delete
- [ ] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-18 passing`

## Phase 3 Completion

- [ ] All 6 features (feat-13 through feat-18) marked as passing
- [ ] Can connect Google Drive and link files
- [ ] Can upload files directly to platform
- [ ] Unified file listing working
- [ ] File preview functional
- [ ] Permissions enforced
- [ ] Run `bun .claude/skills/CORE/Tools/FeatureRegistry.ts verify family-office-files` to confirm
