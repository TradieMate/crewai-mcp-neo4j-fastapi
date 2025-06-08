# 🐳 TradieMate Marketing Analytics - AMD64/Linux Deployment Guide

## 🎯 AMD64/Linux Compatible Docker Images

The TradieMate Marketing Analytics platform includes **optimized Docker configurations specifically for AMD64/Linux architecture**, ensuring maximum compatibility across cloud providers and Linux servers.

## 🏗️ Available AMD64 Configurations

### 1. **AMD64-Optimized Dockerfiles**
- `Dockerfile.amd64` - Backend (CrewAI + FastAPI)
- `frontend/Dockerfile.amd64` - Frontend (Next.js)
- `docker-compose.amd64.yml` - Complete platform
- `build-amd64.sh` - Automated build script

### 2. **Platform Specifications**
```dockerfile
FROM --platform=linux/amd64 python:3.11.11-slim
ENV TARGETPLATFORM=linux/amd64
ENV BUILDPLATFORM=linux/amd64
```

## 🚀 Quick Start - AMD64/Linux Build

### Option 1: Automated Build Script
```bash
# Make script executable
chmod +x build-amd64.sh

# Build all AMD64 images
./build-amd64.sh

# Build with all-in-one container
./build-amd64.sh --all-in-one
```

### Option 2: Manual Docker Build
```bash
# Build backend for AMD64
docker buildx build \
  --platform linux/amd64 \
  --file Dockerfile.amd64 \
  --tag tradiemate-backend:amd64 \
  --load .

# Build frontend for AMD64
docker buildx build \
  --platform linux/amd64 \
  --file frontend/Dockerfile.amd64 \
  --tag tradiemate-frontend:amd64 \
  --load frontend/
```

### Option 3: Docker Compose (Recommended)
```bash
# Start complete AMD64 platform
docker-compose -f docker-compose.amd64.yml up --build -d

# Access services:
# Frontend: http://localhost:12001
# Backend: http://localhost:12000
# Neo4j: http://localhost:7474
```

## 🔧 AMD64 Optimizations

### Backend Optimizations (`Dockerfile.amd64`)
```dockerfile
# Platform-specific base image
FROM --platform=linux/amd64 python:3.11.11-slim

# AMD64-optimized system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Poetry configuration for production
RUN poetry config virtualenvs.create false \
    && poetry config virtualenvs.in-project false

# Install dependencies with platform optimizations
RUN poetry install --no-dev --no-interaction --no-ansi

# Security: Non-root user
RUN groupadd -r tradiemate && useradd -r -g tradiemate tradiemate
USER tradiemate

# Performance environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
```

### Frontend Optimizations (`frontend/Dockerfile.amd64`)
```dockerfile
# Multi-stage build for AMD64
FROM --platform=linux/amd64 node:18-alpine AS base

# Dependencies stage with platform-specific installs
FROM base AS deps
RUN npm ci --only=production --platform=linux --arch=x64

# Builder stage with production optimizations
FROM base AS builder
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
RUN npm run build

# Production runner with minimal footprint
FROM base AS runner
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
USER nextjs
```

## 🌐 Cloud Provider Deployment

### AWS ECS (AMD64)
```bash
# Create ECR repository
aws ecr create-repository --repository-name tradiemate-backend
aws ecr create-repository --repository-name tradiemate-frontend

# Build and push AMD64 images
docker buildx build --platform linux/amd64 \
  --file Dockerfile.amd64 \
  --tag your-account.dkr.ecr.region.amazonaws.com/tradiemate-backend:amd64 \
  --push .

docker buildx build --platform linux/amd64 \
  --file frontend/Dockerfile.amd64 \
  --tag your-account.dkr.ecr.region.amazonaws.com/tradiemate-frontend:amd64 \
  --push frontend/
```

### Google Cloud Run (AMD64)
```bash
# Build for AMD64 and deploy
gcloud builds submit --config cloudbuild.yaml \
  --substitutions=_PLATFORM=linux/amd64

# Deploy with platform specification
gcloud run deploy tradiemate-backend \
  --image gcr.io/your-project/tradiemate-backend:amd64 \
  --platform managed \
  --region us-central1 \
  --cpu 2 \
  --memory 4Gi
```

### Azure Container Instances (AMD64)
```bash
# Build and push to Azure Container Registry
az acr build --registry your-registry \
  --image tradiemate-backend:amd64 \
  --file Dockerfile.amd64 \
  --platform linux/amd64 .

# Deploy with AMD64 specification
az container create \
  --resource-group tradiemate-rg \
  --name tradiemate-backend \
  --image your-registry.azurecr.io/tradiemate-backend:amd64 \
  --os-type Linux \
  --cpu 2 \
  --memory 4
```

### DigitalOcean App Platform (AMD64)
```yaml
# app.yaml
name: tradiemate-platform
services:
- name: backend
  source_dir: /
  dockerfile_path: Dockerfile.amd64
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 12000
  
- name: frontend
  source_dir: /frontend
  dockerfile_path: Dockerfile.amd64
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 3000
```

