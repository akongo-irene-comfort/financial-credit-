#!/usr/bin/env python3
"""
Database Setup Script
Initializes Neon PostgreSQL database with Prisma
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import connect_database, disconnect_database, db_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_database():
    """Setup database and run initial checks"""
    
    logger.info("🚀 Starting database setup...")
    
    try:
        # Connect to database
        await connect_database()
        logger.info("✅ Database connection successful")
        
        # Test database operations
        await test_database_operations()
        
        logger.info("✅ Database setup complete!")
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {str(e)}")
        raise
    finally:
        await disconnect_database()


async def test_database_operations():
    """Test basic database operations"""
    
    logger.info("Testing database operations...")
    
    try:
        # Test model count
        models = await db_manager.list_models(limit=1)
        logger.info(f"Found {len(models)} models in database")
        
        # Test alerts
        alerts = await db_manager.get_unacknowledged_alerts(limit=1)
        logger.info(f"Found {len(alerts)} unacknowledged alerts")
        
        logger.info("✅ Database operations test passed")
        
    except Exception as e:
        logger.error(f"Database operations test failed: {str(e)}")
        raise


async def seed_sample_data():
    """Seed sample data for testing"""
    
    logger.info("Seeding sample data...")
    
    try:
        # Create a sample model
        model = await db_manager.register_model(
            name="sample_model",
            version="1.0.0",
            model_type="random_forest",
            metrics={
                "accuracy": 0.87,
                "precision": 0.85,
                "recall": 0.83,
                "f1_score": 0.84,
                "auc_roc": 0.89,
                "fairness_score": 0.88
            },
            hyperparameters={
                "n_estimators": 100,
                "max_depth": 10,
                "min_samples_split": 5
            },
            feature_importance={
                "credit_score": 0.28,
                "income": 0.19,
                "loan_amount": 0.15
            },
            is_active=True
        )
        
        logger.info(f"✅ Sample model created: {model.id}")
        
        # Create a sample prediction
        prediction = await db_manager.log_prediction(
            model_id=model.id,
            features={
                "credit_score": 750,
                "income": 75000,
                "loan_amount": 25000
            },
            prediction=1,
            probability=0.84,
            confidence=0.92,
            risk_score=0.16,
            latency=45.5
        )
        
        logger.info(f"✅ Sample prediction logged: {prediction.id}")
        
        logger.info("✅ Sample data seeded successfully")
        
    except Exception as e:
        logger.error(f"Sample data seeding failed: {str(e)}")
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database setup script")
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Seed sample data"
    )
    
    args = parser.parse_args()
    
    if args.seed:
        asyncio.run(seed_sample_data())
    else:
        asyncio.run(setup_database())
