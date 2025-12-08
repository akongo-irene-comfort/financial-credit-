"""
MLflow Experiment Tracking
Tracks experiments, parameters, metrics, and artifacts
"""

import mlflow
import mlflow.sklearn
import mlflow.tensorflow
import logging
from typing import Dict, Any, Optional
import os

logger = logging.getLogger(__name__)


class ExperimentTracker:
    """
    Wrapper for MLflow experiment tracking
    Tracks all experiments, hyperparameters, metrics, and models
    """
    
    def __init__(self, tracking_uri: str = "./mlruns"):
        """
        Initialize MLflow experiment tracker
        
        Args:
            tracking_uri: URI for MLflow tracking server
        """
        self.tracking_uri = tracking_uri
        mlflow.set_tracking_uri(tracking_uri)
        self.current_run = None
        self.experiment_name = None
        
        logger.info(f"MLflow tracking URI: {tracking_uri}")
    
    def start_experiment(self, experiment_name: str) -> str:
        """
        Start a new MLflow experiment
        
        Args:
            experiment_name: Name of the experiment
        
        Returns:
            Experiment ID
        """
        try:
            self.experiment_name = experiment_name
            
            # Set or create experiment
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(experiment_name)
                logger.info(f"Created new experiment: {experiment_name} (ID: {experiment_id})")
            else:
                experiment_id = experiment.experiment_id
                logger.info(f"Using existing experiment: {experiment_name} (ID: {experiment_id})")
            
            mlflow.set_experiment(experiment_name)
            
            # Start run
            self.current_run = mlflow.start_run(experiment_id=experiment_id)
            logger.info(f"Started MLflow run: {self.current_run.info.run_id}")
            
            return experiment_id
            
        except Exception as e:
            logger.error(f"Failed to start experiment: {str(e)}")
            raise
    
    def log_params(self, params: Dict[str, Any]):
        """
        Log hyperparameters to MLflow
        
        Args:
            params: Dictionary of parameters
        """
        try:
            if self.current_run is None:
                logger.warning("No active run. Starting new run.")
                self.start_experiment("default")
            
            # MLflow requires string values for params
            for key, value in params.items():
                mlflow.log_param(key, str(value))
            
            logger.info(f"Logged {len(params)} parameters to MLflow")
            
        except Exception as e:
            logger.error(f"Failed to log params: {str(e)}")
    
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """
        Log metrics to MLflow
        
        Args:
            metrics: Dictionary of metrics
            step: Optional step number for time series metrics
        """
        try:
            if self.current_run is None:
                logger.warning("No active run. Starting new run.")
                self.start_experiment("default")
            
            for key, value in metrics.items():
                mlflow.log_metric(key, value, step=step)
            
            logger.info(f"Logged {len(metrics)} metrics to MLflow")
            
        except Exception as e:
            logger.error(f"Failed to log metrics: {str(e)}")
    
    def log_artifact(self, artifact: Any, artifact_name: str):
        """
        Log model or artifact to MLflow
        
        Args:
            artifact: Model or artifact to log
            artifact_name: Name for the artifact
        """
        try:
            if self.current_run is None:
                logger.warning("No active run. Starting new run.")
                self.start_experiment("default")
            
            # Log sklearn models
            if hasattr(artifact, "predict") and hasattr(artifact, "fit"):
                mlflow.sklearn.log_model(artifact, artifact_name)
                logger.info(f"Logged sklearn model: {artifact_name}")
            
            # Log TensorFlow/Keras models
            elif hasattr(artifact, "predict") and hasattr(artifact, "compile"):
                mlflow.tensorflow.log_model(artifact, artifact_name)
                logger.info(f"Logged TensorFlow model: {artifact_name}")
            
            else:
                logger.warning(f"Unsupported artifact type: {type(artifact)}")
            
        except Exception as e:
            logger.error(f"Failed to log artifact: {str(e)}")
    
    def log_figure(self, figure: Any, filename: str):
        """
        Log matplotlib/plotly figure to MLflow
        
        Args:
            figure: Matplotlib or plotly figure
            filename: Filename for the figure
        """
        try:
            if self.current_run is None:
                logger.warning("No active run. Starting new run.")
                self.start_experiment("default")
            
            mlflow.log_figure(figure, filename)
            logger.info(f"Logged figure: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to log figure: {str(e)}")
    
    def end_experiment(self):
        """End the current MLflow run"""
        try:
            if self.current_run is not None:
                mlflow.end_run()
                logger.info(f"Ended MLflow run: {self.current_run.info.run_id}")
                self.current_run = None
            
        except Exception as e:
            logger.error(f"Failed to end experiment: {str(e)}")
    
    def list_experiments(self) -> list:
        """
        List all MLflow experiments
        
        Returns:
            List of experiment dictionaries
        """
        try:
            experiments = mlflow.search_experiments()
            
            results = []
            for exp in experiments:
                results.append({
                    "experiment_id": exp.experiment_id,
                    "name": exp.name,
                    "artifact_location": exp.artifact_location,
                    "lifecycle_stage": exp.lifecycle_stage
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to list experiments: {str(e)}")
            return []
    
    def get_best_run(self, experiment_name: str, metric: str = "accuracy") -> Optional[Dict[str, Any]]:
        """
        Get the best run from an experiment based on a metric
        
        Args:
            experiment_name: Name of the experiment
            metric: Metric to optimize (default: accuracy)
        
        Returns:
            Best run information
        """
        try:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                logger.warning(f"Experiment not found: {experiment_name}")
                return None
            
            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                order_by=[f"metrics.{metric} DESC"],
                max_results=1
            )
            
            if len(runs) == 0:
                return None
            
            best_run = runs.iloc[0]
            return {
                "run_id": best_run["run_id"],
                "metrics": best_run[[col for col in best_run.index if col.startswith("metrics.")]].to_dict(),
                "params": best_run[[col for col in best_run.index if col.startswith("params.")]].to_dict()
            }
            
        except Exception as e:
            logger.error(f"Failed to get best run: {str(e)}")
            return None
    
    def is_connected(self) -> bool:
        """Check if MLflow is connected"""
        try:
            mlflow.search_experiments()
            return True
        except:
            return False
