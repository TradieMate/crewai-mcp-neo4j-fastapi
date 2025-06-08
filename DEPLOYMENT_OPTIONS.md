# TradieMate Deployment Options

## Available Configurations

### 1. Standard Full Stack (`docker-compose.yml`)
- **Backend Port**: 12000
- **Frontend Port**: 12001
- **Use Case**: Development and general deployment
- **Command**: `docker-compose up -d`

### 2. AMD64 Optimized (`docker-compose.amd64.yml`)
- **Backend Port**: 10000 (production optimized)
- **Frontend Port**: 12001
- **Use Case**: Production deployment on AMD64/Linux servers
- **Features**:
  - Explicit AMD64 platform targeting
  - Resource limits and reservations
  - Performance optimizations
  - Security hardening
- **Commands**:
  ```bash
  # Manual build and run
  docker-compose -f docker-compose.amd64.yml up -d
  
  # Or use automated build script
  ./build-amd64.sh
  docker-compose -f docker-compose.amd64.yml up -d
  ```

## Key Differences

| Feature | Standard | AMD64 Optimized |
|---------|----------|-----------------|
| Backend Port | 12000 | 10000 |
| Platform | Any | linux/amd64 |
| Resource Limits | None | Yes (CPU/Memory) |
| Build Optimization | Standard | AMD64-specific |
| Security | Basic | Enhanced |
| Use Case | Development | Production |

## Network Configuration

Both configurations:
- Bind backend to `0.0.0.0` for external access
- Use Docker networks for internal communication
- Expose necessary ports for external access

## Quick Start Commands

```bash
# Standard deployment
docker-compose up -d

# AMD64 optimized deployment
docker-compose -f docker-compose.amd64.yml up -d

# AMD64 with automated build
./build-amd64.sh && docker-compose -f docker-compose.amd64.yml up -d
```

## Access Points

### Standard Deployment
- Frontend: http://localhost:12001
- Backend: http://localhost:12000
- Neo4j: http://localhost:7474

### AMD64 Deployment
- Frontend: http://localhost:12001
- Backend: http://localhost:10000
- Neo4j: http://localhost:7474

Both configurations include:
- Supabase API: http://localhost:54321
- Supabase DB: localhost:54322