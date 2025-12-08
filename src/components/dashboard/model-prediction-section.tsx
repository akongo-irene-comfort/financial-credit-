"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { CheckCircle2, XCircle, Brain, Loader2 } from "lucide-react"
import { Progress } from "@/components/ui/progress"

export default function ModelPredictionSection() {
  const [formData, setFormData] = useState({
    age: "",
    income: "",
    creditScore: "",
    loanAmount: "",
    employmentLength: "",
    homeOwnership: "rent"
  })
  const [prediction, setPrediction] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handlePredict = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch('/api/model/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          features: {
            age: parseFloat(formData.age),
            income: parseFloat(formData.income),
            creditScore: parseFloat(formData.creditScore),
            loanAmount: parseFloat(formData.loanAmount),
            employmentLength: parseFloat(formData.employmentLength),
            homeOwnership: formData.homeOwnership,
          }
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Prediction failed')
      }

      setPrediction(data.prediction)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Prediction failed')
      console.error('Prediction error:', err)
    } finally {
      setLoading(false)
    }
  }

  const updateField = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Loan Application Input</CardTitle>
          <CardDescription>Enter applicant details for credit scoring prediction</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="age">Age</Label>
            <Input
              id="age"
              type="number"
              placeholder="e.g., 35"
              value={formData.age}
              onChange={(e) => updateField("age", e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="income">Annual Income ($)</Label>
            <Input
              id="income"
              type="number"
              placeholder="e.g., 75000"
              value={formData.income}
              onChange={(e) => updateField("income", e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="creditScore">Credit Score</Label>
            <Input
              id="creditScore"
              type="number"
              placeholder="e.g., 720"
              value={formData.creditScore}
              onChange={(e) => updateField("creditScore", e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="loanAmount">Requested Loan Amount ($)</Label>
            <Input
              id="loanAmount"
              type="number"
              placeholder="e.g., 50000"
              value={formData.loanAmount}
              onChange={(e) => updateField("loanAmount", e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="employmentLength">Employment Length (years)</Label>
            <Input
              id="employmentLength"
              type="number"
              placeholder="e.g., 5"
              value={formData.employmentLength}
              onChange={(e) => updateField("employmentLength", e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="homeOwnership">Home Ownership</Label>
            <Select value={formData.homeOwnership} onValueChange={(value) => updateField("homeOwnership", value)}>
              <SelectTrigger id="homeOwnership">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="rent">Rent</SelectItem>
                <SelectItem value="own">Own</SelectItem>
                <SelectItem value="mortgage">Mortgage</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {error && (
            <div className="rounded-lg bg-destructive/10 p-3 text-sm text-destructive">
              {error}
            </div>
          )}

          <Button
            onClick={handlePredict}
            disabled={loading || !formData.age || !formData.income || !formData.creditScore}
            className="w-full"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Predicting...
              </>
            ) : (
              "Predict Credit Score"
            )}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Prediction Results</CardTitle>
          <CardDescription>Model output and risk assessment</CardDescription>
        </CardHeader>
        <CardContent>
          {!prediction ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Brain className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground">
                Fill in the form and click predict to see results
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="flex items-center justify-center">
                {prediction.approved ? (
                  <div className="flex flex-col items-center gap-2">
                    <div className="rounded-full bg-green-100 p-4 dark:bg-green-900/20">
                      <CheckCircle2 className="h-12 w-12 text-green-600 dark:text-green-500" />
                    </div>
                    <h3 className="text-2xl font-bold text-green-600 dark:text-green-500">
                      Approved
                    </h3>
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-2">
                    <div className="rounded-full bg-red-100 p-4 dark:bg-red-900/20">
                      <XCircle className="h-12 w-12 text-red-600 dark:text-red-500" />
                    </div>
                    <h3 className="text-2xl font-bold text-red-600 dark:text-red-500">
                      Rejected
                    </h3>
                  </div>
                )}
              </div>

              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm font-medium">Approval Probability</span>
                    <span className="text-sm font-medium">{(prediction.probability * 100).toFixed(1)}%</span>
                  </div>
                  <Progress value={prediction.probability * 100} className="h-2" />
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm font-medium">Model Confidence</span>
                    <span className="text-sm font-medium">{(prediction.confidence * 100).toFixed(1)}%</span>
                  </div>
                  <Progress value={prediction.confidence * 100} className="h-2" />
                </div>

                <div className="pt-4 border-t">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Risk Score</span>
                    <span className={`text-lg font-bold ${prediction.riskScore < 30 ? 'text-green-600' : prediction.riskScore < 60 ? 'text-yellow-600' : 'text-red-600'}`}>
                      {prediction.riskScore.toFixed(1)}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Lower scores indicate lower risk of default
                  </p>
                </div>

                {prediction.reasoning && prediction.reasoning.length > 0 && (
                  <div className="rounded-lg bg-muted p-4 space-y-2">
                    <h4 className="font-medium text-sm">Key Factors</h4>
                    <ul className="text-xs text-muted-foreground space-y-1">
                      {prediction.reasoning.map((reason: string, idx: number) => (
                        <li key={idx}>• {reason}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              <div className="rounded-lg bg-muted p-4 space-y-2">
                <h4 className="font-medium text-sm">Model Information</h4>
                <div className="text-xs text-muted-foreground space-y-1">
                  <p>• Algorithm: Random Forest Classifier</p>
                  <p>• Model Version: {prediction.modelVersion}</p>
                  <p>• Training Accuracy: 87.3%</p>
                  <p>• Validation AUC-ROC: 0.89</p>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}