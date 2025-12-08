# 🔄 CI/CD Pipeline & MLOps Plan

## Executive Summary

Comprehensive CI/CD pipeline for Credit Scoring ML API with automated testing, deployment, monitoring, and drift detection.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        DEVELOPMENT                               │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                  │
│  │  Commit  │ -> │   Push   │ -> │ GitHub   │                  │
│  │  Code    │    │ to Repo  │    │ Actions  │                  │
│  └──────────┘    └──────────┘    └────┬─────┘                  │
└──────────────────────────────────────────┼─────────────────────┘
                                          │
┌─────────────────────────────────────────┼─────────────────────┐
│                    CI PIPELINE          ▼                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐              │
│  │   Code     │  │   Unit     │  │  Security  │              │
│  │  Quality   │->│   Tests    │->│   Scan     │              │
│  └────────────┘  └────────────┘  └──────┬─────┘              │
│                                          │                     │
│  ┌────────────┐  ┌────────────┐  ┌──────▼─────┐              │
│  │Integration │<-│   Docker   │<-│   Build    │              │
│  │   Tests    │  │   Image    │  │   Image    │              │
│  └──────┬─────┘  └────────────┘  └────────────┘              │
└─────────┼────────────────────────────────────────────────────┘
          │
┌─────────┼────────────────────────────────────────────────────┐
│         ▼           CD PIPELINE                               │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐              │
│  │   Model    │  │   Deploy   │  │   Smoke    │              │
│  │Validation  │->│ to Render  │->│   Tests    │              │
│  └────────────┘  └────────────┘  └──────┬─────┘              │
└──────────────────────────────────────────┼─────────────────────┘
                                           │
┌──────────────────────────────────────────┼─────────────────────┐
│                   PRODUCTION             ▼                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐              │
│  │ Real-time  │  │   Drift    │  │   Alert    │              │
│  │Monitoring  │->│ Detection  │->│  System    │              │
│  └────────────┘  └────────────┘  └────────────┘              │
│                                                                │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐              │
│  │   Model    │  │Retraining  │  │   Deploy   │              │
│  │Performance │->│ Trigger    │->│ New Model  │              │
│  └────────────┘  └────────────┘  └────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Pipeline Stages

### Stage 1: Code Quality & Linting

**Objective**: Ensure code meets quality standards

**Tools**:
- Black (formatter)
- isort (import sorting)
- Flake8 (linting)
- Pylint (static analysis)
- mypy (type checking)

**Process**:
```bash
1. Run Black formatter check
2. Check import organization with isort
3. Lint code with Flake8
4. Run Pylint for code smells
5. Type check with mypy
```

**Success Criteria**:
- No critical linting errors
- Code style compliance > 95%
- Type coverage > 80%

**Duration**: ~2-3 minutes

---

### Stage 2: Unit Testing & Coverage

**Objective**: Verify individual components work correctly

**Tools**:
- pytest (testing framework)
- pytest-cov (coverage reporting)
- codecov (coverage tracking)

**Tests Included**:
```python
- Model training tests
- Prediction accuracy tests
- Data preprocessing tests
- API endpoint tests
- Utility function tests
```

**Process**:
```bash
1. Set up test environment
2. Run pytest with coverage
3. Generate coverage report
4. Upload to Codecov
5. Check coverage threshold
```

**Success Criteria**:
- All tests pass
- Code coverage > 80%
- No critical test failures

**Duration**: ~3-5 minutes

---

### Stage 3: Security Scanning

**Objective**: Identify security vulnerabilities

**Tools**:
- Bandit (security linter)
- Safety (dependency checker)
- Trivy (container scanner)

**Scans**:
```yaml
1. Code Security:
   - SQL injection risks
   - Hardcoded credentials
   - Unsafe function usage

2. Dependency Security:
   - Known CVEs
   - Outdated packages
   - License compliance

3. Container Security:
   - Base image vulnerabilities
   - Exposed ports
   - Privilege escalation risks
```

**Success Criteria**:
- No critical security issues
- All high-severity CVEs addressed
- Container passes security scan

**Duration**: ~2-3 minutes

---

### Stage 4: Docker Build

**Objective**: Create production-ready container image

**Process**:
```dockerfile
1. Multi-stage build:
   - Builder stage: Install dependencies
   - Production stage: Copy artifacts

2. Optimization:
   - Layer caching
   - Minimal base image (python:3.11-slim)
   - Remove build artifacts

3. Tagging:
   - Branch name
   - Git SHA
   - Latest (for main branch)
```

