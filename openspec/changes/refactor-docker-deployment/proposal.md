## Why

Current Docker architecture combines both API and Web in a single container, making scaling, deployment, and maintenance difficult. Need to separate into individual containers to optimize deployment workflow and support external database services.

## What Changes

- **Remove all current Docker configurations** (Dockerfile, docker-compose.yml, .dockerignore)
- **Create separate Dockerfile for API service** (apps/api/)
- **Create separate Dockerfile for Web service** (apps/web/)
- **Create new docker-compose.production.yml** with only API and Web services
- **Create standalone nginx.conf file** for server-side reverse proxy configuration
- **Setup GitHub Actions workflow** for auto deployment
- **Configure SSH-based deployment** with server environment variables
- **Remove PostgreSQL and Redis containers** (use external services)
- **Create production-ready deployment scripts**

## Impact

- Affected specs: deployment, infrastructure
- Affected code: Dockerfile, docker-compose.yml, .github/workflows/
- **BREAKING**: Complete deployment architecture change
- Optimize resource usage and scaling capabilities
- Simplify deployment process with automated CI/CD
