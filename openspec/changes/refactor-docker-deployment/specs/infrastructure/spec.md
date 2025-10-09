## ADDED Requirements

### Requirement: Server Environment Management

The system SHALL support server environment configuration with standardized variables.

#### Scenario: Server environment setup

- **KHI** configure server với CLOUD_HOST, CLOUD_SSH_KEY, CLOUD_USERNAME, ENV_FILE
- **THÌ** server được setup thành công cho deployment
- **VÀ** SSH authentication hoạt động đúng
- **VÀ** environment variables được load securely

#### Scenario: Environment file validation

- **KHI** deploy với ENV_FILE
- **THÌ** tất cả required variables được validate
- **VÀ** missing variables được báo lỗi rõ ràng
- **VÀ** invalid values được rejected

### Requirement: Nginx Configuration File

The system SHALL provide standalone nginx.conf file for server-side reverse proxy configuration.

#### Scenario: Nginx reverse proxy setup

- **KHI** deploy nginx.conf to server
- **THÌ** nginx routes requests correctly to API (port 9000) and Web (port 3000)
- **VÀ** static files served efficiently
- **VÀ** SSL termination works properly
- **VÀ** load balancing configured for multiple instances

#### Scenario: API routing configuration

- **KHI** client requests /api/v1 endpoints
- **THÌ** nginx forwards to API container on port 9000
- **VÀ** headers preserved correctly
- **VÀ** response times optimized

#### Scenario: Web routing configuration

- **KHI** client requests non-API routes
- **THÌ** nginx forwards to Web container on port 3000
- **VÀ** Next.js routing works correctly
- **VÀ** assets served efficiently

### Requirement: Container Health Monitoring

The system SHALL provide health checks for API and Web containers.

#### Scenario: API health check

- **KHI** API container running
- **THÌ** health check endpoint /health trả về status 200
- **VÀ** database connectivity được verify
- **VÀ** critical services status được reported

#### Scenario: Web health check

- **KHI** Web container running
- **THÌ** health check endpoint trả về status 200
- **VÀ** API connectivity được verify
- **VÀ** frontend loads thành công

### Requirement: Service Discovery

The system SHALL support service discovery between API and Web containers.

#### Scenario: Internal communication

- **KHI** Web container cần gọi API
- **THÌ** API service được discover qua Docker network
- **VÀ** connection được established thành công
- **VÀ** latency được minimized

#### Scenario: External access

- **KHI** external clients cần access services
- **THÌ** API accessible qua port 9000
- **VÀ** Web accessible qua port 3000
- **VÀ** proper load balancing được configured

## MODIFIED Requirements

### Requirement: Build Process Optimization

The system SHALL optimize build process for production deployment.

#### Scenario: Multi-stage builds

- **KHI** build containers cho production
- **THÌ** sử dụng multi-stage builds để reduce image size
- **VÀ** remove development dependencies
- **VÀ** optimize layers cho caching

#### Scenario: Build caching

- **KHI** rebuild containers
- **THÌ** utilize Docker layer caching effectively
- **VÀ** chỉ rebuild changed layers
- **VÀ** build time được minimized

### Requirement: Security Configuration

The system SHALL implement security best practices for container deployment.

#### Scenario: Non-root execution

- **KHI** containers start
- **THÌ** chạy với non-root users
- **VÀ** file permissions được configured correctly
- **VÀ** security vulnerabilities được minimized

#### Scenario: Secret management

- **KHI** deploy với sensitive data
- **THÌ** secrets được injected qua environment variables
- **VÀ** không có sensitive data trong container images
- **VÀ** access được logged và monitored

## REMOVED Requirements

### Requirement: Nginx Container

**Lý do**: Server-side nginx configuration is more flexible and maintainable than containerized approach
**Chuyển đổi**: Replace nginx container with standalone nginx.conf file for server deployment

#### Scenario: Remove nginx container

- **KHI** deploy với architecture mới
- **THÌ** không còn Nginx reverse proxy container
- **VÀ** nginx.conf được deploy như file config riêng biệt
- **VÀ** reverse proxy functionality được maintain qua server-side nginx

### Requirement: PM2 Process Management

**Lý do**: Container orchestration handles process management more efficiently
**Chuyển đổi**: Use container-native process management instead of PM2

#### Scenario: Remove PM2 configuration

- **KHI** deploy với containers
- **THÌ** không còn PM2 process management
- **VÀ** container runtime handles process lifecycle
- **VÀ** application restart được handled by container orchestrator
