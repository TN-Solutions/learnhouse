# Media Storage Refactor - Technical Design

## Context

LearnHouse currently has a broken S3 implementation where:

1. Files are always saved to filesystem even when S3 is configured
2. Media retrieval always fetches from filesystem, completely ignoring S3
3. S3 bucket name is hardcoded instead of using configuration
4. Frontend has knowledge of storage backend (constructing file URLs)

This design addresses these issues by introducing a proper storage abstraction layer.

## Goals

- **Primary**: Enable true S3-only storage without filesystem duplication
- **Secondary**: Support direct-to-S3 uploads via presigned URLs for better performance
- **Tertiary**: Make frontend completely storage-agnostic

## Non-Goals

- Multi-cloud storage support (AWS S3, GCP, Azure) - Out of scope, S3-compatible only
- Storage migration tools - Manual migration expected
- Hybrid storage (some files S3, some filesystem) - Single storage backend only
- File versioning or rollback - Not addressed in this change

## Architectural Decisions

### Decision 1: Storage Abstraction Layer

**What**: Create a unified storage interface with filesystem and S3 implementations.

**Why**:

- Eliminates conditional logic scattered across codebase
- Enables easier testing with mock implementations
- Provides single point of change for storage operations
- Follows Open/Closed Principle (open for extension, closed for modification)

**Implementation**:

```python
# apps/api/src/services/storage/base.py
class StorageBackend(ABC):
    @abstractmethod
    async def get_upload_url(self, path: str, file_type: str) -> UploadUrlResponse

    @abstractmethod
    async def get_download_url(self, path: str) -> str

    @abstractmethod
    async def delete_file(self, path: str) -> bool

# apps/api/src/services/storage/filesystem.py
class FilesystemStorage(StorageBackend):
    async def get_upload_url(self, path: str, file_type: str) -> UploadUrlResponse:
        # Return direct upload endpoint for multipart/form-data
        return UploadUrlResponse(
            upload_url=f"/api/storage/upload",
            method="POST",
            fields={"path": path}
        )

# apps/api/src/services/storage/s3.py
class S3Storage(StorageBackend):
    async def get_upload_url(self, path: str, file_type: str) -> UploadUrlResponse:
        # Generate presigned POST URL
        presigned_data = self.s3_client.generate_presigned_post(
            Bucket=self.bucket_name,
            Key=path,
            ExpiresIn=3600,
            Conditions=[["content-length-range", 0, 104857600]]  # Max 100MB
        )
        return UploadUrlResponse(
            upload_url=presigned_data['url'],
            method="POST",
            fields=presigned_data['fields']
        )
```

**Alternatives Considered**:

- **Option A**: Continue with conditional logic in upload_content.py
  - ❌ Rejected: Leads to complex, hard-to-maintain code
- **Option B**: Separate API endpoints for S3 vs filesystem
  - ❌ Rejected: Frontend would need to know storage backend
- **Option C**: Storage abstraction layer (CHOSEN)
  - ✅ Clean separation, testable, extensible

### Decision 2: Presigned URL Upload Flow

**What**: Use S3 presigned POST URLs for direct client-to-S3 uploads.

**Why**:

