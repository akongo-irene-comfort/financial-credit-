"""
FastAPI Application for Credit Scoring ML Backend
Supports: Classical ML, Deep Learning, Experiment Tracking, Explainability, Monitoring
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import logging
import time

# Import our modules
from app.models.classical_ml import ClassicalMLPipeline
from app.models.deep_learning import DeepLearningPipeline
from app.models.experiment_tracker import ExperimentTracker
from app.evaluation.metrics import ModelEvaluator
from app.evaluation.fairness import FairnessAnalyzer
from app.explainability.shap_explainer import SHAPExplainer
from app.explainability.lime_explainer import LIMEExplainer
from app.monitoring.drift_detector import DriftDetector

# Import Prometheus metrics
try:
    from app.metrics import (
        get_metrics,
        track_prediction,
        track_request,
        update_model_metrics,
        update_drift_metrics,
        track_error
    )
    METRICS_ENABLED = True
except ImportError:
    METRICS_ENABLED = False
    logging.warning("Prometheus metrics not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Credit Scoring ML API",
    description="Production-ready ML API with experiment tracking, explainability, and monitoring",
    version="1.0.0"
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_request_timing(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Track metrics if enabled
    if METRICS_ENABLED:
        track_request(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
            duration=duration
        )
    
    return response

# Global instances
classical_pipeline = ClassicalMLPipeline()
dl_pipeline = DeepLearningPipeline()
experiment_tracker = ExperimentTracker()
evaluator = ModelEvaluator()
fairness_analyzer = FairnessAnalyzer()
shap_explainer = SHAPExplainer()
lime_explainer = LIMEExplainer()
drift_detector = DriftDetector()


# Pydantic Models
class TrainingRequest(BaseModel):
    data: List[Dict[str, Any]]
    model_type: str = "random_forest"  # logistic_regression, random_forest, xgboost, dnn
    hyperparameters: Optional[Dict[str, Any]] = None
    experiment_name: str = "credit_scoring"
    

class PredictionRequest(BaseModel):
    features: Dict[str, Any]
    model_type: str = "random_forest"
    explain: bool = True


class FairnessRequest(BaseModel):
    data: List[Dict[str, Any]]
    predictions: List[int]
    sensitive_features: List[str] = ["gender", "age_group"]


class ExplainRequest(BaseModel):
    features: Dict[str, Any]
    model_type: str = "random_forest"
    method: str = "shap"  # shap or lime


# Health Check
@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "Credit Scoring ML API",
        "version": "1.0.0",
        "models_loaded": {
            "classical": classical_pipeline.is_trained(),
            "deep_learning": dl_pipeline.is_trained()
        }
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mlflow": experiment_tracker.is_connected(),
        "models": {
            "random_forest": classical_pipeline.is_trained(),
            "deep_learning": dl_pipeline.is_trained()
        }
    }


# Prometheus metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    if METRICS_ENABLED:
        return get_metrics()
    else:
        return {"error": "Metrics not enabled"}


# Training Endpoints
@app.post("/api/train")
async def train_model(request: TrainingRequest):
    """
    Train a model with experiment tracking and hyperparameter tuning.
    Supports: Logistic Regression, Random Forest, XGBoost, Deep Neural Network
    """
    try:
        logger.info(f"Training {request.model_type} model with {len(request.data)} samples")
        
        # Start MLflow experiment
        experiment_id = experiment_tracker.start_experiment(request.experiment_name)
        
        if request.model_type in ["logistic_regression", "random_forest", "xgboost"]:
            # Classical ML pipeline
            results = classical_pipeline.train(
                data=request.data,
                model_type=request.model_type,
                hyperparameters=request.hyperparameters,
                experiment_tracker=experiment_tracker
            )
        elif request.model_type == "dnn":
            # Deep Learning pipeline
            results = dl_pipeline.train(
                data=request.data,
                hyperparameters=request.hyperparameters,
                experiment_tracker=experiment_tracker
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported model type: {request.model_type}")
        
        # Evaluate model
        evaluation = evaluator.evaluate(
            y_true=results["y_test"],
            y_pred=results["y_pred"],
            y_pred_proba=results["y_pred_proba"]
        )
        
        # Log metrics to MLflow
        experiment_tracker.log_metrics(evaluation["metrics"])
        experiment_tracker.log_params(results["hyperparameters"])
        
        # End experiment
        experiment_tracker.end_experiment()
        
        # Update metrics
        if METRICS_ENABLED:
            update_model_metrics(
                accuracy=evaluation["metrics"]["accuracy"],
                auc=evaluation["metrics"]["auc_roc"],
                model_type=request.model_type
            )
        
        return {
            "success": True,
            "model_type": request.model_type,
            "model_id": results["model_id"],
            "metrics": evaluation["metrics"],
            "feature_importance": results.get("feature_importance", {}),
            "experiment_id": experiment_id,
            "training_samples": len(request.data)
        }
        
    except Exception as e:
        logger.error(f"Training error: {str(e)}")
        if METRICS_ENABLED:
            track_error("/api/train", type(e).__name__)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/predict")
async def predict(request: PredictionRequest):
    """Make prediction with optional explainability"""
    start_time = time.time()
    
    try:
        # Select pipeline
        if request.model_type == "dnn":
            pipeline = dl_pipeline
        else:
            pipeline = classical_pipeline
        
        # Make prediction
        prediction = pipeline.predict(request.features, request.model_type)
        
        # Track metrics
        duration = time.time() - start_time
        if METRICS_ENABLED:
            track_prediction(request.model_type, prediction["prediction"], duration)
        
        # Add explainability if requested
        explanation = None
        if request.explain:
            explanation = shap_explainer.explain(
                model=pipeline.get_model(request.model_type),
                features=request.features,
                feature_names=list(request.features.keys())
            )
        
        return {
            "prediction": int(prediction["prediction"]),
            "probability": float(prediction["probability"]),
            "confidence": float(prediction["confidence"]),
            "risk_score": float(prediction["risk_score"]),
            "explanation": explanation
        }
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        if METRICS_ENABLED:
            track_error("/api/predict", type(e).__name__)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/evaluate")
async def evaluate_model(data: List[Dict[str, Any]], model_type: str = "random_forest"):
    """
    Comprehensive model evaluation with cross-validation, metrics, and fairness analysis
    """
    try:
        # Select pipeline
        if model_type == "dnn":
            pipeline = dl_pipeline
        else:
            pipeline = classical_pipeline
        
        # Evaluate with cross-validation
        evaluation_results = evaluator.comprehensive_evaluation(
            pipeline=pipeline,
            data=data,
            model_type=model_type
        )
        
        # Fairness analysis
        fairness_results = fairness_analyzer.analyze(
            data=data,
            predictions=evaluation_results["predictions"],
            sensitive_features=["gender", "age_group"]
        )
        
        return {
            "metrics": evaluation_results["metrics"],
            "cross_validation": evaluation_results["cv_scores"],
            "confusion_matrix": evaluation_results["confusion_matrix"],
            "fairness": fairness_results,
            "error_analysis": evaluation_results["error_analysis"]
        }
        
    except Exception as e:
        logger.error(f"Evaluation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/fairness/analyze")
async def analyze_fairness(request: FairnessRequest):
    """
    Perform comprehensive fairness analysis including:
    - Demographic Parity
    - Equal Opportunity
    - Disparate Impact (80% rule)
    - Statistical Parity Difference
    """
    try:
        results = fairness_analyzer.analyze(
            data=request.data,
            predictions=request.predictions,
            sensitive_features=request.sensitive_features
        )
        
        return {
            "fairness_score": results["overall_score"],
            "demographic_parity": results["demographic_parity"],
            "equal_opportunity": results["equal_opportunity"],
            "disparate_impact": results["disparate_impact"],
            "recommendations": results["recommendations"]
        }
        
    except Exception as e:
        logger.error(f"Fairness analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/explain")
async def explain_prediction(request: ExplainRequest):
    """
    Generate model explanations using SHAP or LIME
    """
    try:
        # Select pipeline
        if request.model_type == "dnn":
            pipeline = dl_pipeline
        else:
            pipeline = classical_pipeline
        
        model = pipeline.get_model(request.model_type)
        
        if request.method == "shap":
            explanation = shap_explainer.explain(
                model=model,
                features=request.features,
                feature_names=list(request.features.keys())
            )
        else:  # lime
            explanation = lime_explainer.explain(
                model=model,
                features=request.features,
                feature_names=list(request.features.keys())
            )
        
        return {
            "method": request.method,
            "feature_importance": explanation["feature_importance"],
            "explanation": explanation["explanation"],
            "base_value": explanation.get("base_value", 0.5)
        }
        
    except Exception as e:
        logger.error(f"Explanation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/monitoring/drift")
async def detect_drift(reference_data: List[Dict[str, Any]], current_data: List[Dict[str, Any]]):
    """
    Detect data drift and model drift between reference and current data
    """
    try:
        drift_report = drift_detector.detect_drift(
            reference_data=reference_data,
            current_data=current_data
        )
        
        # Update drift metrics
        if METRICS_ENABLED:
            update_drift_metrics(
                drift_score_value=drift_report["drift_score"],
                drifted_features=len(drift_report["drifted_features"])
            )
        
        return {
            "drift_detected": drift_report["drift_detected"],
            "drift_score": drift_report["drift_score"],
            "drifted_features": drift_report["drifted_features"],
            "model_performance_change": drift_report.get("model_performance_change", {}),
            "recommendations": drift_report["recommendations"]
        }
        
    except Exception as e:
        logger.error(f"Drift detection error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/experiments")
async def list_experiments():
    """
    List all MLflow experiments with metrics
    """
    try:
        experiments = experiment_tracker.list_experiments()
        return {"experiments": experiments}
    except Exception as e:
        logger.error(f"List experiments error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )