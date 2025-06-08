#!/bin/bash

# TradieMate Marketing Analytics - AMD64/Linux Build Script
# This script builds Docker images specifically optimized for AMD64/Linux architecture

set -e

echo "🏗️  Building TradieMate Marketing Analytics for AMD64/Linux..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Buildx is available for multi-platform builds
if ! docker buildx version > /dev/null 2>&1; then
    print_warning "Docker Buildx not available. Installing..."
    docker buildx install
fi

# Create buildx builder for AMD64 if it doesn't exist
if ! docker buildx ls | grep -q "tradiemate-builder"; then
    print_status "Creating AMD64 builder..."
    docker buildx create --name tradiemate-builder --platform linux/amd64
fi

# Use the builder
docker buildx use tradiemate-builder

print_status "Building AMD64-optimized images..."

# Build backend image for AMD64
print_status "Building backend image (AMD64)..."
docker buildx build \
    --platform linux/amd64 \
    --file Dockerfile.amd64 \
    --tag tradiemate-backend:amd64 \
    --tag tradiemate-backend:latest-amd64 \
    --load \
    .

if [ $? -eq 0 ]; then
    print_success "Backend image built successfully!"
else
    print_error "Failed to build backend image"
    exit 1
fi

# Build frontend image for AMD64
print_status "Building frontend image (AMD64)..."
docker buildx build \
    --platform linux/amd64 \
    --file frontend/Dockerfile.amd64 \
    --tag tradiemate-frontend:amd64 \
    --tag tradiemate-frontend:latest-amd64 \
    --load \
    frontend/

if [ $? -eq 0 ]; then
    print_success "Frontend image built successfully!"
else
    print_error "Failed to build frontend image"
    exit 1
fi

# Verify images
print_status "Verifying built images..."
echo ""
echo "📦 Built Images:"
docker images | grep tradiemate | grep amd64

# Check image architecture
print_status "Checking image architectures..."
echo ""
echo "🏗️  Backend Architecture:"
docker inspect tradiemate-backend:amd64 | grep -A 5 "Architecture"

echo ""
echo "🎨 Frontend Architecture:"
docker inspect tradiemate-frontend:amd64 | grep -A 5 "Architecture"

print_success "All AMD64 images built successfully!"

echo ""
echo "🚀 To run the complete platform:"
echo "   docker-compose -f docker-compose.amd64.yml up -d"
echo ""
echo "🌐 Access points:"
echo "   Frontend: http://localhost:12001"
echo "   Backend:  http://localhost:10000"
echo "   Neo4j:    http://localhost:7474"
echo ""
echo "📋 To push to registry:"
echo "   docker tag tradiemate-backend:amd64 your-registry/tradiemate-backend:amd64"
echo "   docker tag tradiemate-frontend:amd64 your-registry/tradiemate-frontend:amd64"
echo "   docker push your-registry/tradiemate-backend:amd64"
echo "   docker push your-registry/tradiemate-frontend:amd64"

print_success "Build complete! 🎉"