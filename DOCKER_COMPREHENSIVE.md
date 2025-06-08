# 🐳 TradieMate Marketing Analytics - Comprehensive Docker Guide

## Overview

The TradieMate Marketing Analytics platform provides multiple Docker deployment options to suit different needs and environments.

## 🏗️ Available Docker Configurations

### 1. **Full-Stack Docker Compose** (Recommended for Production)
**File**: `docker-compose.full-stack.yml`
**Purpose**: Complete platform with all services
**Services**:
- Neo4j Database with Graph Data Science
- CrewAI FastAPI Backend
- Next.js Frontend
- Supabase (PostgreSQL + API)

### 2. **Individual Service Dockerfiles**
**Backend**: `Dockerfile` (FastAPI + CrewAI)
**Frontend**: `frontend/Dockerfile` (Next.js)
**Purpose**: Separate containers for microservices architecture

### 3. **All-in-One Dockerfile** (New)
**File**: `Dockerfile.all-in-one`
**Purpose**: Single container with frontend + backend + Nginx
**Use Case**: Simple deployments, development, or resource-constrained environments

### 4. **Unified Docker Setup**
**File**: `docker-compose.unified.yml`
**Purpose**: Backend + Neo4j only (without frontend)

## 🚀 Quick Start Options

### Option 1: Full-Stack Platform (Recommended)

```bash
# Clone repository
git clone https://github.com/TradieMate/crewai-mcp-neo4j-fastapi.git
cd crewai-mcp-neo4j-fastapi

# Set up environment
cp .env.example .env
cp frontend/.env.local.example frontend/.env.local
# Edit .env files with your API keys

# Start complete platform
docker-compose -f docker-compose.full-stack.yml up --build -d

# Access services
# Frontend: http://localhost:12001
# Backend: http://localhost:12000
# Neo4j: http://localhost:7474
```

### Option 2: All-in-One Container

```bash
# Build all-in-one image
docker build -f Dockerfile.all-in-one -t tradiemate-platform .

# Run with external Neo4j and Supabase
docker run -d \
  --name tradiemate-platform \
  -p 80:80 \
  -p 3000:3000 \
  -p 12000:12000 \
  -e OPENAI_API_KEY=your_key \
  -e NEO4J_URI=neo4j://your-neo4j:7687 \
  -e NEO4J_USERNAME=neo4j \
  -e NEO4J_PASSWORD=your_password \
  -e NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co \
  -e NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key \
  tradiemate-platform

# Access via http://localhost
```

### Option 3: Individual Services

```bash
# Build backend
docker build -t tradiemate-backend .

# Build frontend
docker build -t tradiemate-frontend ./frontend

# Run backend
docker run -d \
  --name tradiemate-backend \
  -p 12000:12000 \
  -e OPENAI_API_KEY=your_key \
  -e NEO4J_URI=neo4j://neo4j:7687 \
  tradiemate-backend

# Run frontend
docker run -d \
  --name tradiemate-frontend \
  -p 3000:3000 \
  -e CREWAI_BACKEND_URL=http://backend:12000 \
  tradiemate-frontend
```

## 📋 Docker Compose Services Breakdown

### Full-Stack Configuration (`docker-compose.full-stack.yml`)

#### 🗄️ Neo4j Database
```yaml
neo4j:
  image: neo4j:5.15-enterprise
  ports: ["7474:7474", "7687:7687"]
  environment:
    - NEO4J_PLUGINS=["graph-data-science"]
    - NEO4J_AUTH=neo4j/tradiemate123
  volumes:
    - neo4j_data:/data
    - neo4j_logs:/logs
  healthcheck: cypher-shell connectivity test
```

#### 🤖 CrewAI Backend
```yaml
backend:
  build: .
  ports: ["12000:12000"]
  environment:
    - OPENAI_API_KEY=${OPENAI_API_KEY}
    - NEO4J_URI=neo4j://neo4j:7687
  depends_on: [neo4j]
  healthcheck: curl http://localhost:12000/health
```

