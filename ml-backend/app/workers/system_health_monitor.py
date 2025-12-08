#!/usr/bin/env python3
"""
System Health Monitoring Worker
Tracks CPU, memory, and system metrics
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import psutil
from app.database import db_manager, connect_database, disconnect_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemHealthMonitor:
    """Monitor system health and log metrics"""
    
    def __init__(self, check_interval: int = 60):
        """
        Initialize system health monitor
        
        Args:
            check_interval: Check interval in seconds (default: 60s)
        """
        self.check_interval = check_interval
    
    async def run(self):
        """Run system health monitoring loop"""
        
        logger.info("🚀 Starting system health monitor...")
        logger.info(f"Check interval: {self.check_interval} seconds")
        
        try:
            # Connect to database
            await connect_database()
            logger.info("✅ Database connected")
            
            while True:
                try:
                    await self.collect_metrics()
                except Exception as e:
                    logger.error(f"Error collecting metrics: {str(e)}")
                
                # Wait for next check
                await asyncio.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("System health monitor stopped by user")
        except Exception as e:
            logger.error(f"Fatal error in health monitor: {str(e)}")
        finally:
            await disconnect_database()
    
    async def collect_metrics(self):
        """Collect and log system metrics"""
        
        try:
            # CPU and Memory
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Disk usage (if available)
            try:
                disk = psutil.disk_usage('/')
                disk_usage = disk.percent
            except:
                disk_usage = None
            
            # Get active models count
            models = await db_manager.list_models(limit=100)
            active_models = sum(1 for m in models if m.isActive)
            
            # Get total predictions today
            from datetime import datetime, timedelta
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            predictions_today = await db_manager.client.prediction.count(
                where={"timestamp": {"gte": today_start}}
            )
            
            # Calculate average latency
            recent_predictions = await db_manager.get_recent_predictions(limit=100)
            avg_latency = sum(p.latency for p in recent_predictions) / len(recent_predictions) if recent_predictions else 0
            
            # Calculate error rate (from API usage)
            total_requests = await db_manager.client.apiusage.count(
                where={"timestamp": {"gte": today_start}}
            )
            
            error_requests = await db_manager.client.apiusage.count(
                where={
                    "timestamp": {"gte": today_start},
                    "statusCode": {"gte": 400}
                }
            )
            
            error_rate = (error_requests / total_requests * 100) if total_requests > 0 else 0
            
            # Determine system status
            if cpu_usage > 90 or memory_usage > 90:
                status = "unhealthy"
            elif cpu_usage > 70 or memory_usage > 70:
                status = "degraded"
            else:
                status = "healthy"
            
            # Log to database
            await db_manager.log_system_health(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                active_models=active_models,
                total_predictions=predictions_today,
                avg_latency=avg_latency,
                error_rate=error_rate,
                status=status
            )
            
            # Log to console
            logger.info(
                f"📊 System Health: {status.upper()} | "
                f"CPU: {cpu_usage:.1f}% | "
                f"Memory: {memory_usage:.1f}% | "
                f"Predictions: {predictions_today} | "
                f"Errors: {error_rate:.1f}%"
            )
            
            # Create alert if unhealthy
            if status == "unhealthy":
                await db_manager.create_alert(
                    type="system",
                    severity="critical",
                    title="System Resources Critical",
                    message=f"CPU: {cpu_usage:.1f}%, Memory: {memory_usage:.1f}%",
                    source="system_health_monitor",
                    data={
                        "cpu_usage": cpu_usage,
                        "memory_usage": memory_usage,
                        "disk_usage": disk_usage
                    }
                )
        
        except Exception as e:
            logger.error(f"Metrics collection error: {str(e)}")
            raise


async def main():
    """Main entry point"""
    
    # Get check interval from environment
    check_interval = int(os.getenv("HEALTH_CHECK_INTERVAL", "60"))
    
    monitor = SystemHealthMonitor(check_interval=check_interval)
    await monitor.run()


if __name__ == "__main__":
    asyncio.run(main())
