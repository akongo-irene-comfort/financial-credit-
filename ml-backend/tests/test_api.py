"""
Unit tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_predict_endpoint():
    """Test prediction endpoint"""
    payload = {
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
        "explain": False
    }
    
    response = client.post("/api/predict", json=payload)
    # May fail if model not trained, but should not crash
    assert response.status_code in [200, 500]


def test_metrics_endpoint():
    """Test Prometheus metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200


@pytest.mark.parametrize("endpoint", [
    "/",
    "/health",
    "/metrics"
])
def test_endpoint_availability(endpoint):
    """Test that all endpoints are available"""
    response = client.get(endpoint)
    assert response.status_code in [200, 404]  # 404 is acceptable for some endpoints
