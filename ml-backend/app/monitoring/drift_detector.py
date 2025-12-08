"""
Data Drift and Model Drift Detection
Monitors model performance degradation over time
"""

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp, chi2_contingency
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class DriftDetector:
    """
    Drift detection for monitoring model performance
    
    Detects:
    1. Data Drift: Distribution changes in input features
    2. Concept Drift: Changes in relationship between features and target
    3. Prediction Drift: Changes in model output distribution
    """
    
    def __init__(self, drift_threshold: float = 0.05):
        """
        Initialize drift detector
        
        Args:
            drift_threshold: P-value threshold for drift detection (default: 0.05)
        """
        self.drift_threshold = drift_threshold
        self.reference_stats = {}
    
    def detect_drift(
        self,
        reference_data: List[Dict[str, Any]],
        current_data: List[Dict[str, Any]],
        feature_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Detect data and prediction drift
        
        Args:
            reference_data: Historical reference data
            current_data: Current production data
            feature_names: List of features to monitor (optional)
        
        Returns:
            Drift detection report
        """
        try:
            ref_df = pd.DataFrame(reference_data)
            curr_df = pd.DataFrame(current_data)
            
            if feature_names is None:
                # Use common columns
                feature_names = list(set(ref_df.columns) & set(curr_df.columns))
            
            drift_report = {
                "drift_detected": False,
                "drift_score": 0.0,
                "drifted_features": [],
                "feature_drift_scores": {},
                "model_performance_change": {},
                "recommendations": []
            }
            
            # Detect feature drift
            drifted_features = []
            drift_scores = []
            
            for feature in feature_names:
                if feature not in ref_df.columns or feature not in curr_df.columns:
                    continue
                
                # Skip target variable
                if feature in ["loan_status", "approved", "prediction"]:
                    continue
                
                # Detect drift based on feature type
                if pd.api.types.is_numeric_dtype(ref_df[feature]):
                    drift_score, is_drifted = self._detect_numerical_drift(
                        ref_df[feature],
                        curr_df[feature]
                    )
                else:
                    drift_score, is_drifted = self._detect_categorical_drift(
                        ref_df[feature],
                        curr_df[feature]
                    )
                
                drift_report["feature_drift_scores"][feature] = float(drift_score)
                drift_scores.append(drift_score)
                
                if is_drifted:
                    drifted_features.append(feature)
            
            # Overall drift assessment
            if drift_scores:
                drift_report["drift_score"] = float(np.mean(drift_scores))
                drift_report["drift_detected"] = len(drifted_features) > 0
                drift_report["drifted_features"] = drifted_features
            
            # Detect prediction drift
            if "prediction" in ref_df.columns and "prediction" in curr_df.columns:
                pred_drift = self._detect_prediction_drift(
                    ref_df["prediction"],
                    curr_df["prediction"]
                )
                drift_report["prediction_drift"] = pred_drift
            
            # Model performance change (if labels available)
            if "loan_status" in ref_df.columns and "loan_status" in curr_df.columns:
                if "prediction" in ref_df.columns and "prediction" in curr_df.columns:
                    perf_change = self._detect_performance_drift(
                        ref_df["loan_status"],
                        ref_df["prediction"],
                        curr_df["loan_status"],
                        curr_df["prediction"]
                    )
                    drift_report["model_performance_change"] = perf_change
            
            # Generate recommendations
            drift_report["recommendations"] = self._generate_recommendations(drift_report)
            
            logger.info(f"Drift detection complete. Drift detected: {drift_report['drift_detected']}")
            
            return drift_report
            
        except Exception as e:
            logger.error(f"Drift detection error: {str(e)}")
            raise
    
    def _detect_numerical_drift(
        self,
        reference: pd.Series,
        current: pd.Series
    ) -> tuple:
        """
        Detect drift in numerical features using Kolmogorov-Smirnov test
        
        Args:
            reference: Reference feature values
            current: Current feature values
        
        Returns:
            (drift_score, is_drifted)
        """
        try:
            # Remove NaN values
            ref_clean = reference.dropna()
            curr_clean = current.dropna()
            
            if len(ref_clean) == 0 or len(curr_clean) == 0:
                return 0.0, False
            
            # Kolmogorov-Smirnov test
            statistic, p_value = ks_2samp(ref_clean, curr_clean)
            
            # Drift score (inverse of p-value)
            drift_score = 1 - p_value
            is_drifted = p_value < self.drift_threshold
            
            return drift_score, is_drifted
            
        except Exception as e:
            logger.error(f"Numerical drift detection error: {str(e)}")
            return 0.0, False
    
    def _detect_categorical_drift(
        self,
        reference: pd.Series,
        current: pd.Series
    ) -> tuple:
        """
        Detect drift in categorical features using Chi-square test
        
        Args:
            reference: Reference feature values
            current: Current feature values
        
        Returns:
            (drift_score, is_drifted)
        """
        try:
            # Get value counts
            ref_counts = reference.value_counts()
            curr_counts = current.value_counts()
            
            # Align categories
            all_categories = set(ref_counts.index) | set(curr_counts.index)
            
            ref_freq = [ref_counts.get(cat, 0) for cat in all_categories]
            curr_freq = [curr_counts.get(cat, 0) for cat in all_categories]
            
            if sum(ref_freq) == 0 or sum(curr_freq) == 0:
                return 0.0, False
            
            # Chi-square test
            contingency_table = np.array([ref_freq, curr_freq])
            chi2, p_value, _, _ = chi2_contingency(contingency_table)
            
            # Drift score
            drift_score = 1 - p_value
            is_drifted = p_value < self.drift_threshold
            
            return drift_score, is_drifted
            
        except Exception as e:
            logger.error(f"Categorical drift detection error: {str(e)}")
            return 0.0, False
    
    def _detect_prediction_drift(
        self,
        reference_predictions: pd.Series,
        current_predictions: pd.Series
    ) -> Dict[str, Any]:
        """
        Detect drift in model predictions
        
        Args:
            reference_predictions: Historical predictions
            current_predictions: Current predictions
        
        Returns:
            Prediction drift report
        """
        try:
            ref_rate = reference_predictions.mean()
            curr_rate = current_predictions.mean()
            
            rate_change = curr_rate - ref_rate
            rate_change_pct = (rate_change / ref_rate * 100) if ref_rate > 0 else 0
            
            # Statistical test
            statistic, p_value = ks_2samp(reference_predictions, current_predictions)
            
            return {
                "reference_approval_rate": float(ref_rate),
                "current_approval_rate": float(curr_rate),
                "rate_change": float(rate_change),
                "rate_change_percent": float(rate_change_pct),
                "p_value": float(p_value),
                "significant_drift": p_value < self.drift_threshold
            }
            
        except Exception as e:
            logger.error(f"Prediction drift detection error: {str(e)}")
            return {}
    
    def _detect_performance_drift(
        self,
        ref_true: pd.Series,
        ref_pred: pd.Series,
        curr_true: pd.Series,
        curr_pred: pd.Series
    ) -> Dict[str, Any]:
        """
        Detect model performance degradation
        
        Args:
            ref_true: Reference true labels
            ref_pred: Reference predictions
            curr_true: Current true labels
            curr_pred: Current predictions
        
        Returns:
            Performance drift report
        """
        try:
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
            
            # Reference metrics
            ref_accuracy = accuracy_score(ref_true, ref_pred)
            ref_precision = precision_score(ref_true, ref_pred, zero_division=0)
            ref_recall = recall_score(ref_true, ref_pred, zero_division=0)
            ref_f1 = f1_score(ref_true, ref_pred, zero_division=0)
            
            # Current metrics
            curr_accuracy = accuracy_score(curr_true, curr_pred)
            curr_precision = precision_score(curr_true, curr_pred, zero_division=0)
            curr_recall = recall_score(curr_true, curr_pred, zero_division=0)
            curr_f1 = f1_score(curr_true, curr_pred, zero_division=0)
            
            # Calculate changes
            accuracy_change = curr_accuracy - ref_accuracy
            precision_change = curr_precision - ref_precision
            recall_change = curr_recall - ref_recall
            f1_change = curr_f1 - ref_f1
            
            # Performance degradation threshold: 5%
            degradation_threshold = -0.05
            
            return {
                "reference_accuracy": float(ref_accuracy),
                "current_accuracy": float(curr_accuracy),
                "accuracy_change": float(accuracy_change),
                "precision_change": float(precision_change),
                "recall_change": float(recall_change),
                "f1_change": float(f1_change),
                "performance_degraded": accuracy_change < degradation_threshold
            }
            
        except Exception as e:
            logger.error(f"Performance drift detection error: {str(e)}")
            return {}
    
    def _generate_recommendations(self, drift_report: Dict[str, Any]) -> List[str]:
        """
        Generate actionable recommendations based on drift detection
        
        Args:
            drift_report: Drift detection results
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if not drift_report["drift_detected"]:
            recommendations.append("✅ No significant drift detected. Continue monitoring.")
            return recommendations
        
        # Feature drift recommendations
        if drift_report["drifted_features"]:
            recommendations.append(
                f"⚠️ Data drift detected in {len(drift_report['drifted_features'])} features: "
                f"{', '.join(drift_report['drifted_features'][:3])}"
            )
            recommendations.append(
                "💡 Consider: Retrain model with recent data or investigate data quality issues"
            )
        
        # Prediction drift recommendations
        if "prediction_drift" in drift_report:
            pred_drift = drift_report["prediction_drift"]
            if pred_drift.get("significant_drift", False):
                change_pct = pred_drift.get("rate_change_percent", 0)
                recommendations.append(
                    f"⚠️ Prediction distribution shifted by {change_pct:.1f}%. "
                    "Model behavior may have changed."
                )
        
        # Performance degradation recommendations
        if "model_performance_change" in drift_report:
            perf = drift_report["model_performance_change"]
            if perf.get("performance_degraded", False):
                acc_change = perf.get("accuracy_change", 0) * 100
                recommendations.append(
                    f"❌ Model accuracy dropped by {abs(acc_change):.1f}%. "
                    "Immediate retraining recommended."
                )
        
        # High drift score
        if drift_report["drift_score"] > 0.7:
            recommendations.append(
                "🚨 High overall drift score. Data distribution has significantly changed. "
                "Model retraining is critical."
            )
        
        return recommendations
