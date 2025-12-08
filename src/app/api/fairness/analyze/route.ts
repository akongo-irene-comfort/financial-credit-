import { NextRequest, NextResponse } from 'next/server';

// Fairness metrics calculation
// Implements demographic parity, equal opportunity, and disparate impact analysis

interface FairnessMetrics {
  demographicParity: number;
  equalOpportunity: number;
  disparateImpact: number;
  statisticalParity: number;
}

interface GroupMetrics {
  totalCount: number;
  approvalRate: number;
  truePositiveRate: number;
  falsePositiveRate: number;
  precision: number;
}

function calculateGroupMetrics(data: any[], groupKey: string, groupValue: any): GroupMetrics {
  const groupData = data.filter(row => row[groupKey] === groupValue);
  const totalCount = groupData.length;
  
  if (totalCount === 0) {
    return {
      totalCount: 0,
      approvalRate: 0,
      truePositiveRate: 0,
      falsePositiveRate: 0,
      precision: 0,
    };
  }

  const approved = groupData.filter(row => row.predicted === 1 || row.approved === 1);
  const approvalRate = approved.length / totalCount;

  // For true labels (ground truth)
  const actualPositive = groupData.filter(row => row.actual === 1 || row.loan_status === 1);
  const actualNegative = groupData.filter(row => row.actual === 0 || row.loan_status === 0);
  
  // True Positives: Correctly predicted as approved
  const truePositives = groupData.filter(
    row => (row.predicted === 1 || row.approved === 1) && (row.actual === 1 || row.loan_status === 1)
  ).length;
  
  // False Positives: Incorrectly predicted as approved
  const falsePositives = groupData.filter(
    row => (row.predicted === 1 || row.approved === 1) && (row.actual === 0 || row.loan_status === 0)
  ).length;

  const truePositiveRate = actualPositive.length > 0 ? truePositives / actualPositive.length : 0;
  const falsePositiveRate = actualNegative.length > 0 ? falsePositives / actualNegative.length : 0;
  const precision = approved.length > 0 ? truePositives / approved.length : 0;

  return {
    totalCount,
    approvalRate,
    truePositiveRate,
    falsePositiveRate,
    precision,
  };
}

function calculateFairnessScore(metrics: any): number {
  // Composite fairness score (0-100)
  // Higher is better (more fair)
  
  const dpScore = Math.max(0, 100 - Math.abs(metrics.demographicParityDifference) * 100);
  const eoScore = Math.max(0, 100 - Math.abs(metrics.equalOpportunityDifference) * 100);
  const diScore = metrics.disparateImpact >= 0.8 && metrics.disparateImpact <= 1.25 ? 100 : 
                   Math.max(0, 100 - Math.abs(1 - metrics.disparateImpact) * 100);
  
  return (dpScore + eoScore + diScore) / 3;
}

