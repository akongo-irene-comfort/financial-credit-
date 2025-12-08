"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from "recharts"
import { AlertTriangle, CheckCircle2, Info, Loader2 } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"

interface FairnessAuditSectionProps {
  data: any
}

const chartConfig = {
  approvalRate: { label: "Approval Rate", color: "hsl(217, 91%, 60%)" },
  truePositiveRate: { label: "True Positive Rate", color: "hsl(142, 76%, 36%)" },
  falsePositiveRate: { label: "False Positive Rate", color: "hsl(0, 84%, 60%)" },
  score: { label: "Score", color: "hsl(217, 91%, 60%)" }
}

export default function FairnessAuditSection({ data }: FairnessAuditSectionProps) {
  const [fairnessData, setFairnessData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const analyzeFairness = async () => {
    if (!data || data.length === 0) {
      setError("No data available for fairness analysis")
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/fairness/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          data: data,
          protectedAttribute: 'gender'
        })
      })

      const result = await response.json()

      if (!response.ok) {
        throw new Error(result.error || 'Fairness analysis failed')
      }

      setFairnessData(result.fairness)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Fairness analysis failed')
      console.error('Fairness analysis error:', err)
    } finally {
      setLoading(false)
    }
  }

  // Auto-analyze when data is available
  useEffect(() => {
    if (data && data.length > 0 && !fairnessData && !loading) {
      analyzeFairness()
    }
  }, [data])

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
        <p className="text-muted-foreground">Analyzing fairness metrics...</p>
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  if (!fairnessData) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center space-y-4">
        <Info className="h-12 w-12 text-muted-foreground" />
        <div>
          <p className="text-muted-foreground mb-2">No fairness analysis available</p>
          <Button onClick={analyzeFairness} disabled={!data || data.length === 0}>
            Run Fairness Analysis
          </Button>
        </div>
      </div>
    )
  }

  // Transform data for charts
  const demographicParityData = Object.entries(fairnessData.groupMetrics).map(([group, metrics]: [string, any]) => ({
    group,
    approvalRate: (metrics.approvalRate * 100).toFixed(1),
    population: metrics.totalCount
  }))

  const equalOpportunityData = Object.entries(fairnessData.groupMetrics).map(([group, metrics]: [string, any]) => ({
    group,
    truePositiveRate: metrics.truePositiveRate,
    falsePositiveRate: metrics.falsePositiveRate
  }))

  const fairnessMetricsRadar = [
    { metric: "Demographic Parity", score: fairnessData.metrics.demographicParity },
    { metric: "Equal Opportunity", score: fairnessData.metrics.equalOpportunity },
    { metric: "Disparate Impact", score: Math.min(1, fairnessData.metrics.disparateImpact) },
    { metric: "Statistical Parity", score: fairnessData.metrics.statisticalParity },
  ]

  return (
    <div className="space-y-6">
      {/* Fairness Overview */}
      <Alert>
        <Info className="h-4 w-4" />
        <AlertTitle>Fairness Audit Overview</AlertTitle>
        <AlertDescription>
          This section evaluates the model for potential bias across different demographic groups.
          Metrics include demographic parity, equal opportunity, and disparate impact (80% rule).
        </AlertDescription>
      </Alert>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Overall Fairness Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <div className="text-3xl font-bold">{fairnessData.overallScore.toFixed(1)}</div>
              <span className="text-sm text-muted-foreground">/100</span>
            </div>
            <div className="flex items-center gap-2 mt-2">
              {fairnessData.overallScore >= 80 ? (
                <>
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <span className="text-xs text-green-600">Acceptable range</span>
                </>
              ) : (
                <>
                  <AlertTriangle className="h-4 w-4 text-yellow-600" />
                  <span className="text-xs text-yellow-600">Needs attention</span>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Demographic Parity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <div className="text-3xl font-bold">{(fairnessData.metrics.demographicParity * 100).toFixed(1)}%</div>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Difference: {(fairnessData.metrics.demographicParityDifference * 100).toFixed(1)}%
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Disparate Impact</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <div className="text-3xl font-bold">{fairnessData.metrics.disparateImpact.toFixed(2)}</div>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              {fairnessData.complianceStatus['80PercentRule'] ? '✓ Passes 80% rule' : '✗ Fails 80% rule'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Visualizations */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Approval Rates by Group</CardTitle>
            <CardDescription>Demographic parity analysis across groups</CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer config={chartConfig} className="h-[300px]">
              <BarChart data={demographicParityData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" domain={[0, 100]} />
                <YAxis dataKey="group" type="category" width={100} />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Bar dataKey="approvalRate" fill="var(--color-approvalRate)" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ChartContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>True vs False Positive Rates</CardTitle>
            <CardDescription>Equal opportunity metrics comparison</CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer config={chartConfig} className="h-[300px]">
              <BarChart data={equalOpportunityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="group" />
                <YAxis domain={[0, 1]} />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Bar dataKey="truePositiveRate" fill="var(--color-truePositiveRate)" radius={[4, 4, 0, 0]} />
                <Bar dataKey="falsePositiveRate" fill="var(--color-falsePositiveRate)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ChartContainer>
          </CardContent>
        </Card>
      </div>

      {/* Fairness Metrics Radar */}
      <Card>
        <CardHeader>
          <CardTitle>Comprehensive Fairness Metrics</CardTitle>
          <CardDescription>Multi-dimensional fairness assessment</CardDescription>
        </CardHeader>
        <CardContent>
          <ChartContainer config={chartConfig} className="h-[400px]">
            <RadarChart data={fairnessMetricsRadar}>
              <PolarGrid />
              <PolarAngleAxis dataKey="metric" />
              <PolarRadiusAxis angle={90} domain={[0, 1]} />
              <Radar name="Score" dataKey="score" stroke="var(--color-score)" fill="var(--color-score)" fillOpacity={0.6} />
              <ChartTooltip content={<ChartTooltipContent />} />
            </RadarChart>
          </ChartContainer>
        </CardContent>
      </Card>

      {/* Detailed Findings */}
      <Card>
        <CardHeader>
          <CardTitle>Bias Audit Findings</CardTitle>
          <CardDescription>Detailed analysis and recommendations</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {fairnessData.recommendations.map((recommendation: string, idx: number) => {
            const isPositive = recommendation.includes('acceptable') || recommendation.includes('maintained') || recommendation.includes('Continue')
            return (
              <div key={idx} className="flex items-start gap-3">
                <div className={`rounded-full p-2 ${isPositive ? 'bg-green-100 dark:bg-green-900/20' : 'bg-yellow-100 dark:bg-yellow-900/20'}`}>
                  {isPositive ? (
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                  ) : (
                    <AlertTriangle className="h-4 w-4 text-yellow-600" />
                  )}
                </div>
                <div className="flex-1">
                  <p className="text-sm">{recommendation}</p>
                </div>
              </div>
            )
          })}

          <div className="rounded-lg border bg-muted/50 p-4 mt-4">
            <h4 className="font-medium text-sm mb-2">Compliance Status</h4>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• 80% Rule (Disparate Impact): {fairnessData.complianceStatus['80PercentRule'] ? '✓ Pass' : '✗ Fail'}</li>
              <li>• Demographic Parity: {fairnessData.complianceStatus.demographicParity ? '✓ Pass' : '✗ Fail'}</li>
              <li>• Equal Opportunity: {fairnessData.complianceStatus.equalOpportunity ? '✓ Pass' : '✗ Fail'}</li>
            </ul>
          </div>

          <Button onClick={analyzeFairness} variant="outline" className="w-full">
            <Loader2 className="mr-2 h-4 w-4" />
            Re-run Analysis
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}