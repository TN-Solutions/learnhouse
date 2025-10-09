# Thông số kỹ thuật Media Storage

## Yêu cầu THÊM MỚI

### Yêu cầu: Trừu tượng hóa Storage Backend

Hệ thống SHALL cung cấp một lớp trừu tượng hóa storage backend hỗ trợ nhiều triển khai storage (filesystem và storage tương thích S3) với giao diện thống nhất.

#### Kịch bản: Khởi tạo filesystem storage backend

- **WHEN** hệ thống được cấu hình với `content_delivery.type = "filesystem"`
- **THEN** filesystem storage backend SHALL được khởi tạo
- **AND** các file SHALL được lưu trữ trong thư mục `content/` cục bộ
- **AND** không có S3 client nào SHALL được khởi tạo

#### Kịch bản: Khởi tạo S3 storage backend

- **WHEN** hệ thống được cấu hình với `content_delivery.type = "s3api"`
- **AND** cấu hình S3 (bucket_name, endpoint_url) được cung cấp
- **THEN** S3 storage backend SHALL được khởi tạo
- **AND** một S3 client SHALL được tạo với cấu hình được cung cấp
- **AND** không có storage filesystem cục bộ nào SHALL được sử dụng cho các upload mới

#### Kịch bản: Storage backend cung cấp upload URL

- **WHEN** một yêu cầu upload file được thực hiện
- **THEN** storage backend SHALL trả về một upload URL phù hợp với loại của nó
- **AND** đối với filesystem backend, nó SHALL trả về một API endpoint upload trực tiếp
- **AND** đối với S3 backend, nó SHALL trả về một presigned POST URL
- **AND** response SHALL bao gồm phương thức upload (POST) và các trường bắt buộc

#### Kịch bản: Storage backend cung cấp download URL

- **WHEN** một yêu cầu download/truy cập file được thực hiện
- **THEN** storage backend SHALL trả về một URL có thể truy cập công khai
- **AND** đối với filesystem backend, nó SHALL trả về một đường dẫn file tĩnh
- **AND** đối với S3 backend, nó SHALL trả về một public S3 URL hoặc presigned GET URL

### Yêu cầu: Chuẩn bị Upload URL

Hệ thống SHALL cung cấp một API endpoint để chuẩn bị upload file bằng cách tạo các upload URL phù hợp dựa trên storage backend đã cấu hình.

#### Kịch bản: Chuẩn bị upload cho filesystem storage

- **WHEN** một client yêu cầu chuẩn bị upload với file metadata
- **AND** storage backend là filesystem
- **THEN** hệ thống SHALL trả về một direct upload endpoint URL
- **AND** response SHALL bao gồm đường dẫn file đích
- **AND** đường dẫn file SHALL theo mẫu `content/{resource_type}/{uuid}/{filename}`
- **AND** response SHALL bao gồm public file URL cuối cùng

#### Kịch bản: Chuẩn bị upload cho S3 storage

- **WHEN** một client yêu cầu chuẩn bị upload với file metadata
- **AND** storage backend là S3
- **THEN** hệ thống SHALL tạo một S3 presigned POST URL
- **AND** presigned URL SHALL hết hạn sau 1 giờ
- **AND** presigned URL SHALL bao gồm các ràng buộc kích thước file (mặc định tối đa 100MB)
- **AND** presigned URL SHALL bao gồm xác thực content-type
- **AND** response SHALL bao gồm S3 upload URL và các trường form bắt buộc
- **AND** response SHALL bao gồm public file URL cuối cùng

#### Kịch bản: Xác thực file metadata trước khi chuẩn bị

- **WHEN** một client yêu cầu chuẩn bị upload
- **THEN** hệ thống SHALL xác thực loại file với các loại được phép
- **AND** hệ thống SHALL xác thực tên file để bảo mật (không có path traversal)
- **AND** hệ thống SHALL xác thực loại tài nguyên và ID tài nguyên
- **AND** nếu xác thực thất bại, hệ thống SHALL trả về lỗi 400 Bad Request

### Yêu cầu: Upload File Trực Tiếp

Hệ thống SHALL hỗ trợ upload file trực tiếp đến storage backend đã cấu hình.

#### Kịch bản: Upload file lên filesystem

- **WHEN** một client upload một file lên filesystem upload endpoint
- **AND** bao gồm đường dẫn file đích trong yêu cầu
- **THEN** hệ thống SHALL lưu file vào filesystem cục bộ
- **AND** file SHALL được lưu vào đường dẫn được chỉ định dưới `content/`
- **AND** các thư mục cần thiết SHALL được tạo nếu chưa tồn tại
- **AND** hệ thống SHALL trả về public file URL
- **AND** file metadata SHALL được lưu vào database

#### Kịch bản: Upload file lên S3 (client-side)

