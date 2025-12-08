# 🚀 Credit Scoring ML Backend - Complete Setup

**Production-ready ML API with FastAPI, Neon PostgreSQL, Prisma, Docker, and CI/CD**

[![CI/CD](https://github.com/your-username/your-repo/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/your-username/your-repo/actions)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-enabled-blue.svg)](https://www.docker.com/)
[![Render](https://img.shields.io/badge/deploy-render-46e3b7.svg)](https://render.com/)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Detailed Setup Guides](#detailed-setup-guides)
- [API Documentation](#api-documentation)
- [Monitoring & Drift Detection](#monitoring--drift-detection)
- [Deployment](#deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This ML backend provides a complete production-ready API for credit scoring with:

- **Machine Learning Models**: Random Forest, XGBoost, Deep Neural Networks
- **Experiment Tracking**: MLflow integration
- **Model Explainability**: SHAP and LIME explanations
- **Fairness Analysis**: Demographic parity, disparate impact, equal opportunity
- **Drift Detection**: Automated data and model drift monitoring
- **Database**: Neon PostgreSQL with Prisma ORM
- **Containerization**: Docker and Docker Compose
- **CI/CD**: GitHub Actions pipeline
- **Deployment**: Render with auto-scaling
- **Monitoring**: Prometheus metrics, system health tracking

---

## ✨ Features

### 🤖 Machine Learning

- **Classical ML**: Logistic Regression, Random Forest, XGBoost
- **Deep Learning**: Simple DNNs with TensorFlow/PyTorch
- **Hyperparameter Tuning**: Automated grid search and random search
- **Cross-Validation**: K-fold cross-validation for robust evaluation
- **Feature Engineering**: Automated feature importance and selection

### 📊 Model Evaluation

- **Performance Metrics**: Accuracy, Precision, Recall, F1, AUC-ROC
- **Fairness Metrics**: Demographic parity, equal opportunity, disparate impact
- **Business Metrics**: Approval rates, loan amounts, risk scores
- **Error Analysis**: Confusion matrix, classification reports

### 🔍 Model Explainability

- **SHAP Values**: Feature importance and contribution analysis
- **LIME**: Local interpretable model-agnostic explanations
- **Feature Importance**: Global and local feature rankings

### ⚖️ Fairness & Bias Detection

- **Demographic Parity**: Equal approval rates across groups
- **Equal Opportunity**: Equal TPR for qualified applicants
- **Disparate Impact**: 80% rule compliance checking
- **Bias Mitigation**: Recommendations for bias reduction

### 📈 Drift Detection

- **Data Drift**: Distribution changes in features (KS test, Chi-square)
- **Concept Drift**: Changes in feature-target relationships
- **Prediction Drift**: Changes in model output distribution
- **Performance Drift**: Model accuracy degradation over time
- **Automated Alerts**: Real-time drift notifications

### 💾 Database & Storage

- **Neon PostgreSQL**: Serverless PostgreSQL with auto-scaling
- **Prisma ORM**: Type-safe database access with migrations
- **Model Registry**: Track all trained models with metadata
- **Prediction Logging**: Store all predictions for analysis
- **Time-Series Metrics**: Historical performance tracking
- **Drift Reports**: Persistent drift detection history

### 🐳 DevOps & Deployment

- **Docker**: Multi-stage builds for optimized images
- **Docker Compose**: Local development environment
- **GitHub Actions**: Automated CI/CD pipeline
- **Render Deployment**: One-click production deployment
- **Auto-Scaling**: Horizontal scaling based on load
- **Health Checks**: Automated service monitoring

### 📊 Monitoring

- **Prometheus Metrics**: Custom ML metrics exposed at `/metrics`
- **System Health**: CPU, memory, disk usage tracking
- **API Monitoring**: Request rates, latency, error rates
- **Drift Monitoring**: Continuous drift detection worker
- **Alert System**: Database-backed alerts with notifications

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT APPLICATIONS                      │
│              (Next.js Dashboard, Mobile Apps)                │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
┌────────────────────────▼────────────────────────────────────┐
│                    RENDER (Production)                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              FastAPI Application                      │   │
│  │  ┌────────────┬────────────┬─────────────────────┐  │   │
│  │  │  Predict   │   Train    │    Fairness/Drift   │  │   │
│  │  │   API      │    API     │        API          │  │   │
│  │  └────────────┴────────────┴─────────────────────┘  │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │              Prisma ORM Layer                        │   │
│  └──────────────────────┬───────────────────────────────┘   │
└─────────────────────────┼──────────────────────────────────┘
                          │
┌─────────────────────────▼──────────────────────────────────┐
│               Neon PostgreSQL (Database)                    │
│  ┌──────────┬──────────┬──────────┬───────────────────┐   │
│  │  Models  │Predictions│ Metrics  │  Drift Reports    │   │
│  └──────────┴──────────┴──────────┴───────────────────┘   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Background Workers (Monitoring)                 │
│  ┌──────────────────┬────────────────────────────────────┐  │
│  │  Drift Monitor   │   System Health Monitor            │  │
│  │  (Hourly)        │   (Every minute)                   │  │
│  └──────────────────┴────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   CI/CD Pipeline (GitHub)                    │
│  ┌────────┬────────┬──────────┬──────────┬──────────────┐  │
│  │  Lint  │  Test  │  Build   │ Security │   Deploy     │  │
│  └────────┴────────┴──────────┴──────────┴──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

```bash
✅ Python 3.11+
✅ Docker & Docker Compose
✅ Git
✅ Neon account (https://neon.tech)
✅ Render account (https://render.com)
```

### 1. Clone Repository

```bash
git clone https://github.com/your-username/credit-scoring-ml.git
cd credit-scoring-ml/ml-backend
```

### 2. Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Neon DATABASE_URL
nano .env
```

### 3. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt

# Generate Prisma client
prisma generate
```

### 4. Set Up Database

```bash
# Push schema to Neon database
prisma db push

# Run setup script
python scripts/setup_database.py

# Seed sample data (optional)
python scripts/setup_database.py --seed
```

### 5. Start Development Server

```bash
# Run locally
uvicorn app.main:app --reload --port 8000

# Or use Docker Compose
docker compose
 up
```

### 6. Test API

```bash
# Health check
curl http://localhost:8000/health

# Test prediction
curl -X POST http://localhost:8000/api/predict \
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
    "explain": true
  }'
```

### 7. View Metrics

```bash
# Prometheus metrics
curl http://localhost:8000/metrics

# Prisma Studio (database GUI)
prisma studio
```

**🎉 Your ML backend is running!**

---

## 📚 Detailed Setup Guides

### Database Setup
📖 **[NEON_PRISMA_SETUP.md](./NEON_PRISMA_SETUP.md)** - Complete guide for Neon PostgreSQL + Prisma

**Topics covered:**
- Creating Neon database
- Configuring connection string
- Setting up Prisma schema
- Running migrations
- Seeding data
- Querying database
- Troubleshooting

### Deployment
📖 **[RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md)** - Deploy to Render with auto-scaling

**Topics covered:**
- Creating Render service
- Configuring environment variables
- Setting up persistent disks
- Enabling auto-deploy
- Monitoring and logs
- Scaling strategies
- Rollback procedures

### CI/CD Pipeline
📖 **[GITHUB_ACTIONS_SETUP.md](./GITHUB_ACTIONS_SETUP.md)** - Automated testing and deployment

**Topics covered:**
- Adding GitHub secrets
- Understanding pipeline jobs
- Triggering deployments
- Monitoring pipeline
- Troubleshooting failures
- Security best practices

### Docker
📖 **[Dockerfile](./Dockerfile)** - Multi-stage Docker build

**Topics covered:**
- Building Docker image
- Running containers
- Docker Compose setup
- Optimization techniques

---

## 📖 API Documentation

### Base URL

```
Development: http://localhost:8000
Production:  https://your-service.onrender.com
```

### Endpoints

#### Health Check
```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "mlflow": true,
  "models": {
    "random_forest": true,
    "deep_learning": false
  }
}
```

#### Train Model
```http
POST /api/train
```

Request:
```json
{
  "data": [...],
  "model_type": "random_forest",
  "hyperparameters": {
    "n_estimators": 100,
    "max_depth": 10
  },
  "experiment_name": "credit_scoring"
}
```

Response:
```json
{
  "success": true,
  "model_type": "random_forest",
  "model_id": "model_abc123",
  "metrics": {
    "accuracy": 0.87,
    "auc_roc": 0.89,
    "f1_score": 0.84
  },
  "feature_importance": {...}
}
```

#### Make Prediction
```http
POST /api/predict
```

Request:
```json
{
  "features": {
    "credit_score": 750,
    "income": 75000,
    "loan_amount": 25000,
    "employment_years": 5,
    "debt_to_income": 0.3
  },
  "model_type": "random_forest",
  "explain": true
}
```

Response:
```json
{
  "prediction": 1,
  "probability": 0.84,
  "confidence": 0.92,
  "risk_score": 0.16,
  "explanation": {
    "feature_importance": {
      "credit_score": 0.28,
      "income": 0.19,
      "loan_amount": 0.15
    }
  }
}
```

#### Fairness Analysis
```http
POST /api/fairness/analyze
```

Request:
```json
{
  "data": [...],
  "predictions": [1, 0, 1, ...],
  "sensitive_features": ["gender", "age_group"]
}
```

Response:
```json
{
  "fairness_score": 88.9,
  "demographic_parity": 0.89,
  "equal_opportunity": 0.91,
  "disparate_impact": 0.86,
  "recommendations": [...]
}
```

#### Drift Detection
```http
POST /api/monitoring/drift
```

Request:
```json
{
  "reference_data": [...],
  "current_data": [...]
}
```

Response:
```json
{
  "drift_detected": true,
  "drift_score": 0.65,
  "drifted_features": ["income", "credit_score"],
  "model_performance_change": {
    "accuracy_change": -0.03
  },
  "recommendations": [...]
}
```

#### Prometheus Metrics
```http
GET /metrics
```

Returns Prometheus-formatted metrics for monitoring.

---

## 📊 Monitoring & Drift Detection

### Automated Drift Monitoring

The system continuously monitors for drift every hour:

```bash
# Run drift monitor worker
python -m app.workers.drift_monitor
```

**Detects:**
- Data drift (feature distribution changes)
- Concept drift (feature-target relationship changes)
- Prediction drift (output distribution changes)
- Performance drift (accuracy degradation)

### System Health Monitoring

Tracks system resources every minute:

```bash
# Run health monitor worker
python -m app.workers.system_health_monitor
```

**Tracks:**
- CPU and memory usage
- Active models
- Prediction volume
- Error rates
- Average latency

### Alert System

Automatically creates alerts for:
- Critical drift detection (drift score > 0.7)
- Performance degradation (>5% accuracy drop)
- System resource issues (CPU/memory > 90%)
- High error rates (>10% errors)

View alerts:
```python
from app.database import db_manager

alerts = await db_manager.get_unacknowledged_alerts(limit=50)
```

### Metrics Dashboard

Prometheus metrics exposed at `/metrics`:

```
# Model predictions
ml_predictions_total{model_type="random_forest",prediction_class="1"} 1234

# Prediction latency
ml_prediction_latency_seconds_bucket{model_type="random_forest",le="0.1"} 980

# Model accuracy
ml_model_accuracy{model_type="random_forest"} 0.87

# Drift score
ml_drift_score{model_type="random_forest"} 0.45

# API requests
ml_api_requests_total{method="POST",endpoint="/api/predict",status="200"} 5678
```

---

## 🚀 Deployment

### Local Development

```bash
# Docker Compose
docker compose
 up

# Access services
- API: http://localhost:8000
- MLflow UI: http://localhost:5000
- Prisma Studio: http://localhost:5555
```

### Production (Render)

**Quick Deploy:**

1. Click **Deploy to Render** button
2. Connect GitHub repository
3. Add environment variables
4. Deploy!

**Manual Setup:** See [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md)

### Environment Variables

```bash
# Required
DATABASE_URL=postgresql://...neon.tech/mldb?sslmode=require
ENVIRONMENT=production
PORT=8000
WORKERS=2

# Optional
MLFLOW_TRACKING_URI=/app/mlruns
PROMETHEUS_ENABLED=true
DRIFT_DETECTION_ENABLED=true
DRIFT_CHECK_INTERVAL=3600
SENTRY_DSN=your_sentry_dsn
```

---

## 🔄 CI/CD Pipeline

### Automated Pipeline

Every push to `main` triggers:

1. ✅ Code quality checks (Black, Flake8, isort)
2. ✅ Unit tests with coverage
3. ✅ Integration tests
4. ✅ Security scanning (Trivy)
5. ✅ Docker build and test
6. ✅ Deploy to Render
7. ✅ Post-deployment health checks

### Branch Strategy

```
main (production)
  ↑
develop (staging)
  ↑
feature/new-feature (development)
```

### Pipeline Status

View at: `https://github.com/your-username/your-repo/actions`

---

## 🐛 Troubleshooting

### Database Connection Failed

**Error:** `Cannot connect to database`

**Solution:**
```bash
# Check DATABASE_URL
echo $DATABASE_URL

# Test connection
python -c "import asyncio; from app.database import connect_database; asyncio.run(connect_database())"

# Verify Neon project is active
```

### Prisma Client Not Found

**Error:** `prisma.errors.PrismaError`

**Solution:**
```bash
prisma generate
```

### Docker Build Fails

**Error:** `Docker build failed`

**Solution:**
```bash
# Check Dockerfile syntax
docker build -t test-build .

# View detailed logs
docker build --progress=plain -t test-build .
```

### Import Error

**Error:** `ModuleNotFoundError`

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.11+
```

### Render Deployment Fails

**Error:** `Health check failed`

**Solution:**
```bash
# Check logs on Render dashboard
# Verify DATABASE_URL is set
# Ensure /health endpoint responds
```

---

## 📦 Project Structure

```
ml-backend/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── database/              # Prisma client & database manager
│   │   ├── __init__.py
│   │   └── prisma_client.py
│   ├── models/                # ML models
│   │   ├── classical_ml.py
│   │   ├── deep_learning.py
│   │   └── experiment_tracker.py
│   ├── evaluation/            # Model evaluation
│   │   ├── metrics.py
│   │   └── fairness.py
│   ├── explainability/        # SHAP & LIME
│   │   ├── shap_explainer.py
│   │   └── lime_explainer.py
│   ├── monitoring/            # Drift detection
│   │   └── drift_detector.py
│   ├── workers/               # Background workers
│   │   ├── drift_monitor.py
│   │   └── system_health_monitor.py
│   └── metrics.py             # Prometheus metrics
├── prisma/
│   └── schema.prisma          # Database schema
├── scripts/
│   └── setup_database.py      # Database setup
├── tests/
│   ├── unit/
│   └── integration/
├── .github/
│   └── workflows/
│       └── ci-cd.yml          # CI/CD pipeline
├── Dockerfile                  # Docker configuration
├── docker compose
.yml          # Local development
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── render.yaml                # Render configuration
├── README.md                  # This file
├── NEON_PRISMA_SETUP.md       # Database setup guide
├── RENDER_DEPLOYMENT.md       # Deployment guide
└── GITHUB_ACTIONS_SETUP.md    # CI/CD guide
```

---

## 🔗 Resources

### Documentation
- **FastAPI**: https://fastapi.tiangolo.com
- **Prisma**: https://www.prisma.io/docs
- **Neon**: https://neon.tech/docs
- **Render**: https://render.com/docs
- **MLflow**: https://mlflow.org/docs
- **Prometheus**: https://prometheus.io/docs

### Tools
- **Prisma Studio**: Database GUI (`prisma studio`)
- **MLflow UI**: Experiment tracking (`mlflow ui`)
- **Docker Desktop**: Container management
- **Postman**: API testing

### Support
- **GitHub Issues**: Report bugs and request features
- **Render Community**: https://community.render.com
- **Neon Discord**: https://discord.gg/neon

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👥 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## ✅ Production Checklist

- [ ] Set up Neon PostgreSQL database
- [ ] Configure environment variables
- [ ] Run database migrations
- [ ] Deploy to Render
- [ ] Set up GitHub Actions secrets
- [ ] Enable auto-deploy
- [ ] Configure monitoring and alerts
- [ ] Test all API endpoints
- [ ] Enable Prometheus metrics
- [ ] Set up drift detection workers
- [ ] Configure backup strategy
- [ ] Document API for team
- [ ] Set up error tracking (Sentry)
- [ ] Enable CORS for frontend
- [ ] Configure rate limiting
- [ ] Set up SSL/HTTPS (automatic on Render)

---

**🎉 Your production-ready ML backend is complete!**

For questions or support, create an issue on GitHub or reach out to the team.

**Built with ❤️ using FastAPI, Neon, Prisma, Docker, and Render**
