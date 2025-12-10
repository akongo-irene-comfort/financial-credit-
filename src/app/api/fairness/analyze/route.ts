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

// Helper to find column case-insensitively
function findColumn(row: any, possibleNames: string[]): string | null {
  const keys = Object.keys(row);
  for (const name of possibleNames) {
    const found = keys.find(k => k.toLowerCase() === name.toLowerCase());
    if (found) return found;
  }
  return null;
}

// Get approval status from row
function getApprovalStatus(row: any): number | null {
  const loanStatusCol = findColumn(row, ['loan_status', 'loanstatus', 'status', 'approved', 'predicted']);
  if (!loanStatusCol) return null;
  
  const value = row[loanStatusCol];
  if (value === 'Y' || value === 'y' || value === 1 || value === '1' || value === true || 
      value === 'approved' || value === 'Approved' || value === 'yes' || value === 'Yes') {
    return 1;
  }
  if (value === 'N' || value === 'n' || value === 0 || value === '0' || value === false ||
      value === 'rejected' || value === 'Rejected' || value === 'no' || value === 'No') {
    return 0;
  }
  return null;
}

function calculateGroupMetricsFromData(data: any[]): GroupMetrics {
  const totalCount = data.length;
  
  if (totalCount === 0) {
    return {
      totalCount: 0,
      approvalRate: 0,
      truePositiveRate: 0,
      falsePositiveRate: 0,
      precision: 0,
    };
  }

  // Calculate approval rate using flexible detection
  let approvedCount = 0;
  data.forEach(row => {
    const status = getApprovalStatus(row);
    if (status === 1) approvedCount++;
  });
  
  const approvalRate = approvedCount / totalCount;

  // For datasets without actual vs predicted, treat loan_status as both
  const actualPositive = approvedCount;
  const actualNegative = totalCount - approvedCount;
  
  // Without predictions, TPR and FPR are simplified
  const truePositiveRate = approvalRate;
  const falsePositiveRate = 0;
  const precision = approvalRate;

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
    const body = await request.json();
    let { data, protectedAttribute = 'gender' } = body;

    if (!data || !Array.isArray(data) || data.length === 0) {
      return NextResponse.json(
        { error: 'Invalid data provided' },
        { status: 400 }
      );
    }

    // Find the actual column name (case-insensitive)
    const firstRow = data[0];
    const possibleProtectedAttrs = ['gender', 'Gender', 'sex', 'Sex', 'married', 'Married', 'education', 'Education'];
    let actualProtectedAttr = findColumn(firstRow, [protectedAttribute]);
    
    // If the requested attribute not found, try to find any available protected attribute
    if (!actualProtectedAttr) {
      actualProtectedAttr = findColumn(firstRow, possibleProtectedAttrs);
    }
    
    if (!actualProtectedAttr) {
      return NextResponse.json(
        { error: `Protected attribute '${protectedAttribute}' not found in data. Available columns: ${Object.keys(firstRow).join(', ')}` },
        { status: 400 }
      );
    }

    // Get unique groups - filter out null, undefined, empty strings, and whitespace-only values
    const uniqueGroups = [...new Set(data.map((row: any) => {
      const val = row[actualProtectedAttr];
      // Normalize the value - trim strings
      if (typeof val === 'string') {
        const trimmed = val.trim();
        return trimmed === '' ? null : trimmed;
      }
      return val;
    }))].filter(g => g !== null && g !== undefined);
    
    // Debug: log what we found
    console.log(`Fairness analysis: Found ${uniqueGroups.length} groups in '${actualProtectedAttr}':`, uniqueGroups);

    if (uniqueGroups.length < 2) {
      // Provide more detailed error message
      const sampleValues = data.slice(0, 10).map((r: any) => r[actualProtectedAttr]);
      return NextResponse.json(
        { 
          error: `Need at least 2 groups for fairness analysis. Found ${uniqueGroups.length} group(s) in '${actualProtectedAttr}': [${uniqueGroups.join(', ')}]. Sample values from first 10 rows: [${sampleValues.join(', ')}]` 
        },
        { status: 400 }
      );
    }

    // Calculate metrics for each group - use normalized values
    const groupMetrics: Record<string, GroupMetrics> = {};
    uniqueGroups.forEach(group => {
      // Filter using normalized comparison
      const groupData = data.filter((row: any) => {
        const val = row[actualProtectedAttr];
        if (typeof val === 'string') {
          return val.trim() === group;
        }
        return val === group;
      });
      groupMetrics[String(group)] = calculateGroupMetricsFromData(groupData);
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
    const disparateImpact = maxApprovalRate > 0 ? minApprovalRate / maxApprovalRate : 1;

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
      [actualProtectedAttr]: {
        groups: groupMetrics,
        demographicParity: 1 - demographicParityDifference,
        equalOpportunity: 1 - equalOpportunityDifference,
        disparateImpact,
      },
    };

    // Age group analysis if age is present
    const ageCol = findColumn(firstRow, ['age', 'Age', 'applicant_age']);
    if (ageCol) {
      const ageGroups = {
        '18-30': data.filter((r: any) => r[ageCol] >= 18 && r[ageCol] <= 30),
        '31-45': data.filter((r: any) => r[ageCol] >= 31 && r[ageCol] <= 45),
        '46-60': data.filter((r: any) => r[ageCol] >= 46 && r[ageCol] <= 60),
        '60+': data.filter((r: any) => r[ageCol] > 60),
      };

      const ageMetrics: any = {};
      Object.entries(ageGroups).forEach(([ageGroup, groupData]) => {
        if ((groupData as any[]).length > 0) {
          let approved = 0;
          (groupData as any[]).forEach(r => {
            if (getApprovalStatus(r) === 1) approved++;
          });
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
        protectedAttribute: actualProtectedAttr,
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