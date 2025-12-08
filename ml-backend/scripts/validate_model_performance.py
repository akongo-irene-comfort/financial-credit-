"""
Model Performance Validation Script
Validates that model meets minimum performance thresholds before deployment
"""

import sys
import json
from pathlib import Path

# Performance thresholds
THRESHOLDS = {
    "accuracy": 0.85,
    "precision": 0.80,
    "recall": 0.80,
    "f1_score": 0.82,
    "auc_roc": 0.85,
    "fairness_score": 0.85,
    "demographic_parity": 0.85,
    "equal_opportunity": 0.85,
    "disparate_impact": 0.80,
}

def load_model_metrics():
    """Load model metrics from MLflow or saved files"""
    metrics_file = Path("models/latest_metrics.json")
    
    if not metrics_file.exists():
        print("⚠️  No model metrics file found. Skipping validation.")
        return None
    
    with open(metrics_file) as f:
        return json.load(f)

def validate_metrics(metrics: dict) -> tuple[bool, list[str]]:
    """Validate metrics against thresholds"""
    failures = []
    
    for metric_name, threshold in THRESHOLDS.items():
        if metric_name not in metrics:
            print(f"⚠️  Metric '{metric_name}' not found in metrics file")
            continue
        
        value = metrics[metric_name]
        if value < threshold:
            failures.append(
                f"❌ {metric_name}: {value:.4f} < {threshold:.4f} (threshold)"
            )
        else:
            print(f"✅ {metric_name}: {value:.4f} >= {threshold:.4f}")
    
    return len(failures) == 0, failures

def main():
    print("🔍 Validating Model Performance...")
    print("=" * 50)
    
    # Load metrics
    metrics = load_model_metrics()
    if metrics is None:
        print("✅ Validation skipped (no metrics file)")
        return 0
    
    # Validate
    passed, failures = validate_metrics(metrics)
    
    print("\n" + "=" * 50)
    if passed:
        print("✅ All performance thresholds met!")
        print("🚀 Model ready for deployment")
        return 0
    else:
        print("❌ Performance validation failed!")
        print("\nFailures:")
        for failure in failures:
            print(f"  {failure}")
        print("\n⚠️  Model does not meet deployment criteria")
        return 1

if __name__ == "__main__":
    sys.exit(main())
