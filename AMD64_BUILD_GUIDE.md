# 🏗️ TradieMate Marketing Analytics - AMD64/Linux Build Guide

## 🎯 AMD64/Linux Optimized Docker Images

This guide provides instructions for building Docker images specifically optimized for **AMD64/Linux** architecture, ensuring maximum compatibility with Linux servers, cloud platforms, and CI/CD pipelines.

## 📋 AMD64-Specific Files

### 🐳 Docker Files
- `Dockerfile.amd64` - Backend optimized for AMD64
- `frontend/Dockerfile.amd64` - Frontend optimized for AMD64  
- `docker-compose.amd64.yml` - Complete stack for AMD64
- `build-amd64.sh` - Automated build script

### 🔧 Key Optimizations

#### Platform Specification
```dockerfile
FROM --platform=linux/amd64 python:3.11.11-slim
ENV TARGETPLATFORM=linux/amd64
ENV BUILDPLATFORM=linux/amd64
```

#### Resource Limits
```yaml
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '2.0'
    reservations:
      memory: 2G
      cpus: '1.0'
```

#### Security Enhancements
```dockerfile
# Non-root user
RUN groupadd -r tradiemate && useradd -r -g tradiemate tradiemate
USER tradiemate
```

## 🚀 Quick Start - AMD64 Build

### Option 1: Automated Build Script
```bash
# Clone repository
git clone https://github.com/TradieMate/crewai-mcp-neo4j-fastapi.git
cd crewai-mcp-neo4j-fastapi

# Run automated AMD64 build
./build-amd64.sh
```

### Option 2: Manual Build Commands
```bash
# Build backend for AMD64
docker buildx build \
  --platform linux/amd64 \
  --file Dockerfile.amd64 \
  --tag tradiemate-backend:amd64 \
  --load \
  .

# Build frontend for AMD64
docker buildx build \
  --platform linux/amd64 \
  --file frontend/Dockerfile.amd64 \
  --tag tradiemate-frontend:amd64 \
  --load \
  frontend/
```

### Option 3: Docker Compose AMD64
```bash
# Set up environment
cp .env.example .env
cp frontend/.env.local.example frontend/.env.local
# Edit .env files with your API keys

# Build and run complete AMD64 stack
docker-compose -f docker-compose.amd64.yml up --build -d
```

## 🔍 Architecture Verification

### Check Built Images
```bash
# List AMD64 images
docker images | grep tradiemate | grep amd64

# Verify architecture
docker inspect tradiemate-backend:amd64 | grep -A 5 "Architecture"
docker inspect tradiemate-frontend:amd64 | grep -A 5 "Architecture"
```

### Expected Output
```json
"Architecture": "amd64",
"Os": "linux",
"Platform": {
    "architecture": "amd64",
    "os": "linux"
}
```

## 🌐 Deployment Options

### 1. Local Development
```bash
# Start AMD64 stack
docker-compose -f docker-compose.amd64.yml up -d

# Access services
# Frontend: http://localhost:12001
# Backend:  http://localhost:12000
# Neo4j:    http://localhost:7474
```

### 2. Cloud Deployment

#### AWS ECS (AMD64)
```bash
# Tag for ECR
docker tag tradiemate-backend:amd64 your-account.dkr.ecr.us-east-1.amazonaws.com/tradiemate-backend:amd64
docker tag tradiemate-frontend:amd64 your-account.dkr.ecr.us-east-1.amazonaws.com/tradiemate-frontend:amd64

# Push to ECR
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/tradiemate-backend:amd64
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/tradiemate-frontend:amd64
```

#### Google Cloud Run (AMD64)
```bash
# Tag for GCR
docker tag tradiemate-backend:amd64 gcr.io/your-project/tradiemate-backend:amd64
docker tag tradiemate-frontend:amd64 gcr.io/your-project/tradiemate-frontend:amd64

# Push to GCR
docker push gcr.io/your-project/tradiemate-backend:amd64
docker push gcr.io/your-project/tradiemate-frontend:amd64

# Deploy to Cloud Run
gcloud run deploy tradiemate-backend \
  --image gcr.io/your-project/tradiemate-backend:amd64 \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure Container Instances (AMD64)
```bash
# Tag for ACR
docker tag tradiemate-backend:amd64 your-registry.azurecr.io/tradiemate-backend:amd64
docker tag tradiemate-frontend:amd64 your-registry.azurecr.io/tradiemate-frontend:amd64

# Push to ACR
docker push your-registry.azurecr.io/tradiemate-backend:amd64
docker push your-registry.azurecr.io/tradiemate-frontend:amd64
```

### 3. Kubernetes Deployment

#### Create Kubernetes Manifests
```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tradiemate-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tradiemate-backend
  template:
    metadata:
      labels:
        app: tradiemate-backend
    spec:
      nodeSelector:
        kubernetes.io/arch: amd64
      containers:
      - name: backend
        image: tradiemate-backend:amd64
        ports:
        - containerPort: 12000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: tradiemate-secrets
              key: openai-api-key
        resources:
          limits:
            memory: "2Gi"
            cpu: "1000m"
          requests:
            memory: "1Gi"
            cpu: "500m"
