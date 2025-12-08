# 🚀 Render Deployment Guide

Complete guide to deploy the ML Backend to Render with CI/CD using GitHub Actions.

---

## 📋 Prerequisites

- GitHub account with repository
- Render account (sign up at https://render.com)
- Neon PostgreSQL database set up
- Docker Hub account (optional, for custom images)

---

## 🌐 Step 1: Create Render Account

1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repositories

---

## 🔧 Step 2: Create Web Service on Render

### 2.1 From Dashboard

1. Click **New +** → **Web Service**
2. Connect your GitHub repository
3. Configure service:

```yaml
Name: credit-scoring-ml-api
Environment: Docker
Region: Oregon (US West)
Branch: main
Dockerfile Path: ./ml-backend/Dockerfile
Docker Context: ./ml-backend
```

### 2.2 Instance Type

**For Development:**
- Instance Type: Starter ($7/month)
- CPU: 0.5
- RAM: 512 MB

**For Production:**
- Instance Type: Standard ($25/month)
- CPU: 1
- RAM: 2 GB

---

## 🔐 Step 3: Configure Environment Variables

In Render dashboard, add these environment variables:

### Required

```bash
# Database
DATABASE_URL=postgresql://user:pass@host.neon.tech/mldb?sslmode=require

# Application
ENVIRONMENT=production
PORT=8000
WORKERS=2
LOG_LEVEL=info

# MLflow
MLFLOW_TRACKING_URI=/app/mlruns

# Monitoring
PROMETHEUS_ENABLED=true
DRIFT_DETECTION_ENABLED=true
DRIFT_CHECK_INTERVAL=3600
```

### Optional

```bash
# Alerts
SENTRY_DSN=your_sentry_dsn
ALERT_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK

# Feature Flags
ENABLE_CORS=true
CORS_ORIGINS=*
```

---

## 💾 Step 4: Add Persistent Disk

Models and MLflow data need persistent storage:

1. In Render dashboard, go to **Disks** tab
2. Click **Add Disk**
3. Configure:
   ```
   Name: ml-models-disk
   Mount Path: /app/models
   Size: 10 GB
   ```

4. Add another disk for MLflow:
   ```
   Name: mlruns-disk
   Mount Path: /app/mlruns
   Size: 5 GB
   ```

---

## 🏗️ Step 5: Configure Build & Deploy

### Build Command

Render automatically detects Dockerfile, but you can customize:

```bash
# Optional: Custom build command
docker build -t ml-backend:latest -f ./ml-backend/Dockerfile ./ml-backend
```

### Start Command

Defined in `Dockerfile`, but can override:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers $WORKERS
```

### Health Check

Render uses this endpoint:
```
Path: /health
Expected Status: 200
Timeout: 30s
Interval: 30s
```

---

## 🔄 Step 6: Set Up Auto-Deploy

### 6.1 Enable Auto-Deploy

In Render dashboard:
1. Go to **Settings** tab
2. Enable **Auto-Deploy**
3. Select branch: `main`

Now every push to `main` triggers automatic deployment.

### 6.2 Deploy Hooks (Optional)

Get deploy hook URL:
1. Go to **Settings** → **Deploy Hook**
2. Copy webhook URL
3. Use in CI/CD or external tools

---

## 🤖 Step 7: GitHub Actions CI/CD Setup

### 7.1 Add GitHub Secrets

In your GitHub repository:
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add these secrets:

```bash
RENDER_API_KEY=your_render_api_key
RENDER_SERVICE_ID=srv-xxxxxxxxxxxxx
RENDER_SERVICE_URL=https://your-service.onrender.com
DATABASE_URL=postgresql://...neon.tech/mldb

# Optional
DOCKER_USERNAME=your_dockerhub_username
DOCKER_PASSWORD=your_dockerhub_token
```

### 7.2 Get Render API Key

1. Go to Render dashboard → **Account Settings**
2. Click **API Keys** tab
3. Create new API key
4. Copy and add to GitHub secrets

### 7.3 Get Service ID

From your service URL:
```
https://dashboard.render.com/web/srv-xxxxxxxxxxxxx
                                    ↑ This is your SERVICE_ID
```

---

## 🧪 Step 8: Test Deployment

### 8.1 Manual Deploy

1. Go to Render dashboard
2. Click **Manual Deploy** → **Deploy latest commit**
3. Monitor logs in real-time

### 8.2 Check Health

```bash
curl https://your-service.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "mlflow": true,
  "models": {
    "random_forest": false,
    "deep_learning": false
  }
}
```

### 8.3 Test Prediction Endpoint

```bash
curl -X POST https://your-service.onrender.com/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "credit_score": 750,
      "income": 75000,
      "loan_amount": 25000,
      "employment_years": 5,
      "debt_to_income": 0.3
    },
    "model_type": "random_forest",
    "explain": false
  }'
