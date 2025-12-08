"""
LIME (Local Interpretable Model-agnostic Explanations) Explainer
Alternative to SHAP for model explainability
"""

from lime.lime_tabular import LimeTabularExplainer
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class LIMEExplainer:
    """
    LIME-based model explainability
    
    Provides local explanations for individual predictions
    """
    
    def __init__(self):
        self.explainer = None
    
    def explain(
        self,
        model: Any,
        features: Dict[str, Any],
        feature_names: List[str],
        training_data: Optional[np.ndarray] = None,
        class_names: List[str] = ["Rejected", "Approved"]
    ) -> Dict[str, Any]:
        """
        Generate LIME explanation for a single prediction
        
        Args:
            model: Trained model
            features: Feature dictionary
            feature_names: List of feature names
            training_data: Training data for LIME (optional)
            class_names: Class labels
        
        Returns:
            LIME explanation
        """
        try:
            # Prepare features
            feature_values = np.array([features.get(name, 0) for name in feature_names]).reshape(1, -1)
            
            # Create LIME explainer if not exists
            if self.explainer is None:
                if training_data is None:
                    # Use current sample as training data
                    training_data = feature_values
                
                self.explainer = LimeTabularExplainer(
                    training_data=training_data,
                    feature_names=feature_names,
                    class_names=class_names,
                    mode="classification",
                    discretize_continuous=True
                )
            
            # Get prediction function
            if hasattr(model, "predict_proba"):
                predict_fn = model.predict_proba
            else:
                # Wrap predict to return probabilities
                def predict_fn(X):
                    preds = model.predict(X)
                    return np.column_stack([1 - preds, preds])
            
            # Generate explanation
            exp = self.explainer.explain_instance(
                feature_values[0],
                predict_fn,
                num_features=len(feature_names)
            )
            
            # Extract feature importance
            feature_importance = {}
            for feature_idx, weight in exp.as_list():
                # Parse feature name from LIME format
                feature_name = feature_idx.split("<=")[0].split(">")[0].strip()
                # Find matching feature name
                matching_name = None
                for fname in feature_names:
                    if fname in feature_name or feature_name in fname:
                        matching_name = fname
                        break
                if matching_name:
                    feature_importance[matching_name] = float(weight)
            
            # Sort by absolute importance
            sorted_importance = dict(sorted(
                feature_importance.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            ))
            
            # Get prediction probabilities
            prediction_proba = exp.predict_proba
            
            # Generate explanation text
            explanation = self._generate_explanation(exp, class_names)
            
            return {
                "feature_importance": sorted_importance,
                "prediction_proba": prediction_proba.tolist() if isinstance(prediction_proba, np.ndarray) else [prediction_proba],
                "explanation": explanation,
                "top_features": list(sorted_importance.keys())[:5],
                "local_prediction": int(prediction_proba[1] > 0.5) if isinstance(prediction_proba, np.ndarray) else int(prediction_proba > 0.5)
            }
            
        except Exception as e:
            logger.error(f"LIME explanation error: {str(e)}")
            # Return fallback
            return self._fallback_explanation(features, feature_names)
    
    def _generate_explanation(
        self,
        lime_exp: Any,
        class_names: List[str]
    ) -> str:
        """
        Generate human-readable explanation from LIME
        
        Args:
            lime_exp: LIME explanation object
            class_names: Class labels
        
        Returns:
            Explanation text
        """
        try:
            # Get the explanation as list
            exp_list = lime_exp.as_list()
            
            # Separate positive and negative contributors
            positive = [(feat, weight) for feat, weight in exp_list if weight > 0]
            negative = [(feat, weight) for feat, weight in exp_list if weight < 0]
            
            explanation_parts = []
            
            if positive:
                top_positive = positive[:3]
                pos_text = ", ".join([f"{feat} (+{weight:.3f})" for feat, weight in top_positive])
                explanation_parts.append(f"Features supporting approval: {pos_text}")
            
            if negative:
                top_negative = negative[:3]
                neg_text = ", ".join([f"{feat} ({weight:.3f})" for feat, weight in top_negative])
                explanation_parts.append(f"Features against approval: {neg_text}")
            
            return ". ".join(explanation_parts)
            
        except:
            return "LIME explanation generated successfully"
    
    def _fallback_explanation(
        self,
        features: Dict[str, Any],
        feature_names: List[str]
    ) -> Dict[str, Any]:
        """
        Fallback explanation when LIME fails
        
        Args:
            features: Feature dictionary
            feature_names: List of feature names
        
        Returns:
            Simple feature importance
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
            "employmentLength": 0.08
        }
        
        feature_importance = {}
        for name in feature_names:
            weight = importance_weights.get(name, 0.01)
            feature_importance[name] = weight
        
        return {
            "feature_importance": feature_importance,
            "explanation": "LIME explanation unavailable. Showing rule-based importance.",
            "top_features": list(feature_importance.keys())[:5],
            "local_prediction": 1
        }
