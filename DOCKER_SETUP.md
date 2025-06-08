# Docker Setup Guide

## Quick Start

This project provides two Docker Compose configurations:
- **Standard**: `docker-compose.yml` - General full stack deployment
- **AMD64 Optimized**: `docker-compose.amd64.yml` - Optimized for AMD64/Linux platforms with resource limits and performance tuning

### Prerequisites

- Docker and Docker Compose installed
- OpenAI API key

### Setup

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the .env file and add your OpenAI API key:**
   ```bash
   OPENAI_API_KEY=your-actual-openai-api-key-here
   ```

3. **Start the full stack:**
   
   **Standard deployment:**
   ```bash
   docker-compose up -d
   ```
   
   **AMD64 optimized deployment:**
   ```bash
   docker-compose -f docker-compose.amd64.yml up -d
   ```
   
   **Or use the automated AMD64 build script:**
   ```bash
   chmod +x build-amd64.sh
   ./build-amd64.sh
   docker-compose -f docker-compose.amd64.yml up -d
   ```

### Services

The stack includes:

- **Neo4j Database** (port 7474 for browser, 7687 for bolt)
  - Username: `neo4j`
  - Password: `tradiemate123`
  - Includes Graph Data Science plugin

- **FastAPI Backend** 
  - Standard: port 12000
  - AMD64: port 10000 (optimized for production)
  - CrewAI agents and API endpoints
  - Health check at `/health`
  - Binds to 0.0.0.0 for external access

- **Next.js Frontend** (port 12001)
  - React-based user interface
  - Connected to backend and Supabase

- **Supabase Database** (port 54322)
  - PostgreSQL for frontend data

- **Supabase API** (port 54321)
  - Authentication and API services

### Access Points

**Standard deployment:**
- Frontend: http://localhost:12001
- Backend API: http://localhost:12000
- Neo4j Browser: http://localhost:7474
- Supabase API: http://localhost:54321

**AMD64 deployment:**
- Frontend: http://localhost:12001
- Backend API: http://localhost:10000
- Neo4j Browser: http://localhost:7474
- Supabase API: http://localhost:54321

### Troubleshooting

- Check logs: `docker-compose logs [service-name]`
- Restart services: `docker-compose restart`
- Rebuild: `docker-compose up --build`

## AMD64 Optimizations

The AMD64 version includes:
- **Platform Specification**: Explicit linux/amd64 targeting
- **Resource Limits**: Memory and CPU allocation for production
- **Performance Tuning**: Architecture-specific optimizations
- **Security**: Non-root users and minimal attack surface
- **Port Configuration**: Backend runs on port 10000 for production

## Changes Made

- Fixed duplicate environment variable in Supabase API configuration
- Restored AMD64-optimized docker-compose configuration
- Updated AMD64 backend to use port 10000 binding to 0.0.0.0
- All Dockerfiles are properly referenced and exist in the project
- Maintained both standard and AMD64 deployment options