## 🐧 Linux Server Deployment

### Ubuntu/Debian Server
```bash
# Install Docker with AMD64 support
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Buildx
sudo apt-get update
sudo apt-get install docker-buildx-plugin

# Clone and deploy
git clone https://github.com/TradieMate/crewai-mcp-neo4j-fastapi.git
cd crewai-mcp-neo4j-fastapi

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Build and deploy for AMD64
./build-amd64.sh
docker-compose -f docker-compose.amd64.yml up -d
```

### CentOS/RHEL Server
```bash
# Install Docker
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Deploy platform
git clone https://github.com/TradieMate/crewai-mcp-neo4j-fastapi.git
cd crewai-mcp-neo4j-fastapi
chmod +x build-amd64.sh
./build-amd64.sh
docker-compose -f docker-compose.amd64.yml up -d
```

## 🔍 Verification Commands

### Check Image Architecture
```bash
# Verify AMD64 architecture
docker inspect tradiemate-backend:amd64 | grep -A 5 "Architecture"
docker inspect tradiemate-frontend:amd64 | grep -A 5 "Architecture"

# Expected output: "Architecture": "amd64"
```

### Performance Testing
```bash
# Test backend performance
curl -X POST http://localhost:12000/crewai \
  -H "Content-Type: application/json" \
  -d '{"query": "What are my top performing Google Ads campaigns?"}'

# Test frontend
curl -f http://localhost:12001/api/health

# Monitor resource usage
docker stats tradiemate-backend-amd64 tradiemate-frontend-amd64
```

## 📊 Resource Requirements (AMD64)

### Minimum Requirements
- **CPU**: 2 cores (AMD64)
- **RAM**: 4GB
- **Storage**: 20GB
- **Network**: 1Gbps

### Recommended Production
- **CPU**: 4 cores (AMD64)
- **RAM**: 8GB
- **Storage**: 50GB SSD
- **Network**: 10Gbps

### Resource Allocation
```yaml
# docker-compose.amd64.yml includes:
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '2.0'
    reservations:
      memory: 2G
      cpus: '1.0'
```

## 🔒 Security Features (AMD64)

### Container Security
```dockerfile
# Non-root user execution
RUN groupadd -r tradiemate && useradd -r -g tradiemate tradiemate
USER tradiemate

# Read-only filesystem
--read-only --tmpfs /tmp

# Security scanning
docker scout cves tradiemate-backend:amd64
```

### Network Security
```yaml
# Isolated network
networks:
  tradie-network-amd64:
    driver: bridge
    internal: true  # No external access
```

## 🚀 Production Deployment Checklist

### Pre-Deployment
- [ ] Set `OPENAI_API_KEY` environment variable
- [ ] Configure Neo4j credentials
- [ ] Set up Supabase project
- [ ] Configure domain and SSL certificates
- [ ] Set up monitoring and logging

### Build Process
- [ ] Run `./build-amd64.sh` successfully
- [ ] Verify AMD64 architecture with `docker inspect`
- [ ] Test images locally before deployment
- [ ] Push images to container registry

### Deployment
- [ ] Deploy with `docker-compose -f docker-compose.amd64.yml up -d`
- [ ] Verify all services are healthy
- [ ] Test frontend at http://localhost:12001
- [ ] Test backend API at http://localhost:12000/health
- [ ] Verify Neo4j connection at http://localhost:7474

### Post-Deployment
- [ ] Set up SSL/TLS certificates
- [ ] Configure reverse proxy (Nginx/Traefik)
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure log aggregation
- [ ] Set up automated backups

## 🎯 Quick Commands Reference

```bash
# Build AMD64 images
./build-amd64.sh

# Start platform
docker-compose -f docker-compose.amd64.yml up -d

# View logs
docker-compose -f docker-compose.amd64.yml logs -f

# Stop platform
docker-compose -f docker-compose.amd64.yml down

# Update images
docker-compose -f docker-compose.amd64.yml pull
docker-compose -f docker-compose.amd64.yml up -d

# Backup data
docker run --rm -v neo4j_data_amd64:/data -v $(pwd):/backup ubuntu tar czf /backup/neo4j-backup.tar.gz /data
```

## 🎉 Success!

Your TradieMate Marketing Analytics platform is now optimized and ready for AMD64/Linux deployment across any cloud provider or Linux server!

**Access your platform:**
- **Frontend**: http://localhost:12001
- **Backend API**: http://localhost:12000
- **Neo4j Database**: http://localhost:7474

The platform includes:
✅ **Modern Chat UI** with TradieMate branding  
✅ **CrewAI Marketing Agents** for Google Ads & website optimization  
✅ **Neo4j Database** with automatic Google Analytics/Ads data ingestion  
✅ **AMD64/Linux Optimization** for maximum compatibility  
✅ **Production-Ready** with comprehensive monitoring and security  

**Ready for enterprise deployment! 🚀**