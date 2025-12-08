"""
SHAP (SHapley Additive exPlanations) Explainer
Global and local feature importance
"""

import shap
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class SHAPExplainer:
    """
    SHAP-based model explainability
    
    Provides:
    - Global feature importance
    - Local prediction explanations
    - Feature interactions
    """
    
    def __init__(self):
        self.explainer = None
        self.shap_values = None
    
    def explain(
        self,
        model: Any,
        features: Dict[str, Any],
        feature_names: List[str],
        background_data: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Generate SHAP explanation for a single prediction
        
        Args:
            model: Trained model
            features: Feature dictionary
            feature_names: List of feature names
            background_data: Background dataset for SHAP (optional)
        
        Returns:
            SHAP explanation with feature importance
        """
        try:
            # Prepare features
            feature_values = [features.get(name, 0) for name in feature_names]
            X = np.array(feature_values).reshape(1, -1)
            
            # Create SHAP explainer
            if self.explainer is None:
                # Use TreeExplainer for tree-based models, KernelExplainer for others
                if hasattr(model, "predict_proba"):
                    try:
                        self.explainer = shap.TreeExplainer(model)
                        logger.info("Using TreeExplainer")
                    except:
                        # Fallback to KernelExplainer
                        if background_data is None:
                            background_data = X  # Use current sample as background
                        self.explainer = shap.KernelExplainer(model.predict_proba, background_data)
                        logger.info("Using KernelExplainer")
                else:
                    self.explainer = shap.KernelExplainer(model.predict, X)
                    logger.info("Using KernelExplainer")
            
            # Calculate SHAP values
            shap_values = self.explainer.shap_values(X)
            
            # Handle different SHAP value formats
            if isinstance(shap_values, list):
                # Binary classification returns list of 2 arrays
                shap_values = shap_values[1] if len(shap_values) > 1 else shap_values[0]
            
            # Extract values for single prediction
            if shap_values.ndim > 1:
                shap_values = shap_values[0]
            
            # Create feature importance dictionary
            feature_importance = {}
            for i, name in enumerate(feature_names):
                feature_importance[name] = float(shap_values[i])
            
            # Sort by absolute importance
            sorted_importance = dict(sorted(
                feature_importance.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            ))
            
            # Base value (expected model output)
            base_value = self.explainer.expected_value
            if isinstance(base_value, list):
                base_value = base_value[1] if len(base_value) > 1 else base_value[0]
            
            # Generate explanation text
            explanation = self._generate_explanation(sorted_importance, feature_names)
            
            return {
                "feature_importance": sorted_importance,
                "base_value": float(base_value),
                "prediction_value": float(base_value + sum(shap_values)),
                "explanation": explanation,
                "top_features": list(sorted_importance.keys())[:5]
            }
            
        except Exception as e:
            logger.error(f"SHAP explanation error: {str(e)}")
            # Return fallback explanation
            return self._fallback_explanation(features, feature_names)
    
    def global_importance(
        self,
        model: Any,
        X: np.ndarray,
        feature_names: List[str],
        max_samples: int = 100
    ) -> Dict[str, Any]:
        """
        Calculate global feature importance using SHAP
        
        Args:
            model: Trained model
            X: Feature matrix
            feature_names: List of feature names
            max_samples: Maximum samples to use for SHAP calculation
        
        Returns:
            Global feature importance
        """
        try:
            # Limit samples for performance
            if len(X) > max_samples:
                X_sample = X[np.random.choice(len(X), max_samples, replace=False)]
            else:
                X_sample = X
            
            # Create explainer
            try:
                explainer = shap.TreeExplainer(model)
            except:
                explainer = shap.KernelExplainer(model.predict_proba, X_sample[:10])
            
            # Calculate SHAP values
            shap_values = explainer.shap_values(X_sample)
            
            if isinstance(shap_values, list):
                shap_values = shap_values[1] if len(shap_values) > 1 else shap_values[0]
            
            # Calculate mean absolute SHAP values
            mean_abs_shap = np.abs(shap_values).mean(axis=0)
            
            # Create importance dictionary
            importance = {}
            for i, name in enumerate(feature_names):
                importance[name] = float(mean_abs_shap[i])
            
            # Normalize to percentages
            total = sum(importance.values())
            if total > 0:
                importance = {k: (v/total)*100 for k, v in importance.items()}
            
            # Sort by importance
            importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
            
            return {
                "global_importance": importance,
                "top_features": list(importance.keys())[:10]
            }
            
        except Exception as e:
            logger.error(f"Global SHAP importance error: {str(e)}")
            raise
    
    def _generate_explanation(
        self,
        feature_importance: Dict[str, float],
        feature_names: List[str]
    ) -> str:
        """
        Generate human-readable explanation from SHAP values
        
        Args:
            feature_importance: Dictionary of feature SHAP values
            feature_names: List of all feature names
        
        Returns:
            Explanation text
        """
        # Get top positive and negative contributors
        positive = {k: v for k, v in feature_importance.items() if v > 0}
        negative = {k: v for k, v in feature_importance.items() if v < 0}
        
        explanation_parts = []
        
        # Top positive contributors
        if positive:
            top_positive = list(positive.items())[:3]
            pos_text = ", ".join([f"{k} (+{v:.3f})" for k, v in top_positive])
            explanation_parts.append(f"Factors increasing approval: {pos_text}")
        
        # Top negative contributors
        if negative:
            top_negative = sorted(negative.items(), key=lambda x: x[1])[:3]
            neg_text = ", ".join([f"{k} ({v:.3f})" for k, v in top_negative])
            explanation_parts.append(f"Factors decreasing approval: {neg_text}")
        
        return ". ".join(explanation_parts)
    
    def _fallback_explanation(
        self,
        features: Dict[str, Any],
        feature_names: List[str]
    ) -> Dict[str, Any]:
        """
        Fallback explanation when SHAP fails
        
        Args:
            features: Feature dictionary
            feature_names: List of feature names
        
        Returns:
            Simple feature importance based on heuristics
        """
        # Simple rule-based importance
        importance_weights = {
            "credit_score": 0.30,
            "creditScore": 0.30,
            "income": 0.25,
            "loan_amount": 0.15,
            "loanAmount": 0.15,
            "debt_to_income": 0.10,
            "debtToIncome": 0.10,
            "employment_length": 0.08,
            "employmentLength": 0.08,
            "age": 0.07,
            "total_debt": 0.05,
            "totalDebt": 0.05
        }
        
        feature_importance = {}
        for name in feature_names:
            weight = importance_weights.get(name, 0.01)
            feature_importance[name] = weight
        
        return {
            "feature_importance": feature_importance,
            "base_value": 0.5,
            "prediction_value": 0.5,
            "explanation": "SHAP explanation unavailable. Showing rule-based importance.",
            "top_features": list(feature_importance.keys())[:5]
        }
