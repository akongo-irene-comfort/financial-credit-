# ML Backend Deployment Guide

Complete guide for deploying the Credit Scoring ML Backend to production.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [CI/CD Setup](#cicd-setup)
6. [Monitoring Setup](#monitoring-setup)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 20GB minimum
- **OS**: Linux (Ubuntu 20.04+), macOS, Windows with WSL2

### Software Requirements
- Python 3.11+
- Docker 20.10+
- Docker Compose 2.0+
- Git

## Local Development

### 1. Setup Environment

```bash
# Clone repository
git clone <repo-url>
cd ml-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

### 3. Run Development Server

```bash
# Start FastAPI with hot reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Test the API

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

## Docker Deployment

### Option 1: Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f ml-backend

# Stop services
docker-compose down
```

Services:
- ML Backend: http://localhost:8000
- MLflow UI: http://localhost:5000

### Option 2: Docker Only

```bash
# Build image
docker build -t credit-scoring-ml-backend .

# Run container
docker run -d \
  --name ml-backend \
  -p 8000:8000 \
  -v $(pwd)/mlruns:/app/mlruns \
  -v $(pwd)/models:/app/models \
  credit-scoring-ml-backend

# View logs
docker logs -f ml-backend

# Stop container
docker stop ml-backend
```

## Cloud Deployment

### AWS Elastic Container Service (ECS)

#### 1. Build and Push to ECR

```bash
# Authenticate to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and tag image
docker build -t credit-scoring-ml-backend .
docker tag credit-scoring-ml-backend:latest \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com/credit-scoring-ml-backend:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/credit-scoring-ml-backend:latest
```

#### 2. Create ECS Task Definition

```json
{
  "family": "credit-scoring-ml-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "containerDefinitions": [
    {
      "name": "ml-backend",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/credit-scoring-ml-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "LOG_LEVEL",
          "value": "INFO"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/credit-scoring-ml-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### 3. Create ECS Service

```bash
aws ecs create-service \
  --cluster production-cluster \
  --service-name credit-scoring-ml-backend \
  --task-definition credit-scoring-ml-backend \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

### Google Cloud Run

```bash
# Build and submit to Cloud Build
gcloud builds submit --tag gcr.io/PROJECT_ID/credit-scoring-ml-backend

# Deploy to Cloud Run
gcloud run deploy credit-scoring-ml-backend \
  --image gcr.io/PROJECT_ID/credit-scoring-ml-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2
```

### Azure Container Instances

```bash
# Create resource group
az group create --name ml-backend-rg --location eastus

# Create container instance
az container create \
  --resource-group ml-backend-rg \
  --name credit-scoring-ml-backend \
  --image <registry>.azurecr.io/credit-scoring-ml-backend:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8000 \
  --dns-name-label credit-scoring-ml-backend \
  --environment-variables LOG_LEVEL=INFO
```

## CI/CD Setup

### GitHub Actions

1. **Add Secrets to Repository**
   - Go to Settings → Secrets and variables → Actions
   - Add:
     - `DOCKER_USERNAME`
     - `DOCKER_PASSWORD`
     - `AWS_ACCESS_KEY_ID` (for AWS)
     - `AWS_SECRET_ACCESS_KEY` (for AWS)

2. **Enable Actions**
   - The workflow is defined in `.github/workflows/ci-cd.yml`
   - Automatically triggers on push to `main` branch

3. **Monitor Builds**
   - Visit Actions tab in GitHub repository
   - View build logs and test results

### GitLab CI/CD

Create `.gitlab-ci.yml`:

```yaml
stages:
  - lint
  - test
  - build
  - deploy

variables:
  DOCKER_IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

lint:
  stage: lint
  image: python:3.11
  script:
    - pip install flake8 black
    - flake8 app/
    - black --check app/

test:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt pytest
    - pytest tests/

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $DOCKER_IMAGE .
    - docker push $DOCKER_IMAGE

deploy:
  stage: deploy
  script:
    - echo "Deploy to production"
  only:
    - main
```

## Monitoring Setup

### 1. MLflow Tracking

```bash
# Start MLflow UI
mlflow ui --backend-store-uri ./mlruns --host 0.0.0.0 --port 5000
```

Access at: http://localhost:5000

### 2. Application Logging

Configure structured logging:

```python
# In app/main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

### 3. Prometheus Metrics

Add Prometheus integration:

```bash
pip install prometheus-fastapi-instrumentator
```

```python
# In app/main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### 4. Health Monitoring

Set up health checks:

```bash
# Kubernetes liveness probe
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

# Kubernetes readiness probe
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Troubleshooting

### Common Issues

#### Issue: Import errors when starting server
```bash
# Solution: Ensure PYTHONPATH is set
export PYTHONPATH=/app:$PYTHONPATH
```

#### Issue: MLflow tracking not working
```bash
# Solution: Check MLFLOW_TRACKING_URI
echo $MLFLOW_TRACKING_URI
mkdir -p mlruns
```

#### Issue: Out of memory errors
```bash
# Solution: Increase Docker memory limit
# In docker-compose.yml:
services:
  ml-backend:
    deploy:
      resources:
        limits:
          memory: 8G
```

#### Issue: Slow model training
```bash
# Solution: Enable parallel processing
# In training code, set n_jobs=-1
model = RandomForestClassifier(n_jobs=-1)
```

### Debug Mode

```bash
# Run with debug logging
LOG_LEVEL=DEBUG uvicorn app.main:app --reload

# Access container shell
docker exec -it ml-backend bash

# Check logs
docker logs ml-backend --tail 100
```

### Performance Tuning

```python
# app/main.py
app = FastAPI(
    title="Credit Scoring ML API",
    workers=4,  # Increase workers
    timeout=300  # Increase timeout for long-running requests
)
```

## Security Best Practices

1. **Environment Variables**: Never commit `.env` files
2. **API Keys**: Use secrets management (AWS Secrets Manager, HashiCorp Vault)
3. **Network Security**: Use HTTPS in production
4. **Access Control**: Implement API authentication (JWT tokens)
5. **Input Validation**: Validate all API inputs
6. **Rate Limiting**: Implement rate limiting to prevent abuse

## Scaling

### Horizontal Scaling

```bash
# Docker Compose
docker-compose up --scale ml-backend=3

# Kubernetes
kubectl scale deployment ml-backend --replicas=5
```

### Load Balancing

```nginx
# Nginx configuration
upstream ml_backend {
    server ml-backend-1:8000;
    server ml-backend-2:8000;
    server ml-backend-3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://ml_backend;
    }
}
```

## Backup and Recovery

```bash
# Backup MLflow experiments
tar -czf mlruns-backup.tar.gz mlruns/

# Backup trained models
tar -czf models-backup.tar.gz models/

# Restore
tar -xzf mlruns-backup.tar.gz
tar -xzf models-backup.tar.gz
```

## Production Checklist

- [ ] Environment variables configured
- [ ] Docker image built and tested
- [ ] Health checks implemented
- [ ] Logging configured
- [ ] Monitoring setup (Prometheus/Grafana)
- [ ] CI/CD pipeline configured
- [ ] Security measures in place
- [ ] Backup strategy defined
- [ ] Load testing completed
- [ ] Documentation updated

---

For additional support, refer to the main README.md or open an issue on GitHub.
