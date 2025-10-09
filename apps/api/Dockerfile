# Multi-stage build for Learnhouse API
FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app" \
    UV_CACHE_DIR=/tmp/uv-cache

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Development stage
FROM base AS development
RUN uv sync --frozen
ENV PATH="/app/.venv/bin:$PATH"
COPY . .
EXPOSE 9000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9000", "--reload"]

# Production stage
FROM base AS production

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Install only production dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY --chown=app:app . .

# Change to non-root user
USER app

# Expose port
EXPOSE 9000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9000/health || exit 1

# Run the application
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9000"]