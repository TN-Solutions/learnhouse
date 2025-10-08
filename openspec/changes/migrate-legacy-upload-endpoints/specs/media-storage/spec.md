# Media Storage Spec Deltas

## MODIFIED Requirements

### Requirement: Chuẩn bị Upload URL

Hệ thống SHALL cung cấp một API endpoint để chuẩn bị upload file bằng cách tạo S3 presigned POST URLs.

#### Kịch bản: Chuẩn bị S3 upload

- **WHEN** một client yêu cầu chuẩn bị upload với file metadata
- **THEN** hệ thống SHALL tạo một S3 presigned POST URL
- **AND** presigned URL SHALL hết hạn sau 1 giờ
- **AND** presigned URL SHALL bao gồm các ràng buộc kích thước file (mặc định tối đa 100MB)
- **AND** presigned URL SHALL bao gồm xác thực content-type
- **AND** response SHALL bao gồm S3 upload URL và các trường form bắt buộc
- **AND** response SHALL bao gồm public file URL cuối cùng
- **AND** response SHALL bao gồm `file_uuid` để client tracking và confirm

#### Kịch bản: Xác thực file metadata trước khi chuẩn bị

- **WHEN** một client yêu cầu chuẩn bị upload
- **THEN** hệ thống SHALL xác thực loại file với các loại được phép
- **AND** hệ thống SHALL xác thực tên file để bảo mật (không có path traversal)
- **AND** hệ thống SHALL xác thực loại tài nguyên và ID tài nguyên
- **AND** nếu xác thực thất bại, hệ thống SHALL trả về lỗi 400 Bad Request

### Requirement: Upload File Trực Tiếp

Hệ thống SHALL hỗ trợ upload file trực tiếp lên S3 thông qua presigned URLs.

#### Kịch bản: Upload file lên S3 (client-side)

- **WHEN** một client nhận được một presigned S3 URL từ prepare endpoint
- **AND** upload file trực tiếp lên S3 sử dụng presigned URL
- **THEN** file SHALL được lưu trữ trong S3 bucket
- **AND** upload SHALL thành công mà không có sự tham gia của backend
- **AND** client SHALL xác nhận upload với backend API bằng confirm endpoint
- **AND** backend SHALL verify file existence trong S3 trước khi lưu metadata
- **AND** backend SHALL lưu file metadata vào database nếu file tồn tại
- **AND** nếu file không tồn tại trong S3, backend SHALL trả về lỗi 400 Bad Request

#### Kịch bản: Xử lý upload thất bại

- **WHEN** một S3 upload thất bại (lỗi mạng, timeout, S3 errors)
- **THEN** client SHALL nhận được error từ S3
- **AND** client SHALL có thể request presigned URL mới và retry upload
- **AND** không có database metadata nào SHALL được tạo cho các upload thất bại
- **AND** expired presigned URLs SHALL bị S3 reject với 403 Forbidden

## ADDED Requirements

### Requirement: Resource Type Mapping

Hệ thống SHALL hỗ trợ các resource types chuẩn cho các loại uploads phổ biến.

#### Kịch bản: Upload user avatar

- **WHEN** client upload user avatar
- **THEN** resource_type SHALL là "user_avatar"
- **AND** resource_id SHALL là user UUID
- **AND** file path SHALL theo pattern `user_avatar/{user_uuid}/{file_uuid}.{ext}`

#### Kịch bản: Upload course thumbnail

- **WHEN** client upload course thumbnail (image hoặc video)
- **THEN** resource_type SHALL là "course_thumbnail_image" hoặc "course_thumbnail_video"
- **AND** resource_id SHALL là course UUID
- **AND** file path SHALL theo pattern `course_thumbnail_{type}/{course_uuid}/{file_uuid}.{ext}`

#### Kịch bản: Upload organization images

- **WHEN** client upload organization logo, thumbnail, hoặc preview
- **THEN** resource_type SHALL là "org_logo", "org_thumbnail", hoặc "org_preview"
- **AND** resource_id SHALL là organization UUID
- **AND** file path SHALL theo pattern `{resource_type}/{org_uuid}/{file_uuid}.{ext}`

#### Kịch bản: Upload activity block media

- **WHEN** client upload activity block media (image, video, PDF)
- **THEN** resource_type SHALL là "activity_block"
- **AND** resource_id SHALL là activity UUID
- **AND** file path SHALL theo pattern `activity_block/{activity_uuid}/{file_uuid}.{ext}`

### Requirement: File Existence Verification

Hệ thống SHALL xác minh file tồn tại trong storage trước khi lưu metadata vào database.

#### Kịch bản: Verify S3 upload success

- **WHEN** client confirms S3 upload completion
- **AND** backend nhận được confirm request với file_uuid và file_path
- **THEN** backend SHALL thực hiện S3 HEAD request để verify file existence
- **AND** nếu file tồn tại, backend SHALL lưu metadata vào database
- **AND** nếu file không tồn tại, backend SHALL trả về lỗi 400 với message "File not found in S3"

#### Kịch bản: Handle verification failure

- **WHEN** S3 HEAD request thất bại (network error, S3 unavailable)
- **THEN** backend SHALL trả về lỗi 503 Service Unavailable
- **AND** backend SHALL log error với full context cho debugging
- **AND** client SHALL có thể retry confirm request

#### Kịch bản: Prevent fake uploads

- **WHEN** malicious client cố gắng confirm upload mà không thực sự upload file
- **THEN** backend verification SHALL phát hiện file không tồn tại
- **AND** backend SHALL reject confirm request với 400 Bad Request
- **AND** không có metadata record nào SHALL được tạo trong database

### Requirement: Legacy Endpoint Compatibility

Hệ thống SHALL duy trì backward compatibility với legacy upload endpoints trong thời gian migration, nhưng tất cả uploads SHALL được chuyển sang S3.

#### Kịch bản: Legacy user avatar upload

- **WHEN** client sử dụng legacy endpoint `PUT /users/update_avatar/{user_uuid}`
- **THEN** hệ thống SHALL vẫn accept FormData upload
- **AND** file SHALL được upload lên S3 bucket
- **AND** endpoint documentation SHALL mark endpoint as deprecated
- **AND** response SHALL khuyến khích dùng unified `/api/v1/media` API

#### Kịch bản: Legacy course thumbnail upload

- **WHEN** client sử dụng legacy endpoint `PUT /courses/{course_uuid}/thumbnail`
- **THEN** hệ thống SHALL vẫn accept FormData upload với thumbnail và thumbnail_type
- **AND** file SHALL được upload lên S3 bucket
- **AND** endpoint documentation SHALL mark endpoint as deprecated
- **AND** response SHALL khuyến khích dùng unified `/api/v1/media` API

#### Kịch bản: Legacy organization images upload

- **WHEN** client sử dụng legacy endpoints `PUT /orgs/{org_id}/logo`, `/thumbnail`, hoặc `/preview`
- **THEN** hệ thống SHALL vẫn accept FormData upload
- **AND** file SHALL được upload lên S3 bucket
- **AND** endpoint documentation SHALL mark endpoints as deprecated
- **AND** response SHALL khuyến khích dùng unified `/api/v1/media` API
