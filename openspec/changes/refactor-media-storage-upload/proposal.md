# Refactor Media Storage Upload

## Tại sao

Hệ thống media upload hiện tại có những lỗi nghiêm trọng: file luôn được lưu vào filesystem ngay cả khi S3 được cấu hình, và việc truy xuất media luôn fetch từ filesystem và bỏ qua S3. Điều này gây ra lưu trữ trùng lặp, lãng phí không gian đĩa, và làm cho tính năng S3 hoàn toàn không sử dụng được trong production. Ngoài ra, kiến trúc thiếu sự phân tách trách nhiệm—frontend không cần phải biết về storage backends.

## Thay đổi gì

- **BREAKING**: Tách biệt hoàn toàn S3 và filesystem storage implementations trong backend
- **ADDED**: Hỗ trợ direct S3 upload thông qua presigned URLs khi S3 được bật
- **MODIFIED**: Backend API trả về appropriate upload endpoints dựa trên storage configuration
- **MODIFIED**: Frontend trở thành storage-agnostic, dựa vào backend để xác định storage mechanism
- **ADDED**: S3 media retrieval với presigned URLs hoặc streaming khi S3 được bật
- **MODIFIED**: Static file serving trở thành conditional dựa trên storage configuration
- **FIXED**: Loại bỏ lỗi duplicate file storage (file được lưu cả filesystem và S3)
- **FIXED**: Loại bỏ hardcoded S3 bucket name, sử dụng configuration thay thế

## Tác động

### Affected Specs

- **CREATED**: `media-storage` - New capability defining storage abstraction layer

### Affected Code

- `apps/api/src/services/utils/upload_content.py` - Complete refactor của upload logic
- `apps/api/src/routers/*` - Update upload endpoints để hỗ trợ storage-agnostic flow
- `apps/api/app.py` - Conditional static file mounting dựa trên storage type
- `apps/api/config/config.py` - Enhanced S3 configuration
- `apps/web/services/media/media.ts` - Simplified để trở thành storage-agnostic
- `apps/web/components/Objects/*` - Update upload components để sử dụng new API
- All upload-related services (images, videos, PDFs, avatars, thumbnails)

### Migration Impact

- **Breaking Change**: Existing S3 configurations sẽ cần updated environment variables
- **Storage Migration**: Files được lưu trong filesystem với S3 được bật có thể cần migration
- **API Changes**: Upload endpoints sẽ trả về different response formats (presigned URLs vs direct upload)
- **Frontend Changes**: Upload components cần xử lý cả direct và presigned URL uploads

### Benefits

- ✅ S3 upload thực sự hoạt động và files có thể truy cập từ S3
- ✅ Không có duplicate storage (files chỉ trong configured storage)
- ✅ Better separation of concerns (frontend storage-agnostic)
- ✅ Improved security (presigned URLs với expiration)
- ✅ Better scalability (offload upload đến S3 trực tiếp)
- ✅ Reduced backend load (direct-to-S3 uploads)

### Risks

- Migration complexity cho existing deployments
- Potential downtime trong storage backend switch
- Need for comprehensive testing của cả storage paths