#### 🎨 Next.js Frontend
```yaml
frontend:
  build: ./frontend
  ports: ["12001:3000"]
  environment:
    - CREWAI_BACKEND_URL=http://backend:12000
    - NEXT_PUBLIC_SUPABASE_URL=http://localhost:54321
  depends_on: [backend, supabase-api]
  healthcheck: curl http://localhost:3000
```

#### 📊 Supabase Services
```yaml
supabase-db:
  image: supabase/postgres:15.1.0.147
  ports: ["54322:5432"]
  
supabase-api:
  image: supabase/gotrue:v2.132.3
  ports: ["54321:8000"]
  depends_on: [supabase-db]
```

## 🔧 Environment Configuration

### Required Environment Variables

#### Backend (.env)
```bash
# Core
OPENAI_API_KEY=your_openai_api_key_here
NEO4J_URI=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=tradiemate123

# Application
ENVIRONMENT=production
PORT=12000
HOST=0.0.0.0
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:12001
```

#### Frontend (frontend/.env.local)
```bash
# Backend Connection
CREWAI_BACKEND_URL=http://localhost:12000

# Supabase
NEXT_PUBLIC_SUPABASE_URL=http://localhost:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Branding
NEXT_PUBLIC_APP_NAME=TradieMate Marketing Analytics
NEXT_PUBLIC_APP_DESCRIPTION=AI-powered Google Ads and website optimization for trade businesses
```

## 🚀 Production Deployment

### Cloud Deployment with Docker

#### AWS ECS
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com

# Build images
docker build -t tradiemate-backend .
docker build -t tradiemate-frontend ./frontend

# Tag and push
docker tag tradiemate-backend:latest your-account.dkr.ecr.us-east-1.amazonaws.com/tradiemate-backend:latest
docker tag tradiemate-frontend:latest your-account.dkr.ecr.us-east-1.amazonaws.com/tradiemate-frontend:latest

docker push your-account.dkr.ecr.us-east-1.amazonaws.com/tradiemate-backend:latest
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/tradiemate-frontend:latest
```

#### Google Cloud Run
```bash
# Build and deploy backend
gcloud builds submit --tag gcr.io/your-project/tradiemate-backend
gcloud run deploy tradiemate-backend \
  --image gcr.io/your-project/tradiemate-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Build and deploy frontend
cd frontend
gcloud builds submit --tag gcr.io/your-project/tradiemate-frontend
gcloud run deploy tradiemate-frontend \
  --image gcr.io/your-project/tradiemate-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure Container Instances
```bash
# Create resource group
az group create --name tradiemate-rg --location eastus

# Deploy backend
az container create \
  --resource-group tradiemate-rg \
  --name tradiemate-backend \
  --image tradiemate-backend:latest \
  --ports 12000 \
  --environment-variables OPENAI_API_KEY=your_key

# Deploy frontend
az container create \
  --resource-group tradiemate-rg \
  --name tradiemate-frontend \
  --image tradiemate-frontend:latest \
  --ports 3000 \
  --environment-variables CREWAI_BACKEND_URL=http://backend:12000
```

### Self-Hosted Production

#### With SSL and Domain
```bash
# Create production docker-compose override
cat > docker-compose.prod.yml << EOF
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    networks:
      - tradie-network

  frontend:
    environment:
      - CREWAI_BACKEND_URL=https://api.yourdomain.com
      - NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co

  backend:
    environment:
      - ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
EOF

# Deploy with production overrides
docker-compose -f docker-compose.full-stack.yml -f docker-compose.prod.yml up -d
```

## 🔍 Docker Image Optimization

### Multi-Stage Build Benefits

#### Backend Dockerfile Optimization
```dockerfile
# Development stage
FROM python:3.11.11-slim AS development
WORKDIR /app
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install

# Production stage
FROM python:3.11.11-slim AS production
WORKDIR /app
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi
COPY . .
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "12000"]
```

#### Frontend Dockerfile Optimization
```dockerfile
# Dependencies stage
FROM node:18-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Builder stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
CMD ["node", "server.js"]
```

## 📊 Monitoring and Logging

### Docker Health Checks

#### Backend Health Check
```dockerfile
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:12000/health || exit 1
```

