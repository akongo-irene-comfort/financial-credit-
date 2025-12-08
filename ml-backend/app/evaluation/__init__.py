"""Evaluation modules initialization"""

from .metrics import ModelEvaluator
from .fairness import FairnessAnalyzer

__all__ = [
    "ModelEvaluator",
    "FairnessAnalyzer"
]
