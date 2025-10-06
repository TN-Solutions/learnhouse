## Why

The current dual storage backend system (filesystem + S3) adds unnecessary complexity, maintenance overhead, and operational burden. Filesystem storage creates scaling limitations, backup challenges, and deployment inconsistencies. Removing it will simplify the codebase while providing a more robust, scalable, and cloud-native solution.

## What Changes

- **Remove filesystem storage backend** - Eliminate `filesystem.py` and related code
- **Simplify storage factory** - Remove backend selection logic, default to S3 only
- **Update configuration** - Remove filesystem-specific config options
- **Modify API endpoints** - Remove direct-upload endpoint (filesystem-only)
- **Update tests** - Remove filesystem storage tests, focus on S3 testing
- **Migrate existing data** - Provide migration path for any filesystem-stored files
- **Update documentation** - Reflect S3-only architecture

## Impact

- **Affected specs**: media-storage capability (new spec to be created)
- **Affected code**:
  - `apps/api/src/services/storage/filesystem.py` (removed)
  - `apps/api/src/services/storage/factory.py` (simplified)
  - `apps/api/src/routers/media/upload.py` (remove direct-upload)
  - `apps/api/config/config.py` (remove filesystem config)
  - `apps/api/src/tests/services/storage/test_filesystem.py` (removed)
  - All services using filesystem storage backend

**Benefits**:
- Reduced code complexity and maintenance overhead
- Consistent cloud-native storage architecture
- Simplified deployment and operations
- Better scalability and reliability
- Eliminated backup/disaster recovery complexity for local files

**Risks**:
- S3 dependency becomes mandatory (mitigated by S3-compatible alternatives like MinIO)
- Network dependency for all file operations (mitigated by presigned URLs and caching)