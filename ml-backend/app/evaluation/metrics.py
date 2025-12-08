"""
Comprehensive Model Evaluation Metrics
Includes: Accuracy, Precision, Recall, F1, AUC-ROC, RMSE, Cross-Validation
"""

import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    mean_squared_error, mean_absolute_error, r2_score
)
from sklearn.model_selection import cross_val_score, cross_validate
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """
    Comprehensive model evaluation with multiple metrics
    """
    
    def evaluate(
        self,
        y_true: List[int],
        y_pred: List[int],
        y_pred_proba: List[float]
    ) -> Dict[str, Any]:
        """
        Calculate all evaluation metrics
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Predicted probabilities
        
        Returns:
            Dictionary of metrics
        """
        try:
            y_true = np.array(y_true)
            y_pred = np.array(y_pred)
            y_pred_proba = np.array(y_pred_proba)
            
            # Classification metrics
            accuracy = accuracy_score(y_true, y_pred)
            precision = precision_score(y_true, y_pred, zero_division=0)
            recall = recall_score(y_true, y_pred, zero_division=0)
            f1 = f1_score(y_true, y_pred, zero_division=0)
            
            # AUC-ROC
            try:
                auc_roc = roc_auc_score(y_true, y_pred_proba)
            except:
                auc_roc = 0.0
            
            # Confusion matrix
            cm = confusion_matrix(y_true, y_pred)
            tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)
            
            # Specificity and sensitivity
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
            sensitivity = recall  # Same as recall/TPR
            
            # Regression-like metrics (for probability calibration)
            rmse = np.sqrt(mean_squared_error(y_true, y_pred))
            mae = mean_absolute_error(y_true, y_pred)
            
            # Business metrics
            approval_rate = np.mean(y_pred)
            actual_approval_rate = np.mean(y_true)
            
            metrics = {
                # Primary classification metrics
                "accuracy": float(accuracy),
                "precision": float(precision),
                "recall": float(recall),
                "f1_score": float(f1),
                "auc_roc": float(auc_roc),
                
                # Confusion matrix components
                "true_positives": int(tp),
                "true_negatives": int(tn),
                "false_positives": int(fp),
                "false_negatives": int(fn),
                
                # Additional metrics
                "specificity": float(specificity),
                "sensitivity": float(sensitivity),
                "rmse": float(rmse),
                "mae": float(mae),
                
                # Business metrics
                "predicted_approval_rate": float(approval_rate),
                "actual_approval_rate": float(actual_approval_rate),
                
                # Model diagnostics
                "samples": len(y_true),
            }
            
            logger.info(f"Evaluation complete. Accuracy: {accuracy:.4f}, AUC: {auc_roc:.4f}")
            
            return {
                "metrics": metrics,
                "confusion_matrix": cm.tolist(),
                "classification_report": classification_report(y_true, y_pred, output_dict=True)
            }
            
        except Exception as e:
            logger.error(f"Evaluation error: {str(e)}")
            raise
    
    def cross_validation(
        self,
        model: Any,
        X: np.ndarray,
        y: np.ndarray,
        cv: int = 5
    ) -> Dict[str, Any]:
        """
        Perform k-fold cross-validation
        
        Args:
            model: Trained model
            X: Features
            y: Target
            cv: Number of folds
        
        Returns:
            Cross-validation scores
        """
        try:
            scoring = {
                "accuracy": "accuracy",
                "precision": "precision",
                "recall": "recall",
                "f1": "f1",
                "roc_auc": "roc_auc"
            }
            
            cv_results = cross_validate(
                model, X, y,
                cv=cv,
                scoring=scoring,
                return_train_score=True,
                n_jobs=-1
            )
            
            results = {}
            for metric in scoring.keys():
                test_scores = cv_results[f"test_{metric}"]
                train_scores = cv_results[f"train_{metric}"]
                
                results[metric] = {
                    "test_mean": float(np.mean(test_scores)),
                    "test_std": float(np.std(test_scores)),
                    "test_scores": test_scores.tolist(),
                    "train_mean": float(np.mean(train_scores)),
                    "train_std": float(np.std(train_scores)),
                }
            
            logger.info(f"Cross-validation complete. Mean accuracy: {results['accuracy']['test_mean']:.4f}")
            
            return results
            
        except Exception as e:
            logger.error(f"Cross-validation error: {str(e)}")
            raise
    
    def comprehensive_evaluation(
        self,
        pipeline: Any,
        data: List[Dict[str, Any]],
        model_type: str
    ) -> Dict[str, Any]:
        """
        Perform comprehensive evaluation including cross-validation and error analysis
        
        Args:
            pipeline: Model pipeline
            data: Evaluation data
            model_type: Type of model
        
        Returns:
            Comprehensive evaluation results
        """
        try:
            # This would integrate with the actual pipeline
            # For now, return structured results
            
            logger.info("Performing comprehensive evaluation...")
            
            return {
                "metrics": {},
                "cv_scores": {},
                "confusion_matrix": [],
                "predictions": [],
                "error_analysis": {
                    "high_confidence_errors": 0,
                    "low_confidence_errors": 0,
                    "error_rate_by_group": {}
                }
            }
            
        except Exception as e:
            logger.error(f"Comprehensive evaluation error: {str(e)}")
            raise
    
    def error_analysis(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_pred_proba: np.ndarray,
        features: np.ndarray,
        feature_names: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze prediction errors
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Prediction probabilities
            features: Feature matrix
            feature_names: Feature names
        
        Returns:
            Error analysis results
        """
        try:
            # Find errors
            errors = y_true != y_pred
            error_indices = np.where(errors)[0]
            
            # Confidence analysis
            confidence = np.max(y_pred_proba, axis=1) if y_pred_proba.ndim > 1 else np.abs(y_pred_proba - 0.5) * 2
            
            high_confidence_errors = np.sum((errors) & (confidence > 0.8))
            low_confidence_errors = np.sum((errors) & (confidence < 0.5))
            
            # Feature statistics for errors
            error_features = features[errors]
            correct_features = features[~errors]
            
            feature_diffs = {}
            for i, name in enumerate(feature_names):
                error_mean = np.mean(error_features[:, i]) if len(error_features) > 0 else 0
                correct_mean = np.mean(correct_features[:, i]) if len(correct_features) > 0 else 0
                feature_diffs[name] = float(abs(error_mean - correct_mean))
            
            return {
                "total_errors": int(np.sum(errors)),
                "error_rate": float(np.mean(errors)),
                "high_confidence_errors": int(high_confidence_errors),
                "low_confidence_errors": int(low_confidence_errors),
                "feature_differences": feature_diffs,
                "error_indices": error_indices.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error analysis failed: {str(e)}")
            raise
