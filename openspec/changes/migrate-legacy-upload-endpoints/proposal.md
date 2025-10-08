# Migrate Legacy Upload Endpoints to S3 Flow

## Why

Hệ thống đã migrate sang **S3-only architecture** (loại bỏ filesystem storage), nhưng frontend vẫn còn 3 components sử dụng legacy direct upload pattern (FormData upload trực tiếp đến backend-specific endpoints) thay vì unified S3 presigned URL flow. Điều này gây ra:
- **Inconsistent architecture**: Một số uploads dùng unified media API với S3 presigned URLs (ImageBlock, VideoBlock), một số khác vẫn dùng legacy endpoints (User Avatar, Course Thumbnail, Org Images)
- **Backend bottleneck**: Legacy uploads phải đi qua backend server (receive FormData → upload to S3) thay vì client upload trực tiếp lên S3
- **Code duplication**: Duy trì 2 upload patterns khác nhau (legacy FormData endpoints và unified media API)
- **Scalability issues**: Backend phải xử lý file data trong memory thay vì offload hoàn toàn sang S3 với presigned URLs

Hiện tại **43% upload features** (3/7 components) vẫn chưa migrate sang unified media API.

## What Changes

### Frontend Changes
- **MODIFIED**: `UserEditGeneral` component - Migrate user avatar upload từ `updateUserAvatar()` sang `useFileUpload` hook
- **MODIFIED**: `ThumbnailUpdate` component - Migrate course thumbnail upload từ `updateCourseThumbnail()` sang `useFileUpload` hook
- **MODIFIED**: `OrgEditImages` component - Migrate organization images upload (logo, thumbnail, preview) từ `uploadOrganization*()` sang `useFileUpload` hook
- **REMOVED**: Legacy upload service functions: `updateUserAvatar()`, `updateCourseThumbnail()`, `uploadOrganizationLogo()`, `uploadOrganizationThumbnail()`, `uploadOrganizationPreview()`
- **CLEANUP**: Remove dead code trong `useFileUpload` hook (filesystem fallback path)

### Backend Changes
- **DEPRECATED**: Legacy upload endpoints (vẫn giữ cho backward compatibility nhưng khuyến khích dùng unified media API):
  - `PUT /api/v1/users/update_avatar/{user_uuid}`
  - `PUT /api/v1/courses/{course_uuid}/thumbnail`
  - `PUT /api/v1/orgs/{org_id}/logo`
  - `PUT /api/v1/orgs/{org_id}/thumbnail`
  - `PUT /api/v1/orgs/{org_id}/preview`
- **ADDED**: Return `file_uuid` explicitly trong `/api/v1/media/prepare` response
- **ADDED**: File existence verification trong `/api/v1/media/confirm` endpoint (S3 HEAD request)

### Resource Type Mapping
- User Avatar: `resource_type="user_avatar"`, `resource_id=user_uuid`
- Course Thumbnail Image: `resource_type="course_thumbnail_image"`, `resource_id=course_uuid`
- Course Thumbnail Video: `resource_type="course_thumbnail_video"`, `resource_id=course_uuid`
- Org Logo: `resource_type="org_logo"`, `resource_id=org_uuid`
- Org Thumbnail: `resource_type="org_thumbnail"`, `resource_id=org_uuid`
- Org Preview: `resource_type="org_preview"`, `resource_id=org_uuid`

## Impact

### Affected Specs
- **MODIFIED**: `media-storage` - Update requirements để:
  - Add file_uuid return trong prepare response
  - Add file existence verification trong confirm
  - Document resource types cho user/course/org uploads

### Affected Code

**Frontend:**
- `apps/web/components/Dashboard/Pages/UserAccount/UserEditGeneral/UserEditGeneral.tsx` - Migrate avatar upload
- `apps/web/components/Dashboard/Pages/Course/EditCourseGeneral/ThumbnailUpdate.tsx` - Migrate thumbnail upload
- `apps/web/components/Dashboard/Pages/Org/OrgEditImages/OrgEditImages.tsx` - Migrate org images upload
- `apps/web/services/users/users.ts` - Remove `updateUserAvatar()`
- `apps/web/services/courses/courses.ts` - Remove `updateCourseThumbnail()`
- `apps/web/services/settings/org.ts` - Remove `uploadOrganization*()` functions
- `apps/web/hooks/useFileUpload.ts` - Cleanup dead filesystem fallback code

**Backend:**
- `apps/api/src/services/media/upload_preparation.py` - Add file_uuid to response
- `apps/api/src/routers/media/upload.py` - Add S3 file existence verification
- `apps/api/src/routers/users/*` - Mark avatar endpoint as deprecated (in docs/comments)
- `apps/api/src/routers/courses/*` - Mark thumbnail endpoint as deprecated
- `apps/api/src/routers/orgs/*` - Mark image endpoints as deprecated

### Migration Impact
- **Non-breaking**: Legacy endpoints vẫn hoạt động cho backward compatibility
- **Client Migration**: New deployments nên dùng unified `/api/v1/media` API
- **Zero Downtime**: Có thể deploy frontend trước, backend sau (hoặc ngược lại)

### Benefits
- ✅ **100% S3 flow adoption** - Tất cả uploads đều dùng presigned URLs
- ✅ **Reduced backend load** - Tất cả uploads trực tiếp lên S3
- ✅ **Consistent architecture** - Single upload pattern trong toàn bộ codebase
- ✅ **Better scalability** - Không có file data đi qua backend server
- ✅ **Simplified maintenance** - Loại bỏ duplicate upload logic
- ✅ **Better security** - File existence verification ngăn fake uploads

### Risks
- **Low Risk**: Backward compatible với legacy endpoints
- **Testing Required**: Cần test kỹ tất cả 3 upload flows (avatar, thumbnail, org images)
- **Deployment Coordination**: Khuyến khích deploy frontend và backend cùng lúc để consistency
