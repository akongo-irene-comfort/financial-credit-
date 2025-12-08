"""
Comprehensive Fairness Analysis
Includes: Demographic Parity, Equal Opportunity, Disparate Impact (80% rule)
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class FairnessAnalyzer:
    """
    Fairness and bias analysis for credit scoring models
    
    Metrics:
    1. Demographic Parity: Equal approval rates across groups
    2. Equal Opportunity: Equal TPR (recall) across groups
    3. Disparate Impact: 80% rule compliance
    4. Statistical Parity Difference
    """
    
    def __init__(self):
        self.results = {}
    
    def analyze(
        self,
        data: List[Dict[str, Any]],
        predictions: List[int],
        sensitive_features: List[str] = ["gender", "age_group"]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive fairness analysis
        
        Args:
            data: Original data with sensitive features
            predictions: Model predictions
            sensitive_features: List of sensitive feature names
        
        Returns:
            Fairness analysis results
        """
        try:
            df = pd.DataFrame(data)
            df["prediction"] = predictions
            
            # Get true labels
            target_col = "loan_status" if "loan_status" in df.columns else "approved"
            if target_col in df.columns:
                df["actual"] = df[target_col]
            else:
                df["actual"] = predictions  # Fallback
            
            results = {
                "overall_score": 0.0,
                "demographic_parity": {},
                "equal_opportunity": {},
                "disparate_impact": {},
                "statistical_parity": {},
                "recommendations": []
            }
            
            # Analyze each sensitive feature
            fairness_scores = []
            
            for feature in sensitive_features:
                if feature not in df.columns:
                    logger.warning(f"Sensitive feature '{feature}' not found in data")
                    continue
                
                # Demographic Parity (approval rates)
                dp_results = self._demographic_parity(df, feature)
                results["demographic_parity"][feature] = dp_results
                fairness_scores.append(dp_results["fairness_score"])
                
                # Equal Opportunity (TPR equality)
                eo_results = self._equal_opportunity(df, feature)
                results["equal_opportunity"][feature] = eo_results
                fairness_scores.append(eo_results["fairness_score"])
                
                # Disparate Impact (80% rule)
                di_results = self._disparate_impact(df, feature)
                results["disparate_impact"][feature] = di_results
                fairness_scores.append(di_results["fairness_score"])
                
                # Statistical Parity Difference
                sp_results = self._statistical_parity(df, feature)
                results["statistical_parity"][feature] = sp_results
            
            # Overall fairness score
            if fairness_scores:
                results["overall_score"] = float(np.mean(fairness_scores))
            
            # Generate recommendations
            results["recommendations"] = self._generate_recommendations(results)
            
            logger.info(f"Fairness analysis complete. Overall score: {results['overall_score']:.2f}")
            
            return results
            
        except Exception as e:
            logger.error(f"Fairness analysis error: {str(e)}")
            raise
    
    def _demographic_parity(self, df: pd.DataFrame, feature: str) -> Dict[str, Any]:
        """
        Calculate demographic parity (equal approval rates)
        
        Args:
            df: DataFrame with predictions and sensitive features
            feature: Sensitive feature name
        
        Returns:
            Demographic parity results
        """
        groups = df.groupby(feature)
        approval_rates = groups["prediction"].mean()
        
        # Calculate parity difference
        max_rate = approval_rates.max()
        min_rate = approval_rates.min()
        parity_diff = max_rate - min_rate
        
        # Fairness score (0-100): lower difference = higher fairness
        fairness_score = max(0, 100 - (parity_diff * 100))
        
        return {
            "approval_rates": approval_rates.to_dict(),
            "max_rate": float(max_rate),
            "min_rate": float(min_rate),
            "parity_difference": float(parity_diff),
            "fairness_score": float(fairness_score),
            "is_fair": parity_diff < 0.1  # Within 10% difference
        }
    
    def _equal_opportunity(self, df: pd.DataFrame, feature: str) -> Dict[str, Any]:
        """
        Calculate equal opportunity (equal TPR across groups)
        
        Args:
            df: DataFrame with predictions, actual labels, and sensitive features
            feature: Sensitive feature name
        
        Returns:
            Equal opportunity results
        """
        # TPR = TP / (TP + FN)
        groups = df.groupby(feature)
        
        tpr_by_group = {}
        for group_name, group_df in groups:
            if len(group_df) == 0:
                continue
            
            # Only consider positive class (approved loans)
            positive_samples = group_df[group_df["actual"] == 1]
            if len(positive_samples) == 0:
                tpr_by_group[group_name] = 0.0
            else:
                tp = ((positive_samples["prediction"] == 1) & (positive_samples["actual"] == 1)).sum()
                tpr = tp / len(positive_samples)
                tpr_by_group[group_name] = float(tpr)
        
        # Calculate TPR difference
        if tpr_by_group:
            max_tpr = max(tpr_by_group.values())
            min_tpr = min(tpr_by_group.values())
            tpr_diff = max_tpr - min_tpr
        else:
            max_tpr = min_tpr = tpr_diff = 0.0
        
        # Fairness score
        fairness_score = max(0, 100 - (tpr_diff * 100))
        
        return {
            "tpr_by_group": tpr_by_group,
            "max_tpr": float(max_tpr),
            "min_tpr": float(min_tpr),
            "tpr_difference": float(tpr_diff),
            "fairness_score": float(fairness_score),
            "is_fair": tpr_diff < 0.1
        }
    
    def _disparate_impact(self, df: pd.DataFrame, feature: str) -> Dict[str, Any]:
        """
        Calculate disparate impact (80% rule)
        
        The 80% rule: Selection rate for protected group should be at least 80% 
        of the selection rate for the most favored group
        
        Args:
            df: DataFrame with predictions and sensitive features
            feature: Sensitive feature name
        
        Returns:
            Disparate impact results
        """
        groups = df.groupby(feature)
        approval_rates = groups["prediction"].mean()
        
        if len(approval_rates) < 2:
            return {
                "approval_rates": approval_rates.to_dict(),
                "disparate_impact_ratio": 1.0,
                "passes_80_rule": True,
                "fairness_score": 100.0
            }
        
        # Disparate impact ratio = min_rate / max_rate
        max_rate = approval_rates.max()
        min_rate = approval_rates.min()
        
        if max_rate == 0:
            di_ratio = 1.0
        else:
            di_ratio = min_rate / max_rate
        
        # 80% rule compliance
        passes_80_rule = di_ratio >= 0.8
        
        # Fairness score based on how close to 1.0 (perfect parity)
        fairness_score = min(100, di_ratio * 100)
        
        return {
            "approval_rates": approval_rates.to_dict(),
            "disparate_impact_ratio": float(di_ratio),
            "passes_80_rule": passes_80_rule,
            "fairness_score": float(fairness_score),
            "threshold": 0.8
        }
    
    def _statistical_parity(self, df: pd.DataFrame, feature: str) -> Dict[str, Any]:
        """
        Calculate statistical parity difference
        
        Statistical Parity Difference = P(Y=1|A=a) - P(Y=1|A=b)
        
        Args:
            df: DataFrame with predictions and sensitive features
            feature: Sensitive feature name
        
        Returns:
            Statistical parity results
        """
        groups = df.groupby(feature)
        approval_rates = groups["prediction"].mean()
        
        # Calculate all pairwise differences
        group_names = list(approval_rates.index)
        pairwise_diffs = {}
        
        for i, group_a in enumerate(group_names):
            for group_b in group_names[i+1:]:
                diff = abs(approval_rates[group_a] - approval_rates[group_b])
                pairwise_diffs[f"{group_a}_vs_{group_b}"] = float(diff)
        
        # Maximum difference
        max_diff = max(pairwise_diffs.values()) if pairwise_diffs else 0.0
        
        return {
            "approval_rates": approval_rates.to_dict(),
            "pairwise_differences": pairwise_diffs,
            "max_difference": float(max_diff),
            "is_fair": max_diff < 0.1
        }
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """
        Generate fairness improvement recommendations
        
        Args:
            results: Fairness analysis results
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        overall_score = results["overall_score"]
        
        if overall_score < 70:
            recommendations.append("⚠️ Overall fairness score is low. Consider bias mitigation techniques.")
        
        # Check disparate impact
        for feature, di_results in results["disparate_impact"].items():
            if not di_results.get("passes_80_rule", True):
                recommendations.append(
                    f"❌ Disparate impact detected for {feature}. "
                    f"Ratio: {di_results['disparate_impact_ratio']:.2f} (should be ≥ 0.80)"
                )
        
        # Check demographic parity
        for feature, dp_results in results["demographic_parity"].items():
            if not dp_results.get("is_fair", True):
                recommendations.append(
                    f"⚠️ Demographic parity violation for {feature}. "
                    f"Approval rate difference: {dp_results['parity_difference']:.2%}"
                )
        
        # Check equal opportunity
        for feature, eo_results in results["equal_opportunity"].items():
            if not eo_results.get("is_fair", True):
                recommendations.append(
                    f"⚠️ Equal opportunity violation for {feature}. "
                    f"TPR difference: {eo_results['tpr_difference']:.2%}"
                )
        
        if not recommendations:
            recommendations.append("✅ Model passes all fairness checks. Continue monitoring.")
        else:
            recommendations.append(
                "💡 Consider: Reweighting samples, threshold optimization, or adversarial debiasing."
            )
        
        return recommendations
