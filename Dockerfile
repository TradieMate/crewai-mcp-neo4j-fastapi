# TradieMate Marketing Analytics - Render Optimized (Backend + Frontend)
FROM --platform=linux/amd64 node:18-slim AS frontend-builder

# Build frontend
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Backend stage
FROM --platform=linux/amd64 python:3.11.11-slim

# Set platform explicitly
ENV TARGETPLATFORM=linux/amd64
ENV BUILDPLATFORM=linux/amd64

# Set working directory
WORKDIR /app

# Install system dependencies for AMD64
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Configure poetry for production
RUN poetry config virtualenvs.create false \
    && poetry config virtualenvs.in-project false

# Install dependencies with platform-specific optimizations
RUN poetry install --no-dev --no-root --no-interaction --no-ansi

# Install uvx for MCP tools
RUN pip install --no-cache-dir uv

# Copy application code
COPY main.py cai.py logging_config.py security_config.py ./
COPY agents/ ./agents/ 2>/dev/null || true
COPY tools/ ./tools/ 2>/dev/null || true

# Copy built frontend from frontend-builder stage
COPY --from=frontend-builder /frontend/.next/standalone ./frontend/
COPY --from=frontend-builder /frontend/.next/static ./frontend/.next/static
COPY --from=frontend-builder /frontend/public ./frontend/public

# Create non-root user for security
RUN groupadd -r tradiemate && useradd -r -g tradiemate tradiemate
RUN chown -R tradiemate:tradiemate /app
USER tradiemate

# Expose port
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:10000/health || exit 1

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run the application
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000", "--workers", "1"]