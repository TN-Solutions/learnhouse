## ADDED Requirements

### Requirement: Separate API Container

The system SHALL provide separate container for API service with FastAPI backend.

#### Scenario: API container build thành công

- **KHI** chạy Docker build cho apps/api/Dockerfile
- **THÌ** tạo thành công container image với Python 3.12 và FastAPI
- **VÀ** expose port 9000 cho external access
- **VÀ** include tất cả required dependencies qua UV package manager

#### Scenario: API container hoạt động với external database

- **KHI** API container start với environment variables cho PostgreSQL và Redis
- **THÌ** kết nối thành công đến external database services
- **VÀ** API endpoints hoạt động bình thường
- **VÀ** health check trả về status 200

### Requirement: Separate Web Container

The system SHALL provide separate container for Web service with Next.js frontend.

#### Scenario: Web container build thành công

- **KHI** chạy Docker build cho apps/web/Dockerfile
- **THÌ** tạo thành công container image với Node.js 22 và Next.js
- **VÀ** expose port 3000 cho external access
- **VÀ** sử dụng standalone build mode cho production optimization

#### Scenario: Web container kết nối đến API

- **KHI** Web container start với API_URL environment variable
- **THÌ** kết nối thành công đến API container
- **VÀ** frontend functionality hoạt động bình thường
- **VÀ** authentication flow hoạt động đúng

### Requirement: Production Docker Compose

The system SHALL provide docker-compose.production.yml with API and Web services.

#### Scenario: Docker Compose start thành công

- **KHI** chạy docker-compose -f docker-compose.production.yml up -d
- **THÌ** cả API và Web containers start thành công
- **VÀ** networking được cấu hình đúng giữa containers
- **VÀ** external database connections được thiết lập

#### Scenario: Environment variables loading

- **KHI** Docker Compose load environment từ ENV_FILE
- **THÌ** tất cả required variables được load correctly
- **VÀ** database connection strings được format đúng
- **VÀ** API endpoints accessible từ Web container

## MODIFIED Requirements

### Requirement: Deployment Automation

The system SHALL automate deployment process via GitHub Actions with SSH-based deployment.

#### Scenario: Automated build và deploy

- **KHI** push code đến main branch
- **THÌ** GitHub Actions trigger build process
- **VÀ** build API và Web containers thành công
- **VÀ** deploy containers đến production server qua SSH

#### Scenario: Server environment configuration

- **KHI** GitHub Actions deploy với CLOUD_HOST, CLOUD_SSH_KEY, CLOUD_USERNAME
- **THÌ** SSH connection được thiết lập thành công
- **VÀ** containers được deploy đến server
- **VÀ** environment variables được configure correctly

#### Scenario: Rollback mechanism

- **KHI** deployment fails hoặc cần rollback
- **THÌ** GitHub Actions có khả năng rollback về previous version
- **VÀ** restore previous containers thành công
- **VÀ** system functionality được maintained

### Requirement: External Database Integration

The system SHALL integrate with external PostgreSQL and Redis services instead of bundled containers.

#### Scenario: PostgreSQL connection

- **KHI** API container start với external PostgreSQL credentials
- **THÌ** kết nối thành công đến database
- **VÀ** migrations chạy thành công với Alembic
- **VÀ** data operations hoạt động bình thường

#### Scenario: Redis connection

- **KHI** API container start với external Redis credentials
- **THÌ** kết nối thành công đến Redis
- **VÀ** session management hoạt động đúng
- **VÀ** caching functionality được maintained

## REMOVED Requirements

### Requirement: Bundled Database Services

**Lý do**: External database services provide better reliability, scalability, and maintenance
**Chuyển đổi**: Replace bundled PostgreSQL and Redis containers with external service connections

#### Scenario: Remove database containers

- **KHI** deploy với architecture mới
- **THÌ** không còn PostgreSQL và Redis containers trong Docker Compose
- **VÀ** database connections được redirect đến external services
- **VÀ** data persistence được maintained qua external providers

### Requirement: Monolithic Container Architecture

**Lý do**: Separate containers provide better scaling, resource management, and deployment flexibility
**Chuyển đổi**: Replace single container approach with separate API and Web containers

#### Scenario: Remove monolithic Dockerfile

- **KHI** implement architecture mới
- **THÌ** không còn Dockerfile gốc chứa cả API và Web
- **VÀ** mỗi service có Dockerfile riêng biệt
- **VÀ** deployment process được optimized cho multi-container architecture
