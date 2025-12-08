"""
Prisma Client Wrapper for ML Backend
Manages database connections and operations
"""

from prisma import Prisma
from typing import Optional, Dict, Any, List
import logging
from contextlib import asynccontextmanager
import os

logger = logging.getLogger(__name__)

# Global Prisma client instance
_prisma_client: Optional[Prisma] = None


def get_prisma_client() -> Prisma:
    """
    Get or create Prisma client singleton
    
    Returns:
        Prisma client instance
    """
    global _prisma_client
    
    if _prisma_client is None:
        _prisma_client = Prisma()
    
    return _prisma_client


async def connect_database():
    """Connect to database"""
    try:
        client = get_prisma_client()
        await client.connect()
        logger.info("✅ Database connected successfully")
        return client
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        raise


async def disconnect_database():
    """Disconnect from database"""
    try:
        client = get_prisma_client()
        await client.disconnect()
        logger.info("Database disconnected")
    except Exception as e:
        logger.error(f"Database disconnection error: {str(e)}")


@asynccontextmanager
async def get_db():
    """
    Context manager for database operations
    
    Usage:
        async with get_db() as db:
            await db.prediction.create(...)
    """
    client = get_prisma_client()
    
    try:
        if not client.is_connected():
            await client.connect()
        yield client
    finally:
        pass  # Keep connection alive for reuse