**Image Optimization**:
```bash
- Base image size: ~150MB
- Final image size: ~800MB (with ML libs)
- Build time: ~5-8 minutes (with cache)
```

**Success Criteria**:
- Image builds successfully
- No vulnerabilities in scan
- Image size < 1GB

**Duration**: ~5-8 minutes

---

### Stage 5: Integration Testing

**Objective**: Test API endpoints and service interactions

**Setup**:
```bash
1. Start services with Docker Compose
2. Wait for health checks
3. Run integration test suite
4. Tear down services
```

**Tests**:
```python
- Health endpoint
- Prediction endpoint
- Training endpoint
- Fairness analysis endpoint
- Drift detection endpoint
- Model explainability
```

**Success Criteria**:
- All endpoints respond correctly
- Response times < 2 seconds
- No integration failures

**Duration**: ~3-5 minutes

---

### Stage 6: Model Validation

**Objective**: Verify model performance meets thresholds

**Validation Checks**:
```yaml
Performance Metrics:
  - Accuracy: > 85%
  - AUC-ROC: > 0.85
  - Precision: > 0.80
  - Recall: > 0.80
  - F1-Score: > 0.82

Fairness Metrics:
  - Demographic Parity: > 0.85
  - Equal Opportunity: > 0.85
  - Disparate Impact: > 0.80
  - Fairness Score: > 85/100

Drift Checks:
  - Data Drift Score: < 0.7
  - Performance Degradation: < 5%
  - Feature Drift: < 30% features
```

**Process**:
```bash
1. Load test dataset
2. Run model predictions
3. Calculate metrics
4. Compare with baselines
5. Generate report
```

**Success Criteria**:
- All metrics above thresholds
- No significant drift detected
- Model ready for deployment

**Duration**: ~2-4 minutes

---

### Stage 7: Deployment to Render

**Objective**: Deploy to production environment

**Deployment Strategy**: Blue-Green Deployment

```yaml
Steps:
  1. Build new version (Green)
  2. Deploy to staging slot
  3. Run health checks
  4. Switch traffic (Blue -> Green)
  5. Monitor for issues
  6. Keep Blue as fallback

Rollback Plan:
  - Automatic rollback on health check failure
  - Manual rollback via Render dashboard
  - Keep previous version for 24 hours
```

**Environment Configuration**:
```bash
# Production settings
ENVIRONMENT=production
WORKERS=2
LOG_LEVEL=info
ENABLE_MONITORING=true
DRIFT_DETECTION_ENABLED=true
```

**Success Criteria**:
- Deployment completes successfully
- Health checks pass
- No errors in logs
- Metrics collecting properly

**Duration**: ~3-5 minutes

---

### Stage 8: Post-Deployment Validation

**Objective**: Verify production deployment

**Smoke Tests**:
```bash
1. Health check endpoint
2. Root endpoint
3. Sample prediction
4. Metrics endpoint
5. API documentation
```

**Monitoring Setup**:
```bash
1. Verify Prometheus scraping
2. Check Grafana dashboards
3. Test alerting rules
4. Validate log aggregation
```

**Success Criteria**:
- All smoke tests pass
- Monitoring active
- No critical errors
- Response times normal

**Duration**: ~2-3 minutes

---

## Continuous Monitoring

### Data Drift Detection

**Method**: Statistical Distribution Testing

```python
Detection Techniques:
  1. Numerical Features:
     - Kolmogorov-Smirnov Test
     - Threshold: p-value < 0.05
  
  2. Categorical Features:
     - Chi-Square Test
     - Threshold: p-value < 0.05
  
  3. Prediction Drift:
     - Approval rate change
     - Distribution shift analysis
```

**Schedule**:
```yaml
Real-time: Every prediction logged
Batch Analysis: Every 1 hour
Comprehensive Report: Daily at 2 AM UTC
```

**Alert Thresholds**:
```yaml
Warning:
  - Drift Score: 0.5 - 0.7
  - Drifted Features: 20-30%
  - Performance Drop: 3-5%

Critical:
  - Drift Score: > 0.7
  - Drifted Features: > 30%
  - Performance Drop: > 5%
```

---

### Model Drift Detection

**Performance Tracking**:

```python
Metrics Monitored:
  - Accuracy over time
  - Precision/Recall trends
  - AUC-ROC stability
  - Fairness metrics consistency
  - Prediction distribution changes
```

**Detection Methods**:

