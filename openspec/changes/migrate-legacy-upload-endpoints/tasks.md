# Implementation Tasks

## 1. Backend Improvements

- [ ] 1.1 Update `upload_preparation.py` để return `file_uuid` explicitly trong prepare response
- [ ] 1.2 Add S3 HEAD request verification trong `/api/v1/media/confirm` endpoint
- [ ] 1.3 Add error handling cho S3 verification failures (network, unavailable, not found)
- [ ] 1.4 Add deprecation notices vào docstrings của legacy endpoints:
  - [ ] `PUT /users/update_avatar/{user_uuid}`
  - [ ] `PUT /courses/{course_uuid}/thumbnail`
  - [ ] `PUT /orgs/{org_id}/logo`
  - [ ] `PUT /orgs/{org_id}/thumbnail`
  - [ ] `PUT /orgs/{org_id}/preview`
- [ ] 1.5 Add logging cho file verification events (success, failure, not found)
- [ ] 1.6 Update API documentation để reflect deprecation và khuyến khích dùng unified media API

## 2. Frontend - User Avatar Upload Migration

- [ ] 2.1 Update `UserEditGeneral.tsx` để sử dụng `useFileUpload` hook
- [ ] 2.2 Replace `updateUserAvatar()` call với `upload()` from hook
- [ ] 2.3 Set resource_type="user_avatar" và resource_id=user_uuid
- [ ] 2.4 Update success/error handling để work với new upload flow
- [ ] 2.5 Test avatar upload flow (prepare → S3 upload → confirm)
- [ ] 2.6 Remove `updateUserAvatar()` function từ `services/users/users.ts`

## 3. Frontend - Course Thumbnail Upload Migration

- [ ] 3.1 Update `ThumbnailUpdate.tsx` để sử dụng `useFileUpload` hook
- [ ] 3.2 Replace `updateCourseThumbnail()` call với `upload()` from hook
- [ ] 3.3 Set resource_type="course_thumbnail_image" hoặc "course_thumbnail_video" dựa vào type
- [ ] 3.4 Set resource_id=course_uuid
- [ ] 3.5 Handle both image và video uploads với appropriate resource types
- [ ] 3.6 Update success/error handling và state management
- [ ] 3.7 Test thumbnail upload flow cho cả image và video
- [ ] 3.8 Remove `updateCourseThumbnail()` function từ `services/courses/courses.ts`

## 4. Frontend - Organization Images Upload Migration

- [ ] 4.1 Update `OrgEditImages.tsx` để sử dụng `useFileUpload` hook
- [ ] 4.2 Migrate logo upload:
  - [ ] Replace `uploadOrganizationLogo()` với `upload()`
  - [ ] Set resource_type="org_logo", resource_id=org_uuid
  - [ ] Test logo upload flow
- [ ] 4.3 Migrate thumbnail upload:
  - [ ] Replace `uploadOrganizationThumbnail()` với `upload()`
  - [ ] Set resource_type="org_thumbnail", resource_id=org_uuid
  - [ ] Test thumbnail upload flow
- [ ] 4.4 Migrate preview upload:
  - [ ] Replace `uploadOrganizationPreview()` với `upload()`
  - [ ] Set resource_type="org_preview", resource_id=org_uuid
  - [ ] Handle multiple preview uploads (batch)
  - [ ] Test preview upload flow
- [ ] 4.5 Update success/error handling cho tất cả 3 upload types
- [ ] 4.6 Remove legacy functions từ `services/settings/org.ts`:
  - [ ] `uploadOrganizationLogo()`
  - [ ] `uploadOrganizationThumbnail()`
  - [ ] `uploadOrganizationPreview()`

## 5. Frontend Cleanup

- [ ] 5.1 Remove dead filesystem fallback code trong `useFileUpload.ts`:
  - [ ] Remove `else` block xử lý backend upload (filesystem path)
  - [ ] Remove filesystem-related checks
- [ ] 5.2 Remove `uploadFileToBackend()` function từ `services/media/upload.ts`
- [ ] 5.3 Verify `useFileUpload` hook chỉ handle S3 flow (no filesystem references)
- [ ] 5.4 Update TypeScript types nếu cần (remove filesystem-related types)
- [ ] 5.5 Review và cleanup any unused imports

## 6. Testing & Validation

- [ ] 6.1 Test user avatar upload:
  - [ ] Upload new avatar
  - [ ] Verify file exists in S3
  - [ ] Verify metadata saved correctly
  - [ ] Verify avatar displays correctly
- [ ] 6.2 Test course thumbnail upload:
  - [ ] Upload image thumbnail
  - [ ] Upload video thumbnail
  - [ ] Verify files exist in S3
  - [ ] Verify thumbnails display correctly
- [ ] 6.3 Test organization images upload:
  - [ ] Upload logo
  - [ ] Upload thumbnail
  - [ ] Upload multiple previews
  - [ ] Verify all files exist in S3
  - [ ] Verify images display correctly
- [ ] 6.4 Test error scenarios:
  - [ ] Invalid file type
  - [ ] File size exceeds limit
  - [ ] Network failure during upload
  - [ ] S3 unavailable
  - [ ] Fake upload attempt (confirm without actual upload)
- [ ] 6.5 Verify backward compatibility:
  - [ ] Legacy endpoints vẫn hoạt động
  - [ ] Old clients vẫn có thể upload
- [ ] 6.6 Performance testing:
  - [ ] Upload speed comparison
  - [ ] Backend CPU/memory usage
  - [ ] Concurrent uploads

## 7. Documentation

- [ ] 7.1 Update API documentation với deprecation notices
- [ ] 7.2 Document new unified media upload flow
- [ ] 7.3 Add migration guide cho clients sử dụng legacy endpoints
- [ ] 7.4 Document resource type mapping (user_avatar, course_thumbnail_*, org_*)
- [ ] 7.5 Update frontend component documentation

## 8. Deployment

- [ ] 8.1 Deploy backend changes (file_uuid return, verification, deprecation notices)
- [ ] 8.2 Deploy frontend changes (migrate components sang useFileUpload)
- [ ] 8.3 Monitor error logs cho upload failures
- [ ] 8.4 Monitor S3 metrics (upload count, bandwidth)
- [ ] 8.5 Monitor legacy endpoint usage (track deprecation adoption)
- [ ] 8.6 Plan sunset timeline cho legacy endpoints (nếu cần)

## Notes

- **S3-Only Architecture**: Hệ thống đã remove filesystem storage, chỉ còn S3-only
- Tasks có thể thực hiện song song: Backend (1) và Frontend (2, 3, 4) có thể develop đồng thời
- Testing (6) nên thực hiện sau khi hoàn thành backend và frontend changes
- Legacy endpoints vẫn hoạt động nhưng uploads sẽ đi lên S3 (không có filesystem fallback)
- Legacy endpoints nên giữ ít nhất 6 tháng sau khi deploy new API để clients có thời gian migrate
- Consider adding analytics/metrics để track adoption rate của unified media API
- Tất cả uploads (legacy và new) đều phải upload lên S3 bucket
