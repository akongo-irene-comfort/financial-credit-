# Credit Scoring ML Backend

Production-ready ML backend for credit scoring with experiment tracking, explainability, and monitoring.

## 🎯 Features

### Model Development
- **Classical ML**: Logistic Regression, Random Forest, XGBoost
- **Deep Learning**: TensorFlow/Keras DNN
- **Hyperparameter Tuning**: GridSearchCV with cross-validation
- **Train/Val/Test Split**: 70% / 15% / 15%

### Experiment Tracking
- **MLflow Integration**: Track all experiments, parameters, and metrics
- **Model Registry**: Version control for trained models
- **Comparison**: Compare multiple model runs

### Model Evaluation
- **Metrics**: Accuracy, Precision, Recall, F1, AUC-ROC, RMSE
- **Cross-Validation**: K-fold validation with stratification
- **Error Analysis**: High/low confidence error breakdown
- **Business Metrics**: Approval rates, cost analysis

### Fairness & Bias
- **Demographic Parity**: Equal approval rates across groups
- **Equal Opportunity**: Equal TPR across protected groups
- **Disparate Impact**: 80% rule compliance
- **Statistical Parity**: Deviation measurement

### Explainability
- **SHAP**: Global and local feature importance
- **LIME**: Local model-agnostic explanations
- **Feature Interactions**: Understand feature relationships

### Monitoring & Deployment
- **Data Drift Detection**: Kolmogorov-Smirnov test
- **Model Drift**: Performance degradation tracking
- **Docker Deployment**: Containerized application
- **CI/CD Pipeline**: Automated testing and deployment

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (optional)

### Installation

1. **Clone the repository**
```bash
git clone <repo-url>
cd ml-backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the server**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

5. **Access the API**
- API: http://localhost:8000
- Health check: http://localhost:8000/health
- API docs: http://localhost:8000/docs

### Docker Deployment

1. **Build and run with Docker Compose**
```bash
docker compose
 up -d
```

2. **Access services**
- ML API: http://localhost:8000
- MLflow UI: http://localhost:5000

3. **Stop services**
```bash
docker compose
 down
```

## 📚 API Endpoints

### Training
```bash
POST /api/train
```
Train a model with hyperparameter tuning and experiment tracking.

**Request:**
```json
{
  "data": [...],
  "model_type": "random_forest",
  "hyperparameters": {},
  "experiment_name": "credit_scoring"
}
```

### Prediction
```bash
POST /api/predict
```
Make predictions with explainability.

**Request:**
```json
{
  "features": {
    "age": 35,
    "income": 75000,
    "credit_score": 720,
    "loan_amount": 25000
  },
  "model_type": "random_forest",
  "explain": true
}
```

### Evaluation
```bash
POST /api/evaluate
```
Comprehensive model evaluation with cross-validation.

### Fairness Analysis
```bash
POST /api/fairness/analyze
```
Analyze model fairness across sensitive features.

**Request:**
```json
{
  "data": [...],
  "predictions": [...],
  "sensitive_features": ["gender", "age_group"]
}
```

### Explainability
```bash
POST /api/explain
```
Generate SHAP or LIME explanations.

### Drift Detection
```bash
POST /api/monitoring/drift
```
Detect data and model drift.

## 🏗️ Architecture

```
ml-backend/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── models/                 # ML models
│   │   ├── classical_ml.py     # Logistic Regression, RF, XGBoost
│   │   ├── deep_learning.py    # TensorFlow DNN
│   │   └── experiment_tracker.py # MLflow integration
│   ├── evaluation/             # Model evaluation
│   │   ├── metrics.py          # Comprehensive metrics
│   │   └── fairness.py         # Fairness analysis
│   ├── explainability/         # Model interpretability
│   │   ├── shap_explainer.py   # SHAP explanations
│   │   └── lime_explainer.py   # LIME explanations
│   └── monitoring/             # Production monitoring
│       └── drift_detector.py   # Drift detection
├── Dockerfile                  # Docker configuration
├── docker compose
.yml          # Multi-container setup
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 📊 Model Justifications

### 1. Logistic Regression
- **Purpose**: Baseline linear model
- **Strengths**: Interpretable, fast, low complexity
- **Use Case**: When feature relationships are linear
- **Limitations**: Cannot capture non-linear patterns

### 2. Random Forest
- **Purpose**: Non-linear ensemble model
- **Strengths**: Handles non-linearity, feature importance, robust
- **Use Case**: Complex feature interactions
- **Limitations**: Can overfit, slower than linear models

### 3. XGBoost
- **Purpose**: State-of-the-art gradient boosting
- **Strengths**: High accuracy, handles imbalance, regularization
- **Use Case**: Maximum performance needed
- **Limitations**: Longer training time, more parameters

### 4. Deep Neural Network (DNN)
- **Purpose**: Learn complex representations
- **Strengths**: Captures subtle patterns, scalable
- **Use Case**: Large datasets, complex non-linearity
- **Limitations**: Requires more data, less interpretable

## 🎓 Evaluation Metrics

### Classification Metrics
- **Accuracy**: Overall correctness
- **Precision**: Positive predictive value
- **Recall (Sensitivity)**: True positive rate
- **F1 Score**: Harmonic mean of precision and recall
- **AUC-ROC**: Area under ROC curve
- **Specificity**: True negative rate

### Regression Metrics (for probability calibration)
- **RMSE**: Root mean squared error
- **MAE**: Mean absolute error

### Business Metrics
- **Approval Rate**: % of approved loans
- **Default Rate**: % of defaulted loans
- **Cost Analysis**: Financial impact

## ⚖️ Fairness Analysis

### Demographic Parity
Equal approval rates across demographic groups:
```
P(Y=1|A=a) ≈ P(Y=1|A=b)
```

### Equal Opportunity
Equal true positive rates across groups:
```
P(Ŷ=1|Y=1,A=a) ≈ P(Ŷ=1|Y=1,A=b)
```

### Disparate Impact (80% Rule)
Protected group approval rate ≥ 80% of favored group:
```
P(Ŷ=1|A=protected) / P(Ŷ=1|A=favored) ≥ 0.80
```

## 🔍 Model Explainability

### SHAP Values
- **Global Importance**: Feature impact across all predictions
- **Local Explanations**: Why a specific prediction was made
- **Interaction Effects**: How features combine

### LIME
- **Local Surrogate**: Approximate model behavior locally
- **Model-Agnostic**: Works with any model type
- **Interpretable**: Simple linear explanations

## 📈 Monitoring

### Data Drift
- **Detection**: Kolmogorov-Smirnov test
- **Threshold**: p-value < 0.05
- **Action**: Retrain model with recent data

### Model Drift
- **Metrics**: Accuracy, precision, recall degradation
- **Threshold**: > 5% performance drop
- **Action**: Investigate and retrain

### Prediction Drift
- **Detection**: Distribution shift in predictions
- **Monitoring**: Approval rate changes
- **Action**: Review model behavior

## 🔐 CI/CD Pipeline

### Stages
1. **Linting**: Code quality checks (flake8, black, isort)
2. **Unit Tests**: Component-level testing
3. **Integration Tests**: End-to-end API testing
4. **Build**: Docker image creation
5. **Deploy**: Production deployment
6. **Monitor**: Performance tracking

### GitHub Actions
Automated pipeline triggered on push/PR to main branch.

## 📝 License

MIT License

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest tests/`
5. Submit a pull request

## 📞 Support

For issues and questions, please open a GitHub issue.

---

**Built for production ML workflows with enterprise-grade features.**