```

## 🔧 Build Customization

### Custom Build Arguments
```bash
# Build with custom Python version
docker buildx build \
  --platform linux/amd64 \
  --build-arg PYTHON_VERSION=3.11.11 \
  --file Dockerfile.amd64 \
  --tag tradiemate-backend:custom-amd64 \
  .

# Build with custom Node version
docker buildx build \
  --platform linux/amd64 \
  --build-arg NODE_VERSION=18 \
  --file frontend/Dockerfile.amd64 \
  --tag tradiemate-frontend:custom-amd64 \
  frontend/
```

### Multi-Stage Build Optimization
```dockerfile
# Example: Custom backend with additional tools
FROM --platform=linux/amd64 python:3.11.11-slim AS base
# ... base setup

FROM base AS development
RUN pip install pytest black flake8
# ... development tools

FROM base AS production
# ... production-only setup
```

## 📊 Performance Optimization

### Memory and CPU Tuning
```yaml
# docker-compose.amd64.yml optimizations
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G      # Adjust based on your needs
          cpus: '1.0'     # Adjust based on your server
        reservations:
          memory: 1G
          cpus: '0.5'
    environment:
      - WORKERS=4       # Adjust based on CPU cores
```

### Neo4j Memory Configuration
```yaml
neo4j:
  environment:
    - NEO4J_dbms_memory_heap_initial_size=1G
    - NEO4J_dbms_memory_heap_max_size=2G
    - NEO4J_dbms_memory_pagecache_size=1G
```

## 🔍 Troubleshooting

### Common AMD64 Build Issues

#### 1. Platform Mismatch
```bash
# Error: exec format error
# Solution: Ensure platform is specified
docker buildx build --platform linux/amd64 ...
```

#### 2. Buildx Not Available
```bash
# Install Docker Buildx
docker buildx install

# Create builder
docker buildx create --name tradiemate-builder --platform linux/amd64
docker buildx use tradiemate-builder
```

#### 3. Memory Issues During Build
```bash
# Increase Docker memory limit
# Docker Desktop: Settings > Resources > Memory > 8GB+

# Or build with limited parallelism
docker buildx build --platform linux/amd64 --build-arg MAKEFLAGS="-j2" ...
```

### Verification Commands
```bash
# Check Docker Buildx
docker buildx ls

# Check available platforms
docker buildx inspect --bootstrap

# Test image architecture
docker run --rm tradiemate-backend:amd64 uname -m
# Expected output: x86_64
```

## 📋 Environment Variables

### Required for AMD64 Build
```bash
# .env
OPENAI_API_KEY=your_openai_api_key_here
NEO4J_URI=neo4j://neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=tradiemate123

# Build-specific
DOCKER_BUILDKIT=1
BUILDX_EXPERIMENTAL=1
```

### Frontend Environment
```bash
# frontend/.env.local
CREWAI_BACKEND_URL=http://backend:12000
NEXT_PUBLIC_SUPABASE_URL=http://localhost:54321
NEXT_PUBLIC_APP_NAME=TradieMate Marketing Analytics
```

## 🚀 CI/CD Integration

### GitHub Actions Example
```yaml
name: Build AMD64 Images
on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
      with:
        platforms: linux/amd64
    
    - name: Build Backend
      run: |
        docker buildx build \
          --platform linux/amd64 \
          --file Dockerfile.amd64 \
          --tag tradiemate-backend:amd64 \
          --load \
          .
    
    - name: Build Frontend
      run: |
        docker buildx build \
          --platform linux/amd64 \
          --file frontend/Dockerfile.amd64 \
          --tag tradiemate-frontend:amd64 \
          --load \
          frontend/
```

## ✅ Production Checklist

- [ ] Images built with `--platform linux/amd64`
- [ ] Architecture verified as `amd64`
- [ ] Resource limits configured
- [ ] Health checks implemented
- [ ] Non-root users configured
- [ ] Environment variables set
- [ ] Secrets properly managed
- [ ] Monitoring endpoints available
- [ ] Backup strategy in place
- [ ] SSL/TLS configured for production

## 🎉 Summary

The AMD64/Linux optimized build provides:

- ✅ **Maximum Compatibility**: Works on all Linux servers and cloud platforms
- ✅ **Performance Optimized**: Tuned for AMD64 architecture
- ✅ **Production Ready**: Security hardened with resource limits
- ✅ **Easy Deployment**: Single command deployment options
- ✅ **Scalable**: Kubernetes and cloud-native ready

**Quick Start Command:**
```bash
./build-amd64.sh && docker-compose -f docker-compose.amd64.yml up -d
```

Your TradieMate Marketing Analytics platform will be running on AMD64/Linux architecture at:
- **Frontend**: http://localhost:12001
- **Backend**: http://localhost:12000
- **Neo4j**: http://localhost:7474

🚀 **Ready for production deployment on any AMD64/Linux environment!**