- **WHEN** một client nhận được một presigned S3 URL
- **AND** upload file trực tiếp lên S3 sử dụng presigned URL
- **THEN** file SHALL được lưu trữ trong S3 bucket
- **AND** upload SHALL thành công mà không có sự tham gia của backend
- **AND** client SHALL xác nhận upload với backend API
- **AND** backend SHALL lưu file metadata vào database

#### Kịch bản: Xử lý upload thất bại

- **WHEN** một upload file thất bại (lỗi mạng, timeout, v.v.)
- **THEN** hệ thống SHALL trả về một thông báo lỗi phù hợp
- **AND** không có file nào bị thiếu SHALL còn lại trong storage
- **AND** không có database metadata nào SHALL được tạo cho các upload thất bại
- **AND** client SHALL có thể thử lại upload

### Yêu cầu: Truy xuất Media File

Hệ thống SHALL cung cấp quyền truy cập vào các media file đã upload dựa trên storage backend đã cấu hình.

#### Kịch bản: Phục vụ file từ filesystem

- **WHEN** storage backend là filesystem
- **AND** một yêu cầu được thực hiện đến `/content/{path}`
- **THEN** hệ thống SHALL phục vụ file sử dụng FastAPI StaticFiles
- **AND** file SHALL được phục vụ với các content-type headers phù hợp
- **AND** nếu không tìm thấy file, trả về 404 Not Found

#### Kịch bản: Phục vụ file từ S3

- **WHEN** storage backend là S3
- **AND** một yêu cầu được thực hiện cho một file URL
- **THEN** hệ thống SHALL trả về public S3 URL hoặc tạo một presigned GET URL
- **AND** file SHALL có thể truy cập trực tiếp từ S3
- **AND** không có StaticFiles middleware nào SHALL được mount cho `/content`

#### Kịch bản: Xử lý file không tìm thấy

- **WHEN** một yêu cầu được thực hiện cho một file không tồn tại
- **THEN** hệ thống SHALL trả về 404 Not Found
- **AND** error response SHALL nhất quán trên tất cả storage backends

### Yêu cầu: Cấu hình Storage

Hệ thống SHALL hỗ trợ cấu hình storage toàn diện thông qua các biến môi trường và file cấu hình.

#### Kịch bản: Cấu hình filesystem storage

- **WHEN** hệ thống khởi động với cấu hình filesystem storage
- **THEN** hệ thống SHALL sử dụng thư mục `content/` mặc định để lưu trữ
- **AND** thư mục SHALL được tạo nếu chưa tồn tại
- **AND** không có cấu hình liên quan đến S3 nào SHALL được yêu cầu

#### Kịch bản: Cấu hình S3 storage

- **WHEN** hệ thống khởi động với cấu hình S3 storage
- **THEN** hệ thống SHALL yêu cầu cấu hình `bucket_name`
- **AND** hệ thống SHALL yêu cầu cấu hình `endpoint_url` (hoặc sử dụng mặc định của AWS)
- **AND** hệ thống SHALL sử dụng AWS credentials từ các biến môi trường
- **AND** nếu cấu hình S3 không đầy đủ, hệ thống SHALL không khởi động được với lỗi rõ ràng

#### Kịch bản: Xác thực kết nối S3 khi khởi động

- **WHEN** S3 storage được cấu hình
- **AND** hệ thống khởi động
- **THEN** hệ thống SHALL xác minh khả năng truy cập S3 bucket
- **AND** nếu S3 không thể truy cập, ghi log warning (không làm hỏng khởi động)
- **AND** cung cấp các thông báo lỗi rõ ràng cho các vấn đề cấu hình S3

### Yêu cầu: Quản lý File Metadata

Hệ thống SHALL theo dõi metadata cho tất cả các file đã upload trong database.

#### Kịch bản: Lưu file metadata khi upload

- **WHEN** một upload file hoàn thành thành công
- **THEN** hệ thống SHALL tạo một database record với:
  - Unique file UUID
  - Storage backend type (filesystem hoặc s3api)
  - File path trong storage
  - Public file URL
  - Content type
  - File size tính bằng bytes
  - Upload timestamp
  - Resource type (user_avatar, course_thumbnail, v.v.)
  - Resource ID (user UUID, course UUID, v.v.)

#### Kịch bản: Truy vấn file theo tài nguyên

- **WHEN** một yêu cầu được thực hiện để lấy các file cho một tài nguyên cụ thể
- **THEN** hệ thống SHALL trả về tất cả các file liên quan đến tài nguyên đó
- **AND** kết quả SHALL bao gồm file URLs, metadata, và upload timestamps
- **AND** kết quả SHALL được sắp xếp theo upload timestamp (mới nhất trước)

#### Kịch bản: Xóa file và metadata

- **WHEN** một yêu cầu xóa file được thực hiện
- **THEN** hệ thống SHALL xóa file khỏi storage (filesystem hoặc S3)
- **AND** hệ thống SHALL xóa database metadata record
- **AND** nếu xóa storage thất bại, ghi log lỗi nhưng vẫn xóa metadata
- **AND** nếu không tìm thấy file trong storage, vẫn xóa metadata (dọn dẹp các bản ghi mồ côi)