- Reduces backend load (files don't transit through API server)
- Better upload performance (direct to S3, no proxy)
- Scalability (S3 handles upload traffic, not API)
- Security (presigned URLs expire, scoped permissions)

**Flow**:

```
┌─────────┐                    ┌─────────┐                    ┌─────────┐
│ Frontend│                    │ Backend │                    │   S3    │
└────┬────┘                    └────┬────┘                    └────┬────┘
     │                              │                              │
     │ 1. Request upload URL        │                              │
     ├─────────────────────────────>│                              │
     │                              │                              │
     │ 2. Generate presigned URL    │                              │
     │                              ├─────────────────────────────>│
     │                              │                              │
     │ 3. Return presigned URL      │                              │
     │<─────────────────────────────┤                              │
     │                              │                              │
     │ 4. Upload file directly      │                              │
     ├──────────────────────────────────────────────────────────>│
     │                              │                              │
     │ 5. Confirm upload            │                              │
     ├─────────────────────────────>│                              │
     │                              │                              │
     │ 6. Update database metadata  │                              │
     │<─────────────────────────────┤                              │
     │                              │                              │
```

**Alternatives Considered**:

- **Option A**: Backend proxies all uploads
  - ❌ Rejected: High backend load, poor scalability
- **Option B**: Presigned URLs (CHOSEN)
  - ✅ Better performance, scalability, security
- **Option C**: Multipart upload with streaming
  - ❌ Rejected: Complex implementation, minimal benefit

### Decision 3: Storage-Agnostic Frontend

**What**: Frontend calls generic upload API, backend decides storage mechanism.

**Why**:

- Frontend doesn't need storage backend knowledge
- Storage backend can change without frontend changes
- Cleaner separation of concerns
- Easier to add new storage backends later

**API Contract**:

```typescript
// Request
POST /api/media/upload/prepare
{
  "file_type": "image/png",
  "file_name": "avatar.png",
  "resource_type": "user_avatar",
  "resource_id": "user_uuid"
}

// Response (Filesystem)
{
  "upload_url": "https://api.learnhouse.app/api/storage/upload",
  "method": "POST",
  "fields": {
    "path": "content/users/uuid/avatar.png"
  },
  "file_url": "https://api.learnhouse.app/content/users/uuid/avatar.png"
}

// Response (S3)
{
  "upload_url": "https://s3.amazonaws.com/bucket-name",
  "method": "POST",
  "fields": {
    "key": "content/users/uuid/avatar.png",
    "AWSAccessKeyId": "...",
    "policy": "...",
    "signature": "..."
  },
  "file_url": "https://s3.amazonaws.com/bucket-name/content/users/uuid/avatar.png"
}
```

### Decision 4: Conditional Static File Serving

**What**: Mount StaticFiles middleware only when storage type is filesystem.

**Why**:

- S3 files served directly from S3 (or via presigned URLs)
- No need for StaticFiles when using S3
- Cleaner architecture, less confusion

**Implementation**:

```python
# apps/api/app.py
if learnhouse_config.hosting_config.content_delivery.type == "filesystem":
    app.mount("/content", StaticFiles(directory="content"), name="content")
else:
    # S3 mode: files served directly from S3
    # No static file mounting needed
    pass
```

### Decision 5: File Metadata in Database

**What**: Store file metadata (storage_backend, file_path, file_url) in database.

**Why**:

- Track which storage backend was used for each file
- Support future migration scenarios
- Enable file access logging and analytics
- Facilitate cleanup of orphaned files

**Schema**:

```python
class MediaFile(SQLModel, table=True):
    id: int
    file_uuid: str
    storage_backend: str  # "filesystem" | "s3api"
    file_path: str        # Path in storage
    file_url: str         # Public access URL
    content_type: str
    file_size: int
    uploaded_at: datetime
    resource_type: str    # "user_avatar", "course_thumbnail", etc.
    resource_id: str
```

## Risks & Trade-offs

### Risk 1: Migration Complexity

- **Risk**: Existing deployments have files in filesystem, switching to S3 requires migration
- **Mitigation**:
  - Provide migration script to copy files from filesystem to S3
  - Document migration process clearly
  - Support gradual migration (keep filesystem for old files, S3 for new)

### Risk 2: Presigned URL Expiration

- **Risk**: If upload takes longer than presigned URL expiry (default 1 hour), upload fails
- **Mitigation**:
  - Set reasonable expiry time (1 hour)
  - Add file size validation before generating presigned URL
  - Implement retry mechanism in frontend
  - Show clear error message on expiry

### Risk 3: CORS Configuration

- **Risk**: Direct-to-S3 uploads require proper CORS configuration on S3 bucket
- **Mitigation**:
  - Document required CORS configuration
  - Add health check endpoint to verify S3 CORS
  - Provide clear error messages for CORS issues

### Risk 4: Testing Complexity

- **Risk**: Need to test both filesystem and S3 paths thoroughly
- **Mitigation**:
  - Use MinIO (S3-compatible) for local S3 testing
  - Create comprehensive test suite covering both backends
  - Add integration tests for upload flows

### Trade-off 1: Complexity vs Flexibility

- **Trade-off**: Abstract storage layer adds complexity but enables flexibility
- **Decision**: Complexity is justified by benefits (testability, extensibility, separation of concerns)

### Trade-off 2: Direct Upload vs Backend Proxy

- **Trade-off**: Direct S3 upload is faster but requires CORS setup and presigned URLs
- **Decision**: Performance and scalability benefits outweigh setup complexity

## Migration Plan

### Phase 1: Implementation (No Breaking Changes)

1. Implement storage abstraction layer
2. Add new upload preparation endpoint
3. Keep old upload endpoints functioning
4. Add feature flag to enable new flow

### Phase 2: Frontend Migration

1. Update upload components to use new API
2. Test both storage backends thoroughly
3. Deploy with feature flag disabled

### Phase 3: Enable New System

1. Enable feature flag in staging
2. Test end-to-end with both backends
3. Enable in production gradually

### Phase 4: Cleanup (Breaking Changes)

1. Remove old upload endpoints
2. Remove duplicate storage logic
3. Update documentation

### Rollback Plan

If issues arise:

1. Disable feature flag to revert to old flow
2. Fix issues in new implementation
3. Re-enable after fixes

## Open Questions

1. **File Cleanup**: How to handle orphaned files when resources are deleted?

   - **Proposed**: Add background job to periodically clean orphaned files
   - **Needs**: Discussion on cleanup schedule and safety

2. **File Size Limits**: Should limits differ between filesystem and S3?

   - **Proposed**: Same limits for consistency
   - **Needs**: Product decision on limits per file type

3. **CDN Integration**: Should we add CDN support for S3?

   - **Proposed**: Out of scope for this change, can be added later
   - **Needs**: Validation that it's not blocking

4. **Multipart Upload**: Do we need multipart upload for large files?
   - **Proposed**: Not initially, presigned POST supports up to 100MB
   - **Needs**: Validation of max file size requirements

## Performance Expectations

### Current System (Broken)

- Upload: File → Backend → Filesystem → S3 (duplicate)
- Download: Always from filesystem
- Backend load: High (proxies all uploads)

### New System (Filesystem)

- Upload: File → Backend → Filesystem
- Download: Direct from filesystem via StaticFiles
- Backend load: Moderate (processes uploads)

### New System (S3)

- Upload: File → S3 (direct, via presigned URL)
- Download: Direct from S3 (or presigned URL)
- Backend load: Low (only generates URLs)

Expected improvements:

- 50-70% reduction in backend upload traffic (S3 mode)
- Faster upload times (direct to S3, no proxy)
- Better scalability (S3 handles traffic)
