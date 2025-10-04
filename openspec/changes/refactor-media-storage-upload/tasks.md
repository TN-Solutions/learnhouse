# Implementation Tasks

## 1. Backend - Storage Abstraction Layer

- [ ] 1.1 Create storage backend base class and interface

  - File: `apps/api/src/services/storage/base.py`
  - Define `StorageBackend` abstract class with `get_upload_url()`, `get_download_url()`, `delete_file()` methods
  - Define response models: `UploadUrlResponse`, `DownloadUrlResponse`

- [ ] 1.2 Implement filesystem storage backend

  - File: `apps/api/src/services/storage/filesystem.py`
  - Implement `FilesystemStorage` class extending `StorageBackend`
  - Handle file path generation, directory creation, file operations
  - Return direct upload endpoints for filesystem

- [ ] 1.3 Implement S3 storage backend

  - File: `apps/api/src/services/storage/s3.py`
  - Implement `S3Storage` class extending `StorageBackend`
  - Integrate boto3 for S3 operations
  - Implement presigned POST URL generation with proper constraints
  - Implement presigned GET URL generation for downloads
  - Add S3 connectivity validation

- [ ] 1.4 Create storage factory

  - File: `apps/api/src/services/storage/factory.py`
  - Implement `get_storage_backend()` function that returns appropriate backend based on config
  - Handle backend initialization and caching

- [ ] 1.5 Update configuration
  - File: `apps/api/config/config.py`
  - Ensure S3 configuration uses config values (not hardcoded)
  - Add validation for S3 required fields when s3api type is selected
  - Add optional configuration for presigned URL expiry, file size limits

## 2. Backend - Database Models

- [ ] 2.1 Create MediaFile database model

  - File: `apps/api/src/db/media/media.py`
  - Define `MediaFile` model with fields: file_uuid, storage_backend, file_path, file_url, content_type, file_size, uploaded_at, resource_type, resource_id
  - Add indexes for efficient querying by resource_type and resource_id

- [ ] 2.2 Create database migration
  - Generate Alembic migration for MediaFile table
  - Run migration in development environment

## 3. Backend - Upload Preparation API

- [ ] 3.1 Create upload preparation service

  - File: `apps/api/src/services/media/upload_preparation.py`
  - Implement `prepare_upload()` function that validates file metadata and calls storage backend
  - Add file type validation (MIME types, extensions)
  - Add filename sanitization (path traversal prevention)
  - Add file size validation

- [ ] 3.2 Create upload preparation router

  - File: `apps/api/src/routers/media/upload.py`
  - Add `POST /api/media/upload/prepare` endpoint
  - Accept file metadata: file_type, file_name, resource_type, resource_id
  - Return upload URL, method, fields, and final file URL
  - Add RBAC authorization checks

- [ ] 3.3 Create direct upload endpoint (filesystem only)

  - File: `apps/api/src/routers/media/upload.py`
  - Add `POST /api/storage/upload` endpoint for filesystem uploads
  - Handle multipart file upload
  - Save file to filesystem at specified path
  - Create MediaFile database record
  - Return public file URL

- [ ] 3.4 Create upload confirmation endpoint (S3)
  - File: `apps/api/src/routers/media/upload.py`
  - Add `POST /api/media/upload/confirm` endpoint
  - Verify file exists in S3 (optional, for reliability)
  - Create MediaFile database record
  - Return success response

## 4. Backend - File Retrieval API

- [ ] 4.1 Create file retrieval service

  - File: `apps/api/src/services/media/retrieval.py`
  - Implement `get_file_url()` function that queries database and returns appropriate URL
  - Support both public URLs and presigned URLs based on storage backend

- [ ] 4.2 Update static file mounting

  - File: `apps/api/app.py`
  - Make StaticFiles mounting conditional: only mount if `content_delivery.type == "filesystem"`
  - Add comment explaining why conditional mounting is needed

- [ ] 4.3 Create file metadata endpoint
  - File: `apps/api/src/routers/media/files.py`
  - Add `GET /api/media/files/{file_uuid}` endpoint to get file metadata
  - Add `GET /api/media/files?resource_type={type}&resource_id={id}` to query files by resource
  - Add `DELETE /api/media/files/{file_uuid}` to delete file and metadata

## 5. Backend - Refactor Existing Upload Code

- [ ] 5.1 Update image upload service

  - File: `apps/api/src/services/blocks/imageBlock.py`
  - Migrate to use new upload preparation API
  - Remove direct calls to `upload_content()`
  - Update to return presigned URL when S3 is enabled

- [ ] 5.2 Update video upload service

  - File: `apps/api/src/services/blocks/videoBlock.py`
  - Migrate to use new upload preparation API
  - Handle large file uploads with presigned URLs

- [ ] 5.3 Update PDF upload service

  - File: `apps/api/src/services/blocks/pdfBlock.py`
  - Migrate to use new upload preparation API

