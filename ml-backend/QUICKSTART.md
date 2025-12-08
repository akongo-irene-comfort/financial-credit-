# 🚀 Quick Start Guide - Credit Scoring ML API

Get your ML API up and running in 5 minutes!

---

## Prerequisites

- **Docker** & **Docker Compose** installed
- **Python 3.11+** (for local development)
- **Git** (for cloning repository)

---

## Option 1: Docker (Recommended)

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd ml-backend
```

### 2. Start Services

```bash
docker-compose up -d
```

This starts:
- ✅ ML API (port 8000)
- ✅ MLflow UI (port 5000)

### 3. Verify Deployment

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

### 4. Make Your First Prediction

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "credit_score": 720,
      "annual_income": 75000,
      "loan_amount": 25000,
      "employment_length": 5,
      "debt_to_income": 0.3,
      "number_of_credit_lines": 8,
      "age": 35,
      "loan_purpose": "debt_consolidation",
      "home_ownership": "MORTGAGE"
    },
    "model_type": "random_forest",
    "explain": true
  }'
```

---

## Option 2: Local Development

### 1. Install Dependencies

```bash
cd ml-backend
pip install -r requirements.txt
```

### 2. Start Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Access API

```bash
# API docs
open http://localhost:8000/docs

# Health check
curl http://localhost:8000/health
```

---

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info |
| `/health` | GET | Health check |
| `/docs` | GET | API documentation |
| `/api/predict` | POST | Make prediction |
| `/api/train` | POST | Train model |
| `/api/evaluate` | POST | Evaluate model |
| `/api/fairness/analyze` | POST | Fairness analysis |
| `/api/explain` | POST | Explain prediction |
| `/api/monitoring/drift` | POST | Detect drift |
| `/metrics` | GET | Prometheus metrics |

---

## Next Steps

### 1. Train Your Model

```bash
curl -X POST http://localhost:8000/api/train \
  -H "Content-Type: application/json" \
  -d '{
    "data": [...],
    "model_type": "random_forest",
    "experiment_name": "credit_scoring"
  }'
```

### 2. Monitor Performance

```bash
# Access MLflow UI
open http://localhost:5000

# Check metrics
curl http://localhost:8000/metrics
```

### 3. Deploy to Production

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

---

## Common Commands

```bash
# Stop services
docker-compose down

# View logs
docker-compose logs -f ml-backend

# Rebuild container
docker-compose build

# Run tests
pytest tests/

# Check code quality
flake8 app/
black app/
```

---

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Container Won't Start

```bash
# Check logs
docker logs credit-scoring-ml-backend

# Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Model Not Found

```bash
# Train a model first
curl -X POST http://localhost:8000/api/train -H "Content-Type: application/json" -d '{"data": [...]}'
```

---

## Resources

- 📖 [Full Deployment Guide](DEPLOYMENT.md)
- 🔄 [CI/CD Pipeline](CICD_PLAN.md)
- 🐛 [API Documentation](http://localhost:8000/docs)
- 📊 [MLflow UI](http://localhost:5000)

---

## Support

For issues or questions:
1. Check [DEPLOYMENT.md](DEPLOYMENT.md)
2. Review logs: `docker-compose logs`
3. Create GitHub issue

---

**Ready to deploy?** Check out [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment to Render! 🚀
