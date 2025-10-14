# Multi-stage build for FastAPI application
# Stage 1: Builder - Install dependencies
FROM python:3.12-slim-bookworm AS builder

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    pkg-config \
    libmagic-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency management
RUN pip install --no-cache-dir uv==0.5.1

# Set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv with frozen lockfile
RUN uv pip install --system --no-cache -r pyproject.toml

# Stage 2: Runtime - Production image
FROM python:3.12-slim-bookworm AS runtime

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/appuser/.local/bin:$PATH"

# Install runtime system dependencies only
RUN apt-get update && apt-get install -y \
    libpq5 \
    libgomp1 \
    libmagic1 \
    libssl3 \
    libffi8 \
    libstdc++6 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create logs directory and set permissions
RUN mkdir -p logs && \
    touch logs/logs.txt && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 1338

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:1338/api/v1/health || exit 1

# Default command - can be overridden for development
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "1338", "--workers", "1"]