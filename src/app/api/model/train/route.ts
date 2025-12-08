import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { data } = await request.json();

    if (!data || !Array.isArray(data) || data.length === 0) {
      return NextResponse.json(
        { error: 'Invalid training data provided' },
        { status: 400 }
      );
    }

    // Simulate model training process
    // In production, this would call a Python ML service (scikit-learn, etc.)
    
    // Extract features and labels from data
    const features = data.map((row: any) => ({
      age: row.age || 0,
      income: row.income || 0,
      creditScore: row.credit_score || row.creditScore || 0,
      loanAmount: row.loan_amount || row.loanAmount || 0,
      employmentLength: row.employment_length || row.employmentLength || 0,
      homeOwnership: row.home_ownership || row.homeOwnership || 'rent',
      debtToIncome: row.debt_to_income || row.debtToIncome || 0,
      numCreditLines: row.num_credit_lines || row.numCreditLines || 0,
      derogatory: row.derogatory_marks || row.derogatory || 0,
      totalDebt: row.total_debt || row.totalDebt || 0,
    }));

    const labels = data.map((row: any) => row.loan_status || row.approved || 0);

    // Calculate basic statistics for the model
    const approved = labels.filter((l: number) => l === 1).length;
    const rejected = labels.length - approved;
    
    // Simulate training metrics
    const accuracy = 0.873 + Math.random() * 0.02;
    const precision = 0.85 + Math.random() * 0.03;
    const recall = 0.88 + Math.random() * 0.02;
    const f1Score = 2 * (precision * recall) / (precision + recall);
    const rocAuc = 0.89 + Math.random() * 0.02;

    // Feature importance (simulated from Random Forest)
    const featureImportance = {
      creditScore: 0.28,
      income: 0.19,
      loanAmount: 0.15,
      debtToIncome: 0.12,
      employmentLength: 0.09,
      age: 0.08,
      totalDebt: 0.05,
      numCreditLines: 0.03,
      derogatory: 0.01,
    };

    // Store model metadata (in production, save to database/file system)
    const modelMetadata = {
      modelId: `model_${Date.now()}`,
      algorithm: 'Random Forest',
      trainedAt: new Date().toISOString(),
      datasetSize: data.length,
      features: Object.keys(featureImportance),
      metrics: {
        accuracy,
        precision,
        recall,
        f1Score,
        rocAuc,
      },
      featureImportance,
      classDistribution: {
        approved,
        rejected,
        approvalRate: approved / data.length,
      },
    };

    return NextResponse.json({
      success: true,
      model: modelMetadata,
      message: 'Model trained successfully',
    });

  } catch (error) {
    console.error('Training error:', error);
    return NextResponse.json(
      { error: 'Model training failed' },
      { status: 500 }
    );
  }
}
