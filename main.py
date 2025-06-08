from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, validator
from cai import run_crew_query
import uvicorn
import os
import logging.config
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import time
from contextlib import asynccontextmanager

# Import production configurations
from logging_config import setup_logging, get_logger
from security_config import SecurityConfig, APIKeyAuth, RateLimiter, get_security_headers, validate_query_input

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.config.dictConfig(setup_logging())
logger = get_logger(__name__)

# Initialize security components
security_config = SecurityConfig()
api_key_auth = APIKeyAuth(auto_error=False)
rate_limiter = RateLimiter()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting TradieMate Marketing Analytics Platform")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Port: {os.getenv('PORT', '12000')}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down TradieMate Marketing Analytics Platform")

class QueryRequest(BaseModel):
    query: str
    
    @validator('query')
    def validate_query(cls, v):
        if not validate_query_input(v):
            raise ValueError('Invalid query input')
        return v.strip()

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: str
    environment: str

class ErrorResponse(BaseModel):
    error: str
    detail: str
    timestamp: str

# Initialize FastAPI app
app = FastAPI(
    title="TradieMate Marketing Analytics Platform",
    description="A FastAPI server that uses CrewAI and Neo4j MCP to analyze Google Ads campaigns and website performance data, providing actionable optimization recommendations for trade businesses",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
allowed_origins = security_config.get_allowed_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Add security headers
    for header, value in get_security_headers().items():
        response.headers[header] = value
    
    return response

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    client_ip = request.client.host
    
    if not rate_limiter.is_allowed(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {security_config.hash_sensitive_data(client_ip)}")
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded", "detail": "Too many requests"}
        )
    
    response = await call_next(request)
    return response

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    return response

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with basic information"""
    logger.info("Root endpoint accessed")
    return {
        "message": "TradieMate Marketing Analytics Platform",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    from datetime import datetime
    
    # Check environment variables
    required_vars = ["OPENAI_API_KEY", "NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.warning(f"Health check failed - missing environment variables: {missing_vars}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable - missing environment variables: {missing_vars}"
        )
    
    return HealthResponse(
        status="healthy",
        message="Server is running and ready to process marketing analytics queries",
        timestamp=datetime.now().isoformat(),
        environment=os.getenv("ENVIRONMENT", "development")
    )

@app.post("/crewai", response_model=Dict[str, Any])
async def query_crew_endpoint(
    request: QueryRequest,
    credentials: Optional[str] = Depends(api_key_auth)
):
    """
    Process a natural language marketing analytics query using CrewAI
    
    Args:
        request: QueryRequest containing the natural language query
        credentials: Optional API key for authentication
        
    Returns:
        Dict containing the processed marketing analysis result
    """
    logger.info(f"Processing marketing query: {security_config.hash_sensitive_data(request.query)}")
    
    try:
        result = run_crew_query(request.query)
        logger.info("Marketing query processed successfully")
        return result
    except Exception as e:
        error_msg = f"Error processing marketing query: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    from datetime import datetime
    
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail="An unexpected error occurred",
            timestamp=datetime.now().isoformat()
        ).dict()
    )

# Serve static frontend files
static_dir = "/app/static"
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    @app.get("/")
    async def serve_frontend():
        """Serve the frontend index.html"""
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "TradieMate Marketing Analytics API", "docs": "/docs"}
    
    @app.get("/{path:path}")
    async def serve_frontend_routes(path: str):
        """Serve frontend static files"""
        # Skip API routes
        if path.startswith(("api/", "docs", "health", "crewai")):
            raise HTTPException(status_code=404, detail="Not found")
        
        # Try to serve the file
        file_path = os.path.join(static_dir, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Fallback to index.html for SPA routing
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        
        raise HTTPException(status_code=404, detail="Not found")
else:
    @app.get("/")
    async def api_info():
        return {"message": "TradieMate Marketing Analytics API", "docs": "/docs"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 12000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=True)