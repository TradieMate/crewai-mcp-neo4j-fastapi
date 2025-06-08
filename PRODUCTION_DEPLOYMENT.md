# Production Deployment Guide

This guide covers deploying the TradieMate Marketing Analytics Platform to production environments.

## 🚀 Pre-Deployment Checklist

### ✅ **Security Requirements**
- [ ] API keys configured in secure environment variables
- [ ] CORS origins restricted to production domains
- [ ] Rate limiting configured appropriately
- [ ] Security headers enabled
- [ ] Input validation implemented
- [ ] Non-root user in Docker container

### ✅ **Environment Configuration**
- [ ] Production environment variables set
- [ ] Neo4j database accessible and configured
- [ ] OpenAI API key valid and has sufficient credits
- [ ] Logging configuration appropriate for production
- [ ] Health checks configured

### ✅ **Infrastructure Requirements**
- [ ] Container orchestration platform ready (Docker, Kubernetes, etc.)
- [ ] Load balancer configured (if needed)
- [ ] SSL/TLS certificates installed
- [ ] Monitoring and alerting set up
- [ ] Backup strategy for logs and data

## 🔧 Environment Variables

### **Required Variables**
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_production_openai_api_key

# Neo4j Database Configuration
NEO4J_URI=neo4j+s://your-production-neo4j-instance
NEO4J_USERNAME=your_neo4j_username
NEO4J_PASSWORD=your_secure_neo4j_password

# Server Configuration
PORT=12000
HOST=0.0.0.0
ENVIRONMENT=production

# Security Configuration
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
API_KEYS=your_secure_api_key_1,your_secure_api_key_2

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Logging
LOG_LEVEL=INFO
```

### **Optional Variables**
```bash
# Advanced Configuration
WORKERS=1
MAX_CONNECTIONS=100
TIMEOUT=30
```

## 🐳 Docker Deployment

### **1. Build Production Image**
```bash
# Build optimized production image
docker build -t tradie-marketing-analytics:latest .

# Tag for registry
docker tag tradie-marketing-analytics:latest your-registry/tradie-marketing-analytics:v1.0.0
```

### **2. Run Container**
```bash
# Run with environment file
docker run -d \
  --name tradie-marketing \
  --env-file .env.production \
  -p 12000:12000 \
  --restart unless-stopped \
  --memory="1g" \
  --cpus="0.5" \
  tradie-marketing-analytics:latest
```

### **3. Docker Compose Production**
```yaml
version: '3.8'
services:
  tradie-marketing:
    image: tradie-marketing-analytics:latest
    ports:
      - "12000:12000"
    environment:
      - ENVIRONMENT=production
    env_file:
      - .env.production
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:12000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## ☸️ Kubernetes Deployment

### **1. ConfigMap for Environment Variables**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: tradie-marketing-config
data:
  ENVIRONMENT: "production"
  PORT: "12000"
  HOST: "0.0.0.0"
  LOG_LEVEL: "INFO"
  RATE_LIMIT_REQUESTS: "100"
  RATE_LIMIT_WINDOW: "3600"
```

### **2. Secret for Sensitive Data**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: tradie-marketing-secrets
type: Opaque
stringData:
  OPENAI_API_KEY: "your_openai_api_key"
  NEO4J_URI: "neo4j+s://your-neo4j-instance"
  NEO4J_USERNAME: "your_username"
  NEO4J_PASSWORD: "your_password"
  API_KEYS: "your_api_keys"
```

### **3. Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tradie-marketing-analytics
spec:
  replicas: 2
  selector:
    matchLabels:
      app: tradie-marketing
  template:
    metadata:
      labels:
        app: tradie-marketing
    spec:
      containers:
      - name: tradie-marketing
        image: tradie-marketing-analytics:v1.0.0
        ports:
        - containerPort: 12000
        envFrom:
        - configMapRef:
            name: tradie-marketing-config
        - secretRef:
            name: tradie-marketing-secrets
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 12000
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 12000
          initialDelaySeconds: 5
          periodSeconds: 10
```

### **4. Service**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: tradie-marketing-service
spec:
  selector:
    app: tradie-marketing
  ports:
  - port: 80
    targetPort: 12000
  type: ClusterIP
```

## 🌐 Cloud Platform Deployments

### **AWS ECS/Fargate**
```json
{
  "family": "tradie-marketing-analytics",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "tradie-marketing",
      "image": "your-ecr-repo/tradie-marketing-analytics:latest",
      "portMappings": [
        {
          "containerPort": 12000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"},
        {"name": "PORT", "value": "12000"}
      ],
      "secrets": [
        {"name": "OPENAI_API_KEY", "valueFrom": "arn:aws:secretsmanager:region:account:secret:openai-key"},
        {"name": "NEO4J_URI", "valueFrom": "arn:aws:secretsmanager:region:account:secret:neo4j-uri"}
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:12000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      },
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/tradie-marketing",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### **Google Cloud Run**
```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: tradie-marketing-analytics
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containerConcurrency: 80
      containers:
      - image: gcr.io/your-project/tradie-marketing-analytics:latest
        ports:
        - containerPort: 12000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: PORT
          value: "12000"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-key
              key: api-key
        resources:
          limits:
            cpu: "1"
            memory: "1Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 12000
          initialDelaySeconds: 30
          periodSeconds: 30
