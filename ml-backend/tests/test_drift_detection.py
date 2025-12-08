"""
Tests for drift detection functionality
"""

import pytest
import numpy as np
import pandas as pd
from app.monitoring.drift_detector import DriftDetector


@pytest.fixture
def sample_data():
    """Generate sample data for testing"""
    np.random.seed(42)
    
    reference_data = [
        {
            "credit_score": np.random.randint(600, 800),
            "annual_income": np.random.randint(30000, 100000),
            "loan_amount": np.random.randint(5000, 50000),
            "loan_status": np.random.choice([0, 1])
        }
        for _ in range(100)
    ]
    
    # Current data with slight drift
    current_data = [
        {
            "credit_score": np.random.randint(550, 750),  # Shifted distribution
            "annual_income": np.random.randint(25000, 95000),
            "loan_amount": np.random.randint(6000, 55000),
            "loan_status": np.random.choice([0, 1])
        }
        for _ in range(100)
    ]
    
    return reference_data, current_data


def test_drift_detector_initialization():
    """Test DriftDetector initialization"""
    detector = DriftDetector()
    assert detector.drift_threshold == 0.05


def test_detect_drift(sample_data):
    """Test drift detection"""
    reference_data, current_data = sample_data
    detector = DriftDetector()
    
    report = detector.detect_drift(reference_data, current_data)
    
    assert "drift_detected" in report
    assert "drift_score" in report
    assert "drifted_features" in report
    assert "recommendations" in report
    assert isinstance(report["drift_detected"], bool)
    assert isinstance(report["drift_score"], float)


def test_no_drift_same_data():
    """Test that no drift is detected for identical data"""
    detector = DriftDetector()
    
    data = [{"value": i} for i in range(100)]
    
    report = detector.detect_drift(data, data)
    
    assert report["drift_score"] < 0.1  # Very low drift score


def test_recommendations_generated(sample_data):
    """Test that recommendations are generated"""
    reference_data, current_data = sample_data
    detector = DriftDetector()
    
    report = detector.detect_drift(reference_data, current_data)
    
    assert len(report["recommendations"]) > 0
    assert all(isinstance(rec, str) for rec in report["recommendations"])
