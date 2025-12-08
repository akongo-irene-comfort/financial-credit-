"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts"
import { Info, TrendingUp, TrendingDown, Loader2 } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface ExplainabilitySectionProps {
  data: any
}

const chartConfig = {
  importance: { label: "Importance", color: "hsl(217, 91%, 60%)" },
  value: { label: "Value", color: "hsl(217, 91%, 60%)" },
  contribution: { label: "Contribution", color: "hsl(217, 91%, 60%)" }
}

export default function ExplainabilitySection({ data }: ExplainabilitySectionProps) {
  const [globalExplanation, setGlobalExplanation] = useState<any>(null)
  const [individualExplanation, setIndividualExplanation] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [formData, setFormData] = useState({
    age: "35",
    income: "75000",
    creditScore: "720",
    loanAmount: "50000",
    employmentLength: "5",
    homeOwnership: "rent"
  })

  const loadGlobalExplanation = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/shap/explain', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ type: 'global' })
      })

      const result = await response.json()

      if (!response.ok) {
        throw new Error(result.error || 'Failed to load explanation')
      }

      setGlobalExplanation(result.explanation)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load explanation')
    } finally {
      setLoading(false)
    }
  }

  const explainIndividual = async () => {
    setLoading(true)
    setError(null)

    try {
      // First get prediction
      const predResponse = await fetch('/api/model/predict', {
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

      const predData = await predResponse.json()

      // Then get explanation
      const explainResponse = await fetch('/api/shap/explain', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: 'individual',
          features: {
            age: parseFloat(formData.age),
            income: parseFloat(formData.income),
            creditScore: parseFloat(formData.creditScore),
            loanAmount: parseFloat(formData.loanAmount),
            employmentLength: parseFloat(formData.employmentLength),
            homeOwnership: formData.homeOwnership,
          },
          prediction: predData.prediction.probability
        })
      })

      const explainData = await explainResponse.json()

      if (!explainResponse.ok) {
        throw new Error(explainData.error || 'Failed to generate explanation')
      }

      setIndividualExplanation(explainData.explanation)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate explanation')
    } finally {
      setLoading(false)
    }
  }

  const updateField = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  return (
    <div className="space-y-6">
      {/* Explainability Overview */}
      <Alert>
        <Info className="h-4 w-4" />
        <AlertTitle>SHAP Explainability Analysis</AlertTitle>
        <AlertDescription>
          SHAP (SHapley Additive exPlanations) values show how each feature contributes to predictions.
          Positive values increase approval probability, negative values decrease it.
        </AlertDescription>
      </Alert>

      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="global" className="space-y-4">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="global">Global Importance</TabsTrigger>
          <TabsTrigger value="individual">Individual Prediction</TabsTrigger>
        </TabsList>

        <TabsContent value="global" className="space-y-6">
          {!globalExplanation ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Info className="h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground mb-4">Load global feature importance</p>
                <Button onClick={loadGlobalExplanation} disabled={loading}>
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Loading...
                    </>
                  ) : (
                    'Load Global Explanation'
                  )}
                </Button>
              </CardContent>
            </Card>
          ) : (
            <>
              {/* Global Feature Importance */}
              <Card>
                <CardHeader>
                  <CardTitle>Global Feature Importance</CardTitle>
                  <CardDescription>Average absolute impact across all predictions</CardDescription>
                </CardHeader>
                <CardContent>
                  <ChartContainer config={chartConfig} className="h-[400px]">
                    <BarChart data={globalExplanation.featureImportance} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" domain={[0, 0.35]} />
                      <YAxis dataKey="feature" type="category" width={150} />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Bar dataKey="importance" fill="var(--color-importance)" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ChartContainer>
                </CardContent>
              </Card>

              {/* Feature Details */}
              <Card>
                <CardHeader>
                  <CardTitle>Feature Impact Details</CardTitle>
                  <CardDescription>How each feature influences model decisions</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {globalExplanation.featureImportance.map((feature: any, idx: number) => (
                      <div key={idx} className="flex items-center justify-between border-b pb-3 last:border-0">
                        <div className="flex items-center gap-3 flex-1">
                          <TrendingUp className="h-5 w-5 text-primary" />
                          <div>
                            <p className="font-medium">{feature.feature}</p>
                            <p className="text-xs text-muted-foreground">{feature.description}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-mono font-medium">{(feature.importance * 100).toFixed(1)}%</p>
                          <p className="text-xs text-muted-foreground">contribution</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        <TabsContent value="individual" className="space-y-6">
          {/* Input Form */}
          <Card>
            <CardHeader>
              <CardTitle>Enter Applicant Details</CardTitle>
              <CardDescription>Provide information to explain prediction</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="exp-age">Age</Label>
                  <Input
                    id="exp-age"
                    type="number"
                    value={formData.age}
                    onChange={(e) => updateField("age", e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="exp-income">Annual Income ($)</Label>
                  <Input
                    id="exp-income"
                    type="number"
                    value={formData.income}
                    onChange={(e) => updateField("income", e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="exp-credit">Credit Score</Label>
                  <Input
                    id="exp-credit"
                    type="number"
                    value={formData.creditScore}
                    onChange={(e) => updateField("creditScore", e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="exp-loan">Loan Amount ($)</Label>
                  <Input
                    id="exp-loan"
                    type="number"
                    value={formData.loanAmount}
                    onChange={(e) => updateField("loanAmount", e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="exp-employment">Employment (years)</Label>
                  <Input
                    id="exp-employment"
                    type="number"
                    value={formData.employmentLength}
                    onChange={(e) => updateField("employmentLength", e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="exp-home">Home Ownership</Label>
                  <Select value={formData.homeOwnership} onValueChange={(value) => updateField("homeOwnership", value)}>
                    <SelectTrigger id="exp-home">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="rent">Rent</SelectItem>
                      <SelectItem value="own">Own</SelectItem>
                      <SelectItem value="mortgage">Mortgage</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <Button onClick={explainIndividual} disabled={loading} className="w-full">
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating Explanation...
                  </>
                ) : (
                  'Explain Prediction'
                )}
              </Button>
            </CardContent>
          </Card>

          {individualExplanation && (
            <>
              {/* SHAP Waterfall Chart */}
              <Card>
                <CardHeader>
                  <CardTitle>Individual Prediction Breakdown</CardTitle>
                  <CardDescription>SHAP waterfall showing feature contributions</CardDescription>
                </CardHeader>
                <CardContent>
                  <ChartContainer config={chartConfig} className="h-[400px]">
                    <BarChart data={individualExplanation.shapValues} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" domain={[-0.3, 0.3]} />
                      <YAxis dataKey="displayName" type="category" width={150} />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Bar dataKey="contribution" fill="var(--color-contribution)" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ChartContainer>
                </CardContent>
              </Card>

              {/* Prediction Details */}
              <Card>
                <CardHeader>
                  <CardTitle>Prediction Analysis</CardTitle>
                  <CardDescription>Detailed breakdown and interpretation</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 p-4 rounded-lg bg-muted/50">
                    <div>
                      <p className="text-sm text-muted-foreground mb-2">Final Prediction</p>
                      <div className="flex items-baseline gap-2">
                        <span className={`text-3xl font-bold ${individualExplanation.interpretation.decision === 'Approved' ? 'text-green-600' : 'text-red-600'}`}>
                          {(individualExplanation.finalPrediction * 100).toFixed(1)}%
                        </span>
                      </div>
                      <p className="text-sm font-medium mt-1">{individualExplanation.interpretation.decision}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground mb-2">Confidence</p>
                      <div className="flex items-baseline gap-2">
                        <span className="text-3xl font-bold">{(individualExplanation.interpretation.confidence * 100).toFixed(0)}%</span>
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">Model confidence</p>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-sm mb-3">Key Drivers</h4>
                    <div className="space-y-2">
                      {individualExplanation.shapValues.slice(0, 5).map((sv: any, idx: number) => (
                        <div 
                          key={idx}
                          className={`flex items-center justify-between p-2 rounded ${sv.contribution > 0 ? 'bg-green-50 dark:bg-green-900/10' : 'bg-red-50 dark:bg-red-900/10'}`}
                        >
                          <span className="text-sm">{sv.displayName}: {typeof sv.value === 'number' ? sv.value.toLocaleString() : sv.value}</span>
                          <span className={`text-sm font-medium ${sv.contribution > 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {sv.contribution > 0 ? '+' : ''}{(sv.contribution * 100).toFixed(1)}%
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="rounded-lg border bg-muted/50 p-4">
                    <h4 className="font-medium text-sm mb-2">Interpretation</h4>
                    <p className="text-sm text-muted-foreground">{individualExplanation.interpretation.reasoning}</p>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}