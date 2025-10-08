# Project Context

## Purpose

LearnHouse is an open-source learning management system (LMS) platform designed for creating and managing educational content. It provides a comprehensive solution for organizations to deliver courses, track student progress, manage assignments, and facilitate online learning experiences.

### Key Features

- Multi-tenant architecture supporting multiple organizations
- Course management with rich content editing capabilities
- AI-powered content generation and assistance
- Student progress tracking and activity management
- Payment integration for course monetization
- Role-based access control (RBAC) for security
- Assignment submission and grading system
- Content collections and organization tools

## Tech Stack

### Backend

- **Python 3.12.3+** with type hints
- **FastAPI 0.115.0** - Modern async web framework
- **SQLModel 0.0.19** - ORM combining SQLAlchemy and Pydantic
- **PostgreSQL** - Primary database with Redis for caching
- **Alembic 1.13.2** - Database migrations
- **Pytest 8.2.2** - Testing framework
- **JWT Authentication** - fastapi-jwt-auth with OAuth2 support
- **AI/ML**: OpenAI, LangChain, ChromaDB
- **Payments**: Stripe integration
- **Storage**: S3-compatible (boto3)
- **Email**: Resend service

### Frontend

- **Next.js 15.3.5** with App Router architecture
- **React 19.0.0** with TypeScript 5.4.4
- **Tailwind CSS 4.1.11** - Utility-first styling
- **shadcn/ui** with Radix UI primitives
- **TipTap 2.26.1** - Rich text editor (ProseMirror-based)
- **SWR 2.3.4** - Data fetching and caching
- **NextAuth.js 4.24.11** - Authentication
- **Formik 2.4.6** with Yup validation
- **Framer Motion 12.23.12** - Animations
- **Lucide React** - Icon library

### Infrastructure

- **Docker** - Containerization with multi-stage builds
- **Nginx** - Reverse proxy and static file serving
- **UV** - Fast Python package manager (preferred for local development)
- **pnpm** - Node.js package manager
- **Turbo** - Monorepo build system

## Project Conventions

### Code Style

#### Backend (Python)

- **Ruff** for linting with flexible line length (E501 ignored)
- **Type hints required** throughout codebase
- **Snake case** for functions, variables, files: `create_user()`, `user_object`, `user_organizations.py`
- **PascalCase** for classes and models: `UserCreate`, `OrganizationRead`
- **Descriptive suffixes** for models: `*Base`, `*Create`, `*Read`, `*Update`
- **Async/await** pattern for all I/O operations
- **Docstrings** for classes and functions

#### Frontend (TypeScript)

- **ESLint** with Next.js config and unused-imports plugin
- **Prettier** configuration:
  - Single quotes
  - No semicolons
  - Trailing commas (ES5)
- **TypeScript strict mode** enabled
- **PascalCase** for components: `CourseThumbnail`, `UserAvatar`
- **camelCase** for functions and variables
- **Path aliases** for imports:
  - `@components/*`, `@services/*`, `@/*`
- **'use client'** directive for interactive components

### Architecture Patterns

#### Backend Architecture

- **Layered Architecture**:
  - Routers Layer: API endpoints (`src/routers/`)
  - Services Layer: Business logic (`src/services/`)
  - Database Layer: Models (`src/db/`)
  - Security Layer: Auth & RBAC (`src/security/`)
- **Dependency Injection** via FastAPI
- **Repository Pattern** for database operations
- **RESTful API** with OpenAPI/Swagger documentation
- **JWT-based authentication** with refresh tokens
- **RBAC** with resource-level authorization

#### Frontend Architecture

- **Next.js App Router** with file-based routing
- **Multi-tenant routing** with organization slugs: `/orgs/[orgslug]/...`
- **Server Components** for data fetching and static content
- **Client Components** for interactivity
- **Service Layer Pattern** for API integration
- **React Context** for state management (LHSession, AIEditor)
- **SWR** for server state caching and revalidation
- **Compound Components** pattern (shadcn/ui)
- **Composition over inheritance**

### Testing Strategy

#### Backend

- **Pytest** for unit and integration tests
- **Test structure**: Class-based organization with descriptive names
- **Mock objects** for external dependencies with `pytest.fixture`
- **Async test support** with pytest-asyncio
- **Coverage reporting** with pytest-cov
- **SQLite in-memory** database for testing
- **Test organization** mirrors source structure in `src/tests/`