```

## 📊 Monitoring & Observability

### **Health Monitoring**
```bash
# Health check endpoint
curl https://your-domain.com/health

# Expected response
{
  "status": "healthy",
  "message": "Server is running and ready to process marketing analytics queries",
  "timestamp": "2024-01-01T12:00:00",
  "environment": "production"
}
```

### **Logging**
- Application logs: `/app/logs/app.log`
- Error logs: `/app/logs/error.log`
- Access logs: Uvicorn access logs
- Structured JSON logging in production

### **Metrics to Monitor**
- Response time (< 5 seconds for queries)
- Error rate (< 1%)
- Memory usage (< 80% of allocated)
- CPU usage (< 70% of allocated)
- Request rate and rate limiting
- Health check success rate

### **Alerting Rules**
```yaml
# Example Prometheus alerting rules
groups:
- name: tradie-marketing-alerts
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"
      
  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 5
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"
      
  - alert: ServiceDown
    expr: up{job="tradie-marketing"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "TradieMate Marketing Analytics service is down"
```

## 🔒 Security Best Practices

### **1. API Key Management**
- Use secure secret management (AWS Secrets Manager, Azure Key Vault, etc.)
- Rotate API keys regularly
- Monitor API key usage
- Implement key-specific rate limiting

### **2. Network Security**
- Use HTTPS/TLS encryption
- Restrict CORS origins to production domains
- Implement IP whitelisting if needed
- Use private networks for database connections

### **3. Container Security**
- Run as non-root user
- Use minimal base images
- Scan images for vulnerabilities
- Keep dependencies updated

### **4. Input Validation**
- Validate all user inputs
- Sanitize query parameters
- Implement request size limits
- Use parameterized queries

## 🚨 Troubleshooting

### **Common Issues**

1. **Health Check Failures**
   ```bash
   # Check environment variables
   docker exec container-name env | grep -E "(OPENAI|NEO4J)"
   
   # Check logs
   docker logs container-name
   ```

2. **High Memory Usage**
   ```bash
   # Monitor memory usage
   docker stats container-name
   
   # Adjust memory limits
   docker update --memory="2g" container-name
   ```

3. **Rate Limiting Issues**
   ```bash
   # Check rate limit configuration
   curl -H "X-API-Key: your-key" https://your-domain.com/health
   
   # Adjust rate limits in environment variables
   RATE_LIMIT_REQUESTS=200
   RATE_LIMIT_WINDOW=3600
   ```

4. **Database Connection Issues**
   ```bash
   # Test Neo4j connectivity
   docker exec container-name curl -v neo4j://your-neo4j-instance:7687
   
   # Check credentials
   docker exec container-name env | grep NEO4J
   ```

### **Performance Optimization**

1. **Scaling**
   - Horizontal scaling: Add more container instances
   - Vertical scaling: Increase CPU/memory limits
   - Load balancing: Distribute requests across instances

2. **Caching**
   - Implement Redis for query result caching
   - Cache frequently accessed data
   - Use CDN for static assets

3. **Database Optimization**
   - Optimize Neo4j queries
   - Use connection pooling
   - Monitor query performance

## 📋 Deployment Checklist

### **Pre-Deployment**
- [ ] All tests passing
- [ ] Security scan completed
- [ ] Environment variables configured
- [ ] Secrets properly managed
- [ ] Monitoring set up
- [ ] Backup strategy in place

### **Deployment**
- [ ] Blue-green deployment strategy
- [ ] Health checks passing
- [ ] Smoke tests completed
- [ ] Performance tests passed
- [ ] Security tests passed

### **Post-Deployment**
- [ ] Monitor application metrics
- [ ] Check error logs
- [ ] Verify functionality with test queries
- [ ] Update documentation
- [ ] Notify stakeholders

## 🔄 Maintenance

### **Regular Tasks**
- Update dependencies monthly
- Rotate API keys quarterly
- Review and update security configurations
- Monitor and optimize performance
- Backup logs and configurations
- Test disaster recovery procedures

### **Monitoring Dashboard**
Create dashboards to monitor:
- Request volume and response times
- Error rates and types
- Resource utilization
- Security events
- Business metrics (query types, user patterns)

This production deployment guide ensures a secure, scalable, and maintainable deployment of the TradieMate Marketing Analytics Platform.