- [ ] 5.4 Update thumbnail upload service

  - File: `apps/api/src/services/courses/thumbnails.py`
  - Migrate to use new upload preparation API

- [ ] 5.5 Update avatar upload service

  - File: `apps/api/src/services/users/avatars.py`
  - Migrate to use new upload preparation API

- [ ] 5.6 Update organization upload services

  - Files: `apps/api/src/routers/orgs.py` or `apps/api/src/services/organizations/orgs.py`
  - Migrate organization logo upload to use new upload preparation API
  - Migrate organization thumbnail upload to use new upload preparation API
  - Migrate organization preview upload to use new upload preparation API
  - Migrate landing content upload to use new upload preparation API

- [ ] 5.7 Update course creation service

  - File: `apps/api/src/services/courses/courses.py`
  - Migrate thumbnail upload in `createNewCourse()` to use new upload preparation API
  - Ensure course creation flow works with both filesystem and S3

- [ ] 5.8 Update activity upload service

  - File: `apps/api/src/services/courses/activities.py` or related activity routers
  - Migrate video activity upload to use new upload preparation API
  - Migrate PDF (documentpdf) activity upload to use new upload preparation API
  - Handle both activity types in createNewActivity flow

- [ ] 5.9 Update assignment reference file upload service

  - File: `apps/api/src/services/courses/activities/uploads/tasks_ref_files.py`
  - Migrate to use new upload preparation API
  - Ensure reference file uploads work with both backends

- [ ] 5.10 Update assignment submission file upload service

  - File: `apps/api/src/services/courses/activities/uploads/sub_file.py`
  - Migrate to use new upload preparation API
  - Ensure submission file uploads work with both backends

- [ ] 5.11 Deprecate old upload_content function
  - File: `apps/api/src/services/utils/upload_content.py`
  - Add deprecation warning
  - Plan for eventual removal after all code migrated

## 6. Frontend - Media Service Update

- [ ] 6.1 Create upload preparation service

  - File: `apps/web/services/media/upload.ts`
  - Add `prepareUpload()` function that calls `/api/media/upload/prepare`
  - Add `uploadFile()` function that handles both direct upload and S3 presigned URL upload
  - Add `confirmUpload()` function for S3 uploads

- [ ] 6.2 Create generic file upload hook

  - File: `apps/web/hooks/useFileUpload.ts`
  - Implement `useFileUpload()` hook that:
    - Prepares upload (gets URL from backend)
    - Uploads file (direct or S3)
    - Confirms upload (S3 only)
    - Tracks progress
    - Handles errors and retries
  - Make storage-agnostic (works with both backends)

- [ ] 6.3 Update media URL service
  - File: `apps/web/services/media/media.ts`
  - Simplify to only construct URLs from backend responses
  - Remove storage-specific logic
  - Support both filesystem and S3 URLs

## 7. Frontend - Component Updates

- [ ] 7.1 Update ImageBlock component

  - File: `apps/web/components/Objects/Editor/Extensions/Image/ImageBlockComponent.tsx`
  - Use new `useFileUpload()` hook
  - Remove storage-specific logic
  - Add proper error handling and retry

- [ ] 7.2 Update VideoBlock component

  - File: `apps/web/components/Objects/Editor/Extensions/Video/VideoBlockComponent.tsx`
  - Use new `useFileUpload()` hook
  - Maintain existing progress tracking
  - Support large file uploads via presigned URLs

- [ ] 7.3 Update ThumbnailUpdate component

  - File: `apps/web/components/Dashboard/Pages/Course/EditCourseGeneral/ThumbnailUpdate.tsx`
  - Use new `useFileUpload()` hook
  - Maintain existing preview functionality

- [ ] 7.4 Update avatar upload components

  - File: `apps/web/components/Dashboard/Pages/UserAccount/UserEditGeneral/UserEditGeneral.tsx`
  - Use new `useFileUpload()` hook for avatar uploads
  - Maintain existing preview functionality

- [ ] 7.5 Update organization upload components

  - File: `apps/web/components/Dashboard/Pages/Org/OrgEditImages/OrgEditImages.tsx`
  - Use new `useFileUpload()` hook for organization logo upload
  - Use new `useFileUpload()` hook for organization thumbnail upload
  - Use new `useFileUpload()` hook for organization preview upload
  - Maintain existing preview and validation functionality

- [ ] 7.6 Update landing content upload component

  - File: `apps/web/components/Dashboard/Pages/Org/OrgEditLanding/OrgEditLanding.tsx`
  - Use new `useFileUpload()` hook for landing content uploads
  - Ensure proper integration with landing page editor

- [ ] 7.7 Update course creation component

  - File: `apps/web/components/Objects/Modals/Course/Create/CreateCourse.tsx`
  - Use new `useFileUpload()` hook for course thumbnail upload during creation
  - Ensure thumbnail upload integrates smoothly with course creation flow

