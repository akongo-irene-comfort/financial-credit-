"""
Deep Neural Network (DNN) implementation using TensorFlow/Keras
For comparison with classical ML models
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, callbacks
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class DeepLearningPipeline:
    """
    Deep Neural Network Pipeline
    
    Model Justification:
    - DNN: Can learn complex non-linear patterns, handles high-dimensional data
    - Comparison with classical ML to understand when deep learning adds value
    - For credit scoring: May capture subtle interactions between features
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.history = None
        self.model_metadata = {}
    
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
    
    def _build_model(self, input_dim: int, hyperparameters: Optional[Dict[str, Any]] = None) -> keras.Model:
        """
        Build a simple DNN architecture
        
        Architecture:
        - Input layer
        - 2-3 hidden layers with dropout for regularization
        - Output layer with sigmoid activation
        """
        hp = hyperparameters or {}
        
        # Hyperparameters
        hidden_units_1 = hp.get("hidden_units_1", 128)
        hidden_units_2 = hp.get("hidden_units_2", 64)
        hidden_units_3 = hp.get("hidden_units_3", 32)
        dropout_rate = hp.get("dropout_rate", 0.3)
        learning_rate = hp.get("learning_rate", 0.001)
        activation = hp.get("activation", "relu")
        
        # Build model
        model = keras.Sequential([
            layers.Input(shape=(input_dim,)),
            
            # First hidden layer
            layers.Dense(hidden_units_1, activation=activation, name="hidden_1"),
            layers.BatchNormalization(),
            layers.Dropout(dropout_rate),
            
            # Second hidden layer
            layers.Dense(hidden_units_2, activation=activation, name="hidden_2"),
            layers.BatchNormalization(),
            layers.Dropout(dropout_rate),
            
            # Third hidden layer
            layers.Dense(hidden_units_3, activation=activation, name="hidden_3"),
            layers.BatchNormalization(),
            layers.Dropout(dropout_rate),
            
            # Output layer
            layers.Dense(1, activation="sigmoid", name="output")
        ])
        
        # Compile model
        optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
        model.compile(
            optimizer=optimizer,
            loss="binary_crossentropy",
            metrics=[
                "accuracy",
                keras.metrics.AUC(name="auc"),
                keras.metrics.Precision(name="precision"),
                keras.metrics.Recall(name="recall")
            ]
        )
        
        return model
    
    def train(
        self,
        data: List[Dict[str, Any]],
        hyperparameters: Optional[Dict[str, Any]] = None,
        experiment_tracker: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Train a Deep Neural Network
        
        Args:
            data: Training data
            hyperparameters: Model hyperparameters
            experiment_tracker: MLflow experiment tracker
        
        Returns:
            Training results
        """
        try:
            logger.info("Training Deep Neural Network...")
            
            # Prepare data
            df = self._prepare_data(data)
            
            # Separate features and target
            target_col = "loan_status" if "loan_status" in df.columns else "approved"
            if target_col not in df.columns:
                raise ValueError("Target column not found in data")
            
            X = df.drop(columns=[target_col])
            y = df[target_col]
            self.feature_names = list(X.columns)
            
            # Train/Validation/Test split
            X_train, X_temp, y_train, y_temp = train_test_split(
                X, y, test_size=0.3, random_state=42, stratify=y
            )
            X_val, X_test, y_val, y_test = train_test_split(
                X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
            )
            
            # Feature scaling (critical for neural networks)
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_val_scaled = self.scaler.transform(X_val)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Build model
            input_dim = X_train_scaled.shape[1]
            self.model = self._build_model(input_dim, hyperparameters)
            
            logger.info(f"Model architecture: {self.model.summary()}")
            
            # Callbacks
            early_stopping = callbacks.EarlyStopping(
                monitor="val_loss",
                patience=10,
                restore_best_weights=True
            )
            
            reduce_lr = callbacks.ReduceLROnPlateau(
                monitor="val_loss",
                factor=0.5,
                patience=5,
                min_lr=1e-6
            )
            
            # Training hyperparameters
            hp = hyperparameters or {}
            epochs = hp.get("epochs", 100)
            batch_size = hp.get("batch_size", 32)
            
            # Train model
            logger.info("Training model...")
            self.history = self.model.fit(
                X_train_scaled, y_train,
                validation_data=(X_val_scaled, y_val),
                epochs=epochs,
                batch_size=batch_size,
                callbacks=[early_stopping, reduce_lr],
                verbose=1
            )
            
            # Evaluate on test set
            y_pred_proba = self.model.predict(X_test_scaled).flatten()
            y_pred = (y_pred_proba > 0.5).astype(int)
            
            # Feature importance (using permutation importance approximation)
            feature_importance = self._calculate_feature_importance(X_test_scaled, y_test)
            
            # Model metadata
            model_id = f"dnn_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
            self.model_metadata = {
                "model_id": model_id,
                "model_type": "dnn",
                "hyperparameters": hyperparameters or {},
                "feature_names": self.feature_names,
                "training_samples": len(X_train),
                "validation_samples": len(X_val),
                "test_samples": len(X_test),
                "architecture": {
                    "total_params": self.model.count_params(),
                    "layers": len(self.model.layers)
                }
            }
            
            # Log to MLflow if tracker provided
            if experiment_tracker:
                experiment_tracker.log_params(hyperparameters or {})
                experiment_tracker.log_artifact(self.model, "model_dnn")
            
            return {
                "model_id": model_id,
                "model_type": "dnn",
                "hyperparameters": hyperparameters or {},
                "feature_importance": feature_importance,
                "y_test": y_test.tolist(),
                "y_pred": y_pred.tolist(),
                "y_pred_proba": y_pred_proba.tolist(),
                "training_history": {
                    "loss": self.history.history["loss"],
                    "val_loss": self.history.history["val_loss"],
                    "accuracy": self.history.history["accuracy"],
                    "val_accuracy": self.history.history["val_accuracy"]
                }
            }
            
        except Exception as e:
            logger.error(f"DNN training error: {str(e)}")
            raise
    
    def _calculate_feature_importance(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """Calculate feature importance using permutation importance"""
        baseline_score = self.model.evaluate(X_test, y_test, verbose=0)[1]  # accuracy
        
        importances = {}
        for i, feature_name in enumerate(self.feature_names):
            X_permuted = X_test.copy()
            np.random.shuffle(X_permuted[:, i])
            permuted_score = self.model.evaluate(X_permuted, y_test, verbose=0)[1]
            importance = baseline_score - permuted_score
            importances[feature_name] = max(0, importance)  # Only positive importance
        
        # Normalize
        total = sum(importances.values())
        if total > 0:
            importances = {k: v/total for k, v in importances.items()}
        
        return dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))
    
    def predict(self, features: Dict[str, Any], model_type: str = "dnn") -> Dict[str, Any]:
        """Make prediction with trained DNN"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        # Prepare features
        df = pd.DataFrame([features])
        
        # Feature engineering
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
        
        # Scale
        X = self.scaler.transform(df)
        
        # Predict
        probability = float(self.model.predict(X, verbose=0)[0][0])
        prediction = int(probability > 0.5)
        
        return {
            "prediction": prediction,
            "probability": probability,
            "confidence": max(probability, 1 - probability),
            "risk_score": 1 - probability
        }
    
    def get_model(self, model_type: str = "dnn"):
        """Get trained model"""
        return self.model
    
    def is_trained(self) -> bool:
        """Check if model is trained"""
        return self.model is not None
    
    def save_model(self, filepath: str):
        """Save model to disk"""
        if self.model is None:
            raise ValueError("No model to save")
        self.model.save(filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load model from disk"""
        self.model = keras.models.load_model(filepath)
        logger.info(f"Model loaded from {filepath}")
