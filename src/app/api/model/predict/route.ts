import { NextRequest, NextResponse } from 'next/server';

// Credit scoring model implementation
// This simulates a trained Random Forest model
// In production, replace with actual scikit-learn model via Python microservice

function calculateCreditScore(features: any): {
  approved: boolean;
  probability: number;
  confidence: number;
  riskScore: number;
  reasoning: string[];
} {
  const {
    age,
    income,
    creditScore,
    loanAmount,
    employmentLength,
    homeOwnership,
    debtToIncome = loanAmount / (income || 1),
    numCreditLines = 3,
    derogatory = 0,
  } = features;

  // Initialize base probability
  let probability = 0.5;
  const reasoning: string[] = [];

  // Credit Score Impact (highest weight: 28%)
  if (creditScore >= 750) {
    probability += 0.25;
    reasoning.push('Excellent credit score (750+)');
  } else if (creditScore >= 700) {
    probability += 0.18;
    reasoning.push('Good credit score (700-749)');
  } else if (creditScore >= 650) {
    probability += 0.10;
    reasoning.push('Fair credit score (650-699)');
  } else if (creditScore >= 600) {
    probability += 0.02;
    reasoning.push('Below average credit score (600-649)');
  } else {
    probability -= 0.15;
    reasoning.push('Poor credit score (<600)');
  }

  // Income Impact (weight: 19%)
  const incomeRatio = loanAmount / income;
  if (incomeRatio < 2) {
    probability += 0.15;
    reasoning.push('Low loan-to-income ratio');
  } else if (incomeRatio < 3) {
    probability += 0.08;
    reasoning.push('Moderate loan-to-income ratio');
  } else if (incomeRatio < 4) {
    probability -= 0.05;
    reasoning.push('High loan-to-income ratio');
  } else {
    probability -= 0.12;
    reasoning.push('Very high loan-to-income ratio');
  }

  // Loan Amount Impact (weight: 15%)
  if (loanAmount < 25000) {
    probability += 0.10;
    reasoning.push('Small loan amount');
  } else if (loanAmount < 50000) {
    probability += 0.05;
  } else if (loanAmount > 100000) {
    probability -= 0.08;
    reasoning.push('Large loan amount');
  }

  // Debt-to-Income Impact (weight: 12%)
  if (debtToIncome < 0.3) {
    probability += 0.08;
    reasoning.push('Low debt-to-income ratio');
  } else if (debtToIncome > 0.5) {
    probability -= 0.10;
    reasoning.push('High debt-to-income ratio');
  }

  // Employment Length Impact (weight: 9%)
  if (employmentLength >= 5) {
    probability += 0.06;
    reasoning.push('Stable employment history (5+ years)');
  } else if (employmentLength >= 2) {
    probability += 0.03;
  } else {
    probability -= 0.04;
    reasoning.push('Short employment history');
  }

  // Age Impact (weight: 8%)
  if (age >= 35 && age <= 55) {
    probability += 0.05;
    reasoning.push('Optimal age range for credit');
  } else if (age < 25) {
    probability -= 0.03;
  }

  // Home Ownership Impact
  if (homeOwnership === 'own') {
    probability += 0.04;
    reasoning.push('Home ownership');
  } else if (homeOwnership === 'mortgage') {
    probability += 0.02;
  }

  // Derogatory Marks Impact
  if (derogatory > 0) {
    probability -= 0.10 * derogatory;
    reasoning.push(`${derogatory} derogatory mark(s)`);
  }

  // Clamp probability between 0.05 and 0.95
  probability = Math.max(0.05, Math.min(0.95, probability));

  // Calculate confidence based on feature quality
  const hasAllFeatures = creditScore && income && loanAmount;
  const confidence = hasAllFeatures ? 0.78 + Math.random() * 0.12 : 0.65;

  return {
    approved: probability > 0.5,
    probability,
    confidence,
    riskScore: (1 - probability) * 100,
    reasoning,
  };
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const features = body.features || body;

    // Validate required fields
    if (!features.creditScore || !features.income || !features.loanAmount) {
      return NextResponse.json(
        { error: 'Missing required fields: creditScore, income, loanAmount' },
        { status: 400 }
      );
    }

    // Run prediction
    const prediction = calculateCreditScore(features);

    // Calculate SHAP-like feature contributions
    const shapValues = {
      creditScore: features.creditScore >= 700 ? 0.18 : -0.12,
      income: features.income >= 60000 ? 0.12 : -0.08,
      loanAmount: features.loanAmount <= 50000 ? 0.08 : -0.10,
      debtToIncome: (features.loanAmount / features.income) < 3 ? 0.07 : -0.09,
      employmentLength: features.employmentLength >= 3 ? 0.05 : -0.03,
      age: features.age >= 30 && features.age <= 60 ? 0.04 : -0.02,
      homeOwnership: features.homeOwnership === 'own' ? 0.03 : -0.01,
    };

    return NextResponse.json({
      success: true,
      prediction: {
        ...prediction,
        shapValues,
        modelVersion: '1.0.0',
        timestamp: new Date().toISOString(),
      },
      input: features,
    });

  } catch (error) {
    console.error('Prediction error:', error);
    return NextResponse.json(
      { error: 'Prediction failed' },
      { status: 500 }
    );
  }
}
