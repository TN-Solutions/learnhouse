## ADDED Requirements

### Requirement: S3-Only Media Storage
The system SHALL provide S3-only media storage backend for all file operations.

#### Scenario: Prepare S3 upload
- **WHEN** client requests file upload preparation
- **THEN** system returns S3 presigned POST URL with required fields
- **AND** includes file metadata validation
- **AND** generates unique file UUID for tracking

#### Scenario: Confirm S3 upload completion
- **WHEN** client confirms successful S3 upload
- **THEN** system creates MediaFile database record
- **AND** stores S3 object path and metadata
- **AND** returns final file URL for access

#### Scenario: Retrieve S3 file
- **WHEN** client requests file by UUID
- **THEN** system generates S3 presigned GET URL
- **AND** returns file metadata and access URL
- **AND** URL expires after configured time limit

#### Scenario: Delete S3 file
- **WHEN** authorized user requests file deletion
- **THEN** system removes file from S3 storage
- **AND** deletes corresponding MediaFile database record
- **AND** returns deletion confirmation

## REMOVED Requirements

### Requirement: Filesystem Storage Backend
**Reason**: Filesystem storage creates scaling limitations, backup challenges, and operational complexity. S3 provides better scalability, reliability, and cloud-native integration.

**Migration**: Existing filesystem-stored files must be migrated to S3 before removal. System will provide migration utility to transfer files and update database records.

### Requirement: Direct File Upload Endpoint
**Reason**: Direct upload endpoint was specific to filesystem storage. S3 uses presigned URLs for direct client-to-S3 uploads, which is more secure and scalable.

**Migration**: Clients must use the prepare-upload workflow to get S3 presigned URLs instead of direct file uploads to the backend.

### Requirement: Storage Backend Selection
**Reason**: With filesystem removal, backend selection logic becomes unnecessary. All storage operations will use S3 by default.

**Migration**: Configuration code for storage backend selection will be removed, and all storage services will default to S3 implementation.