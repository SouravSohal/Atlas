# ==============================================================================
# Stage 1: Build stage
# ==============================================================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy packages and service definition
COPY packages/atlas-core /build/packages/atlas-core
COPY services/api /build/services/api

# Build wheels for the core library and API service
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir build && \
    python -m build --wheel --outdir /build/wheels /build/packages/atlas-core && \
    python -m build --wheel --outdir /build/wheels /build/services/api

# Install wheels locally using --find-links to resolve local dependencies from /build/wheels
RUN python -m pip install --no-cache-dir --prefix=/install --find-links=/build/wheels /build/wheels/atlas_api-0.1.0-py3-none-any.whl

# ==============================================================================
# Stage 2: Final runtime stage
# ==============================================================================
FROM python:3.12-slim AS runner

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    ENVIRONMENT=production

WORKDIR /app

# Create non-root system user and group
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -m -s /bin/bash appuser

# Copy installed dependencies and packages from builder stage
COPY --from=builder /install /usr/local

# Expose server port
EXPOSE 8000

# Switch to non-root user
USER appuser

# Start the uvicorn API gateway, respecting the PORT environment variable
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
