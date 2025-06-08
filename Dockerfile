# TradieMate Marketing Analytics - Single Build File
FROM --platform=linux/amd64 node:18-slim AS frontend

# Build frontend to static files
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build && npm run export

# Main application
FROM --platform=linux/amd64 python:3.11.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install Poetry and dependencies
RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-root

# Install uvx for MCP tools
RUN pip install --no-cache-dir uv

# Copy application code
COPY main.py cai.py logging_config.py security_config.py ./

# Copy built frontend static files
COPY --from=frontend /frontend/out ./static

# Create user and set permissions
RUN groupadd -r app && useradd -r -g app app && chown -R app:app /app
USER app

EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:10000/health || exit 1

# Run the application
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]