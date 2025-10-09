## 1. Dọn dẹp Docker hiện tại

- [x] 1.1 Xóa Dockerfile gốc
- [x] 1.2 Xóa docker-compose.yml gốc
- [x] 1.3 Xóa .dockerignore gốc
- [x] 1.4 Giữ lại nginx.conf như file config tham khảo

## 2. Tạo Dockerfile cho API service

- [x] 2.1 Tạo apps/api/Dockerfile với Python 3.12 base
- [x] 2.2 Cấu hình UV package manager
- [x] 2.3 Tối ưu hóa multi-stage build
- [x] 2.4 Expose port 9000 cho FastAPI
- [x] 2.5 Cấu hình production-ready settings

## 3. Tạo Dockerfile cho Web service

- [x] 3.1 Tạo apps/web/Dockerfile với Node.js 22 base
- [x] 3.2 Cấu hình pnpm package manager
- [x] 3.3 Tối ưu hóa Next.js standalone build
- [x] 3.4 Expose port 3000 cho Next.js
- [x] 3.5 Cấu hình production-ready settings

## 4. Tạo Docker Compose production và Nginx config

- [x] 4.1 Tạo docker-compose.production.yml
- [x] 4.2 Định nghĩa api service với port 9000
- [x] 4.3 Định nghĩa web service với port 3000
- [x] 4.4 Cấu hình networking giữa services
- [x] 4.5 Cấu hình environment variables từ external file
- [x] 4.6 Tạo nginx.conf file cho server-side reverse proxy

## 5. Tạo GitHub Actions workflow

- [x] 5.1 Tạo .github/workflows/deploy.yml
- [x] 5.2 Cấu hình build steps cho API và Web
- [x] 5.3 Cấu hình SSH deployment với server secrets
- [x] 5.4 Thêm environment variables validation
- [x] 5.5 Cấu hình rollback mechanism

## 6. Cấu hình Server Environment

- [x] 6.1 Tạo deployment script cho server
- [x] 6.2 Cấu hình SSH key authentication
- [x] 6.3 Tạo environment file template
- [x] 6.4 Cấu hình service management (systemd)
- [x] 6.5 Thêm health checks và monitoring

## 7. Testing và Validation

- [ ] 7.1 Test local Docker builds
- [ ] 7.2 Test GitHub Actions workflow
- [ ] 7.3 Test deployment to staging
- [ ] 7.4 Validate external services connectivity
- [ ] 7.5 Performance testing và optimization
