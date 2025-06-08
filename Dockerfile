# Production Dockerfile for TradieMate Marketing Analytics Platform
FROM python:3.11.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Poetry
RUN pip install poetry==1.7.1

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Configure poetry
RUN poetry config virtualenvs.create false

# Install dependencies (production only)
RUN poetry install --only=main --no-dev

# Install uvx for MCP tools
RUN pip install uv==0.5.0

# Create logs directory
RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 12000

# Health check with improved reliability
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:12000/health || exit 1

# Production command with optimized settings
CMD ["uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "12000", \
     "--workers", "1", \
     "--log-level", "info", \
     "--access-log", \
     "--no-use-colors"]