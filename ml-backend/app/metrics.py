"""
Prometheus metrics for monitoring
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# Prediction metrics
predictions_total = Counter(
    'predictions_total',
    'Total predictions made',
    ['model_type', 'prediction']
)

prediction_duration_seconds = Histogram(
    'prediction_duration_seconds',
    'Prediction latency in seconds',
    ['model_type']
)

# Model performance metrics
model_accuracy = Gauge(
    'model_accuracy',
    'Current model accuracy',
    ['model_type']
)

model_auc = Gauge(
    'model_auc',
    'Current model AUC-ROC',
    ['model_type']
)

# Drift metrics
drift_score = Gauge(
    'drift_score',
    'Current data drift score'
)

drifted_features_count = Gauge(
    'drifted_features_count',
    'Number of features with detected drift'
)

# API errors
api_errors_total = Counter(
    'api_errors_total',
    'Total API errors',
    ['endpoint', 'error_type']
)

# Training metrics
model_training_duration_seconds = Histogram(
    'model_training_duration_seconds',
    'Model training duration in seconds',
    ['model_type']
)

model_training_total = Counter(
    'model_training_total',
    'Total model training runs',
    ['model_type', 'status']
)

# Fairness metrics
fairness_score = Gauge(
    'fairness_score',
    'Overall fairness score'
)

demographic_parity = Gauge(
    'demographic_parity',
    'Demographic parity metric',
    ['group']
)


def get_metrics() -> Response:
    """
    Return Prometheus metrics
    
    Returns:
        Response with metrics in Prometheus format
    """
    metrics = generate_latest()
    return Response(content=metrics, media_type=CONTENT_TYPE_LATEST)


def track_prediction(model_type: str, prediction: int, duration: float):
    """
    Track prediction metrics
    
    Args:
        model_type: Type of model used
        prediction: Prediction result (0 or 1)
        duration: Prediction duration in seconds
    """
    predictions_total.labels(
        model_type=model_type,
        prediction=str(prediction)
    ).inc()
    
    prediction_duration_seconds.labels(
        model_type=model_type
    ).observe(duration)


def track_request(method: str, endpoint: str, status: int, duration: float):
    """
    Track HTTP request metrics
    
    Args:
        method: HTTP method
        endpoint: API endpoint
        status: HTTP status code
        duration: Request duration in seconds
    """
    http_requests_total.labels(
        method=method,
        endpoint=endpoint,
        status=str(status)
    ).inc()
    
    http_request_duration_seconds.labels(
        method=method,
        endpoint=endpoint
    ).observe(duration)


def update_model_metrics(accuracy: float, auc: float, model_type: str = "random_forest"):
    """
    Update model performance metrics
    
    Args:
        accuracy: Model accuracy
        auc: Model AUC-ROC
        model_type: Type of model
    """
    model_accuracy.labels(model_type=model_type).set(accuracy)
    model_auc.labels(model_type=model_type).set(auc)


def update_drift_metrics(drift_score_value: float, drifted_features: int):
    """
    Update drift detection metrics
    
    Args:
        drift_score_value: Drift score
        drifted_features: Number of drifted features
    """
    drift_score.set(drift_score_value)
    drifted_features_count.set(drifted_features)


def track_error(endpoint: str, error_type: str):
    """
    Track API errors
    
    Args:
        endpoint: API endpoint where error occurred
        error_type: Type of error
    """
    api_errors_total.labels(
        endpoint=endpoint,
        error_type=error_type
    ).inc()