#### Frontend Health Check
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1
```

### Logging Configuration

#### Centralized Logging
```yaml
# Add to docker-compose.full-stack.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        
  frontend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

#### Log Aggregation with ELK Stack
```yaml
# Add ELK services
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

## 🔧 Troubleshooting

### Common Docker Issues

#### 1. Container Won't Start
```bash
# Check logs
docker-compose -f docker-compose.full-stack.yml logs -f backend
docker-compose -f docker-compose.full-stack.yml logs -f frontend

# Check container status
docker ps -a

# Restart specific service
docker-compose -f docker-compose.full-stack.yml restart backend
```

#### 2. Network Connectivity Issues
```bash
# Check network
docker network ls
docker network inspect crewai-mcp-neo4j-fastapi_tradie-network

# Test connectivity between containers
docker exec -it tradie-backend curl http://neo4j:7474
docker exec -it tradie-frontend curl http://backend:12000/health
```

#### 3. Volume Permission Issues
```bash
# Fix Neo4j volume permissions
sudo chown -R 7474:7474 ./neo4j_data
sudo chmod -R 755 ./neo4j_data

# Fix Supabase volume permissions
sudo chown -R 999:999 ./supabase_db_data
```

#### 4. Memory Issues
```bash
# Check resource usage
docker stats

# Increase memory limits
# Add to docker-compose.yml:
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

### Performance Optimization

#### 1. Image Size Reduction
```bash
# Use alpine images where possible
FROM node:18-alpine
FROM python:3.11-alpine

# Multi-stage builds to reduce final image size
# Remove unnecessary packages after installation
RUN apt-get update && apt-get install -y package \
    && rm -rf /var/lib/apt/lists/*
```

#### 2. Build Cache Optimization
```bash
# Use .dockerignore to exclude unnecessary files
echo "node_modules" >> .dockerignore
echo ".git" >> .dockerignore
echo "*.md" >> .dockerignore

# Layer caching - copy package files first
COPY package*.json ./
RUN npm install
COPY . .
```

#### 3. Resource Limits
```yaml
# Add resource limits to docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
```

## 🚀 Scaling and Load Balancing

### Horizontal Scaling
```yaml
# Scale services
services:
  backend:
    deploy:
      replicas: 3
      
  frontend:
    deploy:
      replicas: 2
```

### Load Balancer Configuration
```nginx
# nginx.conf for load balancing
upstream backend {
    server backend_1:12000;
    server backend_2:12000;
    server backend_3:12000;
}

upstream frontend {
    server frontend_1:3000;
    server frontend_2:3000;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://frontend;
    }
    
    location /api/ {
        proxy_pass http://backend/;
    }
}
```

## 📚 Additional Resources

### Docker Commands Reference
```bash
# Build and run
docker-compose -f docker-compose.full-stack.yml up --build -d

# View logs
docker-compose -f docker-compose.full-stack.yml logs -f

# Stop services
docker-compose -f docker-compose.full-stack.yml down

# Remove volumes (careful!)
docker-compose -f docker-compose.full-stack.yml down -v

# Update images
docker-compose -f docker-compose.full-stack.yml pull
docker-compose -f docker-compose.full-stack.yml up -d

# Scale services
docker-compose -f docker-compose.full-stack.yml up -d --scale backend=3

# Execute commands in containers
docker exec -it tradie-backend bash
docker exec -it tradie-frontend sh
```

### Security Best Practices
```dockerfile
# Use non-root users
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
USER nextjs

# Scan images for vulnerabilities
docker scan tradiemate-backend:latest

# Use specific image tags, not 'latest'
FROM node:18.17.0-alpine
FROM python:3.11.11-slim
```

---

## 🎉 Summary

The TradieMate Marketing Analytics platform provides comprehensive Docker support with multiple deployment options:

1. **Full-Stack**: Complete platform with all services
2. **All-in-One**: Single container for simple deployments
3. **Microservices**: Individual containers for scalability
4. **Production**: Optimized configurations with monitoring

Choose the option that best fits your deployment needs and infrastructure requirements.

**Ready to deploy? Start with the Full-Stack option for the complete experience!**