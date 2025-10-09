## Bối cảnh

Hệ thống LearnHouse hiện tại sử dụng kiến trúc Docker monolithic với cả API và Web trong một container. Điều này gây ra các vấn đề:

- Khó khăn trong scaling từng service riêng biệt
- Phụ thuộc vào bundled database services (PostgreSQL, Redis)
- Deployment workflow phức tạp và không linh hoạt
- Resource usage không tối ưu

Yêu cầu mới cần tách biệt services, sử dụng external databases và tự động hóa deployment qua GitHub Actions với SSH-based deployment.

## Mục tiêu / Không phải mục tiêu

### Mục tiêu

- Tách biệt API và Web thành containers riêng biệt
- Sử dụng external PostgreSQL và Redis services
- Tự động hóa deployment qua GitHub Actions
- Tối ưu hóa resource usage và startup time
- Simplify production deployment process
- Hỗ trợ scaling từng service độc lập

### Không phải mục tiêu

- Thay đổi logic ứng dụng hoặc API endpoints
- Migration database schema
- Thay đổi frontend functionality
- Thêm monitoring hoặc logging phức tạp
- Multi-region deployment

## Quyết định

### Quyết định 1: Separate Containers

- **Cái gì**: API và Web trong containers riêng biệt
- **Tại sao**: Independent scaling, deployment, và resource management
- **Các phương án đã xem xét**:
  - Single container (hiện tại) - ❌ Không scalable
  - Multi-container với shared volume - ❌ Phức tạp
  - Separate containers - ✅ Linh hoạt và hiệu quả

### Quyết định 2: External Database Services

- **Cái gì**: Không bundle PostgreSQL và Redis trong Docker
- **Tại sao**: Production-ready, managed services, better performance
- **Các phương án đã xem xét**:
  - Docker containers cho databases - ❌ Không production-ready
  - Managed cloud services - ✅ Reliable và scalable
  - Self-hosted databases - ❌ High maintenance

### Quyết định 3: Server-side Nginx Configuration

- **Cái gì**: Tạo nginx.conf file riêng biệt cho server-side reverse proxy
- **Tại sao**: Flexible configuration, separate from containers, easier management
- **Các phương án đã xem xét**:
  - Nginx container - ❌ Adds complexity to Docker setup
  - Cloud load balancer - ❌ Additional cost and dependency
  - Server-side nginx - ✅ Simple, cost-effective, standard practice

### Quyết định 4: GitHub Actions + SSH Deployment

- **Cái gì**: Auto deploy qua GitHub Actions với SSH
- **Tại sao**: Native Git workflow, automated, secure
- **Các phương án đã xem xét**:
  - Manual deployment - ❌ Error-prone
  - Docker Swarm - ❌ Overkill cho current scale
  - Kubernetes - ❌ Quá phức tạp
  - GitHub Actions + SSH - ✅ Simple và effective

### Quyết định 4: Environment Variables Management

- **Cái gì**: Server environment với CLOUD_HOST, CLOUD_SSH_KEY, CLOUD_USERNAME, ENV_FILE
- **Tại sao**: Secure, flexible, follows 12-factor app principles
- **Các phương án đã xem xét**:
  - Hardcoded values - ❌ Not secure
  - Docker secrets - ❌ Complex cho current setup
  - Environment files - ✅ Simple và standard

## Rủi ro / Trade-offs

### Rủi ro

- **Deployment complexity increase** → Mitigation: Comprehensive documentation and testing
- **Service communication latency** → Mitigation: Proper networking configuration
- **Environment management overhead** → Mitigation: Standardized templates and scripts
- **Rollback complexity** → Mitigation: Automated rollback mechanisms in GitHub Actions

### Trade-offs

- **Simplicity vs Scalability**: Chọn scalability thay vì simplicity của monolithic approach
- **Control vs Managed Services**: Chọn managed databases thay vì self-hosted control
- **Automation vs Flexibility**: Chọn automated deployment thay vì manual control

## Kế hoạch Migration

### Phase 1: Preparation

1. Backup current Docker configuration
2. Setup external database services
3. Prepare server environment
4. Create backup and rollback plans

### Phase 2: Implementation

1. Create new Dockerfiles
2. Setup GitHub Actions workflow
3. Configure server deployment scripts
4. Test in staging environment

### Phase 3: Deployment

1. Deploy to production with zero-downtime
2. Monitor performance and errors
3. Optimize based on metrics
4. Update documentation

### Phase 4: Cleanup

1. Remove old Docker configurations
2. Archive old deployment scripts
3. Update team documentation
4. Conduct post-mortem

## Rollback Plan

### Immediate Rollback (< 5 minutes)

- Switch to previous Docker Compose configuration
- Restore bundled database services
- Revert GitHub Actions workflow

### Full Rollback (< 30 minutes)

- Restore from database backup
- Deploy previous container images
- Verify all services functionality

## Câu hỏi còn mở

- Database migration strategy cho existing data?
- SSL certificate management cho external services?
- Backup và disaster recovery procedures?
- Monitoring và alerting setup cho new architecture?
- Cost implications của external database services?
