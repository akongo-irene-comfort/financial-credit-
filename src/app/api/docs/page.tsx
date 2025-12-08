import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Code, Server, Shield, Sparkles } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function APIDocsPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-12 max-w-5xl">
        {/* Header */}
        <div className="mb-12">
          <Link href="/dashboard">
            <Button variant="outline" className="mb-4">
              ← Back to Dashboard
            </Button>
          </Link>
          <h1 className="text-4xl font-bold mb-4">Credit Scoring API Documentation</h1>
          <p className="text-xl text-muted-foreground">
            Complete API reference for the credit-worthiness model, fairness analysis, and explainability endpoints
          </p>
        </div>

        {/* Quick Links */}
        <div className="grid gap-4 md:grid-cols-4 mb-12">
          <a href="#predict" className="p-4 rounded-lg border hover:bg-muted/50 transition-colors">
            <Server className="h-6 w-6 mb-2 text-primary" />
            <h3 className="font-semibold">Predictions</h3>
          </a>
          <a href="#train" className="p-4 rounded-lg border hover:bg-muted/50 transition-colors">
            <Code className="h-6 w-6 mb-2 text-primary" />
            <h3 className="font-semibold">Training</h3>
          </a>
          <a href="#fairness" className="p-4 rounded-lg border hover:bg-muted/50 transition-colors">
            <Shield className="h-6 w-6 mb-2 text-primary" />
            <h3 className="font-semibold">Fairness</h3>
          </a>
          <a href="#shap" className="p-4 rounded-lg border hover:bg-muted/50 transition-colors">
            <Sparkles className="h-6 w-6 mb-2 text-primary" />
            <h3 className="font-semibold">SHAP</h3>
          </a>
        </div>

        {/* Base URL */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Base URL</CardTitle>
          </CardHeader>
          <CardContent>
            <code className="block p-4 rounded-lg bg-muted font-mono text-sm">
              https://your-domain.com/api
            </code>
            <p className="text-sm text-muted-foreground mt-2">
              All endpoints are relative to this base URL. In development: <code>http://localhost:3000/api</code>
            </p>
          </CardContent>
        </Card>

        {/* Model Prediction Endpoint */}
        <Card className="mb-8" id="predict">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Server className="h-5 w-5" />
              Credit Score Prediction
            </CardTitle>
            <CardDescription>Predict loan approval probability for an applicant</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium mb-2">Endpoint</p>
              <code className="block p-3 rounded-lg bg-muted font-mono text-sm">
                POST /api/model/predict
              </code>
            </div>

            <div>
              <p className="text-sm font-medium mb-2">Request Body</p>
              <pre className="p-4 rounded-lg bg-muted font-mono text-xs overflow-x-auto">
{`{
  "features": {
    "age": 35,
    "income": 75000,
    "creditScore": 720,
    "loanAmount": 50000,
    "employmentLength": 5,
    "homeOwnership": "rent",
    "debtToIncome": 0.4,        // Optional
    "numCreditLines": 3,        // Optional
    "derogatory": 0             // Optional
  }
}`}
              </pre>
            </div>

            <div>
              <p className="text-sm font-medium mb-2">Response</p>
              <pre className="p-4 rounded-lg bg-muted font-mono text-xs overflow-x-auto">
{`{
  "success": true,
  "prediction": {
    "approved": true,
    "probability": 0.73,
    "confidence": 0.85,
    "riskScore": 27.0,
    "reasoning": [
      "Good credit score (700-749)",
      "Low loan-to-income ratio",
      "Stable employment history (5+ years)"
    ],
    "shapValues": {
      "creditScore": 0.18,
      "income": 0.12,
      "loanAmount": -0.10,
      // ... other features
    },
    "modelVersion": "1.0.0",
    "timestamp": "2025-12-08T10:30:00.000Z"
  },
  "input": { /* echoed input features */ }
}`}
              </pre>
            </div>

            <div>
              <p className="text-sm font-medium mb-2">Example cURL</p>
              <pre className="p-4 rounded-lg bg-muted font-mono text-xs overflow-x-auto">
{`curl -X POST http://localhost:3000/api/model/predict \\
  -H "Content-Type: application/json" \\
  -d '{
    "features": {
      "age": 35,
      "income": 75000,
      "creditScore": 720,
      "loanAmount": 50000,
      "employmentLength": 5,
      "homeOwnership": "rent"
    }
  }'`}
              </pre>
            </div>
          </CardContent>
        </Card>

        {/* Model Training Endpoint */}
        <Card className="mb-8" id="train">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Code className="h-5 w-5" />
              Model Training
            </CardTitle>
            <CardDescription>Train credit scoring model on new data</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium mb-2">Endpoint</p>
              <code className="block p-3 rounded-lg bg-muted font-mono text-sm">
                POST /api/model/train
              </code>
            </div>

            <div>
              <p className="text-sm font-medium mb-2">Request Body</p>
              <pre className="p-4 rounded-lg bg-muted font-mono text-xs overflow-x-auto">
{`{
  "data": [
    {
      "age": 35,
      "income": 75000,
      "credit_score": 720,
      "loan_amount": 50000,
      "employment_length": 5,
      "home_ownership": "rent",
      "debt_to_income": 0.4,
      "num_credit_lines": 3,
      "derogatory_marks": 0,
      "total_debt": 30000,
      "loan_status": 1  // 1 = approved, 0 = rejected
    },
    // ... more training samples
  ]
}`}
              </pre>
            </div>

            <div>
              <p className="text-sm font-medium mb-2">Response</p>
              <pre className="p-4 rounded-lg bg-muted font-mono text-xs overflow-x-auto">
{`{
  "success": true,
  "model": {
    "modelId": "model_1701234567890",
    "algorithm": "Random Forest",
    "trainedAt": "2025-12-08T10:30:00.000Z",
    "datasetSize": 5000,
    "features": ["creditScore", "income", "loanAmount", ...],
    "metrics": {
      "accuracy": 0.873,
      "precision": 0.85,
      "recall": 0.88,
      "f1Score": 0.865,
      "rocAuc": 0.89
    },
    "featureImportance": {
      "creditScore": 0.28,
      "income": 0.19,
      "loanAmount": 0.15,
      // ... other features
    },
    "classDistribution": {
      "approved": 3200,
      "rejected": 1800,
      "approvalRate": 0.64
    }
  },
  "message": "Model trained successfully"
}`}
              </pre>
            </div>
          </CardContent>
        </Card>

        {/* Fairness Analysis Endpoint */}
        <Card className="mb-8" id="fairness">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Fairness Analysis
            </CardTitle>
            <CardDescription>Conduct bias and disparate impact analysis</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium mb-2">Endpoint</p>
              <code className="block p-3 rounded-lg bg-muted font-mono text-sm">
                POST /api/fairness/analyze
              </code>
            </div>

            <div>
              <p className="text-sm font-medium mb-2">Request Body</p>
              <pre className="p-4 rounded-lg bg-muted font-mono text-xs overflow-x-auto">
{`{
  "data": [
    {
      "gender": "male",
      "age": 35,
      "predicted": 1,      // Model prediction
      "actual": 1,         // Ground truth
      "approved": 1,       // Alias for predicted
      "loan_status": 1     // Alias for actual
    },
    // ... more samples with predictions
  ],
  "protectedAttribute": "gender"  // Can be "gender", "age", etc.
}`}
              </pre>
            </div>

            <div>
              <p className="text-sm font-medium mb-2">Response</p>
              <pre className="p-4 rounded-lg bg-muted font-mono text-xs overflow-x-auto">
{`{
  "success": true,
  "fairness": {
    "overallScore": 88.6,
    "metrics": {
      "demographicParity": 0.92,
      "demographicParityDifference": 0.08,
      "equalOpportunity": 0.88,
      "equalOpportunityDifference": 0.12,
      "disparateImpact": 0.85,
      "disparateImpactRatio": 0.85,
      "statisticalParity": 0.91
    },
    "groupMetrics": {
      "male": {
        "totalCount": 2800,
        "approvalRate": 0.712,
        "truePositiveRate": 0.82,
        "falsePositiveRate": 0.15,
        "precision": 0.87
      },
      "female": {
        "totalCount": 2200,
        "approvalRate": 0.658,
        "truePositiveRate": 0.79,
        "falsePositiveRate": 0.18,
        "precision": 0.84
      }
    },
    "biasAnalysis": {
      "gender": { /* detailed analysis */ },
      "age": { /* age group analysis if present */ }
    },
    "recommendations": [
      "Disparate impact detected: Approval rate ratio is below 80% threshold",
      "Consider reviewing feature selection and model training data for bias"
    ],
    "complianceStatus": {
      "80PercentRule": true,
      "demographicParity": true,
      "equalOpportunity": false
    },
    "protectedAttribute": "gender"
  },
  "timestamp": "2025-12-08T10:30:00.000Z"
}`}
              </pre>
            </div>

            <div className="rounded-lg border bg-muted/50 p-4">
              <h4 className="font-medium text-sm mb-2">Key Metrics Explained</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li><strong>Demographic Parity:</strong> Similar approval rates across groups (closer to 1.0 is better)</li>
                <li><strong>Equal Opportunity:</strong> Similar true positive rates across groups</li>
                <li><strong>Disparate Impact:</strong> Ratio of approval rates (should be ≥ 0.8 for 80% rule)</li>
                <li><strong>Statistical Parity:</strong> Measures deviation from average approval rate</li>
              </ul>
            </div>
          </CardContent>
        </Card>

        {/* SHAP Explainability Endpoint */}
        <Card className="mb-8" id="shap">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5" />
              SHAP Explainability
            </CardTitle>
            <CardDescription>Generate feature importance and prediction explanations</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium mb-2">Endpoint</p>
              <code className="block p-3 rounded-lg bg-muted font-mono text-sm">
                POST /api/shap/explain
              </code>
            </div>

            <div>
              <p className="text-sm font-medium mb-2">Global Explanation Request</p>
              <pre className="p-4 rounded-lg bg-muted font-mono text-xs overflow-x-auto">
{`{
  "type": "global"
}`}
              </pre>
            </div>

            <div>
              <p className="text-sm font-medium mb-2">Global Explanation Response</p>
              <pre className="p-4 rounded-lg bg-muted font-mono text-xs overflow-x-auto">
{`{
  "success": true,
  "explanation": {
    "type": "global",
    "featureImportance": [
      {
        "feature": "Credit Score",
        "importance": 0.28,
        "description": "Primary indicator of creditworthiness"
      },
      {
        "feature": "Annual Income",
        "importance": 0.19,
        "description": "Ability to repay the loan"
      },
      // ... more features
    ],
    "modelType": "Random Forest Classifier",
    "totalFeatures": 9
  }
}`}
              </pre>
            </div>

            <div>
              <p className="text-sm font-medium mb-2">Individual Explanation Request</p>
              <pre className="p-4 rounded-lg bg-muted font-mono text-xs overflow-x-auto">
{`{
  "type": "individual",
  "features": {
    "age": 35,
    "income": 75000,
    "creditScore": 720,
    "loanAmount": 50000,
    "employmentLength": 5,
    "homeOwnership": "rent"
  },
  "prediction": 0.73  // Optional, from /api/model/predict
}`}
              </pre>
            </div>

            <div>
              <p className="text-sm font-medium mb-2">Individual Explanation Response</p>
              <pre className="p-4 rounded-lg bg-muted font-mono text-xs overflow-x-auto">
{`{
  "success": true,
  "explanation": {
    "type": "individual",
    "baseValue": 0.5,
    "shapValues": [
      {
        "feature": "creditScore",
        "value": 720,
        "contribution": 0.15,
        "displayName": "Credit Score"
      },
      // ... other features
    ],
    "finalPrediction": 0.73,
    "interpretation": {
      "decision": "Approved",
      "confidence": 0.85,
      "mainFactors": ["Credit Score", "Annual Income", "Employment Length"],
      "reasoning": "Strong positive indicators: Credit Score, Annual Income, Employment Length"
    },
    "features": { /* echoed input */ },
    "waterfallData": [
      { "feature": "Base Value", "value": 0.5 },
      { "feature": "Credit Score", "value": 0.15 },
      // ... cumulative contributions
      { "feature": "Final Prediction", "value": 0.73 }
    ]
  }
}`}
              </pre>
            </div>
          </CardContent>
        </Card>

        {/* Error Responses */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Error Responses</CardTitle>
            <CardDescription>Standard error format across all endpoints</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium mb-2">400 Bad Request</p>
              <pre className="p-4 rounded-lg bg-muted font-mono text-xs overflow-x-auto">
{`{
  "error": "Missing required fields: creditScore, income, loanAmount"
}`}
              </pre>
            </div>

            <div>
              <p className="text-sm font-medium mb-2">500 Internal Server Error</p>
              <pre className="p-4 rounded-lg bg-muted font-mono text-xs overflow-x-auto">
{`{
  "error": "Prediction failed"
}`}
              </pre>
            </div>
          </CardContent>
        </Card>

        {/* Integration Examples */}
        <Card>
          <CardHeader>
            <CardTitle>Integration Examples</CardTitle>
            <CardDescription>Common use cases and workflows</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <h4 className="font-medium mb-2">Complete Loan Application Flow</h4>
              <pre className="p-4 rounded-lg bg-muted font-mono text-xs overflow-x-auto">
{`// 1. Get prediction
const predictionResponse = await fetch('/api/model/predict', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ features: applicantData })
});
const { prediction } = await predictionResponse.json();

// 2. Get explanation
const explainResponse = await fetch('/api/shap/explain', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    type: 'individual',
    features: applicantData,
    prediction: prediction.probability
  })
});
const { explanation } = await explainResponse.json();

// 3. Display results with reasoning
console.log(\`Decision: \${prediction.approved ? 'Approved' : 'Rejected'}\`);
console.log(\`Probability: \${prediction.probability}\`);
console.log(\`Key Factors: \${explanation.interpretation.mainFactors.join(', ')}\`);`}
              </pre>
            </div>

            <div>
              <h4 className="font-medium mb-2">Batch Fairness Audit</h4>
              <pre className="p-4 rounded-lg bg-muted font-mono text-xs overflow-x-auto">
{`// Analyze fairness on batch predictions
const fairnessResponse = await fetch('/api/fairness/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    data: batchPredictions,  // Array of predictions with demographics
    protectedAttribute: 'gender'
  })
});
const { fairness } = await fairnessResponse.json();

// Check compliance
if (!fairness.complianceStatus['80PercentRule']) {
  console.warn('Disparate impact detected!');
  console.log('Recommendations:', fairness.recommendations);
}`}
              </pre>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
