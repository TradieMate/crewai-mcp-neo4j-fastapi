# Render Deployment Guide

This guide explains how to deploy TradieMate Marketing Analytics to Render.com.

## Architecture

The application is configured as a **single service** that runs both the FastAPI backend and Next.js frontend on **port 10000**, as required by Render.

### How it works:
1. **Backend**: FastAPI serves the API endpoints (`/api/*`, `/docs`, `/health`, `/crewai`)
2. **Frontend**: Next.js chat interface is built and served by the FastAPI server
3. **Single Port**: Everything runs on port 10000 with 0.0.0.0 binding

## Required Environment Variables

Set these in your Render service environment:

### Required
```bash
# OpenAI API Key (REQUIRED)
OPENAI_API_KEY=your_openai_api_key_here

# Neo4j Database (use hosted Neo4j like Neo4j Aura)
NEO4J_URI=neo4j+s://your-neo4j-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password
```

### Optional
```bash
# Additional API Keys
CREWAI_API_KEY=your_crewai_key_if_needed
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

# Security (optional)
API_KEYS=your_api_key_for_authentication
```

## Deployment Steps

### 1. Prepare Neo4j Database
- Sign up for [Neo4j Aura](https://neo4j.com/cloud/aura/) (free tier available)
- Create a new database instance
- Note the connection URI, username, and password

### 2. Deploy to Render
1. Connect your GitHub repository to Render
2. Create a new **Web Service**
3. Use these settings:
   - **Build Command**: `docker build -t tradie-app .`
   - **Start Command**: `docker run -p 10000:10000 tradie-app`
   - **Port**: `10000`

### 3. Set Environment Variables
In Render dashboard, add all the required environment variables listed above.

### 4. Deploy
Click "Deploy" and wait for the build to complete.

## Local Testing

Test the Render-compatible setup locally:

```bash
# Use the Render-specific docker-compose
docker-compose -f docker-compose.render.yml up --build

# Or test with external Neo4j
export NEO4J_URI=your_hosted_neo4j_uri
export NEO4J_USERNAME=neo4j
export NEO4J_PASSWORD=your_password
export OPENAI_API_KEY=your_key

docker-compose -f docker-compose.render.yml up --build
```

## Accessing the Application

Once deployed:
- **Frontend**: `https://your-app-name.onrender.com/`
- **API Docs**: `https://your-app-name.onrender.com/docs`
- **Health Check**: `https://your-app-name.onrender.com/health`
- **CrewAI Endpoint**: `https://your-app-name.onrender.com/crewai`

## Troubleshooting

### Build Issues
- Check that all environment variables are set
- Verify Neo4j connection details
- Check Render build logs

### Runtime Issues
- Check application logs in Render dashboard
- Verify Neo4j database is accessible
- Test API endpoints individually

### Frontend Issues
- Frontend is served by FastAPI on the same port
- Check browser console for errors
- Verify API calls are reaching `/crewai` endpoint

## File Structure

```
├── Dockerfile                 # Multi-stage build (frontend + backend)
├── docker-compose.yml         # Local development with Neo4j
├── docker-compose.render.yml  # Render deployment (single service)
├── main.py                    # FastAPI app with frontend serving
├── .env                       # Environment template
└── frontend/                  # Next.js chat interface
```

## Notes

- The frontend is built during Docker build and served by FastAPI
- All requests go through port 10000 as required by Render
- Neo4j must be hosted externally (Neo4j Aura recommended)
- The application automatically detects if frontend is available