#### Frontend

- **Testing framework not yet implemented** - Recommended setup:
  - Jest/Vitest for unit tests
  - React Testing Library for component tests
  - Playwright/Cypress for E2E tests

### Git Workflow

- **Conventional Commits** format required
- **Focus on actual code changes** in commits
- **Pre-commit**: Run linting (Ruff for backend, ESLint for frontend)
- **Pre-push**: Run tests and ensure they pass
- **Never commit secrets**: No .env files, API keys, credentials
- **No AI attribution** in commit messages
- **English only** for commit messages, code comments, documentation
- **Local development preferred** over Docker during development

### Development Workflow

- **Prefer local virtual environment** setup instead of Docker
- **Use `repomix`** to understand codebase structure
- **Read @docs/** before implementing features
- **Verify task completion** against TODO list
- **Check for remaining TODO comments** in code
- **Try-catch error handling** required
- **Real implementation only** - no mocking or simulation

## Domain Context

### Educational Platform Concepts

- **Organizations**: Multi-tenant units with separate courses, users, and content
- **Courses**: Container for educational content with chapters and activities
- **Activities**: Learning units including videos, documents, assignments, quizzes
- **Collections**: Groupings of courses for organization
- **Assignments**: Student submissions with grading capabilities
- **User Roles**: Admin, Instructor, Contributor, Student with permission levels
- **Learning Paths**: Structured sequences of courses
- **Progress Tracking**: Student completion and performance metrics

### Content Types

- **Rich Text Documents** with TipTap editor
- **Video Content** with Plyr player
- **PDF Documents** with viewer
- **External Links** and embeds
- **Code Blocks** with syntax highlighting
- **Math Equations** with KaTeX
- **Interactive Quizzes** and assessments

### AI Features

- **Content Generation** with OpenAI integration
- **Vector Search** with ChromaDB
- **AI Editor Toolkit** for assisted content creation
- **Embeddings** for semantic search
- **Token counting** with tiktoken

## Important Constraints

### Technical Constraints

- **Python 3.12.3+ required** for backend
- **Node.js 22** for frontend production
- **PostgreSQL database** required (SQLite only for testing)
- **Redis** required for session management and caching
- **S3-compatible storage** for file uploads
- **TypeScript strict mode** must be maintained
- **Next.js App Router** architecture (no Pages Router)

### Development Constraints

- **Don't be too harsh on linting** - Prioritize functionality
- **Real implementation required** - No mocked code
- **All tests must pass** before push
- **No confidential data** in repository

### Performance Constraints

- **Database connection pooling** configured (pool_size: 20, max_overflow: 10)
- **Connection recycling** every 5 minutes
- **JWT token expiry**: 8 hours for access tokens
- **Image optimization** required with Next.js Image
- **Bundle size monitoring** recommended

### Security Constraints

- **RBAC required** for all protected resources
- **Input validation** via Pydantic (backend) and Yup (frontend)
- **Password hashing** with bcrypt
- **Secure cookies**: HttpOnly, SameSite, Secure flags
- **CORS configuration** with allowed origins
- **XSS prevention** with DOMPurify
- **SQL injection prevention** via ORM

## External Dependencies

### Required Services

- **PostgreSQL Database** - Primary data storage
- **Redis** - Session management and caching
- **S3-Compatible Storage** (AWS S3, MinIO, etc.) - File uploads
- **SMTP Server or Resend** - Email delivery
- **OpenAI API** - AI content generation features
- **Stripe** - Payment processing (optional)
- **Google OAuth** - Social authentication (optional)

### Monitoring & Logging

- **Logfire** - Application monitoring and observability
- **File-based logging** - `logs/learnhouse.log`
- **Console logging** for development

### Build & Deployment

- **Docker Registry** - Container image storage
- **Domain/Subdomain** - Multi-tenant routing support
- **SSL Certificates** - HTTPS required for production
- **CDN** - Recommended for static assets

### Development Tools

- **UV** - Python package management (preferred)
- **pnpm** - Node.js package management
- **Ruff** - Python linting
- **ESLint/Prettier** - TypeScript/JavaScript linting
- **Alembic** - Database migrations
- **Context7** - Documentation exploration
- **Repomix** - Codebase understanding