### Yêu cầu: Bảo mật và Xác thực

Hệ thống SHALL thực hiện các biện pháp bảo mật để ngăn chặn truy cập trái phép và các upload độc hại.

#### Kịch bản: Xác thực loại file

- **WHEN** một upload file được khởi tạo
- **THEN** hệ thống SHALL xác thực loại file với một allowlist
- **AND** chỉ các MIME types được phê duyệt SHALL được chấp nhận (images: image/png, image/jpeg; videos: video/mp4, video/webm; documents: application/pdf)
- **AND** file extension SHALL được xác thực với MIME type
- **AND** từ chối các upload có extension và MIME type không khớp

#### Kịch bản: Xác thực kích thước file

- **WHEN** một upload file được khởi tạo
- **THEN** hệ thống SHALL thực thi các giới hạn kích thước file tối đa
- **AND** images SHALL bị giới hạn 10MB theo mặc định
- **AND** videos SHALL bị giới hạn 100MB theo mặc định
- **AND** PDFs SHALL bị giới hạn 50MB theo mặc định
- **AND** giới hạn kích thước SHALL có thể cấu hình theo loại file

#### Kịch bản: Ngăn chặn path traversal

- **WHEN** một upload file bao gồm một filename
- **THEN** hệ thống SHALL làm sạch filename
- **AND** xóa hoặc mã hóa các path separators (/, \)
- **AND** xóa các tham chiếu thư mục cha (..)
- **AND** giới hạn độ dài filename thành 255 ký tự
- **AND** từ chối các filename có null bytes hoặc control characters

#### Kịch bản: Bảo mật S3 presigned URL

- **WHEN** tạo S3 presigned URLs
- **THEN** URL SHALL hết hạn sau một khoảng thời gian xác định (mặc định 1 giờ)
- **AND** URL SHALL được giới hạn trong bucket và key cụ thể
- **AND** URL SHALL bao gồm các ràng buộc content-length
- **AND** URL SHALL bao gồm xác thực content-type
- **AND** URL SHALL là single-use (không thể tái sử dụng sau khi upload thành công)

### Yêu cầu: Xử lý Lỗi và Khả năng Chống chịu

Hệ thống SHALL xử lý lỗi một cách nhẹ nhàng và cung cấp các thông báo lỗi rõ ràng.

#### Kịch bản: Xử lý lỗi kết nối S3

- **WHEN** S3 upload hoặc retrieval thất bại do các vấn đề mạng
- **THEN** hệ thống SHALL trả về lỗi 503 Service Unavailable
- **AND** bao gồm một retry-after header gợi ý thời gian thử lại
- **AND** ghi log lỗi với đầy đủ ngữ cảnh để gỡ lỗi
- **AND** không tiết lộ S3 credentials hoặc chi tiết nội bộ trong các thông báo lỗi

#### Kịch bản: Xử lý lỗi filesystem

- **WHEN** các thao tác filesystem thất bại (đĩa đầy, bị từ chối quyền)
- **THEN** hệ thống SHALL trả về lỗi 500 Internal Server Error
- **AND** ghi log lỗi với đường dẫn file và thao tác đã thử
- **AND** không tiết lộ các đường dẫn file nội bộ trong các thông báo lỗi hướng đến người dùng

#### Kịch bản: Xử lý hết hạn presigned URL

- **WHEN** một client cố gắng sử dụng một presigned URL đã hết hạn
- **THEN** S3 SHALL từ chối upload với 403 Forbidden
- **AND** client SHALL có thể yêu cầu một presigned URL mới
- **AND** frontend SHALL phát hiện hết hạn và tự động thử lại với URL mới

### Yêu cầu: Tương thích Ngược

Hệ thống SHALL duy trì tính tương thích với các tham chiếu file hiện có trong thời kỳ di chuyển.

#### Kịch bản: Truy cập các file filesystem cũ

- **WHEN** S3 storage được bật
- **AND** một yêu cầu được thực hiện cho một file được upload trước khi di chuyển S3
- **THEN** hệ thống SHALL kiểm tra database để tìm vị trí file
- **AND** nếu file nằm trong filesystem, phục vụ nó từ filesystem
- **AND** nếu file nằm trong S3, phục vụ nó từ S3
- **AND** cung cấp định dạng URL nhất quán bất kể storage backend

#### Kịch bản: Di chuyển các file hiện có

- **WHEN** một di chuyển file được khởi tạo
- **THEN** hệ thống SHALL sao chép các file từ filesystem sang S3
- **AND** cập nhật database metadata để phản ánh vị trí lưu trữ mới
- **AND** xác minh tính toàn vẹn của file sau khi di chuyển (kích thước, checksum)
- **AND** tùy chọn xóa bản sao filesystem sau khi di chuyển thành công
- **AND** cung cấp báo cáo tiến trình di chuyển
