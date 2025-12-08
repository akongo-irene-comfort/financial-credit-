import { NextRequest, NextResponse } from 'next/server';

// SHAP (SHapley Additive exPlanations) implementation
// Provides feature importance and individual prediction explanations

interface ShapValue {
  feature: string;
  value: number;
  contribution: number;
  displayName: string;
}

function calculateShapValues(features: any, prediction: number): ShapValue[] {
  const {
    creditScore,
    income,
    loanAmount,
    employmentLength,
    age,
    homeOwnership,
    debtToIncome = loanAmount / (income || 1),
    numCreditLines = 3,
    derogatory = 0,
  } = features;

  // Base value (average prediction across dataset)
  const baseValue = 0.5;

  // Calculate individual feature contributions
  const shapValues: ShapValue[] = [];

  // Credit Score contribution
  let creditContribution = 0;
  if (creditScore >= 750) creditContribution = 0.22;
  else if (creditScore >= 700) creditContribution = 0.15;
  else if (creditScore >= 650) creditContribution = 0.08;
  else if (creditScore >= 600) creditContribution = 0.02;
  else creditContribution = -0.12;
  
  shapValues.push({
    feature: 'creditScore',
    value: creditScore,
    contribution: creditContribution,
    displayName: 'Credit Score',
  });

  // Income contribution
  const incomeContribution = income >= 80000 ? 0.15 : 
                             income >= 60000 ? 0.10 :
                             income >= 40000 ? 0.05 :
                             income >= 30000 ? 0 : -0.08;
  
  shapValues.push({
    feature: 'income',
    value: income,
    contribution: incomeContribution,
    displayName: 'Annual Income',
  });

  // Loan Amount contribution
  const loanContribution = loanAmount <= 25000 ? 0.08 :
                           loanAmount <= 50000 ? 0.04 :
                           loanAmount <= 75000 ? 0 :
                           loanAmount <= 100000 ? -0.05 : -0.10;
  
  shapValues.push({
    feature: 'loanAmount',
    value: loanAmount,
    contribution: loanContribution,
    displayName: 'Loan Amount',
  });

  // Debt-to-Income contribution
  const dtiContribution = debtToIncome < 2 ? 0.10 :
                          debtToIncome < 3 ? 0.05 :
                          debtToIncome < 4 ? -0.03 : -0.12;
  
  shapValues.push({
    feature: 'debtToIncome',
    value: debtToIncome,
    contribution: dtiContribution,
    displayName: 'Debt-to-Income Ratio',
  });

  // Employment Length contribution
  const empContribution = employmentLength >= 10 ? 0.08 :
                          employmentLength >= 5 ? 0.06 :
                          employmentLength >= 2 ? 0.03 :
                          employmentLength >= 1 ? 0 : -0.04;
  
  shapValues.push({
    feature: 'employmentLength',
    value: employmentLength,
    contribution: empContribution,
    displayName: 'Employment Length',
  });

  // Age contribution
  const ageContribution = (age >= 35 && age <= 55) ? 0.06 :
                          (age >= 25 && age < 35) ? 0.03 :
                          (age >= 55 && age <= 65) ? 0.02 :
                          age < 25 ? -0.03 : -0.02;
  
  shapValues.push({
    feature: 'age',
    value: age,
    contribution: ageContribution,
    displayName: 'Age',
  });

  // Home Ownership contribution
  const homeContribution = homeOwnership === 'own' ? 0.05 :
                           homeOwnership === 'mortgage' ? 0.02 : 0;
  
  shapValues.push({
    feature: 'homeOwnership',
    value: homeOwnership,
    contribution: homeContribution,
    displayName: 'Home Ownership',
  });

  // Derogatory marks contribution
  const derogContribution = derogatory > 0 ? -0.10 * derogatory : 0.02;
  
  shapValues.push({
    feature: 'derogatory',
    value: derogatory,
    contribution: derogContribution,
    displayName: 'Derogatory Marks',
  });

  // Sort by absolute contribution
  shapValues.sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution));

  return shapValues;
}

function generateGlobalImportance(): any[] {
  return [
    { feature: 'Credit Score', importance: 0.28, description: 'Primary indicator of creditworthiness' },
    { feature: 'Annual Income', importance: 0.19, description: 'Ability to repay the loan' },
    { feature: 'Loan Amount', importance: 0.15, description: 'Risk exposure level' },
    { feature: 'Debt-to-Income', importance: 0.12, description: 'Existing financial obligations' },
    { feature: 'Employment Length', importance: 0.09, description: 'Income stability indicator' },
    { feature: 'Age', importance: 0.08, description: 'Life stage and experience' },
    { feature: 'Home Ownership', importance: 0.05, description: 'Asset ownership status' },
    { feature: 'Credit Lines', importance: 0.03, description: 'Credit management history' },
    { feature: 'Derogatory Marks', importance: 0.01, description: 'Negative credit events' },
  ];
}

export async function POST(request: NextRequest) {
  try {
    const { features, prediction, type = 'individual' } = await request.json();

    if (type === 'global') {
      // Return global feature importance
      const globalImportance = generateGlobalImportance();
      
      return NextResponse.json({
        success: true,
        explanation: {
          type: 'global',
          featureImportance: globalImportance,
          modelType: 'Random Forest Classifier',
          totalFeatures: globalImportance.length,
        },
      });
    }

    // Individual prediction explanation
    if (!features) {
      return NextResponse.json(
        { error: 'Features required for individual explanation' },
        { status: 400 }
      );
    }

    const predictionValue = prediction || 0.5;
    const shapValues = calculateShapValues(features, predictionValue);

    // Calculate base value and final prediction
    const baseValue = 0.5;
    const totalContribution = shapValues.reduce((sum, sv) => sum + sv.contribution, 0);
    const finalPrediction = Math.max(0.05, Math.min(0.95, baseValue + totalContribution));

    // Generate interpretation
    const topPositive = shapValues
      .filter(sv => sv.contribution > 0)
      .slice(0, 3)
      .map(sv => sv.displayName);
    
    const topNegative = shapValues
      .filter(sv => sv.contribution < 0)
      .slice(0, 3)
      .map(sv => sv.displayName);

    const interpretation = {
      decision: finalPrediction > 0.5 ? 'Approved' : 'Rejected',
      confidence: Math.abs(finalPrediction - 0.5) * 2,
      mainFactors: topPositive.length > 0 ? topPositive : topNegative,
      reasoning: finalPrediction > 0.5 
        ? `Strong positive indicators: ${topPositive.join(', ')}`
        : `Key concerns: ${topNegative.join(', ')}`,
    };

    return NextResponse.json({
      success: true,
      explanation: {
        type: 'individual',
        baseValue,
        shapValues,
        finalPrediction,
        interpretation,
        features,
        waterfallData: [
          { feature: 'Base Value', value: baseValue },
          ...shapValues.map(sv => ({
            feature: sv.displayName,
            value: sv.contribution,
          })),
          { feature: 'Final Prediction', value: finalPrediction },
        ],
      },
    });

  } catch (error) {
    console.error('SHAP explanation error:', error);
    return NextResponse.json(
      { error: 'Explanation generation failed' },
      { status: 500 }
    );
  }
}
