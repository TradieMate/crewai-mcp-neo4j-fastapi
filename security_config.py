"""
Production security configuration for TradieMate Marketing Analytics Platform
"""
import os
from typing import List, Optional
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta

class SecurityConfig:
    """Security configuration and utilities"""
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.api_key_header = "X-API-Key"
        self.rate_limit_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour
        
    def get_allowed_origins(self) -> List[str]:
        """Get allowed CORS origins based on environment"""
        if self.environment == "production":
            origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
            return [origin.strip() for origin in origins if origin.strip()]
        else:
            # Development - allow all origins
            return ["*"]
    
    def get_api_keys(self) -> List[str]:
        """Get valid API keys from environment"""
        api_keys = os.getenv("API_KEYS", "").split(",")
        return [key.strip() for key in api_keys if key.strip()]
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key"""
        valid_keys = self.get_api_keys()
        if not valid_keys:
            # If no API keys configured, allow access (development mode)
            return True
        
        return api_key in valid_keys
    
    def generate_api_key(self) -> str:
        """Generate a secure API key"""
        return secrets.token_urlsafe(32)
    
    def hash_sensitive_data(self, data: str) -> str:
        """Hash sensitive data for logging"""
        return hashlib.sha256(data.encode()).hexdigest()[:8]

# Security middleware
class APIKeyAuth(HTTPBearer):
    """API Key authentication"""
    
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
        self.security_config = SecurityConfig()
    
    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        # Skip authentication in development if no API keys configured
        if (self.security_config.environment == "development" and 
            not self.security_config.get_api_keys()):
            return None
            
        # Check for API key in header
        api_key = request.headers.get(self.security_config.api_key_header)
        if api_key and self.security_config.validate_api_key(api_key):
            return HTTPAuthorizationCredentials(scheme="ApiKey", credentials=api_key)
        
        # Check for Bearer token
        credentials = await super().__call__(request)
        if credentials and self.security_config.validate_api_key(credentials.credentials):
            return credentials
            
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )

# Rate limiting (simple in-memory implementation)
class RateLimiter:
    """Simple rate limiter for API endpoints"""
    
    def __init__(self):
        self.requests = {}
        self.security_config = SecurityConfig()
    
    def is_allowed(self, client_ip: str) -> bool:
        """Check if request is allowed based on rate limit"""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.security_config.rate_limit_window)
        
        # Clean old entries
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip] 
                if req_time > window_start
            ]
        else:
            self.requests[client_ip] = []
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.security_config.rate_limit_requests:
            return False
        
        # Add current request
        self.requests[client_ip].append(now)
        return True

# Security headers middleware
def get_security_headers() -> dict:
    """Get security headers for responses"""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

# Input validation
def validate_query_input(query: str) -> bool:
    """Validate user query input for security"""
    if not query or not isinstance(query, str):
        return False
    
    # Check length
    if len(query) > 1000:  # Max 1000 characters
        return False
    
    # Check for potentially malicious patterns
    malicious_patterns = [
        "javascript:",
        "<script",
        "eval(",
        "exec(",
        "import(",
        "__import__",
        "subprocess",
        "os.system",
        "shell=True"
    ]
    
    query_lower = query.lower()
    for pattern in malicious_patterns:
        if pattern in query_lower:
            return False
    
    return True