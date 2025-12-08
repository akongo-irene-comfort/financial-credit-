"""
Continuous drift monitoring worker
Runs in background to detect data and model drift
"""

import time
import logging
import os
from datetime import datetime
from typing import Dict, Any
import asyncio

from app.monitoring.drift_detector import DriftDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DriftMonitorWorker:
    """
    Background worker for continuous drift detection
    """
    
    def __init__(self, check_interval: int = 3600):
        """
        Initialize drift monitor
        
        Args:
            check_interval: Interval between drift checks in seconds (default: 1 hour)
        """
        self.check_interval = check_interval
        self.drift_detector = DriftDetector()
        self.reference_data = []
        self.current_data = []
        self.alert_webhook_url = os.getenv("ALERT_WEBHOOK_URL")
    
    def load_reference_data(self):
        """Load reference data for drift comparison"""
        try:
            # Load from storage (file, database, or API)
            # For now, using placeholder
            logger.info("Loading reference data for drift detection...")
            # self.reference_data = load_from_storage()
            return True
        except Exception as e:
            logger.error(f"Failed to load reference data: {str(e)}")
            return False
    
    def collect_current_data(self):
        """Collect recent production data"""
        try:
            # Collect from logs, database, or monitoring system
            logger.info("Collecting current production data...")
            # self.current_data = collect_from_production()
            return True
        except Exception as e:
            logger.error(f"Failed to collect current data: {str(e)}")
            return False
    
    def check_drift(self) -> Dict[str, Any]:
        """
        Run drift detection
        
        Returns:
            Drift detection report
        """
        try:
            if not self.reference_data or not self.current_data:
                logger.warning("Insufficient data for drift detection")
                return {"error": "Insufficient data"}
            
            # Run drift detection
            drift_report = self.drift_detector.detect_drift(
                reference_data=self.reference_data,
                current_data=self.current_data
            )
            
            # Log results
            logger.info(f"Drift Check Complete - Drift Detected: {drift_report['drift_detected']}")
            logger.info(f"Drift Score: {drift_report['drift_score']:.3f}")
            
            if drift_report['drift_detected']:
                logger.warning(f"⚠️ Drift detected in features: {drift_report['drifted_features']}")
                self.send_alert(drift_report)
            
            # Save report
            self.save_drift_report(drift_report)
            
            return drift_report
            
        except Exception as e:
            logger.error(f"Drift detection error: {str(e)}")
            return {"error": str(e)}
    
    def send_alert(self, drift_report: Dict[str, Any]):
        """
        Send alert when drift is detected
        
        Args:
            drift_report: Drift detection results
        """
        try:
            if not self.alert_webhook_url:
                logger.info("No alert webhook configured, skipping alert")
                return
            
            alert_message = {
                "timestamp": datetime.now().isoformat(),
                "alert_type": "drift_detected",
                "drift_score": drift_report.get("drift_score", 0),
                "drifted_features": drift_report.get("drifted_features", []),
                "recommendations": drift_report.get("recommendations", [])
            }
            
            logger.info(f"📢 Alert sent: {alert_message}")
            # Send to webhook (Slack, PagerDuty, etc.)
            # requests.post(self.alert_webhook_url, json=alert_message)
            
        except Exception as e:
            logger.error(f"Failed to send alert: {str(e)}")
    
    def save_drift_report(self, drift_report: Dict[str, Any]):
        """
        Save drift report for historical tracking
        
        Args:
            drift_report: Drift detection results
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"/app/logs/drift_report_{timestamp}.json"
            
            import json
            with open(report_file, "w") as f:
                json.dump(drift_report, f, indent=2)
            
            logger.info(f"Drift report saved to {report_file}")
            
        except Exception as e:
            logger.error(f"Failed to save drift report: {str(e)}")
    
    async def run(self):
        """
        Run drift monitoring loop
        """
        logger.info(f"🚀 Drift Monitor Worker started (check interval: {self.check_interval}s)")
        
        while True:
            try:
                logger.info("=" * 60)
                logger.info(f"Starting drift check at {datetime.now()}")
                
                # Load reference data
                if not self.load_reference_data():
                    logger.warning("Skipping drift check - no reference data")
                    await asyncio.sleep(self.check_interval)
                    continue
                
                # Collect current data
                if not self.collect_current_data():
                    logger.warning("Skipping drift check - failed to collect current data")
                    await asyncio.sleep(self.check_interval)
                    continue
                
                # Run drift detection
                drift_report = self.check_drift()
                
                logger.info(f"Next drift check in {self.check_interval} seconds")
                logger.info("=" * 60)
                
                # Wait for next check
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in drift monitoring loop: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute on error


def main():
    """Main entry point for drift monitor worker"""
    # Get configuration from environment
    check_interval = int(os.getenv("DRIFT_CHECK_INTERVAL", 3600))
    
    # Create and run worker
    worker = DriftMonitorWorker(check_interval=check_interval)
    
    # Run async loop
    asyncio.run(worker.run())


if __name__ == "__main__":
    main()