1. **Performance Degradation**
   ```python
   # Track sliding window metrics
   window_size = 1000 predictions
   comparison_period = 7 days
   alert_threshold = -5% accuracy
   ```

2. **Concept Drift**
   ```python
   # Monitor feature-target relationships
   method = "Statistical tests on residuals"
   frequency = "Daily"
   ```

3. **Covariate Drift**
   ```python
   # Track input distribution changes
   method = "KS test on features"
   frequency = "Hourly"
   ```

**Automated Actions**:
```yaml
Drift Level: Warning
  Action: Log alert, notify team
  
Drift Level: Critical
  Action:
    - Trigger retraining workflow
    - Send urgent notification
    - Create incident ticket
    - Enable fallback model
```

---

### Monitoring Dashboard

**Key Metrics Displayed**:

```yaml
Model Performance:
  - Real-time accuracy
  - Prediction distribution
  - Latency percentiles (p50, p95, p99)
  - Error rate

Business Metrics:
  - Approval rate
  - Average loan amount
  - Risk score distribution
  - Fairness scores

System Health:
  - CPU/Memory usage
  - Request rate
  - Error count
  - Uptime

Drift Indicators:
  - Drift score trend
  - Drifted features list
  - Performance degradation
  - Alert status
```

**Dashboard Access**:
- **Grafana**: http://localhost:3001
- **Prometheus**: http://localhost:9090
- **MLflow**: http://localhost:5000

---

## Automated Retraining Pipeline

### Trigger Conditions

```yaml
Automatic Retraining Triggered When:
  1. Performance Degradation:
     - Accuracy drops > 5%
     - F1-score drops > 5%
     
  2. Significant Drift:
     - Drift score > 0.7 for 24 hours
     - > 30% features drifted
     
  3. Scheduled:
     - Weekly: Sunday 2 AM UTC
     - After major data updates
     
  4. Manual:
     - Via API endpoint
     - Through MLflow UI
```

### Retraining Workflow

```yaml
Step 1: Data Collection
  - Gather recent production data
  - Validate data quality
  - Check for class balance
  
Step 2: Data Preparation
  - Clean and preprocess
  - Feature engineering
  - Train/validation split
  
Step 3: Model Training
  - Hyperparameter tuning
  - Cross-validation
  - Multiple model comparison
  
Step 4: Evaluation
  - Performance metrics
  - Fairness analysis
  - Explainability check
  
Step 5: Approval Gate
  - Compare with current model
  - Require metrics improvement
  - Manual approval for production
  
Step 6: Deployment
  - Deploy to staging
  - Run integration tests
  - Canary deployment to production
  - Full rollout if successful
```

### Retraining Code

```python
# Automated retraining scheduler
# File: app/workers/retraining_scheduler.py

import schedule
import time
from app.models.retrain import retrain_model
from app.monitoring.drift_detector import DriftDetector

def check_and_retrain():
    """Check if retraining is needed"""
    drift_detector = DriftDetector()
    
    # Check drift status
    drift_report = drift_detector.get_latest_report()
    
    if drift_report['requires_retraining']:
        print("🔄 Triggering model retraining...")
        retrain_model(
            reason=drift_report['reason'],
            priority='high' if drift_report['critical'] else 'normal'
        )
    else:
        print("✅ Model performance stable")

# Schedule checks
schedule.every(1).hours.do(check_and_retrain)
schedule.every().sunday.at("02:00").do(lambda: retrain_model(reason='scheduled'))

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## Environment-Specific Configurations

### Development

```yaml
Environment: development
Deployment: Docker Compose locally
Testing: Unit + Integration tests
Monitoring: Basic logging
CI Trigger: Every commit
Duration: ~15 minutes full pipeline
```

### Staging

```yaml
Environment: staging
Deployment: Render (separate service)
Testing: Full test suite + smoke tests
Monitoring: Prometheus + Grafana
CI Trigger: Merge to develop branch
Duration: ~20 minutes full pipeline
```

### Production

```yaml
Environment: production
Deployment: Render (production service)
Testing: Smoke tests + canary testing
Monitoring: Full monitoring + alerting
CI Trigger: Merge to main branch
Duration: ~25 minutes full pipeline
Approval: Manual approval required
```

---

## Rollback Strategy

### Automatic Rollback

```yaml
Triggered When:
  - Health check fails > 3 times
  - Error rate > 10%
  - Latency > 5 seconds
  - Critical alerts fired

Process:
  1. Detect issue
  2. Switch to previous version
  3. Send alert notification
  4. Create incident report
  5. Log rollback event