class DatabaseManager:
    """High-level database operations manager"""
    
    def __init__(self):
        self.client = get_prisma_client()
    
    async def ensure_connected(self):
        """Ensure database is connected"""
        if not self.client.is_connected():
            await self.client.connect()
    
    # ==================== Model Registry ====================
    
    async def register_model(
        self,
        name: str,
        version: str,
        model_type: str,
        metrics: Dict[str, float],
        hyperparameters: Dict[str, Any],
        feature_importance: Dict[str, float],
        is_active: bool = False
    ) -> Any:
        """
        Register a new trained model
        
        Args:
            name: Model name
            version: Model version
            model_type: Type of model (random_forest, xgboost, etc.)
            metrics: Performance metrics
            hyperparameters: Model hyperparameters
            feature_importance: Feature importance scores
            is_active: Whether this is the active model
        
        Returns:
            Created model record
        """
        await self.ensure_connected()
        
        try:
            # If setting as active, deactivate other models
            if is_active:
                await self.client.model.update_many(
                    where={"modelType": model_type, "isActive": True},
                    data={"isActive": False}
                )
            
            model = await self.client.model.create(
                data={
                    "name": name,
                    "version": version,
                    "modelType": model_type,
                    "accuracy": metrics.get("accuracy", 0.0),
                    "precision": metrics.get("precision", 0.0),
                    "recall": metrics.get("recall", 0.0),
                    "f1Score": metrics.get("f1_score", 0.0),
                    "aucRoc": metrics.get("auc_roc", 0.0),
                    "fairnessScore": metrics.get("fairness_score", 0.0),
                    "hyperparameters": hyperparameters,
                    "featureImportance": feature_importance,
                    "isActive": is_active
                }
            )
            
            logger.info(f"✅ Model registered: {name} v{version}")
            return model
            
        except Exception as e:
            logger.error(f"Model registration error: {str(e)}")
            raise
    
    async def get_active_model(self, model_type: str) -> Optional[Any]:
        """Get the currently active model"""
        await self.ensure_connected()
        
        return await self.client.model.find_first(
            where={"modelType": model_type, "isActive": True}
        )
    
    async def list_models(
        self,
        model_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Any]:
        """List all models, optionally filtered by type"""
        await self.ensure_connected()
        
        where = {"modelType": model_type} if model_type else {}
        
        return await self.client.model.find_many(
            where=where,
            order={"trainingDate": "desc"},
            take=limit
        )
    
    # ==================== Predictions ====================
    
    async def log_prediction(
        self,
        model_id: str,
        features: Dict[str, Any],
        prediction: int,
        probability: float,
        confidence: float,
        risk_score: float,
        latency: float
    ) -> Any:
        """
        Log a prediction for monitoring
        
        Args:
            model_id: ID of model used
            features: Input features
            prediction: Predicted class (0 or 1)
            probability: Prediction probability
            confidence: Model confidence
            risk_score: Calculated risk score
            latency: Prediction latency in ms
        
        Returns:
            Created prediction record
        """
        await self.ensure_connected()
        
        try:
            prediction_record = await self.client.prediction.create(
                data={
                    "modelId": model_id,
                    "features": features,
                    "prediction": prediction,
                    "probability": probability,
                    "confidence": confidence,
                    "riskScore": risk_score,
                    "latency": latency
                }
            )
            
            return prediction_record
            
        except Exception as e:
            logger.error(f"Prediction logging error: {str(e)}")
            raise
    
    async def get_recent_predictions(
        self,
        model_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Any]:
        """Get recent predictions"""
        await self.ensure_connected()
        
        where = {"modelId": model_id} if model_id else {}
        
        return await self.client.prediction.find_many(
            where=where,
            order={"timestamp": "desc"},
            take=limit
        )
    
    async def add_prediction_feedback(
        self,
        prediction_id: str,
        ground_truth: int
    ):
        """Add ground truth feedback to prediction"""
        await self.ensure_connected()
        
        from datetime import datetime
        
        await self.client.prediction.update(
            where={"id": prediction_id},
            data={
                "groundTruth": ground_truth,
                "feedbackDate": datetime.now()
            }
        )
    
    # ==================== Model Metrics ====================
    
    async def log_model_metrics(
        self,
        model_id: str,
        metrics: Dict[str, float],
        period_start,
        period_end,
        sample_size: int
    ) -> Any:
        """
        Log time-series model metrics
        
        Args:
            model_id: Model ID
            metrics: Performance metrics
            period_start: Start of measurement period
            period_end: End of measurement period
            sample_size: Number of samples evaluated
        
        Returns:
            Created metric record
        """
        await self.ensure_connected()
        
        try:
            metric_record = await self.client.modelmetric.create(
                data={
                    "modelId": model_id,
                    "accuracy": metrics.get("accuracy", 0.0),
                    "precision": metrics.get("precision", 0.0),
                    "recall": metrics.get("recall", 0.0),
                    "f1Score": metrics.get("f1_score", 0.0),
                    "aucRoc": metrics.get("auc_roc", 0.0),
                    "demographicParity": metrics.get("demographic_parity", 0.0),
                    "equalOpportunity": metrics.get("equal_opportunity", 0.0),
                    "disparateImpact": metrics.get("disparate_impact", 0.0),
                    "fairnessScore": metrics.get("fairness_score", 0.0),
                    "approvalRate": metrics.get("approval_rate", 0.0),
                    "avgLoanAmount": metrics.get("avg_loan_amount"),
                    "periodStart": period_start,
                    "periodEnd": period_end,
                    "sampleSize": sample_size
                }
            )
            
            return metric_record
            
        except Exception as e:
            logger.error(f"Metrics logging error: {str(e)}")
            raise
    
    async def get_metrics_time_series(
        self,
        model_id: str,
        limit: int = 100
    ) -> List[Any]:
        """Get time series of model metrics"""
        await self.ensure_connected()
        
        return await self.client.modelmetric.find_many(
            where={"modelId": model_id},
            order={"timestamp": "desc"},
            take=limit
        )
    
    # ==================== Drift Reports ====================
    
    async def log_drift_report(
        self,
        model_id: str,
        drift_report: Dict[str, Any],
        reference_start,
        reference_end,
        current_start,
        current_end,
        reference_size: int,
        current_size: int
    ) -> Any:
        """
        Log a drift detection report
        
        Args:
            model_id: Model ID
            drift_report: Drift detection results
            reference_start: Start of reference period
            reference_end: End of reference period
            current_start: Start of current period
            current_end: End of current period
            reference_size: Reference sample size
            current_size: Current sample size
        
        Returns:
            Created drift report record
        """
        await self.ensure_connected()
        
        try:
            # Determine alert level
            drift_score = drift_report.get("drift_score", 0.0)
            performance_degraded = drift_report.get("model_performance_change", {}).get("performance_degraded", False)
            
            if performance_degraded or drift_score > 0.7:
                alert_level = "critical"
            elif drift_score > 0.5 or drift_report.get("drift_detected", False):
                alert_level = "warning"
            else:
                alert_level = "none"
            
            report = await self.client.driftreport.create(
                data={
                    "modelId": model_id,
                    "driftDetected": drift_report.get("drift_detected", False),
                    "driftScore": drift_score,
                    "driftedFeatures": drift_report.get("drifted_features", []),
                    "featureDriftScores": drift_report.get("feature_drift_scores", {}),
                    "predictionDrift": drift_report.get("prediction_drift"),
                    "performanceChange": drift_report.get("model_performance_change"),
                    "performanceDegraded": performance_degraded,
                    "recommendations": drift_report.get("recommendations", []),
                    "alertLevel": alert_level,
                    "referenceStart": reference_start,
                    "referenceEnd": reference_end,
                    "currentStart": current_start,
                    "currentEnd": current_end,
                    "referenceSampleSize": reference_size,
                    "currentSampleSize": current_size
                }
            )
            
            # Create alert if critical
            if alert_level == "critical":
                await self.create_alert(
                    type="drift",
                    severity="critical",
                    title="Critical Model Drift Detected",
                    message=f"Model {model_id} has significant drift. Retraining recommended.",
                    source=model_id,
                    data=drift_report
                )
            
            return report
            
        except Exception as e:
            logger.error(f"Drift report logging error: {str(e)}")
            raise
    
    async def get_drift_reports(
        self,
        model_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Any]:
        """Get recent drift reports"""
        await self.ensure_connected()
        
        where = {"modelId": model_id} if model_id else {}
        
        return await self.client.driftreport.find_many(
            where=where,
            order={"timestamp": "desc"},
            take=limit
        )
    
    # ==================== Alerts ====================
    
    async def create_alert(
        self,
        type: str,
        severity: str,
        title: str,
        message: str,
        source: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Create a new alert"""
        await self.ensure_connected()
        
        try:
            alert = await self.client.alert.create(
                data={
                    "type": type,
                    "severity": severity,
                    "title": title,
                    "message": message,
                    "source": source,
                    "data": data
                }
            )
            
            logger.warning(f"🚨 Alert created: [{severity}] {title}")
            return alert
            
        except Exception as e:
            logger.error(f"Alert creation error: {str(e)}")
            raise
    
    async def get_unacknowledged_alerts(self, limit: int = 50) -> List[Any]:
        """Get unacknowledged alerts"""
        await self.ensure_connected()
        
        return await self.client.alert.find_many(
            where={"acknowledged": False},
            order={"timestamp": "desc"},
            take=limit
        )
    
    async def acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert"""
        await self.ensure_connected()
        
        from datetime import datetime
        
        await self.client.alert.update(
            where={"id": alert_id},
            data={
                "acknowledged": True,
                "acknowledgedAt": datetime.now()
            }
        )
    
    # ==================== API Usage Tracking ====================
    
    async def log_api_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time: float,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        error_type: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Log API request for monitoring"""
        await self.ensure_connected()
        
        try:
            await self.client.apiusage.create(
                data={
                    "endpoint": endpoint,
                    "method": method,
                    "statusCode": status_code,
                    "responseTime": response_time,
                    "userAgent": user_agent,
                    "ipAddress": ip_address,
                    "errorType": error_type,
                    "errorMessage": error_message
                }
            )
        except Exception as e:
            logger.error(f"API usage logging error: {str(e)}")
    
    # ==================== System Health ====================
    
    async def log_system_health(
        self,
        cpu_usage: float,
        memory_usage: float,
        disk_usage: Optional[float],
        active_models: int,
        total_predictions: int,
        avg_latency: float,
        error_rate: float,
        status: str
    ):
        """Log system health metrics"""
        await self.ensure_connected()
        
        try:
            await self.client.systemhealth.create(
                data={
                    "cpuUsage": cpu_usage,
                    "memoryUsage": memory_usage,
                    "diskUsage": disk_usage,
                    "activeModels": active_models,
                    "totalPredictions": total_predictions,
                    "avgLatency": avg_latency,
                    "errorRate": error_rate,
                    "status": status
                }
            )
        except Exception as e:
            logger.error(f"System health logging error: {str(e)}")


# Global database manager instance
db_manager = DatabaseManager()
