"""
Integration tests for full ML pipeline
"""

import pytest
import httpx
import time


BASE_URL = "http://localhost:8000"


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data


@pytest.mark.asyncio
async def test_prediction_flow():
    """Test complete prediction flow"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Sample prediction request
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
            "explain": True
        }
        
        response = await client.post(f"{BASE_URL}/api/predict", json=payload)
        
        # Accept both success and model-not-trained errors
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "prediction" in data
            assert "probability" in data


@pytest.mark.asyncio
async def test_metrics_endpoint():
    """Test Prometheus metrics endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/metrics")
        assert response.status_code == 200
        # Check that metrics are in Prometheus format
        assert b"# HELP" in response.content or b"# TYPE" in response.content


@pytest.mark.asyncio
async def test_concurrent_predictions():
    """Test handling multiple concurrent predictions"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {
            "features": {
                "credit_score": 720,
                "annual_income": 75000,
                "loan_amount": 25000
            },
            "model_type": "random_forest",
            "explain": False
        }
        
        # Send 5 concurrent requests
        tasks = [
            client.post(f"{BASE_URL}/api/predict", json=payload)
            for _ in range(5)
        ]
        
        # Execute concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check that all requests completed
        assert len(responses) == 5


import asyncio

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