```

### Manual Rollback

```bash
# Via Render Dashboard
1. Go to your service
2. Click "Rollback" button
3. Select previous deployment
4. Confirm rollback

# Via Render API
curl -X POST \
  "https://api.render.com/v1/services/${SERVICE_ID}/deploys/${DEPLOY_ID}/rollback" \
  -H "Authorization: Bearer ${RENDER_API_KEY}"
```

---

## Performance Benchmarks

### Pipeline Performance

```yaml
Stage                Duration    Success Rate
─────────────────────────────────────────────
Code Quality         2-3 min     99%
Unit Tests           3-5 min     98%
Security Scan        2-3 min     99%
Docker Build         5-8 min     97%
Integration Tests    3-5 min     96%
Model Validation     2-4 min     98%
Deploy to Render     3-5 min     99%
Post-Deployment      2-3 min     99%
─────────────────────────────────────────────
Total Pipeline       22-36 min   95%
```

### Deployment Frequency

```yaml
Development: Multiple times per day
Staging: 2-3 times per day
Production: 1-2 times per week
Hotfixes: Within 1 hour
```

---

## Security & Compliance

### Secrets Management

```yaml
GitHub Secrets:
  - RENDER_API_KEY
  - RENDER_SERVICE_ID
  - RENDER_SERVICE_URL
  - SENTRY_DSN (optional)

Environment Variables:
  - API_KEY (auto-generated by Render)
  - Database credentials (if needed)
  - Third-party API keys
```

### Compliance Checks

```yaml
Pre-Deployment:
  ✓ Security scan passed
  ✓ No high-severity vulnerabilities
  ✓ License compliance verified
  ✓ Data privacy checks

Post-Deployment:
  ✓ Audit logs enabled
  ✓ Encryption in transit (HTTPS)
  ✓ Access controls configured
  ✓ Monitoring active
```

---

## Disaster Recovery

### Backup Strategy

```yaml
Code:
  - Git repository (GitHub)
  - Multiple branches maintained
  - Release tags for versions

Models:
  - MLflow artifact storage
  - Persistent disk on Render
  - S3 backup (optional)

Data:
  - Database backups (daily)
  - Logs retained for 30 days
  - Metrics stored in Prometheus
```

### Recovery Time Objectives

```yaml
Code Rollback: < 5 minutes
Service Restart: < 2 minutes
Full Redeployment: < 15 minutes
Data Recovery: < 30 minutes
```

---

## Cost Optimization

### Resource Allocation

```yaml
Development:
  - Single instance
  - 512MB RAM
  - 0.5 CPU
  - Cost: $7/month

Production:
  - 1-3 instances (auto-scaling)
  - 2GB RAM per instance
  - 1 CPU per instance
  - Cost: $25-75/month
```

### Optimization Strategies

```python
1. Model Compression
   - Quantization
   - Pruning
   - Distillation

2. Caching
   - Model predictions
   - Feature preprocessing
   - API responses

3. Batching
   - Batch predictions when possible
   - Reduce API calls
   - Optimize database queries
```

---

## Success Metrics

### Pipeline Health

```yaml
Target Metrics:
  - Success Rate: > 95%
  - Average Duration: < 30 minutes
  - Time to Production: < 1 hour
  - Deployment Frequency: 2-3x per week
  - Mean Time to Recovery: < 15 minutes
```

### Model Quality

```yaml
Target Metrics:
  - Model Accuracy: > 85%
  - Fairness Score: > 85/100
  - Drift Detection Rate: > 90%
  - False Alert Rate: < 10%
  - Retraining Success Rate: > 95%
```

---

## Next Steps & Improvements

### Phase 1 (Current)
- ✅ Basic CI/CD pipeline
- ✅ Docker containerization
- ✅ Render deployment
- ✅ Drift detection

### Phase 2 (3 months)
- [ ] A/B testing framework
- [ ] Advanced monitoring with Datadog
- [ ] Automated feature engineering
- [ ] Multi-region deployment

### Phase 3 (6 months)
- [ ] ML model registry
- [ ] Automated retraining pipeline
- [ ] Feature store integration
- [ ] Advanced explainability

### Phase 4 (12 months)
- [ ] Real-time predictions at scale
- [ ] Advanced anomaly detection
- [ ] Federated learning support
- [ ] AutoML integration

---

**Document Version**: 1.0
**Last Updated**: December 2025
**Status**: ✅ Production Ready

For questions or suggestions, please create a GitHub issue.
