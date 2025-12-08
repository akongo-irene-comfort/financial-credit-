"""
Classical ML Models: Logistic Regression, Random Forest, XGBoost
With hyperparameter tuning and experiment tracking
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import joblib
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ClassicalMLPipeline:
    """
    Classical ML Pipeline with multiple model support
    
    Model Justifications:
    1. Logistic Regression: Baseline linear model, interpretable, fast, good for linearly separable data
    2. Random Forest: Handles non-linear relationships, feature importance, robust to outliers
    3. XGBoost: State-of-the-art gradient boosting, handles imbalanced data well, high accuracy
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_names = []
        self.model_metadata = {}
        
        # Model hyperparameter search spaces
        self.param_grids = {
            "logistic_regression": {
                "C": [0.001, 0.01, 0.1, 1, 10, 100],
                "penalty": ["l1", "l2"],
                "solver": ["liblinear", "saga"],
                "max_iter": [1000]
            },
            "random_forest": {
                "n_estimators": [50, 100, 200],
                "max_depth": [10, 20, 30, None],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4],
                "max_features": ["sqrt", "log2"]
            },
            "xgboost": {
                "n_estimators": [50, 100, 200],
                "max_depth": [3, 5, 7, 10],
                "learning_rate": [0.01, 0.05, 0.1, 0.2],
                "subsample": [0.8, 0.9, 1.0],
                "colsample_bytree": [0.8, 0.9, 1.0]
            }
        }
    
    def _prepare_data(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert data to DataFrame and handle preprocessing"""
        df = pd.DataFrame(data)
        
        # Feature engineering
        if "age" in df.columns and "income" in df.columns:
            df["age_income_ratio"] = df["age"] / (df["income"] + 1)
        
        if "loan_amount" in df.columns and "income" in df.columns:
            df["loan_to_income"] = df["loan_amount"] / (df["income"] + 1)
        
        # One-hot encode categorical features
        categorical_cols = df.select_dtypes(include=["object"]).columns
        if len(categorical_cols) > 0:
            df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
        
        return df
    
    def train(
        self,
        data: List[Dict[str, Any]],
        model_type: str = "random_forest",
        hyperparameters: Optional[Dict[str, Any]] = None,
        experiment_tracker: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Train a classical ML model with hyperparameter tuning
        
        Args:
            data: Training data
            model_type: "logistic_regression", "random_forest", or "xgboost"
            hyperparameters: Optional custom hyperparameters
            experiment_tracker: MLflow experiment tracker
        
        Returns:
            Training results with metrics and model info
        """
        try:
            logger.info(f"Training {model_type} model...")
            
            # Prepare data
            df = self._prepare_data(data)
            
            # Separate features and target
            target_col = "loan_status" if "loan_status" in df.columns else "approved"
            if target_col not in df.columns:
                raise ValueError("Target column not found in data")
            
            X = df.drop(columns=[target_col])
            y = df[target_col]
            self.feature_names = list(X.columns)
            
            # Train/Validation/Test split: 70% / 15% / 15%
            X_train, X_temp, y_train, y_temp = train_test_split(
                X, y, test_size=0.3, random_state=42, stratify=y
            )
            X_val, X_test, y_val, y_test = train_test_split(
                X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
            )
            
            # Feature scaling (important for Logistic Regression)
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_val_scaled = scaler.transform(X_val)
            X_test_scaled = scaler.transform(X_test)
            self.scalers[model_type] = scaler
            
            # Initialize model
            if model_type == "logistic_regression":
                base_model = LogisticRegression(random_state=42)
                param_grid = hyperparameters or self.param_grids["logistic_regression"]
                X_train_final, X_val_final = X_train_scaled, X_val_scaled
                X_test_final = X_test_scaled
                
            elif model_type == "random_forest":
                base_model = RandomForestClassifier(random_state=42)
                param_grid = hyperparameters or self.param_grids["random_forest"]
                X_train_final, X_val_final = X_train, X_val
                X_test_final = X_test
                
            elif model_type == "xgboost":
                base_model = xgb.XGBClassifier(random_state=42, use_label_encoder=False, eval_metric="logloss")
                param_grid = hyperparameters or self.param_grids["xgboost"]
                X_train_final, X_val_final = X_train, X_val
                X_test_final = X_test
                
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
            
            # Hyperparameter tuning with GridSearchCV
            logger.info("Performing hyperparameter tuning...")
            grid_search = GridSearchCV(
                base_model,
                param_grid,
                cv=5,
                scoring="roc_auc",
                n_jobs=-1,
                verbose=1
            )
            grid_search.fit(X_train_final, y_train)
            
            # Best model
            best_model = grid_search.best_estimator_
            best_params = grid_search.best_params_
            
            logger.info(f"Best parameters: {best_params}")
            
            # Store model
            self.models[model_type] = best_model
            
            # Predictions
            y_pred = best_model.predict(X_test_final)
            y_pred_proba = best_model.predict_proba(X_test_final)[:, 1]
            
            # Feature importance
            feature_importance = {}
            if hasattr(best_model, "feature_importances_"):
                importances = best_model.feature_importances_
                feature_importance = dict(zip(self.feature_names, importances.tolist()))
                feature_importance = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
            elif hasattr(best_model, "coef_"):
                importances = np.abs(best_model.coef_[0])
                feature_importance = dict(zip(self.feature_names, importances.tolist()))
                feature_importance = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
            
            # Model metadata
            model_id = f"{model_type}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
            self.model_metadata[model_type] = {
                "model_id": model_id,
                "model_type": model_type,
                "hyperparameters": best_params,
                "feature_names": self.feature_names,
                "training_samples": len(X_train),
                "validation_samples": len(X_val),
                "test_samples": len(X_test)
            }
            
            # Log to MLflow if tracker provided
            if experiment_tracker:
                experiment_tracker.log_params(best_params)
                experiment_tracker.log_artifact(best_model, f"model_{model_type}")
            
            return {
                "model_id": model_id,
                "model_type": model_type,
                "hyperparameters": best_params,
                "feature_importance": feature_importance,
                "y_test": y_test.tolist(),
                "y_pred": y_pred.tolist(),
                "y_pred_proba": y_pred_proba.tolist(),
                "cv_scores": grid_search.cv_results_["mean_test_score"].tolist()
            }
            
        except Exception as e:
            logger.error(f"Training error: {str(e)}")
            raise
    
    def predict(self, features: Dict[str, Any], model_type: str = "random_forest") -> Dict[str, Any]:
        """Make prediction with a trained model"""
        if model_type not in self.models:
            raise ValueError(f"Model {model_type} not trained yet")
        
        model = self.models[model_type]
        scaler = self.scalers.get(model_type)
        
        # Prepare features
        df = pd.DataFrame([features])
        
        # Feature engineering (same as training)
        if "age" in df.columns and "income" in df.columns:
            df["age_income_ratio"] = df["age"] / (df["income"] + 1)
        
        if "loan_amount" in df.columns and "income" in df.columns:
            df["loan_to_income"] = df["loan_amount"] / (df["income"] + 1)
        
        # One-hot encode
        categorical_cols = df.select_dtypes(include=["object"]).columns
        if len(categorical_cols) > 0:
            df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
        
        # Align with training features
        for col in self.feature_names:
            if col not in df.columns:
                df[col] = 0
        df = df[self.feature_names]
        
        # Scale if needed
        if scaler is not None and model_type == "logistic_regression":
            X = scaler.transform(df)
        else:
            X = df.values
        
        # Predict
        prediction = model.predict(X)[0]
        probability = model.predict_proba(X)[0]
        
        return {
            "prediction": int(prediction),
            "probability": float(probability[1]),
            "confidence": float(max(probability)),
            "risk_score": float(1 - probability[1])
        }
    
    def get_model(self, model_type: str):
        """Get trained model"""
        return self.models.get(model_type)
    
    def is_trained(self) -> bool:
        """Check if any model is trained"""
        return len(self.models) > 0
    
    def save_model(self, model_type: str, filepath: str):
        """Save model to disk"""
        if model_type not in self.models:
            raise ValueError(f"Model {model_type} not found")
        joblib.dump(self.models[model_type], filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, model_type: str, filepath: str):
        """Load model from disk"""
        self.models[model_type] = joblib.load(filepath)
        logger.info(f"Model loaded from {filepath}")