- [ ] 7.8 Update activity creation components

  - File: `apps/web/components/Objects/Modals/Activities/Create/NewActivityModal/DocumentActivityModal.tsx`
  - Use new `useFileUpload()` hook for video activity uploads
  - Use new `useFileUpload()` hook for PDF activity uploads
  - Handle both activity types with new upload flow

- [ ] 7.9 Update assignment reference file upload component

  - File: `apps/web/app/orgs/[orgslug]/dash/assignments/[assignmentuuid]/_components/TaskEditor/Subs/AssignmentTaskGeneralEdit.tsx`
  - Use new `useFileUpload()` hook for reference file uploads
  - Maintain existing file display and management functionality

- [ ] 7.10 Update assignment submission file upload component

  - File: `apps/web/app/orgs/[orgslug]/dash/assignments/[assignmentuuid]/_components/TaskEditor/Subs/TaskFileObject.tsx`
  - Use new `useFileUpload()` hook for submission file uploads
  - Maintain existing submission file display and management

## 8. Testing

- [ ] 8.1 Create storage backend tests

  - File: `apps/api/src/tests/services/storage/test_filesystem.py`
  - Test filesystem backend: upload, download, delete operations

- [ ] 8.2 Create S3 storage tests

  - File: `apps/api/src/tests/services/storage/test_s3.py`
  - Test S3 backend with MinIO (local S3-compatible server)
  - Test presigned URL generation
  - Test S3 upload and download flows

- [ ] 8.3 Create upload preparation API tests

  - File: `apps/api/src/tests/routers/media/test_upload.py`
  - Test upload preparation endpoint with both backends
  - Test file validation (type, size, filename)
  - Test authorization

- [ ] 8.4 Create file retrieval tests

  - File: `apps/api/src/tests/routers/media/test_files.py`
  - Test file metadata endpoints
  - Test file deletion

- [ ] 8.5 Create integration tests

  - File: `apps/api/src/tests/integration/test_media_upload.py`
  - Test complete upload flows (prepare → upload → confirm)
  - Test both filesystem and S3 backends
  - Test error scenarios

- [ ] 8.6 Frontend upload hook tests
  - File: `apps/web/hooks/__tests__/useFileUpload.test.ts`
  - Test upload hook with mocked backend
  - Test progress tracking, error handling, retries

## 9. Documentation

- [ ] 9.1 Update API documentation

  - Document new upload preparation endpoint
  - Document upload confirmation endpoint
  - Document file metadata endpoints
  - Add examples for both filesystem and S3 flows

- [ ] 9.2 Update configuration documentation

  - Document S3 configuration requirements
  - Document environment variables
  - Document CORS configuration for S3

- [ ] 9.3 Create migration guide

  - Document how to migrate from filesystem to S3
  - Provide migration script or manual steps
  - Document rollback procedure

- [ ] 9.4 Update developer documentation
  - Document storage abstraction architecture
  - Document how to add new upload types
  - Document testing with MinIO for S3

## 10. Deployment & Migration

- [ ] 10.1 Create file migration script

  - Script to copy files from filesystem to S3
  - Script to update database metadata for migrated files
  - Script to verify migration completeness

- [ ] 10.2 Create S3 bucket setup script

  - Script or documentation for S3 bucket creation
  - CORS configuration for direct uploads
  - Bucket policy configuration

- [ ] 10.3 Deploy to staging

  - Test filesystem backend in staging
  - Test S3 backend in staging with test bucket
  - Verify all upload flows work correctly

- [ ] 10.4 Production deployment checklist
  - [ ] Database migration applied
  - [ ] S3 bucket configured (if using S3)
  - [ ] Environment variables updated
  - [ ] Existing files migrated (if switching to S3)
  - [ ] Rollback plan documented
  - [ ] Monitoring in place for upload errors

## 11. Cleanup

- [ ] 11.1 Remove old upload_content function

  - After all code migrated and tested
  - Remove `apps/api/src/services/utils/upload_content.py`

- [ ] 11.2 Remove deprecated upload endpoints

  - Remove old direct upload endpoints from routers
  - Update any remaining references

- [ ] 11.3 Clean up unused code
  - Search for unused imports and functions
  - Remove dead code from migration

## Validation Checklist

After completing all tasks, verify:

- [ ] All uploads work with filesystem storage
- [ ] All uploads work with S3 storage
- [ ] File retrieval works from both backends
- [ ] File deletion works correctly
- [ ] Frontend is storage-agnostic (no backend knowledge)
- [ ] All tests pass (backend and frontend)
- [ ] No duplicate file storage
- [ ] S3 bucket name from config (not hardcoded)
- [ ] Security validations in place (file type, size, path traversal)
- [ ] Error handling and user feedback work correctly
- [ ] Documentation is complete and accurate
