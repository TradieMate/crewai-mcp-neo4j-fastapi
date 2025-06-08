"""
Test suite for TradieMate Marketing Analytics Platform
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os
import json

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["NEO4J_URI"] = "neo4j://test:7687"
os.environ["NEO4J_USERNAME"] = "test"
os.environ["NEO4J_PASSWORD"] = "test"

from main import app

client = TestClient(app)

class TestHealthEndpoints:
    """Test health and basic endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "TradieMate Marketing Analytics Platform"
        assert "docs" in data
        assert "health" in data
        assert "version" in data
    
    def test_health_check_success(self):
        """Test health check with valid environment"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "environment" in data
    
    def test_health_check_missing_env_vars(self):
        """Test health check with missing environment variables"""
        with patch.dict(os.environ, {}, clear=True):
            response = client.get("/health")
            assert response.status_code == 503
            assert "missing environment variables" in response.json()["detail"]

class TestSecurityFeatures:
    """Test security features"""
    
    def test_security_headers(self):
        """Test that security headers are present"""
        response = client.get("/")
        headers = response.headers
        
        assert "X-Content-Type-Options" in headers
        assert "X-Frame-Options" in headers
        assert "X-XSS-Protection" in headers
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert headers["X-Frame-Options"] == "DENY"
    
    def test_cors_headers(self):
        """Test CORS configuration"""
        response = client.options("/", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200

class TestQueryValidation:
    """Test query input validation"""
    
    def test_valid_query(self):
        """Test valid marketing query"""
        with patch('main.run_crew_query') as mock_crew:
            mock_crew.return_value = {"result": "test result", "status": "success"}
            
            response = client.post("/crewai", json={
                "query": "What are our top performing Google Ads campaigns?"
            })
            assert response.status_code == 200
            assert mock_crew.called
    
    def test_empty_query(self):
        """Test empty query validation"""
        response = client.post("/crewai", json={"query": ""})
        assert response.status_code == 422  # Validation error
    
    def test_malicious_query(self):
        """Test malicious query rejection"""
        malicious_queries = [
            "javascript:alert('xss')",
            "<script>alert('xss')</script>",
            "eval('malicious code')",
            "import os; os.system('rm -rf /')"
        ]
        
        for query in malicious_queries:
            response = client.post("/crewai", json={"query": query})
            assert response.status_code == 422  # Validation error
    
    def test_long_query(self):
        """Test overly long query rejection"""
        long_query = "a" * 1001  # Over 1000 character limit
        response = client.post("/crewai", json={"query": long_query})
        assert response.status_code == 422  # Validation error

class TestMarketingQueries:
    """Test marketing-specific query handling"""
    
    @patch('main.run_crew_query')
    def test_google_ads_query(self, mock_crew):
        """Test Google Ads optimization query"""
        mock_crew.return_value = {
            "result": "Google Ads analysis complete",
            "status": "success"
        }
        
        response = client.post("/crewai", json={
            "query": "How can we improve our plumbing ads ROAS?"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        mock_crew.assert_called_once()
    
    @patch('main.run_crew_query')
    def test_website_optimization_query(self, mock_crew):
        """Test website optimization query"""
        mock_crew.return_value = {
            "result": "Website optimization analysis complete",
            "status": "success"
        }
        
        response = client.post("/crewai", json={
            "query": "Why is our landing page conversion rate declining?"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        mock_crew.assert_called_once()
    
    @patch('main.run_crew_query')
    def test_crew_query_error_handling(self, mock_crew):
        """Test error handling in crew query"""
        mock_crew.side_effect = Exception("CrewAI processing error")
        
        response = client.post("/crewai", json={
            "query": "What are our top campaigns?"
        })
        
        assert response.status_code == 500
        assert "Error processing marketing query" in response.json()["detail"]

class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limit_not_exceeded(self):
        """Test normal request rate"""
        # Make a few requests (should be under limit)
        for _ in range(5):
            response = client.get("/health")
            assert response.status_code == 200
    
    @patch('main.rate_limiter.is_allowed')
    def test_rate_limit_exceeded(self, mock_rate_limiter):
        """Test rate limit exceeded"""
        mock_rate_limiter.return_value = False
        
        response = client.get("/health")
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["error"]

class TestErrorHandling:
    """Test error handling"""
    
    def test_404_endpoint(self):
        """Test non-existent endpoint"""
        response = client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_json(self):
        """Test invalid JSON in request"""
        response = client.post("/crewai", 
                             data="invalid json",
                             headers={"Content-Type": "application/json"})
        assert response.status_code == 422

# Performance tests
class TestPerformance:
    """Test performance characteristics"""
    
    @patch('main.run_crew_query')
    def test_response_time(self, mock_crew):
        """Test response time is reasonable"""
        import time
        
        mock_crew.return_value = {"result": "test", "status": "success"}
        
        start_time = time.time()
        response = client.post("/crewai", json={
            "query": "Test query for performance"
        })
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 5.0  # Should respond within 5 seconds

# Integration tests
class TestIntegration:
    """Integration tests (require actual services)"""
    
    @pytest.mark.integration
    def test_full_marketing_query_flow(self):
        """Test complete marketing query flow (requires real services)"""
        # This test would require actual Neo4j and OpenAI connections
        # Skip in unit tests, run separately for integration testing
        pytest.skip("Integration test - requires live services")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])