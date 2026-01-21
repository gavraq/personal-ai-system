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

- [x] Create `backend/app/core/storage.py` for GCS operations ✓ StorageService class with upload/download
- [x] Implement POST `/api/deals/{deal_id}/files/upload` with multipart form ✓ files.py router
- [x] Validate file size (max 100MB) ✓ validate_file_size() method
- [x] Validate file types (configurable allowlist) ✓ validate_mime_type() with ALLOWED_MIME_TYPES
- [x] Upload to GCS with deal-scoped path: `deals/{deal_id}/{file_id}/{filename}` ✓ get_file_path() method
- [x] Store GCS path in files table with source='gcs' ✓ FileSource.GCS enum
- [x] Implement GET `/api/files/{file_id}/download` - generate signed URL ✓ generate_signed_url() method
- [x] Create `frontend/components/files/FileUploader.tsx` with drag-drop ✓ with drag-drop zone
- [x] Show upload progress indicator ✓ Progress component with XHR progress tracking
- [x] Test: Upload valid file succeeds ✓ test_upload_valid_file_success
- [x] Test: Upload oversized file returns 413 ✓ test_upload_oversized_file_returns_413
- [x] Test: Download returns file contents ✓ test_download_gcs_file_returns_signed_url
- [x] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-15 passing`

**Note:** Also created/updated:
- `backend/app/core/storage.py` - GCS storage service with validation and signed URL generation
- `backend/app/schemas/file.py` - Added UploadFileResponse and FileDownloadResponse schemas
- `backend/app/routers/files.py` - Added upload and download endpoints
- `frontend/components/files/FileUploader.tsx` - Drag-drop upload component with progress
- `frontend/components/ui/progress.tsx` - Progress bar component
- `frontend/lib/api.ts` - Added getDownloadUrl method
- `backend/tests/test_files.py` - Added TestUploadFile and TestDownloadFile test classes
- `backend/requirements.txt` - Added pytest-mock for testing
- `backend/app/models/file.py` - Fixed enum serialization for PostgreSQL

## 3.4 File Listing Per Deal (feat-16)

- [x] Implement GET `/api/deals/{deal_id}/files` - list all files ✓ Enhanced with sort_by, sort_order, search params
- [x] Return unified list from both Drive and GCS sources ✓ FileListResponse with FileResponse models
- [x] Include source indicator (drive/gcs), name, size, mime_type, uploaded_by, created_at ✓ FileResponse schema
- [x] Support sorting: name, date, type ✓ sort_by=name|date|type, sort_order=asc|desc
- [x] Support search/filter by filename ✓ search param with case-insensitive ilike matching
- [x] Create `frontend/components/files/FileList.tsx` component ✓ Full implementation with all features
- [x] Display source icon (Drive vs Upload) ✓ DriveIcon and UploadIcon components
- [x] Add sort and filter controls ✓ Search input, source filter buttons, sort buttons
- [x] Test: List shows both Drive and GCS files ✓ test_list_files_filter_by_source
- [x] Test: Sort by date works ✓ test_list_files_sort_by_date_desc
- [x] Test: Search filters results ✓ test_list_files_search_by_filename, test_list_files_search_no_results
- [x] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-16 passing` ✓

**Note:** Implementation complete. Also created/updated:
- `backend/app/routers/files.py` - Enhanced list_deal_files with sort_by, sort_order, search parameters
- `frontend/components/files/FileList.tsx` - Full-featured file list component with sort/filter/search
- `frontend/lib/api.ts` - Added FileListOptions interface and updated filesApi.list()
- `frontend/components/files/index.ts` - Exported FileList component
- `backend/tests/test_files.py` - Added 5 new tests for sorting and search functionality:
  - test_list_files_sort_by_date_desc
  - test_list_files_sort_by_name_asc
  - test_list_files_search_by_filename
  - test_list_files_search_no_results
  - test_list_files_combined_filter_sort_search

## 3.5 File Preview (feat-17)

- [x] Create `frontend/components/files/FilePreview.tsx` modal component ✓ Full implementation with Dialog wrapper
- [x] Implement PDF preview using react-pdf or iframe ✓ Using iframe for PDF rendering
- [x] Implement image preview (jpg, png, gif, webp) ✓ Native img tag with object-fit
- [x] For Drive files, use Google Docs Viewer embed ✓ drive.google.com/file/d/{id}/preview
- [x] For GCS files, generate signed URL for preview ✓ Using filesApi.getDownloadUrl()
- [x] Fallback to download button for unsupported types ✓ Shows "Preview not available" with download option
- [x] Test: Preview PDF renders in modal ✓ test_renders_pdf_in_modal_with_iframe
- [x] Test: Preview image displays correctly ✓ test_renders_image_preview_correctly
- [x] Test: Unsupported type offers download ✓ test_shows_fallback_message_for_unsupported_file_types
- [x] Update registry: `bun .claude/skills/CORE/Tools/FeatureRegistry.ts update family-office-files feat-17 passing` ✓

**Note:** Implementation complete. Also created/updated:
- `frontend/components/files/FilePreview.tsx` - Full preview modal with PDF, image, Drive file support
- `frontend/components/files/FileList.tsx` - Added preview button and FilePreview integration
- `frontend/components/files/index.ts` - Exported FilePreview component
- `frontend/__tests__/files/FilePreview.test.tsx` - 10 tests covering all preview scenarios:
  - test_renders_pdf_in_modal_with_iframe
  - test_renders_image_preview_correctly
  - test_renders_drive_file_with_google_drive_preview_url
  - test_shows_fallback_message_for_unsupported_file_types
  - test_provides_download_button
  - test_calls_download_api_when_download_button_clicked
  - test_shows_error_message_when_preview_fails_to_load
  - test_displays_file_size_in_description
  - test_renders_nothing_when_file_is_null
  - test_closes_modal_when_open_changes_to_false

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