export async function POST(request: NextRequest) {
  try {
    const { data, protectedAttribute = 'gender' } = await request.json();

    if (!data || !Array.isArray(data) || data.length === 0) {
      return NextResponse.json(
        { error: 'Invalid data provided' },
        { status: 400 }
      );
    }

    // Get unique groups
    const uniqueGroups = [...new Set(data.map((row: any) => row[protectedAttribute]))];
    
    if (uniqueGroups.length < 2) {
      return NextResponse.json(
        { error: 'Need at least 2 groups for fairness analysis' },
        { status: 400 }
      );
    }

    // Calculate metrics for each group
    const groupMetrics: Record<string, GroupMetrics> = {};
    uniqueGroups.forEach(group => {
      groupMetrics[String(group)] = calculateGroupMetrics(data, protectedAttribute, group);
    });

    // Demographic Parity: Difference in approval rates
    const approvalRates = Object.values(groupMetrics).map(m => m.approvalRate);
    const maxApprovalRate = Math.max(...approvalRates);
    const minApprovalRate = Math.min(...approvalRates);
    const demographicParityDifference = maxApprovalRate - minApprovalRate;

    // Equal Opportunity: Difference in TPR (True Positive Rates)
    const tprValues = Object.values(groupMetrics).map(m => m.truePositiveRate);
    const maxTPR = Math.max(...tprValues);
    const minTPR = Math.min(...tprValues);
    const equalOpportunityDifference = maxTPR - minTPR;

    // Disparate Impact: Ratio of approval rates (min/max)
    // Should be >= 0.8 (80% rule)
    const disparateImpact = minApprovalRate / (maxApprovalRate || 1);

    // Statistical Parity Difference
    const avgApprovalRate = approvalRates.reduce((a, b) => a + b, 0) / approvalRates.length;
    const statisticalParityDifference = Math.max(
      ...approvalRates.map(rate => Math.abs(rate - avgApprovalRate))
    );

    // Calculate overall fairness score
    const fairnessScore = calculateFairnessScore({
      demographicParityDifference,
      equalOpportunityDifference,
      disparateImpact,
    });

    // Analyze bias by additional attributes if present
    const biasAnalysis: any = {
      [protectedAttribute]: {
        groups: groupMetrics,
        demographicParity: 1 - demographicParityDifference,
        equalOpportunity: 1 - equalOpportunityDifference,
        disparateImpact,
      },
    };

    // Age group analysis if age is present
    if (data[0].age) {
      const ageGroups = {
        '18-30': data.filter((r: any) => r.age >= 18 && r.age <= 30),
        '31-45': data.filter((r: any) => r.age >= 31 && r.age <= 45),
        '46-60': data.filter((r: any) => r.age >= 46 && r.age <= 60),
        '60+': data.filter((r: any) => r.age > 60),
      };

      const ageMetrics: any = {};
      Object.entries(ageGroups).forEach(([ageGroup, groupData]) => {
        if ((groupData as any[]).length > 0) {
          const approved = (groupData as any[]).filter(
            r => r.predicted === 1 || r.approved === 1
          ).length;
          ageMetrics[ageGroup] = {
            count: (groupData as any[]).length,
            approvalRate: approved / (groupData as any[]).length,
          };
        }
      });

      biasAnalysis.age = {
        groups: ageMetrics,
      };
    }

    // Generate recommendations
    const recommendations: string[] = [];
    
    if (disparateImpact < 0.8) {
      recommendations.push('Disparate impact detected: Approval rate ratio is below 80% threshold');
      recommendations.push('Consider reviewing feature selection and model training data for bias');
    }
    
    if (demographicParityDifference > 0.1) {
      recommendations.push('Significant demographic parity gap detected (>10%)');
      recommendations.push('Implement fairness constraints during model training');
    }
    
    if (equalOpportunityDifference > 0.1) {
      recommendations.push('Equal opportunity violation: Different TPR across groups');
      recommendations.push('Apply post-processing techniques to equalize TPR');
    }

    if (recommendations.length === 0) {
      recommendations.push('Model shows acceptable fairness metrics across protected groups');
      recommendations.push('Continue monitoring for fairness in production');
    }

    return NextResponse.json({
      success: true,
      fairness: {
        overallScore: fairnessScore,
        metrics: {
          demographicParity: 1 - demographicParityDifference,
          demographicParityDifference,
          equalOpportunity: 1 - equalOpportunityDifference,
          equalOpportunityDifference,
          disparateImpact,
          disparateImpactRatio: disparateImpact,
          statisticalParity: 1 - statisticalParityDifference,
        },
        groupMetrics,
        biasAnalysis,
        recommendations,
        protectedAttribute,
        complianceStatus: {
          '80PercentRule': disparateImpact >= 0.8,
          demographicParity: demographicParityDifference <= 0.1,
          equalOpportunity: equalOpportunityDifference <= 0.1,
        },
      },
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    console.error('Fairness analysis error:', error);
    return NextResponse.json(
      { error: 'Fairness analysis failed' },
      { status: 500 }
    );
  }
}
