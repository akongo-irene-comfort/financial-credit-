# 🚀 Complete CI/CD Guide - Full Stack Credit Scoring System

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Setup Instructions](#setup-instructions)
- [GitHub Actions Workflows](#github-actions-workflows)
- [Docker Configuration](#docker-configuration)
- [Deployment to Render](#deployment-to-render)
- [Monitoring & Drift Detection](#monitoring--drift-detection)
- [Database Setup (Neon + Prisma)](#database-setup-neon--prisma)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This is a **comprehensive CI/CD pipeline** for your full-stack ML system:

### **System Components**
- **Frontend**: Next.js 15 (TypeScript, Tailwind CSS)
- **Backend**: FastAPI (Python 3.11, ML models, Prisma ORM)
- **Database**: Neon PostgreSQL (Serverless)
- **Deployment**: Render (Docker containers)
- **Monitoring**: Prometheus + Grafana
- **ML Tracking**: MLflow

### **CI/CD Features**
✅ Automated testing (unit + integration)  
✅ Code quality checks (linting, formatting, security)  
✅ Docker containerization  
✅ Blue-green deployment  
✅ Data drift detection  
✅ Model drift monitoring  
✅ Automated retraining triggers  
✅ Health checks & smoke tests  

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         GITHUB REPOSITORY                        │
│  ┌────────────┐              ┌────────────┐                     │
│  │  Frontend  │              │  Backend   │                     │
│  │  (Next.js) │              │  (FastAPI) │                     │
│  └──────┬─────┘              └──────┬─────┘                     │
└─────────┼─────────────────────────┼─────────────────────────────┘
          │                          │
          │      [Git Push]          │
          ▼                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                       GITHUB ACTIONS CI/CD                       │
│  ┌───────────────┐       ┌───────────────┐                     │
│  │ Frontend CI   │       │  Backend CI   │                     │
│  │ - Lint        │       │ - Lint        │                     │
│  │ - Build       │       │ - Unit Tests  │                     │
│  │ - Docker      │       │ - Integration │                     │
│  └───────┬───────┘       └───────┬───────┘                     │
│          │                       │                              │
│          └───────┬───────────────┘                              │
│                  │                                               │
│          ┌───────▼────────┐                                     │
│          │ Full Stack CI  │                                     │
│          │ Integration    │                                     │
│          └───────┬────────┘                                     │
└──────────────────┼──────────────────────────────────────────────┘
                   │
                   │  [Deploy]
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RENDER PLATFORM                             │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐            │
│  │  Frontend  │◄───┤  Backend   │◄───┤  Database  │            │
│  │  Service   │    │  Service   │    │  (Neon)    │            │
│  └────────────┘    └──────┬─────┘    └────────────┘            │
│                           │                                      │
│                    ┌──────┴──────┐                              │
│                    │  Workers    │                              │
│                    │ - Drift     │                              │
│                    │ - Retrain   │                              │
│                    │ - Health    │                              │
│                    └─────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MONITORING & ALERTS                           │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐            │
│  │ Prometheus │───►│  Grafana   │───►│   Alerts   │            │
│  │  Metrics   │    │ Dashboard  │    │  (Email)   │            │
│  └────────────┘    └────────────┘    └────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Setup Instructions

### **Step 1: GitHub Repository Setup**

1. **Initialize Git** (if not already done):
```bash
git init
git remote add origin https://github.com/your-username/your-repo.git
```

2. **Configure GitHub Secrets**

Go to: `Settings → Secrets and variables → Actions → New repository secret`

Add the following secrets:

**Neon Database:**
```
NEON_DATABASE_URL=postgresql://user:password@ep-xxx.region.neon.tech/dbname?sslmode=require
```

**Render Deployment:**
```
RENDER_API_KEY=rnd_xxxxxxxxxxxx
RENDER_BACKEND_SERVICE_ID=srv-xxxxxxxxxxxx
RENDER_FRONTEND_SERVICE_ID=srv-xxxxxxxxxxxx
RENDER_BACKEND_URL=https://your-backend.onrender.com
RENDER_FRONTEND_URL=https://your-frontend.onrender.com
```

**Docker Hub** (optional):
```
DOCKER_USERNAME=your-dockerhub-username
DOCKER_PASSWORD=your-dockerhub-password
```

**Frontend Environment:**
```
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

---

### **Step 2: Neon Database Setup**

1. **Create Neon Project**
   - Go to [neon.tech](https://neon.tech)
   - Create a new project
   - Copy the connection string

2. **Setup Prisma**
```bash
cd ml-backend

# Update DATABASE_URL in .env
echo "DATABASE_URL=your_neon_connection_string" > .env

# Generate Prisma client
prisma generate

# Push schema to database
prisma db push

# Verify connection
prisma studio
```

3. **Seed Database** (optional)
```bash
python scripts/setup_database.py
```

---

### **Step 3: Local Development Setup**

1. **Install Dependencies**

**Backend:**
```bash
cd ml-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
prisma generate
```

**Frontend:**
```bash
cd ..  # Back to root
npm install
```

2. **Run Locally**

**Backend:**
```bash
cd ml-backend
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
npm run dev
```

**Full Stack with Docker:**
```bash
docker-compose -f docker-compose.fullstack.yml up
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001
- MLflow: http://localhost:5000

---

### **Step 4: Deploy to Render**

#### **Option A: Using Render Dashboard**

1. **Create Backend Service**
   - New → Web Service
   - Connect GitHub repo
   - **Root Directory**: `ml-backend`
   - **Environment**: Docker
   - **Dockerfile Path**: `./Dockerfile`
   - **Plan**: Standard ($25/month)
   - Add environment variables (DATABASE_URL, etc.)

2. **Create Frontend Service**
   - New → Web Service
   - Connect GitHub repo
   - **Root Directory**: `.` (root)
   - **Environment**: Docker
   - **Dockerfile Path**: `./Dockerfile.frontend`
   - **Plan**: Starter ($7/month)
   - Add NEXT_PUBLIC_API_URL

3. **Create Background Workers**
   - New → Background Worker
   - Use same repo
   - **Root Directory**: `ml-backend`
   - **Docker Command**: `python -m app.workers.drift_monitor`

#### **Option B: Using render.yaml (Blueprint)**

1. **Push render.yaml** to your repo
2. **In Render Dashboard**: New → Blueprint
3. **Connect** your GitHub repo
4. Render will automatically create all services

---

## 📊 GitHub Actions Workflows

### **Workflow Files**

1. **`.github/workflows/frontend-cicd.yml`**
   - Frontend linting, building, Docker, deployment
   - Triggers: Push to main/develop, PR to main

2. **`.github/workflows/backend-cicd.yml`** (enhanced)
   - Backend linting, testing, Docker, deployment
   - Prisma migrations, model validation
   - Triggers: Push to ml-backend/**, PR to main

3. **`.github/workflows/full-stack-cicd.yml`**
   - Full system integration testing
   - Deploys both services together
   - Triggers: Push to main, manual dispatch

4. **`.github/workflows/drift-monitoring.yml`**
   - Scheduled drift detection
   - Triggers: Every 6 hours, manual

### **Pipeline Stages**

#### **Backend Pipeline (25-30 mins)**
```
1. Lint & Security (3 min)
   ├── Flake8, Black, isort
   ├── Bandit security scan
   └── Safety dependency check

2. Unit Tests (5 min)
   ├── pytest with coverage
   ├── Neon database setup
   └── Upload to Codecov

3. Integration Tests (5 min)
   ├── Start FastAPI server
   ├── Test all endpoints
   └── API health checks

4. Docker Build (8 min)
   ├── Multi-stage build
   ├── Security scan with Trivy
   └── Push to Docker Hub

5. Model Validation (3 min)
   ├── Check performance metrics
   └── Verify thresholds

6. Deploy to Render (5 min)
   ├── Trigger deployment
   ├── Wait for health check
   └── Smoke tests

7. Post-Deploy Monitor (2 min)
   └── Verify metrics endpoint
```

#### **Frontend Pipeline (15-20 mins)**
```
1. Lint & Type Check (2 min)
   ├── ESLint
   └── TypeScript check

2. Build (5 min)
   └── Next.js production build

3. Docker Build (8 min)
   ├── Multi-stage build
   └── Container test

4. Deploy to Render (5 min)
   ├── Trigger deployment
   └── Smoke tests
```

---

## 🐳 Docker Configuration

### **Backend Dockerfile**
- **Location**: `ml-backend/Dockerfile`
- **Multi-stage build**: Builder + Runner
- **Base**: `python:3.11-slim`
- **Final Size**: ~800MB (with ML libraries)
- **Health Check**: `/health` endpoint

### **Frontend Dockerfile**
- **Location**: `Dockerfile.frontend`
- **Multi-stage build**: deps → builder → runner
- **Base**: `node:20-alpine`
- **Final Size**: ~150-200MB
- **Standalone mode**: Optimized Next.js output

### **Docker Compose**
- **Development**: `ml-backend/docker-compose.yml` (backend only)
- **Full Stack**: `docker-compose.fullstack.yml` (frontend + backend + monitoring)

**Start Full Stack:**
```bash
docker-compose -f docker-compose.fullstack.yml up -d
```

---

## 📈 Monitoring & Drift Detection

### **Prometheus Metrics**

**Collected Metrics:**
- Request count & latency
- Prediction count by model type
- Model accuracy/performance
- Drift scores
- Error rates
- System resources (CPU, memory)

**Metrics Endpoint**: `http://backend:8000/metrics`

### **Drift Detection**

**Data Drift:**
- **Method**: Kolmogorov-Smirnov test (numerical), Chi-square (categorical)
- **Frequency**: Every 1 hour (configurable)
- **Alert Threshold**: Drift score > 0.7

**Model Drift:**
- **Method**: Performance degradation monitoring
- **Frequency**: Continuous (with predictions)
- **Alert Threshold**: Accuracy drop > 5%

**Automated Actions:**
1. **Warning Level** (drift 0.5-0.7): Log alert, notify team
2. **Critical Level** (drift > 0.7): Trigger retraining workflow

### **Drift Monitoring Worker**
```python
# Runs as background worker on Render
# File: ml-backend/app/workers/drift_monitor.py
```

**Schedule:**
- GitHub Actions: Every 6 hours
- Render Worker: Continuous monitoring

---

## 💾 Database Setup (Neon + Prisma)

### **Prisma Schema**
- **Location**: `ml-backend/prisma/schema.prisma`
- **Models**: Model, Prediction, ModelMetric, DriftReport, Experiment, etc.

### **Database Operations**

**Generate Client:**
```bash
prisma generate
```

**Push Schema:**
```bash
prisma db push
```

**Migrate (Production):**
```bash
prisma migrate deploy
```

**Browse Data:**
```bash
prisma studio
```

### **Neon Features Used**
- ✅ Serverless PostgreSQL
- ✅ Automatic scaling
- ✅ Branching for dev/staging
- ✅ Connection pooling
- ✅ SSL connections

---

## 🎯 Deployment Strategy

### **Blue-Green Deployment**

1. **Build new version** (Green)
2. **Deploy to staging slot**
3. **Run health checks**
4. **Switch traffic** (Blue → Green)
5. **Monitor for 10 minutes**
6. **Keep Blue as fallback** (24 hours)

### **Rollback Process**

**Automatic Rollback** (if):
- Health check fails > 3 times
- Error rate > 10%
- Critical alerts fired

**Manual Rollback:**
```bash
# Via Render Dashboard
Services → Select service → Rollback button

# Via Render API
curl -X POST \
  "https://api.render.com/v1/services/SERVICE_ID/deploys/DEPLOY_ID/rollback" \
  -H "Authorization: Bearer $RENDER_API_KEY"
```

---

## 🔧 Troubleshooting

### **Common Issues**

#### **1. GitHub Actions Failing**

**Neon Database Connection Error:**
```
Error: Connection refused
```
**Solution**: Check `NEON_DATABASE_URL` secret is set correctly with `?sslmode=require`

**Docker Build Timeout:**
```
Error: Build exceeded time limit
```
**Solution**: Use Docker layer caching, reduce dependencies

#### **2. Render Deployment Issues**

**Health Check Failing:**
```
Service failed health check
```
**Solution**: 
- Check logs: `Render Dashboard → Service → Logs`
- Verify DATABASE_URL is set
- Increase health check timeout

**Out of Memory:**
```
Container killed (OOM)
```
**Solution**: Upgrade to higher plan (2GB+ RAM)

#### **3. Drift Detection Not Working**

**No Drift Reports:**
```
Drift detection worker not running
```
**Solution**:
- Check worker logs on Render
- Verify DATABASE_URL is set in worker
- Check drift detection is enabled: `DRIFT_DETECTION_ENABLED=true`

---

## 📞 Support & Next Steps

### **Verify Setup**

Run this checklist:
- [ ] GitHub secrets configured
- [ ] Neon database created and connected
- [ ] Local development working
- [ ] Docker builds successfully
- [ ] Render services created
- [ ] CI/CD pipeline passes
- [ ] Monitoring dashboards accessible

### **Access Points**

After deployment:
- **Frontend**: Your Render frontend URL
- **Backend API**: Your Render backend URL + `/docs`
- **Monitoring**: Set up Grafana Cloud or self-hosted
- **Database**: Neon dashboard

### **Next Enhancements**

- [ ] Set up Slack/email notifications for alerts
- [ ] Add end-to-end tests (Playwright)
- [ ] Implement A/B testing for models
- [ ] Add feature flags
- [ ] Set up log aggregation (e.g., Logtail)
- [ ] Add performance monitoring (e.g., Sentry)

---

## 🎉 Success Criteria

Your CI/CD is successful when:
- ✅ Code pushed → Automated tests run
- ✅ Tests pass → Docker images built
- ✅ Images built → Deployed to Render
- ✅ Deployed → Health checks pass
- ✅ Drift detected → Alerts sent
- ✅ Performance degrades → Auto-retraining triggered

**You now have a production-ready ML system with full CI/CD! 🚀**

---

**Last Updated**: December 2025  
**Version**: 1.0  
**Status**: ✅ Production Ready