```

---

## 📊 Step 9: Set Up Monitoring

### 9.1 Render Metrics

Render provides built-in monitoring:
- CPU usage
- Memory usage
- Request count
- Response times

Access at: Dashboard → Your Service → **Metrics**

### 9.2 Custom Metrics (Prometheus)

Your app exposes metrics at `/metrics`:

```bash
curl https://your-service.onrender.com/metrics
```

### 9.3 Set Up Alerts

1. Go to **Notifications** tab in Render
2. Add notification rules:
   ```
   - Service unhealthy for 5 minutes
   - Deploy failed
   - Memory usage > 90%
   ```

3. Configure webhook or email notifications

---

## 🔍 Step 10: Monitor Logs

### Real-Time Logs

In Render dashboard:
1. Go to **Logs** tab
2. View real-time application logs
3. Filter by log level (INFO, WARNING, ERROR)

### Download Logs

```bash
# Using Render CLI
render logs --service your-service-id --tail 1000 > logs.txt
```

### Log Aggregation (Advanced)

Send logs to external service:
- Datadog
- New Relic
- Sentry
- Logtail

Configure via environment variables.

---

## 🔄 Step 11: Rollback Strategy

### Automatic Rollback

Render automatically rolls back if:
- Health check fails after deploy
- Service crashes repeatedly

### Manual Rollback

1. Go to **Deploys** tab
2. Find previous successful deploy
3. Click **Rollback to this deploy**

### Using API

```bash
curl -X POST \
  "https://api.render.com/v1/services/$SERVICE_ID/deploys/$DEPLOY_ID/rollback" \
  -H "Authorization: Bearer $RENDER_API_KEY"
```

---

## 🚀 Step 12: Scaling

### Vertical Scaling

Upgrade instance type:
1. Go to **Settings** tab
2. Change **Instance Type**
3. Options: Starter → Standard → Pro

### Horizontal Scaling (Auto-Scaling)

Configure auto-scaling:
```yaml
# In render.yaml
services:
  - type: web
    name: ml-api
    scaling:
      minInstances: 1
      maxInstances: 3
      targetMemoryPercent: 80
      targetCPUPercent: 70
```

---

## 🔐 Step 13: Security

### 13.1 Environment Secrets

Never commit sensitive data:
- Use Render environment variables
- Rotate secrets regularly

### 13.2 HTTPS/SSL

Render provides free SSL:
- Automatic certificate provisioning
- Auto-renewal
- Force HTTPS redirect

### 13.3 DDoS Protection

Render includes:
- Rate limiting
- DDoS mitigation
- CDN edge caching

---

## 🐛 Step 14: Troubleshooting

### Build Fails

**Check:**
1. Dockerfile syntax
2. requirements.txt dependencies
3. Build logs in Render dashboard

**Solution:**
```bash
# Test locally
docker build -t test-ml-backend -f ml-backend/Dockerfile ml-backend
docker run -p 8000:8000 test-ml-backend
```

### Health Check Fails

**Check:**
1. `/health` endpoint responds
2. Database connection works
3. Service starts within timeout

**Solution:**
```bash
# Check logs
render logs --service your-service-id --tail 100
```

### High Memory Usage

**Solutions:**
1. Upgrade instance type
2. Optimize model loading
3. Implement model caching
4. Use model compression

### Slow Response Times

**Solutions:**
1. Enable caching
2. Optimize database queries
3. Use connection pooling
4. Add read replicas

---

## 📈 Step 15: Performance Optimization

### 1. Enable Caching

```python
# In app/main.py
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    FastAPICache.init(RedisBackend(), prefix="fastapi-cache")
```

### 2. Connection Pooling

Already configured in Prisma:
```python
# Prisma automatically pools connections
# Max connections: 10 (default)
```

### 3. Async Operations

Use async/await for I/O operations:
```python
# Database queries
await db_manager.log_prediction(...)

# HTTP requests
async with httpx.AsyncClient() as client:
    await client.get(url)
```

### 4. Model Caching

Cache loaded models:
```python
from functools import lru_cache

@lru_cache(maxsize=10)
def get_model(model_id: str):
    return load_model(model_id)
```

---

## 🔄 Step 16: Continuous Deployment Flow

### Development → Staging → Production

```
1. Develop on branch: feature/new-model
   ↓
2. Push to GitHub
   ↓
3. GitHub Actions runs tests
   ↓
4. Merge to develop → Deploy to Staging
   ↓
5. Test on staging
   ↓
6. Merge to main → Deploy to Production
   ↓
7. Monitor metrics
```

### Branch Strategy

```
main (production) ← merge from develop
  ↑
develop (staging) ← merge from feature branches
  ↑
feature/new-feature ← development
```

---

## 📊 Step 17: Cost Optimization

### Instance Sizing

```
Development: Starter ($7/month)
  - 0.5 CPU, 512 MB RAM
  - Good for testing

Production: Standard ($25/month)
  - 1 CPU, 2 GB RAM
  - Handles 100-200 req/min

High Traffic: Pro ($85/month)
  - 2 CPU, 4 GB RAM
  - Handles 500+ req/min
```

### Disk Usage

```
Models: 10 GB ($1/GB/month) = $10/month
MLflow: 5 GB = $5/month
Total: $15/month for storage
```

### Total Estimated Cost

```
Starter Plan: $7 + $15 = $22/month
Standard Plan: $25 + $15 = $40/month
Pro Plan: $85 + $15 = $100/month
```

---

## ✅ Deployment Checklist

- [ ] Created Render account
- [ ] Connected GitHub repository
- [ ] Created web service with Docker
- [ ] Configured environment variables
- [ ] Added persistent disks for models/mlruns
- [ ] Set up Neon database connection
- [ ] Enabled auto-deploy from main branch
- [ ] Added GitHub secrets for CI/CD
- [ ] Tested manual deployment
- [ ] Verified health check endpoint
- [ ] Tested prediction API
- [ ] Set up monitoring and alerts
- [ ] Configured log streaming
- [ ] Documented rollback procedure
- [ ] Set up Prometheus metrics
- [ ] Configured auto-scaling (optional)

---

## 🎉 Your ML Backend is Live!

Access your API at: `https://your-service.onrender.com`

**Endpoints:**
- Health: `GET /health`
- Predictions: `POST /api/predict`
- Training: `POST /api/train`
- Fairness: `POST /api/fairness/analyze`
- Drift: `POST /api/monitoring/drift`
- Metrics: `GET /metrics`

**Monitoring:**
- Render Dashboard: https://dashboard.render.com
- Logs: Real-time in Render dashboard
- Metrics: `/metrics` endpoint
- Prisma Studio: `prisma studio` (local only)

---

## 🔗 Resources

- **Render Docs**: https://render.com/docs
- **Render API**: https://api-docs.render.com
- **Deploy Hooks**: https://render.com/docs/deploy-hooks
- **Zero Downtime Deploys**: https://render.com/docs/deploys

---

For support:
- Render Community: https://community.render.com
- GitHub Issues: Your repository issues
- Status Page: https://status.render.com
